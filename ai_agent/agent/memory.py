import json
import os
import glob
import uuid
from datetime import datetime

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), '../data/sessions')
DEFAULT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), '../data/history.json')

class Memory:
    def __init__(self, session_id=None):
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        self.session_id = session_id or self._get_latest_session_id() or self._new_session_id()
        self.history = []
        self.load()

    def _session_file(self, session_id=None):
        sid = session_id or self.session_id
        return os.path.join(SESSIONS_DIR, f'{sid}.json')

    def _new_session_id(self):
        return datetime.now().strftime('%Y%m%d_%H%M%S_') + str(uuid.uuid4())[:8]

    def _get_latest_session_id(self):
        files = sorted(glob.glob(os.path.join(SESSIONS_DIR, '*.json')))
        if files:
            return os.path.splitext(os.path.basename(files[-1]))[0]
        return None

    def list_sessions(self):
        files = sorted(glob.glob(os.path.join(SESSIONS_DIR, '*.json')))
        return [os.path.splitext(os.path.basename(f))[0] for f in files]

    def switch_session(self, session_id):
        self.session_id = session_id
        self.load()

    def load(self):
        path = self._session_file()
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save(self):
        with open(self._session_file(), 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_message(self, role, content):
        self.history.append({'role': role, 'content': content})
        self.save()

    def get_history(self, limit=20):
        return self.history[-limit:]

    def clear_history(self):
        self.history = []
        self.save()

    def get_session_history(self, session_id):
        path = self._session_file(session_id)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def replace_last_ai_message(self, content):
        # 替换最后一条AI消息（role==assistant 或 role==ai）
        for i in range(len(self.history)-1, -1, -1):
            if self.history[i]['role'] in ('assistant', 'ai'):
                self.history[i]['content'] = content
                self.save()
                break

    def delete_session(self, session_id):
        path = self._session_file(session_id)
        if os.path.exists(path):
            os.remove(path)
