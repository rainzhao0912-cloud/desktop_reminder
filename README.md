# 桌面强提醒工具

这是一个 macOS 本地桌面提醒工具。它会读取 `schedule.json` 里的日程，到点后弹出全屏置顶提醒，并播放系统提示音，适合做“必须看到”的强提醒。

如果当前 Python 的 Tk 图形库不可用，程序会自动切换到 `scripts/macos_overlay.swift` 提供的 macOS 原生全屏覆盖层。

程序每天第一次运行时，会先弹出“今天的日程”窗口。你可以在输入框里写下今天要做的事，也可以使用 macOS 自带听写把语音转成文字；提交后程序会自动拆分任务、估算时长，并生成当天计划。生成的私人计划保存在 `data/plans/YYYY-MM-DD.json`，不会提交到 Git。

## 快速开始

桌面上有两个可点击入口：

- `桌面提醒工具.app`：启动当天提醒程序
- `填写今日日程.app`：立刻打开今天的日程输入窗口

日程输入窗口里有“语音输入”按钮。点击后会尝试启动 macOS 听写；如果没有反应，请先到系统设置 > 键盘 > 听写中开启听写。部分系统可能还会要求给这个应用辅助功能权限。

```bash
/usr/bin/python3 reminder.py --schedule schedule.json
```

查看今天会触发的提醒：

```bash
/usr/bin/python3 reminder.py --schedule schedule.json --list
```

立刻测试弹窗和声音：

```bash
/usr/bin/python3 reminder.py --schedule schedule.json --test
```

重新生成今天计划：

```bash
/usr/bin/python3 reminder.py --plan
```

只查看提醒、不弹出计划输入窗口：

```bash
/usr/bin/python3 reminder.py --schedule schedule.json --list --no-plan
```

## 日程格式

编辑 `schedule.json`：

```json
{
  "tasks": [
    {
      "time": "09:00",
      "title": "开始工作",
      "detail": "整理今天最重要的三件事",
      "duration_minutes": 30
    }
  ]
}
```

字段说明：

- `time`：提醒时间，格式为 `HH:MM`
- `title`：提醒标题
- `detail`：提醒详情
- `duration_minutes`：预计持续时间，可选
- `date`：指定日期，可选，格式为 `YYYY-MM-DD`；不填表示每天都可触发
- `sound`：自定义声音文件路径，可选；默认使用 macOS 系统声音

## 每日自动排程

早上输入类似下面的内容即可：

```text
今天要写项目方案，回复邮件，开一个会，下午整理代码，晚上复盘。
```

程序会把它拆成多个任务，并按当前时间或 09:00 之后的时间顺序安排。没有明确时长时，会按任务类型估算；例如会议通常按 60 分钟，邮件按 30 分钟，普通任务按 45 分钟。

## 开机自启动

如果希望它每天自动在后台运行，可以参考 `launch_agents/com.desktop-reminder.plist`。把里面的路径确认无误后复制到：

```bash
~/Library/LaunchAgents/com.desktop-reminder.plist
```

再运行：

```bash
launchctl load ~/Library/LaunchAgents/com.desktop-reminder.plist
```

注意：macOS 自带的 `/usr/bin/python3` 通常包含 Tk 弹窗支持；如果使用 Homebrew Python，可能需要额外安装对应版本的 `python-tk`。

## 下一步

后续可以继续扩展：

- 从你的日程表文件自动生成当天时间块
- 接入 Apple Calendar / Google Calendar
- 接入真正的语音识别或 AI 排程 API
- 加入“必须输入确认文字才能关闭”的更强提醒模式
- 增加每日复盘和明日计划生成
