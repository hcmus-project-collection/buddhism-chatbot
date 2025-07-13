from fastmcp import Client
from loguru import logger


async def main():
    async with Client("backend/llm/tools.py") as client:
        tools = await client.list_tools()
        logger.info(f"Type of tools: {type(tools)}")
        logger.info(f"Tools: {tools}")
        logger.info(f"Type of each tool: {[type(tool) for tool in tools]}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
