
from PySide6.QtCore import QEvent
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QMessageBox


class UploadGuard(QApplication):

    def notify(self, receiver, event):

        event_type = event.type()

        # Block file and image drag-and-drop.
        if event_type in (
            QEvent.Type.DragEnter,
            QEvent.Type.DragMove,
            QEvent.Type.Drop
        ):
            mime = event.mimeData()

            if (
                mime.hasUrls()
                or mime.hasImage()
                or mime.hasFormat("application/octet-stream")
            ):
                event.ignore()

                if event_type == QEvent.Type.DragEnter:
                    print(
                        "[Guard] File drag-and-drop blocked"
                    )

                return True

        # Block keyboard-based file and image paste.
        if event_type == QEvent.Type.KeyPress:

            if event.matches(
                QKeySequence.StandardKey.Paste
            ):
                mime = self.clipboard().mimeData()

                if mime and (
                    mime.hasImage()
                    or mime.hasUrls()
                    or any(
                        fmt.startswith("image/")
                        for fmt in mime.formats()
                    )
                ):
                    event.accept()

                    print(
                        "[Guard] Clipboard upload blocked"
                    )

                    QMessageBox.warning(
                        None,
                        "Sensitive Upload Guard",
                        "Direct file and image paste is blocked.\n\n"
                        "Please use the attachment button "
                        "so the file can be inspected."
                    )

                    return True

        return super().notify(receiver, event)
