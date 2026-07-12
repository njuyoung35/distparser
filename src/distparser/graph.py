"""DistGraph: dependency-aware distribution graph with safe expression evaluation."""

from __future__ import annotations

import ast as _ast
import contextlib
import re as _re
from typing import Any, Iterator

import graphlib
import numpy as np
from asteval import Interpreter

from distparser.core import REGISTRY, ParseError, _split_args

# ---------------------------------------------------------------------------
# Seed management
# ---------------------------------------------------------------------------

_DEFAULT_SEED: int | None = None
_DEFAULT_RNG: np.random.Generator | None = None


def seed(value: int) -> None:
    """Set the global legacy seed for distribution sampling."""
    global _DEFAULT_SEED, _DEFAULT_RNG
    _DEFAULT_SEED = value
    _DEFAULT_RNG = np.random.default_rng(value)


@contextlib.contextmanager
def seed_context(value: int) -> Iterator[None]:
    """Temporarily override the global seed within a ``with`` block.

    Example:
        >>> with seed_context(42):
        ...     graph = DistGraph({"x": "uniform(0,1)"})
        ...     graph.resolve_all()
    """
    global _DEFAULT_RNG
    old_rng = _DEFAULT_RNG
    _DEFAULT_RNG = np.random.default_rng(value)
    try:
        yield
    finally:
        _DEFAULT_RNG = old_rng


def _get_current_rng() -> np.random.Generator:
    """Return the current global RNG, creating a fresh one if unset."""
    global _DEFAULT_RNG
    if _DEFAULT_RNG is None:
        _DEFAULT_RNG = np.random.default_rng()
    return _DEFAULT_RNG


# ---------------------------------------------------------------------------
# Distribution sampler factory
# ---------------------------------------------------------------------------


_BOUND_KEYS = frozenset({"min", "max", "lbound", "rbound"})
_NAME_RE = _re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)$")
# Math constants and functions exposed in expressions
_MATH_SYMBOLS: dict[str, Any] = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": abs,
    "pi": np.pi,
    "e": np.e,
}


def _make_dist_samplers(rng: np.random.Generator) -> dict[str, Any]:
    """Build a dict mapping each registered distribution name to a callable
    sampler that returns a single ``.rvs()`` sample, clipped to bounds."""
    samplers: dict[str, Any] = {}
    for name, entry in REGISTRY.items():
        dist_class = entry["class"]
        param_order: list[str] = entry["param_order"]

        def _sampler(
            *args: Any,
            _dc: Any = dist_class,
            _po: list[str] = param_order,
            _rng: np.random.Generator = rng,
            **kwargs: Any,
        ) -> Any:
            # Separate bound kwargs from distribution kwargs
            bounds: dict[str, float] = {}
            dist_kwargs: dict[str, Any] = {}
            for k, v in kwargs.items():
                if k in _BOUND_KEYS:
                    bounds[k] = float(v)
                else:
                    dist_kwargs[k] = v

            params: dict[str, Any] = {}
            for i, val in enumerate(args):
                if i < len(_po):
                    params[_po[i]] = val
            params.update(dist_kwargs)

            value = float(_dc(**params).rvs(random_state=_rng))

            # Clip to bounds
            lb = bounds.get("min", bounds.get("lbound", -float("inf")))
            ub = bounds.get("max", bounds.get("rbound", float("inf")))
            return float(np.clip(value, lb, ub))

        samplers[name] = _sampler
    return samplers


# ---------------------------------------------------------------------------
# DistGraph
# ---------------------------------------------------------------------------


class DistGraph:
    """A dependency-aware graph of distribution expressions.

    Users supply a flat dictionary mapping keys to expressions (or numeric
    values).  ``DistGraph`` detects cross-references, resolves evaluation
    order via topological sort, and injects resolved values into subsequent
    expressions.

    Parameters
    ----------
    config : dict
        Mapping of key → expression string, numeric value, or bounds dict.
        See the user guide for the bounds dict format.
    seed : int | None
        Per-instance RNG seed.  Overrides any global seed setting.
    """

    def __init__(self, config: dict[str, Any], seed: int | None = None) -> None:
        self._raw_config = config
        self._rng = np.random.default_rng(seed) if seed is not None else None
        self._resolved: dict[str, Any] = {}
        self._bounds: dict[str, dict[str, float]] = {}

        # Parse config into dist expressions + bounds
        self._dists: dict[str, Any] = {}
        self._parse_config()

        # Build dependency graph and resolve evaluation order
        self._order = self._resolve_order()

    # ------------------------------------------------------------------
    # Config parsing
    # ------------------------------------------------------------------

    def _parse_config(self) -> None:
        for key, value in self._raw_config.items():
            if isinstance(value, str):
                self._dists[key] = value
                self._bounds[key] = self._extract_bounds(value)
            else:
                self._dists[key] = value

    # ------------------------------------------------------------------
    # Bound extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_bounds(expr: str) -> dict[str, float]:
        """Extract bound keyword args (min/max/lbound/rbound) from an expression."""
        m = _NAME_RE.match(expr.strip())
        if not m:
            return {}
        args_str = m.group(2)
        bounds: dict[str, float] = {}
        for arg in _split_args(args_str):
            arg = arg.strip()
            if "=" in arg:
                key, val_str = arg.split("=", 1)
                key = key.strip()
                if key in _BOUND_KEYS:
                    try:
                        bounds[key] = float(_ast.literal_eval(val_str.strip()))
                    except (ValueError, SyntaxError):
                        pass
        return bounds

    # ------------------------------------------------------------------
    # Dependency resolution
    # ------------------------------------------------------------------

    def _resolve_order(self) -> list[str]:
        graph: dict[str, set[str]] = {k: set() for k in self._dists}
        for key, expr in self._dists.items():
            if isinstance(expr, str):
                for var in self._extract_variables(expr):
                    if var in self._dists:
                        graph[key].add(var)
        try:
            ts = graphlib.TopologicalSorter(graph)
            return list(ts.static_order())
        except graphlib.CycleError as exc:
            raise ParseError(f"Circular dependency detected in config: {exc}") from exc

    @staticmethod
    def _extract_variables(expr: str) -> set[str]:
        """Return the set of bare-name identifiers in *expr*."""
        try:
            tree = _ast.parse(expr, mode="eval")
        except SyntaxError:
            return set()
        return {node.id for node in _ast.walk(tree) if isinstance(node, _ast.Name)}

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def _evaluate(self, key: str) -> Any:
        expr = self._dists[key]
        if not isinstance(expr, str):
            return expr

        rng = self._rng or _get_current_rng()

        interp = Interpreter()
        # Pre-populate with already-resolved dependencies
        interp.symtable.update(self._resolved)
        # Math symbols
        interp.symtable.update(_MATH_SYMBOLS)
        # Distribution samplers
        interp.symtable.update(_make_dist_samplers(rng))

        result = interp(expr)
        if interp.error:
            messages: list[str] = []
            for err in interp.error:
                messages.append(f"{err.msg} (line {err.lineno})")
            raise ParseError(
                f"Error evaluating {expr!r} for key {key!r}: " + "; ".join(messages)
            )
        return result

    def resolve_all(self) -> dict[str, Any]:
        """Evaluate all keys in dependency order and return resolved values."""
        for key in self._order:
            if key not in self._resolved:
                self._resolved[key] = self._evaluate(key)
        return dict(self._resolved)

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        """Access a resolved value, evaluating on demand if needed."""
        if key not in self._dists:
            raise KeyError(key)
        if key not in self._resolved:
            # Build the dependency graph to find what 'key' needs
            graph = self._build_dep_graph()
            self._resolve_deps(key, graph)
        return self._resolved[key]

    def _build_dep_graph(self) -> dict[str, set[str]]:
        """Build the dependency graph (key → set of keys it depends on)."""
        graph: dict[str, set[str]] = {k: set() for k in self._dists}
        for k, expr in self._dists.items():
            if isinstance(expr, str):
                for var in self._extract_variables(expr):
                    if var in self._dists:
                        graph[k].add(var)
        return graph

    def _resolve_deps(self, key: str, graph: dict[str, set[str]]) -> None:
        """Recursively resolve dependencies of *key*, then evaluate *key*."""
        if key in self._resolved:
            return
        for dep in graph.get(key, set()):
            self._resolve_deps(dep, graph)
        self._resolved[key] = self._evaluate(key)

    def __contains__(self, key: str) -> bool:
        return key in self._dists

    def __len__(self) -> int:
        return len(self._dists)

    def __iter__(self) -> Iterator[str]:
        return iter(self._dists)

    def keys(self) -> Any:
        return self._dists.keys()

    def get_bounds(self, key: str) -> dict[str, float] | None:
        """Return the bounds dict for *key*, or ``None`` if no bounds set."""
        b = self._bounds.get(key)
        return b if b else None

    @property
    def order(self) -> list[str]:
        """The topological evaluation order (read-only)."""
        return list(self._order)

    def __repr__(self) -> str:
        resolved_count = len(self._resolved)
        total = len(self._dists)
        return f"<DistGraph keys={total} resolved={resolved_count}>"
