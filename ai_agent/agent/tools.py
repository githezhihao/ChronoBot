import requests
import os
from openai import OpenAI

def call_llm_api(prompt, history=None, model="gpt-3.5-turbo"):
    """
    调用 chatanywhere (OpenAI 兼容) API，支持多轮对话。
    prompt: 当前用户输入
    history: [{role: 'user'/'assistant', content: str}, ...]
    model: 模型名，默认 gpt-3.5-turbo
    """
    client = OpenAI(
        api_key="sk-yovFkUJzugSJBcwX7o6ulAm7FEOJiM8PjM3QRqjEO6stqzZB",
        base_url="https://api.chatanywhere.tech/v1"
    )
    messages = history if history else []
    messages = messages + [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f'API调用失败: {e}'
