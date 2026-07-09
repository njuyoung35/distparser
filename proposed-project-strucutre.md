# 📁 Proposed Project Structure

```
distparser/
├── .gitignore
├── .readthedocs.yaml          # <-- NEW
├── AGENTS.md                  # <-- UPDATED (with docs & release sections)
├── CHANGELOG.md               # <-- NEW (create empty or with initial entry)
├── LICENSE
├── README.md
├── mkdocs.yml                 # <-- NEW
├── pyproject.toml             # <-- UPDATED (docs extra)
├── docs/
│   ├── index.md               # (already exists, keep it)
│   ├── user_guide.md          # <-- NEW
│   ├── api_reference.md       # <-- NEW
│   ├── releasing.md           # <-- NEW
│   └── development.md         # <-- NEW
├── src/
│   └── distparser/
│       ├── __init__.py
│       ├── core.py
│       └── version.py
└── tests/
    └── test_core.py
```
