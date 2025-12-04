"""AI 排程引擎 - 使用 Claude API 生成智能行程"""
from typing import List, Dict, Optional
from datetime import datetime, date, time, timedelta
import json
from anthropic import Anthropic
from config import Config


class AIScheduler:
    """AI 排程引擎"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("需要提供 Anthropic API Key")
        self.client = Anthropic(api_key=self.api_key)

    def generate_schedule(
        self,
        tasks: List[Dict],
        calendar_events: List[Dict],
        preferences: Dict,
        target_date: date = None
    ) -> List[Dict]:
        """
        生成每日行程

        Args:
            tasks: 待辦任務列表
            calendar_events: Google Calendar 事件
            preferences: 使用者偏好設定
            target_date: 目標日期

        Returns:
            排程列表，每個項目包含 title, start_time, end_time, type, source
        """
        if target_date is None:
            target_date = date.today()

        # 準備提示詞
        prompt = self._build_scheduling_prompt(tasks, calendar_events, preferences, target_date)

        # 呼叫 Claude API
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 解析回應
            schedule_text = response.content[0].text
            schedule = self._parse_schedule_response(schedule_text)

            return schedule

        except Exception as e:
            print(f"AI 排程錯誤: {e}")
            # 返回基礎排程作為備案
            return self._create_basic_schedule(tasks, calendar_events, preferences)

    def _build_scheduling_prompt(
        self,
        tasks: List[Dict],
        calendar_events: List[Dict],
        preferences: Dict,
        target_date: date
    ) -> str:
        """建構給 AI 的提示詞"""

        date_str = target_date.strftime('%Y年%m月%d日 (%A)')
        day_of_week = target_date.strftime('%A')

        # 將日期轉換為中文星期
        weekday_map = {
            'Monday': '星期一',
            'Tuesday': '星期二',
            'Wednesday': '星期三',
            'Thursday': '星期四',
            'Friday': '星期五',
            'Saturday': '星期六',
            'Sunday': '星期日'
        }
        date_display = target_date.strftime('%Y年%m月%d日') + f" ({weekday_map.get(day_of_week, day_of_week)})"

        prompt = f"""你是一個專業的時間管理 AI 助手，請幫我規劃 {date_display} 的完整行程。

## 使用者偏好設定
- 起床時間：{preferences.get('wake_time', '07:00')}
- 就寢時間：{preferences.get('sleep_time', '23:00')}
- 早餐時間：{preferences.get('breakfast_time', '07:30')}
- 午餐時間：{preferences.get('lunch_time', '12:00')}
- 晚餐時間：{preferences.get('dinner_time', '18:30')}
- 緩衝時間：{preferences.get('buffer_time', 10)} 分鐘

## Google Calendar 已排定事件
"""

        if calendar_events:
            for event in calendar_events:
                start = event.get('start_time', '')
                end = event.get('end_time', '')
                title = event.get('title', '未命名活動')
                prompt += f"- {start} - {end}: {title}\n"
        else:
            prompt += "（無固定行程）\n"

        prompt += "\n## 待辦任務清單\n"

        if tasks:
            for task in tasks:
                title = task.get('title', '')
                duration = task.get('duration', 30)
                priority = task.get('priority', 0)
                preferred_time = task.get('preferred_time', '')
                category = task.get('category', 'other')

                priority_text = "高" if priority >= 3 else "中" if priority >= 1 else "低"
                time_hint = f"，建議時間：{preferred_time}" if preferred_time else ""

                prompt += f"- {title}（{duration}分鐘，優先級：{priority_text}，類別：{category}{time_hint}）\n"
        else:
            prompt += "（無待辦任務）\n"

        prompt += """
## 排程要求

1. **包含所有日常微任務**：刷牙、洗澡、早餐、午餐、晚餐、通勤等基本生活活動都要納入
2. **遵守固定行程**：Google Calendar 的事件不可更動
3. **優先級排序**：高優先級任務優先安排，但要考慮時間合理性
4. **緩衝時間**：活動之間留適當緩衝
5. **彈性安排**：在空檔時間合理分配任務
6. **時間連貫性**：從起床到就寢，每個時段都要有安排

## 輸出格式

請以 JSON 陣列格式回應，每個行程項目包含：
- title: 活動名稱
- start_time: 開始時間（HH:MM 格式）
- end_time: 結束時間（HH:MM 格式）
- type: 類型（calendar/task/routine/break）
- source: 來源（task_id 或 "calendar" 或 "auto"）
- description: 簡短說明（選填）

範例：
```json
[
  {
    "title": "起床與刷牙",
    "start_time": "07:00",
    "end_time": "07:15",
    "type": "routine",
    "source": "auto",
    "description": "開始新的一天"
  },
  {
    "title": "早餐",
    "start_time": "07:30",
    "end_time": "08:00",
    "type": "routine",
    "source": "auto"
  }
]
```

請直接輸出 JSON 格式，不要其他文字說明。
"""

        return prompt

    def _parse_schedule_response(self, response_text: str) -> List[Dict]:
        """解析 AI 回應的排程"""
        try:
            # 移除可能的 markdown 標記
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # 解析 JSON
            schedule = json.loads(response_text)

            # 驗證格式
            for item in schedule:
                if not all(k in item for k in ['title', 'start_time', 'end_time']):
                    raise ValueError("排程項目缺少必要欄位")

                # 確保有預設值
                item.setdefault('type', 'task')
                item.setdefault('source', 'auto')
                item.setdefault('description', '')

            return schedule

        except json.JSONDecodeError as e:
            print(f"JSON 解析錯誤: {e}")
            print(f"回應內容: {response_text}")
            return []
        except Exception as e:
            print(f"解析錯誤: {e}")
            return []

    def _create_basic_schedule(
        self,
        tasks: List[Dict],
        calendar_events: List[Dict],
        preferences: Dict
    ) -> List[Dict]:
        """建立基礎排程（當 AI 失敗時的備案）"""
        schedule = []

        wake_time = preferences.get('wake_time', '07:00')
        breakfast_time = preferences.get('breakfast_time', '07:30')
        lunch_time = preferences.get('lunch_time', '12:00')
        dinner_time = preferences.get('dinner_time', '18:30')
        sleep_time = preferences.get('sleep_time', '23:00')

        # 加入基本日常活動
        schedule.append({
            'title': '起床',
            'start_time': wake_time,
            'end_time': self._add_minutes(wake_time, 15),
            'type': 'routine',
            'source': 'auto'
        })

        schedule.append({
            'title': '早餐',
            'start_time': breakfast_time,
            'end_time': self._add_minutes(breakfast_time, 30),
            'type': 'routine',
            'source': 'auto'
        })

        schedule.append({
            'title': '午餐',
            'start_time': lunch_time,
            'end_time': self._add_minutes(lunch_time, 45),
            'type': 'routine',
            'source': 'auto'
        })

        schedule.append({
            'title': '晚餐',
            'start_time': dinner_time,
            'end_time': self._add_minutes(dinner_time, 45),
            'type': 'routine',
            'source': 'auto'
        })

        # 加入 Google Calendar 事件
        for event in calendar_events:
            schedule.append({
                'title': event['title'],
                'start_time': event['start_time'],
                'end_time': event['end_time'],
                'type': 'calendar',
                'source': 'calendar',
                'description': event.get('description', '')
            })

        # 簡單加入任務（按優先級）
        sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 0), reverse=True)
        current_time = self._add_minutes(breakfast_time, 30)

        for task in sorted_tasks[:5]:  # 只加入前5個任務
            duration = task.get('duration', 30)
            schedule.append({
                'title': task['title'],
                'start_time': current_time,
                'end_time': self._add_minutes(current_time, duration),
                'type': 'task',
                'source': f"task_{task['id']}"
            })
            current_time = self._add_minutes(current_time, duration + 10)

        # 排序
        schedule.sort(key=lambda x: x['start_time'])

        return schedule

    def _add_minutes(self, time_str: str, minutes: int) -> str:
        """時間字串加上分鐘數"""
        try:
            t = datetime.strptime(time_str, '%H:%M')
            new_time = t + timedelta(minutes=minutes)
            return new_time.strftime('%H:%M')
        except:
            return time_str
