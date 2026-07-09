"""distparser – parse function-call strings into frozen scipy.stats distributions."""

from distparser.core import (
    REGISTRY,
    DistParserError,
    ParseError,
    UnknownDistributionError,
    parse_dist,
    register_distribution,
)
from distparser.version import __version__

__all__ = [
    "__version__",
    "DistParserError",
    "ParseError",
    "UnknownDistributionError",
    "REGISTRY",
    "parse_dist",
    "register_distribution",
]
