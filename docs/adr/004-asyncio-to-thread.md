# ADR-004: asyncio.to_thread() over ProcessPoolExecutor for Expression Evaluation

## Status
Accepted

## Context
`evaluate_with_timeout()` in `eval.py` runs `safe_eval_expression()` -- a synchronous, CPU-bound
`eval()` call -- inside an async server. Two execution strategies were considered and one was
attempted in production:

**Attempt: ProcessPoolExecutor** (PR #141, reverted in PR #201)
A module-level `ProcessPoolExecutor(max_workers=1)` was introduced to provide true timeout
enforcement (OS-level process kill) and GIL-free CPU isolation. It was reverted because
FastMCP Cloud runs on AWS Lambda, where `sys.executable` is invalid and process spawning is
forbidden. The pool failed at import time on the deployment target.

**Current approach: asyncio.to_thread()**
```python
# eval.py
return await asyncio.wait_for(
    asyncio.to_thread(safe_eval_expression, expression),
    timeout=EXPRESSION_TIMEOUT_SECONDS,
)
```

`asyncio.to_thread()` offloads the synchronous call to the default `ThreadPoolExecutor`.
`asyncio.wait_for()` cancels the awaitable on timeout -- the caller unblocks -- but the
underlying thread continues until the `eval()` call returns naturally.

## Decision
Use `asyncio.to_thread()`. The deployment constraint (Lambda) is non-negotiable. The timeout
limitation is acceptable because:

1. The character whitelist (`eval.py`, line 49) and function whitelist (`settings.py`, line 65)
   eliminate expressions capable of infinite loops or unbounded computation before `eval()` runs.
2. `EXPRESSION_TIMEOUT_SECONDS` (default 5.0s, env-configurable) is a defense-in-depth backstop,
   not the primary security boundary.
3. `safe_eval_expression()` is a single `eval()` call; CPU time is negligible for any expression
   the whitelist admits.

The whitelist is the security layer. The timeout is the safety net.

## Consequences

**Gained:**
- Compatible with Lambda and any serverless runtime (no process spawning)
- No module-level state; no shutdown handler required
- Clean async integration; no `concurrent.futures` imports

**Accepted:**
- `asyncio.wait_for()` does not kill the thread on timeout; the thread runs to completion
  after the caller receives `TimeoutError`. This is a known Python limitation with threads.
- True CPU isolation (separate memory space) is not achieved; the whitelist compensates.
