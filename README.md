# distparser

**Parse function‑call syntax strings into frozen `scipy.stats` distributions**

[![PyPI version](https://badge.fury.io/py/distparser.svg)](https://badge.fury.io/py/distparser)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why `distparser`?

When you have configuration files or user input that specifies a probability
distribution (e.g. `"norm(loc=0, scale=1)"`), you want to turn that string
into a ready‑to‑sample object. `distparser` does exactly that, with a tiny
API and zero surprises.

## Installation

```bash
pip install distparser
```

## Quick Start

```
from distparser import parse_dist

# Positional arguments (order matters)
dist = parse_dist("uniform(0, 1)")
sample = dist.rvs()          # e.g. 0.374

# Keyword arguments (order ignored)
dist = parse_dist("norm(loc=0, scale=1)")
samples = dist.rvs(size=5)   # array([-0.12, 1.03, ...])

# Mixed (positional + keyword) – works, but not recommended
dist = parse_dist("expon(scale=2, loc=1)")
```

## Supported Distributions

Built‑in registry covers the most common continuous distributions:

- `uniform(loc, scale)`
- `norm(loc, scale)`
- `expon(loc, scale)`
- … and many more (see [docs](https://distparser.readthedocs.io)).

You can **add your own** at runtime:

```python
from distparser import register_distribution
from scipy.stats import gumbel_r

register_distribution("gumbel", gumbel_r, ["loc", "scale"])
```

## Development

See [AGENTS.md](AGENTS.md) for development setup and guidelines.

## License

MIT
