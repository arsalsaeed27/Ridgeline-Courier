"""Streamlit smoke tests (headless AppTest): the app loads, every tab renders, the stamp is
shown, sidebar live changes reach the config, and a bad change shows an error, not a crash.
Nothing here plans from scratch or calls the API (cached plans / cached LLM replies only)."""
import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from oel.config import ROOT, load_config

APP = str(ROOT / "ui" / "app.py")   # AppTest resolves relative paths against this test file
TABS = ["World", "Plan", "Search visualisation", "Simulate", "Rival game", "LLM Dispatcher", "Experiments"]


@pytest.fixture
def app():
    at = AppTest.from_file(APP, default_timeout=180)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_app_loads_with_all_tabs_and_stamp(app):
    assert [t.label for t in app.tabs] == TABS
    for tab in app.tabs:
        assert len(tab.children) > 0, f"tab {tab.label} is empty"
    page = " ".join(m.value for m in app.markdown)
    assert "Laiba Rehman (505099)" in page and "M. Rayyan (534733)" in page
    assert "instance 38bfda97" in page


def test_sidebar_slip_changes_config(app):
    assert app.session_state["cfg_slip"] == load_config().slip
    app.sidebar.slider(key="slip").set_value(0.5).run()
    assert not app.exception
    assert app.session_state["cfg_slip"] == 0.5
    assert any("--slip 0.5" in c.value for c in app.sidebar.code)


def test_invalid_stop_move_shows_error_not_crash(app):
    cfg = load_config()
    r, c = (int(x) for x in np.argwhere(cfg.grid == -1)[0])   # a wall cell
    app.sidebar.checkbox(key="move_stop").check().run()
    app.sidebar.number_input(key="move_row").set_value(r)
    app.sidebar.number_input(key="move_col").set_value(c).run()
    assert not app.exception
    assert app.session_state["config_error"]
    assert any("Invalid" in e.value for e in app.error)


def test_reset_restores_defaults(app):
    app.sidebar.slider(key="slip").set_value(0.7).run()
    app.sidebar.button[0].click().run()
    assert app.session_state["cfg_slip"] == load_config().slip


def test_llm_tab_replays_a_cached_request(app):
    app.selectbox(key="llm_choice").set_value(app.selectbox(key="llm_choice").options[0]).run()
    app.button(key="llm_btn").click().run()
    assert not app.exception
    run = app.session_state["llm_run"]
    assert run["error"] is None and run["result"]["kind"] == "plan"
