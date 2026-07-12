# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-09
### Added
- 12 new built-in distributions: `gamma`, `beta`, `lognorm`, `weibull_min`, `t`, `chi2`, `f`, `pareto`, `cauchy`, `laplace`, `logistic`, `rayleigh`.

## [Unreleased]
### Added
- `DistGraph` class with automatic dependency resolution via topological sort.
- Arithmetic expression evaluation via `asteval` (e.g. `"60 + 30 * uniform(0,1)"`).
- Distribution name aliases (`normal` → `norm`, `gaussian` → `norm`, `unif` → `uniform`).
- Seed management: global `seed()`, `seed_context()`, and per-instance `DistGraph(..., seed=...)`.
- Bounds constraints on distribution parameters via dict config format.

## [0.1.0] - 2026-07-09
### Added
- Initial release with built-in `uniform`, `norm`, and `expon` distributions.
- `parse_dist()` function for parsing function-call strings into frozen distributions.
- `register_distribution()` function for extending the built-in registry.
- Custom exception hierarchy: `DistParserError`, `ParseError`, `UnknownDistributionError`.
