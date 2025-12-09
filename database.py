"""資料庫模型 - 支援 PostgreSQL 和 SQLite"""
import os
from datetime import datetime, date
from typing import List, Dict, Optional
from config import Config


class SimpleDatabase:
    """支援 PostgreSQL 和 SQLite 的資料庫類別"""

    def __init__(self):
        self.use_postgres = bool(Config.DATABASE_URL)

        if self.use_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.psycopg2 = psycopg2
            self.RealDictCursor = RealDictCursor
            print(f"✅ 使用 PostgreSQL 資料庫")
        else:
            import sqlite3
            self.sqlite3 = sqlite3
            self._ensure_data_dir()
            print(f"✅ 使用 SQLite 資料庫: {Config.DATABASE_PATH}")

        self._init_db()

    def _ensure_data_dir(self):
        """確保 SQLite 資料目錄存在"""
        dir_path = os.path.dirname(Config.DATABASE_PATH)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

    def _get_connection(self):
        """取得資料庫連線"""
        if self.use_postgres:
            conn = self.psycopg2.connect(Config.DATABASE_URL)
            return conn
        else:
            conn = self.sqlite3.connect(Config.DATABASE_PATH)
            conn.row_factory = self.sqlite3.Row
            return conn

    def _execute(self, query: str, params: tuple = None):
        """執行 SQL（自動處理參數佔位符差異）"""
        if self.use_postgres:
            # PostgreSQL 使用 %s
            query = query.replace('?', '%s')

        conn = self._get_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        return conn, cursor

    def _fetchall(self, query: str, params: tuple = None) -> List[Dict]:
        """查詢並返回所有結果"""
        if self.use_postgres:
            query = query.replace('?', '%s')
            conn = self.psycopg2.connect(Config.DATABASE_URL)
            cursor = conn.cursor(cursor_factory=self.RealDictCursor)
        else:
            conn = self.sqlite3.connect(Config.DATABASE_PATH)
            conn.row_factory = self.sqlite3.Row
            cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        conn.close()

        if self.use_postgres:
            return [dict(row) for row in rows]
        else:
            return [dict(row) for row in rows]

    def _fetchone(self, query: str, params: tuple = None) -> Optional[Dict]:
        """查詢並返回單一結果"""
        if self.use_postgres:
            query = query.replace('?', '%s')
            conn = self.psycopg2.connect(Config.DATABASE_URL)
            cursor = conn.cursor(cursor_factory=self.RealDictCursor)
        else:
            conn = self.sqlite3.connect(Config.DATABASE_PATH)
            conn.row_factory = self.sqlite3.Row
            cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def _init_db(self):
        """初始化資料庫結構"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            # PostgreSQL 語法
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'daily',
                    estimated_minutes INTEGER DEFAULT 30,
                    target_date TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schedule_items (
                    id SERIAL PRIMARY KEY,
                    date TEXT NOT NULL,
                    title TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    display_order INTEGER DEFAULT 0,
                    routine_id INTEGER DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 建立 UNIQUE 索引（如果不存在）
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_schedule_unique
                ON schedule_items(date, title, start_time, end_time)
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_routines (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS routine_exceptions (
                    id SERIAL PRIMARY KEY,
                    routine_id INTEGER NOT NULL,
                    exception_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(routine_id, exception_date)
                )
            ''')

        else:
            # SQLite 語法
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'daily',
                    estimated_minutes INTEGER DEFAULT 30,
                    target_date TEXT,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

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

            # 建立 UNIQUE 索引
            try:
                cursor.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_schedule_unique
                    ON schedule_items(date, title, start_time, end_time)
                ''')
            except:
                pass

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
        """新增待辦事項"""
        if self.use_postgres:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO todos (content, type, estimated_minutes, target_date) VALUES (%s, %s, %s, %s) RETURNING id',
                (content, todo_type, estimated_minutes, target_date)
            )
            todo_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
        else:
            conn, cursor = self._execute(
                'INSERT INTO todos (content, type, estimated_minutes, target_date) VALUES (?, ?, ?, ?)',
                (content, todo_type, estimated_minutes, target_date)
            )
            todo_id = cursor.lastrowid
            conn.commit()
            conn.close()
        return todo_id

    def get_todos(self, todo_type: str = None, target_date: str = None) -> List[Dict]:
        """取得待辦事項"""
        query = 'SELECT * FROM todos WHERE 1=1'
        params = []

        if todo_type:
            query += ' AND type = ?'
            params.append(todo_type)

        if target_date:
            query += ' AND target_date = ?'
            params.append(target_date)

        query += ' ORDER BY created_at DESC'
        return self._fetchall(query, tuple(params) if params else None)

    def delete_todo(self, todo_id: int):
        """刪除待辦事項"""
        conn, cursor = self._execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()

    def update_todo(self, todo_id: int, content: str = None, todo_type: str = None,
                    estimated_minutes: int = None, completed: bool = None):
        """更新待辦事項"""
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
            values.append(completed)

        if updates:
            values.append(todo_id)
            query = f"UPDATE todos SET {', '.join(updates)} WHERE id = ?"
            conn, cursor = self._execute(query, tuple(values))
            conn.commit()
            conn.close()

    def toggle_todo_complete(self, todo_id: int):
        """切換待辦事項完成狀態"""
        conn, cursor = self._execute(
            'UPDATE todos SET completed = NOT completed WHERE id = ?',
            (todo_id,)
        )
        conn.commit()
        conn.close()

    # ===== 排程 =====

    def add_schedule_item(self, date_str: str, title: str, start_time: str, end_time: str, routine_id: int = None) -> int:
        """新增排程項目（如果重複則忽略）"""
        try:
            if self.use_postgres:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO schedule_items (date, title, start_time, end_time, routine_id) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                    (date_str, title, start_time, end_time, routine_id)
                )
                item_id = cursor.fetchone()[0]
                conn.commit()
                conn.close()
            else:
                conn, cursor = self._execute(
                    'INSERT INTO schedule_items (date, title, start_time, end_time, routine_id) VALUES (?, ?, ?, ?, ?)',
                    (date_str, title, start_time, end_time, routine_id)
                )
                item_id = cursor.lastrowid
                conn.commit()
                conn.close()
            return item_id
        except Exception as e:
            # UNIQUE 約束違反，查詢現有項目
            row = self._fetchone(
                'SELECT id FROM schedule_items WHERE date = ? AND title = ? AND start_time = ? AND end_time = ?',
                (date_str, title, start_time, end_time)
            )
            return row['id'] if row else 0

    def get_schedule(self, date_str: str) -> List[Dict]:
        """取得指定日期的排程"""
        return self._fetchall(
            'SELECT * FROM schedule_items WHERE date = ? ORDER BY start_time',
            (date_str,)
        )

    def update_schedule_item(self, item_id: int, title: str = None, start_time: str = None,
                             end_time: str = None, completed: bool = None, display_order: int = None):
        """更新排程項目"""
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
            values.append(completed)
        if display_order is not None:
            updates.append('display_order = ?')
            values.append(display_order)

        if updates:
            values.append(item_id)
            query = f"UPDATE schedule_items SET {', '.join(updates)} WHERE id = ?"
            conn, cursor = self._execute(query, tuple(values))
            conn.commit()
            conn.close()

    def toggle_schedule_complete(self, item_id: int):
        """切換排程完成狀態"""
        conn, cursor = self._execute(
            'UPDATE schedule_items SET completed = NOT completed WHERE id = ?',
            (item_id,)
        )
        conn.commit()
        conn.close()

    def delete_schedule_item(self, item_id: int):
        """刪除排程項目"""
        conn, cursor = self._execute('DELETE FROM schedule_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

    def clear_schedule(self, date_str: str):
        """清空指定日期的排程"""
        conn, cursor = self._execute('DELETE FROM schedule_items WHERE date = ?', (date_str,))
        conn.commit()
        conn.close()

    def batch_add_schedule(self, date_str: str, items: List[Dict]):
        """批次新增排程（用於 AI 生成）"""
        # 先清空該日期的排程
        self.clear_schedule(date_str)

        # 批次插入
        for item in items:
            self.add_schedule_item(date_str, item['title'], item['start_time'], item['end_time'])

    # ===== 延誤偵測與管理 =====

    def get_delayed_schedules(self, date_str: str, current_time: str) -> List[Dict]:
        """取得已延誤的排程"""
        return self._fetchall(
            'SELECT * FROM schedule_items WHERE date = ? AND end_time < ? AND completed = FALSE ORDER BY start_time',
            (date_str, current_time)
        )

    def get_uncompleted_schedules(self, date_str: str) -> List[Dict]:
        """取得指定日期所有未完成的排程"""
        return self._fetchall(
            'SELECT * FROM schedule_items WHERE date = ? AND completed = FALSE ORDER BY start_time',
            (date_str,)
        )

    def move_schedule_to_date(self, item_id: int, new_date: str, new_start_time: str = None, new_end_time: str = None):
        """移動排程到新日期"""
        if new_start_time and new_end_time:
            conn, cursor = self._execute(
                'UPDATE schedule_items SET date = ?, start_time = ?, end_time = ? WHERE id = ?',
                (new_date, new_start_time, new_end_time, item_id)
            )
        else:
            conn, cursor = self._execute(
                'UPDATE schedule_items SET date = ? WHERE id = ?',
                (new_date, item_id)
            )
        conn.commit()
        conn.close()

    def get_uncompleted_todos_by_date(self) -> Dict[str, List[Dict]]:
        """取得所有未完成的待辦，按類型分組"""
        todos = self._fetchall('SELECT * FROM todos WHERE completed = FALSE ORDER BY type, created_at DESC')

        grouped = {'daily': [], 'weekly': [], 'monthly': [], 'quick': []}
        for todo in todos:
            todo_type = todo.get('type', 'daily')
            if todo_type in grouped:
                grouped[todo_type].append(todo)

        return grouped

    # ===== 每日固定排程 =====

    def add_routine(self, title: str, start_time: str, end_time: str) -> int:
        """新增每日固定排程"""
        if self.use_postgres:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO daily_routines (title, start_time, end_time) VALUES (%s, %s, %s) RETURNING id',
                (title, start_time, end_time)
            )
            routine_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
        else:
            conn, cursor = self._execute(
                'INSERT INTO daily_routines (title, start_time, end_time) VALUES (?, ?, ?)',
                (title, start_time, end_time)
            )
            routine_id = cursor.lastrowid
            conn.commit()
            conn.close()
        return routine_id

    def get_routines(self, enabled_only: bool = False) -> List[Dict]:
        """取得所有每日固定排程"""
        if enabled_only:
            return self._fetchall('SELECT * FROM daily_routines WHERE enabled = TRUE ORDER BY start_time')
        return self._fetchall('SELECT * FROM daily_routines ORDER BY start_time')

    def update_routine(self, routine_id: int, title: str = None, start_time: str = None,
                       end_time: str = None, enabled: bool = None):
        """更新每日固定排程"""
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
            values.append(enabled)

        if updates:
            values.append(routine_id)
            query = f"UPDATE daily_routines SET {', '.join(updates)} WHERE id = ?"
            conn, cursor = self._execute(query, tuple(values))
            conn.commit()
            conn.close()

    def delete_routine(self, routine_id: int):
        """刪除每日固定排程"""
        conn, cursor = self._execute('DELETE FROM daily_routines WHERE id = ?', (routine_id,))
        conn.commit()
        conn.close()

    def toggle_routine_enabled(self, routine_id: int):
        """切換每日固定排程的啟用狀態"""
        conn, cursor = self._execute(
            'UPDATE daily_routines SET enabled = NOT enabled WHERE id = ?',
            (routine_id,)
        )
        conn.commit()
        conn.close()

    def apply_routines_to_date(self, date_str: str) -> int:
        """將啟用的固定排程套用到指定日期（排除有例外的），返回新增數量"""
        routines = self.get_routines(enabled_only=True)
        exceptions = self.get_routine_exceptions(date_str)
        excepted_routine_ids = set(exceptions)
        added_count = 0

        for routine in routines:
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
                pass

        return added_count

    # ===== 固定排程例外管理 =====

    def add_routine_exception(self, routine_id: int, exception_date: str):
        """新增固定排程例外"""
        try:
            conn, cursor = self._execute(
                'INSERT INTO routine_exceptions (routine_id, exception_date) VALUES (?, ?)',
                (routine_id, exception_date)
            )
            conn.commit()
            conn.close()
        except:
            pass

    def remove_routine_exception(self, routine_id: int, exception_date: str):
        """移除固定排程例外"""
        conn, cursor = self._execute(
            'DELETE FROM routine_exceptions WHERE routine_id = ? AND exception_date = ?',
            (routine_id, exception_date)
        )
        conn.commit()
        conn.close()

    def get_routine_exceptions(self, date_str: str) -> List[int]:
        """取得指定日期的所有例外 routine_id"""
        rows = self._fetchall(
            'SELECT routine_id FROM routine_exceptions WHERE exception_date = ?',
            (date_str,)
        )
        return [row['routine_id'] for row in rows]

    def delete_schedule_by_routine(self, routine_id: int, date_str: str):
        """刪除指定日期來自特定固定排程的排程項目"""
        conn, cursor = self._execute(
            'DELETE FROM schedule_items WHERE routine_id = ? AND date = ?',
            (routine_id, date_str)
        )
        conn.commit()
        conn.close()
