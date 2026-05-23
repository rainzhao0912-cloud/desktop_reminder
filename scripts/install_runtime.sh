#!/bin/zsh

PROJECT_DIR="/Users/bytedance/Documents/桌面提醒工具"
RUNTIME_DIR="/Users/bytedance/Library/Application Support/DesktopReminder"

mkdir -p "$RUNTIME_DIR/scripts" "$RUNTIME_DIR/logs"

cp "$PROJECT_DIR/reminder.py" "$RUNTIME_DIR/reminder.py"
cp "$PROJECT_DIR/schedule.json" "$RUNTIME_DIR/schedule.json"
cp "$PROJECT_DIR/scripts/daily_planner.swift" "$RUNTIME_DIR/scripts/daily_planner.swift"
cp "$PROJECT_DIR/scripts/macos_overlay.swift" "$RUNTIME_DIR/scripts/macos_overlay.swift"
cp "$PROJECT_DIR/scripts/start_reminder_terminal.sh" "$RUNTIME_DIR/scripts/start_reminder_terminal.sh"
cp "$PROJECT_DIR/scripts/open_daily_plan_terminal.sh" "$RUNTIME_DIR/scripts/open_daily_plan_terminal.sh"

chmod +x "$RUNTIME_DIR/scripts/start_reminder_terminal.sh"
chmod +x "$RUNTIME_DIR/scripts/open_daily_plan_terminal.sh"

echo "Installed runtime to $RUNTIME_DIR"

