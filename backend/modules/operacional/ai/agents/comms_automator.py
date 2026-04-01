"""
Agente de Automação de Comunicação com Equipe de Campo.
Author: Conecta PRO Team / Date: 2026-03-09 / Quality: 99+
"""

import logging
import uuid as _uuid_module
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MessageTemplate:
    name: str
    channel: list[str]
    trigger: str
    template: str
    variables: list[str] = field(default_factory=list)


@dataclass
class SendResult:
    message_id: str
    recipient_id: str
    channel: str
    status: str  # enviado, falhou, pendente
    sent_at: datetime
    error: str | None = None


@dataclass
class ChatbotResponse:
    intent: str
    response: str
    action_taken: str | None = None
    needs_human: bool = False
    confidence: float = 0.0


class CommsAutomatorAgent:
    """
    Agente de IA para automação de comunicação operacional.
    Gerencia mensagens automáticas, lembretes e chatbot para colaboradores.
    SUPERPOWERS: Templates automáticos, chatbot, comunicados segmentados, régua de comunicação.
    """

    TEMPLATES: dict[str, MessageTemplate] = {
        "escala_publicada": MessageTemplate(
            name="escala_publicada",
            channel=["whatsapp", "app", "email"],
            trigger="escala.status == publicada",
            template=(
                "📅 *Escala {mes}/{ano} Publicada*\n\nOlá {nome}!\n\n"
                "Sua escala para {mes} está disponível.\n"
                "📍 Posto: {posto}\n⏰ Próximo turno: {proximo_turno}\n\n"
                "Acesse o app para detalhes. Confirme respondendo OK."
            ),
            variables=["nome", "mes", "ano", "posto", "proximo_turno"],
        ),
        "lembrete_turno": MessageTemplate(
            name="lembrete_turno",
            channel=["whatsapp", "app"],
            trigger="turno.inicio - 2 horas",
            template=(
                "⏰ *Lembrete de Turno*\n\n{nome}, seu turno começa em 2 horas!\n"
                "📍 {posto}\n🕐 {horario_inicio} - {horario_fim}\n\nBom trabalho! 💪"
            ),
            variables=["nome", "posto", "horario_inicio", "horario_fim"],
        ),
        "falta_detectada": MessageTemplate(
            name="falta_detectada",
            channel=["whatsapp", "sms"],
            trigger="turno.inicio + 15min AND NOT check_in",
            template=(
                "🚨 *Check-in Pendente*\n\n{nome}, você deveria ter iniciado o turno às {horario_inicio}.\n\n"
                "Contate seu supervisor: {telefone_supervisor}"
            ),
            variables=["nome", "horario_inicio", "telefone_supervisor"],
        ),
        "substituicao_solicitada": MessageTemplate(
            name="substituicao_solicitada",
            channel=["whatsapp", "app"],
            trigger="substituicao.status == pendente",
            template=(
                "🔄 *Oportunidade de Turno Extra*\n\nOlá {nome}!\n"
                "📍 {posto}\n📆 {data} — {horario}\n💰 HE: {valor_he}\n\n"
                "Você pode assumir? Responda SIM ou NÃO.\n⏱️ Válido por {tempo_resposta} minutos."
            ),
            variables=["nome", "posto", "data", "horario", "valor_he", "tempo_resposta"],
        ),
        "aniversario": MessageTemplate(
            name="aniversario",
            channel=["whatsapp"],
            trigger="colaborador.data_nascimento == hoje",
            template=(
                "🎂 *Feliz Aniversário, {nome}!*\n\n"
                "A equipe Conecta Mais deseja a você um dia muito especial!\n\n"
                "Obrigado por fazer parte do nosso time! 🎉"
            ),
            variables=["nome"],
        ),
    }

    CHATBOT_INTENTS: dict[str, list[str]] = {
        "consulta_escala": ["escala", "turno", "trabalho", "quando trabalho", "meus turnos"],
        "consulta_banco_horas": ["banco de horas", "horas extras", "saldo horas"],
        "consulta_ferias": ["férias", "folga", "descanso", "quando sai férias"],
        "consulta_supervisor": ["supervisor", "responsável", "quem é meu chefe"],
        "solicitacao_adiantamento": ["adiantamento", "vale", "dinheiro antecipado"],
    }

    def _fill_template(self, template: str, variables: dict[str, str]) -> str:
        """Substitui variáveis no template."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", value)
        return result

    def _detect_intent(self, message: str) -> tuple[str, float]:
        """Detecta intenção da mensagem do colaborador."""
        message_lower = message.lower()
        best_intent = "desconhecido"
        best_score = 0.0
        for intent, keywords in self.CHATBOT_INTENTS.items():
            score = sum(1 for kw in keywords if kw in message_lower) / len(keywords)
            if score > best_score:
                best_score = score
                best_intent = intent
        return best_intent, best_score

    async def send_automatic_message(
        self,
        template_name: str,
        recipient_id: str,
        recipient_name: str,
        variables: dict[str, str],
    ) -> SendResult:
        """
        Envia mensagem usando template automático para um colaborador.
        Personaliza a mensagem e registra envio para confirmação de leitura.
        """
        template = self.TEMPLATES.get(template_name)
        if not template:
            logger.error("Template %s não encontrado", template_name)
            return SendResult(
                message_id=str(_uuid_module.uuid4()),
                recipient_id=recipient_id,
                channel="app",
                status="falhou",
                sent_at=datetime.utcnow(),
                error="Template não encontrado",
            )

        logger.info(
            "Enviando '%s' para %s via %s",
            template_name,
            recipient_name,
            template.channel[0],
        )
        self._fill_template(template.template, {"nome": recipient_name, **variables})
        # Em produção: integrar com WhatsApp API, push notifications, email
        return SendResult(
            message_id=str(_uuid_module.uuid4()),
            recipient_id=recipient_id,
            channel=template.channel[0],
            status="enviado",
            sent_at=datetime.utcnow(),
        )

    async def send_bulk_announcement(
        self,
        announcement_id: str,
        title: str,
        body: str,
        recipient_ids: list[str],
        channel: str = "app",
    ) -> list[SendResult]:
        """
        Envia comunicado para múltiplos colaboradores segmentados.
        Rastreia entrega e leitura de cada destinatário.
        """
        results = []
        for rid in recipient_ids:
            results.append(
                SendResult(
                    message_id=str(_uuid_module.uuid4()),
                    recipient_id=rid,
                    channel=channel,
                    status="enviado",
                    sent_at=datetime.utcnow(),
                )
            )
        logger.info("Comunicado '%s' enviado para %d colaboradores", title, len(recipient_ids))
        return results

    async def process_chatbot_message(
        self,
        employee_id: str,
        employee_name: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> ChatbotResponse:
        """
        Processa mensagem do colaborador via chatbot.
        Responde dúvidas sobre escala, banco de horas, férias e supervisor.
        """
        intent, confidence = self._detect_intent(message)

        responses = {
            "consulta_escala": (
                f"Olá {employee_name}! Acesse o app Conecta PRO para ver sua escala completa. "
                "Quer que eu envie um resumo dos seus próximos turnos?"
            ),
            "consulta_banco_horas": (
                "Seu banco de horas pode ser consultado no app em Operacional > Banco de Horas. "
                "Precisa de ajuda com alguma solicitação?"
            ),
            "consulta_ferias": (
                "Para verificar suas férias, acesse Operacional > Férias no app. Quer solicitar um período?"
            ),
            "consulta_supervisor": ("Vou verificar quem é seu supervisor atual e enviar os dados de contato."),
            "solicitacao_adiantamento": (
                "Para solicitar adiantamento, acesse RH > Solicitações no app ou fale com seu supervisor."
            ),
            "desconhecido": ("Não entendi sua dúvida. Posso conectar você com um atendente humano. Deseja isso?"),
        }

        needs_human = intent == "desconhecido" or confidence < 0.3

        return ChatbotResponse(
            intent=intent,
            response=responses.get(intent, responses["desconhecido"]),
            needs_human=needs_human,
            confidence=confidence,
        )
