import os
from agent.memory import Memory
import requests
from ui.app import create_window
import PySimpleGUI as sg

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'YOUR_API_KEY_HERE')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'  # 请根据官方文档确认

memory = Memory()


def call_deepseek_api(messages):
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'deepseek-chat',  # 请根据实际模型名调整
        'messages': messages,
        'temperature': 0.7,
    }
    resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if resp.status_code == 200:
        return resp.json()['choices'][0]['message']['content']
    else:
        return f"[API错误] {resp.status_code}: {resp.text}"


def main():
    window = create_window()
    history = memory.get_history()
    window['-HISTORY-'].update('\n'.join([f"{m['role']}: {m['content']}" for m in history]))

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == '发送':
            user_input = values['-INPUT-'].strip()
            if not user_input:
                continue
            memory.add_message('user', user_input)
            window['-HISTORY-'].update(f"你: {user_input}\n", append=True)
            messages = memory.get_history()
            response = call_deepseek_api(messages)
            memory.add_message('assistant', response)
            window['-HISTORY-'].update(f"AI: {response}\n", append=True)
            window['-INPUT-'].update('')
    window.close()

if __name__ == '__main__':
    main()
