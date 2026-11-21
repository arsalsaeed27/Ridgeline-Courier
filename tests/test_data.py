"""The data files in data/ are the ones for our instance."""
import json

import numpy as np

from oel import config
from oel.config import DATA_DIR, INSTANCE_ID, load_config


def test_instance_id():
    inst = json.loads((DATA_DIR / f"instance_{INSTANCE_ID}.json").read_text())
    assert inst["instance_id"] == "38bfda97"


def test_grid_shape():
    assert load_config().grid.shape == (40, 40)


def test_fuel_capacity():
    assert load_config().fuel_capacity == 98


def test_twist_layout():
    cfg = load_config()
    assert cfg.stations == [(23, 11), (0, 25), (21, 28), (31, 20)]
    assert cfg.tunnels == [((26, 14), (22, 35)), ((10, 36), (4, 2)), ((19, 6), (38, 12))]


def test_elevation_range():
    elev = load_config().elevation
    assert elev.shape == (40, 40)
    assert np.issubdtype(elev.dtype, np.integer)
    assert elev.min() >= 0 and elev.max() <= 9


def test_no_free_fuel_loop():
    assert config.REGEN < config.UP_FUEL
