"""Tests for distparser.mapping."""

from distparser.mapping import DISTRIBUTION_ALIASES, normalize_dist_name


class TestNormalizeDistName:
    def test_known_alias(self):
        assert normalize_dist_name("normal") == "norm"
        assert normalize_dist_name("gaussian") == "norm"
        assert normalize_dist_name("unif") == "uniform"

    def test_unknown_name_passthrough(self):
        assert normalize_dist_name("norm") == "norm"
        assert normalize_dist_name("gamma") == "gamma"
        assert normalize_dist_name("custom_dist") == "custom_dist"

    def test_case_sensitive(self):
        assert normalize_dist_name("Normal") == "Normal"
        assert normalize_dist_name("NORM") == "NORM"


class TestAliasMap:
    def test_contains_expected_aliases(self):
        assert DISTRIBUTION_ALIASES["normal"] == "norm"
        assert DISTRIBUTION_ALIASES["gaussian"] == "norm"
        assert DISTRIBUTION_ALIASES["unif"] == "uniform"
