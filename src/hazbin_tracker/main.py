import sys
import logging

from hazbin_tracker.api import HazbinTrackerApplication

logging.basicConfig(level=logging.INFO)


def main():
    app = HazbinTrackerApplication(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
