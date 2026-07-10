# distparser

**Parse function-call strings into frozen `scipy.stats` distributions.**

```python
from distparser import parse_dist

dist = parse_dist("norm(loc=0, scale=1)")
samples = dist.rvs(size=1000)  # numpy array
```

## Features

- **String → Distribution**: Turn `"gamma(2, scale=1.5)"` into a ready-to-sample object.
- **15 built-in distributions**: `uniform`, `norm`, `expon`, `gamma`, `beta`, `lognorm`, `weibull_min`, `t`, `chi2`, `f`, `pareto`, `cauchy`, `laplace`, `logistic`, `rayleigh`.
- **Extensible**: Register your own distributions at runtime.
- **Positional & keyword args**: `"uniform(0, 1)"` or `"norm(loc=0, scale=1)"` — both work.

## Quick Start

```bash
pip install distparser
```

```python
import distparser as lib

# Positional arguments (matched to param_order)
d = lib.parse_dist("uniform(0, 1)")
print(d.mean())   # 0.5

# Keyword arguments
d = lib.parse_dist("gamma(2, scale=1.5)")
print(d.rvs(size=3, random_state=42))  # [3.59 2.24 2.07]

# Extend the registry
from scipy.stats import gumbel_r
lib.register_distribution("gumbel", gumbel_r, ["loc", "scale"])
d = lib.parse_dist("gumbel(loc=0, scale=2)")
```

## License

MIT
