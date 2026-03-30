"""
Integração com eventos de RH — health_occupational.
=======================================================

Consome eventos do barramento para disparar automaticamente:
- FUNCIONARIO_ADMITIDO  → agenda exame admissional
- FUNCIONARIO_DEMITIDO  → agenda exame demissional
- FUNCIONARIO_MUDANCA_FUNCAO → agenda exame de mudança de função
- FUNCIONARIO_RETORNO_TRABALHO → agenda exame de retorno ao trabalho

Os handlers são registrados na inicialização do módulo.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# IDs de referência para quando não há usuario logado
SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"


def _get_db_session():
    """Obtém sessão síncrona do banco."""
    from core.database import get_sync_session

    return get_sync_session()


def _schedule_exam_sync(
    funcionario_id: str,
    tipo_exame: str,
    funcao: str,
    setor: str,
    dias_para_agendamento: int = 3,
) -> dict[str, Any]:
    """
    Agenda exame médico via PCMSOService usando sessão síncrona.
    Retorna dict com resultado do agendamento.
    """
    from modules.health_occupational.schemas.pcmso import MedicalExamRequest
    from modules.health_occupational.services.pcmso_service import PCMSOService

    data_agendamento = date.today() + timedelta(days=dias_para_agendamento)

    try:
        with _get_db_session() as db:
            service = PCMSOService(db=db)
            request = MedicalExamRequest(
                funcionario_id=funcionario_id,
                tipo_exame=tipo_exame,
                data_agendamento=data_agendamento,
                funcao=funcao or "Não informado",
                setor=setor or "Não informado",
                riscos=[],
                exames_complementares=[],
                observacoes=f"Agendamento automático — evento: {tipo_exame}",
            )
            exam = service.schedule_exam(request)
            logger.info(
                "Exame %s agendado automaticamente para funcionário %s (exam_id=%s)",
                tipo_exame,
                funcionario_id,
                exam.id,
            )
            return {"success": True, "exam_id": str(exam.id), "tipo": tipo_exame}
    except Exception as exc:
        logger.error(
            "Erro ao agendar exame %s para funcionário %s: %s",
            tipo_exame,
            funcionario_id,
            exc,
        )
        return {"success": False, "error": str(exc)}


async def handle_funcionario_admitido(message: Any) -> None:
    """
    Handler: FUNCIONARIO_ADMITIDO → agenda exame admissional automaticamente.
    """
    try:
        payload = message.payload if hasattr(message, "payload") else message
        data = payload.get("data", payload) if isinstance(payload, dict) else {}

        funcionario_id = data.get("funcionario_id") or data.get("employee_id") or data.get("id")
        funcao = data.get("funcao") or data.get("cargo") or data.get("role") or ""
        setor = data.get("setor") or data.get("department") or data.get("sector") or ""

        if not funcionario_id:
            logger.warning("FUNCIONARIO_ADMITIDO sem funcionario_id, ignorando")
            return

        logger.info("Processando admissão: funcionario_id=%s", funcionario_id)
        result = _schedule_exam_sync(
            funcionario_id=str(funcionario_id),
            tipo_exame="admissional",
            funcao=funcao,
            setor=setor,
            dias_para_agendamento=1,  # Admissional deve ser agendado para amanhã
        )
        logger.info("Resultado agendamento admissional: %s", result)

    except Exception as exc:
        logger.error("Erro no handler FUNCIONARIO_ADMITIDO: %s", exc)


async def handle_funcionario_demitido(message: Any) -> None:
    """
    Handler: FUNCIONARIO_DEMITIDO → agenda exame demissional automaticamente.
    """
    try:
        payload = message.payload if hasattr(message, "payload") else message
        data = payload.get("data", payload) if isinstance(payload, dict) else {}

        funcionario_id = data.get("funcionario_id") or data.get("employee_id") or data.get("id")
        funcao = data.get("funcao") or data.get("cargo") or ""
        setor = data.get("setor") or data.get("department") or ""

        if not funcionario_id:
            logger.warning("FUNCIONARIO_DEMITIDO sem funcionario_id, ignorando")
            return

        logger.info("Processando demissão: funcionario_id=%s", funcionario_id)
        result = _schedule_exam_sync(
            funcionario_id=str(funcionario_id),
            tipo_exame="demissional",
            funcao=funcao,
            setor=setor,
            dias_para_agendamento=5,  # Demissional geralmente dentro de 5 dias
        )
        logger.info("Resultado agendamento demissional: %s", result)

    except Exception as exc:
        logger.error("Erro no handler FUNCIONARIO_DEMITIDO: %s", exc)


async def handle_funcionario_mudanca_funcao(message: Any) -> None:
    """
    Handler: FUNCIONARIO_TRANSFERIDO/PROMOVIDO → agenda exame de mudança de função.
    """
    try:
        payload = message.payload if hasattr(message, "payload") else message
        data = payload.get("data", payload) if isinstance(payload, dict) else {}

        funcionario_id = data.get("funcionario_id") or data.get("employee_id") or data.get("id")
        funcao_nova = (
            data.get("funcao_nova") or data.get("nova_funcao") or data.get("funcao") or data.get("cargo") or ""
        )
        setor_novo = (
            data.get("setor_novo") or data.get("novo_setor") or data.get("setor") or data.get("department") or ""
        )

        if not funcionario_id:
            logger.warning("Evento mudança de função sem funcionario_id, ignorando")
            return

        logger.info("Processando mudança de função: funcionario_id=%s, nova_funcao=%s", funcionario_id, funcao_nova)
        result = _schedule_exam_sync(
            funcionario_id=str(funcionario_id),
            tipo_exame="mudanca_funcao",
            funcao=funcao_nova,
            setor=setor_novo,
            dias_para_agendamento=7,
        )
        logger.info("Resultado agendamento mudança de função: %s", result)

    except Exception as exc:
        logger.error("Erro no handler mudança de função: %s", exc)


def register_hr_event_subscribers() -> None:
    """
    Registra os subscribers de eventos de RH no message bus.
    Deve ser chamado na inicialização do módulo (startup).
    """
    try:
        from infrastructure.message_bus.events import EventType, subscribe_to_event

        subscribe_to_event(EventType.FUNCIONARIO_ADMITIDO, handle_funcionario_admitido)
        subscribe_to_event(EventType.FUNCIONARIO_DEMITIDO, handle_funcionario_demitido)
        subscribe_to_event(EventType.FUNCIONARIO_MUDANCA_FUNCAO, handle_funcionario_mudanca_funcao)

        # Padrão genérico como fallback para outros subtipos de fase2.funcionario.*
        from infrastructure.message_bus.events import subscribe_to_pattern

        subscribe_to_pattern("fase2.funcionario.*", _handle_fase2_funcionario_generic)

        logger.info(
            "✅ Health Occupational: subscribers de eventos RH registrados "
            "(FUNCIONARIO_ADMITIDO, FUNCIONARIO_DEMITIDO, FUNCIONARIO_MUDANCA_FUNCAO, fase2.funcionario.*)"
        )
    except Exception as exc:
        logger.warning("Health Occupational: não foi possível registrar subscribers de eventos RH: %s", exc)


async def _handle_fase2_funcionario_generic(message: Any) -> None:
    """
    Handler genérico para eventos fase2.funcionario.* não mapeados diretamente.
    Captura mudança de função, promoções, transferências.
    """
    try:
        topic = getattr(message, "topic", "") or ""
        payload = message.payload if hasattr(message, "payload") else {}
        data = payload.get("data", {}) if isinstance(payload, dict) else {}

        # Já tratados individualmente por subscribers diretos
        if topic in (
            "fase2.funcionario.admitido",
            "fase2.funcionario.demitido",
            "fase2.funcionario.mudanca_funcao",
        ):
            return

        # Verificar se é mudança de função
        tipo_evento = data.get("tipo_evento") or data.get("event_type") or topic.split(".")[-1]
        if any(kw in tipo_evento.lower() for kw in ["transfer", "promov", "funcao", "cargo"]):
            await handle_funcionario_mudanca_funcao(message)

    except Exception as exc:
        logger.debug("Handler genérico fase2: %s", exc)
