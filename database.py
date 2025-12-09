"""簡化版資料庫模型"""
import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional
import os
from config import Config


class SimpleDatabase:
    """簡化版資料庫"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_data_dir()
        self._init_db()

    def _ensure_data_dir(self):
        """確保資料目錄存在"""
        dir_path = os.path.dirname(self.db_path)
        if dir_path:  # 只有當路徑包含目錄時才建立
            os.makedirs(dir_path, exist_ok=True)

    def _get_connection(self):
        """取得資料庫連線"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化資料庫結構"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 待辦事項表（簡化版）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                type TEXT DEFAULT 'daily',
                estimated_minutes INTEGER DEFAULT 30,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 檢查並添加 type 欄位（如果是舊資料庫）
        try:
            cursor.execute("SELECT type FROM todos LIMIT 1")
        except:
            cursor.execute("ALTER TABLE todos ADD COLUMN type TEXT DEFAULT 'daily'")

        # 檢查並添加 target_date 欄位（支援多日待辦）
        try:
            cursor.execute("SELECT target_date FROM todos LIMIT 1")
        except:
            cursor.execute("ALTER TABLE todos ADD COLUMN target_date TEXT")

        # 排程表（可編輯的時間）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                routine_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 檢查並添加 routine_id 欄位（如果是舊資料庫）
        try:
            cursor.execute("SELECT routine_id FROM schedule_items LIMIT 1")
        except:
            cursor.execute("ALTER TABLE schedule_items ADD COLUMN routine_id INTEGER DEFAULT NULL")

        # 建立 UNIQUE 索引防止重複排程
        try:
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_schedule_unique
                ON schedule_items(date, title, start_time, end_time)
            ''')
        except Exception as e:
            # 如果索引已存在或其他錯誤，忽略
            pass

        # 每日固定排程表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_routines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 固定排程例外表（記錄某天排除某個固定排程）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routine_exceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                routine_id INTEGER NOT NULL,
                exception_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(routine_id, exception_date)
            )
        ''')

        conn.commit()
        conn.close()

    # ===== 待辦事項 =====

    def add_todo(self, content: str, todo_type: str = 'daily', estimated_minutes: int = 30, target_date: str = None) -> int:
        """新增待辦事項

        Args:
            content: 待辦內容
            todo_type: 類型 (quick/daily/weekly/monthly)
            estimated_minutes: 預估時間（分鐘）
            target_date: 目標日期 (YYYY-MM-DD)，None 表示不限定日期
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO todos (content, type, estimated_minutes, target_date) VALUES (?, ?, ?, ?)',
                      (content, todo_type, estimated_minutes, target_date))
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return todo_id

    def get_todos(self, todo_type: str = None, target_date: str = None) -> List[Dict]:
        """取得待辦事項（可選類型和日期篩選）

        Args:
            todo_type: 待辦類型 (quick/daily/weekly/monthly)
            target_date: 目標日期 (YYYY-MM-DD)，None 表示取得所有
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM todos WHERE 1=1'
        params = []

        if todo_type:
            query += ' AND type = ?'
            params.append(todo_type)

        if target_date:
            query += ' AND target_date = ?'
            params.append(target_date)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params)
        todos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return todos

    def delete_todo(self, todo_id: int):
        """刪除待辦事項"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()

    def update_todo(self, todo_id: int, content: str = None, todo_type: str = None, estimated_minutes: int = None, completed: bool = None):
        """更新待辦事項"""
        conn = self._get_connection()
        cursor = conn.cursor()

        updates = []
        values = []

        if content is not None:
            updates.append('content = ?')
            values.append(content)
        if todo_type is not None:
            updates.append('type = ?')
            values.append(todo_type)
        if estimated_minutes is not None:
            updates.append('estimated_minutes = ?')
            values.append(estimated_minutes)
        if completed is not None:
            updates.append('completed = ?')
            values.append(1 if completed else 0)

        if updates:
            values.append(todo_id)
            cursor.execute(f"UPDATE todos SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

        conn.close()

    def toggle_todo_complete(self, todo_id: int):
        """切換待辦事項完成狀態"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE todos
            SET completed = CASE WHEN completed = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        ''', (todo_id,))
        conn.commit()
        conn.close()

    # ===== 排程 =====

    def add_schedule_item(self, date_str: str, title: str, start_time: str, end_time: str, routine_id: int = None) -> int:
        """新增排程項目（如果重複則忽略）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO schedule_items (date, title, start_time, end_time, routine_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_str, title, start_time, end_time, routine_id))
            item_id = cursor.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            # UNIQUE 約束違反，表示重複，忽略並返回現有項目的 ID
            cursor.execute('''
                SELECT id FROM schedule_items
                WHERE date = ? AND title = ? AND start_time = ? AND end_time = ?
            ''', (date_str, title, start_time, end_time))
            item_id = cursor.fetchone()[0]
        finally:
            conn.close()
        return item_id

    def get_schedule(self, date_str: str) -> List[Dict]:
        """取得指定日期的排程"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM schedule_items
            WHERE date = ?
            ORDER BY start_time
        ''', (date_str,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def update_schedule_item(self, item_id: int, title: str = None,
                            start_time: str = None, end_time: str = None,
                            completed: bool = None, display_order: int = None):
        """更新排程項目"""
        conn = self._get_connection()
        cursor = conn.cursor()

        updates = []
        values = []

        if title is not None:
            updates.append('title = ?')
            values.append(title)
        if start_time is not None:
            updates.append('start_time = ?')
            values.append(start_time)
        if end_time is not None:
            updates.append('end_time = ?')
            values.append(end_time)
        if completed is not None:
            updates.append('completed = ?')
            values.append(1 if completed else 0)
        if display_order is not None:
            updates.append('display_order = ?')
            values.append(display_order)

        if updates:
            values.append(item_id)
            cursor.execute(
                f"UPDATE schedule_items SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()

        conn.close()

    def toggle_schedule_complete(self, item_id: int):
        """切換排程完成狀態"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE schedule_items
            SET completed = CASE WHEN completed = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        ''', (item_id,))
        conn.commit()
        conn.close()

    def delete_schedule_item(self, item_id: int):
        """刪除排程項目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schedule_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

    def clear_schedule(self, date_str: str):
        """清空指定日期的排程"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schedule_items WHERE date = ?', (date_str,))
        conn.commit()
        conn.close()

    def batch_add_schedule(self, date_str: str, items: List[Dict]):
        """批次新增排程（用於 AI 生成）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 先清空該日期的排程
        cursor.execute('DELETE FROM schedule_items WHERE date = ?', (date_str,))

        # 批次插入
        for item in items:
            cursor.execute('''
                INSERT INTO schedule_items (date, title, start_time, end_time)
                VALUES (?, ?, ?, ?)
            ''', (date_str, item['title'], item['start_time'], item['end_time']))

        conn.commit()
        conn.close()

    # ===== 延誤偵測與管理 =====

    def get_delayed_schedules(self, date_str: str, current_time: str) -> List[Dict]:
        """取得已延誤的排程（已過結束時間且未完成）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM schedule_items
            WHERE date = ? AND end_time < ? AND completed = 0
            ORDER BY start_time
        ''', (date_str, current_time))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def get_uncompleted_schedules(self, date_str: str) -> List[Dict]:
        """取得指定日期所有未完成的排程"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM schedule_items
            WHERE date = ? AND completed = 0
            ORDER BY start_time
        ''', (date_str,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def move_schedule_to_date(self, item_id: int, new_date: str, new_start_time: str = None, new_end_time: str = None):
        """移動排程到新日期"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if new_start_time and new_end_time:
            cursor.execute('''
                UPDATE schedule_items
                SET date = ?, start_time = ?, end_time = ?
                WHERE id = ?
            ''', (new_date, new_start_time, new_end_time, item_id))
        else:
            cursor.execute('''
                UPDATE schedule_items
                SET date = ?
                WHERE id = ?
            ''', (new_date, item_id))

        conn.commit()
        conn.close()

    def get_uncompleted_todos_by_date(self) -> Dict[str, List[Dict]]:
        """取得所有未完成的待辦，按類型分組"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM todos WHERE completed = 0 ORDER BY type, created_at DESC')
        todos = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # 按類型分組
        grouped = {'daily': [], 'weekly': [], 'monthly': [], 'quick': []}
        for todo in todos:
            todo_type = todo.get('type', 'daily')
            if todo_type in grouped:
                grouped[todo_type].append(todo)

        return grouped

    # ===== 每日固定排程 =====

    def add_routine(self, title: str, start_time: str, end_time: str) -> int:
        """新增每日固定排程"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_routines (title, start_time, end_time)
            VALUES (?, ?, ?)
        ''', (title, start_time, end_time))
        routine_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return routine_id

    def get_routines(self, enabled_only: bool = False) -> List[Dict]:
        """取得所有每日固定排程"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if enabled_only:
            cursor.execute('SELECT * FROM daily_routines WHERE enabled = 1 ORDER BY start_time')
        else:
            cursor.execute('SELECT * FROM daily_routines ORDER BY start_time')
        routines = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return routines

    def update_routine(self, routine_id: int, title: str = None, start_time: str = None,
                       end_time: str = None, enabled: bool = None):
        """更新每日固定排程"""
        conn = self._get_connection()
        cursor = conn.cursor()

        updates = []
        values = []

        if title is not None:
            updates.append('title = ?')
            values.append(title)
        if start_time is not None:
            updates.append('start_time = ?')
            values.append(start_time)
        if end_time is not None:
            updates.append('end_time = ?')
            values.append(end_time)
        if enabled is not None:
            updates.append('enabled = ?')
            values.append(1 if enabled else 0)

        if updates:
            values.append(routine_id)
            cursor.execute(
                f"UPDATE daily_routines SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()

        conn.close()

    def delete_routine(self, routine_id: int):
        """刪除每日固定排程"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM daily_routines WHERE id = ?', (routine_id,))
        conn.commit()
        conn.close()

    def toggle_routine_enabled(self, routine_id: int):
        """切換每日固定排程的啟用狀態"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE daily_routines
            SET enabled = CASE WHEN enabled = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        ''', (routine_id,))
        conn.commit()
        conn.close()

    def apply_routines_to_date(self, date_str: str) -> int:
        """將啟用的固定排程套用到指定日期（排除有例外的），返回新增數量"""
        routines = self.get_routines(enabled_only=True)
        exceptions = self.get_routine_exceptions(date_str)
        excepted_routine_ids = set(exceptions)
        added_count = 0

        for routine in routines:
            # 跳過有例外的固定排程
            if routine['id'] in excepted_routine_ids:
                continue

            try:
                self.add_schedule_item(
                    date_str,
                    routine['title'],
                    routine['start_time'],
                    routine['end_time'],
                    routine_id=routine['id']
                )
                added_count += 1
            except:
                # 如果已存在則跳過
                pass

        return added_count

    # ===== 固定排程例外管理 =====

    def add_routine_exception(self, routine_id: int, exception_date: str):
        """新增固定排程例外（某天排除某個固定排程）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO routine_exceptions (routine_id, exception_date)
                VALUES (?, ?)
            ''', (routine_id, exception_date))
            conn.commit()
        except sqlite3.IntegrityError:
            # 已存在則忽略
            pass
        finally:
            conn.close()

    def remove_routine_exception(self, routine_id: int, exception_date: str):
        """移除固定排程例外（恢復某天的固定排程）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM routine_exceptions
            WHERE routine_id = ? AND exception_date = ?
        ''', (routine_id, exception_date))
        conn.commit()
        conn.close()

    def get_routine_exceptions(self, date_str: str) -> List[int]:
        """取得指定日期的所有例外 routine_id"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT routine_id FROM routine_exceptions
            WHERE exception_date = ?
        ''', (date_str,))
        routine_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return routine_ids

    def delete_schedule_by_routine(self, routine_id: int, date_str: str):
        """刪除指定日期來自特定固定排程的排程項目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM schedule_items
            WHERE routine_id = ? AND date = ?
        ''', (routine_id, date_str))
        conn.commit()
        conn.close()
