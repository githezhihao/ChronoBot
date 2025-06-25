import PySimpleGUI as sg

def create_window():
    layout = [
        [sg.Text('AI Agent 聊天窗口', font=('Arial', 16))],
        [sg.Multiline(key='-HISTORY-', size=(60, 20), disabled=True, autoscroll=True)],
        [sg.Input(key='-INPUT-', size=(50, 1)), sg.Button('发送', bind_return_key=True)],
    ]
    return sg.Window('AI Agent', layout, finalize=True)
