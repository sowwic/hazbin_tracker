# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Hazbin Tracker is a macOS menu-bar (tray) app, built with PySide6, that periodically checks the Hazbin Hotel store's products JSON for new cards and notifies through tray messages and optionally Pushover. Python is pinned to 3.14 (`.python-version`); dependencies are managed with `uv`.

## Commands

The Makefile includes shared targets from `.make/` (fetched from `sowwic/makefiles`; `make update-make` refreshes them; commit `.make/`). `make help` lists everything.

- `uv sync --locked --dev` — install
- `make check` — lint + tests; `make lint` / `make lint-fix` / `make format` — Ruff on `src tests` (line length 89, rules E/F/UP/D; lint fails the shell on errors)
- `make pytest` — `uv run pytest tests` (coverage always on); single test: `uv run pytest tests/test_tracker.py::test_name`; `make pytest-pdb` drops into pdb
- `make qrc` — regenerate `resources/resources_rc.py` from `resources.qrc` (needed after changing icons or the `.qrc`; also a prerequisite of `bundle`)
- `make bundle` / `make app` — PyInstaller build from `HazbinTracker.spec` into `dist/HazbinTracker.app`; `make install` copies it to `/Applications`; `make iconset` regenerates the `.icns` from `hazbin.png`
- `make update-version` — sync `pyproject.toml` with the `VERSION` file
- `make release VERSION=x.y.z` — runs `release.py` from `sowwic/gh-workflows` (tags, pushes, back-merges `master` into `develop`). It needs a `v x.y.z` entry in `CHANGELOG.rst`, matching `VERSION` and `pyproject.toml`, a clean `master` checkout.
- `make mkdocs` — docs dev server (`docs/`, `mkdocs.yml`)

Tests need `QT_QPA_PLATFORM=offscreen` on headless machines (CI sets it).

## Architecture

The PyPI distribution is `sowwic-hazbin-tracker`, but the import package is `hazbin_tracker` (`[tool.uv.build-backend] module-name` in `pyproject.toml`; keep it when touching the build config).

- `core/scrapper.py` — `CardsScraper` pages through the store's products JSON with `curl_cffi` (browser impersonation) and retry/backoff; raises `ScraperError` / `RateLimitedError`. Tunables live in `core/constants.py` and `ScraperConfig`.
- `core/cards_tracker.py` — `CardsTracker` (a `QObject`) owns the `QTimer` for periodic checks, runs `CheckWorker` (a `QRunnable`) on the thread pool so fetching stays off the GUI thread, diffs results against the persisted `track_data.json` and check history, and emits Qt signals (`new_cards_found`, `check_failed`, `repeated_checks_failed`, ...). It also sends the Pushover notification. It reaches settings through the running `HazbinTrackerApplication`.
- `core/config.py` — `HazbinAppConfig`, a `json_config` `LayeredConfig` whose pydantic `ConfigValues` hold the Pushover and tracker settings (nested categories need an `alias`). `json-config` is the author's own library, pinned by git tag in `[tool.uv.sources]`.
- `ui/` — `HazbinTrackerApplication` (single-instance via a temp lock file; creates config, tracker and tray), `tray.py` (tray icon and menu, reacts to tracker signals), plus the settings, history and about dialogs. Everything is wired with signals/slots, so new behaviour usually means a new tracker signal and a tray/dialog slot.
- `version.py` reads the `VERSION` file from the project root, or from `sys._MEIPASS` when frozen by PyInstaller; the spec bundles `VERSION` as data. `hooks-pyside6.py` is a PyInstaller hook.
- User files (config, track data, history, logs) live under the `platformdirs` data dir defined in `core/constants.py`.

## Conventions

- Google-style docstrings (`Args:`, `Returns:`, `Raises:`).
- Prefer flexibility: when a subclass needs to run code at a point inside a base class's sequence (before or after a step), add an overridable hook (`pre_*` / `post_*`, a no-op in the base class) rather than changing constructor arguments, reordering the subclass `__init__` around `super().__init__`, or copying the base sequence.
- `develop` is the default and PR branch; `master` is the release branch. `VERSION` is the version source. Record user-visible changes in `CHANGELOG.rst`.
- CI uses the reusable workflows of `sowwic/gh-workflows` (tests, lint, docs, release). `build_app.yml` builds the macOS app on `v*` tags and attaches the zip to the GitHub release.
- Dependabot targets `develop`.

## Development

- If the current branch is `develop`, ask the user for the GitHub issue number before starting work. Use the related branch.
- Do not commit unless asked to.
- Do not update CHANGELOG unless asked to.
- Do not push extra created worktrees to remote. Once work in them is done, patch it back into the feature branch and delete the extra worktree.
- When a task done in a worktree is finished, do this without being asked: exit the worktree (`ExitWorktree` keep), cherry-pick its commit(s) onto the feature branch in the main checkout, then remove the worktree and its branch. Git can't reach the main checkout from inside the worktree session.

## Qt Notes

New QWidgets should follow this structure unless it causes issues. `__init__` runs these methods in order:

- `_create_actions` — creates actions and configures them
- `_create_widgets` — creates child widgets and configures them
- `_create_layouts` — creates layouts, populates them with widgets
- `_create_connections` — creates signal-slot connections

## Token hygiene

- Find symbols with the LSP tool if possible before grepping; then Read with offset/limit.
