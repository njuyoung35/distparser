"""Tests for distparser.graph (DistGraph + seed management)."""

import numpy as np
import pytest

from distparser.core import ParseError
from distparser.graph import DistGraph, seed, seed_context

# ---------------------------------------------------------------------------
# Simple configs — no dependencies
# ---------------------------------------------------------------------------


class TestDistGraphSimple:
    def test_single_distribution(self):
        g = DistGraph({"x": "uniform(0, 1)"})
        result = g.resolve_all()
        assert "x" in result
        assert 0 <= result["x"] <= 1

    def test_numeric_value_passthrough(self):
        g = DistGraph({"a": 42, "b": 3.14})
        result = g.resolve_all()
        assert result["a"] == 42
        assert result["b"] == 3.14

    def test_empty_config(self):
        g = DistGraph({})
        result = g.resolve_all()
        assert result == {}

    def test_arithmetic_expression_no_deps(self):
        g = DistGraph({"x": "60 + 30 * uniform(0, 1)"})
        result = g.resolve_all()
        assert 60 <= result["x"] <= 90


# ---------------------------------------------------------------------------
# Dependencies — cross-references between keys
# ---------------------------------------------------------------------------


class TestDistGraphDependencies:
    def test_linear_chain(self):
        g = DistGraph({"a": 10, "b": "a + 5", "c": "b * 2"})
        result = g.resolve_all()
        assert result["a"] == 10
        assert result["b"] == 15
        assert result["c"] == 30

    def test_topological_order(self):
        g = DistGraph({"a": 1, "b": "a + 1", "c": "a + b"})
        result = g.resolve_all()
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["c"] == 3
        # 'a' must come before 'b' and 'c'
        order = g.order
        assert order.index("a") < order.index("b")
        assert order.index("a") < order.index("c")

    def test_distribution_with_dependency(self):
        g = DistGraph({"mean": 5.0, "x": "norm(mean, 0.1)"}, seed=42)
        result = g.resolve_all()
        assert result["mean"] == 5.0
        assert abs(result["x"] - 5.0) < 1.0  # should be near mean

    def test_separate_sampling_per_evaluation(self):
        g = DistGraph({"a": "uniform(0, 1)", "b": "uniform(0, 1)"}, seed=42)
        result = g.resolve_all()
        # With same seed but separate calls, patterns should differ
        assert result["a"] != result["b"]


# ---------------------------------------------------------------------------
# Circular dependencies
# ---------------------------------------------------------------------------


class TestDistGraphCycles:
    def test_direct_cycle_detected(self):
        with pytest.raises(ParseError, match="Circular"):
            DistGraph({"a": "b + 1", "b": "a + 1"})

    def test_indirect_cycle_detected(self):
        with pytest.raises(ParseError, match="Circular"):
            DistGraph({"a": "b", "b": "c", "c": "a"})


# ---------------------------------------------------------------------------
# __getitem__ access
# ---------------------------------------------------------------------------


class TestDistGraphGetItem:
    def test_lazy_resolution(self):
        g = DistGraph({"a": 1, "b": "a + 2"})
        assert g["a"] == 1
        assert g["b"] == 3

    def test_missing_key(self):
        g = DistGraph({"a": 1})
        with pytest.raises(KeyError):
            _ = g["nonexistent"]

    def test_contains_and_len(self):
        g = DistGraph({"a": 1, "b": "a + 2"})
        assert "a" in g
        assert "c" not in g
        assert len(g) == 2

    def test_iter_and_keys(self):
        g = DistGraph({"a": 1, "b": 2})
        assert set(g) == {"a", "b"}
        assert set(g.keys()) == {"a", "b"}


# ---------------------------------------------------------------------------
# Seed management
# ---------------------------------------------------------------------------


class TestSeedManagement:
    def test_global_seed_reproducible(self):
        seed(42)
        g1 = DistGraph({"x": "uniform(0, 1)"})
        v1 = g1.resolve_all()["x"]

        seed(42)
        g2 = DistGraph({"x": "uniform(0, 1)"})
        v2 = g2.resolve_all()["x"]

        assert v1 == v2

    def test_per_instance_seed_overrides_global(self):
        seed(99)
        g1 = DistGraph({"x": "uniform(0, 1)"}, seed=42)
        g2 = DistGraph({"x": "uniform(0, 1)"}, seed=42)
        assert g1.resolve_all()["x"] == g2.resolve_all()["x"]

    def test_seed_context_manager(self):
        seed(0)
        with seed_context(42):
            g = DistGraph({"x": "uniform(0, 1)"})
            v_ctx = g.resolve_all()["x"]

        # Outside context, back to seed(0) RNG
        g2 = DistGraph({"x": "uniform(0, 1)"})
        v_outside = g2.resolve_all()["x"]

        # Different seeds should produce different values (usually)
        assert v_ctx != v_outside


# ---------------------------------------------------------------------------
# Bounds
# ---------------------------------------------------------------------------


class TestDistGraphBounds:
    def test_bounds_dict_format(self):
        g = DistGraph(
            {
                "wall": {
                    "dist": "norm(loc=0.25, scale=0.025)",
                    "bounds": {"loc": (0.0, 1.0), "scale": (0.001, 0.1)},
                }
            }
        )
        result = g.resolve_all()
        assert abs(result["wall"] - 0.25) < 0.2

    def test_get_bounds(self):
        g = DistGraph({"x": {"dist": "uniform(0, 1)", "bounds": {"loc": (-1, 2)}}})
        bounds = g.get_bounds("x")
        assert bounds == {"loc": (-1, 2)}

    def test_get_bounds_none(self):
        g = DistGraph({"x": "uniform(0, 1)"})
        assert g.get_bounds("x") is None

    def test_missing_dist_key_raises(self):
        with pytest.raises(ParseError, match="missing required 'dist'"):
            DistGraph({"x": {"bounds": {"loc": (0, 1)}}})

    def test_bounds_not_used_for_sampling(self):
        # bounds are metadata only — sampling should still work
        g = DistGraph(
            {
                "x": {
                    "dist": "norm(loc=100, scale=0.01)",
                    "bounds": {"loc": (0.0, 1.0)},
                }
            },
            seed=42,
        )
        result = g.resolve_all()
        # Value is near loc=100, not clipped to bounds (0, 1)
        assert abs(result["x"] - 100.0) < 1.0


# ---------------------------------------------------------------------------
# Math expressions
# ---------------------------------------------------------------------------


class TestDistGraphMath:
    def test_sin_cos(self):
        g = DistGraph({"x": "sin(0)", "y": "cos(0)"})
        result = g.resolve_all()
        assert abs(result["x"]) < 1e-12
        assert abs(result["y"] - 1.0) < 1e-12

    def test_pi(self):
        g = DistGraph({"x": "pi"})
        result = g.resolve_all()
        assert abs(result["x"] - np.pi) < 1e-12

    def test_sqrt(self):
        g = DistGraph({"x": "sqrt(16)"})
        result = g.resolve_all()
        assert abs(result["x"] - 4.0) < 1e-12


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


class TestDistGraphErrors:
    def test_invalid_expression(self):
        g = DistGraph({"x": "1 / 0"})
        with pytest.raises(ParseError, match="Error evaluating"):
            g.resolve_all()

    def test_undefined_variable(self):
        g = DistGraph({"x": "unknown_func(0)"})
        with pytest.raises(ParseError, match="Error evaluating"):
            g.resolve_all()

    def test_syntax_error_expression_graceful(self):
        # Invalid Python syntax → extract returns empty set, init succeeds
        g = DistGraph({"bad": "x +", "ok": "42"})
        # 'ok' has no deps and is valid — resolves fine
        assert g["ok"] == 42
        # 'bad' has invalid syntax — evaluation raises
        with pytest.raises(ParseError, match="Error evaluating"):
            g.resolve_all()


# ---------------------------------------------------------------------------
# Repr
# ---------------------------------------------------------------------------


class TestDistGraphRepr:
    def test_repr(self):
        g = DistGraph({"a": 1, "b": "a + 2"})
        assert "DistGraph" in repr(g)
        assert "keys=2" in repr(g)
