#!/usr/bin/env python3
"""測試系統設定是否正確"""

import os
import sys
from datetime import date

print("=" * 60)
print("Daily Schedule AI - 系統檢查")
print("=" * 60)

# 檢查 1: Python 版本
print("\n[1/6] 檢查 Python 版本...")
if sys.version_info >= (3, 8):
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(f"❌ Python 版本過舊，需要 3.8+")
    sys.exit(1)

# 檢查 2: 套件安裝
print("\n[2/6] 檢查套件安裝...")
required_packages = [
    ('flask', 'Flask'),
    ('anthropic', 'Anthropic'),
    ('google.auth', 'Google Auth'),
    ('dotenv', 'Python Dotenv')
]

missing_packages = []
for package_name, display_name in required_packages:
    try:
        if package_name == 'google.auth':
            import google.auth
        elif package_name == 'dotenv':
            import dotenv
        elif package_name == 'flask':
            import flask
        elif package_name == 'anthropic':
            import anthropic
        print(f"✅ {display_name}")
    except ImportError:
        print(f"❌ {display_name} 未安裝")
        missing_packages.append(package_name)

if missing_packages:
    print("\n請執行: pip install -r requirements.txt")
    sys.exit(1)

# 檢查 3: 環境變數
print("\n[3/6] 檢查環境變數...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key and api_key != 'your_api_key_here':
    print(f"✅ ANTHROPIC_API_KEY 已設定")
else:
    print(f"⚠️  ANTHROPIC_API_KEY 未設定或使用預設值")
    print("   請編輯 .env 檔案並填入真實的 API Key")

google_client_id = os.getenv('GOOGLE_CLIENT_ID')
if google_client_id:
    print(f"✅ GOOGLE_CLIENT_ID 已設定")
else:
    print(f"ℹ️  GOOGLE_CLIENT_ID 未設定（Google Calendar 整合為選用功能）")

# 檢查 4: 資料庫初始化
print("\n[4/6] 檢查資料庫...")
try:
    from database import Database
    db = Database()
    print("✅ 資料庫初始化成功")

    # 測試基本操作
    prefs = db.get_preferences()
    print(f"✅ 偏好設定載入成功（起床時間: {prefs.get('wake_time')}）")
except Exception as e:
    print(f"❌ 資料庫錯誤: {e}")
    sys.exit(1)

# 檢查 5: AI 排程引擎
print("\n[5/6] 檢查 AI 排程引擎...")
try:
    from scheduler import AIScheduler
    if api_key and api_key != 'your_api_key_here':
        scheduler = AIScheduler()
        print("✅ AI 排程引擎初始化成功")
    else:
        print("⚠️  需要真實 API Key 才能測試 AI 排程引擎")
except Exception as e:
    print(f"❌ AI 排程引擎錯誤: {e}")

# 檢查 6: Google Calendar 客戶端
print("\n[6/6] 檢查 Google Calendar 客戶端...")
try:
    from google_cal import GoogleCalendarClient
    google_cal = GoogleCalendarClient()
    print("✅ Google Calendar 客戶端初始化成功")
except Exception as e:
    print(f"❌ Google Calendar 客戶端錯誤: {e}")

# 總結
print("\n" + "=" * 60)
print("系統檢查完成！")
print("=" * 60)

if api_key and api_key != 'your_api_key_here':
    print("\n✅ 所有核心組件已就緒")
    print("\n🚀 執行以下指令啟動應用程式：")
    print("   python app.py")
    print("\n然後開啟瀏覽器訪問：")
    print("   http://localhost:5000")
else:
    print("\n⚠️  請先設定 Anthropic API Key")
    print("\n步驟：")
    print("1. 編輯 .env 檔案")
    print("2. 將 ANTHROPIC_API_KEY 設定為你的真實 API Key")
    print("3. 重新執行此測試：python test_setup.py")

print("\n" + "=" * 60)
