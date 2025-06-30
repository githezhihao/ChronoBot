import requests
import os
from openai import OpenAI

API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 或直接写成 'sk-xxxx'
url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "你好"}]
}

client = OpenAI(
    api_key="sk-yovFkUJzugSJBcwX7o6ulAm7FEOJiM8PjM3QRqjEO6stqzZB",  # 替换为你的 chatanywhere API Key
    base_url="https://api.chatanywhere.tech/v1"
)

# 示例：调用 chat/completions
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)

try:
    resp = requests.post(url, headers=headers, json=data, timeout=10)
    print("Status code:", resp.status_code)
    print("Response:", resp.text)
    if resp.status_code == 200:
        print("API Key 可用")
    elif resp.status_code == 401:
        print("API Key 无效或未填写")
    elif resp.status_code == 402:
        print("API Key 已欠费或额度不足")
    else:
        print("API 发生其他错误")
except Exception as e:
    print("请求异常:", e)