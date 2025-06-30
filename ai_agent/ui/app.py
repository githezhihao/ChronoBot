import sys
from PyQt5.QtWidgets import QApplication
from .chat_window import ChatWindow

def main():
    app = QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
