import os, time
from dataclasses import dataclass, field
from openai import OpenAI

LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://localhost:1234/v1")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "google/gemma-4-e4b")
LOCAL_API_KEY = os.getenv("LOCAL_API_KEY", "lm-studio")

@dataclass
class Result:
    backend: str
    model: str
    text: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    cost_usd: float
    extra: dict = field(default_factory=dict)

def call_local(prompt, system=None, **kw):
    client = OpenAI(base_url=LOCAL_BASE_URL, api_key=LOCAL_API_KEY)
    msgs = ([{"role": "system", "content": system}] if system else []) + \
        [{"role": "user", "content": prompt}]
    t0 = time.perf_counter()
    resp = client.chat.completions.create(model=LOCAL_MODEL, messages=msgs, **kw)
    latency = time.perf_counter() - t0

    u = resp.usage
    details = getattr(u, "completion_tokens_details", None)
    thinking = getattr(details, "reasoning_tokens", 0) or 0
    return Result("local", resp.model, resp.choices[0].message.content or "",
                  u.prompt_tokens, u.completion_tokens, latency, 0.0,
                  {"thinking_tokens": thinking})


import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "haiku")

async def _claude_async(prompt, system):
    opts = ClaudeAgentOptions(
        model=CLAUDE_MODEL,
        system_prompt=system,
        tools=[],
        max_turns=1,
        setting_sources=[],
        strict_mcp_config=True,
    )
    result = None
    async for msg in query(prompt=prompt, options=opts):
        if isinstance(msg, ResultMessage):
            result = msg
    return result

def call_claude(prompt, system=None, **kw):
    t0 = time.perf_counter()
    msg = asyncio.run(_claude_async(prompt, system))
    latency = time.perf_counter() - t0

    u = msg.usage or {}
    model_usage = getattr(msg, "model_usage", None) or {}
    model = next(iter(model_usage), CLAUDE_MODEL)
    cache_w = u.get("cache_creation_input_tokens", 0)
    cache_r = u.get("cache_read_input_tokens", 0)
    total_in = u.get("input_tokens", 0) + cache_w + cache_r
    thinking = (u.get("output_tokens_details") or {}).get("thinking_tokens", 0)
    return Result("claude", model, msg.result or "",
                  total_in, u.get("output_tokens", 0),
                  latency, msg.total_cost_usd or 0.0,
                  {"thinking_tokens": thinking,
                   "cache_write": cache_w, "cache_read": cache_r,
                   "session_usage": model_usage})

def call(backend, prompt, system=None, **kw):
    if backend == "local":
        return call_local(prompt, system, **kw)
    if backend == "claude":
        return call_claude(prompt, system)
    raise ValueError(backend)