"""AI 助手 - 處理語音辨識和自動排程"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from openai import OpenAI
from config import Config
import json
import os
import httpx


class AIHelper:
    """AI 助手"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("需要提供 OpenAI API Key")

        # 清除可能導致問題的 proxy 環境變數
        http_client = httpx.Client()
        self.client = OpenAI(api_key=self.api_key, http_client=http_client)

    def _clean_json_response(self, text: str) -> str:
        """移除 AI 回應中的 markdown 標記"""
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        return text.strip()

    def process_voice_input(self, text: str) -> Dict:
        """
        處理語音輸入，自動分類並整理為待辦或排程

        Args:
            text: 語音轉文字的結果

        Returns:
            {
                'todos': [
                    {'content': '待辦1', 'type': 'daily', 'estimated_minutes': 30, 'date': '2025-01-15'},
                    {'content': '待辦2', 'type': 'quick', 'estimated_minutes': 10, 'date': '2025-01-16'},
                    ...
                ],
                'schedules': [
                    {'title': '排程1', 'start_time': '09:00', 'end_time': '10:00', 'date': '2025-01-15'},
                    ...
                ]
            }
        """
        from datetime import datetime, timedelta

        # 計算今天、明天、後天的日期
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        tomorrow_str = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after_tomorrow_str = (today + timedelta(days=2)).strftime('%Y-%m-%d')

        # 計算本週和下週的日期範圍
        weekday = today.weekday()  # 0=週一, 6=週日
        this_week_start = (today - timedelta(days=weekday)).strftime('%Y-%m-%d')
        this_week_end = (today + timedelta(days=6-weekday)).strftime('%Y-%m-%d')
        next_week_start = (today + timedelta(days=7-weekday)).strftime('%Y-%m-%d')
        next_week_end = (today + timedelta(days=13-weekday)).strftime('%Y-%m-%d')

        prompt = f"""解析使用者的行程輸入，輸出 JSON 格式的待辦和排程。

## 核心規則
1. 每一行輸入只產生一個 schedule（絕對不重複）
2. 完全保留使用者的時間（9:00 就是 09:00）
3. 「XX/XX（X）行程」是日期標題，不要建立 schedule

## 日期處理
- 「11/14」→ "2025-11-14"
- 「今天」→ "{today_str}"
- 「明天」→ "{tomorrow_str}"
- 「後天」→ "{day_after_tomorrow_str}"

**結構化格式**：
```
11/14（五）行程         ← 日期標題
9:00~13:00 公司法       ← 屬於 2025-11-14
13:00~14:00 休息        ← 屬於 2025-11-14

11/15（六）行程         ← 新日期標題
8:00~8:30 練球          ← 屬於 2025-11-15
```

## 時間格式
- 「9:00~13:00」→ "09:00" to "13:00"
- 「下午3點」→ "15:00"
- 「晚上7點半」→ "19:30"

## 括號處理
- **任務**（買XX、洗XX、做XX）→ 提取到 todos
- **建議**（可以...、吃飽後可以...）→ 保留在 schedule title

## 任務分類
- **quick**：5-15分鐘（買牛奶、印考卷、洗碗）
- **daily**：30-120分鐘（寫報告、做簡報、讀書）
- **weekly/monthly**：本週/本月內完成

## 輸出格式
{{
    "todos": [{{"content": "買牛奶", "type": "quick", "estimated_minutes": 10, "date": "{today_str}"}}],
    "schedules": [{{"title": "開會", "start_time": "09:00", "end_time": "10:00", "date": "{today_str}"}}]
}}

## 範例
輸入：
「11/14（五）行程
9:00~13:00 公司法
17:00~17:30 回家（買牛奶、買衛生紙）
18:30~20:00 空檔（可以拿來寫程式）（洗杯子）

11/15（六）行程
8:00~8:30 練球（翁買早餐）
8:30~10:00 吃早餐（吃飽後可以晃晃政大）」

輸出：
{{
    "todos": [
        {{"content": "買牛奶", "type": "quick", "estimated_minutes": 10, "date": "2025-11-14"}},
        {{"content": "買衛生紙", "type": "quick", "estimated_minutes": 5, "date": "2025-11-14"}},
        {{"content": "洗杯子", "type": "quick", "estimated_minutes": 5, "date": "2025-11-14"}},
        {{"content": "翁買早餐", "type": "quick", "estimated_minutes": 15, "date": "2025-11-15"}}
    ],
    "schedules": [
        {{"title": "公司法", "start_time": "09:00", "end_time": "13:00", "date": "2025-11-14"}},
        {{"title": "回家", "start_time": "17:00", "end_time": "17:30", "date": "2025-11-14"}},
        {{"title": "空檔（可以拿來寫程式）", "start_time": "18:30", "end_time": "20:00", "date": "2025-11-14"}},
        {{"title": "練球", "start_time": "08:00", "end_time": "08:30", "date": "2025-11-15"}},
        {{"title": "吃早餐（吃飽後可以晃晃政大）", "start_time": "08:30", "end_time": "10:00", "date": "2025-11-15"}}
    ]
}}

## 使用者輸入
「{text}」

**只輸出 JSON，無其他文字**："""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.choices[0].message.content
            result_text = self._clean_json_response(result_text)
            result = json.loads(result_text)

            return {
                'todos': result.get('todos', []),
                'schedules': result.get('schedules', [])
            }

        except Exception as e:
            print(f"AI 處理錯誤: {e}")
            # 備案：將所有內容作為待辦事項(預設為日待辦)
            return {
                'todos': [{'content': text, 'type': 'daily', 'estimated_minutes': 30}],
                'schedules': []
            }

    def generate_daily_schedule(self, todos: List, date_str: str = None, current_time: str = None) -> List[Dict]:
        """
        根據待辦事項生成今日排程

        Args:
            todos: 待辦事項列表（可以是字串列表或字典列表）
            date_str: 日期字串 (YYYY-MM-DD)
            current_time: 當前時間 (HH:MM)，如果為 None 則使用系統當前時間

        Returns:
            排程列表，每項包含 title, start_time, end_time
        """
        now = datetime.now()

        if not date_str:
            date_str = now.strftime('%Y-%m-%d')

        if not current_time:
            current_time = now.strftime('%H:%M')

        if not todos:
            return self._generate_default_schedule()

        # 處理待辦事項格式（兼容字串和字典格式）
        formatted_todos = []
        for todo in todos:
            if isinstance(todo, dict):
                content = todo.get('content', '')
                estimated_minutes = todo.get('estimated_minutes', 30)
                formatted_todos.append(f"- {content} (預計 {estimated_minutes} 分鐘)")
            else:
                formatted_todos.append(f"- {todo} (預計 30 分鐘)")

        todos_text = '\n'.join(formatted_todos)

        # 計算當前小時，判斷是否需要加入基本活動
        current_hour = int(current_time.split(':')[0])
        current_minute = int(current_time.split(':')[1])

        # 計算到 23:00 還有多少分鐘
        available_minutes = (23 - current_hour) * 60 - current_minute

        # 根據當前時間調整提示詞
        if current_hour < 8:
            time_guidance = "從早上開始安排，包含起床、早餐等日常活動"
        elif current_hour < 12:
            time_guidance = "從上午開始安排，可省略起床、早餐"
        elif current_hour < 14:
            time_guidance = "從中午開始安排，可包含午餐"
        elif current_hour < 18:
            time_guidance = "從下午開始安排，可省略午餐"
        elif current_hour < 22:
            time_guidance = "從傍晚開始安排，可包含晚餐"
        else:
            time_guidance = "從晚上開始安排，優先處理緊急事項"

        prompt = f"""請為以下待辦事項規劃今日行程（{date_str}）。

當前時間：{current_time}
可用時間：約 {available_minutes} 分鐘（到 23:00）

待辦事項：
{todos_text}

規劃要求：
1. 時間範圍：從 {current_time} 開始到 23:00 結束
2. {time_guidance}
3. **嚴格按照每個待辦事項的預計時間**來分配時間段（例如預計30分鐘的任務就分配30分鐘）
4. 時間分配要連貫，避免大空檔
5. 適當加入休息時間（每工作1-2小時休息10-15分鐘）
6. 如果時間不夠完成所有待辦：
   - 優先安排重要且緊急的事項
   - 將無法完成的事項留到明天或之後
   - 在 JSON 中只輸出今天能完成的排程

輸出格式（JSON）：
[
    {{"title": "午餐", "start_time": "12:00", "end_time": "13:00"}},
    {{"title": "寫報告", "start_time": "13:00", "end_time": "14:30"}},
    {{"title": "休息", "start_time": "14:30", "end_time": "14:45"}},
    ...
]

只輸出 JSON 陣列，不要其他文字。所有排程必須在 {current_time} 之後開始，並在 23:00 之前結束。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.choices[0].message.content
            result_text = self._clean_json_response(result_text)
            schedule = json.loads(result_text)

            return schedule

        except Exception as e:
            print(f"生成排程錯誤: {e}")
            return self._generate_default_schedule()

    def _generate_default_schedule(self) -> List[Dict]:
        """生成預設排程（當 AI 失敗時）"""
        return [
            {"title": "起床", "start_time": "07:00", "end_time": "07:30"},
            {"title": "早餐", "start_time": "07:30", "end_time": "08:00"},
            {"title": "工作時段", "start_time": "09:00", "end_time": "12:00"},
            {"title": "午餐", "start_time": "12:00", "end_time": "13:00"},
            {"title": "工作時段", "start_time": "14:00", "end_time": "18:00"},
            {"title": "晚餐", "start_time": "18:30", "end_time": "19:30"},
            {"title": "自由時間", "start_time": "20:00", "end_time": "22:00"},
            {"title": "準備就寢", "start_time": "22:30", "end_time": "23:00"},
        ]

    def suggest_now_activity(self, current_schedules: List[Dict], uncompleted_todos: Dict[str, List[Dict]],
                            current_time: str) -> Dict:
        """
        根據當前時間和排程，建議現在可以做的事

        Args:
            current_schedules: 今日排程列表
            uncompleted_todos: 未完成待辦（按類型分組）
            current_time: 當前時間 (HH:MM)

        Returns:
            {
                'suggestion': '建議活動',
                'reason': '原因說明',
                'available_slots': [{'start': 'HH:MM', 'end': 'HH:MM'}, ...]
            }
        """
        # 找出當前時段的空檔
        now_minutes = self._time_to_minutes(current_time)
        current_activity = None
        next_activity = None

        for schedule in sorted(current_schedules, key=lambda x: x['start_time']):
            start_min = self._time_to_minutes(schedule['start_time'])
            end_min = self._time_to_minutes(schedule['end_time'])

            if start_min <= now_minutes < end_min:
                current_activity = schedule
            elif start_min > now_minutes and next_activity is None:
                next_activity = schedule

        # 計算可用時間
        if next_activity:
            available_minutes = self._time_to_minutes(next_activity['start_time']) - now_minutes
        else:
            available_minutes = self._time_to_minutes("23:59") - now_minutes

        # 準備待辦清單文字，優先顯示碎片任務
        todos_text = ""

        # 先處理碎片任務（最優先）
        quick_todos = uncompleted_todos.get('quick', [])
        if quick_todos:
            todos_text += "\n⚡ 碎片任務（優先）:\n"
            for todo in quick_todos[:5]:
                todos_text += f"  - {todo['content']} (預估{todo['estimated_minutes']}分鐘)\n"

        # 再處理其他類型待辦
        for todo_type in ['daily', 'weekly', 'monthly']:
            todos = uncompleted_todos.get(todo_type, [])
            if todos:
                type_name = {'daily': '日待辦', 'weekly': '週待辦', 'monthly': '月待辦'}[todo_type]
                todos_text += f"\n{type_name}:\n"
                for todo in todos[:5]:  # 最多5個
                    todos_text += f"  - {todo['content']} (預估{todo['estimated_minutes']}分鐘)\n"

        prompt = f"""你是時間管理助手。根據以下資訊，建議使用者現在該做什麼。

現在時間：{current_time}
可用時間：約 {available_minutes} 分鐘
{"下個行程：" + next_activity['title'] + " (" + next_activity['start_time'] + ")" if next_activity else "今日無後續行程"}

未完成待辦：
{todos_text if todos_text else "（無）"}

**重要規則：**
- 優先推薦「碎片任務」,這些是可以見縫插針完成的零碎事項
- 如果有碎片任務且時間充足,優先選擇碎片任務
- 如果時間緊迫(少於15分鐘),只推薦碎片任務或休息
- 如果可用時間很長(超過30分鐘),可以推薦日待辦

請給出：
1. 具體建議（優先考慮可在時間內完成的待辦）
2. 簡短原因說明（1-2句話）

輸出格式（JSON）：
{{
    "suggestion": "建議活動名稱",
    "reason": "原因說明"
}}

只輸出 JSON，不要其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.choices[0].message.content.strip()

            result_text = self._clean_json_response(result_text)
            result = json.loads(result_text)

            return {
                'suggestion': result.get('suggestion', '休息一下'),
                'reason': result.get('reason', '現在有空閒時間'),
                'available_minutes': available_minutes
            }

        except Exception as e:
            print(f"建議活動錯誤: {e}")
            return {
                'suggestion': '休息一下',
                'reason': '目前有空閒時間',
                'available_minutes': available_minutes
            }

    def suggest_reschedule(self, delayed_items: List[Dict], date_str: str) -> Dict:
        """
        為延誤的排程項目提供重排建議

        Args:
            delayed_items: 延誤的排程項目列表
            date_str: 當前日期 (YYYY-MM-DD)

        Returns:
            {
                'suggestions': [
                    {
                        'item_id': 1,
                        'original_title': '原標題',
                        'options': [
                            {'action': 'today', 'time': '20:00-21:00', 'reason': '...'},
                            {'action': 'tomorrow', 'time': '09:00-10:00', 'reason': '...'},
                            {'action': 'cancel', 'reason': '...'}
                        ]
                    }
                ]
            }
        """
        if not delayed_items:
            return {'suggestions': []}

        items_text = ""
        for item in delayed_items:
            items_text += f"- {item['title']} (原定 {item['start_time']}-{item['end_time']})\n"

        prompt = f"""你是時間管理助手。有些排程項目延誤了，請為每個項目提供重排建議。

延誤項目：
{items_text}

當前日期：{date_str}
當前時間：晚間

請為每個項目提供3種選項：
1. 今晚完成（給出建議時段）
2. 明天完成（給出建議時段）
3. 取消（說明原因，例如：可能不重要、可合併到其他任務等）

輸出格式（JSON）：
{{
    "suggestions": [
        {{
            "title": "項目標題",
            "options": [
                {{"action": "today", "time": "20:00-21:00", "reason": "原因"}},
                {{"action": "tomorrow", "time": "09:00-10:00", "reason": "原因"}},
                {{"action": "cancel", "reason": "原因"}}
            ]
        }}
    ]
}}

只輸出 JSON，不要其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.choices[0].message.content.strip()

            result_text = self._clean_json_response(result_text)
            result = json.loads(result_text)

            # 將建議與原始項目的 ID 對應
            suggestions_with_id = []
            for i, item in enumerate(delayed_items):
                if i < len(result.get('suggestions', [])):
                    suggestion = result['suggestions'][i]
                    suggestions_with_id.append({
                        'item_id': item['id'],
                        'original_title': item['title'],
                        'options': suggestion.get('options', [])
                    })

            return {'suggestions': suggestions_with_id}

        except Exception as e:
            print(f"重排建議錯誤: {e}")
            # 備案：簡單建議
            suggestions = []
            for item in delayed_items:
                suggestions.append({
                    'item_id': item['id'],
                    'original_title': item['title'],
                    'options': [
                        {'action': 'tomorrow', 'time': '09:00-10:00', 'reason': '明天早上處理'},
                        {'action': 'cancel', 'reason': '可考慮取消'}
                    ]
                })
            return {'suggestions': suggestions}

    def _time_to_minutes(self, time_str: str) -> int:
        """將時間字串轉換為分鐘數（從00:00開始）"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
