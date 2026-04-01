"""Gerador de respostas formatadas."""

import logging
import re
from dataclasses import dataclass
from typing import Any

from modules.ai.conversation.models.chat_message import IntentCategory

logger = logging.getLogger(__name__)


@dataclass
class FormattedResponse:
    """Resposta formatada."""

    text: str
    html: str
    markdown: str
    suggestions: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    related_links: list[dict[str, Any]]


class ResponseGenerator:
    """
    Gerador de respostas formatadas e enriquecidas.

    Responsabilidades:
    - Formatacao de texto (plain, HTML, markdown)
    - Geracao de sugestoes contextuais
    - Criacao de botoes de acao
    - Links relacionados
    - Templates de resposta
    """

    # Templates de resposta por intencao
    RESPONSE_TEMPLATES: dict[IntentCategory, list[str]] = {
        IntentCategory.GREETING: [
            "Ola! Como posso ajudar voce hoje?",
            "Oi! Estou aqui para ajudar. O que voce precisa?",
            "Bem-vindo! Em que posso ser util?",
        ],
        IntentCategory.FAREWELL: [
            "Ate logo! Estou sempre aqui se precisar.",
            "Tchau! Foi um prazer ajudar.",
            "Ate mais! Volte quando precisar.",
        ],
        IntentCategory.HELP_NAVIGATION: [
            "Claro! Posso te ajudar a encontrar o que precisa.",
            "Vou te guiar ate la. Siga os passos abaixo.",
        ],
        IntentCategory.TROUBLESHOOTING: [
            "Entendo que voce esta com dificuldades. Vamos resolver isso.",
            "Vou te ajudar a solucionar esse problema.",
        ],
    }

    # Links uteis por modulo
    MODULE_LINKS: dict[str, list[dict[str, str]]] = {
        "crm": [
            {"title": "Guia de Leads", "url": "/docs/crm/leads"},
            {"title": "Pipeline de Vendas", "url": "/docs/crm/pipeline"},
            {"title": "Relatorios CRM", "url": "/docs/crm/reports"},
        ],
        "financial": [
            {"title": "Contas a Pagar", "url": "/docs/financial/payables"},
            {"title": "Fluxo de Caixa", "url": "/docs/financial/cashflow"},
            {"title": "Conciliacao", "url": "/docs/financial/reconciliation"},
        ],
        "hr": [
            {"title": "Folha de Pagamento", "url": "/docs/hr/payroll"},
            {"title": "Ponto Eletronico", "url": "/docs/hr/attendance"},
            {"title": "Ferias", "url": "/docs/hr/vacations"},
        ],
        "inventory": [
            {"title": "Produtos", "url": "/docs/inventory/products"},
            {"title": "Movimentacoes", "url": "/docs/inventory/movements"},
            {"title": "Inventario", "url": "/docs/inventory/count"},
        ],
    }

    def __init__(self) -> None:
        """Inicializa o gerador de respostas."""
        pass

    def format_response(
        self,
        text: str,
        intent: IntentCategory,
        module: str | None = None,
        entities: dict[str, Any] | None = None,
    ) -> FormattedResponse:
        """
        Formata resposta com todos os elementos.

        Args:
            text: Texto da resposta
            intent: Intencao identificada
            module: Modulo atual
            entities: Entidades extraidas

        Returns:
            FormattedResponse completa
        """
        return FormattedResponse(
            text=text,
            html=self.to_html(text),
            markdown=self.to_markdown(text),
            suggestions=self.generate_suggestions(intent, module),
            actions=self.generate_actions(intent, entities or {}),
            related_links=self.get_related_links(module, intent),
        )

    def to_html(self, text: str) -> str:
        """Converte texto para HTML formatado."""
        # Escapa caracteres HTML
        html = text.replace("&", "&amp;")
        html = html.replace("<", "&lt;")
        html = html.replace(">", "&gt;")

        # Converte markdown para HTML
        # Headers
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Bold e Italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # Code
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # Links
        html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)

        # Listas
        lines = html.split("\n")
        in_list = False
        result = []

        for line in lines:
            if line.strip().startswith("- "):
                if not in_list:
                    result.append("<ul>")
                    in_list = True
                result.append(f"<li>{line.strip()[2:]}</li>")
            elif line.strip().startswith(("1. ", "2. ", "3. ", "4. ", "5. ")):
                if not in_list:
                    result.append("<ol>")
                    in_list = True
                result.append(f"<li>{line.strip()[3:]}</li>")
            else:
                if in_list:
                    result.append("</ul>" if result[-2].startswith("<li>") else "</ol>")
                    in_list = False
                if line.strip():
                    result.append(f"<p>{line}</p>")
                else:
                    result.append("<br>")

        if in_list:
            result.append("</ul>")

        return "\n".join(result)

    def to_markdown(self, text: str) -> str:
        """Retorna texto em formato markdown."""
        # O texto ja deve estar em markdown na maioria dos casos
        return text

    def to_plain_text(self, text: str) -> str:
        """Converte para texto plano removendo formatacao."""
        # Remove markdown
        plain = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        plain = re.sub(r"\*(.+?)\*", r"\1", plain)
        plain = re.sub(r"`(.+?)`", r"\1", plain)
        plain = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", plain)
        plain = re.sub(r"^#+\s*", "", plain, flags=re.MULTILINE)
        plain = re.sub(r"^[-*]\s*", "• ", plain, flags=re.MULTILINE)

        return plain

    def generate_suggestions(self, intent: IntentCategory, module: str | None = None) -> list[dict[str, Any]]:
        """
        Gera sugestoes de quick replies.

        Args:
            intent: Intencao da mensagem
            module: Modulo atual

        Returns:
            Lista de sugestoes
        """
        suggestions = []

        # Sugestoes baseadas na intencao
        if intent == IntentCategory.GREETING:
            suggestions = [
                {
                    "text": "Ver dashboard",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/dashboard"},
                },
                {"text": "Minhas tarefas", "type": "quick_reply", "action": "navigate", "payload": {"route": "/tasks"}},
                {
                    "text": "Ultimas notificacoes",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/notifications"},
                },
            ]
        elif intent == IntentCategory.HELP_NAVIGATION:
            suggestions = [
                {"text": "Ver menu principal", "type": "quick_reply", "action": "navigate", "payload": {"route": "/"}},
                {"text": "Buscar funcionalidade", "type": "quick_reply", "action": "search"},
                {"text": "Ver tutorial", "type": "quick_reply", "action": "tutorial"},
            ]
        elif intent == IntentCategory.DATA_QUERY:
            suggestions = [
                {"text": "Exportar Excel", "type": "action", "action": "export", "payload": {"format": "xlsx"}},
                {"text": "Exportar PDF", "type": "action", "action": "export", "payload": {"format": "pdf"}},
                {"text": "Ver grafico", "type": "action", "action": "chart"},
            ]
        elif intent == IntentCategory.ANALYSIS_REQUEST:
            suggestions = [
                {"text": "Gerar relatorio", "type": "action", "action": "report"},
                {"text": "Comparar periodos", "type": "action", "action": "compare"},
                {"text": "Ver tendencias", "type": "action", "action": "trends"},
            ]
        elif intent == IntentCategory.TROUBLESHOOTING:
            suggestions = [
                {"text": "Abrir chamado", "type": "action", "action": "ticket"},
                {"text": "Ver FAQ", "type": "quick_reply", "action": "faq"},
                {"text": "Chat com suporte", "type": "action", "action": "support_chat"},
            ]
        elif intent == IntentCategory.ACTION_REQUEST:
            suggestions = [
                {"text": "Confirmar", "type": "action", "action": "confirm"},
                {"text": "Cancelar", "type": "action", "action": "cancel"},
            ]

        # Adiciona sugestoes especificas do modulo
        if module:
            module_suggestions = self._get_module_suggestions(module)
            suggestions.extend(module_suggestions)

        return suggestions[:5]  # Limita a 5 sugestoes

    def _get_module_suggestions(self, module: str) -> list[dict[str, Any]]:
        """Retorna sugestoes especificas do modulo."""
        module_suggestions = {
            "crm": [
                {"text": "Novo lead", "type": "action", "action": "create", "payload": {"entity": "lead"}},
                {
                    "text": "Ver pipeline",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/crm/pipeline"},
                },
            ],
            "financial": [
                {
                    "text": "Fluxo de caixa",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/financial/cashflow"},
                },
                {
                    "text": "Contas a pagar",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/financial/payables"},
                },
            ],
            "hr": [
                {
                    "text": "Colaboradores",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/hr/employees"},
                },
                {"text": "Folha", "type": "quick_reply", "action": "navigate", "payload": {"route": "/hr/payroll"}},
            ],
            "inventory": [
                {
                    "text": "Produtos",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/inventory/products"},
                },
                {
                    "text": "Movimentacoes",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": "/inventory/movements"},
                },
            ],
        }

        return module_suggestions.get(module, [])

    def generate_actions(self, intent: IntentCategory, entities: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Gera acoes possiveis.

        Args:
            intent: Intencao identificada
            entities: Entidades extraidas

        Returns:
            Lista de acoes
        """
        actions = []

        if intent == IntentCategory.ACTION_REQUEST:
            # Detecta tipo de acao baseado em entidades
            if "module" in entities:
                module = entities["module"]
                actions.append(
                    {
                        "type": "create",
                        "label": f"Criar registro em {module}",
                        "module": module,
                        "requires_confirmation": True,
                    }
                )

        elif intent == IntentCategory.DATA_QUERY:
            actions.append(
                {
                    "type": "export",
                    "label": "Exportar resultados",
                    "formats": ["xlsx", "csv", "pdf"],
                }
            )

        elif intent == IntentCategory.ANALYSIS_REQUEST:
            actions.append(
                {
                    "type": "report",
                    "label": "Gerar relatorio completo",
                    "formats": ["pdf", "xlsx"],
                }
            )

        return actions

    def get_related_links(self, module: str | None, intent: IntentCategory) -> list[dict[str, Any]]:
        """
        Retorna links relacionados.

        Args:
            module: Modulo atual
            intent: Intencao da mensagem

        Returns:
            Lista de links
        """
        links = []

        # Links do modulo
        if module and module in self.MODULE_LINKS:
            links.extend(self.MODULE_LINKS[module])

        # Links gerais por intencao
        if intent == IntentCategory.TROUBLESHOOTING:
            links.extend(
                [
                    {"title": "Central de Ajuda", "url": "/help"},
                    {"title": "FAQ", "url": "/faq"},
                    {"title": "Contato Suporte", "url": "/support"},
                ]
            )
        elif intent == IntentCategory.HELP_NAVIGATION:
            links.extend(
                [
                    {"title": "Mapa do Sistema", "url": "/sitemap"},
                    {"title": "Tutoriais", "url": "/tutorials"},
                ]
            )

        return links[:5]  # Limita a 5 links

    def get_template_response(self, intent: IntentCategory) -> str | None:
        """Retorna template de resposta para uma intencao."""
        templates = self.RESPONSE_TEMPLATES.get(intent)
        if templates:
            import random

            return random.choice(templates)  # noqa: S311
        return None

    def enrich_response(
        self,
        response: str,
        data: dict[str, Any] | None = None,
    ) -> str:
        """
        Enriquece resposta com dados.

        Args:
            response: Resposta base
            data: Dados para interpolacao

        Returns:
            Resposta enriquecida
        """
        if not data:
            return response

        # Substitui placeholders
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in response:
                response = response.replace(placeholder, str(value))

        return response

    def format_data_response(
        self,
        data: list[dict[str, Any]],
        columns: list[str] | None = None,
        title: str | None = None,
    ) -> str:
        """
        Formata dados em tabela markdown.

        Args:
            data: Lista de dicionarios
            columns: Colunas a exibir
            title: Titulo da tabela

        Returns:
            Tabela em markdown
        """
        if not data:
            return "Nenhum dado encontrado."

        # Determina colunas
        if not columns:
            columns = list(data[0].keys())

        # Monta tabela
        lines = []

        if title:
            lines.append(f"### {title}\n")

        # Header
        header = " | ".join(columns)
        separator = " | ".join(["---"] * len(columns))
        lines.append(f"| {header} |")
        lines.append(f"| {separator} |")

        # Rows
        for item in data[:20]:  # Limita a 20 linhas
            values = [str(item.get(col, "-")) for col in columns]
            row = " | ".join(values)
            lines.append(f"| {row} |")

        if len(data) > 20:
            lines.append(f"\n*...e mais {len(data) - 20} registros*")

        return "\n".join(lines)

    def format_error_response(self, error_type: str, message: str, suggestion: str | None = None) -> FormattedResponse:
        """
        Formata resposta de erro.

        Args:
            error_type: Tipo do erro
            message: Mensagem de erro
            suggestion: Sugestao de correcao

        Returns:
            FormattedResponse de erro
        """
        text_parts = [f"**Erro**: {message}"]

        if suggestion:
            text_parts.append(f"\n**Sugestao**: {suggestion}")

        text = "\n".join(text_parts)

        return FormattedResponse(
            text=text,
            html=self.to_html(text),
            markdown=text,
            suggestions=[
                {"text": "Tentar novamente", "type": "action", "action": "retry"},
                {"text": "Abrir chamado", "type": "action", "action": "ticket"},
            ],
            actions=[],
            related_links=[
                {"title": "Central de Ajuda", "url": "/help"},
            ],
        )

    def format_success_response(
        self,
        message: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> FormattedResponse:
        """
        Formata resposta de sucesso.

        Args:
            message: Mensagem de sucesso
            entity_type: Tipo da entidade
            entity_id: ID da entidade

        Returns:
            FormattedResponse de sucesso
        """
        text = f"✓ {message}"

        suggestions = []
        if entity_type and entity_id:
            suggestions.append(
                {
                    "text": f"Ver {entity_type}",
                    "type": "quick_reply",
                    "action": "navigate",
                    "payload": {"route": f"/{entity_type}/{entity_id}"},
                }
            )

        suggestions.append(
            {"text": "Voltar ao inicio", "type": "quick_reply", "action": "navigate", "payload": {"route": "/"}}
        )

        return FormattedResponse(
            text=text,
            html=self.to_html(text),
            markdown=text,
            suggestions=suggestions,
            actions=[],
            related_links=[],
        )
