# distparser

**Parse function‑call strings into frozen `scipy.stats` distributions —**
**with dependency resolution, arithmetic expressions, and seed management.**

[![PyPI version](https://badge.fury.io/py/distparser.svg)](https://badge.fury.io/py/distparser)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install distparser
```

## Quick Start

```python
import distparser as lib

# Parse a single distribution string
d = lib.parse_dist("norm(loc=0, scale=1)")
print(d.rvs(size=3))  # array([...])
```

## DistGraph — dependency-aware evaluation

```python
from distparser import DistGraph

config = {
    "mean": 5.0,
    "noise": "norm(0, 0.1)",
    "measurement": "mean + noise",
}

graph = DistGraph(config, seed=42)
result = graph.resolve_all()
print(result["measurement"])  # 5.0 + sample from N(0, 0.1)
```

## Features

- **15 built-in distributions** — `uniform`, `norm`, `expon`, `gamma`, `beta`, `lognorm`, `weibull_min`, `t`, `chi2`, `f`, `pareto`, `cauchy`, `laplace`, `logistic`, `rayleigh`
- **Distribution aliases** — `normal` → `norm`, `gaussian` → `norm`, `unif` → `uniform`
- **DistGraph** — automatic dependency resolution via topological sort
- **Arithmetic expressions** — `"60 + 30 * uniform(0, 1)"` with `sin`, `cos`, `exp`, `sqrt`, `pi` and more
- **Seed management** — global `seed()`, context manager `seed_context()`, per-instance `DistGraph(seed=...)`
- **Bounds clipping** — clamp sampled values with `min`/`max` or `lbound`/`rbound`
- **Extensible registry** — register custom distributions at runtime

## Docs

Full documentation at [distparser.readthedocs.io](https://distparser.readthedocs.io).

## Development

See [AGENTS.md](https://github.com/njuyoung35/distparser/blob/main/AGENTS.md) for setup and guidelines.

## License

MIT
