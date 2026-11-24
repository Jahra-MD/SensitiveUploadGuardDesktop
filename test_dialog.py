
import sys
from PySide6.QtWidgets import QApplication
from approval_bridge import ApprovalBridge

app = QApplication(sys.argv)

bridge = ApprovalBridge()

approved = bridge.requestApproval(
    "Hello WALLED_SENSITIVE TEST_123"
)

print("Approved:", approved)
