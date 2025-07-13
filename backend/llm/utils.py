from mcp import Tool
from mcp.types import CallToolResult
from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)

from loguru import logger
from typing import Any
from fastmcp import Client
import json_repair
import json
from pydantic import BaseModel


class FunctionCall(BaseModel):
    """Representation of a function call."""

    name: str
    arguments: str | dict


class ToolCall(BaseModel):
    """Representation of a tool call."""

    id: str
    function: FunctionCall


# https://github.com/bartolli/mcp-llm-bridge/blob/main/src/mcp_llm_bridge/bridge.py#L140
def sanitize_tool_name(name: str) -> str:
    """Sanitize tool name to be a valid OpenAI function name."""
    return name.replace(" ", "_").replace("-", "_").lower()


# https://github.com/bartolli/mcp-llm-bridge/blob/main/src/mcp_llm_bridge/bridge.py#L86
def convert_tools_to_openai_format(
    tools: list[Tool],
) -> list[ChatCompletionToolParam]:
    """Convert tools to OpenAI format."""
    openai_tools = []

    for tool in tools:
        logger.info(f"Processing tool: {tool.name}")
        this_tool = {
            "type": "function",
            "function": {
                "name": sanitize_tool_name(tool.name),
                "description": tool.description,
                "parameters": getattr(
                    tool,
                    "inputSchema",
                    {"type": "object", "properties": {}, "required": []},
                ),
            },
        }
        openai_tools.append(this_tool)

    return openai_tools


def _get_appropriate_tool(
    tools: list[Tool],
    tool_name: str,
) -> Tool | None:
    """Get appropriate tool."""
    return next(
        (tool for tool in tools if sanitize_tool_name(tool.name) == tool_name),
        None,
    )


def _parse_tool_result(result: CallToolResult) -> Any:
    """Parse tool result."""
    content_type = result.content[0].type
    if content_type == "text":
        return result.content[0].text  # type: ignore
    if content_type == "image":
        return {
            "type": "image_url",
            "image_url": {
                "url": result.content[0].image.uri,  # type: ignore
            },
        }

    if content_type == "embedded-resource":
        return {
            "type": "file",
            "file": {
                "url": result.content[0].resource.uri,  # type: ignore
            },
        }
    raise ValueError(f"Unknown type: {content_type}")


async def handle_tool_call(
    tool_name: str,
    tool_args: dict | str,
    mcp_server_path: str | None = None,
    mcp_client: Client | None = None,
) -> Any:
    """Handle tool call."""
    if not mcp_server_path and not mcp_client:
        raise ValueError(
            "Either mcp_server_path or mcp_client must be provided",
        )
    if isinstance(tool_args, str):
        try:
            tool_args = json_repair.loads(tool_args)  # type: ignore
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON: {tool_args} from {tool_name}",
            ) from exc

    if mcp_server_path:
        async with Client(mcp_server_path) as client:
            tools = await client.list_tools()
            appropriate_tool = _get_appropriate_tool(tools, tool_name)
            if not appropriate_tool:
                raise ValueError(f"Tool {tool_name} not found")
            result = await client.call_tool(appropriate_tool.name, tool_args)
            return _parse_tool_result(result)

    tools = await mcp_client.list_tools()
    appropriate_tool = _get_appropriate_tool(tools, tool_name)
    if not appropriate_tool:
        raise ValueError(f"Tool {tool_name} not found")
    result = await mcp_client.call_tool(appropriate_tool.name, tool_args)
    return _parse_tool_result(result)


async def call_and_return_tool_result(
    tools: list[ChatCompletionMessageToolCall] | None = None,
    mcp_server_path: str | None = None,
    mcp_client: Client | None = None,
) -> Any:
    """Call and return tool result."""
    if not mcp_server_path and not mcp_client:
        raise ValueError(
            "Either mcp_server_path or mcp_client must be provided",
        )

    if not tools:
        return []

    results = []
    for tool in tools:
        result = await handle_tool_call(
            tool_name=tool.function.name,
            tool_args=tool.function.arguments,
            mcp_server_path=mcp_server_path,
            mcp_client=mcp_client,
        )
        results.append(
            {
                "role": "tool",
                "tool_call_id": tool.id,
                "content": result,
            },
        )
    return results


async def main():
    from fastmcp import Client  # noqa

    async with Client("backend/llm/tools.py") as client:
        tools = await client.list_tools()
        logger.info(f"Type of tools: {type(tools)}")
        logger.info(f"Tools: {tools}")
        logger.info(f"Type of each tool: {[type(tool) for tool in tools]}")
        openai_tools = convert_tools_to_openai_format(tools)
        logger.info(f"OpenAI tools: {openai_tools}")
        import openai
        import os
        from dotenv import load_dotenv

        load_dotenv()

        openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "What tools do you have?"}],
            tools=openai_tools,
        )
        logger.info(f"Response: {response.choices[0].message.content}")

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Find me the text 'Đế Quân' in the book 'An Sĩ Toàn Thư'",
                },
            ],
            tools=openai_tools,
        )
        assistant_message = response.choices[0].message
        logger.info(f"Assistant message: {assistant_message}")
        tool_call = response.choices[0].message.tool_calls[0]
        logger.info(f"Tool call ID: {tool_call.id}")
        tool_name = tool_call.function.name
        logger.info(f"Tool name: {tool_name}")
        tool_args = tool_call.function.arguments
        logger.info(f"Tool args: {tool_args}")
        result = await handle_tool_call(
            tool_name,
            tool_args,
            mcp_client=client,
        )
        logger.info(f"Result: {result}")

        results = await call_and_return_tool_result(
            tools=assistant_message.tool_calls,
            mcp_client=client,
        )
        logger.info(f"Results: {results}")

        messages = [
            {
                "role": "user",
                "content": "Find me the text 'Đế Quân' in the book 'An Sĩ Toàn Thư'",
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": assistant_message.tool_calls,
            },
        ]

        messages.extend(results)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        logger.info(f"Response: {response.choices[0].message.content}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
