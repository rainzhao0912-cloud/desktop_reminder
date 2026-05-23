# 桌面强提醒工具

这是一个 macOS 本地桌面提醒工具。它会读取 `schedule.json` 里的日程，到点后弹出全屏置顶提醒，并播放系统提示音，适合做“必须看到”的强提醒。

## 快速开始

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
- 加入“必须输入确认文字才能关闭”的更强提醒模式
- 增加每日复盘和明日计划生成
