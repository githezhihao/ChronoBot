import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout
from agent.memory import Memory
from agent.tools import call_llm_api

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AI Agent 聊天窗口')
        self.resize(500, 500)
        self.memory = Memory()
        self.init_ui()
        self.refresh_history()

    def init_ui(self):
        layout = QVBoxLayout()
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        layout.addWidget(QLabel('AI Agent 聊天窗口'))
        layout.addWidget(self.history)
        
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.returnPressed.connect(self.send_message)
        self.send_btn = QPushButton('发送')
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        self.setLayout(layout)

    def refresh_history(self):
        history = self.memory.get_history()
        text = ''
        for msg in history:
            role = '我' if msg['role'] == 'user' else 'AI'
            text += f"{role}: {msg['content']}\n"
        self.history.setPlainText(text)
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

    def send_message(self):
        user_input = self.input.text().strip()
        if user_input:
            self.memory.add_message('user', user_input)
            self.input.clear()
            self.refresh_history()
            history = self.memory.get_history()
            ai_reply = call_llm_api(user_input, history=history[:-1])
            self.memory.add_message('assistant', ai_reply)
            self.refresh_history()

def main():
    app = QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
