"""Distribution name aliases and canonicalization."""

from __future__ import annotations

DISTRIBUTION_ALIASES: dict[str, str] = {
    "normal": "norm",
    "gaussian": "norm",
    "unif": "uniform",
}


def normalize_dist_name(name: str) -> str:
    """Return the canonical distribution name for *name*.

    If *name* is a known alias, the canonical name is returned.
    Otherwise *name* is returned unchanged.
    """
    return DISTRIBUTION_ALIASES.get(name, name)
