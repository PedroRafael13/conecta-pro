"""
Operacional — Event publishers.

Funções utilitárias para publicar eventos de domínio no ConectaEventBus.
Todas as funções são não-bloqueantes: falhas são registradas em log sem
propagar exceções para o caller.
"""

import logging

from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

logger = logging.getLogger(__name__)


async def publish_ocorrencia_registrada(
    ocorrencia_id: str,
    tipo: str,
    descricao: str,
    employee_id: str | None,
    cliente_id: str,
    data: str,
    tem_bo: bool = False,
) -> None:
    """Publica evento quando uma ocorrência é registrada."""
    try:
        evento = ConectaEvent(
            event_type=EventTypes.OPS_OCORRENCIA_REGISTRADA,
            payload={
                "ocorrencia_id": ocorrencia_id,
                "tipo": tipo,
                "descricao": descricao,
                "employee_id": employee_id,
                "cliente_id": cliente_id,
                "data": data,
                "tem_bo": tem_bo,
            },
            source_module="operacional",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish ocorrencia_registrada: %s", e)


async def publish_escala_publicada(
    escala_id: str,
    cliente_id: str,
    competencia: str,
    total_turnos: int,
    funcionarios: list,
) -> None:
    """Publica evento quando uma escala é publicada."""
    try:
        evento = ConectaEvent(
            event_type=EventTypes.OPS_ESCALA_PUBLICADA,
            payload={
                "escala_id": escala_id,
                "cliente_id": cliente_id,
                "competencia": competencia,
                "total_turnos": total_turnos,
                "funcionarios": funcionarios,
            },
            source_module="operacional",
            cliente_id=cliente_id,
            competencia=competencia,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish escala_publicada: %s", e)


async def publish_cat_registrada(
    cat_id: str,
    employee_id: str,
    funcionario_nome: str,
    cliente_id: str,
    data: str,
    numero_cat: str,
    afastamento: bool,
) -> None:
    """Publica evento quando uma CAT é registrada."""
    try:
        evento = ConectaEvent(
            event_type=EventTypes.OPS_CAT_REGISTRADA,
            payload={
                "cat_id": cat_id,
                "employee_id": employee_id,
                "funcionario_nome": funcionario_nome,
                "cliente_id": cliente_id,
                "data": data,
                "numero_cat": numero_cat,
                "afastamento": afastamento,
            },
            source_module="operacional",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish cat_registrada: %s", e)


async def publish_banco_horas_criado(
    entry_id: str,
    employee_id: str,
    hours: float,
    entry_type: str,
    cliente_id: str = "",
) -> None:
    """Publica evento quando uma entrada no banco de horas é criada."""
    try:
        evento = ConectaEvent(
            event_type=EventTypes.OPS_BANCO_HORAS_CRIADO,
            payload={
                "entry_id": entry_id,
                "employee_id": employee_id,
                "hours": hours,
                "entry_type": entry_type,
            },
            source_module="operacional",
            funcionario_id=employee_id,
            cliente_id=cliente_id or None,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish banco_horas_criado: %s", e)


async def publish_medida_disciplinar_criada(
    action_id: str,
    employee_id: str,
    action_type: str,
    cliente_id: str = "",
) -> None:
    """Publica evento quando uma medida disciplinar é criada."""
    try:
        evento = ConectaEvent(
            event_type=EventTypes.OPS_MEDIDA_DISCIPLINAR_CRIADA,
            payload={
                "action_id": action_id,
                "employee_id": employee_id,
                "action_type": action_type,
            },
            source_module="operacional",
            funcionario_id=employee_id,
            cliente_id=cliente_id or None,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish medida_disciplinar_criada: %s", e)


async def publish_ronda_concluida(
    ronda_id: str,
    inspector_id: str,
    cliente_id: str,
    total_checkpoints: int = 0,
    tem_ocorrencias: bool = False,
    data: str | None = None,
) -> None:
    """Publica evento quando uma ronda de inspeção é concluída."""
    try:
        evento = ConectaEvent(
            event_type=EventTypes.OPS_OCORRENCIA_REGISTRADA,
            payload={
                "ronda_id": ronda_id,
                "inspector_id": inspector_id,
                "cliente_id": cliente_id,
                "total_checkpoints": total_checkpoints,
                "tem_ocorrencias": tem_ocorrencias,
                "data": data,
                "origem": "ronda_inspecao",
            },
            source_module="operacional",
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish ronda_concluida: %s", e)


async def publish_alocacao_criada(
    allocation_id: str,
    employee_id: str,
    post_id: str,
    cliente_id: str = "",
) -> None:
    """Publica evento quando uma alocação funcionário-posto é criada."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_ALOCACAO_CRIADA,
                payload={"allocation_id": allocation_id, "employee_id": employee_id, "post_id": post_id},
                source_module="operacional",
                funcionario_id=employee_id,
                cliente_id=cliente_id or None,
            )
        )
    except Exception as e:
        logger.warning("Falha publish alocacao_criada: %s", e)


async def publish_turno_iniciado(shift_id: str, employee_id: str = "", post_id: str = "") -> None:
    """Publica evento quando check-in de turno é registrado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_TURNO_INICIADO,
                payload={"shift_id": shift_id, "employee_id": employee_id, "post_id": post_id},
                source_module="operacional",
                funcionario_id=employee_id or None,
            )
        )
    except Exception as e:
        logger.warning("Falha publish turno_iniciado: %s", e)


async def publish_turno_encerrado(shift_id: str, employee_id: str = "", post_id: str = "") -> None:
    """Publica evento quando check-out de turno é registrado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_TURNO_ENCERRADO,
                payload={"shift_id": shift_id, "employee_id": employee_id, "post_id": post_id},
                source_module="operacional",
                funcionario_id=employee_id or None,
            )
        )
    except Exception as e:
        logger.warning("Falha publish turno_encerrado: %s", e)


async def publish_ferias_aprovadas_op(
    request_id: str,
    employee_id: str,
    employee_name: str = "",
) -> None:
    """Publica evento quando solicitação de férias operacional é aprovada."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_FERIAS_APROVADAS_OP,
                payload={"request_id": request_id, "employee_id": employee_id, "employee_name": employee_name},
                source_module="operacional",
                funcionario_id=employee_id,
            )
        )
    except Exception as e:
        logger.warning("Falha publish ferias_aprovadas_op: %s", e)


async def publish_diarista_criada(diarist_id: str, nome: str = "") -> None:
    """Publica evento quando uma diarista é cadastrada."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_DIARISTA_CRIADA,
                payload={"diarist_id": diarist_id, "nome": nome},
                source_module="operacional",
            )
        )
    except Exception as e:
        logger.warning("Falha publish diarista_criada: %s", e)


async def publish_diarista_checkin(schedule_id: str, diarist_id: str = "") -> None:
    """Publica evento quando check-in de diarista é registrado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_DIARISTA_CHECKIN,
                payload={"schedule_id": schedule_id, "diarist_id": diarist_id},
                source_module="operacional",
            )
        )
    except Exception as e:
        logger.warning("Falha publish diarista_checkin: %s", e)


async def publish_diarista_checkout(schedule_id: str, diarist_id: str = "") -> None:
    """Publica evento quando check-out de diarista é registrado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_DIARISTA_CHECKOUT,
                payload={"schedule_id": schedule_id, "diarist_id": diarist_id},
                source_module="operacional",
            )
        )
    except Exception as e:
        logger.warning("Falha publish diarista_checkout: %s", e)


async def publish_diarista_pagamento(payment_id: str, diarist_id: str = "", valor: float = 0.0) -> None:
    """Publica evento quando pagamento de diarista é processado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_DIARISTA_PAGAMENTO,
                payload={"payment_id": payment_id, "diarist_id": diarist_id, "valor": valor},
                source_module="operacional",
            )
        )
    except Exception as e:
        logger.warning("Falha publish diarista_pagamento: %s", e)


async def publish_comunicado_publicado(announcement_id: str, titulo: str = "", tenant_id: str = "") -> None:
    """Publica evento quando um comunicado é publicado/enviado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.OPS_COMUNICADO_PUBLICADO,
                payload={"announcement_id": announcement_id, "titulo": titulo, "tenant_id": tenant_id},
                source_module="operacional",
            )
        )
    except Exception as e:
        logger.warning("Falha publish comunicado_publicado: %s", e)


async def publish_substituicao_realizada(
    employee_original_id: str,
    substituto_id: str,
    substituto_nome: str,
    cliente_id: str,
    data: str,
    turno: str,
) -> None:
    """Publica evento quando uma substituição é confirmada."""
    try:
        evento = ConectaEvent(
            event_type=EventTypes.OPS_SUBSTITUICAO_REALIZADA,
            payload={
                "employee_original_id": employee_original_id,
                "substituto_id": substituto_id,
                "substituto_nome": substituto_nome,
                "cliente_id": cliente_id,
                "data": data,
                "turno": turno,
            },
            source_module="operacional",
            funcionario_id=substituto_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish substituicao_realizada: %s", e)
