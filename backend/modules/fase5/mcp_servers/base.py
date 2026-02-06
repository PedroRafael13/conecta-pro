"""
modules/fase5/mcp_servers/base.py - Base MCP Server
==================================================
Classe base para servidores MCP
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from .config import MCPServerConfig, MCPServerType

logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    """Requisicao MCP padrao."""
    method: str
    params: Dict[str, Any] = {}
    id: str = None

    def __init__(self, **data):
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid4())
        super().__init__(**data)


class MCPResponse(BaseModel):
    """Resposta MCP padrao."""
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPTool(BaseModel):
    """Definicao de ferramenta MCP."""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPResource(BaseModel):
    """Definicao de recurso MCP."""
    name: str
    description: str
    uri: str
    mime_type: str = "application/json"


class BaseMCPServer(ABC):
    """
    Classe base para servidores MCP.

    Implementa o Model Context Protocol para integracao com LLMs.
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.app = FastAPI(
            title=config.name,
            description=config.description,
            version="1.0.0"
        )
        self.tools: Dict[str, Callable] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.stats = {
            "requests_handled": 0,
            "errors": 0,
            "started_at": None
        }
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Configura rotas do servidor."""

        @self.app.get(self.config.health_endpoint)
        async def health():
            return {
                "status": "healthy",
                "server_type": self.config.server_type.value,
                "uptime": self._get_uptime()
            }

        @self.app.get(self.config.metrics_endpoint)
        async def metrics():
            return {
                "stats": self.stats,
                "tools_count": len(self.tools),
                "resources_count": len(self.resources)
            }

        @self.app.get("/tools")
        async def list_tools():
            return {
                "tools": [
                    MCPTool(
                        name=name,
                        description=f"Tool: {name}",
                        input_schema={"type": "object"}
                    ).model_dump()
                    for name in self.tools.keys()
                ]
            }

        @self.app.get("/resources")
        async def list_resources():
            return {
                "resources": [r.model_dump() for r in self.resources.values()]
            }

        @self.app.post("/invoke")
        async def invoke_tool(
            request: MCPRequest,
            api_key: str = Header(None, alias="X-API-Key")
        ):
            if self.config.requires_auth and not api_key:
                raise HTTPException(status_code=401, detail="API key required")

            self.stats["requests_handled"] += 1

            if request.method not in self.tools:
                self.stats["errors"] += 1
                return MCPResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"}
                )

            try:
                result = await self.tools[request.method](request.params)
                return MCPResponse(id=request.id, result=result)

            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Tool invocation error: {e}")
                return MCPResponse(
                    id=request.id,
                    error={"code": -32000, "message": str(e)}
                )

    def register_tool(self, name: str, handler: Callable) -> None:
        """Registra uma ferramenta."""
        self.tools[name] = handler
        logger.info(f"Tool registered: {name}")

    def register_resource(self, resource: MCPResource) -> None:
        """Registra um recurso."""
        self.resources[resource.name] = resource
        logger.info(f"Resource registered: {resource.name}")

    def _get_uptime(self) -> str:
        """Calcula uptime do servidor."""
        if not self.stats["started_at"]:
            return "not started"
        delta = datetime.utcnow() - self.stats["started_at"]
        return str(delta)

    @abstractmethod
    async def initialize(self) -> None:
        """Inicializa o servidor. Deve ser implementado por subclasses."""
        pass

    async def start(self, host: str = None, port: int = None) -> None:
        """Inicia o servidor."""
        import uvicorn

        self.stats["started_at"] = datetime.utcnow()
        await self.initialize()

        host = host or self.config.host
        port = port or self.config.port

        logger.info(f"Starting MCP server {self.config.name} on {host}:{port}")

        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
