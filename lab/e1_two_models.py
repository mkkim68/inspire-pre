import json, os
from lv0.backends import call

SYSTEM = "당신은 신입 개발자를 돕는 선배 엔지니어입니다. 한국어로 3문장 이내로 답합니다."
QUESTION = "LLM pipeline과 AI Agent의 차이를 신입 개발자에게 설명해 주세요."

rows = []
for backend in ("claude", "local"):
    r = call(backend, QUESTION, system=SYSTEM)
    rows.append(r)
    print(f"[{r.backend} · {r.model}]\n{r.text}\n")

print(f"{'backend':8} {'model':20} {'in':>5} {'out':>5} {'think':>6} "
      f"{'cache_r':>7} {'latency':>8} {'cost_usd':>10} {'chars':>6}")
for r in rows:
    print(f"{r.backend:8} {r.model:20} {r.input_tokens:>5} {r.output_tokens:>5} "
          f"{r.extra.get('thinking_tokens', 0):>6} {r.extra.get('cache_read', 0):>7} "
          f"{r.latency_s:>8.2f} {r.cost_usd:>10.6f} {len(r.text.strip()):>6}")

os.makedirs("outputs", exist_ok=True)
with open("outputs/e1.json", "w", encoding="utf-8") as f:
    json.dump([vars(r) for r in rows], f, ensure_ascii=False, indent=2, default=str)
print("\nsaved outputs/e1.json")