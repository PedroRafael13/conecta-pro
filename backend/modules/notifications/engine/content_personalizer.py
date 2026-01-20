"""Personalizador de conteúdo para notificações."""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class PersonalizedContent:
    """Conteúdo personalizado."""

    title: str
    body: str
    summary: Optional[str]
    cta_text: Optional[str]
    cta_url: Optional[str]
    image_url: Optional[str]
    metadata: dict[str, Any]
    personalization_score: float
    variables_used: list[str]


@dataclass
class ContentVariant:
    """Variante de conteúdo para A/B testing."""

    variant_id: str
    content: PersonalizedContent
    target_segment: Optional[str]
    weight: float = 1.0


class ContentPersonalizer:
    """
    Personalizador de conteúdo de notificações.

    Personaliza templates com:
    - Variáveis dinâmicas do usuário
    - Conteúdo baseado em comportamento
    - Ajustes de tom e linguagem
    - Localização (i18n)
    """

    # Padrões de variáveis
    VAR_PATTERN = re.compile(r"\{\{(\w+(?:\.\w+)*)\}\}")
    CONDITIONAL_PATTERN = re.compile(
        r"\{% if (\w+) %\}(.*?)\{% else %\}(.*?)\{% endif %\}",
        re.DOTALL,
    )

    # Mapeamento de tons
    TONE_ADJUSTMENTS = {
        "formal": {
            "greeting": "Prezado(a)",
            "closing": "Atenciosamente",
            "pronouns": ["você", "sua", "seu"],
        },
        "friendly": {
            "greeting": "Olá",
            "closing": "Abraços",
            "pronouns": ["você", "sua", "seu"],
        },
        "casual": {
            "greeting": "E aí",
            "closing": "Valeu",
            "pronouns": ["tu", "tua", "teu"],
        },
    }

    def __init__(
        self,
        default_locale: str = "pt-BR",
        max_title_length: int = 100,
        max_body_length: int = 1000,
    ) -> None:
        """
        Inicializa o personalizador.

        Args:
            default_locale: Locale padrão
            max_title_length: Tamanho máximo do título
            max_body_length: Tamanho máximo do corpo
        """
        self.default_locale = default_locale
        self.max_title = max_title_length
        self.max_body = max_body_length

    async def personalize(
        self,
        db: AsyncSession,
        template_title: str,
        template_body: str,
        user_id: int,
        context: Optional[dict[str, Any]] = None,
        tone: str = "friendly",
        locale: Optional[str] = None,
    ) -> PersonalizedContent:
        """
        Personaliza conteúdo do template.

        Args:
            db: Sessão do banco
            template_title: Template do título
            template_body: Template do corpo
            user_id: ID do usuário
            context: Contexto adicional
            tone: Tom da mensagem
            locale: Locale específico

        Returns:
            PersonalizedContent com conteúdo personalizado
        """
        context = context or {}
        locale = locale or self.default_locale

        # Obter dados do usuário
        user_data = await self._get_user_data(db, user_id)
        behavior_data = await self._get_behavior_data(db, user_id)

        # Construir variáveis
        variables = self._build_variables(user_data, behavior_data, context)

        # Processar condicionais
        title = self._process_conditionals(template_title, variables)
        body = self._process_conditionals(template_body, variables)

        # Substituir variáveis
        title, title_vars = self._replace_variables(title, variables)
        body, body_vars = self._replace_variables(body, variables)

        # Aplicar ajustes de tom
        body = self._apply_tone(body, tone)

        # Truncar se necessário
        title = self._truncate(title, self.max_title)
        body = self._truncate(body, self.max_body)

        # Gerar summary
        summary = self._generate_summary(body)

        # Personalizar CTA
        cta_text, cta_url = self._personalize_cta(context, user_data)

        # Calcular score de personalização
        all_vars = list(set(title_vars + body_vars))
        score = self._calculate_personalization_score(all_vars, variables)

        return PersonalizedContent(
            title=title,
            body=body,
            summary=summary,
            cta_text=cta_text,
            cta_url=cta_url,
            image_url=context.get("image_url"),
            metadata={
                "locale": locale,
                "tone": tone,
                "user_segment": user_data.get("segment"),
            },
            personalization_score=score,
            variables_used=all_vars,
        )

    async def _get_user_data(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict[str, Any]:
        """Obtém dados do usuário para personalização."""
        # TODO: Buscar do repositório real

        return {
            "nome": "João Silva",
            "primeiro_nome": "João",
            "email": "joao@example.com",
            "unidade": "Apt 101",
            "bloco": "A",
            "condominio": "Residencial Verde",
            "segment": "engaged",
            "tempo_morador": 24,  # meses
            "is_sindico": False,
            "preferencias": {
                "receber_marketing": True,
                "horario_preferido": "manhã",
            },
        }

    async def _get_behavior_data(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict[str, Any]:
        """Obtém dados comportamentais."""
        # TODO: Buscar do analytics real

        return {
            "ultima_atividade": datetime.utcnow(),
            "notificacoes_lidas_30d": 15,
            "notificacoes_enviadas_30d": 20,
            "taxa_abertura": 0.75,
            "categoria_mais_engajada": "system",
            "horario_mais_ativo": 14,
            "dias_ativos": [1, 2, 3, 4, 5],
        }

    def _build_variables(
        self,
        user_data: dict[str, Any],
        behavior_data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Constrói dicionário de variáveis."""
        now = datetime.utcnow()

        variables = {
            # Dados do usuário
            "user.nome": user_data.get("nome", "Morador"),
            "user.primeiro_nome": user_data.get("primeiro_nome", ""),
            "user.email": user_data.get("email", ""),
            "user.unidade": user_data.get("unidade", ""),
            "user.bloco": user_data.get("bloco", ""),
            "user.condominio": user_data.get("condominio", ""),
            # Comportamento
            "behavior.taxa_abertura": f"{behavior_data.get('taxa_abertura', 0) * 100:.0f}%",
            "behavior.notificacoes_lidas": behavior_data.get("notificacoes_lidas_30d", 0),
            # Contexto temporal
            "time.hora": now.hour,
            "time.periodo": self._get_period(now.hour),
            "time.dia_semana": self._get_weekday_name(now.weekday()),
            "time.data": now.strftime("%d/%m/%Y"),
            # Saudação dinâmica
            "greeting": self._get_greeting(now.hour),
        }

        # Adicionar contexto customizado
        for key, value in context.items():
            if not key.startswith("_"):
                variables[f"context.{key}"] = value

        # Flatten user_data
        for key, value in user_data.items():
            if isinstance(value, (str, int, float, bool)):
                variables[f"user.{key}"] = value

        return variables

    def _process_conditionals(
        self,
        text: str,
        variables: dict[str, Any],
    ) -> str:
        """Processa condicionais no template."""

        def replace_conditional(match):
            condition = match.group(1)
            true_content = match.group(2)
            false_content = match.group(3)

            # Avaliar condição
            value = variables.get(condition) or variables.get(f"user.{condition}")
            if value:
                return true_content.strip()
            return false_content.strip()

        return self.CONDITIONAL_PATTERN.sub(replace_conditional, text)

    def _replace_variables(
        self,
        text: str,
        variables: dict[str, Any],
    ) -> tuple[str, list[str]]:
        """Substitui variáveis no texto."""
        used_vars = []

        def replace_var(match):
            var_name = match.group(1)
            used_vars.append(var_name)

            # Buscar valor
            value = variables.get(var_name)
            if value is None:
                # Tentar com prefixo user.
                value = variables.get(f"user.{var_name}")
            if value is None:
                # Tentar com prefixo context.
                value = variables.get(f"context.{var_name}")

            return str(value) if value is not None else f"[{var_name}]"

        result = self.VAR_PATTERN.sub(replace_var, text)
        return result, used_vars

    def _apply_tone(self, text: str, tone: str) -> str:
        """Aplica ajustes de tom ao texto."""
        adjustments = self.TONE_ADJUSTMENTS.get(tone)
        if not adjustments:
            return text

        # Substituir saudação genérica
        text = re.sub(
            r"\[SAUDACAO\]",
            adjustments["greeting"],
            text,
            flags=re.IGNORECASE,
        )

        # Substituir fechamento
        text = re.sub(
            r"\[FECHAMENTO\]",
            adjustments["closing"],
            text,
            flags=re.IGNORECASE,
        )

        return text

    def _truncate(self, text: str, max_length: int) -> str:
        """Trunca texto mantendo palavras inteiras."""
        if len(text) <= max_length:
            return text

        truncated = text[:max_length - 3]
        # Encontrar última palavra completa
        last_space = truncated.rfind(" ")
        if last_space > max_length // 2:
            truncated = truncated[:last_space]

        return truncated + "..."

    def _generate_summary(self, body: str, max_length: int = 100) -> str:
        """Gera resumo do corpo."""
        # Remover HTML se houver
        clean = re.sub(r"<[^>]+>", "", body)
        # Pegar primeira sentença ou truncar
        first_sentence = re.split(r"[.!?]", clean)[0]
        return self._truncate(first_sentence.strip(), max_length)

    def _personalize_cta(
        self,
        context: dict[str, Any],
        user_data: dict[str, Any],
    ) -> tuple[Optional[str], Optional[str]]:
        """Personaliza call-to-action."""
        cta_text = context.get("cta_text")
        cta_url = context.get("cta_url")

        if cta_url:
            # Adicionar parâmetros de tracking
            separator = "&" if "?" in cta_url else "?"
            cta_url = f"{cta_url}{separator}utm_source=notification&utm_medium=push"

        return cta_text, cta_url

    def _calculate_personalization_score(
        self,
        used_vars: list[str],
        available_vars: dict[str, Any],
    ) -> float:
        """Calcula score de personalização."""
        if not used_vars:
            return 0.0

        # Variáveis de alto valor
        high_value = {"user.nome", "user.primeiro_nome", "user.unidade", "greeting"}
        medium_value = {"user.condominio", "time.periodo", "context."}

        score = 0.0
        for var in used_vars:
            if var in high_value:
                score += 0.3
            elif any(var.startswith(m) for m in medium_value):
                score += 0.2
            else:
                score += 0.1

        return min(score, 1.0)

    def _get_period(self, hour: int) -> str:
        """Retorna período do dia."""
        if 5 <= hour < 12:
            return "manhã"
        elif 12 <= hour < 18:
            return "tarde"
        elif 18 <= hour < 22:
            return "noite"
        return "madrugada"

    def _get_weekday_name(self, weekday: int) -> str:
        """Retorna nome do dia da semana."""
        days = [
            "segunda-feira",
            "terça-feira",
            "quarta-feira",
            "quinta-feira",
            "sexta-feira",
            "sábado",
            "domingo",
        ]
        return days[weekday]

    def _get_greeting(self, hour: int) -> str:
        """Retorna saudação baseada na hora."""
        if 5 <= hour < 12:
            return "Bom dia"
        elif 12 <= hour < 18:
            return "Boa tarde"
        return "Boa noite"

    async def create_variants(
        self,
        db: AsyncSession,
        template_title: str,
        template_body: str,
        user_id: int,
        num_variants: int = 2,
    ) -> list[ContentVariant]:
        """
        Cria variantes de conteúdo para A/B testing.

        Args:
            db: Sessão do banco
            template_title: Template do título
            template_body: Template do corpo
            user_id: ID do usuário
            num_variants: Número de variantes

        Returns:
            Lista de ContentVariant
        """
        variants = []
        tones = ["friendly", "formal", "casual"]

        for i in range(min(num_variants, len(tones))):
            content = await self.personalize(
                db=db,
                template_title=template_title,
                template_body=template_body,
                user_id=user_id,
                tone=tones[i],
            )

            variants.append(
                ContentVariant(
                    variant_id=f"variant_{i + 1}",
                    content=content,
                    target_segment=None,
                    weight=1.0 / num_variants,
                )
            )

        return variants

    async def localize(
        self,
        content: PersonalizedContent,
        target_locale: str,
    ) -> PersonalizedContent:
        """
        Localiza conteúdo para outro idioma.

        Args:
            content: Conteúdo original
            target_locale: Locale alvo

        Returns:
            PersonalizedContent localizado
        """
        # TODO: Integrar com serviço de tradução

        # Por enquanto, retorna o mesmo conteúdo
        return PersonalizedContent(
            title=content.title,
            body=content.body,
            summary=content.summary,
            cta_text=content.cta_text,
            cta_url=content.cta_url,
            image_url=content.image_url,
            metadata={**content.metadata, "locale": target_locale},
            personalization_score=content.personalization_score,
            variables_used=content.variables_used,
        )

    async def optimize_for_channel(
        self,
        content: PersonalizedContent,
        channel: str,
    ) -> PersonalizedContent:
        """
        Otimiza conteúdo para canal específico.

        Args:
            content: Conteúdo original
            channel: Canal de destino

        Returns:
            PersonalizedContent otimizado
        """
        limits = {
            "push": {"title": 50, "body": 200},
            "sms": {"title": 0, "body": 160},
            "email": {"title": 100, "body": 5000},
            "whatsapp": {"title": 0, "body": 1000},
            "in_app": {"title": 80, "body": 500},
        }

        channel_limits = limits.get(channel, {"title": 100, "body": 1000})

        optimized_title = content.title
        optimized_body = content.body

        if channel_limits["title"] > 0:
            optimized_title = self._truncate(content.title, channel_limits["title"])
        else:
            optimized_title = ""

        optimized_body = self._truncate(content.body, channel_limits["body"])

        return PersonalizedContent(
            title=optimized_title,
            body=optimized_body,
            summary=content.summary,
            cta_text=content.cta_text,
            cta_url=content.cta_url,
            image_url=content.image_url if channel not in ["sms"] else None,
            metadata={**content.metadata, "optimized_for": channel},
            personalization_score=content.personalization_score,
            variables_used=content.variables_used,
        )
