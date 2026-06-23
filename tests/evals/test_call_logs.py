"""Call log eval scenarios."""

import asyncio

import pytest

from tests.evals.conftest import _recreate_llm, run_and_judge
from tests.evals.scenarios import CALL_LOG_SCENARIOS


@pytest.mark.evals
def test_call_logs(agent_graph, judge_client):
    async def _run():
        _recreate_llm()
        sem = asyncio.Semaphore(3)
        async def _limited(s):
            async with sem:
                return await run_and_judge(agent_graph, judge_client, s)
        return await asyncio.gather(*[_limited(s) for s in CALL_LOG_SCENARIOS])

    results = asyncio.run(_run())
    failures = [r for r in results if not r["pass"]]
    if failures:
        details = "\n".join(
            f"  {r['scenario_id']}: {r['judge_result'].get('overall_reasoning', 'no reasoning')}"
            for r in failures
        )
        pytest.fail(f"{len(failures)}/{len(results)} call log scenarios failed:\n{details}")
