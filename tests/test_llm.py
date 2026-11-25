"""Part D: constraints, verify_plan, plan cache, validator, agent loop. NO API calls."""
import json

import pytest

from oel.config import TERRAINS, parse_cli
from oel.llm import agent, plans, validator
from oel.search.uninformed import ucs
from oel.world.constraints import PlanConstraints, verify_plan
from oel.world.problem import DeliveryProblem

# all stops near the depot + no fuel limit: plans in well under a second. Chosen so that the
# cheapest plan crosses mud but a mud-free detour exists (on the real map, avoiding mud cuts
# the depot off from stops 0-3).
SMALL = ["--stop", "0=5,5", "--stop", "1=4,1", "--stop", "2=8,3", "--stop", "3=9,4", "--stop", "4=2,2",
         "--no-fuel"]


@pytest.fixture
def cfg():
    return parse_cli(SMALL)


@pytest.fixture
def tmp_caches(tmp_path, monkeypatch):
    monkeypatch.setattr(plans, "PLAN_DIR", tmp_path / "plans")
    monkeypatch.setattr(plans, "SIM_DIR", tmp_path / "sims")
    monkeypatch.setattr(agent, "RESPONSE_DIR", tmp_path / "responses")
    return tmp_path


def _plan(cfg, **kw):
    problem = DeliveryProblem(cfg, constraints=PlanConstraints.build(**kw))
    return problem, ucs(problem)


def _delivery_order(problem, path):
    order = []
    for a, b in zip(path, path[1:]):
        order += problem.delivered(b[2] & ~a[2])
    return order


# ---------------------------------------------------------------- constraints in the planner
def test_unconstrained_is_unchanged(cfg):
    a = ucs(DeliveryProblem(cfg))
    b = ucs(DeliveryProblem(cfg, constraints=PlanConstraints()))
    assert a.cost == b.cost and a.actions == b.actions


def test_avoid_mud_has_no_mud(cfg):
    mud = TERRAINS.index("mud")
    problem0, plain = _plan(cfg)
    assert any(cfg.grid[s[:2]] == mud for s in plain.path[1:]), "test needs a plan that uses mud"
    problem, res = _plan(cfg, avoid_terrain=["mud"])
    assert res.solved
    assert not any(cfg.grid[s[:2]] == mud for s in res.path[1:])
    assert res.cost >= plain.cost
    assert verify_plan(res.actions, PlanConstraints.build(avoid_terrain=["mud"]), cfg) == []


def test_stop_order_delivers_stop_3_first(cfg):
    problem, res = _plan(cfg, stop_order=[3])
    assert res.solved
    assert _delivery_order(problem, res.path)[0] == 3
    assert verify_plan(res.actions, PlanConstraints.build(stop_order=[3]), cfg) == []


def test_verify_plan_catches_wrong_order(cfg):
    problem, res = _plan(cfg)
    first = _delivery_order(problem, res.path)[0]
    other = next(i for i in range(5) if i != first)
    # the unconstrained plan visits `other` after `first`; demanding `other` first must fail
    assert verify_plan(res.actions, PlanConstraints.build(stop_order=[other, first]), cfg) or \
        verify_plan(res.actions, PlanConstraints.build(stop_order=[other]), cfg)


def test_verify_plan_catches_avoided_cell_tunnel_and_cost(cfg):
    problem, res = _plan(cfg)
    some_cell = list(res.path[3][:2])
    assert verify_plan(res.actions, PlanConstraints.build(avoid_cells=[some_cell]), cfg)
    assert verify_plan(res.actions, PlanConstraints.build(max_cost=res.cost - 1), cfg)
    if "TUNNEL" in res.actions:
        assert verify_plan(res.actions, PlanConstraints.build(use_tunnels=False), cfg)


def test_stop_on_avoided_cell_is_infeasible(cfg, tmp_caches):
    rec = plans.plan(cfg, PlanConstraints.build(avoid_cells=[list(cfg.stops[0])]))
    assert not rec["feasible"] and "stop" in rec["reason"]


# ---------------------------------------------------------------- caches
def test_plan_cache_returns_identical_results(cfg, tmp_caches):
    c = PlanConstraints.build(stop_order=[3], avoid_terrain=["mud"])
    first = plans.plan(cfg, c)
    second = plans.plan(cfg, c)
    assert first["from_cache"] is False and second["from_cache"] is True
    assert first["plan_id"] == second["plan_id"] and first["actions"] == second["actions"]
    # the same request written differently (defaults spelled out) hits the same cache entry
    same = PlanConstraints.build(stop_order=[3], avoid_terrain=["mud"], use_tunnels=True)
    assert plans.plan_key(cfg, same, "ucs") == first["plan_id"]


def test_llm_cache_replays_without_api(tmp_caches):
    cfg = parse_cli([])            # llm_live is False: no API call is ever made
    client = agent.LLMClient(cfg)
    messages = [{"role": "user", "content": "hi"}]
    with pytest.raises(agent.CacheMiss):
        client.chat(messages, [])
    reply = {"content": "hello", "reasoning": "", "tool_calls": [], "finish_reason": "stop", "usage": {}}
    agent.RESPONSE_DIR.mkdir(parents=True)
    (agent.RESPONSE_DIR / f"{client._key(messages, [])}.json").write_text(json.dumps(reply))
    assert client.chat(messages, []) == reply == client.chat(messages, [])


# ---------------------------------------------------------------- validator
def test_validator_rejects_bad_arguments():
    cfg = parse_cli([])
    blocked = [int(x) for x in next(zip(*(cfg.grid == -1).nonzero()))]
    bad = [
        {"algorithm": "ucs", "stop_order": [7]},          # stop does not exist
        {"algorithm": "ucs", "avoid_cells": [blocked]},   # already a wall
        {"algorithm": "dijkstra9000"},                    # unknown algorithm
        {"algorithm": "ucs", "avoid_terrain": ["lava"]},  # unknown terrain
        {"algorithm": "ucs", "stop_order": [1, 1]},       # duplicate
        {"algorithm": "ucs", "avoid_cells": [[50, 3]]},   # off the grid
        {"algorithm": "ucs", "colour": "red"},            # invented argument name
        {"algorithm": "ucs", "fuel_reserve": 500},        # out of range
    ]
    for args in bad:
        clean, error = validator.validate(cfg, "plan_route", args)
        assert clean is None and error, args
    clean, error = validator.validate(cfg, "plan_route", {"algorithm": "ucs", "stop_order": [3]})
    assert error is None and clean == {"algorithm": "ucs", "stop_order": [3]}
    assert validator.validate(cfg, "simulate", {"plan_id": "nope"})[1]


# ---------------------------------------------------------------- the agent loop (scripted LLM)
class ScriptedClient:
    """Stands in for Groq: returns pre-written replies in order."""
    api_failures = 0

    def __init__(self, replies):
        self.replies = list(replies)

    def chat(self, messages, tool_schemas):
        return self.replies.pop(0)


def _call(name, args, cid="c1"):
    return {"content": "", "reasoning": f"I should call {name}", "finish_reason": "tool_calls",
            "usage": {}, "tool_calls": [{"id": cid, "name": name, "arguments": json.dumps(args)}]}


def _answer(text):
    return {"content": text, "reasoning": "done", "tool_calls": [], "finish_reason": "stop", "usage": {}}


def test_agent_validation_rejects_then_model_fixes(cfg, tmp_caches):
    replies = [_call("plan_route", {"algorithm": "ucs", "stop_order": [7]}, "c1"),
               _answer("Stop 7 does not exist.\nRESULT: invalid")]
    run = agent.run_agent(cfg, "T1", "deliver stop 7 first", ScriptedClient(replies), validation=True)
    assert run["steps"][0]["validation"] == "rejected"
    assert "does not exist" in run["steps"][0]["observation"]["error"]
    assert run["result"] == {"kind": "invalid", "plan_id": None}


def test_agent_without_validation_crashes_tool_but_survives(cfg, tmp_caches):
    replies = [_call("plan_route", {"algorithm": "ucs", "avoid_terrain": ["lava"]}),
               _answer("Something went wrong.\nRESULT: infeasible")]
    run = agent.run_agent(cfg, "T2", "avoid lava", ScriptedClient(replies), validation=False)
    assert "tool crashed" in run["steps"][0]["observation"]["error"]
    assert run["result"]["kind"] == "infeasible"


def test_agent_plans_and_reports_plan_id(cfg, tmp_caches):
    replies = [_call("plan_route", {"algorithm": "ucs", "stop_order": [3]})]
    client = ScriptedClient(replies)
    run = None

    def finish(messages, tool_schemas):
        obs = json.loads(messages[-1]["content"])
        return _answer(f"Planned.\nRESULT: plan_id={obs['plan_id']}")
    client.replies.append(None)
    original = client.chat

    def chat(messages, tool_schemas):
        reply = original(messages, tool_schemas)
        return reply if reply is not None else finish(messages, tool_schemas)
    client.chat = chat
    run = agent.run_agent(cfg, "T3", "stop 3 first", client, validation=True)
    rec = plans.load_plan(run["result"]["plan_id"])
    assert rec and rec["feasible"] and rec["delivery_order"][0] == 3


def test_parse_result():
    assert agent.parse_result("ok\nRESULT: plan_id=ab12cd34ef56") == {"kind": "plan", "plan_id": "ab12cd34ef56"}
    assert agent.parse_result("RESULT: Infeasible")["kind"] == "infeasible"
    assert agent.parse_result("no result line")["kind"] == "none"


def test_validator_flags_contradiction_as_infeasible():
    """A3: avoiding the cell of a stop that must be delivered is a contradiction -> the
    validator says 'infeasible' (not 'invalid') before any search is run."""
    cfg = parse_cli([])
    stop0 = list(cfg.stops[0])
    clean, error = validator.validate(cfg, "plan_route", {"algorithm": "ucs", "avoid_cells": [stop0]})
    assert clean is None
    assert error.startswith("infeasible request") and "stop 0" in error
    assert "invalid" not in error.split(":")[0]
    # the same check for an avoided terrain that a stop stands on (stop 1 is on grass)
    clean, error = validator.validate(cfg, "plan_route", {"algorithm": "ucs", "avoid_terrain": ["grass"]})
    assert clean is None and error.startswith("infeasible request") and "stop 1" in error


def test_validator_catches_every_injected_fault():
    """Fault injection, validator side only (no planning): every corruption type is caught."""
    from oel.experiments import validator_fault_injection as fi
    cfg = parse_cli([])
    for gold in ({"algorithm": "ucs"}, {"algorithm": "ucs", "stop_order": [2, 0], "avoid_terrain": ["ford"]}):
        assert validator.validate(cfg, "plan_route", gold)[1] is None
        for fault in fi.FAULTS:
            bad = fi.corrupt(fault, gold, cfg)
            clean, error = validator.validate(cfg, "plan_route", bad)
            assert clean is None and error, (fault, bad)


def test_recorded_api_failure_replays_and_is_not_graded(cfg, tmp_caches):
    """A permanent API error (e.g. 413 over the tokens-per-minute limit) is cached, replays as
    an API failure, and the run is reported as api_failure, not as an LLM mistake."""
    client = agent.LLMClient(parse_cli([]))
    messages = [{"role": "system", "content": agent.SYSTEM_PROMPT}, {"role": "user", "content": "x"}]
    from oel.llm import tools as llm_tools
    agent.RESPONSE_DIR.mkdir(parents=True)
    key = client._key(messages, llm_tools.TOOL_SCHEMAS)
    (agent.RESPONSE_DIR / f"{key}.json").write_text(json.dumps({"api_error": "APIStatusError: 413 TPM"}))
    run = agent.run_agent(cfg, "T9", "x", client, validation=True)
    assert run["error"].startswith("api_failure") and run["result"]["kind"] == "none"
