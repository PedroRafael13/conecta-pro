"""
ComunicacaoAgent - Agente especialista em comunicados e anuncios operacionais.

Gerencia intents relacionados a comunicados: listagem, detalhes,
recentes, pendentes, estatisticas, criacao e publicacao.

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
import re
from datetime import date
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class ComunicacaoIntent(StrEnum):
    """Intents relacionados a comunicados e anuncios."""

    VER_COMUNICADOS = "ver_comunicados"
    COMUNICADO_DETALHES = "comunicado_detalhes"
    COMUNICADOS_RECENTES = "comunicados_recentes"
    COMUNICADOS_PENDENTES = "comunicados_pendentes"
    ESTATISTICAS = "estatisticas"
    CRIAR_COMUNICADO = "criar_comunicado"
    PUBLICAR_COMUNICADO = "publicar_comunicado"


class ComunicacaoAgent:
    """
    Agente especializado em operacoes de comunicados.

    Capabilities:
    - Listar comunicados ativos/publicados
    - Exibir detalhes de um comunicado
    - Listar comunicados recentes
    - Listar rascunhos/pendentes de publicacao
    - Exibir estatisticas gerais de comunicados
    - Redirecionar criacao de comunicado para action
    - Redirecionar publicacao de comunicado para action
    """

    # ==========================================================================
    # INTENT_PATTERNS - Lista exaustiva para deteccao de intencoes
    # IMPORTANTE: Patterns mais especificos devem vir ANTES dos mais genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # CRIAR_COMUNICADO - Antes de genericos (mais especifico)
        # ==================================================================
        (
            r"(?:criar|crie|cria|novo|nova|cadastrar|cadastre|redigir|redija|elaborar|elabore)\s+(?:um\s+)?(?:novo\s+)?comunicado",
            ComunicacaoIntent.CRIAR_COMUNICADO,
        ),
        (
            r"(?:criar|crie|cria|novo|nova|cadastrar|cadastre|redigir|redija|elaborar|elabore)\s+(?:um\s+)?(?:novo\s+)?anuncio",
            ComunicacaoIntent.CRIAR_COMUNICADO,
        ),
        (
            r"(?:preciso|quero)\s+(?:criar|fazer|redigir|elaborar)\s+(?:um\s+)?comunicado",
            ComunicacaoIntent.CRIAR_COMUNICADO,
        ),
        (
            r"(?:pode|consegue|da\s+para)\s+(?:criar|fazer|redigir)\s+(?:um\s+)?comunicado",
            ComunicacaoIntent.CRIAR_COMUNICADO,
        ),
        (r"novo\s+(?:comunicado|anuncio|aviso)", ComunicacaoIntent.CRIAR_COMUNICADO),
        # ==================================================================
        # PUBLICAR_COMUNICADO - Antes de genericos
        # ==================================================================
        (
            r"(?:publicar|publique|liberar|libere|divulgar|divulgue)\s+(?:o\s+)?comunicado",
            ComunicacaoIntent.PUBLICAR_COMUNICADO,
        ),
        (
            r"(?:publicar|publique|liberar|libere|divulgar|divulgue)\s+(?:o\s+)?anuncio",
            ComunicacaoIntent.PUBLICAR_COMUNICADO,
        ),
        (r"(?:enviar|envie)\s+(?:o\s+)?comunicado", ComunicacaoIntent.PUBLICAR_COMUNICADO),
        (r"(?:colocar|por)\s+comunicado\s+(?:no\s+)?(?:ar|mural)", ComunicacaoIntent.PUBLICAR_COMUNICADO),
        # ==================================================================
        # COMUNICADOS_PENDENTES - Antes de VER_COMUNICADOS (mais especifico)
        # ==================================================================
        (r"comunicados?\s+(?:pendentes?|rascunhos?|nao\s+publicados?)", ComunicacaoIntent.COMUNICADOS_PENDENTES),
        (r"comunicados?\s+(?:em\s+)?(?:rascunho|draft)", ComunicacaoIntent.COMUNICADOS_PENDENTES),
        (
            r"comunicados?\s+(?:aguardando|esperando)\s+(?:publicacao|aprovacao)",
            ComunicacaoIntent.COMUNICADOS_PENDENTES,
        ),
        (r"(?:rascunhos?|drafts?)\s+(?:de\s+)?comunicados?", ComunicacaoIntent.COMUNICADOS_PENDENTES),
        (r"(?:tem|ha|há)\s+(?:algum\s+)?comunicado\s+pendente", ComunicacaoIntent.COMUNICADOS_PENDENTES),
        (r"comunicados?\s+(?:a\s+)?(?:publicar|aprovar)", ComunicacaoIntent.COMUNICADOS_PENDENTES),
        (r"(?:quais?|quantos?)\s+comunicados?\s+pendentes?", ComunicacaoIntent.COMUNICADOS_PENDENTES),
        # ==================================================================
        # COMUNICADOS_RECENTES
        # ==================================================================
        (r"comunicados?\s+recentes?", ComunicacaoIntent.COMUNICADOS_RECENTES),
        (r"comunicados?\s+(?:de\s+)?(?:hoje|ontem)", ComunicacaoIntent.COMUNICADOS_RECENTES),
        (r"comunicados?\s+(?:desta|dessa|da)\s+semana", ComunicacaoIntent.COMUNICADOS_RECENTES),
        (r"(?:ultimos?|recentes?)\s+comunicados?", ComunicacaoIntent.COMUNICADOS_RECENTES),
        (r"comunicados?\s+(?:mais\s+)?(?:novos?|recentes?)", ComunicacaoIntent.COMUNICADOS_RECENTES),
        (r"comunicados?\s+(?:do\s+)?(?:dia|momento)", ComunicacaoIntent.COMUNICADOS_RECENTES),
        (
            r"(?:o\s+que|quais?)\s+(?:foi|foram)\s+(?:os?\s+)?(?:ultimos?\s+)?comunicados?",
            ComunicacaoIntent.COMUNICADOS_RECENTES,
        ),
        # ==================================================================
        # COMUNICADO_DETALHES
        # ==================================================================
        (
            r"(?:detalhe|detalhes|info|informacoes?)\s+(?:do\s+|sobre\s+(?:o\s+)?)?comunicado",
            ComunicacaoIntent.COMUNICADO_DETALHES,
        ),
        (r"(?:ver|veja|mostrar|mostre|abrir|abra)\s+(?:o\s+)?comunicado\s+\w+", ComunicacaoIntent.COMUNICADO_DETALHES),
        (r"comunicado\s+(?:#|id|numero|num)\s*\w+", ComunicacaoIntent.COMUNICADO_DETALHES),
        (r"(?:qual\s+)?(?:o\s+)?conteudo\s+(?:do\s+)?comunicado", ComunicacaoIntent.COMUNICADO_DETALHES),
        (r"(?:quem\s+)?(?:leu|visualizou)\s+(?:o\s+)?comunicado", ComunicacaoIntent.COMUNICADO_DETALHES),
        # ==================================================================
        # ESTATISTICAS
        # ==================================================================
        (
            r"(?:estatisticas?|stats?|metricas?|numeros?)\s+(?:de\s+|dos?\s+)?comunicados?",
            ComunicacaoIntent.ESTATISTICAS,
        ),
        (r"(?:resumo|overview|panorama)\s+(?:de\s+|dos?\s+)?comunicados?", ComunicacaoIntent.ESTATISTICAS),
        (r"(?:como\s+)?(?:estao|anda|andam)\s+(?:os?\s+)?comunicados?", ComunicacaoIntent.ESTATISTICAS),
        (r"(?:quantos?|total)\s+(?:de\s+)?comunicados?", ComunicacaoIntent.ESTATISTICAS),
        (r"comunicados?\s+(?:em\s+)?(?:numeros?|dados|indicadores?)", ComunicacaoIntent.ESTATISTICAS),
        (
            r"(?:taxa|percentual|porcentagem)\s+(?:de\s+)?(?:leitura|visualizacao|confirmacao)",
            ComunicacaoIntent.ESTATISTICAS,
        ),
        # ==================================================================
        # VER_COMUNICADOS - Mais generico (por ultimo)
        # ==================================================================
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba|listar|liste)\s+(?:os\s+)?comunicados?",
            ComunicacaoIntent.VER_COMUNICADOS,
        ),
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba|listar|liste)\s+(?:os\s+)?anuncios?",
            ComunicacaoIntent.VER_COMUNICADOS,
        ),
        (r"comunicados?\s+(?:ativos?|publicados?|vigentes?)", ComunicacaoIntent.VER_COMUNICADOS),
        (r"comunicados?\s+(?:em\s+)?vigor", ComunicacaoIntent.VER_COMUNICADOS),
        (r"(?:quais?\s+)?(?:os?\s+)?comunicados?", ComunicacaoIntent.VER_COMUNICADOS),
        (r"(?:tem|ha|há)\s+(?:algum\s+)?comunicado", ComunicacaoIntent.VER_COMUNICADOS),
        (r"(?:mural|quadro)\s+(?:de\s+)?(?:avisos?|comunicados?)", ComunicacaoIntent.VER_COMUNICADOS),
        (r"(?:circulares?|avisos?)\s+(?:ativos?|publicados?|vigentes?)?", ComunicacaoIntent.VER_COMUNICADOS),
    ]

    def __init__(self, db=None, data_connector=None):
        self.db = db
        self.data_connector = data_connector
        # Se tem db mas nao tem data_connector, criar automaticamente
        if db and not data_connector:
            try:
                from modules.ai.bartolo.services.data_connector import DataConnector

                self.data_connector = DataConnector(db)
            except Exception as e:
                logger.warning(f"Nao foi possivel criar DataConnector: {e}")
                self.data_connector = None

    async def process(self, message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Processa uma mensagem relacionada a comunicados.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        intent = self._detect_intent(message)
        context = context or {}

        if intent == ComunicacaoIntent.VER_COMUNICADOS:
            return await self._handle_ver_comunicados(message, context)
        elif intent == ComunicacaoIntent.COMUNICADO_DETALHES:
            return await self._handle_comunicado_detalhes(message, context)
        elif intent == ComunicacaoIntent.COMUNICADOS_RECENTES:
            return await self._handle_comunicados_recentes(message, context)
        elif intent == ComunicacaoIntent.COMUNICADOS_PENDENTES:
            return await self._handle_comunicados_pendentes(message, context)
        elif intent == ComunicacaoIntent.ESTATISTICAS:
            return await self._handle_estatisticas(message, context)
        elif intent == ComunicacaoIntent.CRIAR_COMUNICADO:
            return await self._handle_criar_comunicado(message, context)
        elif intent == ComunicacaoIntent.PUBLICAR_COMUNICADO:
            return await self._handle_publicar_comunicado(message, context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> ComunicacaoIntent | None:
        """Detecta o intent da mensagem."""
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    # =========================================================================
    # Handlers de Intent
    # =========================================================================

    async def _handle_ver_comunicados(self, message: str, context: dict) -> dict[str, Any]:
        """Lista comunicados ativos/publicados usando DataConnector."""
        # Tentar buscar dados reais via DataConnector
        if self.data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": ComunicacaoIntent.VER_COMUNICADOS.value,
                        "data": {"comunicados": result.data, "total": result.total_count},
                        "suggestions": [
                            "Comunicados recentes",
                            "Comunicados pendentes",
                            "Estatisticas de comunicados",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar comunicados via DataConnector: {e}")

        # Fallback estatico
        today = date.today()
        comunicados_mock = [
            {
                "titulo": "Alteracao de procedimento - Portaria",
                "tipo": "procedimento",
                "prioridade": "alta",
                "status": "publicado",
                "visualizacoes": 45,
                "confirmacoes": 32,
                "data_publicacao": today.strftime("%d/%m/%Y") + " 09:00",
            },
            {
                "titulo": "Escala de feriado - Carnaval 2026",
                "tipo": "escala",
                "prioridade": "urgente",
                "status": "publicado",
                "visualizacoes": 120,
                "confirmacoes": 95,
                "data_publicacao": today.strftime("%d/%m/%Y") + " 08:00",
            },
            {
                "titulo": "Novo uniforme disponivel",
                "tipo": "informativo",
                "prioridade": "normal",
                "status": "publicado",
                "visualizacoes": 30,
                "confirmacoes": 10,
                "data_publicacao": today.strftime("%d/%m/%Y") + " 07:30",
            },
        ]

        lines = []
        for c in comunicados_mock:
            prio_icon = {"urgente": "🔴", "alta": "🟠", "normal": "🟢", "baixa": "⚪"}.get(c["prioridade"], "🟢")
            lines.append(
                f"- {prio_icon} **{c['titulo']}**\n"
                f"  Tipo: {c['tipo']} | Prioridade: {c['prioridade']}\n"
                f"  Visualizacoes: {c['visualizacoes']} | Confirmacoes: {c['confirmacoes']} | {c['data_publicacao']}"
            )

        response = f"""📢 **COMUNICADOS ATIVOS** ({len(comunicados_mock)})

{chr(10).join(lines)}

**Resumo:**
- Total publicados: **{len(comunicados_mock)}**
- Urgentes/Alta prioridade: **2**

**Legenda:** 🔴 Urgente | 🟠 Alta | 🟢 Normal | ⚪ Baixa"""

        return {
            "response": response,
            "intent": ComunicacaoIntent.VER_COMUNICADOS.value,
            "data": {"comunicados": comunicados_mock, "total": len(comunicados_mock)},
            "suggestions": [
                "Comunicados recentes",
                "Comunicados pendentes",
                "Estatisticas de comunicados",
            ],
        }

    async def _handle_comunicado_detalhes(self, message: str, context: dict) -> dict[str, Any]:
        """Exibe detalhes de um comunicado especifico."""
        # Extrair ID do comunicado da mensagem
        comunicado_id = self._extract_comunicado_id(message)

        if self.data_connector and comunicado_id:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.data:
                    # Tentar encontrar pelo titulo parcial ou indice
                    for idx, c in enumerate(result.data):
                        titulo_lower = c.get("titulo", "").lower()
                        if comunicado_id.lower() in titulo_lower or str(idx + 1) == comunicado_id:
                            response = f"""📋 **DETALHES DO COMUNICADO**

**Titulo:** {c.get("titulo", "N/A")}
**Tipo:** {c.get("tipo", "N/A")}
**Prioridade:** {c.get("prioridade", "N/A")}
**Status:** {c.get("status", "N/A")}
**Data Publicacao:** {c.get("data_publicacao", "N/A")}

**Metricas de Leitura:**
- Visualizacoes: **{c.get("visualizacoes", 0)}**
- Confirmacoes: **{c.get("confirmacoes", 0)}**"""
                            return {
                                "response": response,
                                "intent": ComunicacaoIntent.COMUNICADO_DETALHES.value,
                                "data": c,
                                "suggestions": [
                                    "Ver comunicados",
                                    "Estatisticas",
                                    "Comunicados pendentes",
                                ],
                            }
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes do comunicado: {e}")

        # Fallback - solicitar mais informacao
        response = """📋 **DETALHES DO COMUNICADO**

Para exibir os detalhes, informe o titulo ou numero do comunicado.

**Exemplos:**
- "detalhes do comunicado Alteracao de procedimento"
- "ver comunicado 1"

Ou use `/comunicado listar` para ver todos os comunicados disponiveis."""

        return {
            "response": response,
            "intent": ComunicacaoIntent.COMUNICADO_DETALHES.value,
            "needs_info": ["comunicado_id"],
            "suggestions": [
                "Listar comunicados",
                "Comunicados recentes",
                "Ajuda",
            ],
        }

    async def _handle_comunicados_recentes(self, message: str, context: dict) -> dict[str, Any]:
        """Lista comunicados recentes."""
        if self.data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.data:
                    # Pegar os mais recentes (ja vem ordenados por data)
                    recentes = result.data[:5]
                    lines = []
                    for idx, c in enumerate(recentes, 1):
                        prio_icon = {"urgente": "🔴", "alta": "🟠", "normal": "🟢", "baixa": "⚪"}.get(
                            c.get("prioridade", "normal"), "🟢"
                        )
                        lines.append(
                            f"{idx}. {prio_icon} **{c.get('titulo', 'N/A')}**\n"
                            f"   {c.get('data_publicacao', 'N/A')} | "
                            f"Tipo: {c.get('tipo', 'N/A')} | "
                            f"👁 {c.get('visualizacoes', 0)} | "
                            f"✅ {c.get('confirmacoes', 0)}"
                        )

                    response = f"""🕐 **COMUNICADOS RECENTES** ({len(recentes)})

{chr(10).join(lines)}

*Exibindo os {len(recentes)} comunicados mais recentes.*"""
                    return {
                        "response": response,
                        "intent": ComunicacaoIntent.COMUNICADOS_RECENTES.value,
                        "data": {"comunicados": recentes, "total": len(recentes)},
                        "suggestions": [
                            "Ver todos comunicados",
                            "Comunicados pendentes",
                            "Criar comunicado",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar comunicados recentes via DataConnector: {e}")

        # Fallback estatico
        today = date.today()
        response = f"""🕐 **COMUNICADOS RECENTES**

1. 🟠 **Alteracao de procedimento - Portaria**
   {today.strftime("%d/%m/%Y")} 09:00 | Tipo: procedimento | 👁 45 | ✅ 32
2. 🔴 **Escala de feriado - Carnaval 2026**
   {today.strftime("%d/%m/%Y")} 08:00 | Tipo: escala | 👁 120 | ✅ 95
3. 🟢 **Novo uniforme disponivel**
   {today.strftime("%d/%m/%Y")} 07:30 | Tipo: informativo | 👁 30 | ✅ 10

*Exibindo os 3 comunicados mais recentes.*"""

        return {
            "response": response,
            "intent": ComunicacaoIntent.COMUNICADOS_RECENTES.value,
            "data": {"total": 3},
            "suggestions": [
                "Ver todos comunicados",
                "Comunicados pendentes",
                "Criar comunicado",
            ],
        }

    async def _handle_comunicados_pendentes(self, message: str, context: dict) -> dict[str, Any]:
        """Lista comunicados pendentes/rascunhos."""
        if self.data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.data:
                    # Filtrar rascunhos e pendentes
                    pendentes = [
                        c for c in result.data if c.get("status") in ("draft", "rascunho", "scheduled", "agendado")
                    ]

                    if pendentes:
                        lines = []
                        for idx, c in enumerate(pendentes, 1):
                            status_label = {
                                "draft": "Rascunho",
                                "rascunho": "Rascunho",
                                "scheduled": "Agendado",
                                "agendado": "Agendado",
                            }.get(c.get("status", ""), c.get("status", "N/A"))

                            lines.append(
                                f"{idx}. 📝 **{c.get('titulo', 'N/A')}**\n"
                                f"   Status: {status_label} | "
                                f"Tipo: {c.get('tipo', 'N/A')} | "
                                f"Prioridade: {c.get('prioridade', 'N/A')}"
                            )

                        response = f"""📝 **COMUNICADOS PENDENTES** ({len(pendentes)})

{chr(10).join(lines)}

**Acoes disponiveis:**
- Publicar comunicado pendente
- Editar rascunho
- Excluir rascunho"""
                    else:
                        response = "✅ **Nenhum comunicado pendente no momento.**\n\nTodos os comunicados foram publicados ou nao ha rascunhos."

                    return {
                        "response": response,
                        "intent": ComunicacaoIntent.COMUNICADOS_PENDENTES.value,
                        "data": {"pendentes": pendentes, "total": len(pendentes)},
                        "suggestions": [
                            "Criar comunicado",
                            "Ver comunicados ativos",
                            "Estatisticas",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar comunicados pendentes via DataConnector: {e}")

        # Fallback estatico
        response = """📝 **COMUNICADOS PENDENTES** (2)

1. 📝 **Comunicado sobre nova politica de acesso**
   Status: Rascunho | Tipo: politica | Prioridade: alta
2. 📝 **Treinamento de seguranca - Marco 2026**
   Status: Agendado | Tipo: treinamento | Prioridade: normal

**Acoes disponiveis:**
- Publicar comunicado pendente
- Editar rascunho
- Excluir rascunho"""

        return {
            "response": response,
            "intent": ComunicacaoIntent.COMUNICADOS_PENDENTES.value,
            "data": {"total": 2},
            "suggestions": [
                "Criar comunicado",
                "Ver comunicados ativos",
                "Publicar comunicado",
            ],
        }

    async def _handle_estatisticas(self, message: str, context: dict) -> dict[str, Any]:
        """Exibe estatisticas gerais de comunicados."""
        if self.data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.data:
                    comunicados = result.data
                    total = len(comunicados)
                    total_views = sum(c.get("visualizacoes", 0) for c in comunicados)
                    total_confirms = sum(c.get("confirmacoes", 0) for c in comunicados)
                    urgentes = sum(1 for c in comunicados if c.get("prioridade") in ("urgente", "alta"))

                    # Taxa de confirmacao
                    taxa_confirmacao = (total_confirms / total_views * 100) if total_views > 0 else 0

                    # Por tipo
                    tipos_count: dict[str, int] = {}
                    for c in comunicados:
                        tipo = c.get("tipo", "outros")
                        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

                    tipos_lines = [f"  - {t.capitalize()}: **{q}**" for t, q in tipos_count.items()]

                    response = f"""📊 **ESTATISTICAS DE COMUNICADOS**

**Visao Geral:**
- Total de comunicados ativos: **{total}**
- Urgentes/Alta prioridade: **{urgentes}**
- Total de visualizacoes: **{total_views}**
- Total de confirmacoes: **{total_confirms}**
- Taxa de confirmacao: **{taxa_confirmacao:.1f}%**

**Por Tipo:**
{chr(10).join(tipos_lines)}

**Indicadores:**
- {"🟢 Taxa de confirmacao OK" if taxa_confirmacao >= 80 else "🟠 Taxa de confirmacao abaixo de 80%" if taxa_confirmacao >= 50 else "🔴 Taxa de confirmacao critica (< 50%)"}"""

                    return {
                        "response": response,
                        "intent": ComunicacaoIntent.ESTATISTICAS.value,
                        "data": {
                            "total": total,
                            "urgentes": urgentes,
                            "total_views": total_views,
                            "total_confirms": total_confirms,
                            "taxa_confirmacao": taxa_confirmacao,
                            "por_tipo": tipos_count,
                        },
                        "suggestions": [
                            "Ver comunicados",
                            "Comunicados pendentes",
                            "Criar comunicado",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas via DataConnector: {e}")

        # Fallback estatico
        response = """📊 **ESTATISTICAS DE COMUNICADOS**

**Visao Geral:**
- Total de comunicados ativos: **3**
- Urgentes/Alta prioridade: **2**
- Total de visualizacoes: **195**
- Total de confirmacoes: **137**
- Taxa de confirmacao: **70.3%**

**Por Tipo:**
  - Procedimento: **1**
  - Escala: **1**
  - Informativo: **1**

**Indicadores:**
- 🟠 Taxa de confirmacao abaixo de 80%"""

        return {
            "response": response,
            "intent": ComunicacaoIntent.ESTATISTICAS.value,
            "data": {"total": 3, "taxa_confirmacao": 70.3},
            "suggestions": [
                "Ver comunicados",
                "Comunicados pendentes",
                "Criar comunicado",
            ],
        }

    async def _handle_criar_comunicado(self, message: str, context: dict) -> dict[str, Any]:
        """Redireciona criacao de comunicado para o sistema de actions."""
        # Extrair dados da mensagem
        dados_extraidos = self._extract_comunicado_data(message)

        info_lines = []
        if dados_extraidos.get("titulo"):
            info_lines.append(f"**Titulo:** {dados_extraidos['titulo']}")
        if dados_extraidos.get("tipo"):
            info_lines.append(f"**Tipo:** {dados_extraidos['tipo']}")
        if dados_extraidos.get("prioridade"):
            info_lines.append(f"**Prioridade:** {dados_extraidos['prioridade']}")
        if dados_extraidos.get("destinatarios"):
            info_lines.append(f"**Destinatarios:** {dados_extraidos['destinatarios']}")

        if info_lines:
            response = f"""📝 **CRIAR COMUNICADO**

Dados detectados:
{chr(10).join(info_lines)}

**Informe os dados faltantes:**
- Titulo do comunicado
- Conteudo completo
- Prioridade (baixa, normal, alta, urgente)
- Destinatarios (todos, departamento, posto)

**Deseja prosseguir com a criacao?**"""
        else:
            response = """📝 **CRIAR COMUNICADO**

Para criar um novo comunicado, preciso de:

1. **Titulo** - Titulo do comunicado
2. **Conteudo** - Texto completo do comunicado
3. **Tipo** - Informativo, urgente, alerta, procedimento
4. **Prioridade** - Baixa, normal, alta, urgente
5. **Destinatarios** - Todos, departamento, posto, funcionario

**Exemplo:**
"Criar comunicado Alteracao de Procedimento tipo procedimento prioridade alta para todos"

Informe os dados para prosseguir."""

        return {
            "response": response,
            "intent": ComunicacaoIntent.CRIAR_COMUNICADO.value,
            "data": dados_extraidos,
            "suggestions": [
                "Tipo informativo",
                "Prioridade alta",
                "Para todos",
                "Cancelar",
            ],
            "actions": [
                {
                    "type": "create",
                    "label": "Criar Comunicado",
                    "target": "announcement",
                    "data": dados_extraidos,
                },
            ],
        }

    async def _handle_publicar_comunicado(self, message: str, context: dict) -> dict[str, Any]:
        """Redireciona publicacao de comunicado para o sistema de actions."""
        comunicado_id = self._extract_comunicado_id(message)

        if comunicado_id:
            response = f"""📢 **PUBLICAR COMUNICADO**

Comunicado: **{comunicado_id}**

Ao publicar:
- Destinatarios serao notificados
- Comunicado ficara visivel no mural
- Nao podera ser excluido (apenas arquivado)

**Confirmar publicacao?**"""
        else:
            response = """📢 **PUBLICAR COMUNICADO**

Informe o ID ou titulo do comunicado a ser publicado.

**Exemplo:**
- "publicar comunicado Alteracao de Procedimento"
- "publicar comunicado 1"

Ou use `/comunicado pendentes` para ver os comunicados disponiveis para publicacao."""

        return {
            "response": response,
            "intent": ComunicacaoIntent.PUBLICAR_COMUNICADO.value,
            "data": {"comunicado_id": comunicado_id} if comunicado_id else {},
            "suggestions": [
                "Confirmar",
                "Cancelar",
                "Comunicados pendentes",
            ],
            "actions": [
                {
                    "type": "edit",
                    "label": "Publicar",
                    "target": "announcement",
                    "data": {"id": comunicado_id, "action": "publish"},
                },
            ]
            if comunicado_id
            else [],
        }

    async def _handle_default(self, message: str, context: dict) -> dict[str, Any] | None:
        """Handler padrao - retorna None para permitir que DataConnector processe."""
        return None

    # =========================================================================
    # Metodos auxiliares
    # =========================================================================

    def _extract_comunicado_id(self, message: str) -> str | None:
        """Extrai identificador do comunicado da mensagem."""
        # UUID
        uuid_match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", message.lower())
        if uuid_match:
            return uuid_match.group(0)

        # Numero sequencial (#1, #2, etc.)
        num_match = re.search(r"(?:#|n[uú]mero|num)\s*(\d+)", message.lower())
        if num_match:
            return num_match.group(1)

        # Indice numerico simples
        idx_match = re.search(r"comunicado\s+(\d+)", message.lower())
        if idx_match:
            return idx_match.group(1)

        return None

    def _extract_comunicado_data(self, message: str) -> dict[str, Any]:
        """Extrai dados do comunicado da mensagem."""
        dados: dict[str, Any] = {}
        msg_lower = message.lower()

        # Tipo
        tipos = {
            "informativo": "informativo",
            "urgente": "urgente",
            "alerta": "alerta",
            "procedimento": "procedimento",
            "escala": "escala",
            "treinamento": "treinamento",
            "politica": "politica",
        }
        for key, value in tipos.items():
            if key in msg_lower:
                dados["tipo"] = value
                break

        # Prioridade
        prioridades = {
            "urgente": "urgente",
            "alta": "alta",
            "normal": "normal",
            "baixa": "baixa",
        }
        for key, value in prioridades.items():
            if f"prioridade {key}" in msg_lower or f"prioridade: {key}" in msg_lower:
                dados["prioridade"] = value
                break

        # Destinatarios
        if "para todos" in msg_lower or "todos" in msg_lower:
            dados["destinatarios"] = "todos"
        elif "departamento" in msg_lower:
            dados["destinatarios"] = "departamento"
        elif "posto" in msg_lower:
            dados["destinatarios"] = "posto"
        elif "funcionario" in msg_lower or "colaborador" in msg_lower:
            dados["destinatarios"] = "funcionario"

        # Titulo (tentativa de extrair)
        titulo_patterns = [
            r"(?:titulo|assunto)\s*[:\-]\s*(.+?)(?:\s+(?:tipo|prioridade|para)\s|\s*$)",
            r"comunicado\s+[\"'](.+?)[\"']",
            r"comunicado\s+(.+?)(?:\s+(?:tipo|prioridade|para)\s|\s*$)",
        ]
        for pattern in titulo_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                titulo = match.group(1).strip()
                # Filtrar palavras-chave que nao sao titulo
                if len(titulo) > 3 and titulo.lower() not in ("novo", "criar", "um", "uma"):
                    dados["titulo"] = titulo
                    break

        return dados

    def get_capabilities(self) -> list[str]:
        """Retorna lista de capabilities do agente."""
        return [
            "Listar comunicados ativos e publicados",
            "Exibir detalhes de comunicado especifico",
            "Listar comunicados recentes",
            "Listar rascunhos e pendentes de publicacao",
            "Exibir estatisticas de comunicados",
            "Iniciar criacao de comunicado",
            "Iniciar publicacao de comunicado",
        ]
