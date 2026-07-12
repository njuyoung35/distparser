"""Tests for distparser.core."""

import pytest
from scipy.stats import expon, norm, uniform

from distparser.core import (
    REGISTRY,
    DistParserError,
    ParseError,
    UnknownDistributionError,
    parse_dist,
    register_distribution,
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_builtin_entries(self):
        assert "uniform" in REGISTRY
        assert "norm" in REGISTRY
        assert "expon" in REGISTRY

    def test_builtin_classes(self):
        assert REGISTRY["uniform"]["class"] is uniform
        assert REGISTRY["norm"]["class"] is norm
        assert REGISTRY["expon"]["class"] is expon

    def test_builtin_param_orders(self):
        assert REGISTRY["uniform"]["param_order"] == ["loc", "scale"]
        assert REGISTRY["norm"]["param_order"] == ["loc", "scale"]
        assert REGISTRY["expon"]["param_order"] == ["loc", "scale"]


class TestRegisterDistribution:
    def test_adds_to_registry(self):
        register_distribution("_test", uniform, ["loc", "scale"])
        assert "_test" in REGISTRY
        assert REGISTRY["_test"]["class"] is uniform
        assert REGISTRY["_test"]["param_order"] == ["loc", "scale"]

    def test_custom_distribution_is_usable(self):
        from scipy.stats import gamma

        register_distribution("_gamma_test", gamma, ["a", "loc", "scale"])
        d = parse_dist("_gamma_test(2.0, loc=0, scale=1.5)")
        assert abs(d.kwds["a"] - 2.0) < 1e-12
        assert abs(d.kwds["scale"] - 1.5) < 1e-12


# ---------------------------------------------------------------------------
# parse_dist – success cases
# ---------------------------------------------------------------------------


class TestParseDistPositional:
    def test_all_positional(self):
        d = parse_dist("uniform(0, 1)")
        assert abs(d.kwds["loc"] - 0.0) < 1e-12
        assert abs(d.kwds["scale"] - 1.0) < 1e-12

    def test_partial_positional(self):
        d = parse_dist("uniform(5)")
        # Only explicitly passed args appear in kwds
        assert abs(d.kwds["loc"] - 5.0) < 1e-12
        # scale is not in kwds; verify default (1.0) via std
        assert abs(d.std() - 1.0 / (12**0.5)) < 1e-12


class TestParseDistKeyword:
    def test_all_keyword(self):
        d = parse_dist("norm(loc=0, scale=2)")
        assert abs(d.kwds["loc"] - 0.0) < 1e-12
        assert abs(d.kwds["scale"] - 2.0) < 1e-12

    def test_keyword_order_independent(self):
        d = parse_dist("norm(scale=3, loc=10)")
        assert abs(d.kwds["loc"] - 10.0) < 1e-12
        assert abs(d.kwds["scale"] - 3.0) < 1e-12


class TestParseDistMixed:
    def test_keyword_overrides_positional(self):
        d = parse_dist("uniform(0, loc=5)")
        assert abs(d.kwds["loc"] - 5.0) < 1e-12

    def test_partial_positional_plus_keyword(self):
        d = parse_dist("expon(0.5, scale=3)")
        assert abs(d.kwds["loc"] - 0.5) < 1e-12
        assert abs(d.kwds["scale"] - 3.0) < 1e-12


class TestParseDistDefaults:
    def test_no_args_uses_defaults(self):
        d = parse_dist("uniform()")
        # No explicitly passed args => kwds is empty; verify via stats
        assert d.kwds == {}
        # uniform(0, 1): mean = (0+1)/2 = 0.5, std = 1/sqrt(12)
        assert abs(d.mean() - 0.5) < 1e-12
        assert abs(d.std() - 1.0 / (12**0.5)) < 1e-12

    def test_whitespace_handling(self):
        d = parse_dist("  norm ( loc = 0 , scale = 1 )  ")
        assert abs(d.kwds["loc"] - 0.0) < 1e-12
        assert abs(d.kwds["scale"] - 1.0) < 1e-12


class TestParseDistCommaInQuotes:
    def test_string_arg_with_comma(self):
        d = parse_dist("uniform(0, '1,2,3')")
        assert abs(d.kwds["loc"] - 0.0) < 1e-12

    def test_keyword_string_with_comma(self):
        d = parse_dist('uniform(loc="a,b", scale=5)')
        assert d.kwds["loc"] == "a,b"
        assert abs(d.kwds["scale"] - 5.0) < 1e-12


class TestParseDistReturnsFrozenDistribution:
    def test_rvs_returns_array(self):
        import numpy as np

        d = parse_dist("norm(loc=0, scale=1)")
        samples = d.rvs(size=10, random_state=42)
        assert isinstance(samples, np.ndarray)
        assert len(samples) == 10

    def test_reproducible_with_seed(self):
        d = parse_dist("norm(loc=0, scale=1)")
        s1 = d.rvs(size=5, random_state=42)
        s2 = d.rvs(size=5, random_state=42)
        import numpy as np

        assert np.array_equal(s1, s2)


class TestParseDistNewDistributions:
    """Smoke tests: parse + rvs for each newly added distribution."""

    def test_gamma(self):
        d = parse_dist("gamma(2.0, loc=0, scale=1.5)")
        assert abs(d.kwds["a"] - 2.0) < 1e-12
        assert d.rvs(size=3, random_state=42).shape == (3,)

    def test_beta(self):
        d = parse_dist("beta(2, 5, loc=0, scale=1)")
        assert d.rvs(size=3, random_state=42).shape == (3,)

    def test_lognorm(self):
        d = parse_dist("lognorm(0.5, loc=0, scale=2)")
        assert abs(d.kwds["s"] - 0.5) < 1e-12

    def test_weibull_min(self):
        d = parse_dist("weibull_min(1.5, loc=0, scale=1)")
        assert abs(d.kwds["c"] - 1.5) < 1e-12

    def test_t(self):
        d = parse_dist("t(10, loc=0, scale=1)")
        assert abs(d.kwds["df"] - 10.0) < 1e-12

    def test_chi2(self):
        d = parse_dist("chi2(5, loc=0, scale=1)")
        assert abs(d.kwds["df"] - 5.0) < 1e-12

    def test_f(self):
        d = parse_dist("f(4, 10, loc=0, scale=1)")
        assert abs(d.kwds["dfn"] - 4.0) < 1e-12
        assert abs(d.kwds["dfd"] - 10.0) < 1e-12

    def test_pareto(self):
        d = parse_dist("pareto(3, loc=0, scale=1)")
        assert abs(d.kwds["b"] - 3.0) < 1e-12

    def test_cauchy(self):
        d = parse_dist("cauchy(loc=0, scale=1)")
        assert d.rvs(size=3, random_state=42).shape == (3,)

    def test_laplace(self):
        d = parse_dist("laplace(loc=0, scale=2)")
        assert abs(d.kwds["scale"] - 2.0) < 1e-12

    def test_logistic(self):
        d = parse_dist("logistic(loc=1, scale=3)")
        assert abs(d.kwds["loc"] - 1.0) < 1e-12

    def test_rayleigh(self):
        d = parse_dist("rayleigh(loc=0, scale=1)")
        assert d.rvs(size=3, random_state=42).shape == (3,)


class TestParseDistAliases:
    """Verify that distribution aliases are resolved."""

    def test_normal_alias(self):
        d = parse_dist("normal(loc=0, scale=1)")
        assert abs(d.kwds["loc"] - 0.0) < 1e-12

    def test_gaussian_alias(self):
        d = parse_dist("gaussian(loc=5, scale=2)")
        assert abs(d.kwds["loc"] - 5.0) < 1e-12

    def test_unif_alias(self):
        d = parse_dist("unif(0, 1)")
        assert abs(d.kwds["loc"] - 0.0) < 1e-12

    def test_unknown_distribution_with_alias_message(self):
        # Even with normalize, unknown names still raise UnknownDistributionError
        from distparser.core import UnknownDistributionError

        with pytest.raises(UnknownDistributionError):
            parse_dist("not_an_alias(0, 1)")


# ---------------------------------------------------------------------------
# parse_dist – error cases
# ---------------------------------------------------------------------------


class TestParseDistErrors:
    def test_empty_string(self):
        with pytest.raises(ParseError, match="Cannot parse"):
            parse_dist("")

    def test_no_parens(self):
        with pytest.raises(ParseError, match="Cannot parse"):
            parse_dist("norm")

    def test_only_name_and_parens_missing(self):
        with pytest.raises(ParseError):
            parse_dist("123(0, 1)")

    def test_unknown_distribution(self):
        with pytest.raises(UnknownDistributionError, match="xyzzy"):
            parse_dist("xyzzy(0, 1)")

    def test_unknown_dist_suggests_registered(self):
        with pytest.raises(UnknownDistributionError, match="Registered"):
            parse_dist("foobar(0)")

    def test_too_many_positional(self):
        with pytest.raises(ParseError, match="Too many positional"):
            parse_dist("uniform(0, 1, 2, 3)")

    def test_unclosed_quote(self):
        with pytest.raises((ParseError, SyntaxError)):
            parse_dist("uniform(0, 'hello)")

    def test_garbage_input(self):
        with pytest.raises(ParseError):
            parse_dist("!!not valid!!")


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    def test_parse_error_is_distparser_error(self):
        assert issubclass(ParseError, DistParserError)

    def test_unknown_distribution_is_distparser_error(self):
        assert issubclass(UnknownDistributionError, DistParserError)
