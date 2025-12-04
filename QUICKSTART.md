# 🚀 快速開始

只需 3 步驟，立即使用 Daily Schedule AI！

## Step 1: 設定 API Key

編輯 `.env` 檔案，填入你的 Anthropic API Key：

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

> 💡 如何取得 API Key？
> 1. 前往 https://console.anthropic.com/
> 2. 登入並建立 API Key
> 3. 複製 Key 並貼到 `.env`

## Step 2: 啟動應用程式

```bash
python app.py
```

看到這個訊息就成功了：
```
============================================================
Daily Schedule AI 正在啟動...
============================================================
開啟瀏覽器訪問: http://localhost:5000
============================================================
```

## Step 3: 開始使用

開啟瀏覽器訪問 `http://localhost:5000`

### 首次使用流程

1. **新增任務**
   - 點擊「+ 新增任務」
   - 例如：「寫報告」（60分鐘）、「運動」（45分鐘）

2. **設定偏好**（選用）
   - 點擊「⚙️ 偏好設定」
   - 調整起床時間、用餐時間等

3. **生成行程**
   - 點擊「🤖 生成行程」
   - 等待 AI 規劃完成
   - 查看完整的時間表！

## 🎉 完成！

你現在可以：
- ✅ 新增、編輯、刪除任務
- ✅ AI 自動規劃每日行程
- ✅ 查看分鐘級時間表
- ✅ 即時重新排程

## 📱 在手機上使用

1. 確保手機和電腦在同一個 Wi-Fi
2. 找到電腦的 IP 位址：
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "

   # Windows
   ipconfig
   ```
3. 手機瀏覽器開啟 `http://電腦IP:5000`

## ➕ 進階功能（選用）

### 連接 Google Calendar

詳細步驟請參考 [SETUP.md](SETUP.md)

1. 在 Google Cloud Console 設定 OAuth
2. 填入 `.env` 的 `GOOGLE_CLIENT_ID` 和 `GOOGLE_CLIENT_SECRET`
3. 在應用程式中點擊「連接 Google Calendar」

## ❓ 遇到問題？

查看 [SETUP.md](SETUP.md) 的「常見問題」區塊

或檢查：
- ✅ `.env` 檔案中的 API Key 是否正確
- ✅ Python 套件是否已安裝（`pip install -r requirements.txt`）
- ✅ 終端機的錯誤訊息

---

**享受你的智能行程規劃體驗！** 🎯
