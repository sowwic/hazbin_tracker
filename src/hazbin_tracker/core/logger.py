import logging
import sys
from hazbin_tracker.core.constants import APP_DATA_DIR, DEBUG


class HazbinLogger(logging.Logger):

    LOG_FILE_PATH = str(APP_DATA_DIR / "hazbin.log")
    FILE_LEVEL = logging.WARNING
    STD_OUT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    FILE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    def __init__(self, name, level=logging.INFO):
        level = logging.DEBUG if DEBUG else level
        super().__init__(name, level)
        self.init_handlers()

    def init_handlers(self):
        if self.hasHandlers():
            return

        # Stream to stdout
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(self.STD_OUT_FORMAT))
        self.addHandler(stream_handler)

        # File handler
        file_handler = logging.FileHandler(self.LOG_FILE_PATH)
        file_handler.setLevel(self.FILE_LEVEL)
        file_handler.setFormatter(logging.Formatter(self.FILE_FORMAT))
        self.addHandler(file_handler)
