"""distparser – parse function-call strings into frozen scipy.stats distributions."""

from distparser.core import (
    REGISTRY,
    DistParserError,
    ParseError,
    UnknownDistributionError,
    parse_dist,
    register_distribution,
)
from distparser.graph import DistGraph, seed, seed_context
from distparser.mapping import DISTRIBUTION_ALIASES, normalize_dist_name
from distparser.version import __version__

__all__ = [
    "__version__",
    "DistParserError",
    "ParseError",
    "UnknownDistributionError",
    "REGISTRY",
    "DISTRIBUTION_ALIASES",
    "normalize_dist_name",
    "parse_dist",
    "register_distribution",
    "DistGraph",
    "seed",
    "seed_context",
]
