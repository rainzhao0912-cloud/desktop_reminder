#!/usr/bin/env python3
"""Local full-screen reminder app for macOS."""

from __future__ import annotations

import argparse
import json
import platform
import queue
import re
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional


DEFAULT_SOUND = "/System/Library/Sounds/Glass.aiff"
CHECK_INTERVAL_SECONDS = 10
ROOT_DIR = Path(__file__).resolve().parent
NATIVE_OVERLAY = ROOT_DIR / "scripts" / "macos_overlay.swift"
DAILY_PLANNER = ROOT_DIR / "scripts" / "daily_planner.swift"
PLANS_DIR = ROOT_DIR / "data" / "plans"
DAY_START_HOUR = 9
DAY_END_HOUR = 22
BREAK_MINUTES = 10


@dataclass
class Task:
    at: datetime
    title: str
    detail: str = ""
    duration_minutes: Optional[int] = None
    sound: str = DEFAULT_SOUND
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.at.isoformat()}::{self.title}"


def load_tasks(schedule_path: Path, today: Optional[date] = None) -> list[Task]:
    today = today or date.today()
    tasks: list[Task] = []

    if schedule_path.exists():
        tasks.extend(tasks_from_file(schedule_path, today))

    daily_path = daily_plan_path(today)
    if daily_path.exists():
        tasks.extend(tasks_from_file(daily_path, today))

    return sorted(tasks, key=lambda task: task.at)


def tasks_from_file(path: Path, today: date) -> list[Task]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks: list[Task] = []

    for item in data.get("tasks", []):
        task_date = parse_task_date(item.get("date"), today)
        if task_date != today:
            continue

        task_time = datetime.strptime(item["time"], "%H:%M").time()
        tasks.append(
            Task(
                at=datetime.combine(task_date, task_time),
                title=str(item["title"]),
                detail=str(item.get("detail", "")),
                duration_minutes=item.get("duration_minutes"),
                sound=str(item.get("sound", DEFAULT_SOUND)),
                raw=item,
            )
        )

    return tasks


def parse_task_date(value: Optional[str], fallback: date) -> date:
    if not value:
        return fallback
    return datetime.strptime(value, "%Y-%m-%d").date()


def send_notification(task: Task) -> None:
    title = escape_osascript(task.title)
    detail = escape_osascript(task.detail or "该开始这件事了")
    script = f'display notification "{detail}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], check=False)


def escape_osascript(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


class AlarmPlayer:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self, sound_path: str) -> None:
        self.stop()
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop,
            args=(sound_path,),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self, sound_path: str) -> None:
        path = sound_path if Path(sound_path).exists() else DEFAULT_SOUND
        while not self._stop.is_set():
            subprocess.run(["afplay", path], check=False)
            self._stop.wait(0.8)


class OverlayApp:
    def __init__(self, task_queue: queue.Queue[Task], snooze_queue: queue.Queue[Task]) -> None:
        import tkinter as tk
        from tkinter import font as tkfont

        self.tk = tk
        self.task_queue = task_queue
        self.snooze_queue = snooze_queue
        self.alarm = AlarmPlayer()
        self.current_task: Optional[Task] = None

        self.root = tk.Tk()
        self.root.title("桌面强提醒")
        self.root.configure(bg="#101014")
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self._snooze)

        self.title_font = tkfont.Font(family="Helvetica", size=54, weight="bold")
        self.detail_font = tkfont.Font(family="Helvetica", size=24)
        self.meta_font = tkfont.Font(family="Helvetica", size=18)

        self.container = tk.Frame(self.root, bg="#101014", padx=72, pady=64)
        self.container.pack(expand=True, fill="both")

        self.time_label = tk.Label(
            self.container,
            fg="#ffcf5a",
            bg="#101014",
            font=self.meta_font,
        )
        self.time_label.pack(anchor="w", pady=(0, 24))

        self.title_label = tk.Label(
            self.container,
            fg="#ffffff",
            bg="#101014",
            font=self.title_font,
            wraplength=1100,
            justify="left",
        )
        self.title_label.pack(anchor="w", pady=(0, 24))

        self.detail_label = tk.Label(
            self.container,
            fg="#d8d8e0",
            bg="#101014",
            font=self.detail_font,
            wraplength=1100,
            justify="left",
        )
        self.detail_label.pack(anchor="w", pady=(0, 40))

        button_row = tk.Frame(self.container, bg="#101014")
        button_row.pack(anchor="w")

        self.done_button = tk.Button(
            button_row,
            text="完成",
            command=self._dismiss,
            font=self.meta_font,
            padx=28,
            pady=12,
        )
        self.done_button.pack(side="left", padx=(0, 16))

        self.snooze_button = tk.Button(
            button_row,
            text="5 分钟后再提醒",
            command=self._snooze,
            font=self.meta_font,
            padx=28,
            pady=12,
        )
        self.snooze_button.pack(side="left")

    def run(self) -> None:
        self.root.after(300, self._poll)
        self.root.mainloop()

    def _poll(self) -> None:
        if not self.current_task:
            try:
                task = self.task_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                self._show(task)
        self.root.after(300, self._poll)

    def _show(self, task: Task) -> None:
        self.current_task = task
        send_notification(task)
        self.alarm.start(task.sound)

        self.time_label.config(text=task.at.strftime("%H:%M"))
        self.title_label.config(text=task.title)
        self.detail_label.config(text=task.detail or "时间到了，请现在处理这件事。")

        self.root.deiconify()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()

    def _dismiss(self) -> None:
        self.alarm.stop()
        self.current_task = None
        self.root.withdraw()

    def _snooze(self) -> None:
        if self.current_task:
            snoozed = Task(
                at=datetime.now() + timedelta(minutes=5),
                title=self.current_task.title,
                detail=self.current_task.detail,
                duration_minutes=self.current_task.duration_minutes,
                sound=self.current_task.sound,
                raw=self.current_task.raw,
            )
            self.snooze_queue.put(snoozed)
        self._dismiss()


class MacOverlayApp:
    def __init__(self, task_queue: queue.Queue[Task], snooze_queue: queue.Queue[Task]) -> None:
        self.task_queue = task_queue
        self.snooze_queue = snooze_queue
        self.alarm = AlarmPlayer()

    def run(self) -> None:
        while True:
            task = self.task_queue.get()
            self._show(task)

    def _show(self, task: Task) -> None:
        send_notification(task)
        self.alarm.start(task.sound)
        result = subprocess.run(
            [
                "/usr/bin/swift",
                str(NATIVE_OVERLAY),
                task.at.strftime("%H:%M"),
                task.title,
                task.detail or "时间到了，请现在处理这件事。",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.alarm.stop()

        if result.stdout.strip() == "snooze":
            self.snooze_queue.put(
                Task(
                    at=datetime.now() + timedelta(minutes=5),
                    title=task.title,
                    detail=task.detail,
                    duration_minutes=task.duration_minutes,
                    sound=task.sound,
                    raw=task.raw,
                )
            )


def daily_plan_path(day: Optional[date] = None) -> Path:
    day = day or date.today()
    return PLANS_DIR / f"{day.isoformat()}.json"


def ensure_today_plan(force: bool = False) -> Optional[Path]:
    today = date.today()
    path = daily_plan_path(today)
    if path.exists() and not force:
        return path

    text = collect_daily_plan_text()
    if not text.strip():
        return None

    tasks = build_daily_plan(text, datetime.now())
    if not tasks:
        return None

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "source": text,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "tasks": tasks,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def collect_daily_plan_text() -> str:
    if platform.system() == "Darwin" and DAILY_PLANNER.exists():
        result = subprocess.run(
            ["/usr/bin/swift", str(DAILY_PLANNER)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()

    print("请输入今天要做的事，结束后按 Ctrl-D：")
    lines: list[str] = []
    try:
        while True:
            lines.append(input())
    except EOFError:
        return "\n".join(lines)


def build_daily_plan(text: str, now: datetime) -> list[dict[str, Any]]:
    items = extract_plan_items(text)
    if not items:
        return []

    cursor = next_schedule_start(now)
    tasks: list[dict[str, Any]] = []

    for item in items:
        duration = infer_duration_minutes(item)
        cursor = apply_time_hint(cursor, item)
        cursor = avoid_lunch_overlap(cursor, duration)
        if cursor.hour >= DAY_END_HOUR:
            break

        tasks.append(
            {
                "date": cursor.date().isoformat(),
                "time": cursor.strftime("%H:%M"),
                "title": item,
                "detail": f"预计 {duration} 分钟。来自今天早上的日程输入。",
                "duration_minutes": duration,
            }
        )
        cursor = cursor + timedelta(minutes=duration + BREAK_MINUTES)

    return tasks


def extract_plan_items(text: str) -> list[str]:
    normalized = re.sub(r"[，,；;。！？!?、\n\r]+", "\n", text)
    parts = []
    for raw in normalized.split("\n"):
        item = clean_plan_item(raw)
        if item:
            parts.append(item)
    return parts


def clean_plan_item(value: str) -> str:
    item = value.strip(" \t-_*0123456789.、")
    item = re.sub(r"^(今天|我今天|需要|要|还要|然后|接着|还有|帮我|安排一下)+", "", item).strip()
    item = re.sub(r"^(做|处理|完成|去|把)+", "", item).strip()
    return item[:80]


def infer_duration_minutes(item: str) -> int:
    explicit = re.search(r"(\d+(?:\.\d+)?)\s*(小时|个小时|h|H)", item)
    if explicit:
        return clamp_duration(int(float(explicit.group(1)) * 60))

    explicit = re.search(r"(\d+)\s*(分钟|分|min|m)", item)
    if explicit:
        return clamp_duration(int(explicit.group(1)))

    rules = [
        (("会议", "开会", "沟通", "面试"), 60),
        (("午饭", "吃饭", "午休", "休息"), 60),
        (("运动", "健身", "跑步"), 45),
        (("复盘", "总结", "整理"), 30),
        (("邮件", "消息", "回复"), 30),
        (("学习", "阅读", "写作", "开发", "代码"), 60),
        (("买", "取", "寄", "预约"), 30),
    ]
    if re.search(r"会($|议|面|聊|沟通)", item):
        return 60
    for keywords, minutes in rules:
        if any(keyword in item for keyword in keywords):
            return minutes
    return 45


def clamp_duration(minutes: int) -> int:
    return max(15, min(180, minutes))


def next_schedule_start(now: datetime) -> datetime:
    start = now.replace(hour=DAY_START_HOUR, minute=0, second=0, microsecond=0)
    if now <= start:
        return start

    rounded_minute = ((now.minute + 14) // 15) * 15
    cursor = now.replace(second=0, microsecond=0)
    if rounded_minute >= 60:
        cursor = cursor.replace(minute=0) + timedelta(hours=1)
    else:
        cursor = cursor.replace(minute=rounded_minute)
    return cursor


def apply_time_hint(cursor: datetime, item: str) -> datetime:
    hints = [
        (("早上", "上午"), 9, 0),
        (("中午",), 12, 0),
        (("下午",), 14, 0),
        (("傍晚",), 17, 30),
        (("晚上", "今晚"), 19, 0),
    ]
    for keywords, hour, minute in hints:
        if any(keyword in item for keyword in keywords):
            hinted = cursor.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if cursor < hinted:
                return hinted
    return cursor


def avoid_lunch_overlap(cursor: datetime, duration: int) -> datetime:
    lunch_start = cursor.replace(hour=12, minute=30, second=0, microsecond=0)
    lunch_end = cursor.replace(hour=13, minute=30, second=0, microsecond=0)
    if cursor < lunch_end and cursor + timedelta(minutes=duration) > lunch_start:
        return lunch_end
    return cursor


def scheduler_loop(
    schedule_path: Path,
    task_queue: queue.Queue[Task],
    snooze_queue: queue.Queue[Task],
    fired: set[str],
) -> None:
    planned_day: Optional[date] = None
    while True:
        now = datetime.now()
        if planned_day != now.date():
            ensure_today_plan()
            planned_day = now.date()

        try:
            tasks = load_tasks(schedule_path, now.date())
        except Exception as exc:
            print(f"读取日程失败: {exc}", flush=True)
            time.sleep(CHECK_INTERVAL_SECONDS)
            continue

        while True:
            try:
                tasks.append(snooze_queue.get_nowait())
            except queue.Empty:
                break

        for task in tasks:
            if task.key in fired:
                continue
            if now >= task.at:
                fired.add(task.key)
                task_queue.put(task)

        time.sleep(CHECK_INTERVAL_SECONDS)


def list_tasks(schedule_path: Path, plan_if_missing: bool = True) -> None:
    if plan_if_missing:
        ensure_today_plan()
    tasks = load_tasks(schedule_path)
    if not tasks:
        print("今天没有提醒。")
        return

    for task in tasks:
        duration = f" / {task.duration_minutes} 分钟" if task.duration_minutes else ""
        print(f"{task.at:%H:%M} - {task.title}{duration}")
        if task.detail:
            print(f"  {task.detail}")


def run_test(task_queue: queue.Queue[Task]) -> None:
    task_queue.put(
        Task(
            at=datetime.now(),
            title="测试提醒",
            detail="如果你看到这个全屏弹窗并听到声音，说明强提醒功能正常。",
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="macOS 桌面强提醒工具")
    parser.add_argument(
        "--schedule",
        default="schedule.json",
        help="日程 JSON 文件路径",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出今天的提醒后退出",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="启动后立即弹出一个测试提醒",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="立刻弹出今天的日程输入窗口并重新生成计划",
    )
    parser.add_argument(
        "--no-plan",
        action="store_true",
        help="启动时不弹出今天的日程输入窗口",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schedule_path = Path(args.schedule).expanduser().resolve()

    if args.plan:
        path = ensure_today_plan(force=True)
        if path:
            print(f"已生成今天计划: {path}")
        return

    if not args.no_plan and not args.test:
        ensure_today_plan()

    if args.list:
        list_tasks(schedule_path, plan_if_missing=not args.no_plan)
        return

    task_queue: queue.Queue[Task] = queue.Queue()
    snooze_queue: queue.Queue[Task] = queue.Queue()
    fired: set[str] = set()

    if args.test:
        run_test(task_queue)

    thread = threading.Thread(
        target=scheduler_loop,
        args=(schedule_path, task_queue, snooze_queue, fired),
        daemon=True,
    )
    thread.start()

    if platform.system() == "Darwin" and NATIVE_OVERLAY.exists():
        MacOverlayApp(task_queue, snooze_queue).run()
        return

    OverlayApp(task_queue, snooze_queue).run()


if __name__ == "__main__":
    main()
