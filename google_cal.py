"""Google Calendar API 整合"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from config import Config


class GoogleCalendarClient:
    """Google Calendar 客戶端"""

    def __init__(self):
        self.creds = None
        self.service = None
        self.token_path = 'token.json'

    def is_authenticated(self) -> bool:
        """檢查是否已認證"""
        return self.creds is not None and self.creds.valid

    def load_credentials(self) -> bool:
        """載入已儲存的認證資訊"""
        if os.path.exists(self.token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(
                    self.token_path,
                    Config.GOOGLE_SCOPES
                )

                # 如果 token 過期，嘗試刷新
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    self._save_credentials()

                if self.creds and self.creds.valid:
                    self.service = build('calendar', 'v3', credentials=self.creds)
                    return True
            except Exception as e:
                print(f"載入認證失敗: {e}")
                return False

        return False

    def _save_credentials(self):
        """儲存認證資訊"""
        if self.creds:
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

    def get_authorization_url(self) -> str:
        """取得 OAuth 授權 URL"""
        if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
            raise ValueError("請先在 .env 設定 Google OAuth 憑證")

        # 建立 OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": Config.GOOGLE_CLIENT_ID,
                    "client_secret": Config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=Config.GOOGLE_SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # 儲存 state 用於驗證
        with open('oauth_state.json', 'w') as f:
            json.dump({'state': state}, f)

        return authorization_url

    def handle_oauth_callback(self, code: str) -> bool:
        """處理 OAuth 回調"""
        try:
            # 讀取 state
            with open('oauth_state.json', 'r') as f:
                state_data = json.load(f)

            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": Config.GOOGLE_CLIENT_ID,
                        "client_secret": Config.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
                    }
                },
                scopes=Config.GOOGLE_SCOPES,
                redirect_uri=Config.GOOGLE_REDIRECT_URI
            )

            flow.fetch_token(code=code)
            self.creds = flow.credentials
            self._save_credentials()

            # 建立服務
            self.service = build('calendar', 'v3', credentials=self.creds)

            # 清理 state 檔案
            if os.path.exists('oauth_state.json'):
                os.remove('oauth_state.json')

            return True

        except Exception as e:
            print(f"OAuth 回調處理失敗: {e}")
            return False

    def get_events(self, target_date: date = None) -> List[Dict]:
        """
        取得指定日期的行事曆事件

        Args:
            target_date: 目標日期，預設為今天

        Returns:
            事件列表
        """
        if not self.service:
            if not self.load_credentials():
                return []

        if target_date is None:
            target_date = date.today()

        # 設定時間範圍（當天 00:00 到 23:59）
        time_min = datetime.combine(target_date, datetime.min.time()).isoformat() + 'Z'
        time_max = datetime.combine(target_date, datetime.max.time()).isoformat() + 'Z'

        try:
            # 呼叫 Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # 轉換為統一格式
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                # 處理全天事件
                if 'T' not in start:
                    start_time = '00:00'
                    end_time = '23:59'
                else:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    start_time = start_dt.strftime('%H:%M')
                    end_time = end_dt.strftime('%H:%M')

                formatted_events.append({
                    'title': event.get('summary', '（無標題）'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'source': 'google_calendar'
                })

            return formatted_events

        except Exception as e:
            print(f"取得行事曆事件失敗: {e}")
            return []

    def disconnect(self):
        """中斷連線並刪除認證"""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self.creds = None
        self.service = None
