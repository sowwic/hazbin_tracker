import sys
import logging
from PySide6.QtWidgets import QMessageBox

from hazbin_tracker.api import HazbinTrackerApplication
from hazbin_tracker.core.constants import APP_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    filename=str(APP_DATA_DIR / "hazbin.log"),
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOGGER = logging.getLogger(__name__)


def main():
    try:
        app = HazbinTrackerApplication(sys.argv)
        sys.exit(app.exec())
    except Exception as err:
        LOGGER.exception("App crash due to Exception.")
        msg = QMessageBox()
        msg.setWindowTitle("HazbinTracker Exception")
        msg.setText("Application failed to start due to an exception.")
        msg.setDetailedText(str(err))
        msg.setIcon(QMessageBox.Critical)
        msg.exec()

        return 1


if __name__ == "__main__":
    main()
