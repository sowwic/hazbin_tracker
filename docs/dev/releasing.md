# Building and releasing

## Building the app

```sh
make bundle      # or: make app
```

This compiles the Qt resources and runs PyInstaller with `HazbinTracker.spec`, producing
`dist/HazbinTracker.app`. The app has no Dock icon (`LSUIElement`), and its version comes from
the `VERSION` file. `make install` copies it to `/Applications`.

Only macOS is built.

## Releasing

Releases are cut from the `master` branch.

1. Add a `v x.y.z` entry to `CHANGELOG.rst`.
2. Put the version in `VERSION` and run `make update-version` to sync `pyproject.toml`
   (`uv.lock` too).
3. Commit and merge to `master`.
4. From a clean, up to date `master` run:

   ```sh
   make release VERSION=x.y.z
   ```

`make release` runs `release.py` of
[sowwic/gh-workflows](https://github.com/sowwic/gh-workflows). It checks that the changelog has
the entry, that `VERSION` and `pyproject.toml` match and that the version is higher than the
latest tag. Then it tags `vx.y.z`, pushes the tag and merges `master` back into `develop`.

Pushing the tag triggers two workflows:

* **Release** creates the GitHub release with the changelog entry as its notes.
* **Build app** builds the app on a macOS runner, zips it as
  `HazbinTracker-<version>-macos-<arch>.zip` and attaches it to that release.

## CI

| Workflow | When | What |
| --- | --- | --- |
| `unit_tests.yml` | push, pull request | pytest on Ubuntu and Windows (shared `python-tests.yml`) |
| `code_quality.yml` | pull request | Ruff (shared `python-lint.yml`) |
| `deploy_docs.yml` | push to `master` | publishes these docs to GitHub Pages (shared `mkdocs-deploy.yml`) |
| `release.yml` | tag `v*` | GitHub release (shared `release.yml`) |
| `build_app.yml` | tag `v*`, pull requests touching the build files | builds the macOS app, attaches it to the release |

The shared workflows come from [sowwic/gh-workflows](https://github.com/sowwic/gh-workflows).
