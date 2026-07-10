# Releasing `distparser`

## Prerequisites

- Write access to the [PyPI project](https://pypi.org/project/distparser/).
- `twine` installed (`pip install twine`).
- All changes for the release merged into `main`.

## Step-by-Step

### 1. Pre-release checks

```bash
uv run pytest
uv run ruff check src/ tests/
uv run mypy src/
```

### 2. Bump version

Update both files:

- `pyproject.toml` — `version = "X.Y.Z"`
- `src/distparser/version.py` — `__version__ = "X.Y.Z"`

### 3. Update CHANGELOG.md

Move the `[Unreleased]` section to the new version with today's date:

```markdown
## [X.Y.Z] - YYYY-MM-DD
### Added
- ...
```

### 4. Commit & tag

```bash
git add pyproject.toml src/distparser/version.py CHANGELOG.md
git commit -m "chore: release vX.Y.Z"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
```

### 5. Build

```bash
uv run python -m build
```

This creates `dist/distparser-X.Y.Z.tar.gz` and `dist/distparser-X.Y.Z-py3-none-any.whl`.

### 6. Upload

```bash
# TestPyPI first (optional)
uv run twine upload --repository testpypi dist/*

# Live PyPI
uv run twine upload dist/*
```

### 7. Push

```bash
git push origin main
git push origin vX.Y.Z
```

### 8. Verify

```bash
pip install distparser==X.Y.Z
python -c "import distparser; print(distparser.__version__)"
```

## Rollback

If something goes wrong:

```bash
git tag -d vX.Y.Z && git push --delete origin vX.Y.Z
twine yank distparser==X.Y.Z
```
