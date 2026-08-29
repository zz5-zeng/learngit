from __future__ import annotations

import os
from pathlib import Path

APP_NAME = '打卡助手'
WINDOW_TITLE = '打卡助手'
WINDOW_SIZE = (760, 720)

DATA_DIR_NAME = 'codex_punch_clock'
RECORDS_FILE_NAME = 'records.txt'

TIME_DISPLAY_FORMAT = '%Y/%m/%d %H:%M:%S'
RECORD_DISPLAY_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_data_dir() -> Path:
    local_app_data = os.environ.get('LOCALAPPDATA')
    if local_app_data:
        return Path(local_app_data) / DATA_DIR_NAME
    return Path.home() / f'.{DATA_DIR_NAME}'


def get_records_path() -> Path:
    return get_data_dir() / RECORDS_FILE_NAME
