"""
Bartolo Engine - Motor Principal do Assistente.

Orquestra todos os componentes do Bartolo para processar
mensagens e gerar respostas inteligentes.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Optional
from uuid import UUID, uuid4

from modules.ai.bartolo.config.identity import (
    BARTOLO_IDENTITY,
    BARTOLO_PERSONALITY,
    BartoloConfig,
    get_greeting,
    get_closing,
)
from modules.ai.bartolo.config.modules import (
    MODULE_PROMPTS,
    get_module_prompt,
    get_module_capabilities,
    get_all_modules,
)
from modules.ai.bartolo.config.user_profiles import (
    UserRole,
    get_profile_context,
    get_profile_modules,
    get_communication_style,
)
from modules.ai.bartolo.services.profile_service import ProfileService, UserContext
from modules.ai.bartolo.services.data_connector import DataConnector
from modules.ai.bartolo.wizards.wizard_manager import WizardManager
from modules.ai.conversation.services.llm_provider import LLMProvider
from modules.ai.conversation.services.intent_classifier import IntentClassifier
from modules.ai.conversation.services.context_manager import ContextManager

logger = logging.getLogger(__name__)


@dataclass
class BartoloResponse:
    """Resposta do Bartolo."""
    message_id: UUID
    session_id: str
    response: str
    response_html: Optional[str] = None
    intent: Optional[str] = None
    confidence: float = 0.0
    suggestions: list = field(default_factory=list)
    actions: list = field(default_factory=list)
    wizard_response: Optional[dict] = None
    data_results: Optional[dict] = None
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
        config: Optional[BartoloConfig] = None,
        llm_provider: Optional[LLMProvider] = None,
        context_manager: Optional[ContextManager] = None,
        intent_classifier: Optional[IntentClassifier] = None,
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

        # Cache de sessoes
        self._session_cache: dict[str, dict] = {}

    def _get_session_key(self, user_id: int, session_id: str) -> str:
        """Gera chave de sessao."""
        return f"{user_id}:{session_id}"

    def _build_system_prompt(
        self,
        user_context: UserContext,
        module: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> str:
        """Constroi prompt de sistema completo."""
        parts = [BARTOLO_IDENTITY]

        # Adiciona contexto do usuario
        if user_context:
            parts.append(f"\n{user_context.to_prompt_context()}")

        # Adiciona prompt do modulo
        if module:
            module_prompt = get_module_prompt(module)
            if module_prompt:
                parts.append(f"\nMODULO ATUAL:\n{module_prompt}")

        # Adiciona contexto adicional
        if additional_context:
            parts.append(f"\nCONTEXTO ADICIONAL:\n{additional_context}")

        # Adiciona instrucoes finais
        parts.append("""
INSTRUCOES FINAIS:
- Sempre se apresente como Bartolo quando for a primeira interacao
- Use o nome do usuario quando disponivel
- Ofereca sugestoes proativas quando apropriado
- Se detectar que o usuario precisa de um wizard, ofereca para iniciar
- Mantenha respostas objetivas mas completas
""")

        return "\n".join(parts)

    def _detect_wizard_intent(self, message: str) -> Optional[str]:
        """Detecta se mensagem indica necessidade de wizard."""
        return self.wizard_manager.detect_wizard_type(message)

    def _generate_suggestions(
        self,
        intent: str,
        module: Optional[str],
        user_context: UserContext,
    ) -> list:
        """Gera sugestoes contextualizadas."""
        suggestions = []

        # Sugestoes por modulo
        if module and module in MODULE_PROMPTS:
            capabilities = get_module_capabilities(module)
            for cap in capabilities[:3]:
                cap_friendly = cap.replace("_", " ").title()
                suggestions.append({
                    "text": cap_friendly,
                    "action": cap,
                    "module": module,
                })

        # Sugestoes por perfil
        priority_modules = get_profile_modules(user_context.role) if user_context.role else []
        for mod in priority_modules[:2]:
            if mod != module:
                suggestions.append({
                    "text": f"Ir para {MODULE_PROMPTS.get(mod, {}).get('name', mod)}",
                    "action": "navigate",
                    "module": mod,
                })

        return suggestions[:4]

    async def process_message(
        self,
        user_id: int,
        session_id: str,
        message: str,
        module: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> BartoloResponse:
        """
        Processa uma mensagem do usuario.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            message: Mensagem do usuario
            module: Modulo atual (opcional)
            metadata: Metadados adicionais

        Returns:
            BartoloResponse com resposta completa
        """
        start_time = time.time()
        message_id = uuid4()
        metadata = metadata or {}

        try:
            # 1. Carrega contexto do usuario
            user_context = await self.profile_service.get_user_context(user_id)

            # 2. Verifica se tem wizard ativo
            if self.wizard_manager.has_active_wizard(user_id, session_id):
                wizard_response = self.wizard_manager.process_input(
                    user_id, session_id, message
                )
                if wizard_response:
                    return self._build_wizard_response(
                        message_id, session_id, wizard_response, start_time
                    )

            # 3. Classifica intencao
            intent_result = self.intent_classifier.classify(message)

            # 4. Verifica se deve iniciar wizard
            wizard_type = self._detect_wizard_intent(message)
            if wizard_type:
                wizard_response = self.wizard_manager.start_wizard(
                    wizard_type, user_id, session_id
                )
                return self._build_wizard_response(
                    message_id, session_id, wizard_response, start_time,
                    intro_message=f"Entendi! Vou te ajudar com isso."
                )

            # 5. Verifica se e consulta de dados
            data_results = None
            if self.config.use_data_connector:
                data_results = await self._check_data_query(message, module)

            # 6. Recupera contexto da conversa
            context = await self.context_manager.get_context(user_id, session_id)

            # 7. Atualiza contexto
            if module:
                context.module = module
            if intent_result.entities:
                context.entities.update(intent_result.entities)

            # 8. Adiciona mensagem ao historico
            await self.context_manager.add_message(
                user_id, session_id, "user", message,
                metadata={"intent": intent_result.intent.value}
            )

            # 9. Prepara mensagens para LLM
            llm_messages = await self.context_manager.get_messages_for_llm(
                user_id, session_id
            )

            # 10. Constroi prompt de sistema
            additional_context = None
            if data_results:
                additional_context = f"Dados encontrados no sistema:\n{data_results}"

            system_prompt = self._build_system_prompt(
                user_context, module, additional_context
            )

            # 11. Gera resposta
            llm_response = await self.llm_provider.generate(
                messages=llm_messages,
                system_prompt=system_prompt,
                max_tokens=self.config.max_response_tokens,
                temperature=0.7,
            )

            # 12. Adiciona resposta ao historico
            await self.context_manager.add_message(
                user_id, session_id, "assistant", llm_response.content,
                metadata={"model": llm_response.model}
            )

            # 13. Gera sugestoes
            suggestions = self._generate_suggestions(
                intent_result.intent.value, module, user_context
            )

            # 14. Monta resposta
            processing_time = int((time.time() - start_time) * 1000)

            return BartoloResponse(
                message_id=message_id,
                session_id=session_id,
                response=llm_response.content,
                response_html=self._format_html(llm_response.content),
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                suggestions=suggestions,
                actions=[],
                data_results=data_results,
                processing_time_ms=processing_time,
                model_used=llm_response.model,
                bartolo_mood="professional",
            )

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            processing_time = int((time.time() - start_time) * 1000)

            return BartoloResponse(
                message_id=message_id,
                session_id=session_id,
                response="Desculpe, ocorreu um erro ao processar sua mensagem. Pode tentar novamente?",
                processing_time_ms=processing_time,
                bartolo_mood="supportive",
            )

    async def process_message_stream(
        self,
        user_id: int,
        session_id: str,
        message: str,
        module: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Processa mensagem com streaming."""
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

        # Constroi prompt
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
        await self.context_manager.add_message(
            user_id, session_id, "assistant", response_text
        )

    def _build_wizard_response(
        self,
        message_id: UUID,
        session_id: str,
        wizard_response: Any,
        start_time: float,
        intro_message: Optional[str] = None,
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
            options_text = "\n".join(
                f"  {i+1}. {opt}" for i, opt in enumerate(wizard_response.options)
            )
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
        module: Optional[str],
    ) -> Optional[dict]:
        """Verifica se e consulta de dados e busca resultados."""
        # Por enquanto retorna None
        # Sera expandido para integrar com DataConnector
        return None

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

    async def get_greeting(self, user_id: int, session_id: str) -> str:
        """Retorna saudacao personalizada."""
        user_context = await self.profile_service.get_user_context(user_id)

        is_first_time = not self._session_cache.get(
            self._get_session_key(user_id, session_id)
        )

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
            modules.append({
                "id": module_id,
                "name": config.get("name", module_id),
                "description": config.get("description", ""),
                "category": config.get("category", "").value if config.get("category") else "",
            })
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
