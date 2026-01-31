"""
RondaAgent - Agente especialista em rondas de inspecao.

Processa mensagens relacionadas a rondas de inspecao, detectando intents
e retornando respostas formatadas com dados reais ou fallback estatico.

Author: Conecta PRO Team
Date: 2026-01-29
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class RondaIntent(str, Enum):
    """Intents relacionados a rondas de inspecao."""
    RONDAS_HOJE = "rondas_hoje"
    RONDAS_ANDAMENTO = "rondas_andamento"
    RONDA_DETALHES = "ronda_detalhes"
    RESULTADO_RONDA = "resultado_ronda"
    RONDAS_INSPETOR = "rondas_inspetor"
    ESTATISTICAS_RONDAS = "estatisticas_rondas"
    INICIAR_RONDA = "iniciar_ronda"
    CRIAR_RONDA = "criar_ronda"


class RondaAgent:
    """
    Agente especializado em operacoes de rondas de inspecao.

    Capabilities:
    - Consultar rondas agendadas para hoje
    - Consultar rondas em andamento
    - Ver detalhes de uma ronda especifica
    - Ver resultado/relatorio de ronda concluida
    - Consultar rondas por inspetor
    - Estatisticas de rondas por status
    - Redirecionar para iniciar ronda (action)
    - Redirecionar para criar ronda (wizard)
    """

    # ==========================================================================
    # INTENT_PATTERNS - Lista exaustiva para deteccao de intencoes
    # IMPORTANTE: Patterns mais especificos devem vir ANTES dos mais genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # CRIAR_RONDA - Criar nova ronda (wizard)
        # ==================================================================
        (r"(?:criar|crie|cria|nova|agendar|agende|cadastrar|cadastre)\s+(?:uma\s+)?(?:nova\s+)?ronda", RondaIntent.CRIAR_RONDA),
        (r"(?:quero|preciso)\s+(?:de\s+)?(?:uma\s+)?(?:nova\s+)?ronda", RondaIntent.CRIAR_RONDA),
        (r"(?:pode|consegue|da\s+para)\s+(?:criar|agendar)\s+(?:uma\s+)?ronda", RondaIntent.CRIAR_RONDA),
        (r"(?:me\s+)?(?:ajuda|ajude)\s+(?:a\s+)?(?:criar|agendar)\s+(?:uma\s+)?ronda", RondaIntent.CRIAR_RONDA),
        (r"(?:montar|preparar|planejar)\s+(?:uma\s+)?ronda", RondaIntent.CRIAR_RONDA),
        (r"nova\s+ronda\s+de\s+inspecao", RondaIntent.CRIAR_RONDA),

        # ==================================================================
        # INICIAR_RONDA - Iniciar ronda existente (action)
        # ==================================================================
        (r"(?:iniciar|inicie|comecar|comece|comecar|abrir|abra)\s+(?:a\s+)?ronda", RondaIntent.INICIAR_RONDA),
        (r"(?:dar\s+inicio|comecar)\s+(?:a\s+)?ronda", RondaIntent.INICIAR_RONDA),
        (r"(?:iniciar|inicie)\s+(?:a\s+)?ronda\s+(?:RON-[\w-]+|\w+)", RondaIntent.INICIAR_RONDA),
        (r"(?:iniciar|comecar)\s+inspecao", RondaIntent.INICIAR_RONDA),

        # ==================================================================
        # RESULTADO_RONDA - Resultado/relatorio de ronda
        # ==================================================================
        (r"(?:resultado|relatorio|resumo|conclusao)\s+(?:da\s+)?ronda", RondaIntent.RESULTADO_RONDA),
        (r"ronda\s+(?:RON-[\w-]+)\s+(?:resultado|relatorio|resumo)", RondaIntent.RESULTADO_RONDA),
        (r"(?:como\s+)?(?:foi|ficou|terminou)\s+(?:a\s+)?ronda", RondaIntent.RESULTADO_RONDA),
        (r"(?:ver|veja|mostrar|mostre)\s+(?:o\s+)?resultado\s+(?:da\s+)?ronda", RondaIntent.RESULTADO_RONDA),
        (r"(?:ver|veja|mostrar|mostre)\s+(?:o\s+)?relatorio\s+(?:da\s+)?ronda", RondaIntent.RESULTADO_RONDA),

        # ==================================================================
        # RONDA_DETALHES - Detalhe de uma ronda especifica
        # ==================================================================
        (r"(?:detalhes?|detalhar|info|informacoes?)\s+(?:da\s+)?ronda", RondaIntent.RONDA_DETALHES),
        (r"ronda\s+(?:RON-[\w-]+)", RondaIntent.RONDA_DETALHES),
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:a\s+)?ronda\s+(?:RON-[\w-]+)", RondaIntent.RONDA_DETALHES),
        (r"(?:qual|quais)\s+(?:os?\s+)?(?:dados?|detalhes?)\s+(?:da\s+)?ronda", RondaIntent.RONDA_DETALHES),
        (r"(?:abrir|abra)\s+(?:a\s+)?ronda\s+(?:RON-[\w-]+)", RondaIntent.RONDA_DETALHES),

        # ==================================================================
        # RONDAS_INSPETOR - Rondas por inspetor
        # ==================================================================
        (r"rondas?\s+(?:do|da|de)\s+(?:inspetor|supervisor|gerente|lider)\s+\w+", RondaIntent.RONDAS_INSPETOR),
        (r"rondas?\s+(?:realizadas?|feitas?)\s+(?:por|pelo|pela)\s+\w+", RondaIntent.RONDAS_INSPETOR),
        (r"(?:quais|quantas)\s+rondas?\s+(?:do|da|de)\s+\w+", RondaIntent.RONDAS_INSPETOR),
        (r"(?:ver|veja|mostrar|mostre|listar|liste)\s+rondas?\s+(?:do|da|de)\s+\w+", RondaIntent.RONDAS_INSPETOR),
        (r"(?:historico|historico)\s+(?:de\s+)?rondas?\s+(?:do|da|de)\s+\w+", RondaIntent.RONDAS_INSPETOR),

        # ==================================================================
        # ESTATISTICAS_RONDAS - Estatisticas por status
        # ==================================================================
        (r"(?:estatisticas?|stats?|numeros?|metricas?)\s+(?:de\s+|das?\s+)?rondas?", RondaIntent.ESTATISTICAS_RONDAS),
        (r"rondas?\s+(?:por\s+)?(?:status|situacao)", RondaIntent.ESTATISTICAS_RONDAS),
        (r"(?:quantas|quantos)\s+rondas?\s+(?:por\s+status|temos|existem|tem|ha)", RondaIntent.ESTATISTICAS_RONDAS),
        (r"(?:resumo|painel|dashboard)\s+(?:de\s+|das?\s+)?rondas?", RondaIntent.ESTATISTICAS_RONDAS),
        (r"(?:panorama|visao\s+geral)\s+(?:de\s+|das?\s+)?rondas?", RondaIntent.ESTATISTICAS_RONDAS),

        # ==================================================================
        # RONDAS_ANDAMENTO - Rondas em andamento
        # ==================================================================
        (r"rondas?\s+(?:em\s+)?andamento", RondaIntent.RONDAS_ANDAMENTO),
        (r"rondas?\s+(?:em\s+)?(?:progresso|curso|execucao)", RondaIntent.RONDAS_ANDAMENTO),
        (r"(?:tem|ha|há)\s+(?:alguma\s+)?ronda\s+(?:em\s+)?(?:andamento|progresso|curso)", RondaIntent.RONDAS_ANDAMENTO),
        (r"(?:quais|quantas)\s+rondas?\s+(?:estao|estão)\s+(?:em\s+)?andamento", RondaIntent.RONDAS_ANDAMENTO),
        (r"rondas?\s+(?:ativas?|acontecendo|rodando)", RondaIntent.RONDAS_ANDAMENTO),
        (r"(?:ver|veja|mostrar|mostre)\s+rondas?\s+(?:em\s+)?andamento", RondaIntent.RONDAS_ANDAMENTO),

        # ==================================================================
        # RONDAS_HOJE - Rondas agendadas hoje (mais generico, por ultimo)
        # ==================================================================
        (r"rondas?\s+(?:de\s+)?hoje", RondaIntent.RONDAS_HOJE),
        (r"rondas?\s+(?:agendadas?|previstas?|programadas?)\s+(?:para\s+)?hoje", RondaIntent.RONDAS_HOJE),
        (r"(?:tem|ha|há)\s+rondas?\s+(?:para\s+)?hoje", RondaIntent.RONDAS_HOJE),
        (r"(?:quais|quantas)\s+rondas?\s+(?:para\s+|de\s+)?hoje", RondaIntent.RONDAS_HOJE),
        (r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:as\s+)?rondas?\s+(?:de\s+|para\s+)?hoje", RondaIntent.RONDAS_HOJE),
        (r"rondas?\s+do\s+dia", RondaIntent.RONDAS_HOJE),
        (r"(?:agenda|programacao)\s+(?:de\s+)?rondas?\s+(?:de\s+)?hoje", RondaIntent.RONDAS_HOJE),
        (r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:as\s+)?rondas?(?:\s+(?:atuais?|existentes?|ativas?))?$", RondaIntent.RONDAS_HOJE),
    ]

    def __init__(self, db=None, data_connector=None):
        """
        Inicializa o agente de rondas.

        Args:
            db: Sessao async do banco de dados.
            data_connector: Conector de dados para consultas reais.
        """
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

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa uma mensagem relacionada a rondas de inspecao.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        intent = self._detect_intent(message)
        context = context or {}

        if intent == RondaIntent.RONDAS_HOJE:
            return await self._handle_rondas_hoje(context)
        elif intent == RondaIntent.RONDAS_ANDAMENTO:
            return await self._handle_rondas_andamento(context)
        elif intent == RondaIntent.RONDA_DETALHES:
            return await self._handle_ronda_detalhes(message, context)
        elif intent == RondaIntent.RESULTADO_RONDA:
            return await self._handle_resultado_ronda(message, context)
        elif intent == RondaIntent.RONDAS_INSPETOR:
            return await self._handle_rondas_inspetor(message, context)
        elif intent == RondaIntent.ESTATISTICAS_RONDAS:
            return await self._handle_estatisticas_rondas(context)
        elif intent == RondaIntent.INICIAR_RONDA:
            return await self._handle_iniciar_ronda(message, context)
        elif intent == RondaIntent.CRIAR_RONDA:
            return await self._handle_criar_ronda(message, context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> Optional[RondaIntent]:
        """Detecta o intent da mensagem."""
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    # ==========================================================================
    # HANDLERS
    # ==========================================================================

    async def _handle_rondas_hoje(self, context: Dict) -> Dict[str, Any]:
        """Retorna rondas agendadas para hoje usando DataConnector ou fallback."""
        if self.data_connector:
            try:
                result = await self.data_connector._get_rondas_hoje()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": RondaIntent.RONDAS_HOJE.value,
                        "data": {"rondas": result.data, "total": result.total_count},
                        "suggestions": [
                            "/ronda andamento",
                            "/ronda stats",
                            "Criar nova ronda",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar rondas de hoje via DataConnector: {e}")

        # Fallback estatico
        hoje = datetime.utcnow().strftime("%d/%m/%Y")
        return {
            "response": f"""**Rondas Agendadas para Hoje ({hoje})**

Nenhuma ronda agendada para hoje foi encontrada no momento.

**Dica:** Voce pode agendar uma nova ronda usando o comando `/ronda` ou pedindo "criar nova ronda".""",
            "intent": RondaIntent.RONDAS_HOJE.value,
            "data": {"rondas": [], "total": 0},
            "suggestions": [
                "Criar nova ronda",
                "/ronda andamento",
                "/ronda stats",
            ],
        }

    async def _handle_rondas_andamento(self, context: Dict) -> Dict[str, Any]:
        """Retorna rondas em andamento."""
        if self.data_connector:
            try:
                result = await self.data_connector._get_rondas_andamento()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": RondaIntent.RONDAS_ANDAMENTO.value,
                        "data": {"rondas": result.data, "total": result.total_count},
                        "suggestions": [
                            "/ronda hoje",
                            "/ronda stats",
                            "Ver detalhes da ronda",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar rondas em andamento via DataConnector: {e}")

        # Fallback estatico
        return {
            "response": """**Rondas em Andamento**

Nenhuma ronda em andamento no momento.

**Dica:** Para iniciar uma ronda agendada, use "iniciar ronda RON-XXXX".""",
            "intent": RondaIntent.RONDAS_ANDAMENTO.value,
            "data": {"rondas": [], "total": 0},
            "suggestions": [
                "/ronda hoje",
                "Iniciar ronda",
                "/ronda stats",
            ],
        }

    async def _handle_ronda_detalhes(self, message: str, context: Dict) -> Dict[str, Any]:
        """Retorna detalhes de uma ronda especifica."""
        # Extrair codigo da ronda da mensagem
        code_match = re.search(r"(RON-[\w-]+)", message, re.IGNORECASE)
        round_code = code_match.group(1).upper() if code_match else None

        if self.data_connector and round_code:
            try:
                result = await self.data_connector._get_ronda_detalhes(round_code)
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": RondaIntent.RONDA_DETALHES.value,
                        "data": result.data,
                        "suggestions": [
                            "Ver resultado da ronda",
                            "/ronda andamento",
                            "/ronda hoje",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes da ronda via DataConnector: {e}")

        if round_code:
            return {
                "response": f"""**Detalhes da Ronda {round_code}**

Nao foi possivel carregar os detalhes da ronda {round_code} no momento.

Verifique se o codigo esta correto e tente novamente.""",
                "intent": RondaIntent.RONDA_DETALHES.value,
                "data": {"code": round_code},
                "suggestions": ["/ronda hoje", "/ronda andamento"],
            }

        return {
            "response": """**Detalhes da Ronda**

Para ver os detalhes, informe o codigo da ronda.

**Exemplo:** "detalhes da ronda RON-2026-00001" """,
            "intent": RondaIntent.RONDA_DETALHES.value,
            "needs_info": ["round_code"],
            "suggestions": ["/ronda hoje", "/ronda andamento"],
        }

    async def _handle_resultado_ronda(self, message: str, context: Dict) -> Dict[str, Any]:
        """Retorna resultado/relatorio de uma ronda concluida."""
        code_match = re.search(r"(RON-[\w-]+)", message, re.IGNORECASE)
        round_code = code_match.group(1).upper() if code_match else None

        if self.data_connector and round_code:
            try:
                result = await self.data_connector._get_resultado_ronda(round_code)
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": RondaIntent.RESULTADO_RONDA.value,
                        "data": result.data,
                        "suggestions": [
                            "/ronda stats",
                            "/ronda hoje",
                            "Criar nova ronda",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar resultado da ronda via DataConnector: {e}")

        if round_code:
            return {
                "response": f"""**Resultado da Ronda {round_code}**

Nao foi possivel carregar o resultado da ronda {round_code} no momento.

Verifique se a ronda esta concluida e tente novamente.""",
                "intent": RondaIntent.RESULTADO_RONDA.value,
                "data": {"code": round_code},
                "suggestions": ["/ronda hoje", "/ronda stats"],
            }

        return {
            "response": """**Resultado da Ronda**

Para ver o resultado, informe o codigo da ronda.

**Exemplo:** "resultado da ronda RON-2026-00001" """,
            "intent": RondaIntent.RESULTADO_RONDA.value,
            "needs_info": ["round_code"],
            "suggestions": ["/ronda hoje", "/ronda andamento"],
        }

    async def _handle_rondas_inspetor(self, message: str, context: Dict) -> Dict[str, Any]:
        """Retorna rondas de um inspetor especifico."""
        # Extrair nome do inspetor da mensagem
        name_match = re.search(
            r"(?:inspetor|supervisor|gerente|lider|de|do|da|por|pelo|pela)\s+([A-Za-z\u00C0-\u017F\s]{3,}?)(?:\s*$|\s*,|\s+(?:no|na|em|de))",
            message,
            re.IGNORECASE,
        )
        inspector_name = name_match.group(1).strip().title() if name_match else None

        if self.data_connector and inspector_name:
            try:
                result = await self.data_connector._get_rondas_inspetor(inspector_name)
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": RondaIntent.RONDAS_INSPETOR.value,
                        "data": {"rondas": result.data, "inspetor": inspector_name, "total": result.total_count},
                        "suggestions": [
                            "/ronda stats",
                            "/ronda hoje",
                            f"Detalhes do inspetor {inspector_name}",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar rondas do inspetor via DataConnector: {e}")

        if inspector_name:
            return {
                "response": f"""**Rondas do Inspetor {inspector_name}**

Nao foi possivel carregar as rondas do inspetor {inspector_name} no momento.

Verifique se o nome esta correto e tente novamente.""",
                "intent": RondaIntent.RONDAS_INSPETOR.value,
                "data": {"inspetor": inspector_name},
                "suggestions": ["/ronda hoje", "/ronda stats"],
            }

        return {
            "response": """**Rondas por Inspetor**

Para ver as rondas de um inspetor, informe o nome.

**Exemplo:** "rondas do inspetor Carlos Silva" """,
            "intent": RondaIntent.RONDAS_INSPETOR.value,
            "needs_info": ["inspector_name"],
            "suggestions": ["/ronda hoje", "/ronda stats"],
        }

    async def _handle_estatisticas_rondas(self, context: Dict) -> Dict[str, Any]:
        """Retorna estatisticas de rondas por status."""
        if self.data_connector:
            try:
                result = await self.data_connector._get_estatisticas_rondas()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": RondaIntent.ESTATISTICAS_RONDAS.value,
                        "data": result.data,
                        "suggestions": [
                            "/ronda hoje",
                            "/ronda andamento",
                            "Criar nova ronda",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas via DataConnector: {e}")

        # Fallback estatico
        return {
            "response": """**Estatisticas de Rondas**

| Status | Quantidade |
|--------|-----------|
| Agendadas | 0 |
| Em Andamento | 0 |
| Concluidas | 0 |
| Pausadas | 0 |
| Canceladas | 0 |
| **Total** | **0** |

*Dados indisponiveis no momento. Conecte ao banco de dados para dados reais.*""",
            "intent": RondaIntent.ESTATISTICAS_RONDAS.value,
            "data": {"stats": {}},
            "suggestions": [
                "/ronda hoje",
                "/ronda andamento",
                "Criar nova ronda",
            ],
        }

    async def _handle_iniciar_ronda(self, message: str, context: Dict) -> Dict[str, Any]:
        """Redireciona para action de iniciar ronda."""
        code_match = re.search(r"(RON-[\w-]+)", message, re.IGNORECASE)
        round_code = code_match.group(1).upper() if code_match else None

        if round_code:
            return {
                "response": f"""**Iniciar Ronda {round_code}**

Ao iniciar a ronda:
- O status sera alterado para **Em Andamento**
- O horario de inicio sera registrado
- O GPS sera ativado para rastreamento

**Confirmar inicio da ronda {round_code}?**""",
                "intent": RondaIntent.INICIAR_RONDA.value,
                "data": {"code": round_code},
                "suggestions": ["Confirmar", "Cancelar", "Ver detalhes primeiro"],
                "actions": [
                    {
                        "type": "execute",
                        "label": f"Iniciar Ronda {round_code}",
                        "target": "inspection_round",
                        "data": {"code": round_code, "action": "start"},
                    }
                ],
            }

        return {
            "response": """**Iniciar Ronda**

Para iniciar uma ronda, informe o codigo.

**Exemplo:** "iniciar ronda RON-2026-00001"

Ou consulte as rondas agendadas para hoje com `/ronda hoje`.""",
            "intent": RondaIntent.INICIAR_RONDA.value,
            "needs_info": ["round_code"],
            "suggestions": ["/ronda hoje", "Criar nova ronda"],
        }

    async def _handle_criar_ronda(self, message: str, context: Dict) -> Dict[str, Any]:
        """Redireciona para wizard de criacao de ronda."""
        return {
            "response": """**Criar Nova Ronda de Inspecao**

Vou guiar voce na criacao de uma nova ronda. Precisarei das seguintes informacoes:

1. Tipo de inspecao
2. Area/setor a inspecionar
3. Inspetor responsavel
4. Data e hora do agendamento
5. Pontos de verificacao
6. Observacoes (opcional)

**Vamos comecar?**""",
            "intent": RondaIntent.CRIAR_RONDA.value,
            "data": {"wizard": "ronda_wizard"},
            "suggestions": ["Sim, comecar", "Cancelar", "/ronda hoje"],
            "actions": [
                {
                    "type": "wizard",
                    "label": "Iniciar Wizard de Ronda",
                    "target": "ronda_wizard",
                    "data": {},
                }
            ],
        }

    async def _handle_default(self, message: str, context: Dict) -> Optional[Dict[str, Any]]:
        """Handler padrao - retorna None para permitir que DataConnector processe."""
        return None

    # ==========================================================================
    # FOLLOW-UP
    # ==========================================================================

    FOLLOWUP_PATTERNS = {
        "round_code": [
            r"^(RON-[\w-]+)$",
            r"(RON-\d{4}-\d{5})",
        ],
        "confirmation": [
            r"^(?:sim|s|yes|y|confirmar?|ok|pode|isso|exato|correto|comecar|vamos)$",
        ],
        "negation": [
            r"^(?:nao|n|no|cancelar?|parar|sair)$",
        ],
    }

    async def process_followup(
        self,
        message: str,
        context: Dict[str, Any],
        previous_intent: str,
        previous_data: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Processa follow-up de uma conversa anterior com o RondaAgent.

        Args:
            message: Mensagem do usuario (possivelmente curta)
            context: Contexto da conversa
            previous_intent: Intent da interacao anterior
            previous_data: Dados coletados na interacao anterior

        Returns:
            Dict com resposta ou None se nao for follow-up reconhecido
        """
        message_clean = message.strip().lower()
        previous_data = previous_data or {}

        # Follow-up de INICIAR_RONDA: espera confirmacao
        if previous_intent == RondaIntent.INICIAR_RONDA.value:
            for pattern in self.FOLLOWUP_PATTERNS["confirmation"]:
                if re.match(pattern, message_clean):
                    round_code = previous_data.get("code", "")
                    return {
                        "response": f"Ronda {round_code} iniciada! O status foi alterado para **Em Andamento**.\n\n"
                                    f"Registre os checkpoints durante a inspecao.",
                        "intent": RondaIntent.INICIAR_RONDA.value,
                        "data": {**previous_data, "confirmed": True},
                        "suggestions": ["/ronda andamento", "Ver detalhes"],
                    }

            for pattern in self.FOLLOWUP_PATTERNS["negation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Inicio da ronda cancelado. Posso ajudar com outra coisa?",
                        "intent": RondaIntent.INICIAR_RONDA.value,
                        "data": {**previous_data, "cancelled": True},
                        "suggestions": ["/ronda hoje", "/ronda stats", "Ajuda"],
                    }

        # Follow-up de CRIAR_RONDA: espera confirmacao para iniciar wizard
        if previous_intent == RondaIntent.CRIAR_RONDA.value:
            for pattern in self.FOLLOWUP_PATTERNS["confirmation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Iniciando wizard de criacao de ronda...\n\n"
                                    "**Passo 1/7 - Tipo de Inspecao**\n\n"
                                    "Qual o tipo de inspecao a ser realizada?",
                        "intent": RondaIntent.CRIAR_RONDA.value,
                        "data": {**previous_data, "wizard_started": True},
                        "suggestions": [
                            "Rotina",
                            "Emergencial",
                            "Programada",
                            "Especial",
                        ],
                    }

            for pattern in self.FOLLOWUP_PATTERNS["negation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Criacao de ronda cancelada. Posso ajudar com outra coisa?",
                        "intent": RondaIntent.CRIAR_RONDA.value,
                        "data": {**previous_data, "cancelled": True},
                        "suggestions": ["/ronda hoje", "/ronda stats", "Ajuda"],
                    }

        # Follow-up generico: espera codigo de ronda
        for pattern in self.FOLLOWUP_PATTERNS["round_code"]:
            match = re.search(pattern, message.strip(), re.IGNORECASE)
            if match:
                round_code = match.group(1).upper()
                return {
                    "response": f"Buscando ronda **{round_code}**...",
                    "intent": RondaIntent.RONDA_DETALHES.value,
                    "data": {"code": round_code},
                    "suggestions": ["Ver resultado", "Iniciar ronda", "/ronda hoje"],
                }

        return None

    def get_capabilities(self) -> List[str]:
        """Retorna lista de capabilities do agente."""
        return [
            "Consultar rondas agendadas para hoje",
            "Consultar rondas em andamento",
            "Ver detalhes de uma ronda especifica",
            "Ver resultado/relatorio de ronda concluida",
            "Consultar rondas por inspetor",
            "Estatisticas de rondas por status",
            "Iniciar uma ronda agendada",
            "Criar nova ronda de inspecao (wizard)",
        ]
