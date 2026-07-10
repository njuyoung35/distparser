# API Reference

## `parse_dist(s: str) -> rv_frozen`

Parse a function-call string into a frozen `scipy.stats` distribution.

**Args:**
- `s` — A string like `"norm(loc=0, scale=1)"` or `"uniform(0, 1)"`.

**Returns:**
- A frozen scipy.stats distribution object. Call `.rvs()`, `.pdf()`, `.cdf()`, `.mean()`, etc. on it.

**Raises:**
- `ParseError` — If the string cannot be parsed.
- `UnknownDistributionError` — If the distribution name is not in the registry.

**Examples:**

```python
>>> from distparser import parse_dist
>>> d = parse_dist("norm(loc=0, scale=1)")
>>> d.mean()
0.0
>>> d.rvs(size=3, random_state=42)
array([ 0.49671415, -0.1382643 ,  0.64768854])
```

---

## `register_distribution(name, dist_class, param_order)`

Register a new distribution in the global registry.

**Args:**
- `name` (`str`) — Name used in parse strings (e.g. `"gumbel"`).
- `dist_class` — A scipy.stats distribution class (e.g. `scipy.stats.gumbel_r`).
- `param_order` (`list[str]`) — Ordered list of parameter names for positional arguments.

**Example:**

```python
>>> from distparser import register_distribution
>>> from scipy.stats import gumbel_r
>>> register_distribution("gumbel", gumbel_r, ["loc", "scale"])
```

---

## `REGISTRY`

`dict[str, dict]` — The global distribution registry.

Each entry maps a distribution name to:
- `"class"` — The scipy.stats distribution class.
- `"param_order"` — `list[str]` of parameter names.

```python
>>> from distparser import REGISTRY
>>> sorted(REGISTRY)
['beta', 'cauchy', 'chi2', 'expon', 'f', 'gamma', 'laplace', 'logistic',
 'lognorm', 'norm', 'pareto', 'rayleigh', 't', 'uniform', 'weibull_min']
```

---

## Exceptions

### `DistParserError`

Base exception for all distparser errors. Inherits from `Exception`.

### `ParseError`

Raised when a distribution string cannot be parsed (malformed syntax, too many positional args, un-evaluable values).

### `UnknownDistributionError`

Raised when a distribution name is not found in `REGISTRY`. The error message lists all registered names.
