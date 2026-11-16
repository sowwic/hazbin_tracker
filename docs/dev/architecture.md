# Architecture

The app is a PySide6 tray application. A timer asks the scraper for the store's cards off the
GUI thread, the result is compared with the cards seen before, and the outcome is reported to the
user through Qt signals.

## Modules

### `core.scrapper`

`CardsScraper` pages through the store's `products.json` with `curl_cffi` (impersonating a
browser, as the store rejects plain clients), with a delay between pages and retries with
exponential backoff. It raises `ScraperError`, or `RateLimitedError` when the store keeps
answering `429`. Its tunables are in `core/constants.py` and in the `ScraperConfig` dataclass.

### `core.cards_tracker`

`CardsTracker` is a `QObject` that:

* owns the `QTimer` of the periodic check (`start_periodic_check_timer`, which is also called
  again when the config changes),
* runs a `CheckWorker` (a `QRunnable`) on the thread pool, so a slow request never blocks the UI,
* compares the fetched cards with `track_data.json` and records the result in
  `check_history.json`,
* sends the Pushover message when enabled,
* emits `new_cards_found`, `check_completed`, `check_failed` and `repeated_checks_failed`
  (after `MAX_CONSECUTIVE_FAILED_CHECKS` failures in a row).

### `core.config`

`HazbinAppConfig` is a [json-config](https://github.com/sowwic/json-config) `LayeredConfig`
with a single root layer backed by `config.json`. The values are pydantic models
(`HazbinAppConfigValues` with `PushoverConfigValues` and `CardsTrackerConfigValues` as nested
categories). `get_app_config()` returns the config of the running application.

### `ui`

* `HazbinTrackerApplication` creates the config, the tracker and the tray icon, and prevents a
  second instance with a lock file. Its `configChanged` signal tells the tracker to restart its
  timer.
* `tray.py` holds the tray icon and its menu. It only reacts to tracker signals.
* The settings editor is `ConfigEditorDialog` of
  [json-config-qt](https://github.com/sowwic/json-config-qt) showing the app config. Saving a
  layer emits `configChanged`.
* `check_history_dialog.py` and `about_dialog.py` are plain dialogs.

New behavior usually means a new tracker signal and a slot on the tray or a dialog.

### `version`

`version.py` reads the `VERSION` file, from the project root or from the PyInstaller bundle
(`sys._MEIPASS`) when frozen. The spec bundles `VERSION` as data.

## User files

All user files live in the directory defined as `APP_DATA_DIR` in `core/constants.py`:
`$XDG_CONFIG_HOME/HazbinTracker` (`~/.config/HazbinTracker`) on macOS and Linux, the platform
data directory on Windows. On macOS the files of the former location
(`~/Library/Application Support/HazbinTracker`) are moved there on first start.

## API reference

The API reference is generated from the docstrings by `mkdocs-autoapi` and `mkdocstrings`.
