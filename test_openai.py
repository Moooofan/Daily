"""測試 OpenAI API 連線"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

print("=" * 60)
print("OpenAI API 測試")
print("=" * 60)
print(f"API Key 前 20 字元: {api_key[:20] if api_key else 'None'}...")
print(f"API Key 長度: {len(api_key) if api_key else 0}")
print("=" * 60)

try:
    client = OpenAI(api_key=api_key)
    print("✓ OpenAI 客戶端初始化成功")

    print("\n測試 API 呼叫...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say hello"}]
    )

    print("✓ API 呼叫成功!")
    print(f"回應: {response.choices[0].message.content}")
    print("\n✅ OpenAI API 運作正常!")

except Exception as e:
    print(f"\n❌ 錯誤: {type(e).__name__}")
    print(f"錯誤訊息: {str(e)}")

    if "api_key" in str(e).lower() or "authentication" in str(e).lower():
        print("\n💡 建議: API Key 可能無效或過期")
        print("   請到 https://platform.openai.com/api-keys 檢查")
    elif "quota" in str(e).lower():
        print("\n💡 建議: API 配額可能已用完")
        print("   請到 https://platform.openai.com/account/usage 檢查")
    elif "rate_limit" in str(e).lower():
        print("\n💡 建議: 超過速率限制,請稍後再試")
    else:
        print("\n💡 建議: 檢查網路連線或 API 狀態")

print("=" * 60)
