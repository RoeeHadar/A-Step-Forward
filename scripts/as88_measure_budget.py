"""AS-88: measure runtime BUDGET values and count agents whose LLM call sends max_tokens=None.
Instrumented mock: a fake OpenAI-style client captures the real params dict built by LLM.complete."""
import asyncio, importlib, pathlib, sys, types
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "packages/schemas"), str(R / "packages/agents")]
from agents.base.llm import LLM, LLMRequest
captured = []
class FakeCompletions:
    async def create(self, **params):
        captured.append(params); raise RuntimeError("captured")
class FakeClient: chat = types.SimpleNamespace(completions=FakeCompletions())
class S:  # minimal settings with a dummy (non-secret) key flag
    def __getattr__(self, k): return {"resolved_api_key": "dummy"}.get(k, 0)
none = 0; rows = []
for bp in sorted((R / "packages/agents/agents").glob("*/*/budget.py")):
    pkg = ".".join(bp.relative_to(R / "packages/agents").with_suffix("").parts[:-1])
    B = importlib.import_module(pkg + ".budget").BUDGET
    try: am = importlib.import_module(pkg + ".agent")
    except ModuleNotFoundError: am = None
    cls = next((v for v in vars(am).values() if isinstance(v, type) and getattr(v, "budget", None) is B), None) if am else None
    expr = cls.budget.max_output_tokens if cls else None  # the exact expression agents pass
    llm = LLM(model="m", settings=S(), client=FakeClient())
    llm._call_with_retry = lambda fn, label: fn()
    n = len(captured)
    try: asyncio.run(llm.complete(LLMRequest(system="s", messages=[{"role": "user", "content": "q"}], max_output_tokens=expr)))
    except Exception: pass
    mt = captured[n]["max_tokens"] if len(captured) > n else "NOCALL"
    sends = cls is not None and "self.budget.max_output_tokens" in pathlib.Path(am.__file__).read_text()
    if sends and mt is None: none += 1
    rows.append((pkg.split(".")[-1], (cls.__name__ if cls else "-") + ("" if sends else "(no budget->LLM call)"), B.max_output_tokens, B.max_latency_ms, mt))
for r in rows: print("agent=%-22s class=%-24s BUDGET.max_output_tokens=%s max_latency_ms=%s -> sent max_tokens=%s" % r)
print(f"agents_with_llm_call={sum(1 for r in rows if 'no budget' not in r[1])} sending_max_tokens_None={none}")
