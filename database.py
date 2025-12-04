"""資料庫模型與操作"""
import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional
import os


class Database:
    """資料庫管理類別"""

    def __init__(self, db_path: str = 'data/daily.db'):
        self.db_path = db_path
        self._ensure_data_dir()
        self._init_db()

    def _ensure_data_dir(self):
        """確保資料目錄存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_connection(self):
        """取得資料庫連線"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化資料庫結構"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 任務表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                duration INTEGER DEFAULT 30,
                priority INTEGER DEFAULT 0,
                category TEXT DEFAULT 'other',
                is_routine BOOLEAN DEFAULT 0,
                preferred_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 行程表（AI 生成的排程結果）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                schedule_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 使用者偏好設定
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wake_time TEXT DEFAULT '07:00',
                sleep_time TEXT DEFAULT '23:00',
                breakfast_time TEXT DEFAULT '07:30',
                lunch_time TEXT DEFAULT '12:00',
                dinner_time TEXT DEFAULT '18:30',
                commute_duration INTEGER DEFAULT 30,
                buffer_time INTEGER DEFAULT 10
            )
        ''')

        # 如果沒有偏好設定，插入預設值
        cursor.execute('SELECT COUNT(*) FROM user_preferences')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO user_preferences (wake_time, sleep_time)
                VALUES ('07:00', '23:00')
            ''')

        conn.commit()
        conn.close()

    # ===== 任務管理 =====

    def add_task(self, title: str, duration: int = 30, priority: int = 0,
                 category: str = 'other', is_routine: bool = False,
                 preferred_time: Optional[str] = None) -> int:
        """新增任務"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, duration, priority, category, is_routine, preferred_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, duration, priority, category, is_routine, preferred_time))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_tasks(self) -> List[Dict]:
        """取得所有任務"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks ORDER BY priority DESC, created_at ASC')
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def get_task(self, task_id: int) -> Optional[Dict]:
        """取得單一任務"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_task(self, task_id: int, **kwargs):
        """更新任務"""
        allowed_fields = ['title', 'duration', 'priority', 'category', 'is_routine', 'preferred_time']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return

        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [task_id]

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE tasks SET {set_clause} WHERE id = ?', values)
        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        """刪除任務"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    # ===== 行程管理 =====

    def save_schedule(self, schedule_date: date, schedule_data: List[Dict]):
        """儲存行程"""
        conn = self._get_connection()
        cursor = conn.cursor()

        date_str = schedule_date.isoformat()
        data_json = json.dumps(schedule_data, ensure_ascii=False)

        # 檢查是否已存在該日期的行程
        cursor.execute('SELECT id FROM schedules WHERE date = ?', (date_str,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE schedules SET schedule_data = ?, created_at = CURRENT_TIMESTAMP
                WHERE date = ?
            ''', (data_json, date_str))
        else:
            cursor.execute('''
                INSERT INTO schedules (date, schedule_data)
                VALUES (?, ?)
            ''', (date_str, data_json))

        conn.commit()
        conn.close()

    def get_schedule(self, schedule_date: date) -> Optional[List[Dict]]:
        """取得指定日期的行程"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT schedule_data FROM schedules WHERE date = ?',
                      (schedule_date.isoformat(),))
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    # ===== 偏好設定 =====

    def get_preferences(self) -> Dict:
        """取得使用者偏好設定"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_preferences LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}

    def update_preferences(self, **kwargs):
        """更新使用者偏好設定"""
        allowed_fields = ['wake_time', 'sleep_time', 'breakfast_time', 'lunch_time',
                         'dinner_time', 'commute_duration', 'buffer_time']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return

        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values())

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE user_preferences SET {set_clause}', values)
        conn.commit()
        conn.close()
