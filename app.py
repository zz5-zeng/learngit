from __future__ import annotations

import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from src.config import APP_NAME
from src.ui import PunchClockWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont('Microsoft YaHei UI', 10))

    window = PunchClockWindow()
    window.show()
    return app.exec_()


if __name__ == '__main__':
    raise SystemExit(main())
