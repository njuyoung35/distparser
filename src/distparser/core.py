"""Core parsing logic and distribution registry."""

from __future__ import annotations

import ast
import re
from typing import Any

from scipy.stats import (
    beta,
    cauchy,
    chi2,
    expon,
    f,
    gamma,
    laplace,
    logistic,
    lognorm,
    norm,
    pareto,
    rayleigh,
    t,
    uniform,
    weibull_min,
)

from distparser.mapping import normalize_dist_name

__all__ = [
    "DistParserError",
    "ParseError",
    "UnknownDistributionError",
    "REGISTRY",
    "parse_dist",
    "register_distribution",
]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class DistParserError(Exception):
    """Base exception for all distparser errors."""


class ParseError(DistParserError):
    """Raised when a distribution string cannot be parsed."""


class UnknownDistributionError(DistParserError):
    """Raised when a distribution name is not in the registry."""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

REGISTRY: dict[str, dict[str, Any]] = {
    # Shape-parameter distributions (alphabetical)
    "beta": {"class": beta, "param_order": ["a", "b", "loc", "scale"]},
    "chi2": {"class": chi2, "param_order": ["df", "loc", "scale"]},
    "f": {"class": f, "param_order": ["dfn", "dfd", "loc", "scale"]},
    "gamma": {"class": gamma, "param_order": ["a", "loc", "scale"]},
    "lognorm": {"class": lognorm, "param_order": ["s", "loc", "scale"]},
    "pareto": {"class": pareto, "param_order": ["b", "loc", "scale"]},
    "t": {"class": t, "param_order": ["df", "loc", "scale"]},
    "weibull_min": {"class": weibull_min, "param_order": ["c", "loc", "scale"]},
    # Loc/scale-only distributions (alphabetical)
    "cauchy": {"class": cauchy, "param_order": ["loc", "scale"]},
    "expon": {"class": expon, "param_order": ["loc", "scale"]},
    "laplace": {"class": laplace, "param_order": ["loc", "scale"]},
    "logistic": {"class": logistic, "param_order": ["loc", "scale"]},
    "norm": {"class": norm, "param_order": ["loc", "scale"]},
    "rayleigh": {"class": rayleigh, "param_order": ["loc", "scale"]},
    "uniform": {"class": uniform, "param_order": ["loc", "scale"]},
}


def register_distribution(
    name: str,
    dist_class: Any,
    param_order: list[str],
) -> None:
    """Register a new distribution in the global registry.

    Args:
        name: Name used in parse strings (e.g. ``"gumbel"``).
        dist_class: A scipy.stats distribution class.
        param_order: Ordered list of parameter names for positional arguments.
    """
    REGISTRY[name] = {"class": dist_class, "param_order": list(param_order)}


# ---------------------------------------------------------------------------
# Argument splitting (comma-aware, quote-safe)
# ---------------------------------------------------------------------------


def _split_args(args_str: str) -> list[str]:
    """Split *args_str* on commas, respecting single- and double-quoted regions.

    Empty parts are filtered out so that ``"norm()"`` yields ``[]``.
    """
    parts: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False

    for ch in args_str:
        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
        elif ch == "," and not in_single and not in_double:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)

    parts.append("".join(current).strip())
    return [p for p in parts if p]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)$")


def parse_dist(s: str) -> Any:
    """Parse a function-call string into a frozen ``scipy.stats`` distribution.

    Args:
        s: A string like ``"norm(loc=0, scale=1)"`` or ``"uniform(0, 1)"``.

    Returns:
        A frozen scipy.stats distribution object (callable for ``.rvs()``).

    Raises:
        ParseError: If the string cannot be parsed.
        UnknownDistributionError: If the distribution name is not registered.

    Examples:
        >>> from distparser import parse_dist
        >>> d = parse_dist("norm(loc=0, scale=1)")
        >>> d.rvs(size=3)  # doctest: +SKIP
        array([...])
    """
    s = s.strip()
    m = _NAME_RE.match(s)
    if not m:
        raise ParseError(f"Cannot parse {s!r}. Expected format: 'name(args)'.")

    name = normalize_dist_name(m.group(1))
    if name not in REGISTRY:
        raise UnknownDistributionError(
            f"Unknown distribution {name!r}. Registered: {', '.join(sorted(REGISTRY))}."
        )

    entry = REGISTRY[name]
    dist_class = entry["class"]
    param_order: list[str] = entry["param_order"]

    raw_args = _split_args(m.group(2))

    # Separate positional values from keyword assignments
    positional: list[Any] = []
    keyword: dict[str, Any] = {}

    for arg in raw_args:
        arg = arg.strip()
        if "=" in arg:
            key, val_str = arg.split("=", 1)
            key = key.strip()
            val_str = val_str.strip()
            keyword[key] = _eval_arg(val_str, s)
        else:
            positional.append(_eval_arg(arg, s))

    # Build final parameter dict: positional first, keywords override
    params: dict[str, Any] = {}
    for i, value in enumerate(positional):
        if i >= len(param_order):
            raise ParseError(
                f"Too many positional arguments in {s!r}. "
                f"{name!r} accepts at most {len(param_order)} "
                f"positional args: {', '.join(param_order)}."
            )
        params[param_order[i]] = value

    params.update(keyword)

    return dist_class(**params)


def _eval_arg(raw: str, full_str: str) -> Any:
    """Evaluate a single argument value via ``ast.literal_eval``, with a
    helpful error message on failure."""
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError) as exc:
        raise ParseError(f"Cannot evaluate {raw!r} in {full_str!r}: {exc}") from exc
