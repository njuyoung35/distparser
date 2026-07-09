"""
distparser demo — parse distribution strings and visualize PDFs.

Usage:  python examples/demo.py
"""

import numpy as np
import matplotlib.pyplot as plt
import distparser as lib

# ── Parse distributions from strings ──────────────────────────────────
dists = {
    "uniform(0, 1)":         lib.parse_dist("uniform(0, 1)"),
    "norm(loc=0, scale=1)":  lib.parse_dist("norm(loc=0, scale=1)"),
    "expon(scale=1.5)":      lib.parse_dist("expon(scale=1.5)"),
    "gamma(2, scale=1.5)":   lib.parse_dist("gamma(2, scale=1.5)"),
    "beta(2, 5)":            lib.parse_dist("beta(2, 5)"),
    "lognorm(0.5, scale=2)": lib.parse_dist("lognorm(0.5, scale=2)"),
    "weibull_min(1.5)":      lib.parse_dist("weibull_min(1.5)"),
    "t(3)":                  lib.parse_dist("t(3)"),
    "cauchy(loc=0, scale=1)": lib.parse_dist("cauchy(loc=0, scale=1)"),
}

# ── Plot PDFs ─────────────────────────────────────────────────────────
x = np.linspace(-4, 8, 500)
fig, axes = plt.subplots(3, 3, figsize=(12, 10))
axes = axes.flatten()

for ax, (label, dist) in zip(axes, dists.items()):
    ax.plot(x, dist.pdf(x), linewidth=2, color="steelblue")
    ax.fill_between(x, dist.pdf(x), alpha=0.15, color="steelblue")
    ax.set_title(label, fontsize=12, fontfamily="monospace")
    ax.set_xlim(-4, 8)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)

fig.suptitle("distparser — frozen scipy.stats distributions from strings",
             fontsize=13, fontweight="bold", y=1.01)
fig.tight_layout()

# ── Show version & registry ───────────────────────────────────────────
print(f"distparser v{lib.__version__}")
print(f"Built-in distributions: {', '.join(sorted(lib.REGISTRY))}")
print()

# ── Demonstrate repr-like output ──────────────────────────────────────
for label, dist in dists.items():
    print(f"  parse_dist({label!r})")
    print(f"    → rvs(size=3) = {dist.rvs(size=3, random_state=42)}")
    print(f"    → mean()       = {dist.mean():.4f}")
    print()

# ── Save plot ─────────────────────────────────────────────────────────
out = "examples/demo.png"
fig.savefig(out, dpi=120, bbox_inches="tight")
print(f"Plot saved to {out}")

