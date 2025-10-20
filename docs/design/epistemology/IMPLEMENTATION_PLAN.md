# IMPLEMENTATION_PLAN.md

*Operationalizing Epistemic Governance in GDAL-MCP*

## Goals

* Add **epistemic preflight** to risky geospatial ops (CRS, Resampling, Hydrology Conditioning, Aggregation).
* Produce and validate a **Justification Object** (schema-backed) when escalation is needed.
* **Proceed / warn / block** tool calls based on the presence & freshness of justification.
* Persist justifications as **portable capsules** (disk first; memory MCP later).
* Emit **receipts** for observability and education.

---

## FastMCP Prompts (Pt. 1)

## 1) Keep the global (agent) prompt thin

Use a tiny, stable SYSTEM prompt that sets *governance intent*—not methods:

* “Use epistemic preflight before risky geo ops.”
* “If escalation triggers, produce a justification object per schema.”
* “Prefer property-first choices (what is preserved) to algorithm labels.”

No AGENTS.md bloat; point to docs by *path*, not content.

```txt
SYSTEM (very short)
- You are an epistemically governed geospatial agent.
- Before risky ops (CRS/Datum, Resampling, Hydrology conditioning, Aggregation), run the epistemic preflight and produce a justification object if needed (see schema).
- Choose methods by what property they preserve, not by habit.
- Keep justifications concise; include uncertainty & conditions for revisit.
```

---

## 2) Use **tool-level prompt decorators** for preflight (ideal)

Attach a preflight prompt to each *risky* tool. This keeps reasoning *local* to the operation and avoids long context windows.

**Pattern** (pseudo-fastMCP):

```python
# tools/gdal_reproject.py
from fastmcp import prompt
from mcp.risk.classes import classify, RiskClass
from mcp.epistemic.preflight import build_preflight_prompt
from mcp.epistemic.schema import EpistemicJustification
from mcp.epistemic.store import DiskStore
from mcp.risk.hashing import input_hash
STORE = DiskStore()

@prompt(lambda tool, args: build_preflight_prompt(tool, args))
def reproject(dataset_path: str, src_crs: str, dst_crs: str, **kwargs):
    tool = "gdal.reproject"
    args = locals()

    risk = classify(tool, args)
    ih = input_hash(risk, tool, args)

    # If decorator ran and returned JSON, fastMCP exposes it here:
    preflight = getattr(reproject, "prompt_result", None)

    if risk is RiskClass.NONE or (preflight and preflight.get("needs_escalation") is False):
        return _run_gdal_reproject(dataset_path, src_crs, dst_crs, **kwargs)

    if preflight and preflight.get("needs_escalation"):
        just = EpistemicJustification(**preflight["justification"]).dict()
        STORE.put(ih, just)

    return _run_gdal_reproject(dataset_path, src_crs, dst_crs, **kwargs)
```

**Why this is ideal**

* Scopes reasoning to the *exact* call (arguments visible as `{args}`).
* Lets you iterate per-tool preflights independently.
* Keeps your global agent prompt small and stable.

---

## 3) Centralize the **preflight prompt builder** (one template)

Keep the prompt template in code (or load from `docs/design/epistemology/`), and render with `tool` + `args`.

```python
# mcp/epistemic/preflight.py
EP_PREPROMPT = """Epistemic preflight.
Operation: {tool}
Args: {args}

1) Does this call hit an epistemic risk class? (CRS/Datum, Resampling, Hydrology Conditioning, Aggregation)
2) If NO and you are confident → return: {{"needs_escalation": false}}
3) If YES or uncertain → answer the class’s question block briefly and produce
   an `epistemic_justification` object matching the schema (≤ 250 lines).
Return strictly JSON:
{{ "needs_escalation": true|false, "risk_class": "<class>", "justification": {{...}} }}
"""

def build_preflight_prompt(tool, args):
    return EP_PREPROMPT.format(tool=tool, args=args)
```

This one template covers all four classes because the **question blocks live in the docs** and the model knows which set to use once it classifies the risk.

---

## 4) Add **class-specific nudges** with minimal few-shot (optional)

For stubborn cases (e.g., DEM reprojection), add a *tiny* in-prompt nudge keyed by risk class to reinforce property-first choices:

```python
NUDGES = {
  "crs_datum_justification": "Hydrology relies on local geometry fidelity; prefer projections preserving local distance/shape for drainage realism. Surface justification > cartographic convenience.",
  "resampling_justification": "Frame methods by preservation property: classification-fidelity, gradient-preserving, smoothness-prior. Terrain hydrology usually disfavours smoothing.",
  "hydrology_conditioning_justification": "Name methods by intent: preserve depression realism / restore surface continuity / enforce drainage connectivity.",
  "aggregation_justification": "Choose by interpretation goal: central tendency, dominant behavior, peak condition. Hydrology often values tails over means."
}
```

You can append the nudge to the preflight prompt *only* when that class is detected—keeping token use minimal.

---

## 5) Optional: a **validation prompt** pass (post-preflight, pre-exec)

If you want an extra safeguard, add a second decorator or inline check that *validates* the produced justification against the tool args:

```python
VALIDATOR = """Validate justification vs call.
Tool: {tool}
Args: {args}
Justification: {just}

- Is the chosen method consistent with the stated intent and assumptions? (yes/no)
- Any red flags? (list, brief)
Return JSON: {{"ok": true|false, "notes":[...]}}
"""
```

Use only for truly critical paths (DEM→hydrology).

---

## 6) Keep **model contracts** strict (JSON-only)

In your decorator, **insist** on strict JSON returns and validate with Pydantic. If the model drifts, reject gently and ask it to retry “JSON only”.

* Prevents downstream parsing pain.
* Keeps agents deterministic without over-constraining content.

---

## 7) Where to put the docs in prompts: **don’t inline—link**

* Do **not** paste large doc content into prompts.
* Include **paths** to `docs/design/epistemology/...` so the model can reference the *idea* without spending tokens.
* If you need a small refresher, paste *only* the **question block** (a dozen lines) for the class.

---

## 8) How this plays with **fastMCP routing**

* Keep your tool catalog normal; don’t “hide tools”.
* The preflight prompt runs immediately before the tool body; it can return `needs_escalation=false` quickly for low-risk calls (cheap).
* For high-risk, it emits the justification JSON that your handler caches and associates with an input hash (so repeated calls don’t re-prompt).

---

## 9) Minimal **error/bounce path** (if you prefer middleware)

If you wrap tools with a middleware rather than a decorator, return a structured bounce that your agent (still in fastMCP) can handle by *automatically* calling a generic `epistemic.justify` tool (if you create it) or by **re-invoking the same tool** with the decorator prompt to collect the justification. Both shapes are fine; decorators are simpler.

---

## 10) Prompt hygiene (what *not* to do)

* Don’t embed long methodology prose in the decorator—use the **question prompts** and **nudge** lines only.
* Don’t add “always use X” language—keep choices property-first, not tool-first.
* Don’t couple justifications to a specific model—store them as small JSON capsules your agent can reuse across models.

---

# Quick starter: two decorators you can copy

### A) One-shot preflight (recommended default)

```python
@prompt(lambda tool, args: build_preflight_prompt(tool, args))
def risky_tool(...):
    pre = getattr(risky_tool, "prompt_result", None) or {}
    if pre.get("needs_escalation"):
        just = EpistemicJustification(**pre["justification"]).dict()
        STORE.put(input_hash(...), just)
    return _run(...)
```

### B) Two-phase (preflight + validation) for DEM→hydrology

```python
@prompt(lambda tool, args: build_preflight_prompt(tool, args))
def hydro_flow(...):
    pre = getattr(hydro_flow, "prompt_result", None) or {}
    if pre.get("needs_escalation"):
        just = EpistemicJustification(**pre["justification"]).dict()
        STORE.put(input_hash(...), just)

    # Optional validation pass
    @prompt(lambda tool, args, just=just: VALIDATOR.format(tool=tool, args=args, just=just))
    def _validated(): return {}
    val = getattr(_validated, "prompt_result", {"ok": True})

    if not val.get("ok", True):
        return {"error": "epistemic_validation_failed", "notes": val.get("notes", [])}

    return _run_hydrology(...)
```

---

## FAQ (fast)

**Q: Won’t this add latency?**
A: Only on first high-risk calls. You’ll cache justifications by input hash and skip future prompts. Low-risk ops shortcut with `needs_escalation:false`.

**Q: Where do I keep few-shots?**
A: Avoid long few-shots. If you need them, keep 1–2 ultra-short *property-first* exemplars per class in code, injected *only* when that class is detected.

**Q: Can I evolve this into a dedicated Epistemology MCP later?**
A: Yes. Your decorator/middleware already defines a clean seam (`preflight → justification → validate`) that can be replaced by calls to an Epistemology MCP with the same IO.

---

## TL;DR

* fastMCP’s prompt decorator is the right “thin edge” for invoking epistemic preflight.
* Keep a **single, short preflight template**; add tiny class-specific nudges.
* Validate to **strict JSON** via Pydantic.
* **Cache** by input hash; **persist** to `.epistemic/justifications/…`.
* Add an **optional validation decorator** for truly critical flows.

This gives us an *agentic epistemology* with minimal surface area and maximum portability—without turning your agent into a rule-maze or inflating your context window.


---



## 0) Repo layout (proposed)

```
docs/
  design/
    epistemology/
      AGENT_EPISTEMOLOGY.md
      EPISTEMIC_RISK_CLASSES.md
      EPISTEMIC_JUSTIFICATION_SCHEMA.md
      methodology/
        CRS_JUSTIFICATION.md
        RESAMPLING_JUSTIFICATION.md
        HYDROLOGY_CONDITIONING_JUSTIFICATION.md
        AGGREGATION_JUSTIFICATION.md
mcp/
  __init__.py
  config.py
  risk/
    __init__.py
    category.py           # risk class mapping
    hashing.py           # stable input hashing per class
  epistemology/
    __init__.py
    schema.py            # Pydantic models / JSON Schema
    preflight.py         # prompt builder + result parser
    middleware.py        # requires_epistemic_justification bounce
    store.py             # DiskStore + interface
    receipts.py          # machine-readable receipts
tests/
  test_epistemic_*.py
```

---

## 1) Risk classes & routing

Map tool invocations → risk class.

```python
# mcp/risk/classes.py
from enum import Enum, auto
class RiskClass(Enum):
    NONE = auto()
    CRS_DATUM = auto()
    RESAMPLING = auto()
    HYDROLOGY = auto()
    AGGREGATION = auto()

def classify(tool_name: str, args: dict) -> RiskClass:
    t = tool_name.lower()
    if "reproject" in t or "warp" in t:
        return RiskClass.CRS_DATUM
    if "resample" in t or args.get("resampleAlg"):
        return RiskClass.RESAMPLING
    if any(k in args for k in ["fill_sinks", "breach", "flowdir", "flowacc"]):
        return RiskClass.HYDROLOGY
    if any(k in args for k in ["zonal", "aggregate", "stats"]):
        return RiskClass.AGGREGATION
    return RiskClass.NONE
```

---

## 2) Stable input hashing

Hash only fields that affect epistemic validity.

```python
# mcp/risk/hashing.py
import hashlib, json
from .classes import RiskClass

def _normalize(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def input_hash(risk: RiskClass, tool: str, args: dict) -> str:
    # keep only relevant keys per class (expand as needed)
    keep = {
        RiskClass.CRS_DATUM: ["src_crs","dst_crs","has_vertical","area_extent"],
        RiskClass.RESAMPLING: ["kernel","src_res","dst_res","purpose","roi"],
        RiskClass.HYDROLOGY: ["op","thresholds","roi","conditioning_mode"],
        RiskClass.AGGREGATION: ["stat","zone_layer","target","purpose","roi"],
    }.get(risk, [])
    payload = {k: args.get(k) for k in keep}
    payload["tool"] = tool
    h = hashlib.sha256(_normalize(payload).encode()).hexdigest()
    return f"sha256:{h}"
```

---

## 3) Epistemic schema (Pydantic + JSON Schema)

Keep it portable and enforce size discipline.

```python
# mcp/epistemic/schema.py
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional

Confidence = Literal["low","medium","medium-high","high"]

class JustificationIntent(BaseModel):
    description: str
    context: Optional[str] = None

class Assumptions(BaseModel):
    known: List[str] = []
    uncertain: List[str] = []
    dependencies: List[str] = []

class Rejected(BaseModel):
    method: str
    reason: str

class CandidateMethods(BaseModel):
    considered: List[str] = []
    rejected: List[Rejected] = []

class SelectedMethod(BaseModel):
    name: str
    rationale: str
    tradeoffs: Optional[str] = None

class EpistemicStatus(BaseModel):
    confidence_level: Confidence
    residual_uncertainty_sources: List[str] = []
    conditions_for_revisit: List[str] = []

class EpistemicJustification(BaseModel):
    domain: str
    intent: JustificationIntent
    assumptions: Assumptions
    candidate_methods: CandidateMethods
    selected_method: SelectedMethod
    epistemic_status: EpistemicStatus

    @validator("domain")
    def domain_prefix(cls, v):
        assert v.endswith("_justification"), "domain must end with _justification"
        return v
```

Generate JSON Schema (optional) for validation in other languages:

```python
# e.g., in setup or runtime
JSON_SCHEMA = EpistemicJustification.schema_json(indent=2)
```

---

## 4) Disk store (Tier-1 persistence)

Ephemeral → on-disk capsules with index; pluggable later.

```python
# mcp/epistemic/store.py
from pathlib import Path
import json, time
from typing import Optional
from ..risk.classes import RiskClass
from .schema import EpistemicJustification

class EpistemicStore:
    def get(self, key: str) -> Optional[dict]: ...
    def put(self, key: str, value: dict) -> None: ...

class DiskStore(EpistemicStore):
    def __init__(self, root=".epistemic/justifications"):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "index.json").touch(exist_ok=True)

    def _path(self, risk: RiskClass, key: str) -> Path:
        return self.root / risk.name.lower() / f"{key}.json"

    def get(self, key_path: str) -> Optional[dict]:
        p = Path(key_path)
        if p.exists():
            return json.loads(p.read_text())
        return None

    def put(self, key: str, value: dict) -> None:
        risk = value.get("domain","unknown").split("_justification")[0]
        dirp = self.root / risk
        dirp.mkdir(parents=True, exist_ok=True)
        p = dirp / f"{key}.json"
        value["_meta"] = dict(created_at=int(time.time()))
        p.write_text(json.dumps(value, indent=2))
```

---

## 5) Receipts (observability)

Emit with every risky call.

```python
# mcp/epistemic/receipts.py
def make_receipt(*, risk_class, input_hash, decision, justification_path=None, notes=None):
    return {
        "epistemic_receipt": {
            "risk_class": str(risk_class),
            "input_hash": input_hash,
            "decision": decision,       # "proceed" | "warn" | "blocked"
            "justification_ref": justification_path,
            "notes": notes or ""
        }
    }
```

---

## 6) Preflight prompt (fastMCP decorator)

One light prompt to trigger escalation + get the object back.

```python
# mcp/epistemic/preflight.py
EP_PREPROMPT = """Epistemic preflight.
You are about to perform a geospatial operation: {tool} with args {args}.
1) Identify if this call falls under a known epistemic risk class:
   - CRS/Datum, Resampling, Hydrology Conditioning, Aggregation.
2) If NO risk and you are confident, return: {{"needs_escalation": false}}.
3) If YES or uncertain, answer the class's question block succinctly and produce
   an `epistemic_justification` object matching the schema. Keep it concise.
Return strictly JSON:
{{ "needs_escalation": true|false, "risk_class": "...", "justification": {{...}} }}
"""

def build_preflight_prompt(tool, args):
    return EP_PREPROMPT.format(tool=tool, args=args)
```

Example decorator usage (pseudo-fastMCP):

```python
# mcp/tools/gdal_reproject.py
from ..risk.classes import classify, RiskClass
from ..risk.hashing import input_hash
from ..epistemic.preflight import build_preflight_prompt
from ..epistemic.schema import EpistemicJustification
from ..epistemic.store import DiskStore
from ..epistemic.receipts import make_receipt

STORE = DiskStore()

def reproject(dataset_path: str, src_crs: str, dst_crs: str, **kwargs):
    tool = "gdal.reproject"
    args = locals()
    risk = classify(tool, args)
    ih = input_hash(risk, tool, args)

    # Try load cached justification
    jpath = f".epistemic/justifications/{risk.name.lower()}/{ih}.json"
    cached = STORE.get(jpath)

    if risk is RiskClass.NONE:
        return {"ok": True, **make_receipt(risk_class=risk, input_hash=ih, decision="proceed")}

    if not cached:
        # ask model for justification (one-shot)
        prompt = build_preflight_prompt(tool, args)
        model_response = call_model(prompt)  # implement this with your LLM client
        if not model_response.get("needs_escalation"):
            return {"ok": True, **make_receipt(risk_class=risk, input_hash=ih, decision="proceed")}
        just = EpistemicJustification(**model_response["justification"]).dict()
        STORE.put(ih, just)
        cached = just

    # proceed with actual GDAL op (omitted)
    result = run_gdal_reproject(dataset_path, src_crs, dst_crs, **kwargs)

    return {
        "ok": True,
        "result": result,
        **make_receipt(
            risk_class=risk,
            input_hash=ih,
            decision="proceed",
            justification_path=jpath,
            notes=f"used justification domain={cached['domain']}"
        )
    }
```

---

## 7) Middleware bounce (optional, cleaner separation)

If you prefer a hard gate instead of inline prompt:

```python
# mcp/epistemic/middleware.py
from .store import DiskStore
from ..risk.classes import RiskClass
from ..risk.hashing import input_hash

STORE = DiskStore()

def require_justification(tool: str, args: dict, risk: RiskClass):
    if risk is RiskClass.NONE:
        return {"ok": True}
    ih = input_hash(risk, tool, args)
    jpath = f".epistemic/justifications/{risk.name.lower()}/{ih}.json"
    if STORE.get(jpath):
        return {"ok": True, "justification_path": jpath}
    return {
        "ok": False,
        "error": "requires_epistemic_justification",
        "risk_class": risk.name.lower(),
        "input_hash": ih,
        "schema_ref": "docs/design/epistemology/EPISTEMIC_JUSTIFICATION_SCHEMA.md",
        "methodology_ref": f"docs/design/epistemology/methodology/{_doc_for(risk)}",
    }

def _doc_for(risk: RiskClass) -> str:
    return {
        RiskClass.CRS_DATUM: "CRS_JUSTIFICATION.md",
        RiskClass.RESAMPLING: "RESAMPLING_JUSTIFICATION.md",
        RiskClass.HYDROLOGY: "HYDROLOGY_CONDITIONING_JUSTIFICATION.md",
        RiskClass.AGGREGATION: "AGGREGATION_JUSTIFICATION.md",
    }[risk]
```

Use it at the top of tool handlers; if it returns a bounce, ask the model to create the justification (then retry).

---

## 8) Policy (proceed / warn / block)

* **Proceed**: risk=NONE or justification present & fresh (hash match).
* **Warn**: justification present but *stale* (hash mismatch) → proceed but include `decision="warn"` and a note.
* **Block**: high-risk + no justification + tool classified as “critical” (e.g., DEM reprojection before hydrology). Keep this list short and explicit in `config.py`.

```python
# mcp/config.py
CRITICAL_TOOLS = {"gdal.reproject:DEM", "gdal.resample:DEM_before_slope"}
```

---

## 9) Testing plan

* **Unit**: schema validation, risk classification, hashing determinism.
* **Golden tests**: feed fixed prompts → ensure produced justification passes schema & size limit.
* **Integration**: run each risky tool across:

  * no-risk (pass through)
  * trigger → produce justification
  * cached justification → no prompt
  * stale justification → warn path
* **Doc links**: verify `methodology_ref` and `schema_ref` resolve locally.

---

## 10) Rollout steps

1. Land `risk/`, `epistemic/` modules and docs (no tool changes yet).
2. Wrap **one** tool (reproject) end-to-end; confirm UX & receipts.
3. Extend to resample, hydrology, aggregation.
4. Add **.epistemic/** to `.gitignore` (or opt-in commit policy).
5. Expose receipts in agent logs / UI for educational transparency.
6. (Optional) Add adapter interface for a future **Memory MCP**.

---

## 11) Non-goals / guardrails

* No giant always-on prompts.
* Don’t force justification for low-risk ops.
* Keep justification ≤ ~3KB; trim prose; prefer bullets.
* Preserve **agent agency**: methodology is scaffolding, not a script.

---

## 12) Future adapters (optional)

* `MemoryMCPStore(EpistemicStore)` to delegate `get/put/query` to a memory MCP.
* Bandit-style post-hoc learning on receipts (track which preservation choices correlate with downstream success).
