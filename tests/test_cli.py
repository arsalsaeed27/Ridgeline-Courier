"""CLI overrides for the viva live change."""
import numpy as np
import pytest

from oel.config import parse_cli


def test_defaults():
    cfg = parse_cli([])
    assert cfg.slip == 0.25 and cfg.rival_depth == 6
    assert cfg.use_fuel and cfg.use_tunnels and cfg.use_hills


def test_slip_override():
    assert parse_cli(["--slip", "0.5"]).slip == 0.5


def test_no_hills():
    cfg = parse_cli(["--no-hills"])
    assert cfg.use_hills is False and cfg.use_fuel and cfg.use_tunnels


def test_flags_combined():
    cfg = parse_cli(["--quick", "--no-fuel", "--no-tunnels", "--rival-depth", "3",
                     "--fuel-capacity", "120", "--seed", "7"])
    assert cfg.quick and not cfg.use_fuel and not cfg.use_tunnels
    assert (cfg.rival_depth, cfg.fuel_capacity, cfg.seed) == (3, 120, 7)


def test_valid_stop_move():
    cfg0 = parse_cli([])
    reach = cfg0.reachable_from_start()
    # pick any reachable free cell that isn't the depot or an existing stop
    cell = next(tuple(map(int, p)) for p in np.argwhere(reach)
                if tuple(p) != cfg0.start and tuple(map(int, p)) not in cfg0.stops)
    cfg = parse_cli(["--stop", f"2={cell[0]},{cell[1]}"])
    assert cfg.stops[2] == cell


def test_blocked_stop_rejected():
    cfg0 = parse_cli([])
    r, c = map(int, np.argwhere(cfg0.grid == -1)[0])
    with pytest.raises(ValueError):
        parse_cli(["--stop", f"2={r},{c}"])


def test_bad_values_rejected():
    with pytest.raises(ValueError):
        parse_cli(["--slip", "1.5"])
    with pytest.raises(ValueError):
        parse_cli(["--stop", "9=1,1"])
    with pytest.raises(ValueError):
        parse_cli(["--stop", "2=100,100"])


def test_fuel_reserve_flag():
    assert parse_cli(["--fuel-reserve", "15"]).fuel_reserve == 15
    with pytest.raises(ValueError):
        parse_cli(["--fuel-reserve", "-1"])
    with pytest.raises(ValueError):
        parse_cli(["--fuel-reserve", "98"])   # must leave room in a 98 tank
