"""應用程式配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """應用程式配置類別"""

    # Flask 設定
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Anthropic API (Claude)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Google Calendar API
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5001/oauth2callback')
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    # 資料庫
    DATABASE_PATH = 'data/daily.db'

    # 預設時間設定
    DEFAULT_WAKE_TIME = '07:00'
    DEFAULT_SLEEP_TIME = '23:00'
    DEFAULT_BREAKFAST_TIME = '07:30'
    DEFAULT_LUNCH_TIME = '12:00'
    DEFAULT_DINNER_TIME = '18:30'

    # 預設任務持續時間（分鐘）
    DEFAULT_TASK_DURATIONS = {
        '刷牙': 5,
        '洗澡': 20,
        '早餐': 30,
        '午餐': 45,
        '晚餐': 45,
        '運動': 45,
        '通勤': 30,
        '休息': 15,
    }

    # AI 時間推測規則 (中文關鍵字 -> 時間範圍)
    TIME_KEYWORDS = {
        '早上': ('08:00', '09:00'),
        '上午': ('10:00', '11:00'),
        '中午': ('12:00', '13:00'),
        '下午': ('14:00', '15:00'),
        '傍晚': ('17:00', '18:00'),
        '晚上': ('19:00', '20:00'),
    }

    # 任務類型預估時間（分鐘）
    TASK_TYPE_DURATIONS = {
        'quick': (5, 15),      # 碎片任務
        'daily': (30, 120),    # 日待辦
        'weekly': (60, 240),   # 週待辦
        'monthly': (120, 480), # 月待辦
    }
