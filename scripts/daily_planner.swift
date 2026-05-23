import AppKit

final class PlannerController: NSObject, NSWindowDelegate {
    private var window: NSWindow!
    private let textView = NSTextView()

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

        let scroll = NSScrollView()
        scroll.borderType = .bezelBorder
        scroll.hasVerticalScroller = true
        scroll.translatesAutoresizingMaskIntoConstraints = false
        textView.font = NSFont.systemFont(ofSize: 20)
        textView.string = ""
        textView.isRichText = false
        textView.allowsUndo = true
        scroll.documentView = textView

        let submit = NSButton(title: "生成今天计划", target: self, action: #selector(submit))
        submit.bezelStyle = .rounded
        submit.controlSize = .large

        let later = NSButton(title: "稍后", target: self, action: #selector(cancel))
        later.bezelStyle = .rounded
        later.controlSize = .large

        let buttons = NSStackView(views: [later, submit])
        buttons.orientation = .horizontal
        buttons.spacing = 12
        buttons.translatesAutoresizingMaskIntoConstraints = false

        for view in [title, subtitle, scroll, buttons] {
            content.addSubview(view)
        }

        NSLayoutConstraint.activate([
            title.topAnchor.constraint(equalTo: content.topAnchor, constant: 28),
            title.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 32),
            title.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -32),

            subtitle.topAnchor.constraint(equalTo: title.bottomAnchor, constant: 8),
            subtitle.leadingAnchor.constraint(equalTo: title.leadingAnchor),
            subtitle.trailingAnchor.constraint(equalTo: title.trailingAnchor),

            scroll.topAnchor.constraint(equalTo: subtitle.bottomAnchor, constant: 22),
            scroll.leadingAnchor.constraint(equalTo: title.leadingAnchor),
            scroll.trailingAnchor.constraint(equalTo: title.trailingAnchor),
            scroll.bottomAnchor.constraint(equalTo: buttons.topAnchor, constant: -24),

            buttons.trailingAnchor.constraint(equalTo: title.trailingAnchor),
            buttons.bottomAnchor.constraint(equalTo: content.bottomAnchor, constant: -28)
        ])

        window.makeKeyAndOrderFront(nil)
        window.makeFirstResponder(textView)
    }

    @objc private func submit() {
        print(textView.string)
        NSApp.terminate(nil)
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

