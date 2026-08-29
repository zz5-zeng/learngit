# Codex 打卡助手

一个基于 Python + PyQt5 的 Windows 打卡小工具。

## 功能

- 实时显示系统时间
- 点击打卡完成当日记录
- 打卡成功随机弹出鼓励文案
- 打卡记录本地 TXT 永久保存
- 支持自定义闹钟提醒
- 可用 PyInstaller 打包为独立 EXE

## 运行

```bash
python -m pip install -r requirements.txt
python app.py
```

## 打包

双击 `build.bat`，或执行：

```bash
python -m PyInstaller --noconfirm --clean --onefile --windowed --name PunchClock app.py
```

打包完成后会尝试把 `PunchClock.exe` 复制到桌面。

## 数据位置

打卡记录默认保存到：

`%LOCALAPPDATA%\codex_punch_clock\records.txt`

如果 `LOCALAPPDATA` 不可用，会退回到用户目录下的隐藏文件夹。
