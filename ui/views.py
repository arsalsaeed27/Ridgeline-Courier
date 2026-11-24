"""Plotly figures for the Streamlit UI (drawing only, no planning logic).

Coordinates: x = column, y = row, with the y axis reversed so row 0 is at the top, exactly like
the matplotlib figures in results/figures/.
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from oel.config import TERRAINS

TERRAIN_COLOURS = ["#555555", "#d9d9d9", "#9ccc65", "#a1887f", "#4fc3f7"]  # blocked, road, grass, mud, ford
TUNNEL_COLOURS = ["#e91e63", "#ff9800", "#9c27b0"]
ROUTE = "#d50000"
PLANNED = "#1565c0"
RIVAL = "#212121"
SERIES = "#2a78d6"
MUTED = "#52514e"


def _discrete_scale(colours):
    """Plotly colourscale with one flat band per category (so 5 codes = 5 colours)."""
    scale, k = [], len(colours)
    for i, col in enumerate(colours):
        scale += [[i / k, col], [(i + 1) / k, col]]
    return scale


def _layout(fig, cfg, height=620, title=""):
    fig.update_xaxes(range=[-0.5, cfg.n - 0.5], showgrid=False, title="column", constrain="domain")
    fig.update_yaxes(range=[cfg.n - 0.5, -0.5], showgrid=False, title="row",
                     scaleanchor="x", scaleratio=1)
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=40, b=10), title=title,
                      legend=dict(orientation="v", x=1.02, y=1, font=dict(size=11)),
                      plot_bgcolor="white")
    return fig


def base_map(cfg, layer: str = "terrain", title: str = "") -> go.Figure:
    """Terrain (or elevation) heatmap with blocked cells, plus depot/stops/stations/tunnels."""
    fig = go.Figure()
    if layer == "elevation":
        z = np.where(cfg.grid == -1, np.nan, cfg.elevation).astype(float)
        fig.add_trace(go.Heatmap(z=z, colorscale="Earth", zmin=0, zmax=9, name="height",
                                 colorbar=dict(title="height", x=1.0, len=0.5, y=0.25),
                                 hovertemplate="row %{y}, col %{x}<br>height %{z}<extra></extra>"))
        blocked = np.where(cfg.grid == -1, 1.0, np.nan)
        fig.add_trace(go.Heatmap(z=blocked, colorscale=[[0, "#555555"], [1, "#555555"]],
                                 showscale=False, hoverinfo="skip", name="blocked"))
    else:
        names = ["blocked"] + [f"{t} (cost {cfg.terrain_cost[t]})" for t in TERRAINS]
        text = np.array(names, dtype=object)[cfg.grid + 1]
        fig.add_trace(go.Heatmap(z=cfg.grid + 1, zmin=-0.5, zmax=4.5, colorscale=_discrete_scale(TERRAIN_COLOURS),
                                 showscale=False, text=text, name="terrain",
                                 hovertemplate="row %{y}, col %{x}<br>%{text}<extra></extra>"))
        for name, col in zip(names, TERRAIN_COLOURS):   # legend entries for the colours
            fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=name,
                                     marker=dict(symbol="square", size=12, color=col)))
    add_overlays(fig, cfg)
    return _layout(fig, cfg, title=title)


def add_overlays(fig, cfg) -> None:
    sr, sc = cfg.start
    fig.add_trace(go.Scatter(x=[sc], y=[sr], mode="markers", name="depot (recharges)",
                             marker=dict(symbol="square", size=14, color="black", line=dict(color="white", width=2)),
                             hovertemplate="depot (%{y}, %{x})<extra></extra>"))
    rows = [s[0] for s in cfg.stops]
    cols = [s[1] for s in cfg.stops]
    labels = [str(i) for i in range(len(cfg.stops))]
    fig.add_trace(go.Scatter(x=cols, y=rows, mode="markers+text", text=labels, textposition="top right",
                             textfont=dict(size=14, color="black"), name="stops 0-4",
                             marker=dict(symbol="star", size=18, color="gold", line=dict(color="black", width=1)),
                             hovertemplate="stop %{text} (%{y}, %{x})<extra></extra>"))
    if cfg.use_fuel:
        fig.add_trace(go.Scatter(x=[s[1] for s in cfg.stations], y=[s[0] for s in cfg.stations],
                                 mode="markers", name="charging station",
                                 marker=dict(symbol="cross", size=13, color="#00c853", line=dict(color="black", width=1)),
                                 hovertemplate="station (%{y}, %{x})<extra></extra>"))
    if cfg.use_tunnels:
        for k, (a, b) in enumerate(cfg.tunnels):
            col = TUNNEL_COLOURS[k % len(TUNNEL_COLOURS)]
            fig.add_trace(go.Scatter(x=[a[1], b[1]], y=[a[0], b[0]], mode="lines+markers",
                                     name=f"tunnel {k}", line=dict(color=col, dash="dash", width=1.5),
                                     marker=dict(size=10, color=col, line=dict(color="black", width=1)),
                                     hovertemplate=f"tunnel {k} end (%{{y}}, %{{x}})<extra></extra>"))


def add_path(fig, cells, name, colour=ROUTE, dash=None, width=3) -> None:
    if not cells:
        return
    fig.add_trace(go.Scatter(x=[c[1] for c in cells], y=[c[0] for c in cells], mode="lines",
                             name=name, line=dict(color=colour, width=width, dash=dash),
                             hoverinfo="skip"))


def profile_figure(fuel_after, heights, capacity, reserve) -> go.Figure:
    """Fuel and height along the route: two stacked panels sharing the x axis (no dual axis)."""
    steps = list(range(len(fuel_after)))
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("fuel after each move", "height of the cell"))
    fig.add_trace(go.Scatter(x=steps, y=fuel_after, mode="lines", line=dict(color=SERIES, width=2),
                             name="fuel", hovertemplate="move %{x}: fuel %{y}<extra></extra>"), row=1, col=1)
    fig.add_hline(y=reserve, line=dict(color=MUTED, dash="dash", width=1), row=1, col=1,
                  annotation_text=f"planning reserve {reserve}", annotation_font_color=MUTED)
    fig.add_trace(go.Scatter(x=steps, y=heights, mode="lines", line=dict(color=SERIES, width=2),
                             name="height", hovertemplate="move %{x}: height %{y}<extra></extra>"), row=2, col=1)
    fig.update_yaxes(range=[0, capacity * 1.05], title="fuel", row=1, col=1, gridcolor="#e4e3df")
    fig.update_yaxes(range=[0, 9.5], title="height", row=2, col=1, gridcolor="#e4e3df")
    fig.update_xaxes(title="move number", row=2, col=1)
    fig.update_layout(height=420, showlegend=False, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor="white")
    return fig


def expansion_order_figure(cfg, first_grid, title="", n_frames=60) -> go.Figure:
    """Animation: frame k shows every cell whose first expansion happened before the k-th cut,
    coloured by WHEN it was first expanded (early = light, late = dark)."""
    first = np.asarray(first_grid, dtype=float)
    first[first < 0] = np.nan
    last = np.nanmax(first) if np.isfinite(first).any() else 0
    cuts = np.linspace(0, last, n_frames) if last > 0 else [0]

    def z_at(cut):
        return np.where(first <= cut, first, np.nan)

    walls = np.where(cfg.grid == -1, 1.0, np.nan)
    fig = go.Figure(
        data=[go.Heatmap(z=walls, colorscale=[[0, "#bdbdbd"], [1, "#bdbdbd"]], showscale=False, hoverinfo="skip"),
              go.Heatmap(z=z_at(cuts[0]), colorscale="Blues", zmin=0, zmax=max(last, 1),
                         colorbar=dict(title="expansion #"),
                         hovertemplate="row %{y}, col %{x}<br>first expanded at #%{z}<extra></extra>")],
        frames=[go.Frame(data=[go.Heatmap(z=z_at(c))], traces=[1], name=str(i)) for i, c in enumerate(cuts)])
    add_overlays(fig, cfg)
    fig.update_layout(
        updatemenus=[dict(type="buttons", showactive=False, x=0.0, y=-0.08, xanchor="left",
                          buttons=[dict(label="Play", method="animate",
                                        args=[None, dict(frame=dict(duration=80, redraw=True), fromcurrent=True)]),
                                   dict(label="Pause", method="animate",
                                        args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])],
        sliders=[dict(active=0, y=-0.02, currentvalue=dict(prefix="expansion # up to "),
                      steps=[dict(method="animate", label=f"{int(c)}",
                                  args=[[str(i)], dict(mode="immediate", frame=dict(duration=0, redraw=True))])
                             for i, c in enumerate(cuts)])])
    return _layout(fig, cfg, height=640, title=title)


def expansion_count_figure(cfg, count_grid, title="") -> go.Figure:
    """Heatmap of how many states were expanded per cell (log scale: counts span 1..thousands)."""
    count = np.asarray(count_grid, dtype=float)
    z = np.where(count > 0, np.log10(np.maximum(count, 1)), np.nan)   # log only of positive counts
    walls = np.where(cfg.grid == -1, 1.0, np.nan)
    fig = go.Figure([
        go.Heatmap(z=walls, colorscale=[[0, "#bdbdbd"], [1, "#bdbdbd"]], showscale=False, hoverinfo="skip"),
        go.Heatmap(z=z, customdata=count, colorscale="Blues", zmin=0, zmax=max(np.nanmax(z) if np.isfinite(z).any() else 1, 1),
                   colorbar=dict(title="log10(states)"),
                   hovertemplate="row %{y}, col %{x}<br>%{customdata:.0f} states expanded<extra></extra>")])
    add_overlays(fig, cfg)
    return _layout(fig, cfg, height=600, title=title)


def simulation_figure(cfg, timeline, replans, planned_cells, max_frames=150) -> go.Figure:
    """Animated run: agent, rival, the agent's trail, slips (x) and replans (diamonds)."""
    n = len(timeline)
    idx = sorted(set(np.linspace(0, n - 1, min(n, max_frames)).astype(int)))
    replan_steps = {r["step"] for r in replans}
    fig = base_map(cfg, "terrain")
    add_path(fig, planned_cells, "planned route", PLANNED, dash="dot", width=2)
    first = len(fig.data)   # the animated traces come after the static map

    def frame_data(k):
        upto = timeline[:k + 1]
        trail = [t["cell"] for t in upto]
        slips = [t["cell"] for t in upto if t["event"] in ("slip", "slip_failed")]
        reps = [t["cell"] for t in upto if t["step"] in replan_steps]
        cur = timeline[k]
        rival = cur["rival"]
        return [
            go.Scatter(x=[c[1] for c in trail], y=[c[0] for c in trail], mode="lines",
                       line=dict(color=ROUTE, width=3), name="actual route", hoverinfo="skip"),
            go.Scatter(x=[c[1] for c in slips], y=[c[0] for c in slips], mode="markers", name="slip",
                       marker=dict(symbol="x", size=9, color="#ff6d00"), hoverinfo="skip"),
            go.Scatter(x=[c[1] for c in reps], y=[c[0] for c in reps], mode="markers", name="replan",
                       marker=dict(symbol="diamond", size=10, color="#6a1b9a", line=dict(color="white", width=1)),
                       hoverinfo="skip"),
            go.Scatter(x=[cur["cell"][1]], y=[cur["cell"][0]], mode="markers", name="agent",
                       marker=dict(symbol="circle", size=16, color=ROUTE, line=dict(color="white", width=2)),
                       hovertemplate=f"step {cur['step']}, fuel {cur['fuel']}<extra></extra>"),
            go.Scatter(x=[rival[1]] if rival else [None], y=[rival[0]] if rival else [None], mode="markers",
                       name="rival", marker=dict(symbol="x-thin", size=16, color=RIVAL, line=dict(width=4, color=RIVAL)),
                       hoverinfo="skip"),
        ]

    for trace in frame_data(idx[0]):
        fig.add_trace(trace)
    traces = list(range(first, first + 5))
    fig.frames = [go.Frame(data=frame_data(k), traces=traces, name=str(k)) for k in idx]
    fig.update_layout(
        updatemenus=[dict(type="buttons", showactive=False, x=0.0, y=-0.08, xanchor="left",
                          buttons=[dict(label="Play", method="animate",
                                        args=[None, dict(frame=dict(duration=120, redraw=True), fromcurrent=True)]),
                                   dict(label="Pause", method="animate",
                                        args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])],
        sliders=[dict(active=0, y=-0.02, currentvalue=dict(prefix="step "),
                      steps=[dict(method="animate", label=str(timeline[k]["step"]),
                                  args=[[str(k)], dict(mode="immediate", frame=dict(duration=0, redraw=True))])
                             for k in idx])])
    fig.update_layout(height=680)
    return fig


def fuel_time_figure(timeline, capacity) -> go.Figure:
    steps = [t["step"] for t in timeline]
    fuel = [t["fuel"] for t in timeline]
    slip_x = [t["step"] for t in timeline if t["event"] in ("slip", "slip_failed")]
    slip_y = [t["fuel"] for t in timeline if t["event"] in ("slip", "slip_failed")]
    fig = go.Figure([
        go.Scatter(x=steps, y=fuel, mode="lines", line=dict(color=SERIES, width=2), name="fuel",
                   hovertemplate="step %{x}: fuel %{y}<extra></extra>"),
        go.Scatter(x=slip_x, y=slip_y, mode="markers", name="slip",
                   marker=dict(symbol="x", size=8, color="#ff6d00"), hoverinfo="skip")])
    fig.update_yaxes(range=[0, capacity * 1.05], title="fuel", gridcolor="#e4e3df")
    fig.update_xaxes(title="simulation step")
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="white",
                      title="fuel over time (real world)", legend=dict(orientation="h", y=1.15))
    return fig
