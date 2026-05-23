import AppKit

final class PlannerController: NSObject, NSWindowDelegate {
    private var window: NSWindow!
    private let inputField = NSTextField()

    override init() {
        super.init()
        buildWindow()
    }

    private func buildWindow() {
        let size = NSSize(width: 760, height: 540)
        let origin = NSPoint(
            x: (NSScreen.main?.frame.midX ?? 720) - size.width / 2,
            y: (NSScreen.main?.frame.midY ?? 450) - size.height / 2
        )
        window = NSWindow(
            contentRect: NSRect(origin: origin, size: size),
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "今天的日程"
        window.level = .floating
        window.delegate = self

        let content = NSView(frame: NSRect(origin: .zero, size: size))
        window.contentView = content

        let title = NSTextField(labelWithString: "今天要做什么？")
        title.font = NSFont.systemFont(ofSize: 30, weight: .bold)
        title.translatesAutoresizingMaskIntoConstraints = false

        let subtitle = NSTextField(labelWithString: "说出或写下任务，我会按时间顺序安排今天。")
        subtitle.font = NSFont.systemFont(ofSize: 15, weight: .regular)
        subtitle.textColor = .secondaryLabelColor
        subtitle.translatesAutoresizingMaskIntoConstraints = false

        inputField.font = NSFont.systemFont(ofSize: 22)
        inputField.placeholderString = "例如：今天要写方案，回复邮件，下午整理代码，晚上复盘"
        inputField.textColor = .black
        inputField.backgroundColor = .white
        inputField.drawsBackground = true
        inputField.isBezeled = true
        inputField.isEditable = true
        inputField.isSelectable = true
        inputField.cell?.wraps = true
        inputField.cell?.isScrollable = false
        inputField.translatesAutoresizingMaskIntoConstraints = false

        let hint = NSTextField(labelWithString: "输入示例：今天要写方案，回复邮件，下午整理代码，晚上复盘。")
        hint.font = NSFont.systemFont(ofSize: 13, weight: .regular)
        hint.textColor = .secondaryLabelColor
        hint.translatesAutoresizingMaskIntoConstraints = false

        let voice = NSButton(title: "语音输入", target: self, action: #selector(startDictation))
        voice.bezelStyle = .rounded
        voice.controlSize = .large

        let submit = NSButton(title: "生成今天计划", target: self, action: #selector(submit))
        submit.bezelStyle = .rounded
        submit.controlSize = .large

        let later = NSButton(title: "稍后", target: self, action: #selector(cancel))
        later.bezelStyle = .rounded
        later.controlSize = .large

        let buttons = NSStackView(views: [voice, later, submit])
        buttons.orientation = .horizontal
        buttons.spacing = 12
        buttons.translatesAutoresizingMaskIntoConstraints = false

        for view in [title, subtitle, inputField, hint, buttons] {
            content.addSubview(view)
        }

        NSLayoutConstraint.activate([
            title.topAnchor.constraint(equalTo: content.topAnchor, constant: 28),
            title.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 32),
            title.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -32),

            subtitle.topAnchor.constraint(equalTo: title.bottomAnchor, constant: 8),
            subtitle.leadingAnchor.constraint(equalTo: title.leadingAnchor),
            subtitle.trailingAnchor.constraint(equalTo: title.trailingAnchor),

            inputField.topAnchor.constraint(equalTo: subtitle.bottomAnchor, constant: 22),
            inputField.leadingAnchor.constraint(equalTo: title.leadingAnchor),
            inputField.trailingAnchor.constraint(equalTo: title.trailingAnchor),
            inputField.heightAnchor.constraint(equalToConstant: 170),
            inputField.bottomAnchor.constraint(lessThanOrEqualTo: hint.topAnchor, constant: -10),

            hint.leadingAnchor.constraint(equalTo: title.leadingAnchor),
            hint.trailingAnchor.constraint(equalTo: title.trailingAnchor),
            hint.bottomAnchor.constraint(equalTo: buttons.topAnchor, constant: -18),

            buttons.trailingAnchor.constraint(equalTo: title.trailingAnchor),
            buttons.bottomAnchor.constraint(equalTo: content.bottomAnchor, constant: -28)
        ])

        window.makeKeyAndOrderFront(nil)
        window.makeFirstResponder(inputField)
    }

    @objc private func submit() {
        print(inputField.stringValue)
        NSApp.terminate(nil)
    }

    @objc private func startDictation() {
        window.makeFirstResponder(inputField)

        let source = CGEventSource(stateID: .hidSystemState)
        let keyDown = CGEvent(keyboardEventSource: source, virtualKey: 63, keyDown: true)
        let keyUp = CGEvent(keyboardEventSource: source, virtualKey: 63, keyDown: false)

        keyDown?.post(tap: .cghidEventTap)
        keyUp?.post(tap: .cghidEventTap)
        usleep(120_000)
        keyDown?.post(tap: .cghidEventTap)
        keyUp?.post(tap: .cghidEventTap)

        let alert = NSAlert()
        alert.messageText = "如果没有开始听写"
        alert.informativeText = "请先在系统设置 > 键盘 > 听写中开启听写。也可以点击输入框后按 Fn 键两下。"
        alert.addButton(withTitle: "知道了")
        alert.beginSheetModal(for: window)
    }

    @objc private func cancel() {
        NSApp.terminate(nil)
    }

    func windowWillClose(_ notification: Notification) {
        NSApp.terminate(nil)
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.regular)
let controller = PlannerController()
_ = controller
app.activate(ignoringOtherApps: true)
app.run()
