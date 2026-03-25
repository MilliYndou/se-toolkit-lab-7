"""LLM-based intent router with tool calling.

This module implements the tool calling loop:
1. Send user message + tool definitions to LLM
2. LLM returns tool calls
3. Execute tools and feed results back to LLM
4. LLM produces final answer
"""

import json
import sys
from typing import Any

import httpx

from config import BotSettings


# System prompt for the LLM router
SYSTEM_PROMPT = """You are an intelligent assistant for a Learning Management System (LMS).
You have access to various tools that fetch real data from the LMS backend.

When a user asks a question:
1. Analyze what information they need
2. Call the appropriate tools to fetch that data
3. Once you have the data, provide a clear, helpful answer

Available tools:
- get_items: List all labs and tasks
- get_learners: Get enrolled students and groups
- get_scores: Get score distribution for a lab
- get_pass_rates: Get per-task pass rates for a lab
- get_timeline: Get submission timeline for a lab
- get_groups: Get per-group performance for a lab
- get_top_learners: Get top N learners by score
- get_completion_rate: Get completion rate for a lab
- trigger_sync: Refresh data from autochecker

For multi-step queries (e.g., "which lab has the lowest pass rate?"):
1. First call get_items to get all labs
2. Then call get_pass_rates for each lab
3. Compare the results and provide an answer

Always be specific and include numbers from the data. If you don't have enough information,
ask clarifying questions or suggest what tools could help.

If the user's message is a greeting or doesn't require data, respond naturally without calling tools.
If the user's message is unclear or gibberish, politely explain what you can help with.
"""

# Tool definitions for all 9 backend endpoints
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks available in the LMS",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline to refresh data from autochecker",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


class IntentRouter:
    """LLM-based intent router with tool calling."""

    def __init__(self, settings: BotSettings, lms_client: Any):
        """Initialize the intent router.

        Args:
            settings: Bot configuration settings.
            lms_client: LMS API client for executing tools.
        """
        self.settings = settings
        self.lms_client = lms_client
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_api_base_url
        self.model = settings.llm_api_model or "coder-model"

    async def route(self, message: str) -> str:
        """Route a user message through the LLM tool calling loop.

        Args:
            message: User's message text.

        Returns:
            LLM's final response.
        """
        # Initialize conversation with system prompt and user message
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        # Tool calling loop (max 5 iterations to prevent infinite loops)
        max_iterations = 5
        for iteration in range(max_iterations):
            try:
                # Call LLM
                response = await self._call_llm(messages)

                # Check if LLM returned tool calls
                tool_calls = response.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])

                if not tool_calls:
                    # No tool calls - LLM returned final answer
                    return response["choices"][0]["message"]["content"]

                # Execute tool calls and collect results
                tool_results = []
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    tool_name = function.get("name", "")
                    tool_args_str = function.get("arguments", "{}")

                    try:
                        tool_args = json.loads(tool_args_str) if tool_args_str else {}
                    except json.JSONDecodeError:
                        tool_args = {}

                    # Execute the tool
                    print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                    result = await self._execute_tool(tool_name, tool_args)
                    print(f"[tool] Result: {self._truncate_result(result)}", file=sys.stderr)

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", ""),
                        "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
                    })

                # Feed tool results back to LLM
                print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
                messages.append(response["choices"][0]["message"])
                messages.extend(tool_results)

            except Exception as e:
                print(f"[error] LLM routing error: {e}", file=sys.stderr)
                return f"I encountered an error while processing your request: {str(e)}"

        return "I'm having trouble completing this request. Please try rephrasing your question."

    async def _call_llm(self, messages: list[dict]) -> dict:
        """Call the LLM API.

        Args:
            messages: Conversation messages.

        Returns:
            LLM response.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": TOOLS,
                    "tool_choice": "auto",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def _execute_tool(self, name: str, args: dict) -> Any:
        """Execute a tool by calling the appropriate LMS API endpoint.

        Args:
            name: Tool/function name.
            args: Tool arguments.

        Returns:
            Tool execution result.
        """
        if name == "get_items":
            return await self.lms_client.get_items()
        elif name == "get_learners":
            return await self.lms_client.get_learners()
        elif name == "get_scores":
            return await self.lms_client.get_scores(args.get("lab", ""))
        elif name == "get_pass_rates":
            return await self.lms_client.get_pass_rates(args.get("lab", ""))
        elif name == "get_timeline":
            return await self.lms_client.get_timeline(args.get("lab", ""))
        elif name == "get_groups":
            return await self.lms_client.get_groups(args.get("lab", ""))
        elif name == "get_top_learners":
            return await self.lms_client.get_top_learners(
                args.get("lab", ""), args.get("limit", 5)
            )
        elif name == "get_completion_rate":
            return await self.lms_client.get_completion_rate(args.get("lab", ""))
        elif name == "trigger_sync":
            return await self.lms_client.trigger_sync()
        else:
            return {"error": f"Unknown tool: {name}"}

    def _truncate_result(self, result: Any, max_length: int = 200) -> str:
        """Truncate a result for debug logging.

        Args:
            result: Tool result.
            max_length: Maximum string length.

        Returns:
            Truncated string representation.
        """
        result_str = str(result)
        if len(result_str) > max_length:
            return result_str[:max_length] + "..."
        return result_str
