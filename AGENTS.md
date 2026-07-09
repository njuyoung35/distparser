# AGENTS.md – Guidelines for `distparser`

This file defines the **development process** and **technical guardrails** for this project.  
Follow it strictly when proposing or implementing changes.

---

## 🧩 Tech Stack
- **Python 3.12** (minimum supported version: 3.8, but we develop with 3.12)
- **`uv`** – package manager, virtual environment, and script runner
- **`ruff`** – linting & formatting (replaces Black/isort)
- **`pytest`** – testing with coverage
- **`scipy`**, **`numpy`** – core dependencies

---

## 🔁 Development Workflow – Two‑Step Process

### 1. Spec First
Before writing **any** code, propose a clear specification that includes:
- **Scope** – what exactly will change or be added.
- **Behaviour** – how it works, with examples.
- **Edge cases** – what could go wrong and how errors are handled.
- **Version impact** – is this a `patch`, `minor`, or `major` change (per SemVer)?
- **Registry changes** – if adding a new distribution, specify its `param_order`.

Wait for **user confirmation** before proceeding.

### 2. Implement
Only after spec approval:
- Write the actual code.
- Keep changes **small and testable**.
- Include or update tests.
- Update `CHANGELOG.md` and `pyproject.toml` version if needed.

---

## 📦 Commit & Versioning Standards

- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:` – new feature (minor version bump)
  - `fix:` – bug fix (patch bump)
  - `docs:` – documentation only
  - `refactor:` – code restructuring without behaviour change
  - `chore:` – maintenance, dependencies, etc.
  - `BREAKING CHANGE:` in footer – major version bump
- **Versioning**: Strict [Semantic Versioning](https://semver.org/) – update `pyproject.toml` version accordingly.
- **Changelog**: Update `CHANGELOG.md` per [Keep a Changelog](https://keepachangelog.com/) for every user‑facing change (Added, Changed, Deprecated, Removed, Fixed, Security).

---

## 🧠 Technical Decisions & Architecture (for LLM context)

### Registry
- Defined in `core.py` as a dict `REGISTRY`.
- Each entry: `{"class": <scipy.stats distribution>, "param_order": [list of param names]}`.
- Users can extend via `register_distribution()` – mutates the global dict.

### Parsing
- Use `re` to extract `name(args)` – no full parser.
- Split arguments by commas **but respect quotes** (use a small state machine or regex).
- `ast.literal_eval` for each argument value.
- Positional → zipped with `param_order`; keywords override.

### Error Handling
- Custom exceptions: `ParseError`, `UnknownDistributionError` (both inherit from `DistParserError`).
- Error messages must be **actionable** – tell the user what and how to fix.

### Compatibility
- Version **independent** of `scipy` – we set minimum `scipy>=1.7.0` in `pyproject.toml`.
- Runtime warning if scipy too old (check in `version.py`).

---

## 🚀 Development Commands (with `uv`)

```bash
# Setup
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Format & lint (using ruff)
uv run ruff format src/ tests/
uv run ruff check --fix src/ tests/

# Type check (mypy)
uv run mypy src/

# Build distribution
uv run python -m build

# Upload to PyPI (after building)
uv run twine upload dist/*
```

> **Note**: We use `ruff` for formatting, not Black/isort – adjust `pyproject.toml` accordingly if you switch.

---

## 📚 Documentation Guide (Read the Docs)

We use **MkDocs** with the **Read the Docs** theme. All documentation lives in the `docs/` folder and is written in Markdown.

### Local Documentation Preview
To preview the docs locally:
```bash
# Install docs dependencies (if not already installed)
uv pip install -e ".[docs]"

# Serve the documentation
uv run mkdocs serve
```
Then open `http://127.0.0.1:8000` in your browser. The site auto‑reloads on changes.

### Documentation Structure
- `docs/index.md` – Homepage (quick start, features).
- `docs/user_guide.md` – Detailed usage, registry extension, error handling.
- `docs/api_reference.md` – Auto‑generated from docstrings (optional, we can do manually for now).
- `docs/releasing.md` – Step‑by‑step release guide (see below).
- `docs/development.md` – Contribution setup (links back to this `AGENTS.md`).

### Adding New Pages
1. Create a new `.md` file in `docs/`.
2. Update the `nav` section in `mkdocs.yml` to include it.

### Read the Docs Build
- The `.readthedocs.yaml` file at the project root tells RTD how to build.
- RTD will automatically build and host the latest `main` branch, plus any tagged versions (for versioned docs).

---

## 🚀 Releasing Guide (PyPI & Git Tag)

Follow these steps **strictly in order** to release a new version.

### Prerequisites
- You have write access to the PyPI project (or are the owner).
- You have `twine` installed (it's included in `[dev]` extras).
- All changes for the release are merged into `main`.

### Step‑by‑Step Release Process

1. **Run pre‑release checks** – ensure everything is clean:
   ```bash
   uv run pytest
   uv run ruff check src/ tests/
   uv run mypy src/
   ```

2. **Update version numbers** – sync both places:
   - `pyproject.toml` – change the `version = "X.Y.Z"` field.
   - `src/distparser/version.py` – change `__version__ = "X.Y.Z"`.

   > 💡 **Important**: Always keep these two in sync. A helper script can be added later, but manual is fine for now.

3. **Update `CHANGELOG.md`** – move the "Unreleased" section to the new version and add the date, following [Keep a Changelog](https://keepachangelog.com/):
   ```markdown
   ## [0.1.0] - 2026-07-09
   ### Added
   - Initial release with uniform, norm, expon.
   ```

4. **Commit the version bump**:
   ```bash
   git add pyproject.toml src/distparser/version.py CHANGELOG.md
   git commit -m "chore: release vX.Y.Z"
   ```

5. **Create a Git tag** (annotated):
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   ```

6. **Build the distribution**:
   ```bash
   uv run python -m build
   ```
   This creates `dist/distparser-X.Y.Z.tar.gz` and `dist/distparser-X.Y.Z-py3-none-any.whl`.

7. **Upload to PyPI** (test first, then live):
   ```bash
   # Test with TestPyPI (optional but recommended)
   uv run twine upload --repository testpypi dist/*
   
   # Real upload
   uv run twine upload dist/*
   ```

8. **Push the commit and tag**:
   ```bash
   git push origin main
   git push origin vX.Y.Z
   ```

9. **Verify**:
   - Installation works: `uv pip install distparser==X.Y.Z`
   - Read the Docs builds the new version automatically (check the RTD dashboard).

> **Rollback**: If something goes wrong, delete the tag (`git tag -d vX.Y.Z && git push --delete origin vX.Y.Z`) and yank the version on PyPI (`twine yank distparser==X.Y.Z`).

---

## 🤖 LLM‑Specific Instructions

- **Always** start with a spec and wait for confirmation.
- Propose **one small decision at a time** – explain trade‑offs.
- Show working code **only for the step the user confirms**.
- **Never** commit or push directly – propose changes and wait for review.
- **Never auto-clean** directories like `dist/`, `build/`, `*.pyc`, `__pycache__/`, `output/`.  
  Let the user or build tools handle cleaning (e.g., `uv clean`, `pytest --cache-clear`). If unsure, ask.
- When adding a distribution, always check `scipy.stats` docs for the correct parameter names and order.