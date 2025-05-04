import asyncio
import sys

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession

from config import loadConfig, Model, Config

config_path: str = 'config.yaml'


def handle_event(event):
    event_type = event["event"]
    data = event["data"]
    match event_type:
        case "on_chat_model_stream":
            print(data["chunk"].content, end="", flush=True)
        case "on_tool_start":
            print("========================================")
            print(f"Call tool: {event['name']}")
            print(data["input"])
        case "on_tool_end":
            print(data["output"].content)
            print("========================================")
        case _:
            pass


async def call_model(config: Config, tools: list):
    if len(sys.argv) >= 2:
        modelName: str = sys.argv[1]
        model: Model = config["models"][modelName]
    else:
        model: Model = list(config["models"].values())[0]
    agent = create_react_agent(model.getChatModel(config["providers"][model.provider]), tools)
    message: str = input()
    messages: list = [SystemMessage(""), HumanMessage(message)]
    async for event in agent.astream_events({"messages": messages}):
        handle_event(event)


async def await_sessions(config: Config, clients, index=0, tools=None):
    if tools is None:
        tools = []
    if index < len(clients):
        reader, writer = clients[index]
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            await await_sessions(config, clients, index + 1, tools + (await load_mcp_tools(session)))
    else:
        await call_model(config, tools)


async def await_clients(config: Config, clients, index=0, objects=None):
    if objects is None:
        objects = []
    if index < len(clients):
        async with clients[index] as client:
            await await_clients(config, clients, index + 1, objects + [client])
    else:
        await await_sessions(config, objects)


async def main():
    config: Config = loadConfig(config_path)
    clients = [mcpServer.getClient() for mcpServer in config["mcpServers"].values()]
    await await_clients(config, clients)


if __name__ == '__main__':
    asyncio.run(main())
