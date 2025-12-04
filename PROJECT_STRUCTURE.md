# 專案結構說明

## 📁 檔案結構

```
daily/
├── README.md                 # 專案說明
├── QUICKSTART.md            # 快速開始指南
├── SETUP.md                 # 詳細設定說明
├── PROJECT_STRUCTURE.md     # 本檔案 - 專案結構說明
│
├── .env                     # 環境變數（包含 API Keys）
├── .env.example             # 環境變數範例
├── .gitignore              # Git 忽略清單
├── requirements.txt         # Python 依賴套件
├── test_setup.py           # 系統檢查腳本
│
├── app.py                   # Flask 主應用程式（路由與 API）
├── config.py               # 應用程式配置
├── database.py             # 資料庫模型與操作
├── scheduler.py            # AI 排程引擎（Claude API）
├── google_cal.py           # Google Calendar API 整合
│
├── templates/              # HTML 模板
│   └── index.html          # 主介面
│
├── static/                 # 靜態資源
│   ├── css/
│   │   └── style.css       # 樣式表
│   └── js/
│       └── app.js          # 前端 JavaScript
│
└── data/                   # 資料目錄（執行時自動建立）
    └── daily.db            # SQLite 資料庫
```

## 🔧 核心模組說明

### app.py - Flask 主應用程式

**職責**：HTTP 路由、API 端點、請求處理

**主要端點**：
- `GET /` - 首頁
- `POST /api/tasks` - 新增任務
- `GET /api/tasks` - 取得任務列表
- `POST /api/schedule/generate` - 生成排程
- `GET /api/google/auth-url` - 取得 Google OAuth URL
- `GET /oauth2callback` - Google OAuth 回調

### database.py - 資料庫層

**職責**：SQLite 資料庫操作

**資料表**：
- `tasks` - 任務表
  - id, title, duration, priority, category, is_routine, preferred_time
- `schedules` - 行程表
  - id, date, schedule_data (JSON), created_at
- `user_preferences` - 使用者偏好
  - wake_time, sleep_time, breakfast_time, lunch_time, dinner_time

**主要方法**：
- `add_task()` / `get_tasks()` / `update_task()` / `delete_task()`
- `save_schedule()` / `get_schedule()`
- `get_preferences()` / `update_preferences()`

### scheduler.py - AI 排程引擎

**職責**：使用 Claude API 生成智能排程

**核心流程**：
1. 接收任務、行事曆事件、使用者偏好
2. 建構結構化提示詞
3. 呼叫 Claude API
4. 解析回應並返回排程

**關鍵方法**：
- `generate_schedule()` - 主要排程生成方法
- `_build_scheduling_prompt()` - 建構 AI 提示詞
- `_parse_schedule_response()` - 解析 AI 回應
- `_create_basic_schedule()` - 備案排程（當 AI 失敗時）

### google_cal.py - Google Calendar 整合

**職責**：Google Calendar API 認證與事件讀取

**OAuth 流程**：
1. `get_authorization_url()` - 取得授權 URL
2. 使用者在 Google 授權
3. `handle_oauth_callback()` - 處理回調並儲存 token

**主要方法**：
- `load_credentials()` - 載入已儲存的認證
- `get_events()` - 取得指定日期的事件
- `disconnect()` - 中斷連接

### config.py - 配置管理

**職責**：集中管理應用程式配置

**配置項目**：
- API Keys
- 資料庫路徑
- 預設時間設定
- 預設任務持續時間

## 🎨 前端說明

### templates/index.html

單頁應用（SPA）包含：
- 任務管理介面
- 行程顯示區
- 設定面板
- Modal 對話框

### static/css/style.css

樣式特點：
- 響應式設計（手機/電腦適配）
- 漸變背景
- 卡片式 UI
- 平滑動畫效果

### static/js/app.js

前端邏輯：
- API 呼叫（fetch）
- DOM 操作
- 狀態管理
- 通知系統

## 🗄 資料流

### 生成排程流程

```
使用者點擊「生成行程」
    ↓
前端 app.js → POST /api/schedule/generate
    ↓
Flask app.py → 收集資料
    ↓
├─ database.py → 取得任務
├─ database.py → 取得偏好設定
└─ google_cal.py → 取得 Calendar 事件
    ↓
scheduler.py → 呼叫 Claude API
    ↓
← 返回排程 JSON
    ↓
database.py → 儲存排程
    ↓
← 回傳給前端
    ↓
app.js → 渲染時間表
```

### OAuth 認證流程

```
使用者點擊「連接 Google Calendar」
    ↓
GET /api/google/auth-url
    ↓
← 返回 Google OAuth URL
    ↓
導向 Google 授權頁面
    ↓
使用者授權
    ↓
Google 導回 /oauth2callback?code=xxx
    ↓
google_cal.py → 兌換 token
    ↓
儲存 token.json
    ↓
← 導回首頁
```

## 🔐 安全性考量

1. **API Key 保護**
   - 使用 `.env` 儲存敏感資訊
   - `.gitignore` 排除 `.env`

2. **OAuth Token**
   - 儲存在本地 `token.json`
   - 不上傳到版本控制

3. **資料庫**
   - SQLite 檔案本地儲存
   - 定期備份建議

## 📊 資料庫結構

### tasks 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INTEGER | 主鍵 |
| title | TEXT | 任務名稱 |
| duration | INTEGER | 持續時間（分鐘）|
| priority | INTEGER | 優先級 (0-3) |
| category | TEXT | 類別 |
| is_routine | BOOLEAN | 是否為例行任務 |
| preferred_time | TEXT | 偏好時間 |
| created_at | TIMESTAMP | 建立時間 |

### schedules 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INTEGER | 主鍵 |
| date | TEXT | 日期（ISO 格式）|
| schedule_data | TEXT | 排程資料（JSON）|
| created_at | TIMESTAMP | 建立時間 |

### user_preferences 表

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INTEGER | 主鍵 |
| wake_time | TEXT | 起床時間 |
| sleep_time | TEXT | 就寢時間 |
| breakfast_time | TEXT | 早餐時間 |
| lunch_time | TEXT | 午餐時間 |
| dinner_time | TEXT | 晚餐時間 |
| commute_duration | INTEGER | 通勤時間 |
| buffer_time | INTEGER | 緩衝時間 |

## 🚀 擴展建議

### 短期改進

1. **通知功能**
   - 整合瀏覽器通知 API
   - 提醒即將開始的任務

2. **匯出功能**
   - 匯出為 iCal 格式
   - 匯出為 PDF

3. **歷史記錄**
   - 查看過去的排程
   - 統計分析

### 中期功能

1. **多使用者支援**
   - 使用者認證系統
   - 個人資料隔離

2. **行動 App**
   - PWA 改造
   - 原生 App 開發

3. **進階 AI 功能**
   - 學習使用者習慣
   - 自動調整優先級
   - 預測任務時長

### 長期願景

1. **團隊協作**
   - 共享行程
   - 任務委派

2. **智能建議**
   - 最佳工作時段推薦
   - 健康提醒

3. **整合生態**
   - Notion、Todoist 整合
   - Slack、Teams 通知
   - 穿戴裝置同步
