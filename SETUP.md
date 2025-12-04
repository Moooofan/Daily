# 設定指南

## 1️⃣ 設定 Anthropic API Key

1. 前往 [Anthropic Console](https://console.anthropic.com/)
2. 登入並建立 API Key
3. 複製 API Key

## 2️⃣ 設定 Google Calendar API（選用）

### 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Calendar API：
   - 在左側選單點擊「API 和服務」→「程式庫」
   - 搜尋「Google Calendar API」
   - 點擊「啟用」

### 建立 OAuth 2.0 憑證

1. 在「API 和服務」→「憑證」
2. 點擊「建立憑證」→「OAuth 用戶端 ID」
3. 如果是第一次，需要先設定「OAuth 同意畫面」：
   - 選擇「外部」
   - 填寫應用程式名稱（例如：Daily Schedule AI）
   - 使用者支援電子郵件：填入你的 email
   - 開發人員聯絡資訊：填入你的 email
   - 儲存並繼續
   - 在「範圍」頁面，點擊「新增或移除範圍」
   - 搜尋並勾選 `Google Calendar API` 的 `calendar.readonly`
   - 儲存並繼續
   - 在「測試使用者」頁面，新增你的 Google 帳號
   - 儲存並繼續
4. 回到「憑證」頁面，再次點擊「建立憑證」→「OAuth 用戶端 ID」
5. 應用程式類型：選擇「網頁應用程式」
6. 名稱：隨意填寫（例如：Daily Schedule Web）
7. 已授權的重新導向 URI：新增
   ```
   http://localhost:5000/oauth2callback
   ```
8. 點擊「建立」
9. 複製「用戶端 ID」和「用戶端密碼」

## 3️⃣ 建立 .env 檔案

在專案根目錄建立 `.env` 檔案：

```bash
# Anthropic API Key（必填）
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Google Calendar API（選用，如需整合 Google Calendar）
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret

# Flask 設定（使用預設值即可）
FLASK_SECRET_KEY=your_random_secret_key_here
FLASK_DEBUG=True
```

## 4️⃣ 執行應用程式

```bash
python app.py
```

開啟瀏覽器訪問：
```
http://localhost:5000
```

## 5️⃣ 使用步驟

### 第一次使用

1. **連接 Google Calendar**（選用）
   - 點擊「連接 Google Calendar」按鈕
   - 完成 OAuth 授權流程
   - 授權後會自動導回應用程式

2. **設定偏好**
   - 點擊「⚙️ 偏好設定」
   - 設定起床時間、就寢時間、用餐時間等
   - 點擊「儲存設定」

3. **新增任務**
   - 點擊「+ 新增任務」
   - 填寫任務資訊（名稱、時長、優先級等）
   - 點擊「新增」

4. **生成行程**
   - 點擊「🤖 生成行程」按鈕
   - AI 會根據你的任務、Google Calendar 事件、偏好設定自動規劃行程
   - 查看完整的分鐘級行程表

### 日常使用

1. 早上打開應用程式
2. 檢查並新增今日待辦任務
3. 點擊「生成行程」獲得完整規劃
4. 如有變動，可重新點擊「生成行程」更新

## 🔧 進階設定

### 自訂預設任務時長

編輯 [config.py](config.py:29)：

```python
DEFAULT_TASK_DURATIONS = {
    '刷牙': 5,
    '洗澡': 20,
    '早餐': 30,
    # 新增你的自訂項目
}
```

### 修改 AI 提示詞

編輯 [scheduler.py](scheduler.py:46) 的 `_build_scheduling_prompt` 方法來調整 AI 排程邏輯。

## 📱 在手機上使用

### iOS/Android

1. 在手機瀏覽器開啟 `http://你的電腦IP:5000`
2. iOS：點擊分享 → 加入主畫面
3. Android：選單 → 安裝應用程式

### 遠端訪問（進階）

如需從外網訪問，可使用：
- [ngrok](https://ngrok.com/)
- [Tailscale](https://tailscale.com/)
- 部署到雲端平台（Heroku, Railway, Vercel 等）

## ⚠️ 注意事項

1. **API Key 安全**：
   - 不要將 `.env` 檔案上傳到 Git
   - 不要分享你的 API Key

2. **Google Calendar 授權**：
   - 第一次連接時，Google 可能會顯示「應用程式未經驗證」警告
   - 這是因為應用程式還在測試模式
   - 點擊「進階」→「前往 Daily Schedule AI（不安全）」繼續

3. **資料儲存**：
   - 所有資料儲存在本地 SQLite 資料庫（`data/daily.db`）
   - 定期備份資料庫檔案

## 🐛 常見問題

### Q: 顯示「需要提供 Anthropic API Key」
A: 請確認 `.env` 檔案中的 `ANTHROPIC_API_KEY` 已正確設定

### Q: Google Calendar 連接失敗
A:
- 確認 OAuth 憑證設定正確
- 檢查重新導向 URI 是否為 `http://localhost:5000/oauth2callback`
- 確認已將自己的帳號加入測試使用者

### Q: 生成行程時出錯
A:
- 檢查 Anthropic API Key 是否有效
- 確認有足夠的 API 額度
- 查看終端機的錯誤訊息

## 💡 使用技巧

1. **優先級設定**：高優先級任務會優先被排入行程
2. **偏好時間**：設定偏好時間可以讓 AI 在該時段附近安排任務
3. **即時重排**：完成或延遲任務後，重新生成行程即可更新
4. **類別管理**：使用類別（工作、學習、個人等）來組織任務
