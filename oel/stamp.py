"""Stamping helpers: every figure, table and log carries the team + instance line.

Always use these instead of plt.savefig / df.to_csv / logging.basicConfig.
Each saved figure or table is also recorded in results/manifest.json, which
tests/test_stamp.py uses to prove that PNGs (which can't be text-searched) were stamped.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from oel.config import INSTANCE_ID, MEMBERS, RESULTS_DIR

FIG_DIR = RESULTS_DIR / "figures"
TABLE_DIR = RESULTS_DIR / "tables"
LOG_DIR = RESULTS_DIR / "logs"
MANIFEST = RESULTS_DIR / "manifest.json"


def stamp() -> str:
    """'Laiba Rehman (505099) | ... | M. Rayyan (534733) | instance 38bfda97'"""
    people = " | ".join(f"{name} ({cms})" for name, cms in MEMBERS)
    return f"{people} | instance {INSTANCE_ID}"


def _record(path: Path) -> None:
    """Add a saved file to the manifest (relative path -> the stamp it was saved with)."""
    data = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    rel = path.relative_to(RESULTS_DIR).as_posix()
    data[rel] = stamp()
    MANIFEST.write_text(json.dumps(data, indent=2, sort_keys=True))


def save_fig(fig, name: str, dpi: int = 150) -> Path:
    """Put the stamp at the top of the figure and save it to results/figures/<name>.png."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    if not name.endswith(".png"):
        name += ".png"
    fig.suptitle(stamp(), fontsize=7, y=0.995)
    path = FIG_DIR / name
    # also embed the stamp as PNG text metadata, so the file itself carries it
    fig.savefig(path, dpi=dpi, bbox_inches="tight", metadata={"Description": stamp()})
    _record(path)
    return path


def save_table(df, name: str) -> tuple:
    """Save a DataFrame as CSV and Markdown in results/tables/, stamp on the first line."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    base = name.removesuffix(".csv").removesuffix(".md")
    csv_path = TABLE_DIR / f"{base}.csv"
    md_path = TABLE_DIR / f"{base}.md"
    # '#' first line: pandas can read it back with pd.read_csv(path, comment="#")
    csv_path.write_text(f"# {stamp()}\n" + df.to_csv(index=False), encoding="utf-8")
    md_path.write_text(f"_{stamp()}_\n\n" + df.to_markdown(index=False) + "\n", encoding="utf-8")
    _record(csv_path)
    _record(md_path)
    return csv_path, md_path


def get_logger(name: str) -> logging.Logger:
    """Logger that prints to the console and to results/logs/<name>.log.
    The stamp is written as the first line of the log file (fresh file per run)."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"oel.{name}")
    if logger.handlers:          # already set up in this process: reuse it
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S")

    log_path = LOG_DIR / f"{name}.log"
    log_path.write_text(f"{stamp()}\n", encoding="utf-8")
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(console)
    logger.info(stamp())
    return logger
