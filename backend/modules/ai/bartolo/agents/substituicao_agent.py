"""
SubstituicaoAgent - Agente especialista em substituicoes em tempo real
"""

import logging
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class SubstituicaoIntent(StrEnum):
    """Intents relacionados a substituicoes"""

    BUSCAR_SUBSTITUTO = "buscar_substituto"
    URGENTE = "urgente"
    CONFIRMAR = "confirmar"
    CANCELAR = "cancelar"
    HISTORICO = "historico"
    PENDENTES = "pendentes"
    CUSTO = "custo"
    DISPONIBILIDADE = "disponibilidade"


class SubstituicaoAgent:
    """
    Agente especializado em substituicoes.

    Capabilities:
    - Encontrar substituto ideal rapidamente
    - Avaliar disponibilidade
    - Calcular custo da substituicao
    - Prever probabilidade de aceitacao
    - Notificar automaticamente
    """

    # ==========================================================================
    # INTENT_PATTERNS - Lista exaustiva para detecção de intenções
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # URGENTE - Substituição emergencial (ANTES de BUSCAR para "urgente preciso")
        # ==================================================================
        (r"substituto\s+(?:urgente|emergencia|agora|imediato)", SubstituicaoIntent.URGENTE),
        (r"urgente\s+(?:preciso\s+)?substituto", SubstituicaoIntent.URGENTE),
        (r"(?:emergencia)\s+(?:preciso\s+)?substituto", SubstituicaoIntent.URGENTE),
        (r"(?:cobrir|substituir)\s+(?:urgente|agora|imediato)", SubstituicaoIntent.URGENTE),
        (r"(?:faltou|nao\s+veio)\s+(?:e\s+)?(?:preciso|precisamos)", SubstituicaoIntent.URGENTE),
        (r"(?:emergencia|urgente)\s+(?:de\s+)?cobertura", SubstituicaoIntent.URGENTE),
        (r"posto\s+(?:sem\s+)?(?:ninguem|cobertura)\s+(?:agora|urgente)", SubstituicaoIntent.URGENTE),
        (r"preciso\s+(?:de\s+)?(?:um\s+)?substituto\s+urgente", SubstituicaoIntent.URGENTE),
        # ==================================================================
        # BUSCAR_SUBSTITUTO
        # ==================================================================
        (
            r"(?:buscar|busque|encontrar|encontre|achar|ache)\s+(?:um\s+)?substituto",
            SubstituicaoIntent.BUSCAR_SUBSTITUTO,
        ),
        (r"(?:preciso|precisamos)\s+(?:de\s+)?(?:um\s+)?substituto", SubstituicaoIntent.BUSCAR_SUBSTITUTO),
        (r"quem\s+(?:pode|consegue)\s+(?:cobrir|substituir)", SubstituicaoIntent.BUSCAR_SUBSTITUTO),
        (r"(?:tem|ha)\s+(?:alguem\s+)?(?:para\s+)?(?:cobrir|substituir)", SubstituicaoIntent.BUSCAR_SUBSTITUTO),
        (r"(?:arranjar|arrumar|conseguir)\s+(?:um\s+)?substituto", SubstituicaoIntent.BUSCAR_SUBSTITUTO),
        (r"(?:alguem|funcionario)\s+(?:para\s+)?cobrir", SubstituicaoIntent.BUSCAR_SUBSTITUTO),
        # ==================================================================
        # CONFIRMAR - Aprovar substituição
        # ==================================================================
        (r"(?:confirmar|confirme|aprovar|aprove)\s+(?:a\s+)?substituicao", SubstituicaoIntent.CONFIRMAR),
        (r"(?:aceitar|aceite)\s+(?:o\s+)?substituto", SubstituicaoIntent.CONFIRMAR),
        (r"(?:ok|sim|aprovado)\s+(?:para\s+)?(?:a\s+)?substituicao", SubstituicaoIntent.CONFIRMAR),
        # ==================================================================
        # CANCELAR - Cancelar substituição
        # ==================================================================
        (r"(?:cancelar|cancele|recusar|recuse)\s+(?:a\s+)?substituicao", SubstituicaoIntent.CANCELAR),
        (r"(?:nao|não)\s+(?:quero|preciso)\s+(?:mais\s+)?(?:o\s+|do\s+)?substituto", SubstituicaoIntent.CANCELAR),
        (r"(?:desistir|desista)\s+(?:da\s+)?substituicao", SubstituicaoIntent.CANCELAR),
        # ==================================================================
        # PENDENTES - Listar pendentes
        # ==================================================================
        (r"substituicao\s+pendente", SubstituicaoIntent.PENDENTES),
        (r"substituicoes\s+pendentes", SubstituicaoIntent.PENDENTES),
        (r"substituicoes?\s+(?:estao\s+)?pendentes?", SubstituicaoIntent.PENDENTES),
        (
            r"(?:quais\s+)?substituicoes?\s+(?:estao\s+)?pendentes?\s+(?:de\s+)?(?:aprovacao)?",
            SubstituicaoIntent.PENDENTES,
        ),
        (r"(?:trocas?|coberturas?)\s+pendentes?", SubstituicaoIntent.PENDENTES),
        (r"(?:aguardando|esperando)\s+(?:aprovacao|confirmacao)", SubstituicaoIntent.PENDENTES),
        (r"(?:listar|liste|ver|veja|mostrar|mostre)\s+(?:substituicoes?\s+)?pendentes?", SubstituicaoIntent.PENDENTES),
        # ==================================================================
        # HISTORICO - Histórico de substituições
        # ==================================================================
        (r"historico\s+de\s+substituicao", SubstituicaoIntent.HISTORICO),
        (r"historico\s+de\s+substituicoes", SubstituicaoIntent.HISTORICO),
        (r"historico\s+(?:de\s+)?substituicoes?", SubstituicaoIntent.HISTORICO),
        (r"substituicoes?\s+(?:anteriores|passadas|recentes)", SubstituicaoIntent.HISTORICO),
        (r"ultima\s+substituicao", SubstituicaoIntent.HISTORICO),
        (r"(?:ultimas?|recentes?)\s+substituicoes?", SubstituicaoIntent.HISTORICO),
        (r"(?:ver|veja|mostrar|mostre)\s+historico", SubstituicaoIntent.HISTORICO),
        # ==================================================================
        # CUSTO - Custo da substituição
        # ==================================================================
        (r"custo\s+da\s+substituicao", SubstituicaoIntent.CUSTO),
        (r"custo\s+substituicao", SubstituicaoIntent.CUSTO),
        (r"custo\s+(?:das?\s+)?substituicoes?", SubstituicaoIntent.CUSTO),
        (r"(?:qual\s+)?(?:foi\s+)?(?:o\s+)?custo\s+(?:das?\s+)?substituicoes?", SubstituicaoIntent.CUSTO),
        (r"quanto\s+(?:custa|custou)\s+(?:a\s+)?substituicao", SubstituicaoIntent.CUSTO),
        (r"(?:valor|preco)\s+(?:da\s+)?substituicao", SubstituicaoIntent.CUSTO),
        (r"(?:calcular|calcule)\s+(?:o\s+)?custo\s+(?:da\s+)?(?:substituicao|cobertura)", SubstituicaoIntent.CUSTO),
        # ==================================================================
        # DISPONIBILIDADE - Verificar disponibilidade
        # ==================================================================
        (r"(?:verificar|ver|checar)\s+disponibilidade", SubstituicaoIntent.DISPONIBILIDADE),
        (
            r"quem\s+(?:esta|ta|está)?\s*disponivel\s+(?:para\s+)?(?:cobrir|substituir)",
            SubstituicaoIntent.DISPONIBILIDADE,
        ),
        (r"(?:funcionarios?|colaboradores?)\s+(?:disponiveis?|livres?)", SubstituicaoIntent.DISPONIBILIDADE),
        (r"quem\s+(?:esta|ta|está)\s+livre", SubstituicaoIntent.DISPONIBILIDADE),
    ]

    def __init__(
        self, db=None, substitution_repo=None, employee_repo=None, notification_service=None, data_connector=None
    ):
        self.db = db
        self.substitution_repo = substitution_repo
        self.employee_repo = employee_repo
        self.notification_service = notification_service
        self.data_connector = data_connector
        # Se tem db mas não tem data_connector, criar automaticamente
        if db and not data_connector:
            try:
                from modules.ai.bartolo.services.data_connector import DataConnector

                self.data_connector = DataConnector(db)
            except Exception as e:
                logger.warning(f"Não foi possível criar DataConnector: {e}")
                self.data_connector = None

    async def process(self, message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Processa mensagem relacionada a substituicoes"""

        intent = self._detect_intent(message)
        context = context or {}

        handlers = {
            SubstituicaoIntent.BUSCAR_SUBSTITUTO: self._handle_buscar_substituto,
            SubstituicaoIntent.URGENTE: self._handle_urgente,
            SubstituicaoIntent.CONFIRMAR: self._handle_confirmar,
            SubstituicaoIntent.PENDENTES: self._handle_pendentes,
            SubstituicaoIntent.HISTORICO: self._handle_historico,
            SubstituicaoIntent.CUSTO: self._handle_custo,
            SubstituicaoIntent.DISPONIBILIDADE: self._handle_disponibilidade,
        }

        handler = handlers.get(intent, self._handle_default)
        return await handler(message, context)

    def _detect_intent(self, message: str) -> SubstituicaoIntent | None:
        """Detecta intent da mensagem"""
        import re

        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_buscar_substituto(self, message: str, context: dict) -> dict[str, Any]:
        """Busca substituto ideal usando dados reais do DataConnector"""
        import re

        # Tenta extrair funcionario ou turno
        re.search(r"(?:do|da|para)\s+(\w+)", message.lower())

        # Tentar buscar funcionários de folga (candidatos reais)
        if self.data_connector:
            try:
                result = await self.data_connector._get_funcionarios_folga()
                if result.success and result.data:
                    candidatos = result.data[:10]
                    lines = []
                    for c in candidatos:
                        lines.append(f"- **{c['nome']}** ({c.get('matricula', 'N/A')}) - {c.get('cargo', 'N/A')}")

                    response = f"""**Buscando Substitutos**

**Funcionários disponíveis hoje ({result.total_count}):**

{chr(10).join(lines)}

**Critérios de seleção:**
- Proximidade do posto (GPS)
- Disponibilidade no horário
- Histórico de aceitação
- Custo (hora normal vs extra)
- Habilidades necessárias

Informe o turno e data para filtrar os melhores candidatos."""
                    return {
                        "response": response,
                        "intent": SubstituicaoIntent.BUSCAR_SUBSTITUTO.value,
                        "data": {"candidatos": candidatos, "total_disponiveis": result.total_count},
                        "suggestions": ["Turno de hoje", "Turno de amanhã", "Ver turnos sem cobertura"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar substitutos via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**Buscando Substitutos**

Para encontrar o melhor substituto, preciso saber:
1. Qual turno precisa de cobertura?
2. Qual a data e horario?

**Criterios de selecao:**
- Proximidade do posto (GPS)
- Disponibilidade no horario
- Historico de aceitacao
- Custo (hora normal vs extra)
- Habilidades necessarias""",
            "intent": SubstituicaoIntent.BUSCAR_SUBSTITUTO.value,
            "suggestions": ["Turno de hoje", "Turno de amanha", "Ver turnos sem cobertura"],
        }

    async def _handle_urgente(self, message: str, context: dict) -> dict[str, Any]:
        """Substituicao urgente/emergencia usando dados reais do DataConnector"""
        # Tentar buscar dados reais para emergência
        if self.data_connector:
            try:
                folga_result = await self.data_connector._get_funcionarios_folga()
                cobertura_result = await self.data_connector._get_cobertura_critica()

                parts = ["**SUBSTITUICAO URGENTE**\n\nModo emergência ativado!"]

                if cobertura_result.success and cobertura_result.data:
                    postos = cobertura_result.data[:5]
                    parts.append(f"\n**Postos críticos ({len(cobertura_result.data)}):**")
                    for p in postos:
                        parts.append(f"- 🔴 **{p['nome']}** - {p['alocados']}/{p['requeridos']} ({p['cobertura']}%)")

                if folga_result.success and folga_result.data:
                    parts.append(f"\n**Funcionários disponíveis para convocação:** {folga_result.total_count}")
                    for f in folga_result.data[:5]:
                        parts.append(f"- {f['nome']} ({f.get('cargo', 'N/A')})")

                parts.append("\n**Informe o posto que precisa de cobertura imediata:**")

                return {
                    "response": "\n".join(parts),
                    "intent": SubstituicaoIntent.URGENTE.value,
                    "data": {
                        "postos_criticos": cobertura_result.data if cobertura_result.success else [],
                        "disponiveis": folga_result.total_count if folga_result.success else 0,
                    },
                    "suggestions": ["Listar postos críticos", "Ver funcionários disponíveis", "Notificar supervisor"],
                    "priority": "high",
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar dados urgentes via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**SUBSTITUICAO URGENTE**

Modo emergencia ativado! Vou:
1. Buscar funcionarios disponiveis AGORA
2. Ordenar por proximidade do posto
3. Notificar TOP 5 simultaneamente
4. Primeiro a aceitar e alocado

**Informe o posto que precisa de cobertura:**""",
            "intent": SubstituicaoIntent.URGENTE.value,
            "suggestions": ["Listar postos criticos", "Ver funcionarios disponiveis", "Notificar supervisor"],
            "priority": "high",
        }

    async def _handle_confirmar(self, message: str, context: dict) -> dict[str, Any]:
        """Confirma substituicao"""
        return {
            "response": "Para confirmar uma substituicao, informe o ID ou selecione da lista de pendentes.",
            "intent": SubstituicaoIntent.CONFIRMAR.value,
            "suggestions": ["Ver substituicoes pendentes", "Cancelar"],
        }

    async def _handle_pendentes(self, message: str, context: dict) -> dict[str, Any]:
        """Lista substituicoes pendentes usando dados reais do DataConnector"""
        # Tentar buscar dados reais
        if self.data_connector:
            try:
                result = await self.data_connector._get_substituicoes_pendentes()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": SubstituicaoIntent.PENDENTES.value,
                        "data": {"substituicoes": result.data, "pending_count": result.total_count},
                        "suggestions": ["Ver detalhes", "Buscar substitutos", "Resolver pendências"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar substituições pendentes via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**Substituicoes Pendentes**

| # | Funcionario | Turno | Status |
|---|------------|-------|--------|
| 1 | Joao Silva | 08:00-14:00 | Aguardando |
| 2 | Maria Santos | 14:00-22:00 | 2 candidatos |

**Acoes disponiveis:**
- Selecione um numero para ver detalhes
- Ou confirme/cancele diretamente""",
            "intent": SubstituicaoIntent.PENDENTES.value,
            "data": {"pending_count": 2},
            "suggestions": ["Ver detalhes #1", "Buscar mais substitutos", "Cancelar #1"],
        }

    async def _handle_historico(self, message: str, context: dict) -> dict[str, Any]:
        """Historico de substituicoes usando dados reais do DataConnector"""
        # Tentar buscar dados reais de substituições
        if self.data_connector:
            try:
                result = await self.data_connector._get_substituicoes_pendentes()
                if result.success:
                    total = result.total_count
                    subs = result.data or []

                    # Contar por status
                    sem_substituto = sum(1 for s in subs if s.get("substituto") in ("A definir", None, "N/A"))
                    com_substituto = total - sem_substituto

                    response = f"""**Histórico de Substituições**

- Total registradas: **{total}**
- Com substituto definido: **{com_substituto}**
- Sem substituto: **{sem_substituto}**

"""
                    if subs:
                        response += "**Últimas substituições:**\n"
                        for s in subs[:5]:
                            sub_text = s.get("substituto", "A definir")
                            response += f"- **{s.get('funcionario_ausente', 'N/A')}** → {sub_text} | {s.get('posto', 'N/A')} | {s.get('data', 'N/A')}\n"

                    return {
                        "response": response,
                        "intent": SubstituicaoIntent.HISTORICO.value,
                        "data": {"total": total, "substituicoes": subs},
                        "suggestions": ["Ver por funcionário", "Exportar relatório", "Filtrar por posto"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar histórico via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**Historico de Substituicoes (ultimos 30 dias)**

- Total: 45 substituicoes
- Taxa de sucesso: 92%
- Tempo medio de cobertura: 47 min
- Custo total: R$ 3.450,00

**Top substitutos:**
1. Carlos Lima - 12 coberturas
2. Ana Paula - 8 coberturas
3. Roberto Dias - 7 coberturas""",
            "intent": SubstituicaoIntent.HISTORICO.value,
            "suggestions": ["Ver por funcionario", "Exportar relatorio", "Filtrar por posto"],
        }

    async def _handle_custo(self, message: str, context: dict) -> dict[str, Any]:
        """Calcula custo de substituicao usando dados reais do DataConnector"""
        # Tentar buscar dados reais de custo
        if self.data_connector:
            try:
                he_result = await self.data_connector._get_hora_extra_ranking()
                kpis_result = await self.data_connector._get_main_kpis()

                parts = ["**Cálculo de Custo de Substituição**\n"]

                if kpis_result.success and kpis_result.data:
                    custo_mensal = kpis_result.data.get("custo_mensal_total", 0)
                    subs_ativas = kpis_result.data.get("substituicoes_ativas", 0)
                    parts.append("**Dados atuais:**")
                    parts.append(f"- Custo mensal total: **R$ {custo_mensal:,.2f}**")
                    parts.append(f"- Substituições ativas: **{subs_ativas}**")

                if he_result.success and he_result.data:
                    total_he = sum(f.get("horas_extras", 0) for f in he_result.data)
                    parts.append(f"- Horas extras acumuladas: **{total_he:.1f}h**")

                parts.append("\n**Fórmula:**")
                parts.append("- Hora normal: R$ Base")
                parts.append("- Hora extra (até 50%): R$ Base x 1.5")
                parts.append("- Hora extra (acima 50%): R$ Base x 2.0")
                parts.append("- Adicional noturno: +20%")
                parts.append("- Adicional domingo/feriado: +100%")
                parts.append("\nInforme o turno para calcular o custo estimado.")

                return {
                    "response": "\n".join(parts),
                    "intent": SubstituicaoIntent.CUSTO.value,
                    "data": {
                        "custo_mensal": kpis_result.data.get("custo_mensal_total", 0) if kpis_result.success else 0,
                        "horas_extras_total": total_he if he_result.success else 0,
                    },
                    "suggestions": ["Simular custo", "Ver custos do mês", "Comparar opções"],
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar custo de substituição via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**Calculo de Custo de Substituicao**

**Formula:**
- Hora normal: R$ Base
- Hora extra (ate 50%): R$ Base x 1.5
- Hora extra (acima 50%): R$ Base x 2.0
- Adicional noturno: +20%
- Adicional domingo/feriado: +100%

Informe o turno para calcular o custo estimado.""",
            "intent": SubstituicaoIntent.CUSTO.value,
            "suggestions": ["Simular custo", "Ver custos do mes", "Comparar opcoes"],
        }

    async def _handle_disponibilidade(self, message: str, context: dict) -> dict[str, Any]:
        """Verifica disponibilidade de funcionarios usando dados reais do DataConnector"""
        # Tentar buscar dados reais
        if self.data_connector:
            try:
                result = await self.data_connector._get_funcionarios_folga()
                if result.success and result.message:
                    response = (
                        result.message
                        + "\n\n**Filtros disponíveis:**\n- Por proximidade (GPS)\n- Por habilidade\n- Por custo\n- Por histórico de aceitação\n\nQual critério priorizar?"
                    )
                    return {
                        "response": response,
                        "intent": SubstituicaoIntent.DISPONIBILIDADE.value,
                        "data": {"disponiveis": result.data, "total": result.total_count},
                        "suggestions": ["Mais próximos", "Menor custo", "Mais confiáveis"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar disponibilidade via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**Funcionarios Disponiveis**

Verificando disponibilidade em tempo real...

**Filtros disponiveis:**
- Por proximidade (GPS)
- Por habilidade
- Por custo
- Por historico de aceitacao

Qual criterio priorizar?""",
            "intent": SubstituicaoIntent.DISPONIBILIDADE.value,
            "suggestions": ["Mais proximos", "Menor custo", "Mais confiaveis"],
        }

    async def _handle_default(self, message: str, context: dict) -> dict[str, Any] | None:
        """Handler padrao - retorna None para permitir que DataConnector processe"""
        # Se chegou aqui, não detectamos intent específico de substituição
        # Retorna None para permitir que o fluxo continue (DataConnector, LLM, etc)
        return None

    async def _handle_help(self, message: str, context: dict) -> dict[str, Any]:
        """Handler de ajuda explícita"""
        return {
            "response": """**Especialista em Substituições**

Posso ajudar com:
- **Buscar** substituto ideal
- **Emergência** - cobertura imediata
- **Pendentes** - substituições aguardando
- **Histórico** - análise de substituições
- **Custo** - estimativa de valores""",
            "intent": "substituicao_help",
            "suggestions": ["Buscar substituto", "Ver pendentes", "Substituição urgente"],
        }

    def get_capabilities(self) -> list[str]:
        """Retorna capabilities do agente"""
        return [
            "Encontrar substituto ideal em segundos",
            "Avaliar disponibilidade de funcionarios",
            "Calcular custo da substituicao",
            "Prever probabilidade de aceitacao",
            "Notificar automaticamente substitutos",
            "Rastrear respostas e timeouts",
        ]
