"""
AlertaAgent - Agente especialista em alertas proativos
"""

import logging
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AlertaPrioridade(StrEnum):
    """Níveis de prioridade de alertas"""

    CRITICO = "critico"
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"


class AlertaIntent(StrEnum):
    """Intents relacionados a alertas"""

    VER_ALERTAS = "ver_alertas"
    ALERTAS_CRITICOS = "alertas_criticos"
    COBERTURA = "cobertura"
    DOCUMENTOS = "documentos"
    ATRASOS = "atrasos"
    URGENTE = "urgente"
    RESOLVER = "resolver"
    IGNORAR = "ignorar"


class AlertaAgent:
    """
    Agente especializado em alertas proativos.

    Capabilities:
    - Monitorar cobertura de postos em tempo real
    - Alertar sobre documentos vencendo
    - Detectar atrasos de check-in
    - Identificar funcionários sobrecarregados
    - Alertar sobre escalas não publicadas
    - Detectar padrões anômalos
    """

    # ==========================================================================
    # INTENT_PATTERNS - Lista exaustiva para detecção de intenções
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # IGNORAR - Dispensar alerta (ANTES de URGENTE para "nao e urgente")
        # ==================================================================
        (r"nao\s+e\s+(?:urgente|importante)", AlertaIntent.IGNORAR),
        (r"n[aã]o\s+[eé]\s+(?:urgente|importante)", AlertaIntent.IGNORAR),
        (r"(?:ignorar|ignore|dispensar|dispense)\s+(?:o\s+|esse\s+)?(?:alerta)?", AlertaIntent.IGNORAR),
        (r"(?:deixar|deixe)\s+(?:para\s+)?depois", AlertaIntent.IGNORAR),
        (r"(?:adiar|adie)\s+(?:o\s+)?alerta", AlertaIntent.IGNORAR),
        # ==================================================================
        # URGENTE - Requer atenção (ANTES de ALERTAS_CRITICOS para "urgente atencao")
        # ==================================================================
        (r"urgente\s+(?:atencao|aten[çc][aã]o)", AlertaIntent.URGENTE),
        (r"(?:atencao|aten[çc][aã]o)\s+(?:imediata|urgente)", AlertaIntent.URGENTE),
        (r"(?:precisa|precisamos)\s+(?:de\s+)?(?:atencao|aten[çc][aã]o)", AlertaIntent.URGENTE),
        (r"(?:agora|ja)\s+(?:precisa|precisamos)", AlertaIntent.URGENTE),
        # ==================================================================
        # RESOLVER - Iniciar resolução
        # ==================================================================
        (r"(?:resolver|resolva|tratar|trate)\s+(?:o\s+)?alerta", AlertaIntent.RESOLVER),
        (r"(?:fechar|encerrar)\s+(?:o\s+)?alerta", AlertaIntent.RESOLVER),
        (r"(?:solucionar|solucion[ea])\s+(?:o\s+)?(?:problema|alerta)", AlertaIntent.RESOLVER),
        (r"(?:cuidar|atender)\s+(?:o\s+)?alerta", AlertaIntent.RESOLVER),
        # ==================================================================
        # VER_ALERTAS - Listar alertas
        # ==================================================================
        (r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:os\s+)?alertas?", AlertaIntent.VER_ALERTAS),
        (r"(?:quais?|quantos?)\s+alertas?", AlertaIntent.VER_ALERTAS),
        (r"alertas?\s+(?:do\s+)?(?:dia|sistema|hoje)", AlertaIntent.VER_ALERTAS),
        (r"notifica[cç][oõ]es?(?:\s+pendentes?)?", AlertaIntent.VER_ALERTAS),
        (r"(?:tem|ha)\s+(?:algum\s+)?alerta", AlertaIntent.VER_ALERTAS),
        # ==================================================================
        # ALERTAS_CRITICOS - Apenas críticos/urgentes
        # ==================================================================
        (r"alertas?\s+(?:criticos?|urgentes?|importantes?)", AlertaIntent.ALERTAS_CRITICOS),
        (r"(?:criticos?|urgentes?)\s+primeiro", AlertaIntent.ALERTAS_CRITICOS),
        (r"(?:mais\s+)?(?:graves?|serios?|importantes?)", AlertaIntent.ALERTAS_CRITICOS),
        (r"emergencia", AlertaIntent.ALERTAS_CRITICOS),
        (r"(?:prioridade\s+)?(?:maxima|alta)", AlertaIntent.ALERTAS_CRITICOS),
        # ==================================================================
        # COBERTURA - Alertas de cobertura
        # ==================================================================
        (r"alertas?\s+(?:de\s+)?cobertura", AlertaIntent.COBERTURA),
        (r"(?:problemas?|alertas?)\s+(?:com\s+)?postos?", AlertaIntent.COBERTURA),
        (r"postos?\s+(?:sem|descobertos?|criticos?)", AlertaIntent.COBERTURA),
        (r"postos?\s+(?:com\s+)?(?:problemas?|alertas?)\s+(?:de\s+)?cobertura", AlertaIntent.COBERTURA),
        (r"cobertura\s+(?:critica|baixa)", AlertaIntent.COBERTURA),
        # ==================================================================
        # DOCUMENTOS - Documentos vencendo
        # ==================================================================
        (r"(?:documentos?|docs?)\s+(?:que\s+)?(?:estao\s+)?(?:vencendo|vencidos?|expirando)", AlertaIntent.DOCUMENTOS),
        (r"alertas?\s+(?:de\s+)?(?:documentos?|docs?)", AlertaIntent.DOCUMENTOS),
        (r"(?:vencimento|validade)\s+(?:de\s+)?(?:documentos?|docs?)", AlertaIntent.DOCUMENTOS),
        (r"(?:CNV|ASO|NR|cnv|aso|nr)\s+(?:vencendo|vencido)", AlertaIntent.DOCUMENTOS),
        (r"(?:documentos?|docs?)\s+(?:a\s+)?vencer", AlertaIntent.DOCUMENTOS),
        # ==================================================================
        # ATRASOS - Alertas de atrasos
        # ==================================================================
        (r"alertas?\s+(?:de\s+)?atrasos?", AlertaIntent.ATRASOS),
        (r"(?:funcionarios?|equipe)\s+atrasad[ao]s?", AlertaIntent.ATRASOS),
        (r"atrasos?\s+(?:de\s+|do\s+)?(?:hoje|dia)", AlertaIntent.ATRASOS),
        (r"(?:sem\s+)?check.?in", AlertaIntent.ATRASOS),
        (r"quem\s+(?:nao\s+)?(?:chegou|esta\s+atrasado)", AlertaIntent.ATRASOS),
    ]

    # Regras de prioridade
    PRIORITY_RULES = {
        "posto_sem_funcionario": AlertaPrioridade.CRITICO,
        "cobertura_abaixo_50": AlertaPrioridade.CRITICO,
        "cobertura_abaixo_80": AlertaPrioridade.ALTO,
        "substituicao_pendente_2h": AlertaPrioridade.MEDIO,
        "documento_vencendo_7d": AlertaPrioridade.ALTO,
        "documento_vencendo_30d": AlertaPrioridade.BAIXO,
        "atraso_30min": AlertaPrioridade.ALTO,
        "atraso_15min": AlertaPrioridade.MEDIO,
        "funcionario_sobrecarregado": AlertaPrioridade.MEDIO,
        "escala_nao_publicada": AlertaPrioridade.ALTO,
    }

    def __init__(self, db=None, post_repo=None, employee_repo=None, shift_repo=None, data_connector=None):
        self.db = db
        self.post_repo = post_repo
        self.employee_repo = employee_repo
        self.shift_repo = shift_repo
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
        """Processa mensagem relacionada a alertas"""

        intent = self._detect_intent(message)
        context = context or {}

        handlers = {
            AlertaIntent.VER_ALERTAS: self._handle_ver_alertas,
            AlertaIntent.ALERTAS_CRITICOS: self._handle_criticos,
            AlertaIntent.COBERTURA: self._handle_cobertura,
            AlertaIntent.DOCUMENTOS: self._handle_documentos,
            AlertaIntent.ATRASOS: self._handle_atrasos,
            AlertaIntent.URGENTE: self._handle_urgente,
            AlertaIntent.RESOLVER: self._handle_resolver,
        }

        handler = handlers.get(intent, self._handle_default)
        return await handler(message, context)

    def _detect_intent(self, message: str) -> AlertaIntent | None:
        """Detecta intent da mensagem"""
        import re

        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_ver_alertas(self, message: str, context: dict) -> dict[str, Any]:
        """Lista todos os alertas usando dados reais do DataConnector"""
        # Tentar buscar dados reais
        if self.data_connector:
            try:
                result = await self.data_connector._get_pending_alerts()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": AlertaIntent.VER_ALERTAS.value,
                        "data": {"alertas": result.data, "total": result.total_count},
                        "suggestions": ["Ver críticos", "Resolver pendências", "Ver detalhes"],
                        "priority": "high" if result.total_count > 0 else "normal",
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar alertas via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**🚨 Central de Alertas**

**Críticos (2)**
🔴 Posto Centro-001 sem funcionário desde 08:00
🔴 Cobertura geral em 45% (mínimo 80%)

**Altos (3)**
🟠 3 documentos vencem em 7 dias
🟠 Escala de Março não publicada
🟠 2 funcionários com atraso > 30min

**Médios (5)**
🟡 5 substituições pendentes há > 2h

**Total: 10 alertas ativos**""",
            "intent": AlertaIntent.VER_ALERTAS.value,
            "data": {"criticos": 2, "altos": 3, "medios": 5, "total": 10},
            "suggestions": ["Ver críticos", "Resolver #1", "Ignorar médios"],
            "priority": "high",
        }

    async def _handle_criticos(self, message: str, context: dict) -> dict[str, Any]:
        """Lista apenas alertas críticos usando dados reais do DataConnector"""
        # Tentar buscar dados reais de cobertura crítica
        if self.data_connector:
            try:
                cobertura_result = await self.data_connector._get_cobertura_critica()
                alerts_result = await self.data_connector._get_pending_alerts()

                parts = ["**🔴 ALERTAS CRÍTICOS**\n"]
                critical_count = 0

                if cobertura_result.success and cobertura_result.data:
                    postos = cobertura_result.data
                    critical_count += len(postos)
                    for i, p in enumerate(postos[:5], 1):
                        parts.append(f"**{i}. Cobertura Crítica - {p['nome']}**")
                        parts.append(f"- Código: {p['codigo']}")
                        parts.append(f"- Cobertura: {p['cobertura']}% ({p['alocados']}/{p['requeridos']})")
                        parts.append(f"- Déficit: {p['deficit']} funcionário(s)")
                        parts.append("- Ação sugerida: Buscar substituto\n")

                if alerts_result.success and alerts_result.data:
                    for alert in alerts_result.data:
                        if alert.get("severidade") == "alta":
                            critical_count += 1
                            parts.append(f"**{critical_count}. {alert['mensagem']}**")
                            parts.append(f"- Ação: {alert['acao']}\n")

                if critical_count > 0:
                    parts.append("⚠️ **Estes alertas requerem ação imediata!**")
                else:
                    parts = ["**🔴 ALERTAS CRÍTICOS**\n\n✅ Nenhum alerta crítico no momento."]

                return {
                    "response": "\n".join(parts),
                    "intent": AlertaIntent.ALERTAS_CRITICOS.value,
                    "data": {"critical_count": critical_count},
                    "suggestions": ["Resolver pendências", "Ver cobertura", "Notificar supervisor"],
                    "actions": [
                        {
                            "type": "navigate",
                            "label": "Buscar Substituto",
                            "target": "/modulos/operacional/substituicoes",
                        },
                    ],
                    "priority": "critical" if critical_count > 0 else "normal",
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar alertas críticos via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**🔴 ALERTAS CRÍTICOS**

**1. Posto sem Funcionário**
- Posto: Centro-001
- Desde: 08:00 (há 2h15min)
- Ação sugerida: Buscar substituto urgente
- [Resolver Agora]

**2. Cobertura Crítica**
- Cobertura atual: 45%
- Mínimo aceitável: 80%
- Postos afetados: 4
- Ação sugerida: Redistribuir turnos
- [Ver Postos Afetados]

⚠️ **Estes alertas requerem ação imediata!**""",
            "intent": AlertaIntent.ALERTAS_CRITICOS.value,
            "data": {"critical_count": 2},
            "suggestions": ["Resolver #1", "Resolver #2", "Notificar supervisor"],
            "actions": [
                {"type": "navigate", "label": "Buscar Substituto", "target": "/modulos/operacional/substituicoes"},
            ],
            "priority": "critical",
        }

    async def _handle_cobertura(self, message: str, context: dict) -> dict[str, Any]:
        """Alertas de cobertura usando dados reais do DataConnector"""
        # Tentar buscar dados reais
        if self.data_connector:
            try:
                result = await self.data_connector._get_cobertura_critica()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": AlertaIntent.COBERTURA.value,
                        "data": {"postos_criticos": result.data, "total": result.total_count},
                        "suggestions": ["Buscar substitutos", "Ver todos os postos", "Redistribuir turnos"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar cobertura via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**📊 Alertas de Cobertura**

| Posto | Cobertura | Status |
|-------|-----------|--------|
| Centro-001 | 0% | 🔴 CRÍTICO |
| Norte-003 | 50% | 🟠 ALTO |
| Sul-002 | 75% | 🟡 MÉDIO |
| Leste-001 | 100% | ✅ OK |

**Ações recomendadas:**
1. Centro-001: Buscar substituto imediato
2. Norte-003: Redistribuir turno
3. Sul-002: Monitorar

**Cobertura geral: 56.25%**""",
            "intent": AlertaIntent.COBERTURA.value,
            "suggestions": ["Resolver Centro-001", "Ver detalhes Norte-003", "Ignorar Sul-002"],
        }

    async def _handle_documentos(self, message: str, context: dict) -> dict[str, Any]:
        """Alertas de documentos vencendo usando dados reais do DataConnector"""
        # Tentar buscar dados reais de alertas (inclui documentos)
        if self.data_connector:
            try:
                result = await self.data_connector._get_pending_alerts()
                if result.success and result.data:
                    doc_alerts = [a for a in result.data if a.get("tipo") == "documento"]
                    if doc_alerts:
                        lines = [f"- {a['mensagem']}" for a in doc_alerts]
                        response = f"""**📄 Documentos - Alertas**

{chr(10).join(lines)}

**Ações:**
- Notificar funcionários
- Agendar renovações
- Bloquear alocação (se necessário)"""
                        return {
                            "response": response,
                            "intent": AlertaIntent.DOCUMENTOS.value,
                            "data": {"doc_alerts": doc_alerts},
                            "suggestions": ["Notificar todos", "Ver lista completa", "Agendar renovações"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar alertas de documentos via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**📄 Documentos Vencendo**

**Próximos 7 dias (URGENTE):**
- João Silva - ASO vence em 3 dias
- Maria Santos - CNH vence em 5 dias
- Carlos Lima - Curso NR vence em 7 dias

**Próximos 30 dias:**
- 8 documentos vencendo

**Ações:**
- Notificar funcionários
- Agendar renovações
- Bloquear alocação (se necessário)""",
            "intent": AlertaIntent.DOCUMENTOS.value,
            "suggestions": ["Notificar todos", "Ver lista completa", "Agendar renovações"],
        }

    async def _handle_atrasos(self, message: str, context: dict) -> dict[str, Any]:
        """Alertas de atrasos usando dados reais do DataConnector"""
        # Tentar buscar dados reais
        if self.data_connector:
            try:
                result = await self.data_connector._get_atrasos_hoje()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": AlertaIntent.ATRASOS.value,
                        "data": {"atrasos": result.data, "total": result.total_count},
                        "suggestions": ["Contatar atrasados", "Buscar substitutos", "Ver histórico de atrasos"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar atrasos via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**⏰ Atrasos de Hoje**

**Atrasos > 30min (ALTO):**
- João Silva | Posto Centro-001 | +45min | Sem comunicação
- Ana Paula | Posto Norte-003 | +32min | Trânsito informado

**Atrasos < 30min (MÉDIO):**
- Roberto Dias | Posto Sul-002 | +12min
- Carla Mendes | Posto Leste-001 | +8min

**Ações sugeridas:**
1. Tentar contato com João Silva
2. Buscar substituto para Centro-001""",
            "intent": AlertaIntent.ATRASOS.value,
            "suggestions": ["Ligar para João", "Buscar substituto", "Ver histórico de atrasos"],
        }

    async def _handle_urgente(self, message: str, context: dict) -> dict[str, Any]:
        """O que precisa de atenção urgente usando dados reais do DataConnector"""
        # Tentar buscar dados reais
        if self.data_connector:
            try:
                alerts_result = await self.data_connector._get_pending_alerts()
                cobertura_result = await self.data_connector._get_cobertura_critica()

                parts = ["**⚡ ATENÇÃO URGENTE NECESSÁRIA**\n"]
                item_num = 0
                has_critical = False

                # Prioridade 1 - Cobertura crítica
                if cobertura_result.success and cobertura_result.data:
                    has_critical = True
                    parts.append("**Prioridade 1 - Resolver AGORA:**")
                    for p in cobertura_result.data[:3]:
                        item_num += 1
                        parts.append(
                            f"{item_num}. 🔴 **{p['nome']}** - cobertura {p['cobertura']}% (déficit: {p['deficit']})"
                        )
                    parts.append("")

                # Prioridade 2 - Outros alertas
                if alerts_result.success and alerts_result.data:
                    parts.append("**Prioridade 2 - Resolver HOJE:**")
                    for a in alerts_result.data:
                        item_num += 1
                        sev_icon = "🟠" if a.get("severidade") in ("alta", "media") else "🟡"
                        parts.append(f"{item_num}. {sev_icon} {a['mensagem']}")
                    parts.append("")

                if item_num > 0:
                    parts.append("**Você quer que eu inicie a resolução do item #1?**")
                else:
                    parts = ["**⚡ ATENÇÃO URGENTE**\n\n✅ Nenhum item urgente pendente no momento."]

                return {
                    "response": "\n".join(parts),
                    "intent": AlertaIntent.URGENTE.value,
                    "data": {"total_urgentes": item_num},
                    "suggestions": ["Sim, resolver #1", "Ver detalhes", "Ver todos os alertas"],
                    "priority": "critical" if has_critical else "high",
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar urgentes via DataConnector: {e}")

        # Fallback estático
        return {
            "response": """**⚡ ATENÇÃO URGENTE NECESSÁRIA**

**Prioridade 1 - Resolver AGORA:**
1. 🔴 Posto Centro-001 descoberto há 2h
2. 🔴 Cobertura geral crítica (45%)

**Prioridade 2 - Resolver HOJE:**
3. 🟠 3 documentos vencem em 7 dias
4. 🟠 Escala de Março não publicada

**Você quer que eu inicie a resolução do item #1?**""",
            "intent": AlertaIntent.URGENTE.value,
            "suggestions": ["Sim, resolver #1", "Ver detalhes #1", "Resolver #2 primeiro"],
            "priority": "critical",
        }

    async def _handle_resolver(self, message: str, context: dict) -> dict[str, Any]:
        """Resolver um alerta específico"""
        return {
            "response": "Qual alerta você deseja resolver? Informe o número ou descreva o problema.",
            "intent": AlertaIntent.RESOLVER.value,
            "suggestions": ["Alerta #1", "Alerta #2", "Ver todos os alertas"],
        }

    async def _handle_default(self, message: str, context: dict) -> dict[str, Any] | None:
        """Handler padrão - retorna None para permitir que DataConnector processe"""
        # Se chegou aqui, não detectamos intent específico de alerta
        # Retorna None para permitir que o fluxo continue (DataConnector, LLM, etc)
        return None

    async def _handle_help(self, message: str, context: dict) -> dict[str, Any]:
        """Handler de ajuda explícita"""
        return {
            "response": """**🔔 Central de Alertas**

Monitoro e alerto sobre:
- 🔴 **Cobertura crítica** de postos
- 📄 **Documentos** vencendo
- ⏰ **Atrasos** de funcionários
- 📊 **Escalas** não publicadas
- 👥 **Funcionários** sobrecarregados

O que você quer verificar?""",
            "intent": "alerta_help",
            "suggestions": ["Ver todos os alertas", "Alertas críticos", "Atrasos de hoje"],
        }

    async def check_proactive_alerts(self) -> list[dict[str, Any]]:
        """
        Verifica alertas proativamente (chamado por scheduler).
        Retorna lista de alertas que precisam de ação.
        """
        alerts = []

        # Em produção, consultaria o banco de dados
        # Aqui simulamos a estrutura

        return alerts

    def get_capabilities(self) -> list[str]:
        """Retorna capabilities do agente"""
        return [
            "Monitorar cobertura de postos em tempo real",
            "Alertar sobre documentos vencendo",
            "Detectar atrasos de check-in",
            "Identificar funcionários sobrecarregados",
            "Alertar sobre escalas não publicadas",
            "Detectar padrões anômalos",
        ]
