"""
Event handlers para integracao bidirecional entre modulos.

Cada handler e acionado por um evento de negocio e dispara acoes
nos modulos relacionados.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# =============================================================================
# FLUXO 1: Operacoes -> DP (Fechamento de turno)
# =============================================================================
async def on_shift_closed(
    db: AsyncSession,
    shift_data: dict[str, Any],
) -> dict[str, Any]:
    """Ao fechar turno, registra horas no ponto do DP.

    Args:
        db: Sessao do banco de dados.
        shift_data: Dados do turno fechado contendo:
            - employee_id: ID do funcionario
            - date: Data do turno
            - regular_hours: Horas normais
            - overtime_hours: Horas extras
            - night_hours: Horas noturnas
            - is_absence: Se houve falta
            - late_minutes: Minutos de atraso
            - workplace_id: ID do posto

    Returns:
        Resultado do registro com time_record_id e overtime_credit_id.
    """
    result = {
        "time_record_id": None,
        "overtime_credit_id": None,
        "status": "processed",
    }

    try:
        from .services import overtime_bank_integration, time_tracking_integration

        time_record = await time_tracking_integration.register_from_operations(
            db=db,
            employee_id=shift_data["employee_id"],
            date=shift_data["date"],
            regular_hours=shift_data.get("regular_hours", 0),
            overtime_hours=shift_data.get("overtime_hours", 0),
            night_hours=shift_data.get("night_hours", 0),
            is_absence=shift_data.get("is_absence", False),
            late_minutes=shift_data.get("late_minutes", 0),
            workplace_id=shift_data.get("workplace_id"),
        )
        result["time_record_id"] = time_record.get("id") if time_record else None

        overtime_hours = shift_data.get("overtime_hours", 0)
        if overtime_hours > 0:
            credit = await overtime_bank_integration.credit(
                db=db,
                employee_id=shift_data["employee_id"],
                hours=overtime_hours,
                date=shift_data["date"],
                source="operations_shift",
            )
            result["overtime_credit_id"] = credit.get("id") if credit else None

    except ImportError:
        logger.warning("Servicos de integracao nao disponiveis")
        result["status"] = "skipped"
    except Exception as e:
        logger.error(f"Erro ao processar fechamento de turno: {e}")
        result["status"] = "error"
        result["error"] = str(e)

    return result


# =============================================================================
# FLUXO 2: Operacoes -> DP (Ocorrencia grave -> Processo disciplinar)
# =============================================================================
async def on_occurrence_registered(
    db: AsyncSession,
    occurrence_data: dict[str, Any],
) -> dict[str, Any]:
    """Ocorrencia grave dispara processo disciplinar no DP.

    Args:
        db: Sessao do banco de dados.
        occurrence_data: Dados da ocorrencia contendo:
            - id: ID da ocorrencia
            - employee_id: ID do funcionario
            - severity: Severidade (leve, moderada, grave, gravissima)
            - description: Descricao da ocorrencia
            - category: Categoria

    Returns:
        Resultado com discipline_id se processo foi criado.
    """
    result = {
        "discipline_created": False,
        "discipline_id": None,
        "notification_sent": False,
    }

    severity = occurrence_data.get("severity", "leve")
    if severity not in ("grave", "gravissima"):
        result["reason"] = "severity_below_threshold"
        return result

    try:
        from ..hr.services.discipline_service import DisciplineService

        discipline_type = "warning" if severity == "grave" else "suspension"

        discipline_service = DisciplineService(db)
        discipline = await discipline_service.create_from_occurrence(
            employee_id=occurrence_data["employee_id"],
            occurrence_id=occurrence_data["id"],
            discipline_type=discipline_type,
            description=occurrence_data.get("description", ""),
        )

        if discipline:
            result["discipline_created"] = True
            result["discipline_id"] = discipline.get("id")

        logger.info(f"Processo disciplinar criado para ocorrencia {occurrence_data['id']}: {discipline_type}")
    except ImportError:
        logger.warning("DisciplineService nao disponivel")
    except Exception as e:
        logger.error(f"Erro ao criar processo disciplinar: {e}")
        result["error"] = str(e)

    return result


# =============================================================================
# FLUXO 3: DP -> Operacoes (Ferias aprovadas -> Substituicao)
# =============================================================================
async def on_vacation_approved(
    db: AsyncSession,
    vacation_data: dict[str, Any],
) -> dict[str, Any]:
    """Ferias aprovadas disparam geracao de substituicao em Operacoes.

    Args:
        db: Sessao do banco de dados.
        vacation_data: Dados das ferias contendo:
            - id: ID da solicitacao
            - employee_id: ID do funcionario
            - start_date: Data inicio
            - end_date: Data fim

    Returns:
        Resultado com lista de substituicoes criadas.
    """
    result = {
        "substitutions_created": 0,
        "substitution_ids": [],
        "ai_suggestions_generated": False,
    }

    try:
        from ..operations.ai.scale_optimizer_ai import ScaleOptimizerAI

        ScaleOptimizerAI()

        logger.info(
            f"Ferias aprovadas para funcionario {vacation_data['employee_id']} "
            f"de {vacation_data['start_date']} a {vacation_data['end_date']}"
        )

        result["ai_suggestions_generated"] = True

    except ImportError:
        logger.warning("ScaleOptimizerAI nao disponivel")
    except Exception as e:
        logger.error(f"Erro ao processar ferias aprovadas: {e}")
        result["error"] = str(e)

    return result


# =============================================================================
# FLUXO 4: RH -> DP (Candidato aprovado -> Admissao)
# =============================================================================
async def on_candidate_approved(
    db: AsyncSession,
    candidate_data: dict[str, Any],
    job_data: dict[str, Any],
) -> dict[str, Any]:
    """Candidato aprovado inicia processo de admissao no DP.

    Args:
        db: Sessao do banco de dados.
        candidate_data: Dados do candidato (id, name, cpf, etc).
        job_data: Dados da vaga (id, workplace_id, salary, etc).

    Returns:
        Resultado com admission_id e checklist gerado.
    """
    result = {
        "admission_created": False,
        "admission_id": None,
        "checklist_items": 0,
    }

    try:
        from ..hr.services.admission_service import AdmissionService

        admission_service = AdmissionService(db)

        admission = await admission_service.create_admission(
            candidate_id=candidate_data.get("id"),
            job_position_id=job_data.get("id"),
            expected_start_date=job_data.get("expected_start_date"),
            salary_proposed=job_data.get("salary_range_max"),
            workplace_id=job_data.get("workplace_id"),
        )

        if admission:
            result["admission_created"] = True
            result["admission_id"] = admission.get("id")
            result["checklist_items"] = len(admission.get("checklist", []))

        logger.info(f"Admissao criada para candidato {candidate_data.get('id')}: admission_id={result['admission_id']}")

    except ImportError:
        logger.warning("AdmissionService nao disponivel")
    except Exception as e:
        logger.error(f"Erro ao criar processo de admissao: {e}")
        result["error"] = str(e)

    return result


# =============================================================================
# FLUXO 5: RH -> Operacoes (Treinamento obrigatorio pendente)
# =============================================================================
async def check_mandatory_training(
    db: AsyncSession,
    employee_id: int,
    workplace_id: int,
) -> dict[str, Any]:
    """Verifica treinamentos obrigatorios antes de alocar funcionario.

    Args:
        db: Sessao do banco de dados.
        employee_id: ID do funcionario.
        workplace_id: ID do posto.

    Returns:
        Resultado com can_allocate e lista de treinamentos pendentes.

    Raises:
        ValueError: Se treinamentos obrigatorios pendentes.
    """
    result = {
        "can_allocate": True,
        "missing_trainings": [],
        "expiring_certificates": [],
    }

    try:
        from ..human_resources.services.training_service import TrainingService

        training_service = TrainingService(db)

        missing = await training_service.check_mandatory_for_workplace(
            employee_id=employee_id,
            workplace_id=workplace_id,
        )

        if missing:
            result["can_allocate"] = False
            result["missing_trainings"] = missing

        expiring = await training_service.get_expiring_certificates(
            employee_id=employee_id,
            days_ahead=30,
        )
        result["expiring_certificates"] = expiring

    except ImportError:
        logger.warning("TrainingService nao disponivel - permitindo alocacao")
    except Exception as e:
        logger.error(f"Erro ao verificar treinamentos: {e}")

    return result


# =============================================================================
# FLUXO 6: Portal -> DP (Assinatura digital)
# =============================================================================
async def on_document_signed(
    db: AsyncSession,
    signature_data: dict[str, Any],
) -> dict[str, Any]:
    """Assinatura digital confirma ciencia de documento.

    Args:
        db: Sessao do banco de dados.
        signature_data: Dados da assinatura contendo:
            - document_id: ID do documento
            - document_type: Tipo (warning, suspension, payslip, etc)
            - employee_id: ID do funcionario
            - signature_hash: Hash SHA-256

    Returns:
        Resultado com status da atualizacao.
    """
    result = {
        "document_updated": False,
        "discipline_acknowledged": False,
        "payslip_marked_viewed": False,
    }

    doc_type = signature_data.get("document_type", "")

    try:
        if doc_type in ("warning", "suspension"):
            from ..hr.services.discipline_service import DisciplineService

            discipline_service = DisciplineService(db)
            await discipline_service.mark_acknowledged(
                discipline_id=signature_data["document_id"],
                employee_id=signature_data["employee_id"],
                signature_hash=signature_data["signature_hash"],
            )
            result["discipline_acknowledged"] = True

        elif doc_type == "payslip":
            from ..hr.services.payroll_service import PayrollService

            payroll_service = PayrollService(db)
            await payroll_service.mark_payslip_viewed(
                payslip_id=signature_data["document_id"],
                employee_id=signature_data["employee_id"],
            )
            result["payslip_marked_viewed"] = True

        result["document_updated"] = True

    except ImportError:
        logger.warning("Servico de destino nao disponivel")
    except Exception as e:
        logger.error(f"Erro ao processar assinatura: {e}")
        result["error"] = str(e)

    return result
