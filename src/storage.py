from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .config import RECORD_DISPLAY_FORMAT, get_data_dir, get_records_path


@dataclass(slots=True)
class PunchRecord:
    timestamp: datetime
    kind: str
    note: str

    def to_line(self) -> str:
        return f'{self.timestamp.strftime(RECORD_DISPLAY_FORMAT)}\t{self.kind}\t{self.note}'

    def display_text(self) -> str:
        return f'{self.timestamp.strftime(RECORD_DISPLAY_FORMAT)} | {self.kind} | {self.note}'


def ensure_storage_ready() -> Path:
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    records_path = get_records_path()
    if not records_path.exists():
        records_path.write_text('', encoding='utf-8')
    return records_path


def _rewrite_records(path: Path, records: list[PunchRecord]) -> None:
    content = '\n'.join(record.to_line() for record in records)
    if content:
        content += '\n'
    path.write_text(content, encoding='utf-8')


def _backup_broken_file(path: Path) -> None:
    if not path.exists():
        return

    stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup = path.with_name(f'{path.stem}.broken-{stamp}{path.suffix}')
    try:
        path.replace(backup)
    except OSError:
        try:
            backup.write_text(path.read_text(encoding='utf-8', errors='ignore'), encoding='utf-8')
        except OSError:
            pass


def parse_record_line(line: str) -> PunchRecord:
    parts = line.split('\t', 2)
    if len(parts) != 3:
        raise ValueError('记录格式错误')

    timestamp = datetime.strptime(parts[0].strip(), RECORD_DISPLAY_FORMAT)
    kind = parts[1].strip() or '打卡'
    note = parts[2].strip()
    return PunchRecord(timestamp=timestamp, kind=kind, note=note)


def load_records() -> list[PunchRecord]:
    path = ensure_storage_ready()

    try:
        raw_text = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('', encoding='utf-8')
        return []

    records: list[PunchRecord] = []
    invalid_found = False

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            records.append(parse_record_line(line))
        except ValueError:
            invalid_found = True

    if invalid_found:
        _backup_broken_file(path)
        _rewrite_records(path, records)

    return records


def append_record(record: PunchRecord) -> None:
    path = ensure_storage_ready()
    with path.open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(record.to_line() + '\n')


def format_records(records: list[PunchRecord]) -> str:
    if not records:
        return '暂无打卡记录。'
    return '\n'.join(record.display_text() for record in records)


def has_record_for_day(records: list[PunchRecord], target_day: date) -> bool:
    return any(record.timestamp.date() == target_day for record in records)
