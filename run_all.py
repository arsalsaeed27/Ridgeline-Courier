"""One command that rebuilds every report figure and table.

    python run_all.py            # full run
    python run_all.py --quick    # < 5 minutes (viva live change)
    python run_all.py --quick --slip 0.5 --stop 2=14,23 --no-tunnels --no-hills
"""
import sys
import time
from collections import defaultdict

from oel.config import RESULTS_DIR, parse_cli
from oel.experiments import (eval_along_route, fuel_reserve, heuristic_eval, heuristic_scenarios, llm_eval,
                            memory_limit, search_small, standin_demo, validator_fault_injection,
                            weighted_astar)
from oel.stamp import get_logger, stamp
from oel.world.plots import plot_elevation_map, plot_instance_map


def output_summary(since: float) -> str:
    """Every file under results/ written during this run, grouped by folder. Figures and
    tables are listed by name; folders with many files (logs, LLM traces) are counted."""
    groups = defaultdict(list)
    for path in sorted(RESULTS_DIR.rglob("*")):
        if path.is_file() and path.name != ".gitkeep" and path.stat().st_mtime >= since:
            groups[path.parent.relative_to(RESULTS_DIR).as_posix()].append(path.name)
    lines = [f"output files written in this run: {sum(len(v) for v in groups.values())}"]
    for folder in sorted(groups):
        names = groups[folder]
        where = "results/" if folder == "." else f"results/{folder}/"
        if folder in ("figures", "tables") or len(names) <= 6:
            lines.append(f"  {where} ({len(names)}): " + ", ".join(names))
        else:
            lines.append(f"  {where} ({len(names)} files)")
    return "\n".join(lines)


def main(argv=None):
    t0 = time.perf_counter()
    started = time.time() - 1   # wall clock, for "files written during this run"
    try:
        cfg = parse_cli(argv)
    except ValueError as err:   # bad live-change value: short message, no traceback
        sys.exit(f"Invalid option: {err}")
    log = get_logger("run_all")
    log.info("config:\n" + cfg.summary())

    # ------------------------------------------------------------ maps (Turn 1)
    log.info("saved %s", plot_instance_map(cfg).name)
    log.info("saved %s", plot_elevation_map(cfg).name)

    # ------------------------------------------------------------ pipeline demo (Turn 1)
    # plan with the default planner (A* + h_ours + fuel pruning), execute it in the simulator
    # (slip + rival, rejoin/full replanning), save standin_route.png + standin_summary.
    standin_demo.run(cfg, log)

    # fuel-reserve experiment (Turn 1): 5 reserves x 30 seeds (--quick: 10 seeds). It took
    # ~28 min with UCS replans, so it was skipped in --quick; with A* replans it fits again.
    fuel_reserve.run(cfg, log)

    # ------------------------------------------------------------ Part A (Turn 4: M. Rayyan)
    # TODO: vectorised cost map + loop benchmark table, PEAS / environment tables.

    # ------------------------------------------------------------ Part B (Turn 2: Laiba Rehman)
    # all six algorithms on 30 small instances (7x7 window, ~6 s, so also in --quick)
    search_small.run(cfg, log)
    # heuristics: admissibility + consistency checks, full-map comparison, ablation
    # (~100 s in --quick; the full run also measures peak memory, which is 5-8x slower for UCS)
    heuristic_eval.run(cfg, log)
    # The next three cache their runs in oel/experiments/cache/ (instant when nothing changed;
    # a live change that alters planning recomputes them).
    # weighted A* (w = 1..5) and inadmissible A* on the full map, pruning off/on (~35 s uncached)
    weighted_astar.run(cfg, log)
    # A* / UCS with a memory cap vs IDS vs IDA* on 30 small + 30 medium instances (~30 s uncached)
    memory_limit.run(cfg, log)
    # main comparison + ablation over 30 re-drawn scenarios, failure analysis. --quick runs only
    # the fast variants and reads UCS / A*+h_manhattan / A*+h_farthest from the cache (computing
    # them takes ~10 min on 4 processes: full mode only).
    heuristic_scenarios.run(cfg, log)

    # ------------------------------------------------------------ Part C (Turn 3: Ali Salman Mustafa)
    # Turn 2 (Laiba): the evaluation function along two simulated runs (sanity check, ~3 s)
    eval_along_route.run(cfg, log)
    # TODO (Turn 3): minimax vs alpha-beta node counts, weight tuning with oel/game/tuning.py,
    #       100-game tournament (Wilson CIs).

    # ------------------------------------------------------------ Part D (Turn 1: M. Arsal Saeed)
    # LLM dispatcher: 20 requests x (direct, LLM, LLM + validation). Replays the committed LLM
    # and plan caches (no API key needed, a few seconds); --live calls Groq on a cache miss.
    llm_eval.run(cfg, log)
    # validator fault injection: 18 gold calls x 10 corruptions, no API. The full run computes it
    # (~15-25 min); --quick reuses the cached results (seconds) or skips if the config changed.
    validator_fault_injection.run(cfg, log, compute=not cfg.quick)

    # ------------------------------------------------------------ Part E (Turn 1: M. Arsal Saeed)
    # The Streamlit UI (streamlit run ui/app.py) shows everything above; it needs no extra outputs.

    log.info("%s", output_summary(started))
    log.info("total runtime %.2f s", time.perf_counter() - t0)
    print(stamp())


if __name__ == "__main__":
    main(sys.argv[1:])
