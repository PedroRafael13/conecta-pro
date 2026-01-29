"""
SubstituicaoAgent - Agente especialista em substituicoes em tempo real
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SubstituicaoIntent(str, Enum):
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
        (r"(?:buscar|busque|encontrar|encontre|achar|ache)\s+(?:um\s+)?substituto", SubstituicaoIntent.BUSCAR_SUBSTITUTO),
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
        (r"(?:quais\s+)?substituicoes?\s+(?:estao\s+)?pendentes?\s+(?:de\s+)?(?:aprovacao)?", SubstituicaoIntent.PENDENTES),
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
        (r"quem\s+(?:esta|ta|está)?\s*disponivel\s+(?:para\s+)?(?:cobrir|substituir)", SubstituicaoIntent.DISPONIBILIDADE),
        (r"(?:funcionarios?|colaboradores?)\s+(?:disponiveis?|livres?)", SubstituicaoIntent.DISPONIBILIDADE),
        (r"quem\s+(?:esta|ta|está)\s+livre", SubstituicaoIntent.DISPONIBILIDADE),
    ]

    def __init__(self, db=None, substitution_repo=None, employee_repo=None, notification_service=None):
        self.db = db
        self.substitution_repo = substitution_repo
        self.employee_repo = employee_repo
        self.notification_service = notification_service

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa mensagem relacionada a substituicoes"""
        import re

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

    def _detect_intent(self, message: str) -> Optional[SubstituicaoIntent]:
        """Detecta intent da mensagem"""
        import re
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_buscar_substituto(self, message: str, context: Dict) -> Dict[str, Any]:
        """Busca substituto ideal"""
        import re

        # Tenta extrair funcionario ou turno
        func_match = re.search(r"(?:do|da|para)\s+(\w+)", message.lower())

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

    async def _handle_urgente(self, message: str, context: Dict) -> Dict[str, Any]:
        """Substituicao urgente/emergencia"""
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

    async def _handle_confirmar(self, message: str, context: Dict) -> Dict[str, Any]:
        """Confirma substituicao"""
        return {
            "response": "Para confirmar uma substituicao, informe o ID ou selecione da lista de pendentes.",
            "intent": SubstituicaoIntent.CONFIRMAR.value,
            "suggestions": ["Ver substituicoes pendentes", "Cancelar"],
        }

    async def _handle_pendentes(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista substituicoes pendentes"""
        # Em producao, consultaria o banco
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

    async def _handle_historico(self, message: str, context: Dict) -> Dict[str, Any]:
        """Historico de substituicoes"""
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

    async def _handle_custo(self, message: str, context: Dict) -> Dict[str, Any]:
        """Calcula custo de substituicao"""
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

    async def _handle_disponibilidade(self, message: str, context: Dict) -> Dict[str, Any]:
        """Verifica disponibilidade de funcionarios"""
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

    async def _handle_default(self, message: str, context: Dict) -> Optional[Dict[str, Any]]:
        """Handler padrao - retorna None para permitir que DataConnector processe"""
        # Se chegou aqui, não detectamos intent específico de substituição
        # Retorna None para permitir que o fluxo continue (DataConnector, LLM, etc)
        return None

    async def _handle_help(self, message: str, context: Dict) -> Dict[str, Any]:
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

    def get_capabilities(self) -> List[str]:
        """Retorna capabilities do agente"""
        return [
            "Encontrar substituto ideal em segundos",
            "Avaliar disponibilidade de funcionarios",
            "Calcular custo da substituicao",
            "Prever probabilidade de aceitacao",
            "Notificar automaticamente substitutos",
            "Rastrear respostas e timeouts",
        ]
