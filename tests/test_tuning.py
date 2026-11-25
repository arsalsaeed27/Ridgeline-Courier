"""Turn 2 session 4: the weight-tuning tool, proven with a stand-in play_fn before Ali uses it."""
import pytest

from oel import stamp
from oel.experiments import framework
from oel.game.tuning import (coordinate_ascent, demo_play_fn, grid_search, play_settings,
                             plot_weight_heatmap, summarise_outcomes)


@pytest.fixture(autouse=True)
def private_cache(tmp_path, monkeypatch):
    """Keep the tests' cache out of oel/experiments/cache/."""
    monkeypatch.setattr(framework, "CACHE_DIR", tmp_path / "cache")


GRID = {"interference": [1.0, 2.0, 4.0], "race": [0.5, 1.0, 2.0]}


def test_summarise_outcomes():
    row = summarise_outcomes(["win", "win", "draw", "loss"])
    assert row["games"] == 4 and row["wins"] == 2 and row["win_rate"] == 0.5
    assert row["points"] == 0.5 + 0.5 * 0.25
    assert 0 <= row["win_ci_low"] < 0.5 < row["win_ci_high"] <= 1


def test_grid_search_finds_the_best_setting_and_repeats_exactly():
    df = grid_search(demo_play_fn, GRID, n_games=40, seed=7, workers=1)
    assert len(df) == 9
    assert (df.iloc[0].interference, df.iloc[0].race) == (2.0, 1.0)      # the stand-in's optimum
    again = grid_search(demo_play_fn, GRID, n_games=40, seed=7, workers=1)
    assert df.equals(again)                                              # same seed, same table


def test_parallel_matches_serial_and_the_cache_is_used(tmp_path):
    settings = [{"interference": i, "race": 1.0} for i in (1.0, 2.0, 4.0)]
    serial = play_settings(demo_play_fn, settings, n_games=20, seed=3, workers=1, cache_name="serial")
    parallel = play_settings(demo_play_fn, settings, n_games=20, seed=3, workers=2, cache_name="parallel")
    assert serial.equals(parallel)
    assert (tmp_path / "cache" / "parallel.json").exists()
    cached = play_settings(demo_play_fn, settings, n_games=20, seed=3, workers=2, cache_name="parallel")
    assert cached.equals(parallel)


def test_coordinate_ascent_climbs_to_the_optimum():
    start = {"interference": 8.0, "race": 4.0, "mobility": 0.5}
    best, history = coordinate_ascent(demo_play_fn, start, steps=5, n_games=40, seed=11, workers=1)
    assert best["interference"] == 2.0 and best["race"] == 1.0
    first = history[history.kept].points.iloc[0]
    assert history[history.kept].points.iloc[-1] > first            # it really improved
    assert {"round", "tuned", "kept", "win_ci_low", "win_ci_high"} <= set(history.columns)


def test_heatmap_is_stamped(tmp_path, monkeypatch):
    monkeypatch.setattr(stamp, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(stamp, "FIG_DIR", tmp_path / "figures")
    monkeypatch.setattr(stamp, "MANIFEST", tmp_path / "manifest.json")
    df = grid_search(demo_play_fn, GRID, n_games=10, seed=1, workers=1)
    path = plot_weight_heatmap(df, "interference", "race", name="heatmap_test")
    assert path.exists() and path.parent == tmp_path / "figures"
    assert stamp.stamp() in (tmp_path / "manifest.json").read_text()
