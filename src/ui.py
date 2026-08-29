from __future__ import annotations

from datetime import date, datetime

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .business import pick_encouragement
from .config import TIME_DISPLAY_FORMAT, WINDOW_SIZE, WINDOW_TITLE
from .storage import PunchRecord, append_record, format_records, has_record_for_day, load_records


class PunchClockWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.records: list[PunchRecord] = load_records()
        self.today = date.today()
        self.last_encouragement: str | None = None
        self.alarm_enabled = False
        self.alarm_hour = 0
        self.alarm_minute = 0
        self.alarm_fire_key: str | None = None

        self._build_ui()
        self._apply_initial_state()
        self._start_clock()

    def _build_ui(self) -> None:
        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(*WINDOW_SIZE)

        central = QWidget(self)
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        title = QLabel('每日打卡助手')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Microsoft YaHei UI', 20, QFont.Bold))
        root.addWidget(title)

        self.time_label = QLabel('--')
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setObjectName('timeLabel')
        self.time_label.setFont(QFont('Consolas', 24, QFont.Bold))
        root.addWidget(self.time_label)

        self.status_label = QLabel('今日状态：未打卡')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont('Microsoft YaHei UI', 10))
        root.addWidget(self.status_label)

        self.checkin_button = QPushButton('打卡')
        self.checkin_button.setObjectName('checkInButton')
        self.checkin_button.setMinimumHeight(52)
        self.checkin_button.setFont(QFont('Microsoft YaHei UI', 12, QFont.Bold))
        self.checkin_button.clicked.connect(self.handle_checkin)
        root.addWidget(self.checkin_button)

        alarm_frame = QFrame()
        alarm_layout = QVBoxLayout(alarm_frame)
        alarm_layout.setContentsMargins(0, 0, 0, 0)
        alarm_layout.setSpacing(8)

        alarm_title = QLabel('闹钟提醒')
        alarm_title.setFont(QFont('Microsoft YaHei UI', 11, QFont.Bold))
        alarm_layout.addWidget(alarm_title)

        alarm_row = QHBoxLayout()
        alarm_row.setSpacing(8)

        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setSuffix(' 时')
        self.hour_spin.setFixedWidth(96)

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setSuffix(' 分')
        self.minute_spin.setFixedWidth(96)

        alarm_row.addWidget(QLabel('设置时间：'))
        alarm_row.addWidget(self.hour_spin)
        alarm_row.addWidget(self.minute_spin)

        self.alarm_button = QPushButton('开启闹钟')
        self.alarm_button.setObjectName('alarmButton')
        self.alarm_button.clicked.connect(self.toggle_alarm)
        alarm_row.addWidget(self.alarm_button)
        alarm_row.addStretch(1)

        alarm_layout.addLayout(alarm_row)

        self.alarm_status_label = QLabel('闹钟状态：未开启')
        self.alarm_status_label.setFont(QFont('Microsoft YaHei UI', 10))
        alarm_layout.addWidget(self.alarm_status_label)

        root.addWidget(alarm_frame)

        history_title = QLabel('打卡记录')
        history_title.setFont(QFont('Microsoft YaHei UI', 11, QFont.Bold))
        root.addWidget(history_title)

        self.history_view = QPlainTextEdit()
        self.history_view.setReadOnly(True)
        self.history_view.setPlaceholderText('暂无打卡记录')
        self.history_view.setFont(QFont('Microsoft YaHei UI', 10))
        root.addWidget(self.history_view, 1)

        self.setStyleSheet(
            """
            QMainWindow {
                background: #f6f8fb;
            }
            QLabel {
                color: #1f2937;
            }
            QPlainTextEdit {
                background: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 6px;
            }
            QSpinBox {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 10px 14px;
            }
            QPushButton#checkInButton {
                background: #2563eb;
                color: white;
            }
            QPushButton#checkInButton:disabled {
                background: #9ca3af;
            }
            QPushButton#alarmButton {
                background: #0f766e;
                color: white;
            }
            QPushButton#alarmButton:disabled {
                background: #94a3b8;
            }
            """
        )

        self._center_window()

    def _center_window(self) -> None:
        screen = self.screen()
        if not screen:
            return
        available = screen.availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(available.center())
        self.move(frame.topLeft())

    def _apply_initial_state(self) -> None:
        now = datetime.now()
        self.time_label.setText(now.strftime(TIME_DISPLAY_FORMAT))
        self.history_view.setPlainText(format_records(self.records))
        self.history_view.moveCursor(QTextCursor.End)
        self._refresh_checkin_state()
        self._refresh_alarm_controls()

    def _start_clock(self) -> None:
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start()

    def _refresh_history_view(self) -> None:
        self.history_view.setPlainText(format_records(self.records))
        self.history_view.moveCursor(QTextCursor.End)

    def _refresh_checkin_state(self) -> None:
        today_checked = has_record_for_day(self.records, self.today)
        if today_checked:
            self.checkin_button.setEnabled(False)
            self.checkin_button.setText('今日已打卡')
            self.status_label.setText('今日状态：已打卡')
        else:
            self.checkin_button.setEnabled(True)
            self.checkin_button.setText('打卡')
            self.status_label.setText('今日状态：未打卡')

    def _refresh_alarm_controls(self) -> None:
        if self.alarm_enabled:
            self.alarm_button.setText('关闭闹钟')
            self.alarm_status_label.setText(f'闹钟状态：已开启 {self.alarm_hour:02d}:{self.alarm_minute:02d}')
        else:
            self.alarm_button.setText('开启闹钟')
            self.alarm_status_label.setText('闹钟状态：未开启')

    def on_tick(self) -> None:
        now = datetime.now()
        self.time_label.setText(now.strftime(TIME_DISPLAY_FORMAT))

        if now.date() != self.today:
            self.today = now.date()
            self._refresh_checkin_state()

        if self.alarm_enabled and now.hour == self.alarm_hour and now.minute == self.alarm_minute:
            alarm_key = now.strftime('%Y%m%d%H%M')
            if alarm_key != self.alarm_fire_key:
                self.alarm_fire_key = alarm_key
                QMessageBox.information(self, '打卡提醒', f'现在是 {now:%H:%M}，记得打卡。')

    def handle_checkin(self) -> None:
        now = datetime.now()
        if has_record_for_day(self.records, now.date()):
            QMessageBox.information(self, '提示', '今天已经打过卡了。')
            self._refresh_checkin_state()
            return

        encouragement = pick_encouragement(self.last_encouragement)
        record = PunchRecord(timestamp=now, kind='打卡', note=encouragement)
        append_record(record)
        self.records.append(record)
        self.last_encouragement = encouragement

        self._refresh_history_view()
        self._refresh_checkin_state()
        QMessageBox.information(self, '打卡成功', encouragement)

    def toggle_alarm(self) -> None:
        if self.alarm_enabled:
            self.alarm_enabled = False
            self.alarm_fire_key = None
            self._refresh_alarm_controls()
            return

        self.alarm_hour = self.hour_spin.value()
        self.alarm_minute = self.minute_spin.value()
        self.alarm_enabled = True
        self.alarm_fire_key = None
        self._refresh_alarm_controls()
        QMessageBox.information(
            self,
            '闹钟已开启',
            f'已设置 {self.alarm_hour:02d}:{self.alarm_minute:02d} 的打卡提醒。',
        )
