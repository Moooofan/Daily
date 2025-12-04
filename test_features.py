"""測試新功能"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_delay_check():
    """測試延誤檢查"""
    print("\n=== 測試延誤檢查 ===")
    response = requests.get(f"{BASE_URL}/api/delay/check")
    data = response.json()
    print(f"✓ 延誤檢查成功")
    print(f"  延誤項目數: {data['delayed_count']}")
    print(f"  當前時間: {data['current_time']}")
    return data['success']

def test_suggest_now():
    """測試 AI 建議"""
    print("\n=== 測試 AI 建議 ===")
    response = requests.get(f"{BASE_URL}/api/ai/suggest-now")
    data = response.json()
    print(f"✓ AI 建議成功")
    print(f"  建議: {data['suggestion']}")
    print(f"  原因: {data['reason']}")
    print(f"  可用時間: {data['available_minutes']} 分鐘")
    return data['success']

def test_daily_init():
    """測試每日初始化"""
    print("\n=== 測試每日初始化 ===")
    response = requests.post(
        f"{BASE_URL}/api/daily/init",
        json={"date": "2025-11-13"}
    )
    data = response.json()
    print(f"✓ 每日初始化成功")
    print(f"  訊息: {data['message']}")
    print(f"  排程數量: {data['count']}")
    return data['success']

def test_daily_review():
    """測試晚間復盤"""
    print("\n=== 測試晚間復盤 ===")
    response = requests.get(f"{BASE_URL}/api/daily/review")
    data = response.json()
    print(f"✓ 晚間復盤成功")
    print(f"  完成率: {data['completion_rate']:.1f}%")
    print(f"  完成項目: {data['completed']}/{data['total']}")
    print(f"  復盤訊息: {data['review_message'][:100]}...")
    return data['success']

def test_reschedule():
    """測試智能重排建議"""
    print("\n=== 測試智能重排建議 ===")
    response = requests.post(
        f"{BASE_URL}/api/delay/suggest-reschedule",
        json={"date": "2025-11-13"}
    )
    data = response.json()
    print(f"✓ 智能重排建議成功")
    print(f"  建議數量: {len(data.get('suggestions', []))}")
    if data.get('message'):
        print(f"  訊息: {data['message']}")
    return data['success']

def main():
    print("=" * 60)
    print("Daily 系統功能測試")
    print("=" * 60)

    results = []

    try:
        results.append(("延誤檢查", test_delay_check()))
        results.append(("AI 建議", test_suggest_now()))
        results.append(("每日初始化", test_daily_init()))
        results.append(("晚間復盤", test_daily_review()))
        results.append(("智能重排", test_reschedule()))

        print("\n" + "=" * 60)
        print("測試結果摘要")
        print("=" * 60)

        for name, success in results:
            status = "✅ 通過" if success else "❌ 失敗"
            print(f"{name}: {status}")

        all_passed = all(success for _, success in results)
        if all_passed:
            print("\n🎉 所有測試通過!")
        else:
            print("\n⚠️  部分測試失敗")

    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
