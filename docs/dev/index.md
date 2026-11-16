# Developer Guide

## Setup

The project uses [uv](https://docs.astral.sh/uv/) and Python 3.14 (pinned in
`.python-version`).

```sh
uv sync --locked --dev
```

Run the app from source:

```sh
uv run python -m hazbin_tracker.main
```

The VS Code launch configuration `HazbinTracker` does the same and reads `.env`. Set
`HAZBIN_DEBUG=1` to turn on debug logging.

## Make targets

The Makefile includes shared targets from [sowwic/makefiles](https://github.com/sowwic/makefiles),
fetched into `.make/` (committed). `make update-make` fetches them again and `make help` lists
every target.

| Target | What it does |
| --- | --- |
| `make check` | Lint and tests |
| `make lint`, `make lint-fix`, `make format` | Ruff on `src` and `tests` |
| `make pytest`, `make pytest-pdb` | Run the tests, optionally dropping into pdb on failure |
| `make qrc` | Regenerate `resources_rc.py` from `resources.qrc` |
| `make bundle`, `make app` | Build `dist/HazbinTracker.app` with PyInstaller |
| `make install` | Copy the built app to `/Applications` |
| `make iconset` | Regenerate the `.icns` icon from `hazbin.png` |
| `make mkdocs` | Serve these docs |

Run a single test with `uv run pytest tests/test_tracker.py::test_name`. On a headless machine
set `QT_QPA_PLATFORM=offscreen`, which CI does as well.

## Project layout

The distribution on PyPI is `sowwic-hazbin-tracker`, but the import package is `hazbin_tracker`
(`module-name` under `[tool.uv.build-backend]` in `pyproject.toml`).

* [Architecture](architecture.md)
* [Building and releasing](releasing.md)

## Conventions

* Google-style docstrings (`Args:`, `Returns:`, `Raises:`), which the API reference is built from.
* Ruff with a line length of 89.
* `develop` is the default and pull request branch, `master` is the release branch.
* User visible changes are recorded in `CHANGELOG.rst`.
* Dependabot opens its pull requests against `develop`.
