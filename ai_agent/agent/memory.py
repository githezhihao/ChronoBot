import json
import os

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '../data/history.json')

class Memory:
    def __init__(self):
        self.history = []
        self.load()

    def load(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save(self):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_message(self, role, content):
        self.history.append({'role': role, 'content': content})
        self.save()

    def get_history(self, limit=20):
        return self.history[-limit:]
