# User Guide

## Basic Usage

Import `parse_dist` and pass a distribution string:

```python
from distparser import parse_dist

# All keyword arguments
dist = parse_dist("norm(loc=0, scale=1)")

# All positional (matched to param_order)
dist = parse_dist("uniform(0, 1)")

# Mixed — keyword overrides positional
dist = parse_dist("uniform(0, loc=5)")  # loc=5 wins

# No arguments — uses scipy defaults
dist = parse_dist("expon()")
```

The returned object is a frozen `scipy.stats` distribution. You can call `.rvs()`, `.pdf()`, `.cdf()`, `.mean()`, `.std()`, and all other standard methods.

## Supported Distributions

| Name | `param_order` |
|---|---|
| `uniform` | `loc`, `scale` |
| `norm` | `loc`, `scale` |
| `expon` | `loc`, `scale` |
| `gamma` | `a`, `loc`, `scale` |
| `beta` | `a`, `b`, `loc`, `scale` |
| `lognorm` | `s`, `loc`, `scale` |
| `weibull_min` | `c`, `loc`, `scale` |
| `t` | `df`, `loc`, `scale` |
| `chi2` | `df`, `loc`, `scale` |
| `f` | `dfn`, `dfd`, `loc`, `scale` |
| `pareto` | `b`, `loc`, `scale` |
| `cauchy` | `loc`, `scale` |
| `laplace` | `loc`, `scale` |
| `logistic` | `loc`, `scale` |
| `rayleigh` | `loc`, `scale` |

Use `parse_dist("name(args)")` — positional args fill `param_order` left-to-right; keyword args match by name.

## Extending the Registry

Register custom distributions at runtime:

```python
from distparser import register_distribution, parse_dist
from scipy.stats import gumbel_r

register_distribution("gumbel", gumbel_r, ["loc", "scale"])
dist = parse_dist("gumbel(loc=10, scale=3)")
```

## Error Handling

All exceptions inherit from `DistParserError`:

```python
from distparser import parse_dist, ParseError, UnknownDistributionError

try:
    dist = parse_dist("typo(0, 1)")
except UnknownDistributionError as e:
    print(f"Unknown: {e}")  # Unknown: 'typo'. Registered: beta, cauchy, ...

try:
    dist = parse_dist("not valid")
except ParseError as e:
    print(f"Parse: {e}")    # Parse: Cannot parse 'not valid'. Expected format: 'name(args)'.
```

## DistGraph — dependency-aware evaluation

`DistGraph` accepts a flat dictionary of keys and expressions. It automatically
detects cross‑references, resolves evaluation order via topological sort, and
injects resolved values into subsequent expressions.

```python
from distparser import DistGraph

config = {
    "offset": 10,
    "scale": "uniform(1, 3)",
    "point": "offset + scale * norm(0, 1)",
}

graph = DistGraph(config, seed=42)
result = graph.resolve_all()
print(result["point"])
```

Non‑string values (numbers, lists) pass through unchanged. Circular
dependencies raise a `ParseError`.

## Distribution Aliases

Common shorthands are built in:

| Alias | Canonical |
|---|---|
| `normal` | `norm` |
| `gaussian` | `norm` |
| `unif` | `uniform` |

```python
from distparser import parse_dist

d = parse_dist("normal(loc=0, scale=1)")  # resolves to norm
```

## Seed Management

Three levels of RNG control:

```python
from distparser import seed, seed_context, DistGraph

# Global seed
seed(42)

# Context manager (temporary override)
with seed_context(99):
    g = DistGraph({"x": "uniform(0, 1)"})

# Per-instance seed (highest priority)
g = DistGraph({"x": "uniform(0, 1)"}, seed=123)
```

Priority: per‑instance > context manager > global.

## Bounds Constraints

Specify output bounds directly in the expression string using `min`/`max` or
`lbound`/`rbound` keyword arguments.  The sampled value is automatically
clipped to the given range.

```python
from distparser import DistGraph

config = {
    "wall_thickness": "norm(loc=0.25, scale=0.025, min=0.0, max=1.0)",
}

graph = DistGraph(config, seed=42)
result = graph.resolve_all()
print(result["wall_thickness"])  # clipped to [0.0, 1.0]

bounds = graph.get_bounds("wall_thickness")
print(bounds)  # {"min": 0.0, "max": 1.0}
```

Bounds are applied as a final clip after sampling.
