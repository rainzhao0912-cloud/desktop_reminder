#!/bin/zsh

PROJECT_DIR="/Users/bytedance/Library/Application Support/DesktopReminder"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

if pgrep -f "$PROJECT_DIR/reminder.py --schedule" >/dev/null 2>&1; then
  osascript -e 'display notification "提醒程序已经在运行" with title "桌面提醒工具"'
  exit 0
fi

nohup /usr/bin/python3 "$PROJECT_DIR/reminder.py" --schedule "$PROJECT_DIR/schedule.json" >> "$LOG_DIR/reminder.out.log" 2>> "$LOG_DIR/reminder.err.log" &
osascript -e 'display notification "今天的提醒程序已启动" with title "桌面提醒工具"'
