"""
MCP Portal Server — Conecta PRO.

Expoe os dados do portal do cliente (kits documentais e chamados de suporte)
para ferramentas de IA externas como Claude Desktop e Cursor via Model Context Protocol.

Uso:
    PORTAL_TOKEN=<token> python3 mcp_portal_server.py
    python3 mcp_portal_server.py --token <token> --api-url http://localhost:8080

Variáveis de ambiente:
    PORTAL_TOKEN  Token JWT gerado em /api/v1/portal/mcp/token (obrigatorio)
    API_URL       URL base da API (padrão: http://localhost:8080)
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    GetPromptResult,
    ListPromptsResult,
    ListResourcesResult,
    ListToolsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    ReadResourceResult,
    Resource,
    TextContent,
    Tool,
)

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

API_URL = os.environ.get("API_URL", "http://localhost:8080").rstrip("/")
PORTAL_TOKEN = os.environ.get("PORTAL_TOKEN", "")
REQUEST_TIMEOUT = 20.0  # segundos


# ---------------------------------------------------------------------------
# Cliente HTTP
# ---------------------------------------------------------------------------


def _portal_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {PORTAL_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "ConectaPRO-MCP/1.0",
    }


def _get(path: str, params: dict | None = None) -> dict | list:
    """Executa GET na API do portal e retorna o JSON decodificado."""
    url = f"{API_URL}/api/v1/portal{path}"
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            resp = client.get(url, headers=_portal_headers(), params=params or {})
        if resp.status_code == 401:
            return {"erro": "Token inválido ou expirado. Gere um novo token em /area-cliente/configuracoes/mcp"}
        if resp.status_code == 404:
            return {"erro": f"Recurso não encontrado: {path}"}
        if not resp.is_success:
            return {"erro": f"Erro na API ({resp.status_code}): {resp.text[:300]}"}
        return resp.json()
    except httpx.ConnectError:
        return {"erro": f"Não foi possível conectar à API em {API_URL}. Verifique se o servidor está rodando."}
    except httpx.TimeoutException:
        return {"erro": f"Timeout ao conectar à API em {API_URL} após {REQUEST_TIMEOUT}s."}
    except Exception as exc:  # noqa: BLE001
        return {"erro": f"Erro inesperado: {exc}"}


def _post(path: str, body: dict) -> dict:
    """Executa POST na API do portal e retorna o JSON decodificado."""
    url = f"{API_URL}/api/v1/portal{path}"
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            resp = client.post(url, headers=_portal_headers(), json=body)
        if resp.status_code == 401:
            return {"erro": "Token inválido ou expirado. Gere um novo token em /area-cliente/configuracoes/mcp"}
        if resp.status_code in (400, 422):
            return {"erro": f"Dados inválidos: {resp.text[:300]}"}
        if resp.status_code == 404:
            return {"erro": f"Recurso não encontrado: {path}"}
        if not resp.is_success:
            return {"erro": f"Erro na API ({resp.status_code}): {resp.text[:300]}"}
        return resp.json()
    except httpx.ConnectError:
        return {"erro": f"Não foi possível conectar à API em {API_URL}. Verifique se o servidor está rodando."}
    except httpx.TimeoutException:
        return {"erro": f"Timeout ao conectar à API em {API_URL} após {REQUEST_TIMEOUT}s."}
    except Exception as exc:  # noqa: BLE001
        return {"erro": f"Erro inesperado: {exc}"}


# ---------------------------------------------------------------------------
# Helpers de formatação
# ---------------------------------------------------------------------------


def _fmt(data: Any) -> str:
    """Serializa qualquer dado para texto legível."""
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def _kit_resumo(kit: dict) -> str:
    """Formata um kit documental de forma legível."""
    mes = kit.get("reference_month") or kit.get("mes_referencia", "N/A")
    status = kit.get("status", "N/A")
    pct = kit.get("completion_percentage", kit.get("percentual_conclusao", 0))
    total_docs = kit.get("total_documents", kit.get("total_documentos", 0))
    total_emp = kit.get("total_employees", kit.get("total_funcionarios", 0))
    kit_id = kit.get("id", "N/A")
    return (
        f"• ID: {kit_id}\n"
        f"  Mês: {mes} | Status: {status} | Conclusão: {pct:.0f}%\n"
        f"  Documentos: {total_docs} | Funcionários: {total_emp}"
    )


def _chamado_resumo(ticket: dict) -> str:
    """Formata um chamado de suporte de forma legível."""
    ticket_id = ticket.get("id", "N/A")
    assunto = ticket.get("subject", ticket.get("assunto", "N/A"))
    status = ticket.get("status", "N/A")
    prioridade = ticket.get("priority", ticket.get("prioridade", "N/A"))
    criado_em = ticket.get("created_at", "N/A")
    msgs = ticket.get("messages", [])
    num_msgs = len(msgs) if isinstance(msgs, list) else 0
    ultima_msg = ""
    if msgs and isinstance(msgs, list):
        last = msgs[-1]
        remetente = last.get("sender_name", last.get("sender_type", ""))
        ultima_msg = f"\n  Última msg ({remetente}): {str(last.get('message', ''))[:120]}"
    return (
        f"• ID: {ticket_id}\n"
        f"  Assunto: {assunto}\n"
        f"  Status: {status} | Prioridade: {prioridade} | Mensagens: {num_msgs}\n"
        f"  Criado em: {criado_em}{ultima_msg}"
    )


# ---------------------------------------------------------------------------
# Servidor MCP
# ---------------------------------------------------------------------------

server = Server("conecta-portal")


# ------------------------------------
# Tools
# ------------------------------------


@server.list_tools()
async def list_tools() -> ListToolsResult:
    return ListToolsResult(
        tools=[
            Tool(
                name="listar_kits",
                description=(
                    "Lista os kits documentais mensais do cliente. "
                    "Cada kit contém holerites, VT, VA, folha de ponto e atestados dos funcionários. "
                    "Retorna mês de referência, status, percentual de conclusão e quantidade de documentos."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Quantidade máxima de kits a retornar (padrão: 10, máximo: 50)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50,
                        },
                        "status": {
                            "type": "string",
                            "description": "Filtrar por status do kit (ex: 'pending', 'approved', 'rejected')",
                        },
                    },
                },
            ),
            Tool(
                name="detalhes_kit",
                description=(
                    "Retorna detalhes completos de um kit documental específico, "
                    "incluindo a lista de todos os documentos (holerites, VT, VA, etc.) com seus metadados."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kit_id": {
                            "type": "string",
                            "description": "UUID do kit documental (obtido via listar_kits)",
                        },
                    },
                    "required": ["kit_id"],
                },
            ),
            Tool(
                name="baixar_documento",
                description=(
                    "Retorna a URL de download de um documento específico de um kit. "
                    "Use esta ferramenta para obter o link de acesso a holerites, comprovantes de VT/VA, etc."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kit_id": {
                            "type": "string",
                            "description": "UUID do kit ao qual o documento pertence",
                        },
                        "document_id": {
                            "type": "string",
                            "description": "UUID do documento (obtido via detalhes_kit)",
                        },
                    },
                    "required": ["kit_id", "document_id"],
                },
            ),
            Tool(
                name="listar_chamados",
                description=(
                    "Lista os chamados de suporte abertos pelo cliente. "
                    "Retorna assunto, status, prioridade e as mensagens mais recentes de cada chamado."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Quantidade máxima de chamados a retornar (padrão: 10, máximo: 50)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50,
                        },
                        "status": {
                            "type": "string",
                            "description": "Filtrar por status (ex: 'open', 'closed', 'answered')",
                        },
                    },
                },
            ),
            Tool(
                name="abrir_chamado",
                description=(
                    "Cria um novo chamado de suporte. "
                    "Use quando o cliente precisar de ajuda com um kit documental ou tiver outra solicitação."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "Assunto do chamado (mínimo 3 caracteres)",
                        },
                        "message": {
                            "type": "string",
                            "description": "Descrição detalhada do problema ou solicitação (mínimo 10 caracteres)",
                        },
                        "priority": {
                            "type": "string",
                            "description": "Prioridade do chamado: BAIXA, NORMAL, ALTA, URGENTE (padrão: NORMAL)",
                            "enum": ["BAIXA", "NORMAL", "ALTA", "URGENTE"],
                            "default": "NORMAL",
                        },
                        "kit_id": {
                            "type": "string",
                            "description": "UUID do kit relacionado ao chamado (opcional)",
                        },
                    },
                    "required": ["subject", "message"],
                },
            ),
            Tool(
                name="responder_chamado",
                description=(
                    "Adiciona uma mensagem a um chamado de suporte existente. "
                    "Use para responder ou fornecer informações adicionais a chamados em aberto."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "UUID do chamado (obtido via listar_chamados)",
                        },
                        "message": {
                            "type": "string",
                            "description": "Conteúdo da mensagem a adicionar",
                        },
                    },
                    "required": ["ticket_id", "message"],
                },
            ),
            Tool(
                name="status_portal",
                description=(
                    "Retorna um resumo geral do portal do cliente: "
                    "quantidade de kits, chamados abertos, próximas datas e alertas importantes. "
                    "Use como ponto de partida para entender a situação atual do cliente."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:  # noqa: C901
    """Despacha a chamada de ferramenta para o handler correto."""

    if not PORTAL_TOKEN:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=(
                        "PORTAL_TOKEN não configurado.\n"
                        "Configure a variável de ambiente PORTAL_TOKEN com o token gerado em "
                        "/area-cliente/configuracoes/mcp no portal Conecta PRO."
                    ),
                )
            ]
        )

    # ------------------------------------------------------------------
    # listar_kits
    # ------------------------------------------------------------------
    if name == "listar_kits":
        limit = min(int(arguments.get("limit", 10)), 50)
        status = arguments.get("status")
        params: dict = {"limit": limit, "skip": 0}
        if status:
            params["status"] = status

        data = _get("/kits", params=params)

        if "erro" in data:
            return CallToolResult(content=[TextContent(type="text", text=f"Erro: {data['erro']}")])

        items = data.get("items", data) if isinstance(data, dict) else data
        if not items:
            return CallToolResult(
                content=[TextContent(type="text", text="Nenhum kit encontrado com os filtros informados.")]
            )

        total = data.get("total", len(items)) if isinstance(data, dict) else len(items)
        linhas = [f"Kits documentais ({len(items)} de {total} total):\n"]
        for kit in items:
            linhas.append(_kit_resumo(kit))
        return CallToolResult(content=[TextContent(type="text", text="\n".join(linhas))])

    # ------------------------------------------------------------------
    # detalhes_kit
    # ------------------------------------------------------------------
    if name == "detalhes_kit":
        kit_id = arguments.get("kit_id", "").strip()
        if not kit_id:
            return CallToolResult(content=[TextContent(type="text", text="Parâmetro kit_id é obrigatório.")])

        kit = _get(f"/kits/{kit_id}")
        if "erro" in kit:
            return CallToolResult(content=[TextContent(type="text", text=f"Erro: {kit['erro']}")])

        docs = _get(f"/kits/{kit_id}/documents")
        docs_list = docs if isinstance(docs, list) else []

        linhas = [
            f"Kit Documental — {kit.get('reference_month', kit.get('mes_referencia', 'N/A'))}",
            f"Status: {kit.get('status', 'N/A')}",
            f"Conclusão: {kit.get('completion_percentage', 0):.0f}%",
            f"Total de documentos: {kit.get('total_documents', len(docs_list))}",
            f"Funcionários cobertos: {kit.get('total_employees', 0)}",
            "",
            f"Documentos ({len(docs_list)}):",
        ]
        for doc in docs_list:
            doc_nome = doc.get("file_name", doc.get("nome", "N/A"))
            doc_tipo = doc.get("document_type", doc.get("tipo", ""))
            doc_id = doc.get("id", "N/A")
            doc_size = doc.get("file_size", 0)
            size_str = f"{doc_size / 1024:.1f} KB" if doc_size else "N/A"
            linhas.append(f"  • {doc_nome} [{doc_tipo}] — {size_str} — ID: {doc_id}")

        return CallToolResult(content=[TextContent(type="text", text="\n".join(linhas))])

    # ------------------------------------------------------------------
    # baixar_documento
    # ------------------------------------------------------------------
    if name == "baixar_documento":
        kit_id = arguments.get("kit_id", "").strip()
        document_id = arguments.get("document_id", "").strip()
        if not kit_id or not document_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Parâmetros kit_id e document_id são obrigatórios.")]
            )

        download_url = f"{API_URL}/api/v1/portal/kits/{kit_id}/documents/{document_id}/download"
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=(
                        f"URL de download do documento:\n{download_url}\n\n"
                        f"Esta URL requer autenticação via header:\n"
                        f"  Authorization: Bearer {PORTAL_TOKEN[:20]}...\n\n"
                        f"O link é válido enquanto seu token estiver ativo. "
                        f"Acesse diretamente no navegador ou via curl com o token completo."
                    ),
                )
            ]
        )

    # ------------------------------------------------------------------
    # listar_chamados
    # ------------------------------------------------------------------
    if name == "listar_chamados":
        limit = min(int(arguments.get("limit", 10)), 50)
        status = arguments.get("status")
        params = {"limit": limit, "skip": 0}
        if status:
            params["status"] = status

        data = _get("/tickets", params=params)

        if "erro" in data:
            return CallToolResult(content=[TextContent(type="text", text=f"Erro: {data['erro']}")])

        items = data.get("items", data) if isinstance(data, dict) else data
        if not items:
            return CallToolResult(
                content=[TextContent(type="text", text="Nenhum chamado encontrado com os filtros informados.")]
            )

        total = data.get("total", len(items)) if isinstance(data, dict) else len(items)
        linhas = [f"Chamados de suporte ({len(items)} de {total} total):\n"]
        for ticket in items:
            linhas.append(_chamado_resumo(ticket))
        return CallToolResult(content=[TextContent(type="text", text="\n".join(linhas))])

    # ------------------------------------------------------------------
    # abrir_chamado
    # ------------------------------------------------------------------
    if name == "abrir_chamado":
        subject = arguments.get("subject", "").strip()
        message = arguments.get("message", "").strip()
        priority = arguments.get("priority", "NORMAL").upper()
        kit_id = arguments.get("kit_id")

        if not subject or len(subject) < 3:
            return CallToolResult(content=[TextContent(type="text", text="O assunto deve ter no mínimo 3 caracteres.")])
        if not message or len(message) < 10:
            return CallToolResult(
                content=[TextContent(type="text", text="A mensagem deve ter no mínimo 10 caracteres.")]
            )
        if priority not in ("BAIXA", "NORMAL", "ALTA", "URGENTE"):
            priority = "NORMAL"

        body: dict = {
            "subject": subject,
            "description": message,
            "priority": priority,
        }
        if kit_id:
            body["kit_id"] = kit_id

        result = _post("/tickets", body)

        if "erro" in result:
            return CallToolResult(content=[TextContent(type="text", text=f"Erro ao abrir chamado: {result['erro']}")])

        ticket_id = result.get("id", "N/A")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=(
                        f"Chamado aberto com sucesso!\n"
                        f"ID: {ticket_id}\n"
                        f"Assunto: {subject}\n"
                        f"Prioridade: {priority}\n\n"
                        f"Nossa equipe de suporte responderá em breve. "
                        f"Use a ferramenta responder_chamado para adicionar mais informações."
                    ),
                )
            ]
        )

    # ------------------------------------------------------------------
    # responder_chamado
    # ------------------------------------------------------------------
    if name == "responder_chamado":
        ticket_id = arguments.get("ticket_id", "").strip()
        message = arguments.get("message", "").strip()

        if not ticket_id:
            return CallToolResult(content=[TextContent(type="text", text="Parâmetro ticket_id é obrigatório.")])
        if not message:
            return CallToolResult(content=[TextContent(type="text", text="Parâmetro message é obrigatório.")])

        result = _post(f"/tickets/{ticket_id}/messages", {"message": message})

        if "erro" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao responder chamado: {result['erro']}")]
            )

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=(
                        f"Mensagem adicionada ao chamado {ticket_id} com sucesso.\n"
                        f"Status atual: {result.get('status', 'N/A')}\n"
                        f"Total de mensagens: {len(result.get('messages', []))}"
                    ),
                )
            ]
        )

    # ------------------------------------------------------------------
    # status_portal
    # ------------------------------------------------------------------
    if name == "status_portal":
        kits_data = _get("/kits", params={"limit": 50, "skip": 0})
        tickets_data = _get("/tickets", params={"limit": 50, "skip": 0, "status": "open"})

        kits_items = kits_data.get("items", kits_data) if isinstance(kits_data, dict) else []
        tickets_items = tickets_data.get("items", tickets_data) if isinstance(tickets_data, dict) else []

        total_kits = kits_data.get("total", len(kits_items)) if isinstance(kits_data, dict) else len(kits_items)
        total_chamados = (
            tickets_data.get("total", len(tickets_items)) if isinstance(tickets_data, dict) else len(tickets_items)
        )

        # Alertas
        alertas: list[str] = []
        kits_pendentes = [k for k in kits_items if k.get("status") in ("pending", "pendente")]
        kits_rejeitados = [k for k in kits_items if k.get("status") in ("rejected", "rejeitado")]
        chamados_urgentes = [t for t in tickets_items if t.get("priority") in ("URGENTE", "ALTA")]

        if kits_pendentes:
            alertas.append(f"  ⚠ {len(kits_pendentes)} kit(s) aguardando aprovação")
        if kits_rejeitados:
            alertas.append(f"  ✗ {len(kits_rejeitados)} kit(s) rejeitado(s) — verificar documentação")
        if chamados_urgentes:
            alertas.append(f"  ! {len(chamados_urgentes)} chamado(s) com prioridade ALTA/URGENTE em aberto")

        # Kit mais recente
        kit_recente_info = ""
        if kits_items:
            ultimo_kit = kits_items[0]
            kit_recente_info = (
                f"\nÚltimo kit: {ultimo_kit.get('reference_month', 'N/A')} "
                f"— Status: {ultimo_kit.get('status', 'N/A')} "
                f"({ultimo_kit.get('completion_percentage', 0):.0f}% concluído)"
            )

        linhas = [
            "=== Status do Portal Conecta PRO ===",
            f"Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            "📁 Kits Documentais",
            f"  Total: {total_kits}",
        ]
        if kit_recente_info:
            linhas.append(kit_recente_info)

        linhas += [
            "",
            "🎫 Chamados de Suporte",
            f"  Abertos: {total_chamados}",
        ]

        if alertas:
            linhas += ["", "⚠ Alertas:"] + alertas
        else:
            linhas.append("\n✓ Nenhum alerta — tudo em ordem!")

        linhas += [
            "",
            "💡 Dicas:",
            "  • Use listar_kits para ver todos os seus kits documentais",
            "  • Use detalhes_kit <id> para ver os documentos de um kit",
            "  • Use abrir_chamado para contatar o suporte",
        ]

        return CallToolResult(content=[TextContent(type="text", text="\n".join(linhas))])

    # ------------------------------------------------------------------
    # Ferramenta desconhecida
    # ------------------------------------------------------------------
    return CallToolResult(content=[TextContent(type="text", text=f"Ferramenta desconhecida: {name}")])


# ------------------------------------
# Resources
# ------------------------------------


@server.list_resources()
async def list_resources() -> ListResourcesResult:
    return ListResourcesResult(
        resources=[
            Resource(
                uri="portal://summary",
                name="Resumo do Portal",
                description=(
                    "Visão geral do portal do cliente Conecta PRO: kits documentais, chamados de suporte e alertas."
                ),
                mimeType="text/plain",
            ),
        ]
    )


@server.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    if uri != "portal://summary":
        return ReadResourceResult(contents=[TextContent(type="text", text=f"Recurso não encontrado: {uri}")])

    if not PORTAL_TOKEN:
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text="PORTAL_TOKEN não configurado. Configure a variável de ambiente antes de usar este resource.",
                )
            ]
        )

    kits_data = _get("/kits", params={"limit": 5, "skip": 0})
    tickets_data = _get("/tickets", params={"limit": 5, "skip": 0})

    kits_items = kits_data.get("items", []) if isinstance(kits_data, dict) else []
    tickets_items = tickets_data.get("items", []) if isinstance(tickets_data, dict) else []

    total_kits = kits_data.get("total", 0) if isinstance(kits_data, dict) else 0
    total_tickets = tickets_data.get("total", 0) if isinstance(tickets_data, dict) else 0

    linhas = [
        "# Resumo do Portal Conecta PRO",
        f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        f"## Kits Documentais (total: {total_kits})",
    ]
    for kit in kits_items:
        linhas.append(_kit_resumo(kit))

    linhas += ["", f"## Chamados de Suporte (total: {total_tickets})"]
    for ticket in tickets_items:
        linhas.append(_chamado_resumo(ticket))

    linhas += [
        "",
        "## Como usar",
        "Use as ferramentas disponíveis neste servidor MCP para:",
        "• Listar e detalhar kits documentais mensais",
        "• Baixar documentos (holerites, VT, VA, ponto)",
        "• Abrir e responder chamados de suporte",
    ]

    return ReadResourceResult(contents=[TextContent(type="text", text="\n".join(linhas))])


# ------------------------------------
# Prompts
# ------------------------------------


@server.list_prompts()
async def list_prompts() -> ListPromptsResult:
    return ListPromptsResult(
        prompts=[
            Prompt(
                name="portal_help",
                description="Instruções completas de como usar o portal do cliente Conecta PRO via MCP.",
                arguments=[
                    PromptArgument(
                        name="contexto",
                        description="Contexto específico ou dúvida do cliente (opcional)",
                        required=False,
                    )
                ],
            ),
        ]
    )


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
    if name != "portal_help":
        return GetPromptResult(
            description="Prompt não encontrado",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"Prompt '{name}' não existe."),
                )
            ],
        )

    contexto = (arguments or {}).get("contexto", "")
    contexto_str = f"\n\nContexto específico: {contexto}" if contexto else ""

    conteudo = f"""Você é um assistente especializado no portal do cliente Conecta PRO,
sistema ERP de gestão para empresas de vigilância e segurança patrimonial.

## O que é o Portal do Cliente?

O portal do cliente Conecta PRO permite que condomínios e administradoras acessem:

1. **Kits Documentais Mensais** — Pacotes de documentos enviados mensalmente pela empresa
   de segurança, contendo: holerites dos funcionários, comprovantes de VT e VA,
   folha de ponto, atestados e demais documentos de RH.

2. **Chamados de Suporte** — Sistema de tickets para comunicação com a empresa de segurança.

## Ferramentas Disponíveis

### Consultar Kits
- `listar_kits(limit, status)` — Veja todos os seus kits documentais
- `detalhes_kit(kit_id)` — Veja os documentos de um kit específico
- `baixar_documento(kit_id, document_id)` — Obtenha o link de download de um documento

### Gerenciar Chamados
- `listar_chamados(limit, status)` — Veja seus chamados de suporte
- `abrir_chamado(subject, message, priority)` — Abra um novo chamado
- `responder_chamado(ticket_id, message)` — Responda a um chamado existente

### Visão Geral
- `status_portal()` — Resumo geral com alertas e pendências

## Fluxo Típico de Uso

1. Comece com `status_portal()` para ver a situação geral
2. Use `listar_kits()` para ver os kits do mês atual
3. Use `detalhes_kit(id)` para ver os documentos disponíveis
4. Use `baixar_documento(kit_id, doc_id)` para acessar documentos específicos
5. Se tiver dúvidas, use `abrir_chamado()` para contatar o suporte

## Status dos Kits

- **pending** — Aguardando geração ou aprovação
- **approved** — Kit aprovado, documentos disponíveis para download
- **rejected** — Kit rejeitado, entrar em contato com o suporte
- **in_progress** — Em processamento

## Prioridades dos Chamados

- **BAIXA** — Dúvidas gerais, sem urgência
- **NORMAL** — Problemas que precisam de atenção
- **ALTA** — Problemas que afetam operações
- **URGENTE** — Problemas críticos que exigem resposta imediata{contexto_str}
"""

    return GetPromptResult(
        description="Instruções do Portal do Cliente Conecta PRO",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=conteudo),
            )
        ],
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MCP Portal Server — Conecta PRO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--token", help="Token JWT do portal (alternativa à env PORTAL_TOKEN)")
    parser.add_argument(
        "--api-url",
        default=None,
        help="URL base da API (alternativa à env API_URL, padrão: http://localhost:8080)",
    )
    args = parser.parse_args()

    global PORTAL_TOKEN, API_URL  # noqa: PLW0603

    if args.token:
        PORTAL_TOKEN = args.token
    if args.api_url:
        API_URL = args.api_url.rstrip("/")

    if not PORTAL_TOKEN:
        print(
            "AVISO: PORTAL_TOKEN não configurado. "
            "As ferramentas retornarão erros de autenticação.\n"
            "Configure via: PORTAL_TOKEN=<token> python3 mcp_portal_server.py\n"
            "Ou via: python3 mcp_portal_server.py --token <token>",
            file=sys.stderr,
        )

    import asyncio

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(_run())


if __name__ == "__main__":
    main()
