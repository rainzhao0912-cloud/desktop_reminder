import AppKit

final class OverlayController: NSObject {
    private var window: NSWindow!

    init(time: String, title: String, detail: String) {
        super.init()
        buildWindow(time: time, title: title, detail: detail)
    }

    private func buildWindow(time: String, title: String, detail: String) {
        let screenFrame = NSScreen.main?.frame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        window = NSWindow(
            contentRect: screenFrame,
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        window.level = .screenSaver
        window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]
        window.backgroundColor = NSColor(calibratedRed: 0.06, green: 0.06, blue: 0.08, alpha: 0.98)
        window.isOpaque = true
        window.makeKeyAndOrderFront(nil)

        let content = NSView(frame: screenFrame)
        window.contentView = content

        let stack = NSStackView()
        stack.orientation = .vertical
        stack.alignment = .leading
        stack.spacing = 26
        stack.translatesAutoresizingMaskIntoConstraints = false
        content.addSubview(stack)

        let timeLabel = label(time, size: 24, weight: .semibold, color: NSColor(calibratedRed: 1.0, green: 0.81, blue: 0.35, alpha: 1.0))
        let titleLabel = label(title, size: 58, weight: .bold, color: .white)
        let detailLabel = label(detail, size: 28, weight: .regular, color: NSColor(calibratedWhite: 0.86, alpha: 1.0))
        titleLabel.maximumNumberOfLines = 3
        detailLabel.maximumNumberOfLines = 5

        stack.addArrangedSubview(timeLabel)
        stack.addArrangedSubview(titleLabel)
        stack.addArrangedSubview(detailLabel)

        let buttons = NSStackView()
        buttons.orientation = .horizontal
        buttons.spacing = 16
        buttons.alignment = .centerY

        let doneButton = NSButton(title: "完成", target: self, action: #selector(done))
        let snoozeButton = NSButton(title: "5 分钟后再提醒", target: self, action: #selector(snooze))
        for button in [doneButton, snoozeButton] {
            button.bezelStyle = .rounded
            button.controlSize = .large
            button.font = NSFont.systemFont(ofSize: 20, weight: .medium)
            buttons.addArrangedSubview(button)
        }
        stack.addArrangedSubview(buttons)

        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 84),
            stack.trailingAnchor.constraint(lessThanOrEqualTo: content.trailingAnchor, constant: -84),
            stack.centerYAnchor.constraint(equalTo: content.centerYAnchor)
        ])
    }

    private func label(_ text: String, size: CGFloat, weight: NSFont.Weight, color: NSColor) -> NSTextField {
        let field = NSTextField(labelWithString: text)
        field.font = NSFont.systemFont(ofSize: size, weight: weight)
        field.textColor = color
        field.backgroundColor = .clear
        field.lineBreakMode = .byWordWrapping
        field.preferredMaxLayoutWidth = 1100
        return field
    }

    @objc private func done() {
        print("done")
        NSApp.terminate(nil)
    }

    @objc private func snooze() {
        print("snooze")
        NSApp.terminate(nil)
    }
}

let args = CommandLine.arguments
let time = args.count > 1 ? args[1] : "--:--"
let title = args.count > 2 ? args[2] : "Reminder"
let detail = args.count > 3 ? args[3] : "Time to start."

let app = NSApplication.shared
app.setActivationPolicy(.regular)
let controller = OverlayController(time: time, title: title, detail: detail)
_ = controller
app.activate(ignoringOtherApps: true)
app.run()

