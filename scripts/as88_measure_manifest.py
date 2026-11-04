"""AS-88 r1: count agents whose LLM is constructed with model=None / fallback_model=None.
Instrumented: agents.base.agent.LLM and safety_moderation's LLM are replaced by a recorder; the real
Agent.__init__ (agent.py:73) and SafetyModerationAgent.__init__ (:45) run unchanged."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "packages/schemas"), str(R / "packages/agents")]
import agents.base.agent as base
import agents.system.safety_moderation.agent as sm
from agents import AGENT_REGISTRY
calls = []
class Rec:
    def __init__(self, model=None, fallback_model=None, **k): calls.append((model, fallback_model))
base.LLM = Rec; sm.LLM = Rec
class Probe(base.Agent):
    async def run(self, inp, ctx): ...
none = 0
for name, m in AGENT_REGISTRY.items():
    n = len(calls); Probe(manifest=m)
    mo, fb = calls[n]
    bad = mo is None or fb is None; none += bad
    ex = m.model_extra or {}
    print(f"{str(getattr(name,'value',name)):24} attr primary={mo!r:22} fallback={fb!r:14} | model_extra primary={ex.get('primary_model')!r} fallback={ex.get('fallback_model')!r} prompt_version={m.prompt_version!r}/{ex.get('prompt_version')!r}")
n = len(calls); sm.SafetyModerationAgent(); smo = calls[n]
print(f"safety_moderation.agent:45 LLM(model={smo[0]!r}, fallback_model={smo[1]!r})")
print(f"agents={len(AGENT_REGISTRY)} built_with_model_or_fallback_None={none} safety_none={int(None in smo)}")
