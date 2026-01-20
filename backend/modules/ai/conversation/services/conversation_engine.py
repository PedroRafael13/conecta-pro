"""Motor principal de conversacao."""

import logging
import time
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Optional
from uuid import UUID, uuid4

from modules.ai.conversation.models.chat_message import IntentCategory, MessageType
from modules.ai.conversation.services.context_manager import ContextManager, ConversationContext
from modules.ai.conversation.services.intent_classifier import IntentClassifier, IntentResult
from modules.ai.conversation.services.llm_provider import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class ConversationResult:
    """Resultado de uma interacao de conversa."""

    message_id: UUID
    session_id: UUID
    response: str
    response_html: Optional[str]
    intent: IntentCategory
    intent_confidence: float
    entities: dict[str, Any]
    suggestions: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    processing_time_ms: int
    model_used: str
    tokens_used: int


class ConversationEngine:
    """
    Motor principal de conversacao.

    Orquestra todos os componentes:
    - IntentClassifier: Classifica intencoes do usuario
    - ContextManager: Gerencia contexto da conversa
    - LLMProvider: Gera respostas usando LLM
    - ResponseGenerator: Formata e enriquece respostas

    Funcionalidades:
    - Processamento de mensagens
    - Gerenciamento de sessoes
    - Streaming de respostas
    - Metricas e analytics
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        context_manager: Optional[ContextManager] = None,
        intent_classifier: Optional[IntentClassifier] = None,
    ) -> None:
        """
        Inicializa o motor de conversacao.

        Args:
            llm_provider: Provider de LLM
            context_manager: Gerenciador de contexto
            intent_classifier: Classificador de intencoes
        """
        self.llm_provider = llm_provider or LLMProvider()
        self.context_manager = context_manager or ContextManager()
        self.intent_classifier = intent_classifier or IntentClassifier()

        # Sistema de prompts por modulo
        self.module_prompts: dict[str, str] = {
            "crm": self._get_crm_prompt(),
            "financial": self._get_financial_prompt(),
            "hr": self._get_hr_prompt(),
            "inventory": self._get_inventory_prompt(),
        }

    def _get_base_prompt(self) -> str:
        """Retorna prompt base do sistema."""
        return """Voce e o assistente inteligente do Conecta PRO, um sistema ERP completo.

Suas capacidades incluem:
- Ajudar na navegacao do sistema
- Responder perguntas sobre funcionalidades
- Auxiliar na consulta e analise de dados
- Guiar o usuario em operacoes complexas
- Fornecer insights e sugestoes baseadas em dados

Diretrizes:
- Seja claro, objetivo e prestativo
- Use portugues brasileiro
- Ofereca sugestoes de proximos passos quando apropriado
- Se nao souber algo, admita e sugira alternativas
- Mantenha um tom profissional mas amigavel
"""

    def _get_crm_prompt(self) -> str:
        """Prompt especifico para modulo CRM."""
        return """Voce esta no modulo de CRM (Customer Relationship Management).

Funcionalidades disponiveis:
- Gestao de Leads: criar, qualificar, converter
- Gestao de Clientes: cadastro, historico, segmentacao
- Pipeline de Vendas: oportunidades, propostas, conversoes
- Atividades: tarefas, compromissos, follow-ups
- Relatorios: performance, funil, previsoes

Entidades principais:
- Lead: potencial cliente em prospecção
- Cliente: pessoa/empresa com relacionamento ativo
- Oportunidade: negocio em andamento no pipeline
- Proposta: oferta comercial enviada ao cliente
"""

    def _get_financial_prompt(self) -> str:
        """Prompt especifico para modulo Financeiro."""
        return """Voce esta no modulo Financeiro.

Funcionalidades disponiveis:
- Contas a Pagar: cadastro, baixa, programacao
- Contas a Receber: faturamento, cobranca, recebimentos
- Fluxo de Caixa: previsoes, movimentacoes
- Conciliacao Bancaria: importacao, conferencia
- Relatorios: DRE, balanco, indicadores

Entidades principais:
- Lancamento: movimentacao financeira
- Titulo: conta a pagar ou receber
- Centro de Custo: classificacao de despesas/receitas
- Conta Bancaria: contas para movimentacao
"""

    def _get_hr_prompt(self) -> str:
        """Prompt especifico para modulo RH."""
        return """Voce esta no modulo de Recursos Humanos.

Funcionalidades disponiveis:
- Cadastro de Funcionarios: dados, documentos, historico
- Folha de Pagamento: calculos, holerites, encargos
- Ponto Eletronico: registro, banco de horas
- Ferias e Afastamentos: controle, programacao
- Relatorios: headcount, turnover, custos

Entidades principais:
- Funcionario: colaborador da empresa
- Cargo: posicao na estrutura organizacional
- Departamento: area/setor da empresa
- Beneficio: vale, plano de saude, etc.
"""

    def _get_inventory_prompt(self) -> str:
        """Prompt especifico para modulo Estoque."""
        return """Voce esta no modulo de Estoque.

Funcionalidades disponiveis:
- Cadastro de Produtos: SKU, categorias, atributos
- Movimentacoes: entrada, saida, transferencia
- Inventario: contagem, ajustes
- Almoxarifados: localizacao, organizacao
- Relatorios: posicao, giro, curva ABC

Entidades principais:
- Produto: item comercializado ou consumido
- Almoxarifado: local de armazenamento
- Movimentacao: entrada/saida de estoque
- Lote: agrupamento para rastreabilidade
"""

    def _build_system_prompt(
        self, context: ConversationContext, user_name: Optional[str] = None
    ) -> str:
        """Constroi prompt de sistema baseado no contexto."""
        parts = [self._get_base_prompt()]

        # Adiciona prompt do modulo se aplicavel
        if context.module and context.module in self.module_prompts:
            parts.append(self.module_prompts[context.module])

        # Adiciona nome do usuario
        if user_name:
            parts.append(f"\nO usuario se chama {user_name}.")

        # Adiciona entidades do contexto
        if context.entities:
            entities_str = ", ".join(
                f"{k}: {v}" for k, v in context.entities.items()
            )
            parts.append(f"\nEntidades identificadas: {entities_str}")

        # Adiciona preferencias
        if context.preferences:
            prefs_str = ", ".join(
                f"{k}: {v}" for k, v in context.preferences.items()
            )
            parts.append(f"\nPreferencias do usuario: {prefs_str}")

        return "\n".join(parts)

    def _generate_suggestions(
        self, intent: IntentResult, response: str, context: ConversationContext
    ) -> list[dict[str, Any]]:
        """Gera sugestoes baseadas na intencao e resposta."""
        suggestions = []

        # Sugestoes por intencao
        if intent.intent == IntentCategory.GREETING:
            suggestions.extend([
                {"text": "Ver dashboard", "type": "quick_reply", "action": "navigate", "payload": {"route": "/dashboard"}},
                {"text": "Minhas tarefas", "type": "quick_reply", "action": "navigate", "payload": {"route": "/tasks"}},
                {"text": "O que posso fazer?", "type": "quick_reply", "action": "ask"},
            ])
        elif intent.intent == IntentCategory.DATA_QUERY:
            suggestions.extend([
                {"text": "Exportar dados", "type": "action", "action": "export"},
                {"text": "Ver grafico", "type": "action", "action": "chart"},
                {"text": "Filtrar resultados", "type": "action", "action": "filter"},
            ])
        elif intent.intent == IntentCategory.ACTION_REQUEST:
            suggestions.extend([
                {"text": "Confirmar acao", "type": "action", "action": "confirm"},
                {"text": "Cancelar", "type": "action", "action": "cancel"},
            ])
        elif intent.intent == IntentCategory.HELP_NAVIGATION:
            suggestions.extend([
                {"text": "Ver tutorial", "type": "quick_reply", "action": "tutorial"},
                {"text": "Abrir ajuda", "type": "quick_reply", "action": "help"},
            ])
        elif intent.intent == IntentCategory.TROUBLESHOOTING:
            suggestions.extend([
                {"text": "Abrir chamado", "type": "action", "action": "ticket"},
                {"text": "Ver FAQ", "type": "quick_reply", "action": "faq"},
                {"text": "Contatar suporte", "type": "action", "action": "support"},
            ])

        # Sugestoes baseadas no modulo
        if context.module == "crm":
            suggestions.append(
                {"text": "Novo lead", "type": "quick_reply", "action": "create", "payload": {"entity": "lead"}}
            )
        elif context.module == "financial":
            suggestions.append(
                {"text": "Fluxo de caixa", "type": "quick_reply", "action": "navigate", "payload": {"route": "/financial/cashflow"}}
            )

        return suggestions[:4]  # Limita a 4 sugestoes

    def _generate_actions(
        self, intent: IntentResult, entities: dict[str, Any], context: ConversationContext
    ) -> list[dict[str, Any]]:
        """Gera acoes possiveis baseadas na intencao e entidades."""
        actions = []

        if intent.intent == IntentCategory.ACTION_REQUEST:
            # Detecta tipo de acao pelas keywords
            keywords = intent.keywords_matched

            if any(k in keywords for k in ["criar", "adicionar", "cadastrar", "registrar"]):
                entity = entities.get("module", context.module or "item")
                actions.append({
                    "type": "create",
                    "label": f"Criar {entity}",
                    "module": context.module,
                    "entity": entity,
                    "requires_confirmation": True,
                })
            elif any(k in keywords for k in ["deletar", "excluir", "remover"]):
                actions.append({
                    "type": "delete",
                    "label": "Excluir registro",
                    "requires_confirmation": True,
                })
            elif any(k in keywords for k in ["editar", "alterar", "atualizar", "modificar"]):
                actions.append({
                    "type": "update",
                    "label": "Editar registro",
                    "requires_confirmation": False,
                })

        elif intent.intent == IntentCategory.DATA_QUERY:
            actions.append({
                "type": "export",
                "label": "Exportar para Excel",
                "params": {"format": "xlsx"},
            })

        elif intent.intent == IntentCategory.ANALYSIS_REQUEST:
            actions.append({
                "type": "report",
                "label": "Gerar relatorio",
                "params": {"format": "pdf"},
            })

        return actions

    async def process_message(
        self,
        user_id: int,
        session_id: str,
        message: str,
        user_name: Optional[str] = None,
        context_data: Optional[dict[str, Any]] = None,
    ) -> ConversationResult:
        """
        Processa uma mensagem do usuario.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            message: Mensagem do usuario
            user_name: Nome do usuario
            context_data: Dados adicionais de contexto

        Returns:
            ConversationResult com resposta e metadados
        """
        start_time = time.time()
        message_id = uuid4()

        try:
            # 1. Classifica intencao
            intent_result = self.intent_classifier.classify(message)
            logger.info(
                f"Intent classificado: {intent_result.intent.value} "
                f"(conf: {intent_result.confidence})"
            )

            # 2. Recupera/atualiza contexto
            context = await self.context_manager.get_context(user_id, session_id)

            # Atualiza contexto com dados fornecidos
            if context_data:
                context.metadata.update(context_data)
                if "module" in context_data:
                    context.module = context_data["module"]

            # Atualiza entidades extraidas
            if intent_result.entities:
                context.entities.update(intent_result.entities)

            # 3. Adiciona mensagem do usuario ao contexto
            await self.context_manager.add_message(
                user_id=user_id,
                session_id=session_id,
                role="user",
                content=message,
                metadata={
                    "intent": intent_result.intent.value,
                    "confidence": intent_result.confidence,
                },
            )

            # 4. Prepara mensagens para o LLM
            llm_messages = await self.context_manager.get_messages_for_llm(
                user_id, session_id
            )

            # 5. Constroi prompt de sistema
            system_prompt = self._build_system_prompt(context, user_name)

            # 6. Gera resposta do LLM
            llm_response: LLMResponse = await self.llm_provider.generate(
                messages=llm_messages,
                system_prompt=system_prompt,
                max_tokens=1500,
                temperature=0.7,
            )

            # 7. Adiciona resposta ao contexto
            await self.context_manager.add_message(
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                content=llm_response.content,
                metadata={
                    "model": llm_response.model,
                    "tokens": llm_response.tokens_used,
                },
            )

            # 8. Salva contexto atualizado
            await self.context_manager.save_context(context)

            # 9. Gera sugestoes e acoes
            suggestions = self._generate_suggestions(intent_result, llm_response.content, context)
            actions = self._generate_actions(intent_result, intent_result.entities, context)

            # 10. Calcula tempo de processamento
            processing_time_ms = int((time.time() - start_time) * 1000)

            return ConversationResult(
                message_id=message_id,
                session_id=UUID(session_id) if isinstance(session_id, str) else session_id,
                response=llm_response.content,
                response_html=self._format_response_html(llm_response.content),
                intent=intent_result.intent,
                intent_confidence=intent_result.confidence,
                entities=intent_result.entities,
                suggestions=suggestions,
                actions=actions,
                processing_time_ms=processing_time_ms,
                model_used=llm_response.model,
                tokens_used=llm_response.tokens_used,
            )

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Retorna resposta de erro
            return ConversationResult(
                message_id=message_id,
                session_id=UUID(session_id) if isinstance(session_id, str) else session_id,
                response="Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.",
                response_html=None,
                intent=IntentCategory.GENERAL_CONVERSATION,
                intent_confidence=0.0,
                entities={},
                suggestions=[
                    {"text": "Tentar novamente", "type": "action", "action": "retry"}
                ],
                actions=[],
                processing_time_ms=processing_time_ms,
                model_used="error",
                tokens_used=0,
            )

    async def process_message_stream(
        self,
        user_id: int,
        session_id: str,
        message: str,
        user_name: Optional[str] = None,
        context_data: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Processa mensagem com streaming de resposta.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            message: Mensagem do usuario
            user_name: Nome do usuario
            context_data: Dados de contexto

        Yields:
            Chunks da resposta
        """
        try:
            # Classifica intencao
            intent_result = self.intent_classifier.classify(message)

            # Recupera contexto
            context = await self.context_manager.get_context(user_id, session_id)

            if context_data:
                context.metadata.update(context_data)
                if "module" in context_data:
                    context.module = context_data["module"]

            # Adiciona mensagem ao contexto
            await self.context_manager.add_message(
                user_id=user_id,
                session_id=session_id,
                role="user",
                content=message,
            )

            # Prepara mensagens e prompt
            llm_messages = await self.context_manager.get_messages_for_llm(
                user_id, session_id
            )
            system_prompt = self._build_system_prompt(context, user_name)

            # Gera resposta em streaming
            full_response = []
            async for chunk in self.llm_provider.generate_stream(
                messages=llm_messages,
                system_prompt=system_prompt,
            ):
                full_response.append(chunk)
                yield chunk

            # Salva resposta completa no contexto
            response_text = "".join(full_response)
            await self.context_manager.add_message(
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                content=response_text,
            )

        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield "Desculpe, ocorreu um erro. Tente novamente."

    def _format_response_html(self, text: str) -> str:
        """Formata resposta como HTML."""
        import re

        # Escapa HTML
        html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Converte markdown basico
        # Bold
        html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
        # Italic
        html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)
        # Code inline
        html = re.sub(r"`(.*?)`", r"<code>\1</code>", html)
        # Line breaks
        html = html.replace("\n", "<br>")
        # Lists
        html = re.sub(r"^- (.*)$", r"<li>\1</li>", html, flags=re.MULTILINE)

        return f"<div class='chat-response'>{html}</div>"

    async def get_conversation_summary(
        self, user_id: int, session_id: str
    ) -> dict[str, Any]:
        """Retorna resumo da conversa."""
        context = await self.context_manager.get_context(user_id, session_id)

        return {
            "session_id": session_id,
            "message_count": len(context.messages),
            "module": context.module,
            "entities": context.entities,
            "last_updated": context.updated_at.isoformat() if context.updated_at else None,
        }

    async def clear_conversation(self, user_id: int, session_id: str) -> None:
        """Limpa historico da conversa."""
        await self.context_manager.clear_context(user_id, session_id)
        logger.info(f"Conversa limpa: user={user_id}, session={session_id}")

    async def set_module_context(
        self, user_id: int, session_id: str, module: str
    ) -> None:
        """Define modulo ativo na conversa."""
        await self.context_manager.set_module(user_id, session_id, module)
        logger.info(f"Modulo definido: {module}")
