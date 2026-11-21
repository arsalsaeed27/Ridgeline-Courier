"""Shared map drawings (instance map + elevation map), used by run_all.py and
scripts/make_elevation.py so the code exists only once. Saved via oel.stamp.save_fig."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # draw to files only, no window needed
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from oel.stamp import save_fig

TERRAIN_COLOURS = ["#555555", "#d9d9d9", "#9ccc65", "#a1887f", "#4fc3f7"]  # blocked, road, grass, mud, ford
TUNNEL_COLOURS = ["#e91e63", "#ff9800", "#9c27b0"]


def _overlay(ax, cfg):
    """Draw depot, stops, stations and tunnels on top of a map (x = col, y = row)."""
    sr, sc = cfg.start
    ax.plot(sc, sr, marker="s", ms=10, color="black", mec="white", label="depot (recharges)")
    for i, (r, c) in enumerate(cfg.stops):
        ax.plot(c, r, marker="*", ms=14, color="gold", mec="black")
        ax.text(c + 0.6, r - 0.6, str(i), fontsize=9, weight="bold", color="black")
    ax.plot([], [], marker="*", ls="", ms=12, color="gold", mec="black", label="delivery stop (index)")
    if cfg.use_fuel:
        for r, c in cfg.stations:
            ax.plot(c, r, marker="P", ms=10, color="#00c853", mec="black")
        ax.plot([], [], marker="P", ls="", ms=10, color="#00c853", mec="black", label="charging station")
    if cfg.use_tunnels:
        for k, ((r1, c1), (r2, c2)) in enumerate(cfg.tunnels):
            col = TUNNEL_COLOURS[k % len(TUNNEL_COLOURS)]
            ax.plot([c1, c2], [r1, r2], ls="--", lw=1.2, color=col, alpha=0.8)
            ax.plot([c1, c2], [r1, r2], ls="", marker="o", ms=8, color=col, mec="black",
                    label=f"tunnel {k}")
    ax.set_xlabel("column")
    ax.set_ylabel("row")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8)


def plot_instance_map(cfg, name="instance_map"):
    """Terrain colours + overlays. Returns the saved path."""
    fig, ax = plt.subplots(figsize=(9, 7.5))
    shown = cfg.grid + 1  # -1..3 -> 0..4 so it indexes the colour list
    ax.imshow(shown, cmap=ListedColormap(TERRAIN_COLOURS), vmin=0, vmax=4, origin="upper")
    for i, t in enumerate(["blocked"] + [f"{t} (cost {cfg.terrain_cost[t]})" for t in
                                         ["road", "grass", "mud", "ford"]]):
        ax.plot([], [], marker="s", ls="", ms=10, color=TERRAIN_COLOURS[i], label=t)
    _overlay(ax, cfg)
    ax.set_title(f"Instance map {cfg.n}x{cfg.n}")
    path = save_fig(fig, name)
    plt.close(fig)
    return path


def plot_elevation_map(cfg, name="elevation_map"):
    """Heights 0..9 as a colour map; blocked cells drawn grey on top."""
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(cfg.elevation, cmap="terrain", vmin=0, vmax=9, origin="upper")
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.25, label="height (0-9)")
    blocked = np.ma.masked_where(cfg.grid != -1, np.ones_like(cfg.grid))
    ax.imshow(blocked, cmap=ListedColormap(["#555555"]), alpha=0.75, origin="upper")
    ax.plot([], [], marker="s", ls="", ms=10, color="#555555", label="blocked")
    _overlay(ax, cfg)
    ax.set_title("Elevation (twist 3: hills with regenerative braking)")
    path = save_fig(fig, name)
    plt.close(fig)
    return path
