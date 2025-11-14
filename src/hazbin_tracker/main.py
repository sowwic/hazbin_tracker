import sys

from hazbin_tracker.api import HazbinTrackerApplication


def main():
    app = HazbinTrackerApplication(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
