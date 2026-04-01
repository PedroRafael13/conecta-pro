"""
Router de integracao full-duplex entre DP, RH e Operacoes.

Expoe endpoints HTTP para comunicacao cross-module bidirecional.
Cada endpoint dispara eventos que propagam dados entre modulos.
"""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/integration", tags=["Integracao Gestao de Pessoas"])


# =============================================================================
# Schemas
# =============================================================================


class ShiftClosedRequest(BaseModel):
    employee_id: int
    date: str
    regular_hours: float = 0
    overtime_hours: float = 0
    night_hours: float = 0
    is_absence: bool = False
    late_minutes: int = 0
    workplace_id: int | None = None


class OccurrenceRequest(BaseModel):
    id: int
    employee_id: int
    severity: str
    description: str = ""
    category: str = ""


class VacationApprovedRequest(BaseModel):
    id: int
    employee_id: int
    start_date: str
    end_date: str


class CandidateApprovedRequest(BaseModel):
    candidate_id: int | None = None
    candidate_name: str = ""
    cpf: str = ""
    job_position_id: int | None = None
    workplace_id: int | None = None
    salary_proposed: float | None = None
    expected_start_date: str | None = None


class MandatoryTrainingRequest(BaseModel):
    employee_id: int
    workplace_id: int


class DocumentSignedRequest(BaseModel):
    document_id: int
    document_type: str
    employee_id: int
    signature_hash: str = ""


class TerminationNotifyRequest(BaseModel):
    employee_id: int
    termination_type: str
    last_day: str
    reason: str = ""


class AdmissionCompletedRequest(BaseModel):
    employee_id: int
    name: str
    position: str = ""
    workplace_id: int | None = None
    start_date: str = ""


class AvailabilityCheckRequest(BaseModel):
    employee_id: int
    start_date: str
    end_date: str


class PayrollDataRequest(BaseModel):
    employee_id: int
    month: int
    year: int


# =============================================================================
# Helper: get db session
# =============================================================================


async def get_db():
    """Tenta obter sessao do banco via diferentes caminhos."""
    try:
        from core.database import get_async_session

        async for session in get_async_session():
            yield session
    except ImportError:
        try:
            from database import get_async_session

            async for session in get_async_session():
                yield session
        except ImportError:
            yield None


# =============================================================================
# FLUXO 1: Operacoes -> DP (Fechamento de turno -> Ponto)
# =============================================================================


@router.post("/ops-to-dp/shift-closed")
async def shift_closed_to_dp(
    req: ShiftClosedRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Operacoes notifica DP sobre fechamento de turno.

    Registra horas no ponto e credita banco de horas se houver extras.
    """
    from .events import on_shift_closed

    return await on_shift_closed(db, req.model_dump())


# =============================================================================
# FLUXO 2: Operacoes -> DP (Ocorrencia grave -> Disciplinar)
# =============================================================================


@router.post("/ops-to-dp/occurrence")
async def occurrence_to_dp(
    req: OccurrenceRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Operacoes notifica DP sobre ocorrencia grave.

    Cria processo disciplinar automaticamente para severidade grave/gravissima.
    """
    from .events import on_occurrence_registered

    return await on_occurrence_registered(db, req.model_dump())


# =============================================================================
# FLUXO 3: DP -> Operacoes (Ferias aprovadas -> Substituicao)
# =============================================================================


@router.post("/dp-to-ops/vacation-approved")
async def vacation_approved_to_ops(
    req: VacationApprovedRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """DP notifica Operacoes sobre ferias aprovadas.

    Dispara geracao de substituicao/escala via IA.
    """
    from .events import on_vacation_approved

    return await on_vacation_approved(db, req.model_dump())


# =============================================================================
# FLUXO 4: RH -> DP (Candidato aprovado -> Admissao)
# =============================================================================


@router.post("/rh-to-dp/candidate-approved")
async def candidate_approved_to_dp(
    req: CandidateApprovedRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """RH notifica DP sobre aprovacao de candidato.

    Inicia processo de admissao automaticamente.
    """
    from .events import on_candidate_approved

    candidate_data = {
        "id": req.candidate_id,
        "name": req.candidate_name,
        "cpf": req.cpf,
    }
    job_data = {
        "id": req.job_position_id,
        "workplace_id": req.workplace_id,
        "salary_range_max": req.salary_proposed,
        "expected_start_date": req.expected_start_date,
    }
    return await on_candidate_approved(db, candidate_data, job_data)


# =============================================================================
# FLUXO 5: RH -> Operacoes (Treinamento obrigatorio -> Bloqueio)
# =============================================================================


@router.post("/rh-to-ops/mandatory-training-check")
async def mandatory_training_check(
    req: MandatoryTrainingRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """RH verifica treinamentos obrigatorios antes de alocacao.

    Retorna se funcionario pode ser alocado e treinamentos pendentes.
    """
    from .events import check_mandatory_training

    return await check_mandatory_training(db, req.employee_id, req.workplace_id)


# =============================================================================
# FLUXO 6: Portal -> DP (Assinatura digital)
# =============================================================================


@router.post("/portal-to-dp/document-signed")
async def document_signed_to_dp(
    req: DocumentSignedRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Portal notifica DP sobre assinatura digital de documento.

    Marca documento como reconhecido/ciencia pelo funcionario.
    """
    from .events import on_document_signed

    return await on_document_signed(db, req.model_dump())


# =============================================================================
# FLUXO 7: DP -> Operacoes (Rescisao -> Desalocacao) [NOVO]
# =============================================================================


@router.post("/dp-to-ops/termination-notify")
async def termination_to_ops(
    req: TerminationNotifyRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """DP notifica Operacoes sobre rescisao.

    Remove funcionario das escalas e gera necessidade de substituicao.
    """
    from .events import on_termination_initiated

    return await on_termination_initiated(db, req.model_dump())


# =============================================================================
# FLUXO 8: DP -> RH (Admissao concluida -> Onboarding) [NOVO]
# =============================================================================


@router.post("/dp-to-rh/admission-completed")
async def admission_completed_to_rh(
    req: AdmissionCompletedRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """DP notifica RH sobre admissao concluida.

    Inicia processo de onboarding e agenda treinamentos obrigatorios.
    """
    from .events import on_admission_completed

    return await on_admission_completed(db, req.model_dump())


# =============================================================================
# FLUXO 9: Operacoes -> DP (Verificacao disponibilidade) [NOVO]
# =============================================================================


@router.post("/ops-to-dp/check-availability")
async def check_employee_availability(
    req: AvailabilityCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Operacoes verifica no DP se funcionario esta disponivel.

    Consulta ferias, licencas, suspensoes ativas.
    """
    from datetime import date as dt_date

    from .services import scale_integration

    return await scale_integration.check_availability(
        db=db,
        employee_id=req.employee_id,
        start_date=dt_date.fromisoformat(req.start_date),
        end_date=dt_date.fromisoformat(req.end_date),
    )


# =============================================================================
# FLUXO 10: Operacoes -> DP (Coleta dados para folha) [NOVO]
# =============================================================================


@router.post("/ops-to-dp/payroll-data")
async def collect_payroll_data(
    req: PayrollDataRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Operacoes envia dados de turnos para calculo de folha.

    Coleta horas regulares, extras, noturnas, faltas e atrasos.
    """
    from .services import payroll_integration

    return await payroll_integration.collect_shift_data(
        db=db,
        employee_id=req.employee_id,
        month=req.month,
        year=req.year,
    )


# =============================================================================
# OVERVIEW: Dashboard de integracao
# =============================================================================


@router.get("/status")
async def integration_status() -> dict[str, Any]:
    """Retorna status de todos os fluxos de integracao.

    Util para monitoramento e debug da comunicacao full-duplex.
    """
    flows = [
        {
            "id": 1,
            "direction": "Ops -> DP",
            "name": "Fechamento turno -> Ponto",
            "endpoint": "/ops-to-dp/shift-closed",
            "status": "active",
        },
        {
            "id": 2,
            "direction": "Ops -> DP",
            "name": "Ocorrencia grave -> Disciplinar",
            "endpoint": "/ops-to-dp/occurrence",
            "status": "active",
        },
        {
            "id": 3,
            "direction": "DP -> Ops",
            "name": "Ferias aprovadas -> Substituicao",
            "endpoint": "/dp-to-ops/vacation-approved",
            "status": "active",
        },
        {
            "id": 4,
            "direction": "RH -> DP",
            "name": "Candidato aprovado -> Admissao",
            "endpoint": "/rh-to-dp/candidate-approved",
            "status": "active",
        },
        {
            "id": 5,
            "direction": "RH -> Ops",
            "name": "Treinamento obrigatorio -> Bloqueio",
            "endpoint": "/rh-to-ops/mandatory-training-check",
            "status": "active",
        },
        {
            "id": 6,
            "direction": "Portal -> DP",
            "name": "Assinatura digital -> Ciencia",
            "endpoint": "/portal-to-dp/document-signed",
            "status": "active",
        },
        {
            "id": 7,
            "direction": "DP -> Ops",
            "name": "Rescisao -> Desalocacao",
            "endpoint": "/dp-to-ops/termination-notify",
            "status": "active",
        },
        {
            "id": 8,
            "direction": "DP -> RH",
            "name": "Admissao concluida -> Onboarding",
            "endpoint": "/dp-to-rh/admission-completed",
            "status": "active",
        },
        {
            "id": 9,
            "direction": "Ops -> DP",
            "name": "Verificacao disponibilidade",
            "endpoint": "/ops-to-dp/check-availability",
            "status": "active",
        },
        {
            "id": 10,
            "direction": "Ops -> DP",
            "name": "Coleta dados folha",
            "endpoint": "/ops-to-dp/payroll-data",
            "status": "active",
        },
    ]

    directions = {}
    for f in flows:
        d = f["direction"]
        if d not in directions:
            directions[d] = 0
        directions[d] += 1

    return {
        "total_flows": len(flows),
        "active_flows": len([f for f in flows if f["status"] == "active"]),
        "direction_summary": directions,
        "full_duplex": True,
        "flows": flows,
    }
