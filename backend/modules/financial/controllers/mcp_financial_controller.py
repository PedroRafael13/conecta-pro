"""Controller MCP Financial — expõe as 8 ferramentas MCP via HTTP REST."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session as get_db
from modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/mcp/financial", tags=["MCP Financial"])


@router.get("/tools", summary="Lista as 8 ferramentas MCP financeiras")
async def list_mcp_tools(current_user=Depends(get_current_user)):
    """Lista todas as ferramentas MCP disponíveis com schema de entrada."""
    from financial_mcp_server import MCP_TOOLS_SCHEMA

    return {"tools": MCP_TOOLS_SCHEMA, "total": len(MCP_TOOLS_SCHEMA)}


@router.post(
    "/call/{tool_name}",
    summary="Executa uma ferramenta MCP pelo nome",
)
async def call_mcp_tool(
    tool_name: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executa a ferramenta MCP e retorna o resultado em formato JSON."""
    from financial_mcp_server import MCP_TOOLS

    if tool_name not in MCP_TOOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Ferramenta '{tool_name}' não encontrada. Disponíveis: {list(MCP_TOOLS.keys())}",
        )
    result = await MCP_TOOLS[tool_name]()
    return {"tool": tool_name, "result": result}


@router.get("/summary", summary="Resumo financeiro direto via MCP")
async def mcp_summary(current_user=Depends(get_current_user)):
    """Atalho: GET /mcp/financial/summary → get_financial_summary()."""
    from financial_mcp_server import get_financial_summary

    return await get_financial_summary()


@router.post("/request", summary="Handler MCP protocol nativo (tools/list, tools/call)")
async def mcp_request_handler(
    payload: dict,
    current_user=Depends(get_current_user),
):
    """Handler MCP protocol — aceita {method, params} e retorna resposta MCP."""
    from financial_mcp_server import handle_mcp_request

    return await handle_mcp_request(payload)
