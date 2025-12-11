# Developer Guide

## Setup

Project is using Poetry and Python 3.12 as basic requirements.

1. Create a new venv and activate it
2. Run `poetry install --with dev`
3. If you are using VsCode will launch new instance of the app.

## Make commands

* `check` - runs ruff plus pytest
* `pytest-pdb` - runs pytest with pdb on error
* `qrc` - rebuilds qrc resources in case of new/updated icons
* `iconset` - builds iconset for main app icon (Mac)
* `app` - runs pyinstaller that uses `HazbinTracker.spec` file
* `install` - Installs app into Applications directory (Mac)
* `update-version` - updates pyproject.toml to match one in VERSION file
