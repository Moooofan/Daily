"""Google Calendar 整合模組"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import os
from config import Config


class GoogleCalendarHelper:
    """Google Calendar API 輔助類別"""

    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid'
    ]

    def __init__(self):
        """初始化 Google Calendar Helper"""
        self._config_valid = bool(Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_SECRET)

        if self._config_valid:
            self.client_config = {
                "web": {
                    "client_id": Config.GOOGLE_CLIENT_ID,
                    "client_secret": Config.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [Config.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }
        else:
            self.client_config = None
            print("⚠️ Google Calendar API 未設定（缺少 GOOGLE_CLIENT_ID 或 GOOGLE_CLIENT_SECRET）")

    def is_configured(self) -> bool:
        """檢查 Google Calendar 是否已正確設定"""
        return self._config_valid

    def get_authorization_url(self, state: str = None):
        """取得 Google OAuth 授權 URL

        Args:
            state: 可選的狀態參數，用於防止 CSRF 攻擊

        Returns:
            authorization_url: 授權 URL
            state: 狀態參數

        Raises:
            ValueError: 如果 Google Calendar API 未設定
        """
        if not self._config_valid:
            raise ValueError("Google Calendar API 未設定，請設定 GOOGLE_CLIENT_ID 和 GOOGLE_CLIENT_SECRET 環境變數")

        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return authorization_url, state

    def exchange_code_for_credentials(self, code: str):
        """用授權碼交換存取憑證

        Args:
            code: OAuth 授權碼

        Returns:
            credentials: Google OAuth2 憑證物件

        Raises:
            ValueError: 如果 Google Calendar API 未設定
        """
        if not self._config_valid:
            raise ValueError("Google Calendar API 未設定")

        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        return credentials

    def get_calendar_events(self, credentials_dict: dict, date_str: str = None):
        """取得 Google Calendar 事件

        Args:
            credentials_dict: 憑證字典（包含 token, refresh_token 等）
            date_str: 日期字串 (YYYY-MM-DD)，若為 None 則取得今天的事件

        Returns:
            events: 事件列表
        """
        # 從字典建立憑證物件
        credentials = Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret'),
            scopes=credentials_dict.get('scopes')
        )

        # 建立 Calendar API 服務
        service = build('calendar', 'v3', credentials=credentials)

        # 定義台灣時區 (UTC+8)
        taipei_tz = timezone(timedelta(hours=8))

        # 設定時間範圍
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            target_date = datetime.now()

        # 建立台灣時區的時間範圍
        time_min_local = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        time_max_local = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # 轉換為 UTC 時間（台灣時間 - 8 小時）
        time_min_utc = time_min_local.replace(tzinfo=taipei_tz).astimezone(timezone.utc)
        time_max_utc = time_max_local.replace(tzinfo=taipei_tz).astimezone(timezone.utc)

        # 取得事件
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min_utc.isoformat(),
            timeMax=time_max_utc.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # 格式化事件
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # 解析時間
            if 'T' in start:
                # 解析 UTC 時間
                start_time_utc = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_time_utc = datetime.fromisoformat(end.replace('Z', '+00:00'))

                # 轉換為台灣時間
                start_time_local = start_time_utc.astimezone(taipei_tz)
                end_time_local = end_time_utc.astimezone(taipei_tz)

                formatted_events.append({
                    'title': event.get('summary', '（無標題）'),
                    'start_time': start_time_local.strftime('%H:%M'),
                    'end_time': end_time_local.strftime('%H:%M'),
                    'date': start_time_local.strftime('%Y-%m-%d'),
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })

        return formatted_events

    def get_calendar_events_range(self, credentials_dict: dict, start_date: str, end_date: str):
        """取得指定日期範圍的 Google Calendar 事件

        Args:
            credentials_dict: 憑證字典（包含 token, refresh_token 等）
            start_date: 起始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)

        Returns:
            events: 事件列表，按日期分組
        """
        # 從字典建立憑證物件
        credentials = Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret'),
            scopes=credentials_dict.get('scopes')
        )

        # 建立 Calendar API 服務
        service = build('calendar', 'v3', credentials=credentials)

        # 定義台灣時區 (UTC+8)
        taipei_tz = timezone(timedelta(hours=8))

        # 解析起始和結束日期
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        # 建立台灣時區的時間範圍
        time_min_local = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        time_max_local = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        # 轉換為 UTC 時間
        time_min_utc = time_min_local.replace(tzinfo=taipei_tz).astimezone(timezone.utc)
        time_max_utc = time_max_local.replace(tzinfo=taipei_tz).astimezone(timezone.utc)

        # 取得事件
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min_utc.isoformat(),
            timeMax=time_max_utc.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # 格式化事件
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # 解析時間
            if 'T' in start:
                # 解析 UTC 時間
                start_time_utc = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_time_utc = datetime.fromisoformat(end.replace('Z', '+00:00'))

                # 轉換為台灣時間
                start_time_local = start_time_utc.astimezone(taipei_tz)
                end_time_local = end_time_utc.astimezone(taipei_tz)

                formatted_events.append({
                    'title': event.get('summary', '（無標題）'),
                    'start_time': start_time_local.strftime('%H:%M'),
                    'end_time': end_time_local.strftime('%H:%M'),
                    'date': start_time_local.strftime('%Y-%m-%d'),
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })

        return formatted_events

    def credentials_to_dict(self, credentials):
        """將憑證物件轉換為字典

        Args:
            credentials: Google OAuth2 憑證物件

        Returns:
            憑證字典
        """
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    def get_user_info(self, credentials):
        """取得 Google 用戶資訊

        Args:
            credentials: Google OAuth2 憑證物件

        Returns:
            用戶資訊字典（包含 id, email, name, picture）
        """
        from googleapiclient.discovery import build

        # 建立 People API 服務
        service = build('oauth2', 'v2', credentials=credentials)

        # 取得用戶資訊
        user_info = service.userinfo().get().execute()

        return {
            'id': user_info.get('id'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture')
        }
