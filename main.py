
import sys
from response_styler import RESPONSE_STYLE_SCRIPT
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineScript
from approval_bridge import ApprovalBridge
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QFile, QIODevice
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from file_inspector import inspect_file
from upload_guard import UploadGuard
from PySide6.QtCore import Qt

WEBCHANNEL_SCRIPT = """
(function () {
    if (window.__guardChannelInitialized) return;
    window.__guardChannelInitialized = true;

    if (typeof QWebChannel === "undefined") {
        console.log(
            "[SensitiveUploadGuard] QWebChannel unavailable"
        );
        return;
    }

    if (!window.qt || !window.qt.webChannelTransport) {
        console.log(
            "[SensitiveUploadGuard] Qt transport unavailable"
        );
        return;
    }

    new QWebChannel(qt.webChannelTransport, function (channel) {
        window.guardBridge = channel.objects.approvalBridge;

        console.log(
            "[SensitiveUploadGuard] Python bridge connected"
        );
    });
})();
"""



MONITOR_SCRIPT = """
(function () {
    if (window.__sensitiveGuardInstalled) return;
    window.__sensitiveGuardInstalled = true;

    const MARKER = "WALLED_SENSITIVE";

    let approvedPrompt = null;
    let approvedButton = null;
    let approvalPending = false;

    function getEditor(event) {
        const target = event.target;

        if (!(target instanceof Element)) return null;

        return target.closest(
            'textarea, [contenteditable="true"]'
        );
    }

    function findPromptEditor() {
        return document.querySelector(
            '#prompt-textarea, textarea, [contenteditable="true"]'
        );
    }

    function getText(editor) {
        if (!editor) return "";

        if (editor.tagName === "TEXTAREA") {
            return editor.value;
        }

        return editor.innerText || editor.textContent || "";
    }

    function isSendButton(button) {
        const label = (
            (button.getAttribute("aria-label") || "") + " " +
            (button.getAttribute("data-testid") || "") + " " +
            (button.getAttribute("title") || "")
        ).toLowerCase();

        return (
            label.includes("send") ||
            label.includes("submit") ||
            label.includes("ask")
        );
    }

    function requestApproval(prompt, onApproved) {
        if (!window.guardBridge) {
            console.log(
                "[SensitiveUploadGuard] Python bridge unavailable"
            );
            return;
        }

        if (approvalPending) return;

        approvalPending = true;

        window.guardBridge.requestApproval(
            prompt,
            function (approved) {
                approvalPending = false;

                if (approved === true) {
                    console.log(
                        "[SensitiveUploadGuard] User approved prompt"
                    );

                    onApproved();
                } else {
                    console.log(
                        "[SensitiveUploadGuard] User cancelled prompt"
                    );
                }
            }
        );
    }

    // -----------------------------------
    // ENTER KEY PROTECTION
    // -----------------------------------

    window.addEventListener("keydown", function (event) {
        if (event.key !== "Enter") return;
        if (event.shiftKey || event.isComposing) return;

        const editor = getEditor(event);

        if (!editor) return;

        const prompt = getText(editor);

        if (!prompt.trim()) return;

        if (!prompt.includes(MARKER)) return;

        if (approvedPrompt === prompt) {
            approvedPrompt = null;

            console.log(
                "[SensitiveUploadGuard] Approved prompt released"
            );

            return;
        }

        event.preventDefault();
        event.stopImmediatePropagation();

        console.log(
            "[SensitiveUploadGuard] BLOCKED sensitive Enter"
        );

        requestApproval(prompt, function () {
            if (!editor.isConnected ||
                getText(editor) !== prompt) {
                console.log(
                    "[SensitiveUploadGuard] Prompt changed"
                );
                return;
            }

            approvedPrompt = prompt;

            try {
                editor.dispatchEvent(
                    new KeyboardEvent("keydown", {
                        key: "Enter",
                        code: "Enter",
                        bubbles: true,
                        cancelable: true
                    })
                );
            } finally {
                approvedPrompt = null;
            }
        });

    }, true);

    // -----------------------------------
    // SEND BUTTON PROTECTION
    // -----------------------------------

    window.addEventListener("click", function (event) {
        if (!(event.target instanceof Element)) return;

        const button = event.target.closest("button");

        if (!button || !isSendButton(button)) return;

        const editor = findPromptEditor();
        const prompt = getText(editor);

        if (!prompt.includes(MARKER)) return;

        if (approvedButton === button) {
            approvedButton = null;

            console.log(
                "[SensitiveUploadGuard] Approved Send released"
            );

            return;
        }

        event.preventDefault();
        event.stopImmediatePropagation();

        console.log(
            "[SensitiveUploadGuard] BLOCKED Send button"
        );

        requestApproval(prompt, function () {
            if (!editor.isConnected ||
                !button.isConnected ||
                getText(editor) !== prompt) {
                console.log(
                    "[SensitiveUploadGuard] Prompt or button changed"
                );
                return;
            }

            approvedButton = button;

            try {
                button.click();
            } finally {
                approvedButton = null;
            }
        });

    }, true);

    console.log(
        "[SensitiveUploadGuard] Prompt protection installed"
    );

})();
"""



class GuardWebPage(QWebEnginePage):

    def javaScriptConsoleMessage(
        self, level, message, line_number, source_id
    ):
        if "[SensitiveUploadGuard]" in message:
            print(
                f"[Browser Monitor] {message}",
                flush=True
            )

    def chooseFiles(
        self, mode, old_files, accepted_mime_types
    ):
        print("[DEBUG] chooseFiles called", flush=True)
        selected_files = super().chooseFiles(
            mode,
            old_files,
            accepted_mime_types
        )

        print("[DEBUG] Selected files:", selected_files, flush=True)
        if not selected_files:
            return []

        approved_files = []

        for file_path in selected_files:

            file_name = Path(file_path).name

            print(f"[Guard] Inspecting file: {file_name}")

            try:
                sensitive = inspect_file(file_path)
            except Exception as error:
                print(f"[Guard] Inspection error: {error}", flush=True)
                sensitive = None
            print(f"[DEBUG] Inspection result: {sensitive}", flush=True)

            if sensitive is None:
                QMessageBox.warning(
                    None,
                    "Upload Blocked",
                    f"Unable to inspect file: {file_name}"
                )

                print("[Guard] Inspection failed")
                continue

            if sensitive:
                dialog = QMessageBox()

                dialog.setWindowTitle(
                    "Sensitive Upload Guard"
                )

                dialog.setIcon(
                    QMessageBox.Icon.Warning
                )

                dialog.setText(
                    "Sensitive content detected in file."
                )

                dialog.setInformativeText(
                    f"File: {file_name}\n\n"
                    "Do you want to continue?"
                )

                dialog.setStandardButtons(
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.Cancel
                )

                dialog.button(
                    QMessageBox.StandardButton.Yes
                ).setText("Continue")

                dialog.setDefaultButton(
                    QMessageBox.StandardButton.Cancel
                )

                result = dialog.exec()

                if result != QMessageBox.StandardButton.Yes:
                    print(
                        f"[Guard] Upload cancelled: {file_name}"
                    )
                    continue

            approved_files.append(file_path)

            print(f"[Guard] Upload allowed: {file_name}")

        return approved_files


def load_webchannel_library():
    file = QFile(":/qtwebchannel/qwebchannel.js")

    if not file.open(QIODevice.OpenModeFlag.ReadOnly):
        raise RuntimeError(
            "Unable to load Qt WebChannel JavaScript"
        )

    source = bytes(file.readAll()).decode("utf-8")
    file.close()

    return source


class SensitiveUploadGuard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sensitive Upload Guard")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.add_browser("ChatGPT", "https://chatgpt.com")
        self.add_browser("Perplexity", "https://www.perplexity.ai")

    
    def add_browser(self, name, url):
        browser = QWebEngineView()
        browser.setContextMenuPolicy(
        Qt.ContextMenuPolicy.NoContextMenu
      )

        page = GuardWebPage(browser)
        browser.setPage(page)
        print(f"[DEBUG] {name} page: {type(browser.page()).__name__}", flush=True)
        channel = QWebChannel(page)
        bridge = ApprovalBridge(page)

        channel.registerObject("approvalBridge", bridge)
        page.setWebChannel(channel)
        webchannel_script = QWebEngineScript()
        webchannel_script.setName("SensitiveGuardWebChannel")
        webchannel_script.setSourceCode(
            load_webchannel_library() + "\n" + WEBCHANNEL_SCRIPT
        )
        webchannel_script.setInjectionPoint(
            QWebEngineScript.InjectionPoint.DocumentReady
        )
        webchannel_script.setWorldId(
            QWebEngineScript.ScriptWorldId.MainWorld
        )
        webchannel_script.setRunsOnSubFrames(False)

        page.scripts().insert(webchannel_script)

        browser.guard_channel = channel
        browser.guard_bridge = bridge

        browser.loadFinished.connect(
            lambda success, b=browser: self.inject_monitor(b, success)
        )

        browser.setUrl(QUrl(url))
        self.tabs.addTab(browser, name)

    def inject_monitor(self, browser, success):
        if not success:
            print("[Guard] Page failed to load.")
            return

        browser.page().runJavaScript(RESPONSE_STYLE_SCRIPT)
        print("[Guard] Monitoring script injected.")


if __name__ == "__main__":
    app = UploadGuard(sys.argv)

    window = SensitiveUploadGuard()
    window.show()

    sys.exit(app.exec())
