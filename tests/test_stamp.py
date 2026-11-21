"""Every file in results/ carries the stamp.

Text files (csv, md, log, txt, json) are searched directly. PNGs can't be text-searched, so
we check that save_fig recorded them in results/manifest.json AND that the PNG metadata
holds the stamp.
"""
import json

from PIL import Image

from oel.config import RESULTS_DIR
from oel.stamp import MANIFEST, stamp

TEXT_SUFFIXES = {".csv", ".md", ".log", ".txt", ".json"}


def _result_files():
    return [p for p in RESULTS_DIR.rglob("*")
            if p.is_file() and p.name != ".gitkeep" and p != MANIFEST]


def test_stamp_text():
    s = stamp()
    for name in ["Laiba Rehman (505099)", "M. Arsal Saeed (506676)",
                 "Ali Salman Mustafa (534732)", "M. Rayyan (534733)", "instance 38bfda97"]:
        assert name in s


def test_every_result_file_is_stamped():
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    unstamped = []
    for path in _result_files():
        rel = path.relative_to(RESULTS_DIR).as_posix()
        if path.suffix in TEXT_SUFFIXES:
            ok = stamp() in path.read_text(encoding="utf-8", errors="ignore")
        elif path.suffix == ".png":
            ok = manifest.get(rel) == stamp() and Image.open(path).text.get("Description") == stamp()
        else:
            ok = manifest.get(rel) == stamp()
        if not ok:
            unstamped.append(rel)
    assert not unstamped, f"files without the stamp: {unstamped}"


def test_save_helpers_stamp(tmp_path, monkeypatch):
    """save_fig / save_table / get_logger really write the stamp (into a temp folder)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    from oel import stamp as st

    monkeypatch.setattr(st, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(st, "FIG_DIR", tmp_path / "figures")
    monkeypatch.setattr(st, "TABLE_DIR", tmp_path / "tables")
    monkeypatch.setattr(st, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(st, "MANIFEST", tmp_path / "manifest.json")

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    png = st.save_fig(fig, "demo")
    plt.close(fig)
    csv, md = st.save_table(pd.DataFrame({"a": [1, 2]}), "demo")
    st.get_logger("demo_test").info("hello")

    assert Image.open(png).text["Description"] == stamp()
    assert csv.read_text().splitlines()[0] == f"# {stamp()}"
    assert stamp() in md.read_text()
    assert (tmp_path / "logs" / "demo_test.log").read_text().splitlines()[0] == stamp()
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert set(manifest) == {"figures/demo.png", "tables/demo.csv", "tables/demo.md"}
