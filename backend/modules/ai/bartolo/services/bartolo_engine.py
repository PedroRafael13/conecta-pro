"""
Bartolo Engine - Motor Principal do Assistente.

Orquestra todos os componentes do Bartolo para processar
mensagens e gerar respostas inteligentes.
"""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

# Agentes especializados (importação condicional)
try:
    from ..agents import AlertaAgent, EscalaAgent, SubstituicaoAgent

    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    EscalaAgent = None
    SubstituicaoAgent = None
    AlertaAgent = None

# Skills (importação condicional)
try:
    from ..skills import SKILL_REGISTRY, get_skill, list_skills

    SKILLS_AVAILABLE = True
except ImportError:
    SKILLS_AVAILABLE = False
    get_skill = None
    list_skills = None
    SKILL_REGISTRY = {}

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai.bartolo.actions import ActionExecutor, ActionPreview, EnhancedActionDetector
from modules.ai.bartolo.config.identity import (
    BartoloConfig,
    get_greeting,
)
from modules.ai.bartolo.config.modules import (
    MODULE_PROMPTS,
    get_all_modules,
    get_module_capabilities,
    get_module_prompt,
)
from modules.ai.bartolo.config.system_prompt import (
    OPERACIONAL_EXPERT_KNOWLEDGE,
    build_full_system_prompt,
    get_concise_system_prompt,
)
from modules.ai.bartolo.config.user_profiles import (
    get_profile_modules,
)
from modules.ai.bartolo.services.data_connector import DataConnector
from modules.ai.bartolo.services.llm_fallback_classifier import FallbackResult, LLMFallbackClassifier
from modules.ai.bartolo.services.profile_service import ProfileService, UserContext
from modules.ai.bartolo.wizards.wizard_manager import WizardManager
from modules.ai.conversation.services.context_manager import ContextManager
from modules.ai.conversation.services.intent_classifier import IntentClassifier
from modules.ai.conversation.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class BartoloResponse:
    """Resposta do Bartolo."""

    message_id: UUID
    session_id: str
    response: str
    response_html: str | None = None
    intent: str | None = None
    confidence: float = 0.0
    suggestions: list = field(default_factory=list)
    actions: list = field(default_factory=list)
    wizard_response: dict | None = None
    data_results: dict | None = None
    action_preview: ActionPreview | None = None  # NOVO: Preview de ação executiva
    processing_time_ms: int = 0
    model_used: str = ""
    bartolo_mood: str = "professional"


class BartoloEngine:
    """
    Motor principal do Bartolo.

    Integra todos os componentes:
    - LLM Provider para geracao de respostas
    - Profile Service para contexto do usuario
    - Data Connector para dados do sistema
    - Wizard Manager para assistencia guiada
    - Knowledge Base para RAG
    """

    def __init__(
        self,
        config: BartoloConfig | None = None,
        llm_provider: LLMProvider | None = None,
        context_manager: ContextManager | None = None,
        intent_classifier: IntentClassifier | None = None,
    ):
        """Inicializa o Bartolo."""
        self.config = config or BartoloConfig()
        self.llm_provider = llm_provider or LLMProvider()
        self.context_manager = context_manager or ContextManager()
        self.intent_classifier = intent_classifier or IntentClassifier()

        # Componentes do Bartolo
        self.profile_service = ProfileService()
        self.data_connector = DataConnector()
        self.wizard_manager = WizardManager()

        # LLM Fallback Classifier (Fase 3 do refinamento)
        self.llm_fallback_classifier = LLMFallbackClassifier(llm_provider=self.llm_provider)

        # Sistema de ações executivas (com detector avançado NLP)
        self.action_detector = EnhancedActionDetector(llm_provider=self.llm_provider, fuzzy_threshold=0.8)
        self.action_executor: ActionExecutor | None = None  # Inicializado com db

        # Agentes especializados (inicializados sob demanda com db)
        self.escala_agent = None
        self.substituicao_agent = None
        self.alerta_agent = None

        # Mapa de agentes por domínio (keywords -> agent_name)
        # NOTA: Keywords devem ser específicas para evitar capturar data queries.
        # Ex: "turno noite hoje" deve ir para DataConnector, não para agente escala.
        self.specialized_agents_map = {
            "gerar escala": "escala",
            "criar escala": "escala",
            "montar escala": "escala",
            "otimizar escala": "escala",
            "validar escala": "escala",
            "substituicao urgente": "substituicao",
            "buscar substituto": "substituicao",
            "preciso de substituto": "substituicao",
            "cobrir turno": "substituicao",
            "cobrir posto": "substituicao",
            "alerta critico": "alerta",
            "resolver alerta": "alerta",
        }

        # Cache de sessoes
        self._session_cache: dict[str, dict] = {}

    def _get_session_key(self, user_id: str, session_id: str) -> str:
        """Gera chave de sessao."""
        return f"{user_id}:{session_id}"

    def _build_system_prompt(
        self,
        user_context: UserContext,
        module: str | None = None,
        additional_context: str | None = None,
    ) -> str:
        """
        Constroi prompt de sistema otimizado.

        Usa prompt CONCISO (~200 tokens) para conversas gerais,
        enriquecido com contexto de modulo quando necessario.
        Prompt COMPLETO (~6k tokens) apenas quando ha dados adicionais.
        """
        # Formata contexto do usuario
        user_ctx_str = None
        if user_context:
            user_ctx_str = user_context.to_prompt_context()

        # Se ha dados adicionais (consulta com resultados), usa prompt completo
        if additional_context:
            return build_full_system_prompt(
                user_context=user_ctx_str,
                module=module,
                additional_context=additional_context,
            )

        # Para conversas gerais: prompt conciso + modulo especifico
        parts = [get_concise_system_prompt()]

        # Adiciona prompt do modulo atual
        if module:
            module_prompt = get_module_prompt(module)
            if module_prompt:
                parts.append(f"\nMODULO ATUAL:\n{module_prompt}")

            # Conhecimento operacional detalhado quando relevante
            if module in ("operacional", "escalas", "postos", "turnos"):
                parts.append(OPERACIONAL_EXPERT_KNOWLEDGE)

        # Contexto do usuario
        if user_ctx_str:
            parts.append(f"\nUSUARIO ATUAL:\n{user_ctx_str}")

        return "\n".join(parts)

    def _detect_wizard_intent(self, message: str) -> str | None:
        """
        Detecta se mensagem indica necessidade de wizard.

        CORRECAO CRITICA: Nunca retorna wizard se for pergunta/consulta.
        """
        # BLOQUEIO TOTAL: Se é pergunta, NUNCA é wizard
        if self._is_query_intent(message):
            logger.info(f"[WIZARD BLOCK] Mensagem é consulta, não inicia wizard: '{message[:50]}'")
            return None

        # Só tenta detectar wizard se NÃO for consulta
        wizard_type = self.wizard_manager.detect_wizard_type(message)
        if wizard_type:
            logger.info(f"[WIZARD START] Iniciando wizard: {wizard_type}")
        return wizard_type

    async def _check_skill_command(self, message: str, user_id: str, data_connector=None) -> dict[str, Any] | None:
        """
        Verifica se a mensagem é um comando de skill.

        Skills são comandos iniciados com / que executam ações específicas.
        Exemplo: /escala visualizar, /relatorio mensal

        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            data_connector: DataConnector para dados reais (opcional)

        Returns:
            Resultado do skill ou None se não for comando de skill
        """
        if not SKILLS_AVAILABLE or not message.startswith("/"):
            return None

        parts = message[1:].split()
        if not parts:
            return None

        skill_name = parts[0].lower()
        skill = get_skill(skill_name, data_connector=data_connector)

        if skill:
            command = parts[1] if len(parts) > 1 else ""
            args = parts[2:] if len(parts) > 2 else []

            try:
                result = await skill.execute(command, args, {"user_id": user_id})
                return result
            except Exception as e:
                logger.error(f"Erro ao executar skill {skill_name}: {e}")
                return {
                    "response": f"Erro ao executar comando /{skill_name}: {str(e)}",
                    "intent": "skill_error",
                    "suggestions": [f"Tente /{skill_name} ajuda para ver comandos disponíveis"],
                }

        # Skill não encontrado - lista skills disponíveis
        available = list_skills() if list_skills else []
        return {
            "response": f"Comando /{skill_name} não reconhecido.",
            "intent": "skill_not_found",
            "suggestions": [f"/{s}" for s in available[:5]] if available else [],
        }

    def _init_specialized_agents(self, db=None, data_connector=None) -> None:
        """
        Inicializa agentes especializados.

        Args:
            db: Sessão do banco de dados (opcional)
            data_connector: DataConnector com sessão do banco (opcional)
        """
        if not AGENTS_AVAILABLE:
            return

        # Inicializa agentes (funcionam com ou sem db)
        if self.escala_agent is None and EscalaAgent:
            self.escala_agent = EscalaAgent(db=db, data_connector=data_connector)
        elif self.escala_agent and data_connector:
            self.escala_agent.data_connector = data_connector
            self.escala_agent.db = db

        if self.substituicao_agent is None and SubstituicaoAgent:
            self.substituicao_agent = SubstituicaoAgent(db=db, data_connector=data_connector)
        elif self.substituicao_agent and data_connector:
            self.substituicao_agent.data_connector = data_connector
            self.substituicao_agent.db = db

        if self.alerta_agent is None and AlertaAgent:
            self.alerta_agent = AlertaAgent(db=db, data_connector=data_connector)
        elif self.alerta_agent and data_connector:
            self.alerta_agent.data_connector = data_connector
            self.alerta_agent.db = db

    def _get_specialized_agent(self, agent_name: str):
        """
        Retorna o agente especializado pelo nome.

        Args:
            agent_name: Nome do agente (escala, substituicao, alerta)

        Returns:
            Instância do agente ou None
        """
        agents = {
            "escala": self.escala_agent,
            "substituicao": self.substituicao_agent,
            "alerta": self.alerta_agent,
        }
        return agents.get(agent_name)

    def _detect_agent_name(
        self,
        message: str,
        intent: str,
        fallback_result: FallbackResult | None = None,
    ) -> str | None:
        """Detecta o nome do agente para metadata de contexto."""
        if fallback_result and fallback_result.agent_type:
            return fallback_result.agent_type

        message_lower = message.lower()
        for keyword, name in self.specialized_agents_map.items():
            if keyword in message_lower or keyword in intent.lower():
                return name
        return None

    async def _check_agent_followup(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ) -> dict[str, Any] | None:
        """
        Verifica se a mensagem é follow-up de uma interação anterior com agente.

        Consulta o context_manager para ver se a última resposta veio de um
        agente especializado e, se sim, roteia de volta para o mesmo agente.

        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            message: Mensagem atual do usuário

        Returns:
            Resultado do follow-up ou None
        """
        if not AGENTS_AVAILABLE:
            return None

        try:
            # Busca contexto COMPLETO (com metadata) - não usa get_messages_for_llm
            # porque esse método retorna só {role, content} sem metadata
            context = await self.context_manager.get_context(user_id, session_id)

            if not context or not context.messages:
                return None

            # Procura a última mensagem do assistant com metadata de agente
            last_agent_type = None
            last_agent_intent = None
            last_agent_data = None

            for msg in reversed(context.messages):
                if msg.get("role") == "assistant":
                    metadata = msg.get("metadata", {})
                    if metadata.get("model") == "specialized_agent" or metadata.get("agent_type"):
                        last_agent_type = metadata.get("agent_type")
                        last_agent_intent = metadata.get("agent_intent")
                        last_agent_data = metadata.get("agent_data")
                        break
                    # Se a última mensagem do assistant não veio de agente, não é follow-up
                    break

            if not last_agent_type:
                return None

            logger.info(f"[FOLLOWUP] Detectado contexto anterior: agent={last_agent_type} intent={last_agent_intent}")

            # Roteia para o agente com contexto de follow-up
            agent = self._get_specialized_agent(last_agent_type)
            if agent and hasattr(agent, "process_followup"):
                result = await agent.process_followup(
                    message=message,
                    context={"user_id": user_id},
                    previous_intent=last_agent_intent or "",
                    previous_data=last_agent_data,
                )
                if result:
                    logger.info(f"[FOLLOWUP] Agente {last_agent_type} processou follow-up")
                    return result

            # Se o agente não tem process_followup ou retornou None,
            # tenta processar normalmente pelo agente
            if agent:
                result = await agent.process(message, {"user_id": user_id})
                if result:
                    return result

        except Exception as e:
            logger.error(f"[FOLLOWUP] Erro ao verificar follow-up: {e}")

        return None

    async def _route_to_specialized_agent(
        self,
        message: str,
        intent: str,
        user_id: str,
        fallback_result: FallbackResult | None = None,
    ) -> dict[str, Any] | None:
        """
        Roteia para agente especializado se aplicável.

        Detecta pelo intent, palavras-chave ou resultado do LLM fallback
        se deve delegar para um agente especializado.

        Args:
            message: Mensagem do usuário
            intent: Intent detectado
            user_id: ID do usuário
            fallback_result: Resultado do LLM fallback classifier (opcional)

        Returns:
            Resultado do agente ou None se não aplicável
        """
        if not AGENTS_AVAILABLE:
            return None

        message_lower = message.lower()
        agent_name = None

        # 1. Primeiro tenta usar resultado do LLM fallback (mais preciso)
        if fallback_result and fallback_result.agent_type:
            agent_name = fallback_result.agent_type
            logger.info(f"[AGENT ROUTING] Usando sugestão do LLM fallback: {agent_name}")

        # 2. Se não tem fallback, detecta por keywords
        if not agent_name:
            for keyword, name in self.specialized_agents_map.items():
                if keyword in message_lower or keyword in intent.lower():
                    agent_name = name
                    break

        # 3. Roteia para o agente encontrado
        if agent_name:
            agent = self._get_specialized_agent(agent_name)
            if agent:
                try:
                    result = await agent.process(message, {"user_id": user_id})
                    return result
                except Exception as e:
                    logger.error(f"Erro no agente {agent_name}: {e}")
                    # Não retorna erro, deixa o fluxo normal processar

        return None

    def _format_response(
        self,
        response: str,
        intent: str = "unknown",
        suggestions: list = None,
        actions: list = None,
        data_results: dict = None,
    ) -> dict:
        """
        Formata resposta padronizada para retorno.

        Args:
            response: Texto da resposta
            intent: Intent detectado
            suggestions: Sugestões de próximas ações
            actions: Ações disponíveis
            data_results: Dados retornados

        Returns:
            Dicionário formatado
        """
        return {
            "response": response,
            "intent": intent,
            "suggestions": suggestions or [],
            "actions": actions or [],
            "data": data_results,
        }

    def _generate_suggestions(
        self,
        intent: str,
        module: str | None,
        user_context: UserContext,
    ) -> list:
        """Gera sugestoes contextualizadas."""
        suggestions = []

        # Sugestoes por modulo
        if module and module in MODULE_PROMPTS:
            capabilities = get_module_capabilities(module)
            for cap in capabilities[:3]:
                cap_friendly = cap.replace("_", " ").title()
                suggestions.append(
                    {
                        "text": cap_friendly,
                        "action": cap,
                        "module": module,
                    }
                )

        # Sugestoes por perfil
        priority_modules = get_profile_modules(user_context.role) if user_context.role else []
        for mod in priority_modules[:2]:
            if mod != module:
                suggestions.append(
                    {
                        "text": f"Ir para {MODULE_PROMPTS.get(mod, {}).get('name', mod)}",
                        "action": "navigate",
                        "module": mod,
                    }
                )

        return suggestions[:4]

    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        module: str | None = None,
        metadata: dict | None = None,
        db: AsyncSession | None = None,
    ) -> BartoloResponse:
        """
        Processa uma mensagem do usuario.

        Args:
            user_id: ID do usuario (UUID string ou int legacy)
            session_id: ID da sessao
            message: Mensagem do usuario
            module: Modulo atual (opcional)
            metadata: Metadados adicionais
            db: Sessão do banco de dados (opcional, para acesso a dados reais)

        Returns:
            BartoloResponse com resposta completa
        """
        start_time = time.time()
        message_id = uuid4()
        metadata = metadata or {}

        # Criar data_connector com db_session se disponível
        data_connector = DataConnector(db_session=db) if db else self.data_connector

        try:
            # 0. Inicializa agentes especializados (funciona com ou sem db)
            self._init_specialized_agents(db, data_connector=data_connector)

            # 0.1. Atualiza sessao do banco no ProfileService para buscar usuarios reais
            self.profile_service.set_db(db)

            # 1. Verifica se é comando de skill (antes de qualquer processamento)
            skill_result = await self._check_skill_command(message, user_id, data_connector=data_connector)
            if skill_result:
                processing_time = int((time.time() - start_time) * 1000)
                return BartoloResponse(
                    message_id=message_id,
                    session_id=session_id,
                    response=skill_result.get("response", ""),
                    intent=skill_result.get("intent", "skill_command"),
                    suggestions=skill_result.get("suggestions", []),
                    actions=skill_result.get("actions", []),
                    data_results=skill_result.get("data"),
                    processing_time_ms=processing_time,
                    model_used="skill_executor",
                    bartolo_mood="professional",
                )

            # 2. Carrega contexto do usuario
            user_context = await self.profile_service.get_user_context(user_id)

            # 3. Detecta tipo de mensagem (consulta/ação vs resposta wizard)
            # CORRECAO: Permite consultas mesmo com wizard ativo
            is_query_or_action = self._is_query_intent(message)
            logger.info(f"[QUERY DEBUG] Message: '{message[:50]}' | is_query: {is_query_or_action}")

            # 3.5. Verifica se tem wizard ativo E mensagem é resposta (não consulta)
            has_wizard = self.wizard_manager.has_active_wizard(user_id, session_id)
            if has_wizard:
                logger.info(f"[WIZARD DEBUG] Wizard ativo | is_query: {is_query_or_action}")

            if has_wizard and not is_query_or_action:
                wizard_response = self.wizard_manager.process_input(user_id, session_id, message)
                if wizard_response:
                    return self._build_wizard_response(message_id, session_id, wizard_response, start_time)

            # 4. Detecta ação executiva
            logger.info(f"[ACTION DEBUG] db={db is not None}, enable_actions={self.config.enable_actions}")
            if db and self.config.enable_actions:
                logger.info("[ACTION DEBUG] Entrando no fluxo de detecção de ações")
                # Inicializa executor se ainda não foi
                if not self.action_executor:
                    self.action_executor = ActionExecutor(db)
                    logger.info("[ACTION DEBUG] ActionExecutor inicializado")

                action_request = self.action_detector.detect(message, str(user_id), session_id)
                logger.info(f"[ACTION DEBUG] Resultado da detecção: {action_request is not None}")

                if action_request:
                    logger.info(f"Ação detectada: {action_request.action_type.value}")

                    # Criar preview da ação
                    action_preview = await self.action_executor.create_action_preview(action_request)

                    # Formatar resposta para o usuário
                    response_text = self._format_action_preview_response(action_preview)

                    processing_time = int((time.time() - start_time) * 1000)

                    return BartoloResponse(
                        message_id=message_id,
                        session_id=session_id,
                        response=response_text,
                        action_preview=action_preview,  # Inclui preview
                        processing_time_ms=processing_time,
                        model_used="action_detector",
                        bartolo_mood="professional",
                    )

            # 5. Classifica intencao
            intent_result = self.intent_classifier.classify(message)
            detected_intent = intent_result.intent.value
            regex_confidence = intent_result.confidence

            # 5b. LLM Fallback Classifier (se confiança regex baixa)
            fallback_result: FallbackResult | None = None
            if self.llm_fallback_classifier.should_use_fallback(regex_confidence):
                logger.info(f"[FALLBACK] Regex confidence baixa ({regex_confidence:.2f}), usando LLM fallback")
                try:
                    fallback_result = await self.llm_fallback_classifier.classify(
                        message=message,
                        regex_confidence=regex_confidence,
                        context={
                            "role": user_context.role if user_context else None,
                            "module": module,
                        },
                    )

                    # Se fallback tem resultado com agente, pode usar diretamente
                    if fallback_result and fallback_result.agent_type:
                        logger.info(
                            f"[FALLBACK] LLM sugeriu agente: {fallback_result.agent_type}/{fallback_result.agent_intent}"
                        )

                except Exception as e:
                    logger.error(f"[FALLBACK] Erro no LLM fallback: {e}")
                    fallback_result = None

            # 5.5 Detecção de follow-up: verifica se última interação foi com agente
            followup_result = await self._check_agent_followup(user_id, session_id, message)
            if followup_result:
                # Salva contexto do follow-up
                await self.context_manager.add_message(
                    user_id,
                    session_id,
                    "user",
                    message,
                    metadata={"intent": followup_result.get("intent", "followup"), "source": "followup"},
                )
                await self.context_manager.add_message(
                    user_id,
                    session_id,
                    "assistant",
                    followup_result.get("response", ""),
                    metadata={
                        "model": "specialized_agent_followup",
                        "agent_intent": followup_result.get("intent", ""),
                    },
                )

                processing_time = int((time.time() - start_time) * 1000)
                return BartoloResponse(
                    message_id=message_id,
                    session_id=session_id,
                    response=followup_result.get("response", ""),
                    intent=followup_result.get("intent", detected_intent),
                    suggestions=followup_result.get("suggestions", []),
                    actions=followup_result.get("actions", []),
                    data_results=followup_result.get("data"),
                    processing_time_ms=processing_time,
                    model_used="specialized_agent_followup",
                    bartolo_mood="professional",
                )

            # 6. Tenta rotear para agente especializado
            agent_result = await self._route_to_specialized_agent(message, detected_intent, user_id, fallback_result)
            if agent_result:
                # Salva contexto: mensagem do usuário + resposta do agente
                agent_intent = agent_result.get("intent", detected_intent)
                await self.context_manager.add_message(
                    user_id, session_id, "user", message, metadata={"intent": agent_intent, "source": "agent_routing"}
                )
                await self.context_manager.add_message(
                    user_id,
                    session_id,
                    "assistant",
                    agent_result.get("response", ""),
                    metadata={
                        "model": "specialized_agent",
                        "agent_intent": agent_intent,
                        "agent_type": self._detect_agent_name(message, detected_intent, fallback_result),
                    },
                )

                processing_time = int((time.time() - start_time) * 1000)
                return BartoloResponse(
                    message_id=message_id,
                    session_id=session_id,
                    response=agent_result.get("response", ""),
                    intent=agent_result.get("intent", detected_intent),
                    suggestions=agent_result.get("suggestions", []),
                    actions=agent_result.get("actions", []),
                    data_results=agent_result.get("data"),
                    processing_time_ms=processing_time,
                    model_used="specialized_agent",
                    bartolo_mood="professional",
                )

            # 7. Verifica se deve iniciar wizard
            wizard_type = self._detect_wizard_intent(message)
            if wizard_type:
                wizard_response = self.wizard_manager.start_wizard(wizard_type, user_id, session_id)
                return self._build_wizard_response(
                    message_id,
                    session_id,
                    wizard_response,
                    start_time,
                    intro_message="Entendi! Vou te ajudar com isso.",
                )

            # 8. Verifica se e consulta de dados
            logger.info(f"[DEBUG] Verificando data query para: {message}")
            data_results = None
            if self.config.use_data_connector:
                data_results = await self._check_data_query(message, module, data_connector)
                logger.info(f"[DEBUG] Data results: {data_results is not None}")

                # CORRECAO CRITICA: Se temos dados, retorna DIRETO sem LLM
                if data_results and data_results.get("message"):
                    logger.info("[DATA RESPONSE] Retornando dados diretamente")
                    processing_time = int((time.time() - start_time) * 1000)
                    return BartoloResponse(
                        message_id=message_id,
                        session_id=session_id,
                        response=data_results.get("message"),
                        intent="data_query",
                        data_results=data_results,
                        processing_time_ms=processing_time,
                        model_used="data_connector",
                        bartolo_mood="professional",
                    )

            # 9. Recupera contexto da conversa
            logger.info("[DEBUG] Recuperando contexto...")
            context = await self.context_manager.get_context(user_id, session_id)
            logger.info("[DEBUG] Contexto recuperado")

            # 10. Atualiza contexto
            if module:
                context.module = module
            if intent_result.entities:
                context.entities.update(intent_result.entities)

            # 11. Adiciona mensagem ao historico
            await self.context_manager.add_message(
                user_id, session_id, "user", message, metadata={"intent": detected_intent}
            )

            # 12. Prepara mensagens para LLM
            llm_messages = await self.context_manager.get_messages_for_llm(user_id, session_id)

            # 13. Constroi prompt de sistema
            additional_context = None
            if data_results and isinstance(data_results, dict):
                # Formata dados de forma clara e imperativa
                data_msg = data_results.get("message", "")
                total = data_results.get("total_count", 0)
                entity = data_results.get("entity", "")

                additional_context = f"""
🔴 DADOS REAIS CONSULTADOS NO BANCO DE DADOS:

{data_msg}

Total: {total}
Entidade: {entity}

IMPORTANTE: USE ESSES DADOS EXATOS NA SUA RESPOSTA!
NÃO dê instruções de como buscar - os dados JÁ ESTÃO AQUI!
"""

            system_prompt = self._build_system_prompt(user_context, module, additional_context)

            # 14. Gera resposta com LLM real (timeout 30s)
            # Conversas gerais: max_tokens reduzido para respostas concisas
            from core.config.settings import settings

            llm_max_tokens = 800 if not additional_context else settings.LLM_MAX_TOKENS
            llm_temperature = 0.4 if not additional_context else settings.LLM_TEMPERATURE
            logger.info(
                f"[LLM] msgs={len(llm_messages)} prompt={len(system_prompt)} chars "
                f"max_tokens={llm_max_tokens} temp={llm_temperature}"
            )
            llm_response = await asyncio.wait_for(
                self.llm_provider.generate(
                    messages=llm_messages,
                    system_prompt=system_prompt,
                    max_tokens=llm_max_tokens,
                    temperature=llm_temperature,
                ),
                timeout=30.0,
            )
            logger.info(f"[LLM] Respondeu: {len(llm_response.content)} chars")

            # 15. Adiciona resposta ao historico
            await self.context_manager.add_message(
                user_id, session_id, "assistant", llm_response.content, metadata={"model": llm_response.model}
            )

            # 16. Gera sugestoes
            suggestions = self._generate_suggestions(detected_intent, module, user_context)

            # 17. Monta resposta
            processing_time = int((time.time() - start_time) * 1000)

            return BartoloResponse(
                message_id=message_id,
                session_id=session_id,
                response=llm_response.content,
                response_html=self._format_html(llm_response.content),
                intent=detected_intent,
                confidence=intent_result.confidence,
                suggestions=suggestions,
                actions=[],
                data_results=data_results,
                processing_time_ms=processing_time,
                model_used=llm_response.model,
                bartolo_mood="professional",
            )

        except TimeoutError as e:
            logger.error(f"[TIMEOUT] user_id={user_id} session_id={session_id} message='{message[:80]}' error={e}")
            processing_time = int((time.time() - start_time) * 1000)
            return BartoloResponse(
                message_id=message_id,
                session_id=session_id,
                response="O servidor demorou para responder. Isso pode acontecer em momentos de alta demanda. Pode tentar novamente?",
                processing_time_ms=processing_time,
                bartolo_mood="supportive",
            )

        except ConnectionError as e:
            logger.error(f"[CONNECTION] user_id={user_id} session_id={session_id} message='{message[:80]}' error={e}")
            processing_time = int((time.time() - start_time) * 1000)
            return BartoloResponse(
                message_id=message_id,
                session_id=session_id,
                response="Não consegui me conectar ao serviço de IA. Verifique a conexão e tente novamente.",
                processing_time_ms=processing_time,
                bartolo_mood="supportive",
            )

        except PermissionError as e:
            logger.error(f"[PERMISSION] user_id={user_id} session_id={session_id} message='{message[:80]}' error={e}")
            processing_time = int((time.time() - start_time) * 1000)
            return BartoloResponse(
                message_id=message_id,
                session_id=session_id,
                response="Você não tem permissão para acessar este recurso. Entre em contato com o administrador.",
                processing_time_ms=processing_time,
                bartolo_mood="professional",
            )

        except Exception as e:
            error_type = type(e).__name__
            logger.exception(
                f"[UNEXPECTED] user_id={user_id} session_id={session_id} "
                f"message='{message[:80]}' error_type={error_type} error={e}"
            )
            processing_time = int((time.time() - start_time) * 1000)

            # Mensagem contextualizada
            if "rate" in str(e).lower() or "limit" in str(e).lower():
                error_msg = (
                    "O serviço de IA está temporariamente sobrecarregado. Aguarde alguns segundos e tente novamente."
                )
            elif "token" in str(e).lower() or "auth" in str(e).lower():
                error_msg = "Houve um problema de autenticação com o serviço de IA. O administrador foi notificado."
            else:
                error_msg = "Desculpe, ocorreu um erro inesperado ao processar sua mensagem. Pode tentar novamente?"

            return BartoloResponse(
                message_id=message_id,
                session_id=session_id,
                response=error_msg,
                processing_time_ms=processing_time,
                bartolo_mood="supportive",
            )

    async def process_message_stream(
        self,
        user_id: str,
        session_id: str,
        message: str,
        module: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Processa mensagem com streaming (prompt conciso)."""
        # Carrega contexto
        user_context = await self.profile_service.get_user_context(user_id)

        # Recupera contexto da conversa
        context = await self.context_manager.get_context(user_id, session_id)
        if module:
            context.module = module

        # Adiciona mensagem
        await self.context_manager.add_message(user_id, session_id, "user", message)

        # Prepara mensagens
        llm_messages = await self.context_manager.get_messages_for_llm(user_id, session_id)

        # Constroi prompt (conciso para stream)
        system_prompt = self._build_system_prompt(user_context, module)

        # Stream resposta
        full_response = []
        async for chunk in self.llm_provider.generate_stream(
            messages=llm_messages,
            system_prompt=system_prompt,
        ):
            full_response.append(chunk)
            yield chunk

        # Salva resposta completa
        response_text = "".join(full_response)
        await self.context_manager.add_message(user_id, session_id, "assistant", response_text)

    def _build_wizard_response(
        self,
        message_id: UUID,
        session_id: str,
        wizard_response: Any,
        start_time: float,
        intro_message: str | None = None,
    ) -> BartoloResponse:
        """Constroi resposta de wizard."""
        processing_time = int((time.time() - start_time) * 1000)

        # Monta mensagem
        message_parts = []
        if intro_message:
            message_parts.append(intro_message)

        message_parts.append(wizard_response.message)

        if wizard_response.question:
            message_parts.append(f"\n{wizard_response.question}")

        if wizard_response.options:
            options_text = "\n".join(f"  {i + 1}. {opt}" for i, opt in enumerate(wizard_response.options))
            message_parts.append(f"\n{options_text}")

        if wizard_response.help_text:
            message_parts.append(f"\n*{wizard_response.help_text}*")

        # Adiciona progresso
        if wizard_response.total_steps > 0:
            progress = f"\n\n[Passo {wizard_response.step_number} de {wizard_response.total_steps}]"
            message_parts.append(progress)

        return BartoloResponse(
            message_id=message_id,
            session_id=session_id,
            response="\n".join(message_parts),
            wizard_response={
                "wizard_id": str(wizard_response.wizard_id),
                "step_id": wizard_response.step_id,
                "step_number": wizard_response.step_number,
                "total_steps": wizard_response.total_steps,
                "state": wizard_response.state.value,
                "options": wizard_response.options,
                "progress_percent": wizard_response.progress_percent,
            },
            processing_time_ms=processing_time,
            bartolo_mood="focused",
        )

    async def _check_data_query(
        self,
        message: str,
        module: str | None,
        data_connector: DataConnector,
    ) -> dict | None:
        """Verifica se e consulta de dados e busca resultados."""
        try:
            # Detecta se é uma query de dados
            data_query = data_connector.detect_data_query(message)

            if data_query:
                logger.info(f"Query de dados detectada: {data_query.entity} ({data_query.query_type})")

                result = await data_connector.execute_query(data_query)

                if result.success:
                    return {
                        "entity": result.entity,
                        "query_type": result.query_type.value,
                        "total_count": result.total_count,
                        "data": result.data,
                        "message": result.to_natural_language(),
                    }

            # Verifica se é pedido de dashboard
            if any(word in message.lower() for word in ["dashboard", "resumo", "visao geral"]):
                if module:
                    dashboard_data = await data_connector.get_dashboard_data(module)
                    if dashboard_data:
                        return {
                            "type": "dashboard",
                            "module": module,
                            "data": dashboard_data,
                        }

            return None

        except Exception as e:
            logger.error(f"Erro ao verificar data query: {e}")
            return None

    def _format_action_preview_response(self, preview: ActionPreview) -> str:
        """
        Formata resposta com preview de ação para o usuário.

        Args:
            preview: Preview da ação

        Returns:
            Texto formatado em markdown
        """
        response = f"Entendi! Você quer **{preview.title}**.\n\n"
        response += f"{preview.description}\n\n"

        if preview.changes_summary:
            response += "**O que será feito:**\n"
            for change in preview.changes_summary:
                response += f"- {change}\n"
            response += "\n"

        if preview.warnings:
            response += "**⚠️ Avisos:**\n"
            for warning in preview.warnings:
                response += f"- {warning}\n"
            response += "\n"

        if not preview.user_has_permission:
            response += f"**⛔ Permissão Necessária:** {preview.required_permission}\n"
            response += "Você não tem permissão para executar esta ação.\n"
        else:
            response += "**Deseja confirmar esta ação?**\n"
            response += (
                f"_(Pode {'ser desfeita' if preview.can_be_undone else 'não pode ser desfeita'} posteriormente)_"
            )

        return response

    def _format_html(self, text: str) -> str:
        """Formata resposta como HTML."""
        import re

        html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Bold
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        # Italic
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        # Code
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)
        # Line breaks
        html = html.replace("\n", "<br>")

        return f"<div class='bartolo-response'>{html}</div>"

    async def get_greeting(self, user_id: str, session_id: str) -> str:
        """Retorna saudacao personalizada."""
        user_context = await self.profile_service.get_user_context(user_id)

        is_first_time = not self._session_cache.get(self._get_session_key(user_id, session_id))

        greeting = get_greeting(user_context.name, is_first_time)

        # Marca sessao como iniciada
        self._session_cache[self._get_session_key(user_id, session_id)] = {
            "started_at": datetime.utcnow(),
        }

        return greeting

    async def get_available_wizards(self) -> list:
        """Retorna wizards disponiveis."""
        return self.wizard_manager.get_available_wizards()

    async def get_available_modules(self) -> list:
        """Retorna modulos disponiveis."""
        modules = []
        for module_id in get_all_modules():
            config = MODULE_PROMPTS.get(module_id, {})
            modules.append(
                {
                    "id": module_id,
                    "name": config.get("name", module_id),
                    "description": config.get("description", ""),
                    "category": config.get("category", "").value if config.get("category") else "",
                }
            )
        return modules

    def get_stats(self) -> dict:
        """Retorna estatisticas do Bartolo."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "active_sessions": len(self._session_cache),
            "active_wizards": len(self.wizard_manager.active_wizards),
            "modules_available": len(get_all_modules()),
            "wizards_available": len(self.wizard_manager.get_available_wizards()),
        }

    def _is_query_intent(self, message: str) -> bool:
        """
        Detecta se a mensagem é uma consulta/pergunta ao invés de resposta ao wizard.

        Verifica verbos de consulta, interrogação, comandos de skill, etc.
        Usado para permitir consultas mesmo durante wizard ativo.

        Args:
            message: Mensagem do usuário

        Returns:
            True se é consulta/ação, False se é provável resposta ao wizard
        """
        message_lower = message.lower().strip()

        # 1. Comandos de skill sempre são consultas
        if message_lower.startswith("/"):
            return True

        # 2. Verbos de consulta (início da frase)
        query_verbs = [
            "mostrar",
            "listar",
            "ver",
            "verificar",
            "consultar",
            "buscar",
            "checar",
            "conferir",
            "exibir",
            "procurar",
            "encontrar",
            "qual",
            "quais",
            "quantos",
            "quanto",
            "quem",
            "onde",
            "quando",
            "como",
            "existe",
            "tem",
            "há",
            "temos",
            "tenho",
        ]
        if any(message_lower.startswith(verb) for verb in query_verbs):
            return True

        # 3. Perguntas (presença de interrogação ou palavras interrogativas)
        if "?" in message:
            return True

        interrogatives = ["qual", "quais", "quantos", "quanto", "quem", "onde", "quando", "como", "por que", "porque"]
        if any(word in message_lower.split()[:5] for word in interrogatives):  # Primeiras 5 palavras
            return True

        # 4. Comandos de ação
        action_verbs = [
            "criar",
            "registrar",
            "adicionar",
            "excluir",
            "deletar",
            "atualizar",
            "modificar",
            "alterar",
            "editar",
            "salvar",
            "enviar",
            "cancelar",
        ]
        # Ações geralmente têm contexto (ex: "criar comunicado", não só "programada")
        first_word = message_lower.split()[0] if message_lower.split() else ""
        if first_word in action_verbs:
            return True

        # 5. Mensagens muito curtas (1-3 palavras) SEM contexto provavelmente são respostas ao wizard
        words = message_lower.split()
        if len(words) <= 3:
            # Se é uma palavra simples comum em respostas de wizard
            simple_responses = [
                "sim",
                "não",
                "ok",
                "continuar",
                "prosseguir",
                "avançar",
                "rotina",
                "programada",
                "emergencial",
                "noturna",
                "especial",
                "normal",
                "alta",
                "baixa",
                "urgente",
            ]
            if message_lower in simple_responses or any(w in simple_responses for w in words):
                return False  # Provavelmente resposta ao wizard

        # 6. Default: Mensagens com 4+ palavras sem verbos de ação são provavelmente consultas
        if len(words) >= 4:
            return True

        # 7. Se não detectou nada, considera resposta ao wizard
        return False
