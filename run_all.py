"""One command that rebuilds every report figure and table.

    python run_all.py            # full run
    python run_all.py --quick    # < 5 minutes (viva live change)
    python run_all.py --quick --slip 0.5 --stop 2=14,23 --no-tunnels --no-hills
"""
import sys
import time

from oel.config import parse_cli
from oel.experiments import fuel_reserve, standin_demo
from oel.stamp import get_logger, stamp
from oel.world.plots import plot_elevation_map, plot_instance_map


def main(argv=None):
    t0 = time.perf_counter()
    try:
        cfg = parse_cli(argv)
    except ValueError as err:   # bad live-change value: short message, no traceback
        sys.exit(f"Invalid option: {err}")
    log = get_logger("run_all")
    log.info("config:\n" + cfg.summary())

    # ------------------------------------------------------------ maps (Turn 1)
    log.info("saved %s", plot_instance_map(cfg).name)
    log.info("saved %s", plot_elevation_map(cfg).name)

    # ------------------------------------------------------------ stand-in pipeline (Turn 1)
    # TEMPORARY: plan with the stand-in UCS, execute it in the simulator (slip + rival,
    # rejoin/full replanning), save standin_route.png + standin_summary. Swap in Laiba's A*.
    standin_demo.run(cfg, log)

    # fuel-reserve experiment (Turn 1): 5 reserves x 30 seeds, ~28 min with the stand-in UCS.
    # Skipped in --quick (even 10 seeds take ~10 min, over the 5-minute limit); run it alone
    # with:  python -m oel.experiments.fuel_reserve --quick   (10 seeds per reserve)
    if cfg.quick:
        log.info("fuel_reserve experiment skipped in --quick (kept from the last full run)")
    else:
        fuel_reserve.run(cfg, log)

    # ------------------------------------------------------------ Part A (Turn 4: M. Rayyan)
    # TODO: vectorised cost map + loop benchmark table, PEAS / environment tables.

    # ------------------------------------------------------------ Part B (Turn 2: Laiba Rehman)
    # TODO: planner comparison table (BFS, UCS, DLS, IDS, Greedy, A*, weighted A*),
    #       30-seed experiments with 95% CIs, heuristic ablation.

    # ------------------------------------------------------------ Part C (Turn 3: Ali Salman Mustafa)
    # TODO: minimax vs alpha-beta node counts, weight tuning, 100-game tournament (Wilson CIs).

    # ------------------------------------------------------------ Part D (Turn 1: M. Arsal Saeed)
    # TODO: LLM dispatcher runs (from oel/llm/cache/ when no GROQ_API_KEY).

    # ------------------------------------------------------------ Part E (Turn 1: M. Arsal Saeed)
    # TODO: summary figures for the UI / report.

    log.info("total runtime %.2f s", time.perf_counter() - t0)
    print(stamp())


if __name__ == "__main__":
    main(sys.argv[1:])
