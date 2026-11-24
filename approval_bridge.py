
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox


class ApprovalBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str, result=bool)
    def requestApproval(self, prompt):
        dialog = QMessageBox()

        dialog.setWindowTitle("Sensitive Upload Guard")
        dialog.setIcon(QMessageBox.Icon.Warning)

        dialog.setText(
            "Sensitive content detected in text prompt."
        )

        dialog.setInformativeText(
            f"Prompt: {prompt[:150]}\n\n"
            "Do you want to continue?"
        )

        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel
        )

        dialog.button(
            QMessageBox.StandardButton.Yes
        ).setText("Continue")

        result = dialog.exec()

        return result == QMessageBox.StandardButton.Yes
