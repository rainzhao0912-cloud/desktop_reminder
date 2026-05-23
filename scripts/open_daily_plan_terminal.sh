#!/bin/zsh

PROJECT_DIR="/Users/bytedance/Library/Application Support/DesktopReminder"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

/usr/bin/python3 "$PROJECT_DIR/reminder.py" --plan >> "$LOG_DIR/planner.out.log" 2>> "$LOG_DIR/planner.err.log"
