"""
AlertaAgent - Agente especialista em alertas proativos
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertaPrioridade(str, Enum):
    """Níveis de prioridade de alertas"""
    CRITICO = "critico"
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"


class AlertaIntent(str, Enum):
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

    def __init__(self, db=None, post_repo=None, employee_repo=None, shift_repo=None):
        self.db = db
        self.post_repo = post_repo
        self.employee_repo = employee_repo
        self.shift_repo = shift_repo

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa mensagem relacionada a alertas"""
        import re

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

    def _detect_intent(self, message: str) -> Optional[AlertaIntent]:
        """Detecta intent da mensagem"""
        import re
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_ver_alertas(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista todos os alertas"""
        # Simula alertas (em produção viria do banco)
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

    async def _handle_criticos(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista apenas alertas críticos"""
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

    async def _handle_cobertura(self, message: str, context: Dict) -> Dict[str, Any]:
        """Alertas de cobertura"""
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

    async def _handle_documentos(self, message: str, context: Dict) -> Dict[str, Any]:
        """Alertas de documentos vencendo"""
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

    async def _handle_atrasos(self, message: str, context: Dict) -> Dict[str, Any]:
        """Alertas de atrasos"""
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

    async def _handle_urgente(self, message: str, context: Dict) -> Dict[str, Any]:
        """O que precisa de atenção urgente"""
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

    async def _handle_resolver(self, message: str, context: Dict) -> Dict[str, Any]:
        """Resolver um alerta específico"""
        return {
            "response": "Qual alerta você deseja resolver? Informe o número ou descreva o problema.",
            "intent": AlertaIntent.RESOLVER.value,
            "suggestions": ["Alerta #1", "Alerta #2", "Ver todos os alertas"],
        }

    async def _handle_default(self, message: str, context: Dict) -> Optional[Dict[str, Any]]:
        """Handler padrão - retorna None para permitir que DataConnector processe"""
        # Se chegou aqui, não detectamos intent específico de alerta
        # Retorna None para permitir que o fluxo continue (DataConnector, LLM, etc)
        return None

    async def _handle_help(self, message: str, context: Dict) -> Dict[str, Any]:
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

    async def check_proactive_alerts(self) -> List[Dict[str, Any]]:
        """
        Verifica alertas proativamente (chamado por scheduler).
        Retorna lista de alertas que precisam de ação.
        """
        alerts = []

        # Em produção, consultaria o banco de dados
        # Aqui simulamos a estrutura

        return alerts

    def get_capabilities(self) -> List[str]:
        """Retorna capabilities do agente"""
        return [
            "Monitorar cobertura de postos em tempo real",
            "Alertar sobre documentos vencendo",
            "Detectar atrasos de check-in",
            "Identificar funcionários sobrecarregados",
            "Alertar sobre escalas não publicadas",
            "Detectar padrões anômalos",
        ]
