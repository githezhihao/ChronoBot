from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QAbstractItemView, QFrame, QMenu, QAction, QToolButton, QDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from qt_material import apply_stylesheet
from ai_agent.agent.memory import Memory
from ai_agent.agent.tools import call_llm_api
import threading
import pygments
from pygments import lexers, formatters
from .render_utils import render_markdown
from .bubble_utils import user_bubble_html, ai_bubble_html

class ChatWindow(QWidget):
    ai_reply_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('AI Agent 聊天窗口')
        self.resize(900, 650)
        self.memory = Memory()
        self.init_ui()
        self.refresh_sessions()
        self.refresh_history()
        self.ai_reply_ready.connect(self.animate_ai_reply)

    def showEvent(self, event):
        apply_stylesheet(self, theme='light_blue.xml')
        super().showEvent(event)

    def init_ui(self):
        main_layout = QHBoxLayout()
        # 左侧会话面板
        session_panel = QFrame()
        session_panel.setObjectName('SessionPanel')
        session_panel.setFixedWidth(280)
        session_layout = QVBoxLayout()
        # 新建会话按钮放在最上面
        self.new_btn = QPushButton('新建会话')
        self.new_btn.setFont(QFont('Microsoft YaHei', 15))
        self.new_btn.clicked.connect(self.new_session)
        session_layout.addWidget(self.new_btn)
        session_label = QLabel('会话列表')
        session_label.setFont(QFont('Microsoft YaHei', 18, QFont.Bold))
        session_layout.addWidget(session_label)
        self.session_list = QListWidget()
        self.session_list.setSpacing(2)
        self.session_list.setFixedWidth(260)
        self.session_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.session_list.itemClicked.connect(self.on_session_selected)
        session_layout.addWidget(self.session_list)
        session_layout.addStretch(1)
        session_panel.setLayout(session_layout)
        main_layout.addWidget(session_panel)
        # 右侧聊天区
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel('AI Agent 聊天窗口'))
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setFont(QFont('Consolas', 18))
        self.history.setMinimumHeight(350)
        self.history.setStyleSheet('background: #F7F8FA; border: none; color: #222;')
        right_layout.addWidget(self.history)
        # 飞书风格输入区
        input_frame = QFrame()
        input_frame.setStyleSheet('background: #F2F3F5; border-radius: 12px; border: 1px solid #E5E6EB;')
        input_frame.setFixedHeight(80)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 8, 16, 8)
        input_layout.setSpacing(8)
        # 支持拖拽上传
        class DragTextEdit(QTextEdit):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setAcceptDrops(True)
            def keyPressEvent(self, event):
                if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
                    # 只要不是组合键，直接发送
                    self.clearFocus()
                    self.parent().parent().send_message()
                    event.accept()
                    return
                super().keyPressEvent(event)
            def dragEnterEvent(self, event):
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                else:
                    super().dragEnterEvent(event)
            def dropEvent(self, event):
                if event.mimeData().hasUrls():
                    for url in event.mimeData().urls():
                        path = url.toLocalFile()
                        if path:
                            self.parent().parent().upload_file_by_path(path)
                    event.acceptProposedAction()
                else:
                    super().dropEvent(event)
        self.input = DragTextEdit(input_frame)
        self.input.setFont(QFont('Microsoft YaHei', 15))
        self.input.setStyleSheet('background: #fff; border-radius: 8px; border: 1px solid #E5E6EB; color: #222; padding: 8px;')
        self.input.setMinimumHeight(40)
        self.input.setMaximumHeight(60)
        # 右下角按钮区（绝对定位在输入框内）
        btns_frame = QFrame(input_frame)
        btns_frame.setStyleSheet('background: transparent;')
        btns_frame.setFixedHeight(60)
        btns_frame.setFixedWidth(140)
        btns_layout = QHBoxLayout(btns_frame)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(8)
        # 加号按钮（仅加号，无下标图案）
        self.upload_btn = QToolButton(btns_frame)
        self.upload_btn.setText('＋')
        self.upload_btn.setFixedSize(36, 36)
        self.upload_btn.setStyleSheet('QToolButton {background: #E5E6EB; border-radius: 18px; font-size: 22px; color: #86909C;} QToolButton:hover {background: #D1E9FF; color: #1D2129;}')
        self.upload_btn.clicked.connect(self.show_upload_dialog)
        # 发送按钮
        self.send_btn = QPushButton('发送', btns_frame)
        self.send_btn.setFont(QFont('Microsoft YaHei', 15, QFont.Bold))
        self.send_btn.setFixedSize(80, 36)
        self.send_btn.setStyleSheet('QPushButton {background: #246EFF; color: #fff; border-radius: 18px; font-size: 15px;} QPushButton:hover {background: #1D5EFF;}')
        self.send_btn.clicked.connect(self.send_message)
        btns_layout.addWidget(self.upload_btn)
        btns_layout.addWidget(self.send_btn)
        # 输入区布局：输入框+右下角按钮
        input_layout.addWidget(self.input)
        input_layout.addWidget(btns_frame, alignment=Qt.AlignBottom)
        right_layout.addWidget(input_frame)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def refresh_sessions(self):
        self.session_list.clear()
        sessions = self.memory.list_sessions()
        for sid in sessions:
            # 获取会话首条用户消息做预览
            preview = ''
            history = self.memory.get_session_history(sid)
            for msg in history:
                if msg['role'] == 'user' and msg['content'].strip():
                    preview = msg['content'].strip().replace('\n', ' ')
                    if len(preview) > 18:
                        preview = preview[:18] + '...'
                    break
            display_name = f'{sid[-6:]}  {preview}' if preview else sid[-6:]
            item = QListWidgetItem(display_name)
            item.setToolTip(f'会话ID: {sid}')
            if sid == self.memory.session_id:
                item.setSelected(True)
            self.session_list.addItem(item)
        # 增加右键菜单删除会话
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.show_session_context_menu)
        for i in range(self.session_list.count()):
            if self.session_list.item(i).toolTip().endswith(self.memory.session_id):
                self.session_list.setCurrentRow(i)
                break

    def show_session_context_menu(self, pos):
        item = self.session_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        delete_action = QAction('删除会话', self)
        menu.addAction(delete_action)
        def do_delete():
            sid = item.toolTip().replace('会话ID: ', '')
            self.memory.delete_session(sid)
            # 如果删除的是当前会话，自动切换到最新会话
            if sid == self.memory.session_id:
                sessions = self.memory.list_sessions()
                if sessions:
                    self.memory.switch_session(sessions[-1])
            self.refresh_sessions()
            self.refresh_history()
            menu.close()  # 删除后关闭弹窗
        delete_action.triggered.connect(do_delete)
        menu.exec_(self.session_list.mapToGlobal(pos))

    def refresh_history(self):
        import datetime
        import re
        history = self.memory.get_history(limit=100)
        html = ''
        def escape(text):
            return text.replace('<', '&lt;').replace('>', '&gt;')
        def format_time(ts):
            if isinstance(ts, (int, float)):
                return datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
            return ts if ts else ''
        for msg in history:
            content = render_markdown(msg['content'], escape)
            time_str = format_time(msg.get('time'))
            if msg['role'] == 'user':
                html += user_bubble_html(content, time_str)
            else:
                html += ai_bubble_html(content, time_str)
        self.history.setHtml(f'<div style="background:#F7F8FA;">{html}</div>')
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

    def mousePressEvent(self, event):
        # 仅保留必要功能，移除无用头像相关代码
        super().mousePressEvent(event)

    def send_message(self):
        user_input = self.input.toPlainText().strip()
        if user_input:
            self.memory.add_message('user', user_input)
            self.input.clear()
            self.refresh_history()  # 立即刷新，用户气泡立刻出现
            # 先插入AI“正在输入”气泡
            self.memory.add_message('assistant', '__ai_typing__')
            self.refresh_history()
            def ai_reply_thread():
                history = self.memory.get_history(limit=100)
                ai_reply = call_llm_api(user_input, history=history[:-1])
                self.memory.replace_last_ai_message("")  # 先清空
                self.ai_reply_ready.emit(ai_reply)
            threading.Thread(target=ai_reply_thread, daemon=True).start()

    def animate_ai_reply(self, text):
        self.memory.replace_last_ai_message("")
        self.refresh_history()
        self._ai_anim_idx = 0
        self._ai_anim_text = text
        def update():
            if self._ai_anim_idx <= len(self._ai_anim_text):
                self.memory.replace_last_ai_message(self._ai_anim_text[:self._ai_anim_idx])
                self.refresh_history()
                self._ai_anim_idx += 1
                QTimer.singleShot(18, update)
        update()

    def new_session(self):
        # 新建会话时弹窗询问是否引用历史（允许引用当前会话）
        sessions = self.memory.list_sessions()
        ref_history = []
        if sessions:
            dlg = QDialog(self)
            dlg.setWindowTitle('新建会话设置')
            dlg.resize(400, 300)
            vlayout = QVBoxLayout()
            vlayout.addWidget(QLabel('是否引用历史会话？'))
            list_widget = QListWidget()
            list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            for sid in sessions:
                list_widget.addItem(sid)
            vlayout.addWidget(list_widget)
            btn_layout = QHBoxLayout()
            ok_btn = QPushButton('引用')
            no_ref_btn = QPushButton('不引用')
            cancel_btn = QPushButton('取消')
            btn_layout.addWidget(ok_btn)
            btn_layout.addWidget(no_ref_btn)
            btn_layout.addWidget(cancel_btn)
            vlayout.addLayout(btn_layout)
            dlg.setLayout(vlayout)
            ok_btn.clicked.connect(dlg.accept)
            no_ref_btn.clicked.connect(lambda: dlg.done(2))
            cancel_btn.clicked.connect(dlg.reject)
            result = dlg.exec_()
            if result == QDialog.Accepted:
                selected = [item.text() for item in list_widget.selectedItems()]
                for sid in selected:
                    ref_history += self.memory.get_session_history(sid)
            elif result == QDialog.Rejected:
                return  # 取消则不新建
        new_id = self.memory._new_session_id()
        self.memory.session_id = new_id
        self.memory.history = ref_history
        self.memory.save()
        self.refresh_sessions()
        self.refresh_history()

    def on_session_selected(self, item):
        # 会话切换逻辑
        sid = item.toolTip().replace('会话ID: ', '')
        self.memory.switch_session(sid)
        self.refresh_history()

    def show_upload_dialog(self):
        # 文件上传弹窗逻辑（如需保留）
        pass

    def upload_file_by_path(self, path):
        # 文件上传处理逻辑（如需保留）
        pass

    def reference_sessions(self):
        sessions = self.memory.list_sessions()
        sessions = [s for s in sessions if s != self.memory.session_id]
        if not sessions:
            QMessageBox.information(self, "引用历史会话", "没有可引用的历史会话。")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("选择要引用的会话（可多选）")
        dlg.resize(400, 350)
        vlayout = QVBoxLayout()
        vlayout.addWidget(QLabel("请选择要引用的历史会话："))
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        for sid in sessions:
            list_widget.addItem(sid)
        vlayout.addWidget(list_widget)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        vlayout.addLayout(btn_layout)
        dlg.setLayout(vlayout)
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)
        if dlg.exec_() == QDialog.Accepted:
            selected = [item.text() for item in list_widget.selectedItems()]
            if selected:
                all_ref_history = []
                for sid in selected:
                    all_ref_history += self.memory.get_session_history(sid)
                self.memory.history = all_ref_history + self.memory.history
                self.memory.save()
                self.refresh_history()
                QMessageBox.information(self, "引用历史会话", f"已引用会话: {', '.join(selected)} 的全部历史。")

    def upload_file(self, filetype=None, path=None):
        if filetype == 'txt':
            if not path:
                fname, _ = QFileDialog.getOpenFileName(self, '选择要上传的文本文件', '', 'Text Files (*.txt);;All Files (*)')
            else:
                fname = path
            if fname:
                try:
                    with open(fname, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.memory.add_message('user', f'【文本文件内容】\n{content[:2000]}')
                    self.refresh_history()
                    QMessageBox.information(self, '上传文件', '文本文件已上传并解析（前2000字节已加入历史）')
                except Exception as e:
                    QMessageBox.warning(self, '上传文件', f'文件解析失败: {e}')
        elif filetype == 'pdf':
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                QMessageBox.warning(self, '上传文件', '未安装 PyPDF2，无法解析 PDF 文件。请先 pip install PyPDF2')
                return
            if not path:
                fname, _ = QFileDialog.getOpenFileName(self, '选择要上传的PDF文件', '', 'PDF Files (*.pdf);;All Files (*)')
            else:
                fname = path
            if fname:
                try:
                    reader = PdfReader(fname)
                    content = ''
                    for page in reader.pages:
                        content += page.extract_text() or ''
                    self.memory.add_message('user', f'【PDF文件内容】\n{content[:2000]}')
                    self.refresh_history()
                    QMessageBox.information(self, '上传文件', 'PDF文件已上传并解析（前2000字节已加入历史）')
                except Exception as e:
                    QMessageBox.warning(self, '上传文件', f'PDF文件解析失败: {e}')
        elif filetype == 'word':
            try:
                import docx
            except ImportError:
                QMessageBox.warning(self, '上传文件', '未安装 python-docx，无法解析 Word 文件。请先 pip install python-docx')
                return
            if not path:
                fname, _ = QFileDialog.getOpenFileName(self, '选择要上传的Word文件', '', 'Word Files (*.docx);;All Files (*)')
            else:
                fname = path
            if fname:
                try:
                    doc = docx.Document(fname)
                    content = '\n'.join([p.text for p in doc.paragraphs])
                    self.memory.add_message('user', f'【Word文件内容】\n{content[:2000]}')
                    self.refresh_history()
                    QMessageBox.information(self, '上传文件', 'Word文件已上传并解析（前2000字节已加入历史）')
                except Exception as e:
                    QMessageBox.warning(self, '上传文件', f'Word文件解析失败: {e}')
        else:
            QMessageBox.information(self, '上传文件', '请选择文件类型')
