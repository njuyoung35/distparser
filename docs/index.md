# distparser

**Parse function-call strings into frozen `scipy.stats` distributions —**
**with dependency resolution, arithmetic expressions, and seed management.**

```python
from distparser import DistGraph

config = {"mean": 5.0, "noise": "norm(0, 0.1)", "measurement": "mean + noise"}
graph = DistGraph(config, seed=42)
result = graph.resolve_all()
print(result["measurement"])  # 5.0 + sample from N(0, 0.1)
```

## Features

- **String → Distribution**: `"gamma(2, scale=1.5)"` → ready-to-sample object
- **DistGraph**: dependency-aware evaluation with automatic topological sort
- **Arithmetic expressions**: `"60 + 30 * uniform(0,1)"` with `sin`, `cos`, `sqrt`, `pi`
- **15 built-in distributions**: full scipy.stats coverage
- **Distribution aliases**: `normal` → `norm`, `unif` → `uniform`
- **Seed management**: global, context-manager, and per-instance RNG control
- **Bounds metadata**: annotate parameters with `(min, max)` constraints
- **Extensible**: register custom distributions at runtime

## Quick Start

```bash
pip install distparser
```

```python
import distparser as lib

# Single distribution
d = lib.parse_dist("gamma(2, scale=1.5)")
print(d.rvs(size=3, random_state=42))

# DistGraph with dependencies
graph = lib.DistGraph({"a": 10, "b": "a + 5", "c": "b * 2"})
print(graph.resolve_all())  # {'a': 10, 'b': 15, 'c': 30}
```

## License

MIT
