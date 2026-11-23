"""The LLM dispatcher: our own ReAct loop on top of Groq's native tool calling.

One request = a loop of
    Thought      the model's reasoning (gpt-oss returns it separately as `reasoning`)
    Action       ONE tool call (name + JSON arguments)
    Observation  the tool's result, or the validator's error message
until the model answers in text (with a final "RESULT: ..." line) or uses up
cfg.llm_max_tool_calls tool calls. Every run is saved as a trace in results/logs/llm_traces/.

LLM replies are cached on disk (oel/llm/cache/responses/), keyed by a hash of
(model, temperature, messages, tools). With temperature 0 and the cache committed, anyone can
replay the exact same runs without an API key; cfg.llm_live = True calls Groq on a cache miss.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

from oel.config import RESULTS_DIR
from oel.llm import tools, validator
from oel.stamp import get_logger, stamp

RESPONSE_DIR = Path(__file__).resolve().parent / "cache" / "responses"
TRACE_DIR = RESULTS_DIR / "logs" / "llm_traces"
MAX_RETRIES = 3
RESULT_RE = re.compile(r"RESULT:\s*(?:plan_id\s*=\s*([0-9a-f]{6,})|(infeasible|invalid))", re.IGNORECASE)

SYSTEM_PROMPT = """You are the dispatcher of a delivery robot in a 40x40 grid city. The robot starts \
at the depot and must deliver 5 parcels (stops 0-4). You do NOT plan routes yourself: you call \
tools, and our planner does the work.

Rules:
- Call get_instance_info first when the request depends on facts about the map (which stop is \
where, distances, terrain names, stations, tunnels). Never guess these facts.
- Call plan_route with ONLY the constraints the user actually asked for. Leave every other \
argument out (the defaults are correct). Use the algorithm the user names; if they name none, \
use "ucs".
- If the user asks about fuel, refuelling, regeneration or climbing along the route, call \
fuel_report on the plan. If they ask how the route would go in the real world, call simulate.
- If a tool returns an error, read it and fix your call, or decide the request is invalid.
- A request is INVALID if it refers to something that does not exist (e.g. a stop index \
outside 0-4, an unknown terrain or algorithm, a cell outside the grid). A request is \
INFEASIBLE if it is well-formed but no route can satisfy it (plan_route says infeasible, or \
the request contradicts itself).
- Answer briefly in plain words, then end with exactly one final line:
  RESULT: plan_id=<the plan id>    or    RESULT: infeasible    or    RESULT: invalid"""


class CacheMiss(Exception):
    """An LLM reply is not in the cache and live calls are off."""


class LLMError(Exception):
    """The model itself produced an unusable reply (e.g. a malformed tool call)."""


class LLMClient:
    """Groq chat completions with an on-disk cache and retry-with-backoff."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.log = get_logger("llm_api")
        self.api_failures = 0       # transient API errors (not LLM mistakes)
        self._client = None

    def _key(self, messages, tool_schemas) -> str:
        blob = json.dumps({"model": self.cfg.llm_model, "temperature": self.cfg.llm_temperature,
                           "messages": messages, "tools": tool_schemas}, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def chat(self, messages, tool_schemas) -> dict:
        key = self._key(messages, tool_schemas)
        path = RESPONSE_DIR / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if not self.cfg.llm_live:
            raise CacheMiss(f"LLM reply {key[:12]} not cached; rerun with --live")
        reply = self._call_api(messages, tool_schemas)
        RESPONSE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(reply, indent=1), encoding="utf-8")
        return reply

    def _call_api(self, messages, tool_schemas) -> dict:
        import groq
        from dotenv import load_dotenv

        if self._client is None:
            load_dotenv()
            self._client = groq.Groq(timeout=60)
        transient = (groq.APIConnectionError, groq.APITimeoutError, groq.RateLimitError,
                     groq.InternalServerError)
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = self._client.chat.completions.create(
                    model=self.cfg.llm_model, messages=messages, tools=tool_schemas,
                    tool_choice="auto", temperature=self.cfg.llm_temperature)
                break
            except transient as err:
                self.api_failures += 1
                self.log.warning("API failure (attempt %d/%d): %s: %s", attempt + 1,
                                 MAX_RETRIES + 1, type(err).__name__, str(err)[:200])
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(2 ** (attempt + 1))          # 2, 4, 8 s
            except groq.BadRequestError as err:
                # e.g. "tool_use_failed": the MODEL wrote a malformed tool call -> LLM mistake
                raise LLMError(str(err)[:300]) from None
        msg = resp.choices[0].message
        return {
            "content": msg.content or "",
            "reasoning": getattr(msg, "reasoning", None) or "",
            "tool_calls": [{"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments}
                           for tc in (msg.tool_calls or [])],
            "finish_reason": resp.choices[0].finish_reason,
            "usage": {"prompt": resp.usage.prompt_tokens, "completion": resp.usage.completion_tokens},
        }


def parse_result(text: str) -> dict:
    """The final 'RESULT: ...' line -> {"kind": "plan"/"infeasible"/"invalid"/"none", "plan_id"}."""
    matches = RESULT_RE.findall(text or "")
    if not matches:
        return {"kind": "none", "plan_id": None}
    plan_id, word = matches[-1]
    if plan_id:
        return {"kind": "plan", "plan_id": plan_id.lower()}
    return {"kind": word.lower(), "plan_id": None}


def run_agent(cfg, request_id: str, request_text: str, client: LLMClient, validation: bool) -> dict:
    """Answer one English request with the ReAct loop. Returns the run record (also saved
    as a trace)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request_text}]
    steps, tool_calls = [], 0
    run = {"request_id": request_id, "request": request_text, "model": cfg.llm_model,
           "validation": validation, "steps": steps, "final_text": "", "error": None}
    while True:
        try:
            reply = client.chat(messages, tools.TOOL_SCHEMAS)
        except LLMError as err:
            run["error"] = f"llm_error: {err}"
            break
        except CacheMiss as err:
            run["error"] = f"cache_miss: {err}"
            break
        except Exception as err:               # API still failing after the retries
            run["error"] = f"api_failure: {type(err).__name__}: {str(err)[:200]}"
            break

        if not reply["tool_calls"]:
            steps.append({"thought": reply["reasoning"], "action": None, "observation": None,
                          "answer": reply["content"]})
            run["final_text"] = reply["content"]
            break
        if tool_calls >= cfg.llm_max_tool_calls:
            run["error"] = f"stopped: more than {cfg.llm_max_tool_calls} tool calls"
            break

        messages.append({"role": "assistant", "content": reply["content"] or "",
                         "tool_calls": [{"id": tc["id"], "type": "function",
                                         "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                                        for tc in reply["tool_calls"]]})
        for i, tc in enumerate(reply["tool_calls"]):
            tool_calls += 1
            observation, status, args = _act(cfg, tc, validation)
            steps.append({"thought": reply["reasoning"] if i == 0 else "",
                          "action": {"tool": tc["name"], "arguments": args if args is not None else tc["arguments"]},
                          "validation": status, "observation": observation})
            messages.append({"role": "tool", "tool_call_id": tc["id"],
                             "content": json.dumps(observation)})

    run["tool_calls"] = tool_calls
    run["result"] = parse_result(run["final_text"])
    run["plan_calls"] = [s["action"]["arguments"] for s in steps
                         if s.get("action") and s["action"]["tool"] == "plan_route"
                         and isinstance(s["action"]["arguments"], dict)]
    save_trace(run, "llm_validation" if validation else "llm")
    return run


def _act(cfg, tool_call: dict, validation: bool):
    """Execute one tool call. Returns (observation, validation status, parsed args)."""
    try:
        args = json.loads(tool_call["arguments"] or "{}")
    except json.JSONDecodeError as err:
        return {"error": f"arguments are not valid JSON: {err}"}, "bad_json", None
    if validation:
        clean, problem = validator.validate(cfg, tool_call["name"], args)
        if problem:
            return {"error": problem, "note": "rejected by the validator, tool not run"}, "rejected", args
        args_to_run, status = clean, "ok"
    else:
        args_to_run, status = args, "off"
    try:
        return tools.execute(cfg, tool_call["name"], args_to_run), status, args
    except Exception as err:   # with validation OFF bad arguments can crash the tool
        return {"error": f"tool crashed: {type(err).__name__}: {err}"}, status + "_crash", args


def save_trace(run: dict, mode: str) -> Path:
    """Write the run as JSON + a readable Thought/Action/Observation markdown file."""
    folder = TRACE_DIR / mode
    folder.mkdir(parents=True, exist_ok=True)
    data = {"stamp": stamp(), **run}
    (folder / f"{run['request_id']}.json").write_text(json.dumps(data, indent=1, default=str), encoding="utf-8")
    lines = [f"_{stamp()}_", "", f"# {run['request_id']} ({mode}, {run['model']})", "",
             f"**Request:** {run['request']}", ""]
    for k, s in enumerate(run["steps"], 1):
        lines.append(f"## Step {k}")
        if s.get("thought"):
            lines.append(f"**Thought:** {s['thought'].strip()}")
        if s.get("action"):
            lines.append(f"**Action:** `{s['action']['tool']}({json.dumps(s['action']['arguments'])})`"
                         f" (validation: {s.get('validation')})")
            lines.append(f"**Observation:** `{_short(s['observation'])}`")
        if s.get("answer") is not None:
            lines.append(f"**Answer:** {s['answer'].strip()}")
        lines.append("")
    lines.append(f"**Result:** {run['result']}  |  tool calls: {run['tool_calls']}  |  error: {run['error']}")
    path = folder / f"{run['request_id']}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _short(obj, limit: int = 600) -> str:
    text = json.dumps(obj)
    return text if len(text) <= limit else text[:limit] + " ...(truncated)"
