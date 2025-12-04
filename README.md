# Daily Schedule AI

可即時生成並調整的每日行程系統

## 功能特點

- ✅ 整合 Google Calendar 正式行程
- ✅ 管理日常微任務（刷牙、通勤、用餐等）
- ✅ AI 自動規劃完整日程表
- ✅ 即時重排機制
- ✅ 全日可視化排程（分鐘級）
- ✅ 跨平台操作（手機、電腦）

## 技術架構

- **後端**: Python Flask + SQLite
- **AI**: Claude API (Anthropic)
- **整合**: Google Calendar API
- **前端**: HTML + JavaScript + FullCalendar

## 安裝與設定

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

建立 `.env` 檔案：

```
ANTHROPIC_API_KEY=your_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 3. 執行應用

```bash
python app.py
```

開啟瀏覽器訪問 `http://localhost:5000`

## 使用方式

1. 點擊「連接 Google Calendar」授權
2. 在「我的任務」區域新增待辦事項
3. 點擊「生成今日行程」按鈕
4. 查看完整的分鐘級行程表
5. 拖曳調整或標記完成後，點擊「重新排程」

## 專案結構

```
daily/
├── app.py                 # Flask 主程式
├── database.py            # 資料庫模型
├── google_cal.py          # Google Calendar 整合
├── scheduler.py           # AI 排程引擎
├── config.py              # 設定檔
├── requirements.txt       # Python 依賴
├── static/                # 靜態檔案
│   ├── css/
│   └── js/
├── templates/             # HTML 模板
│   └── index.html
└── data/                  # 資料庫檔案
    └── daily.db
```
