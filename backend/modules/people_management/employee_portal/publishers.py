"""
Publishers Portal do Funcionário — Conecta PRO
Publica eventos quando funcionários fazem solicitações ou ações no portal.
"""

import logging

from infrastructure.event_bus import ConectaEvent, event_bus

logger = logging.getLogger(__name__)


async def publish_ferias_solicitadas(
    employee_id: str,
    funcionario_nome: str,
    data_inicio: str,
    data_fim: str,
    dias: int,
) -> None:
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type="portal.ferias.solicitadas",
                payload={
                    "funcionario_nome": funcionario_nome,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "dias": dias,
                },
                source_module="portal",
                funcionario_id=employee_id,
            )
        )
        logger.info("PORTAL: férias solicitadas publicadas — %s", funcionario_nome)
    except Exception as e:
        logger.warning("Falha publish férias portal: %s", e)


async def publish_documento_solicitado(
    employee_id: str,
    funcionario_nome: str,
    tipo_documento: str,
) -> None:
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type="portal.documento.solicitado",
                payload={
                    "funcionario_nome": funcionario_nome,
                    "tipo_documento": tipo_documento,
                },
                source_module="portal",
                funcionario_id=employee_id,
            )
        )
        logger.info(
            "PORTAL: documento solicitado publicado — %s (%s)",
            tipo_documento,
            funcionario_nome,
        )
    except Exception as e:
        logger.warning("Falha publish doc solicitado: %s", e)


async def publish_documento_assinado(
    employee_id: str,
    funcionario_nome: str,
    document_id: int,
    document_type: str,
) -> None:
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type="portal.documento.assinado",
                payload={
                    "funcionario_nome": funcionario_nome,
                    "document_id": document_id,
                    "document_type": document_type,
                },
                source_module="portal",
                funcionario_id=employee_id,
            )
        )
        logger.info(
            "PORTAL: documento assinado publicado — doc_id=%s tipo=%s",
            document_id,
            document_type,
        )
    except Exception as e:
        logger.warning("Falha publish doc assinado: %s", e)
