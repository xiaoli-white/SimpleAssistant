from dataclasses import dataclass
from typing import Optional, TypedDict

import yaml
from langchain_openai import ChatOpenAI
from mcp import StdioServerParameters, stdio_client
from mcp.client.sse import sse_client


@dataclass
class Provider:
    name: str
    base_url: str
    api_key: str = ""
    description: Optional[str] = None


@dataclass
class Model:
    name: str
    provider: str
    model_name: str
    description: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096

    def getChatModel(self, provider: Provider):
        return ChatOpenAI(
            model_name=self.model_name,
            openai_api_base=provider.base_url,
            openai_api_key=provider.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=True,
            stream_usage=True,
        )


class MCPServer:
    name: str
    description: Optional[str] = None
    protocol: str

    def __init__(self, name: str, protocol: str, **kwargs):
        self.name = name
        self.protocol = protocol
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getClient(self):
        match self.protocol.lower():
            case "sse":
                return sse_client(url=self.url, timeout=getattr(self, "timeout", 5))
            case "stdio":
                server_params = StdioServerParameters(command=self.command, args=self.args)
                return stdio_client(server_params)
            case _:
                raise NotImplementedError()


class Config(TypedDict):
    systemPrompt: str
    providers: dict[str, Provider]
    models: dict[str, Model]
    mcpServers: dict[str, MCPServer]


def loadConfig(configFilePath: str) -> Config:
    with open(configFilePath, "r", encoding="utf-8") as f:
        data: dict = yaml.safe_load(f)
    providers: dict[str, Provider] = {}
    for _, provider in data["providers"].items():
        providers[provider["name"]] = Provider(**provider)
    models: dict[str, Model] = {}
    for _, model in data["models"].items():
        models[model["name"]] = Model(**model)
    mcpServers = {}
    for _, mcpServer in data["mcp-servers"].items():
        mcpServers[mcpServer["name"]] = MCPServer(**mcpServer)
    return Config(systemPrompt=getattr(data, "system-prompt", ""), providers=providers, models=models,
                  mcpServers=mcpServers)
