#!/usr/bin/env python3
"""測試 AI 自動分類碎片任務功能"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_ai_classification():
    """測試 AI 分類功能"""

    test_cases = [
        {
            "name": "混合任務(碎片+日待辦+排程)",
            "input": "早上九點開會，記得買牛奶，印考卷，下午要完成報告",
            "expected": {
                "quick": ["買牛奶", "印考卷"],
                "daily": ["完成報告"],
                "schedules": 1
            }
        },
        {
            "name": "四種類型任務",
            "input": "寄包裹、打電話給銀行、本週整理書櫃、本月學習Python、撰寫年度報告",
            "expected": {
                "quick": ["寄包裹", "打電話給銀行"],
                "weekly": ["整理書櫃"],
                "monthly": ["學習Python"],
                "daily": ["撰寫年度報告"]
            }
        },
        {
            "name": "純碎片任務",
            "input": "繳電費、買牛奶、寄信、丟垃圾",
            "expected": {
                "quick": 4
            }
        },
        {
            "name": "複雜任務",
            "input": "準備下週的簡報、洗杯子、本月看完三本書、打電話預約醫生",
            "expected": {
                "quick": ["洗杯子", "打電話預約醫生"],
                "weekly": ["準備下週的簡報"],
                "monthly": ["本月看完三本書"]
            }
        }
    ]

    print("=" * 60)
    print("測試 AI 自動分類碎片任務功能")
    print("=" * 60)

    for i, test in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {test['name']}")
        print(f"輸入: {test['input']}")
        print("-" * 60)

        try:
            response = requests.post(
                f"{BASE_URL}/api/ai/process-voice",
                json={"text": test["input"]},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    print("✅ 請求成功")

                    # 顯示分類結果
                    todos = result['result']['todos']
                    schedules = result['result']['schedules']

                    # 按類型分組
                    by_type = {}
                    for todo in todos:
                        todo_type = todo['type']
                        if todo_type not in by_type:
                            by_type[todo_type] = []
                        by_type[todo_type].append(todo)

                    # 顯示碎片任務
                    if 'quick' in by_type:
                        print(f"\n⚡ 碎片任務 ({len(by_type['quick'])} 個):")
                        for todo in by_type['quick']:
                            print(f"  - {todo['content']} ({todo['estimated_minutes']}分鐘)")

                    # 顯示日待辦
                    if 'daily' in by_type:
                        print(f"\n📝 日待辦 ({len(by_type['daily'])} 個):")
                        for todo in by_type['daily']:
                            print(f"  - {todo['content']} ({todo['estimated_minutes']}分鐘)")

                    # 顯示週待辦
                    if 'weekly' in by_type:
                        print(f"\n📅 週待辦 ({len(by_type['weekly'])} 個):")
                        for todo in by_type['weekly']:
                            print(f"  - {todo['content']} ({todo['estimated_minutes']}分鐘)")

                    # 顯示月待辦
                    if 'monthly' in by_type:
                        print(f"\n🗓️  月待辦 ({len(by_type['monthly'])} 個):")
                        for todo in by_type['monthly']:
                            print(f"  - {todo['content']} ({todo['estimated_minutes']}分鐘)")

                    # 顯示排程
                    if schedules:
                        print(f"\n🕐 排程 ({len(schedules)} 個):")
                        for schedule in schedules:
                            print(f"  - {schedule['start_time']}-{schedule['end_time']} {schedule['title']}")

                    print(f"\n新增統計: {result['todos_added']} 個待辦, {result['schedules_added']} 個排程")

                else:
                    print(f"❌ 請求失敗: {result.get('error')}")

            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")

        except Exception as e:
            print(f"❌ 例外錯誤: {e}")

    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

if __name__ == "__main__":
    test_ai_classification()
