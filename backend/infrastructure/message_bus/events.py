"""
Module: infrastructure/message_bus/events.py
Description: Sistema de eventos para o message bus
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Este modulo implementa:
- Eventos de dominio (DomainEvent)
- Eventos de integracao (IntegrationEvent)
- Funcoes helper para pub/sub
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from .bus import (
    Handler,
    HandlerFunc,
    Message,
    MessagePriority,
    MessageType,
    get_message_bus,
)

logger = logging.getLogger(__name__)


class EventType(StrEnum):
    """Tipos de eventos do sistema.

    Organizado por fase/dominio para facilitar routing.
    """

    # Fase 1 - Core Business
    PROPOSTA_CRIADA = "fase1.proposta.criada"
    PROPOSTA_APROVADA = "fase1.proposta.aprovada"
    PROPOSTA_REJEITADA = "fase1.proposta.rejeitada"
    CONTRATO_CRIADO = "fase1.contrato.criado"
    CONTRATO_ASSINADO = "fase1.contrato.assinado"
    CLIENTE_CADASTRADO = "fase1.cliente.cadastrado"

    # Fase 2 - Gestao Empresarial
    FUNCIONARIO_ADMITIDO = "fase2.funcionario.admitido"
    FUNCIONARIO_DEMITIDO = "fase2.funcionario.demitido"
    FOLHA_PROCESSADA = "fase2.folha.processada"
    PONTO_REGISTRADO = "fase2.ponto.registrado"
    LANCAMENTO_CONTABIL = "fase2.contabilidade.lancamento"

    # Fase 3 - Security/Health/Gov
    CONSENTIMENTO_REGISTRADO = "fase3.lgpd.consentimento"
    CONSENTIMENTO_REVOGADO = "fase3.lgpd.revogacao"
    DADOS_EXCLUIDOS = "fase3.lgpd.exclusao"
    EXAME_AGENDADO = "fase3.saude.exame_agendado"
    ASO_EMITIDO = "fase3.saude.aso_emitido"
    EPI_ENTREGUE = "fase3.saude.epi_entregue"
    ESOCIAL_TRANSMITIDO = "fase3.gov.esocial"
    NFE_EMITIDA = "fase3.gov.nfe"

    # Fase 4 - Licitacoes
    LICITACAO_IDENTIFICADA = "fase4.licitacao.identificada"
    PROPOSTA_ENVIADA = "fase4.licitacao.proposta_enviada"
    RESULTADO_LICITACAO = "fase4.licitacao.resultado"

    # Fase 5 - Grand Finale
    EMAIL_ANALISADO = "fase5.email.analisado"
    CCT_VALIDADO = "fase5.cct.validado"
    PROPOSTA_GERADA = "fase5.cct.proposta"

    # Sistema
    SISTEMA_INICIADO = "sistema.iniciado"
    SISTEMA_ENCERRADO = "sistema.encerrado"
    ERRO_CRITICO = "sistema.erro_critico"
    AUDIT_LOG = "sistema.audit"


@dataclass
class Event:
    """Classe base para eventos do sistema.

    Attributes:
        id: Identificador unico do evento.
        type: Tipo do evento.
        source: Fonte/origem do evento.
        data: Dados do evento.
        timestamp: Momento da criacao.
        version: Versao do schema do evento.
        correlation_id: ID para correlacao com outros eventos.
        causation_id: ID do evento que causou este.
        metadata: Metadados adicionais.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    type: EventType = EventType.SISTEMA_INICIADO
    source: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"
    correlation_id: str | None = None
    causation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_message(
        self,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> Message:
        """Converte o evento para uma mensagem do bus.

        Args:
            priority: Prioridade da mensagem.

        Returns:
            Message configurada com dados do evento.
        """
        return Message(
            id=self.id,
            type=MessageType.EVENT,
            topic=self.type.value,
            payload={
                "source": self.source,
                "data": self.data,
                "version": self.version,
            },
            priority=priority,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte evento para dicionario.

        Returns:
            Dict com dados do evento.
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "metadata": self.metadata,
        }


@dataclass
class DomainEvent(Event):
    """Evento de dominio.

    Eventos de dominio representam algo que aconteceu dentro
    de um bounded context especifico.

    Attributes:
        aggregate_id: ID do agregado relacionado.
        aggregate_type: Tipo do agregado.
        domain: Nome do dominio (procurement, financial, hr, inventory).
    """

    aggregate_id: str | None = None
    aggregate_type: str | None = None
    domain: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario incluindo campos de dominio.

        Returns:
            Dict com dados completos.
        """
        base = super().to_dict()
        base.update(
            {
                "aggregate_id": self.aggregate_id,
                "aggregate_type": self.aggregate_type,
                "domain": self.domain,
            }
        )
        return base


@dataclass
class IntegrationEvent(Event):
    """Evento de integracao.

    Eventos de integracao sao usados para comunicacao
    entre bounded contexts/microservicos.

    Attributes:
        source_service: Servico de origem.
        target_services: Servicos de destino (lista).
        requires_acknowledgment: Se requer confirmacao.
        ttl_seconds: Time to live em segundos.
    """

    source_service: str = ""
    target_services: list[str] = field(default_factory=list)
    requires_acknowledgment: bool = False
    ttl_seconds: int = 3600

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario incluindo campos de integracao.

        Returns:
            Dict com dados completos.
        """
        base = super().to_dict()
        base.update(
            {
                "source_service": self.source_service,
                "target_services": self.target_services,
                "requires_acknowledgment": self.requires_acknowledgment,
                "ttl_seconds": self.ttl_seconds,
            }
        )
        return base


async def publish_event(
    event: Event,
    priority: MessagePriority = MessagePriority.NORMAL,
    wait_for_processing: bool = False,
) -> str:
    """Publica um evento no message bus.

    Args:
        event: Evento a publicar.
        priority: Prioridade do evento.
        wait_for_processing: Aguardar processamento.

    Returns:
        ID do evento publicado.

    Example:
        >>> event = Event(
        ...     type=EventType.PROPOSTA_CRIADA,
        ...     source="crm_service",
        ...     data={"proposta_id": "123", "valor": 50000.00}
        ... )
        >>> event_id = await publish_event(event)
    """
    bus = get_message_bus()
    message = event.to_message(priority)

    logger.info(
        "Publicando evento: type=%s, source=%s",
        event.type.value,
        event.source,
    )

    return await bus.publish(message, wait_for_processing)


def subscribe_to_event(
    event_type: EventType,
    handler: HandlerFunc,
    filter_func: Callable[[Message], bool] | None = None,
) -> str:
    """Registra um subscriber para um tipo de evento.

    Args:
        event_type: Tipo de evento de interesse.
        handler: Funcao para processar eventos.
        filter_func: Funcao opcional para filtrar eventos.

    Returns:
        ID do subscriber registrado.

    Example:
        >>> async def on_proposta_criada(msg: Message):
        ...     proposta_id = msg.payload["data"]["proposta_id"]
        ...     print(f"Nova proposta: {proposta_id}")
        >>>
        >>> sub_id = subscribe_to_event(
        ...     EventType.PROPOSTA_CRIADA,
        ...     on_proposta_criada
        ... )
    """
    bus = get_message_bus()

    logger.info("Registrando subscriber para evento: %s", event_type.value)

    return bus.subscribe(
        topic=event_type.value,
        handler=handler,
        filter_func=filter_func,
    )


def subscribe_to_pattern(
    pattern: str,
    handler: HandlerFunc,
    filter_func: Callable[[Message], bool] | None = None,
) -> str:
    """Registra um subscriber para um padrao de eventos.

    Suporta wildcards:
    - 'fase1.*' para todos eventos da fase 1
    - '*.criado' para todos eventos de criacao
    - 'fase3.lgpd.*' para todos eventos LGPD

    Args:
        pattern: Padrao de topico (com wildcards).
        handler: Funcao para processar eventos.
        filter_func: Funcao opcional para filtrar eventos.

    Returns:
        ID do subscriber registrado.

    Example:
        >>> async def on_fase1_events(msg: Message):
        ...     print(f"Evento Fase 1: {msg.topic}")
        >>>
        >>> sub_id = subscribe_to_pattern("fase1.*", on_fase1_events)
    """
    bus = get_message_bus()

    logger.info("Registrando subscriber para padrao: %s", pattern)

    return bus.subscribe(
        topic=pattern,
        handler=handler,
        filter_func=filter_func,
    )


class EventHandler(Handler):
    """Handler base para eventos.

    Fornece funcionalidade comum para handlers de eventos.
    """

    def __init__(self, event_type: EventType) -> None:
        """Inicializa o handler.

        Args:
            event_type: Tipo de evento que este handler processa.
        """
        self.event_type = event_type

    async def handle(self, message: Message) -> Any | None:
        """Processa uma mensagem de evento.

        Args:
            message: Mensagem do bus.

        Returns:
            Resultado do processamento.
        """
        try:
            event_data = message.payload.get("data", {})
            source = message.payload.get("source", "")

            logger.debug(
                "Processando evento: type=%s, source=%s",
                message.topic,
                source,
            )

            return await self.on_event(event_data, source, message)

        except Exception as e:
            logger.error(
                "Erro ao processar evento %s: %s",
                message.topic,
                str(e),
            )
            raise

    async def on_event(
        self,
        data: dict[str, Any],
        source: str,
        message: Message,
    ) -> Any | None:
        """Metodo a ser sobrescrito pelas subclasses.

        Args:
            data: Dados do evento.
            source: Fonte do evento.
            message: Mensagem original.

        Returns:
            Resultado do processamento.
        """
        raise NotImplementedError("Subclasses devem implementar on_event")
