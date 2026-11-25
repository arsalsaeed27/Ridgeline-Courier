"""Ridgeline Courier: Streamlit UI (Part E).   Run:  streamlit run ui/app.py

The UI only CALLS the project's code: the sidebar builds the same CLI arguments as run_all.py
and passes them to oel.config.parse_cli; plans come from the shared plan cache; simulations from
oel.world.simulator; LLM runs from oel.llm.agent. Expensive work runs only when a button is
pressed, behind a spinner, and is cached.
"""
from __future__ import annotations

import dataclasses
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))        # so "import oel" works under `streamlit run ui/app.py`
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np                    # noqa: E402
import pandas as pd                   # noqa: E402
import streamlit as st                # noqa: E402

import views                          # noqa: E402
from oel.config import TERRAINS, load_config, parse_cli   # noqa: E402
from oel.llm import plans, tools      # noqa: E402
from oel.search import registry       # noqa: E402
from oel.search.uninformed import ucs  # noqa: E402
from oel.stamp import stamp           # noqa: E402
from oel.world.constraints import PlanConstraints        # noqa: E402
from oel.world.problem import DeliveryProblem            # noqa: E402
from oel.world.simulator import RejoinReplanner, Simulator, greedy_blocker   # noqa: E402

PLAN_ESTIMATE = "about 25-50 s with UCS on the full map"
st.set_page_config(page_title="Ridgeline Courier", layout="wide")

# ---------------------------------------------------------------- banner (on every page)
st.markdown(
    """<style>
    .stamp-banner {position: sticky; top: 2.9rem; z-index: 999; background: #1b2a41; color: #fff;
                   padding: 6px 14px; border-radius: 4px; font-size: 0.85rem; margin-bottom: 8px;}
    </style>""", unsafe_allow_html=True)
st.markdown(f"<div class='stamp-banner'><b>Ridgeline Courier</b> &nbsp;|&nbsp; {stamp()}</div>",
            unsafe_allow_html=True)


# ---------------------------------------------------------------- sidebar: live change
@st.cache_resource
def defaults():
    return load_config()


DEF = defaults()
WIDGET_DEFAULTS = {
    "slip": float(DEF.slip), "reserve": int(DEF.fuel_reserve), "rival_depth": int(DEF.rival_depth),
    "capacity": int(DEF.fuel_capacity), "use_fuel": True, "use_tunnels": True, "use_hills": True,
    "seed": int(DEF.seed), "move_stop": False, "move_idx": 0,
    "move_row": int(DEF.stops[0][0]), "move_col": int(DEF.stops[0][1]),
}
for key, value in WIDGET_DEFAULTS.items():
    st.session_state.setdefault(key, value)


def reset_defaults():
    for k, v in WIDGET_DEFAULTS.items():
        st.session_state[k] = v


sb = st.sidebar
sb.header("Live change")
sb.caption("Same options as `run_all.py`; every change goes through `parse_cli`.")
sb.slider("slip probability", 0.0, 0.95, step=0.05, key="slip")
sb.number_input("planning fuel reserve", 0, 300, key="reserve")
sb.number_input("rival search depth", 1, 12, key="rival_depth")
sb.number_input("fuel capacity", 1, 300, key="capacity")
sb.checkbox("fuel limit (twist 1)", key="use_fuel")
sb.checkbox("teleport tunnels (twist 2)", key="use_tunnels")
sb.checkbox("hills (twist 3)", key="use_hills")
sb.number_input("seed", 0, 2**31 - 1, key="seed")
sb.checkbox("move a stop", key="move_stop")
if st.session_state.move_stop:
    sb.selectbox("stop", list(range(len(DEF.stops))), key="move_idx")
    c1, c2 = sb.columns(2)
    c1.number_input("row", 0, DEF.n - 1, key="move_row")
    c2.number_input("col", 0, DEF.n - 1, key="move_col")
sb.button("Reset to instance defaults", on_click=reset_defaults)


def build_argv() -> tuple:
    """Widgets -> the CLI arguments run_all.py would get (only the ones that differ)."""
    s = st.session_state
    argv = []
    if s.slip != DEF.slip:
        argv += ["--slip", f"{s.slip:g}"]
    if s.reserve != DEF.fuel_reserve:
        argv += ["--fuel-reserve", str(s.reserve)]
    if s.rival_depth != DEF.rival_depth:
        argv += ["--rival-depth", str(s.rival_depth)]
    if s.capacity != DEF.fuel_capacity:
        argv += ["--fuel-capacity", str(s.capacity)]
    if not s.use_fuel:
        argv.append("--no-fuel")
    if not s.use_tunnels:
        argv.append("--no-tunnels")
    if not s.use_hills:
        argv.append("--no-hills")
    if s.seed != DEF.seed:
        argv += ["--seed", str(s.seed)]
    if s.move_stop:
        argv += ["--stop", f"{s.move_idx}={s.move_row},{s.move_col}"]
    return tuple(argv)


ARGV = build_argv()
try:
    cfg = parse_cli(list(ARGV))
    config_error = None
except ValueError as err:          # e.g. a stop moved onto a wall: show it, keep the defaults
    cfg = parse_cli([])
    ARGV = ()
    config_error = str(err)
    sb.error(f"Invalid change: {err}")
    st.error(f"Invalid live change ({err}). Showing the instance defaults instead.")
st.session_state["cfg_slip"] = cfg.slip                 # read by the UI tests
st.session_state["config_error"] = config_error
sb.caption("Command line equivalent:")
sb.code("python run_all.py --quick " + " ".join(ARGV), language="bash")


# ---------------------------------------------------------------- cached work
@st.cache_data(show_spinner=False)
def simulate_run(argv: tuple, plan_id: str) -> dict:
    """Simulate a stored plan (slip + rival + rejoin/full replanning) and return the timeline."""
    run_cfg = parse_cli(list(argv))
    rec = plans.load_plan(plan_id)
    problem = DeliveryProblem(run_cfg, constraints=PlanConstraints.from_dict(rec["constraints"]))
    sim = Simulator(run_cfg, problem, np.random.default_rng(run_cfg.seed))
    rep = sim.run_plan(rec["actions"], RejoinReplanner(ucs, ucs, run_cfg.rejoin_radius))
    return {"outcome": rep.outcome, "end_reason": rep.end_reason, "total_cost": rep.total_cost,
            "planned_cost": rep.planned_cost, "extra": rep.extra_cost_text(), "steps": rep.steps,
            "slips": rep.slips, "failed": rep.failed_moves, "waits": rep.waits,
            "rejoins": rep.n_rejoin, "full": rep.n_full, "replans": rep.replans,
            "timeline": rep.timeline, "rival_path": [list(c) for c in rep.rival_path if c]}


def constraints_from_widgets() -> PlanConstraints:
    s = st.session_state
    return PlanConstraints.build(stop_order=s.get("c_order") or None,
                                 avoid_terrain=s.get("c_avoid") or None,
                                 use_tunnels=False if s.get("c_no_tunnels") else None)


def current_plan():
    pid = st.session_state.get("plan_id")
    return plans.load_plan(pid) if pid else None


def stats_table(rec, report):
    rows = {
        "algorithm": rec["algorithm"] + (f" + {rec['heuristic']}" if rec.get("heuristic") else ""),
        "feasible": rec["feasible"], "cost": rec["cost"], "moves": rec.get("length"),
        "nodes expanded": rec["nodes_expanded"], "runtime (s)": rec["runtime_s"],
        "peak memory (KB)": rec.get("peak_mem_kb") or "not measured",
        "refuels": len(rec.get("refuel_cells", [])), "tunnels used": rec.get("tunnels_used"),
        "height climbed": report.get("height_climbed") if report else None,
        "min fuel": report.get("min_fuel") if report else None,
        "delivery order": str(rec.get("delivery_order")),
    }
    return pd.DataFrame({"value": [str(v) for v in rows.values()]}, index=list(rows.keys()))


# ---------------------------------------------------------------- tabs
tab_world, tab_plan, tab_search, tab_sim, tab_rival, tab_llm, tab_exp = st.tabs(
    ["World", "Plan", "Search visualisation", "Simulate", "Rival game", "LLM Dispatcher", "Experiments"])

# ------------------------------------------------ World
with tab_world:
    layer = st.radio("layer", ["terrain", "elevation"], horizontal=True, key="world_layer")
    st.plotly_chart(views.base_map(cfg, layer, title=f"Instance {cfg.instance_id}: {layer}"),
                    width="stretch")
    st.caption(f"Stops are numbered 0-4. Depot {cfg.start}; fuel capacity {cfg.fuel_capacity}; "
               f"planning reserve {cfg.fuel_reserve}; slip {cfg.slip}.")

# ------------------------------------------------ Plan
with tab_plan:
    c1, c2, c3 = st.columns(3)
    algo = c1.selectbox("algorithm (from the planner registry)", sorted(registry.PLANNERS), key="algo")
    heuristic = None
    if registry.PLANNER_INFO[algo]["uses_heuristic"]:
        if registry.HEURISTICS:
            heuristic = c1.selectbox("heuristic", sorted(registry.HEURISTICS), key="heur")
        else:
            c1.warning("This planner needs a heuristic, but none is registered yet.")
    c2.multiselect("deliver these stops first (in the order you pick)", list(range(len(cfg.stops))), key="c_order")
    c2.multiselect("avoid terrain", TERRAINS, key="c_avoid")
    c3.checkbox("no tunnels", key="c_no_tunnels")
    measure = c3.checkbox("measure peak memory (several times slower)", key="c_mem")

    constraints = constraints_from_widgets()
    pid = plans.plan_key(cfg, constraints, algo, heuristic)
    cached = plans.load_plan(pid)
    needs_run = cached is None or (measure and not cached.get("peak_mem_kb"))
    label = "Plan" + (f" ({PLAN_ESTIMATE})" if needs_run else " (cached: instant)")
    # show only a plan that matches the CURRENT settings (a cached one appears straight away)
    st.session_state["plan_id"] = pid if cached is not None else None
    if st.button(label, key="plan_btn", type="primary", disabled=heuristic is None and
                 registry.PLANNER_INFO[algo]["uses_heuristic"]):
        with st.spinner(f"Planning... {PLAN_ESTIMATE if needs_run else 'loading from the cache'}"):
            rec = plans.plan(cfg, constraints, algo, heuristic, measure_memory=measure)
        st.session_state["plan_id"] = rec["plan_id"]

    rec = current_plan()
    if rec is None:
        st.info("No plan for these settings yet: press **Plan**.")
    elif not rec["feasible"]:
        st.error(f"Infeasible: {rec['reason']}")
    else:
        report = tools.fuel_report(cfg, rec["plan_id"])
        left, right = st.columns([3, 2])
        fig = views.base_map(cfg, "terrain", title=f"Route (cost {rec['cost']:.0f})")
        views.add_path(fig, [s[:2] for s in rec["path"]], "route")
        left.plotly_chart(fig, width="stretch")
        right.dataframe(stats_table(rec, report), width="stretch")
        heights = [int(cfg.elevation[s[0], s[1]]) for s in rec["path"]]
        right.plotly_chart(views.profile_figure(report["fuel_after_each_move"], heights,
                                                cfg.fuel_capacity, report["planning_reserve"]),
                           width="stretch")

# ------------------------------------------------ Search visualisation
with tab_search:
    rec = current_plan()
    view = st.radio("view", ["expansion order (animation)", "expansion count (heatmap)"],
                    horizontal=True, key="search_view")
    compare = st.checkbox("compare with a second planner (same constraints)", key="cmp")
    if rec is None:
        st.info("Make a plan in the **Plan** tab first.")
    else:
        con = PlanConstraints.from_dict(rec["constraints"])
        panels = [(rec["algorithm"], rec.get("heuristic"))]
        if compare:
            algo2 = st.selectbox("second planner", sorted(registry.PLANNERS), key="algo2")
            heur2 = None
            if registry.PLANNER_INFO[algo2]["uses_heuristic"] and registry.HEURISTICS:
                heur2 = st.selectbox("its heuristic", sorted(registry.HEURISTICS), key="heur2")
            panels.append((algo2, heur2))
        cols = st.columns(len(panels))
        for col, (a, h) in zip(cols, panels):
            r = plans.load_plan(plans.plan_key(cfg, con, a, h))
            name = a + (f" + {h}" if h else "")
            if r is None or "expansion_first" not in r:
                col.info(f"{name}: the search was not recorded for these settings.")
                if col.button(f"Record the search for {name} ({PLAN_ESTIMATE})", key=f"rec_{a}_{h}_{len(panels)}"):
                    with st.spinner(f"Re-planning with {name} to record its search... {PLAN_ESTIMATE}"):
                        r = plans.plan(cfg, con, a, h, refresh=True)
                    st.rerun()
                continue
            note = (f"{r['nodes_expanded']:,} states expanded"
                    + (f" (grids show the first {r['expansion_recorded']:,})" if r["expansion_capped"] else ""))
            if view.startswith("expansion order"):
                col.plotly_chart(views.expansion_order_figure(cfg, r["expansion_first"], title=name),
                                 width="stretch")
            else:
                col.plotly_chart(views.expansion_count_figure(cfg, r["expansion_count"], title=name),
                                 width="stretch")
            col.caption(note)

# ------------------------------------------------ Simulate
with tab_sim:
    rec = current_plan()
    if rec is None or not rec["feasible"]:
        st.info("Make a feasible plan in the **Plan** tab first.")
    else:
        st.write(f"Plan `{rec['plan_id']}` (cost {rec['cost']:.0f}) in the real world: slip {cfg.slip}, "
                 f"seed {cfg.seed}, placeholder rival, rejoin/full replanning.")
        if st.button("Simulate (usually 10-90 s: full replans run UCS)", key="sim_btn", type="primary"):
            with st.spinner("Simulating..."):
                st.session_state["sim"] = simulate_run(ARGV, rec["plan_id"])
                st.session_state["sim_key"] = (ARGV, rec["plan_id"])
        sim = st.session_state.get("sim")
        if sim and st.session_state.get("sim_key") == (ARGV, rec["plan_id"]):
            m = st.columns(6)
            m[0].metric("outcome", sim["outcome"])
            m[1].metric("real cost", f"{sim['total_cost']:.0f}", sim["extra"])
            m[2].metric("steps", sim["steps"])
            m[3].metric("slips", sim["slips"])
            m[4].metric("replans (rejoin / full)", f"{sim['rejoins']} / {sim['full']}")
            m[5].metric("waits for rival", sim["waits"])
            st.caption(f"Ended because: {sim['end_reason']}")
            st.plotly_chart(views.simulation_figure(cfg, sim["timeline"], sim["replans"],
                                                    [s[:2] for s in rec["path"]]), width="stretch")
            st.plotly_chart(views.fuel_time_figure(sim["timeline"], cfg.fuel_capacity), width="stretch")

# ------------------------------------------------ Rival game (placeholder)
with tab_rival:
    st.subheader("Rival game: Minimax / Alpha-Beta (Turn 3, Ali Salman Mustafa)")
    st.info("Ali adds the adversarial search here: a local game window around the agent, Minimax and "
            "Alpha-Beta with move ordering (rival search depth from the sidebar), node counts, and the "
            "100-game tournament. Until then the rival is the PLACEHOLDER policy below.")
    st.markdown("**Current placeholder rival (`greedy_blocker`):**")
    st.code((greedy_blocker.__doc__ or "").strip(), language="text")
    sim = st.session_state.get("sim")
    if sim and sim.get("rival_path"):
        fig = views.base_map(cfg, "terrain", title="Where the placeholder rival went in the last simulation")
        views.add_path(fig, sim["rival_path"], "rival path", views.RIVAL, dash="dot")
        st.plotly_chart(fig, width="stretch")
        st.caption(f"The agent waited {sim['waits']} step(s) for the rival in that run. A known quirk: "
                   "the placeholder can park on the last undelivered stop.")
    else:
        st.caption("Run a simulation in the **Simulate** tab to see the rival's path here.")

# ------------------------------------------------ LLM Dispatcher
with tab_llm:
    from dotenv import load_dotenv

    from oel.experiments.llm_eval import EVAL_MODELS, load_requests
    from oel.llm.agent import LLMClient, run_agent

    load_dotenv(ROOT / ".env")
    has_key = bool(os.getenv("GROQ_API_KEY"))
    requests = load_requests()
    options = [f"{r['id']}: {r['text']}" for r in requests] + ["Custom request..."]
    c1, c2 = st.columns([3, 1])
    choice = c1.selectbox("request", options, key="llm_choice")
    model = c2.selectbox("model", EVAL_MODELS, key="llm_model")
    custom = choice == "Custom request..."
    text = c1.text_area("your request", key="llm_text") if custom else choice.split(": ", 1)[1]
    validation = c2.checkbox("validation layer", value=True, key="llm_val")
    live = c2.checkbox("live mode (calls Groq)", value=False, key="llm_live", disabled=not has_key,
                       help=None if has_key else "No GROQ_API_KEY in .env: cached replies only.")
    if custom and not live:
        st.caption("Custom requests need live mode (only the 20 benchmark requests are cached).")
    if st.button("Run the dispatcher", key="llm_btn", type="primary", disabled=custom and not (live and text)):
        rid = "ui_custom" if custom else choice.split(":")[0]
        run_cfg = dataclasses.replace(cfg, llm_model=model, llm_live=live)
        with st.spinner("Running the agent (cached replies are instant; a new plan can take ~30 s)..."):
            st.session_state["llm_run"] = run_agent(run_cfg, rid, text, LLMClient(run_cfg), validation)
    run = st.session_state.get("llm_run")
    if run:
        if run["error"]:
            msg = run["error"]
            if msg.startswith("cache_miss"):
                st.warning("This conversation is not in the cache (different settings or request). "
                           "Turn on live mode to call Groq.")
            else:
                st.error(msg[:300])
        st.markdown(f"**Answer:** {run['final_text'] or '(none)'}")
        st.write(f"Result: `{run['result']}`, tool calls: {run['tool_calls']}")
        if run["result"]["kind"] == "plan":
            r = plans.load_plan(run["result"]["plan_id"])
            if r and r["feasible"]:
                fig = views.base_map(cfg, "terrain", title=f"LLM's plan {r['plan_id']} (cost {r['cost']:.0f})")
                views.add_path(fig, [s[:2] for s in r["path"]], "route")
                st.plotly_chart(fig, width="stretch")
        st.markdown("**Trace (Thought = Reason, Action = Act, Observation = Sense)**")
        for k, step in enumerate(run["steps"], 1):
            title = step["action"]["tool"] if step.get("action") else "final answer"
            with st.expander(f"step {k}: {title}"):
                if step.get("thought"):
                    st.markdown(f"**Thought:** {step['thought']}")
                if step.get("action"):
                    st.markdown(f"**Action:** `{step['action']['tool']}` (validation: {step.get('validation')})")
                    st.json(step["action"]["arguments"])
                    st.markdown("**Observation:**")
                    st.json(step["observation"])
                if step.get("answer"):
                    st.markdown(f"**Answer:** {step['answer']}")

# ------------------------------------------------ Experiments
with tab_exp:
    st.caption("Every stamped table and figure in results/, as produced by `python run_all.py`.")
    groups = {
        "World, hills and twists": ["instance_map", "elevation_map"],
        "Pipeline demo: UCS plan + simulator": ["standin_"],
        "Fuel reserve experiment": ["fuel_reserve"],
        "Part D: LLM dispatcher": ["llm_eval"],
        "Part D: validator fault injection": ["validator_fault"],
    }
    figs = sorted((ROOT / "results" / "figures").glob("*.png"))
    tables = sorted((ROOT / "results" / "tables").glob("*.csv"))
    used = set()
    for title, prefixes in list(groups.items()) + [("Other", None)]:
        mine_f = [f for f in figs if (prefixes is None and f not in used) or
                  (prefixes and any(f.name.startswith(p) for p in prefixes))]
        mine_t = [t for t in tables if (prefixes is None and t not in used) or
                  (prefixes and any(t.name.startswith(p) for p in prefixes))]
        used |= set(mine_f) | set(mine_t)
        if not mine_f and not mine_t:
            continue
        st.subheader(title)
        for f in mine_f:
            st.image(str(f), caption=f.name, width="stretch")
        for t in mine_t:
            with st.expander(t.name):
                st.dataframe(pd.read_csv(t, comment="#"), width="stretch")
