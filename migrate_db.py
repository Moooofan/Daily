"""資料庫遷移腳本 - 為 todos 和 schedule_items 添加新欄位"""
import sqlite3
import os

def migrate_database():
    db_path = 'data/daily.db'

    if not os.path.exists(db_path):
        print(f"資料庫不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 檢查並添加 todos 表的 completed 欄位
    try:
        cursor.execute("SELECT completed FROM todos LIMIT 1")
        print("todos.completed 欄位已存在")
    except sqlite3.OperationalError:
        print("添加 todos.completed 欄位...")
        cursor.execute("ALTER TABLE todos ADD COLUMN completed BOOLEAN DEFAULT 0")
        print("✓ 已添加 todos.completed 欄位")

    # 檢查並添加 todos 表的 estimated_minutes 欄位
    try:
        cursor.execute("SELECT estimated_minutes FROM todos LIMIT 1")
        print("todos.estimated_minutes 欄位已存在")
    except sqlite3.OperationalError:
        print("添加 todos.estimated_minutes 欄位...")
        cursor.execute("ALTER TABLE todos ADD COLUMN estimated_minutes INTEGER DEFAULT 30")
        print("✓ 已添加 todos.estimated_minutes 欄位")

    # 檢查並添加 schedule_items 表的 completed 欄位
    try:
        cursor.execute("SELECT completed FROM schedule_items LIMIT 1")
        print("schedule_items.completed 欄位已存在")
    except sqlite3.OperationalError:
        print("添加 schedule_items.completed 欄位...")
        cursor.execute("ALTER TABLE schedule_items ADD COLUMN completed BOOLEAN DEFAULT 0")
        print("✓ 已添加 schedule_items.completed 欄位")

    # 檢查並添加 schedule_items 表的 display_order 欄位
    try:
        cursor.execute("SELECT display_order FROM schedule_items LIMIT 1")
        print("schedule_items.display_order 欄位已存在")
    except sqlite3.OperationalError:
        print("添加 schedule_items.display_order 欄位...")
        cursor.execute("ALTER TABLE schedule_items ADD COLUMN display_order INTEGER DEFAULT 0")
        print("✓ 已添加 schedule_items.display_order 欄位")

    conn.commit()
    conn.close()

    print("\n資料庫遷移完成！")

if __name__ == '__main__':
    migrate_database()
