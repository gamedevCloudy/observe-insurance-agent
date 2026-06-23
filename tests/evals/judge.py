"""LLM-as-judge evaluation for agent scenarios."""

import asyncio
import json
import re

JUDGE_PROMPT = """You are an evaluator assessing an AI insurance claims support agent for Observe Insurance.
Your job is to determine if the agent correctly handled a customer interaction scenario.

## SCENARIO
{description}

## USER MESSAGES (what the customer said)
{user_messages}

## AGENT RESPONSE (final text output)
{agent_response}

## TOOL CALLS MADE (names + results)
{tool_calls}

## EVALUATION CRITERIA
{criteria}

For each criterion, determine if the agent met it based on the evidence in the agent's response AND tool calls.
- An agent meets a criterion if its behavior demonstrates the expected action or response.
- If the agent partially meets a criterion, note what was missing.
- Consider conversational agents charitably — minor wording differences are fine as long as intent matches.
- If the agent output is an error message (SQL errors, system errors), mark all criteria as not met with a note about the error.

Return ONLY a valid JSON object (no markdown, no code fences, no extra text):
{{"pass": true/false, "criteria_results": [{{"criterion": "exact criterion text", "met": true/false, "note": "brief explanation"}}], "overall_reasoning": "2-3 sentence summary of evaluation"}}
"""


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM output, handling code fences and stray text."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def format_user_messages(messages: list[dict]) -> str:
    lines = []
    for i, m in enumerate(messages, 1):
        lines.append(f"Turn {i}: {m['content']}")
    return "\n".join(lines)


def format_tool_calls(tool_calls: list[dict]) -> str:
    if not tool_calls:
        return "(no tool calls)"
    lines = []
    for tc in tool_calls:
        content = str(tc.get("content", ""))
        if len(content) > 300:
            content = content[:300] + "..."
        lines.append(f"- {tc['name']}: {content}")
    return "\n".join(lines)


def format_criteria(criteria: list[str]) -> str:
    return "\n".join(f"{i+1}. {c}" for i, c in enumerate(criteria))


async def evaluate(judge_client, scenario: dict, agent_result: dict, max_retries: int = 3) -> dict:
    prompt = JUDGE_PROMPT.format(
        description=scenario["description"],
        user_messages=format_user_messages(scenario["messages"]),
        agent_response=agent_result.get("agent_output", "") or "(no agent text output)",
        tool_calls=format_tool_calls(agent_result.get("tool_calls", [])),
        criteria=format_criteria(scenario["criteria"]),
    )

    last_error = "unknown"
    for attempt in range(max_retries):
        response = None
        try:
            response = await judge_client.ainvoke(prompt)
            result = _extract_json(str(response.content))
            return result
        except Exception as exc:
            last_error = str(response.content)[:300] if response else str(exc)[:300]
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)

    return {
        "pass": False,
        "criteria_results": [],
        "overall_reasoning": f"Judge error after {max_retries} retries: {last_error}",
        "judge_error": True,
    }
