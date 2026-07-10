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
