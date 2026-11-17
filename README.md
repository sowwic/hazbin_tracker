# Hazbin Tracker

![Tests](https://github.com/sowwic/hazbin_tracker/actions/workflows/unit_tests.yml/badge.svg)
![Code Quality](https://github.com/sowwic/hazbin_tracker/actions/workflows/code_quality.yml/badge.svg)

**[Documentation](https://sowwic.github.io/hazbin_tracker/)**

A menu-bar app that watches the Hazbin Hotel store for new trading cards and tells you
when some are published.

- **Background checks.** Runs every 60 minutes by default, and on demand from the tray menu.
- **Notifications.** A desktop notification (click it to open the store), and optionally a
  push notification to your phone through [Pushover](https://pushover.net).
- **History.** A dialog with the results of previous checks.
- **Settings.** Edited in a config editor and stored in `~/.config/HazbinTracker`.

## Installation

Only macOS is supported.

1. Download `HazbinTracker-<version>-macos-<arch>.zip` from the
   [latest release](https://github.com/sowwic/hazbin_tracker/releases/latest).
2. Unzip it and move `HazbinTracker.app` to your Applications folder.
3. Launch it, the icon appears in the menu bar.

See the [User Guide](https://sowwic.github.io/hazbin_tracker/user/) for the settings and
the Pushover setup.

## Development

The project uses [uv](https://docs.astral.sh/uv/) and Python 3.14.

```sh
git clone https://github.com/sowwic/hazbin_tracker.git
cd hazbin_tracker
uv sync --locked --dev
uv run python -m hazbin_tracker.main   # run the app
make check                             # lint + tests
make help                              # list all targets
```

The distribution is named `sowwic-hazbin-tracker`, the import package is `hazbin_tracker`.
See the [Developer Guide](https://sowwic.github.io/hazbin_tracker/dev/) for the architecture
and the build.

## Releasing

Add a `v x.y.z` entry to `CHANGELOG.rst`, update `VERSION` (`make update-version`) and merge
to `master`. Then run `make release VERSION=x.y.z` from `master`: it tags the release, and CI
creates the GitHub release with the macOS build attached.
