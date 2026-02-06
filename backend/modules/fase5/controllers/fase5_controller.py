"""
modules/fase5/controllers/fase5_controller.py - Fase 5 API Controller
====================================================================
Endpoints REST para Fase 5 - Grand Finale
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Query, Body
from pydantic import BaseModel, Field, EmailStr

from ..cct_compliance.service import CCTComplianceService
from ..cct_compliance.enums import TipoCargo, TipoJornada, TipoBeneficio
from ..email_intelligence.service import EmailIntelligenceService
from ..email_intelligence.models import EmailMessage
from ..quality_framework.validator import QualityValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fase5", tags=["Fase 5 - Grand Finale"])

# Services
cct_service = CCTComplianceService()
email_service = EmailIntelligenceService()
quality_validator = QualityValidator()


# ============================================================================
# Schemas
# ============================================================================

class ValidarSalarioRequest(BaseModel):
    """Request para validacao de salario."""
    cargo: str
    salario: float


class ValidarCompletoRequest(BaseModel):
    """Request para validacao completa CCT."""
    cargo: str
    salario: float
    jornada: str = "44h_semanais"
    beneficios: List[str] = Field(default_factory=list)


class CalcularCustoRequest(BaseModel):
    """Request para calculo de custo."""
    cargo: str
    salario: Optional[float] = None
    jornada: str = "44h_semanais"
    incluir_encargos: bool = True


class GerarPropostaRequest(BaseModel):
    """Request para geracao de proposta."""
    cargos: List[Dict[str, Any]]
    margem: float = 15.0


class AnalisarEmailRequest(BaseModel):
    """Request para analise de email."""
    from_address: EmailStr
    to_addresses: List[EmailStr]
    subject: str
    body_text: Optional[str] = None
    tenant_id: str


class QualidadeRequest(BaseModel):
    """Request para validacao de qualidade."""
    component: str = "fase5"
    phase: str = "grand_finale"


# ============================================================================
# CCT Compliance Endpoints
# ============================================================================

@router.get("/cct/cargos", response_model=Dict[str, Any])
async def listar_cargos():
    """Lista todos os cargos com pisos salariais CCT 2026."""
    try:
        cargos = cct_service.listar_cargos()
        return {
            "success": True,
            "data": cargos,
            "total": len(cargos),
            "vigencia": "SINDCOND 2026"
        }
    except Exception as e:
        logger.error(f"Erro ao listar cargos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar cargos"
        )


@router.get("/cct/cargo/{cargo}", response_model=Dict[str, Any])
async def obter_cargo(cargo: str):
    """Obtem detalhes de um cargo especifico."""
    try:
        tipo_cargo = TipoCargo(cargo)
        piso = cct_service.obter_piso_salarial(tipo_cargo)

        if not piso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cargo {cargo} nao encontrado"
            )

        return {
            "success": True,
            "data": {
                "cargo": cargo,
                "piso_salarial": str(piso),
                "vigencia": "SINDCOND 2026",
                "reajuste": "7.1%"
            }
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cargo invalido: {cargo}"
        )


@router.post("/cct/validar-salario", response_model=Dict[str, Any])
async def validar_salario(request: ValidarSalarioRequest):
    """Valida salario contra piso da CCT."""
    try:
        tipo_cargo = TipoCargo(request.cargo)
        resultado = cct_service.validar_salario(
            tipo_cargo,
            Decimal(str(request.salario))
        )

        return {
            "success": True,
            "data": resultado
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/cct/validar-completo", response_model=Dict[str, Any])
async def validar_completo(request: ValidarCompletoRequest):
    """Executa validacao completa de compliance CCT."""
    try:
        tipo_cargo = TipoCargo(request.cargo)
        tipo_jornada = TipoJornada(request.jornada)
        beneficios = [TipoBeneficio(b) for b in request.beneficios]

        validacao = cct_service.validar_completo(
            cargo=tipo_cargo,
            salario=Decimal(str(request.salario)),
            jornada=tipo_jornada,
            beneficios=beneficios
        )

        return {
            "success": True,
            "data": validacao.model_dump()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/cct/calcular-custo", response_model=Dict[str, Any])
async def calcular_custo(request: CalcularCustoRequest):
    """Calcula custo total de um funcionario."""
    try:
        tipo_cargo = TipoCargo(request.cargo)
        tipo_jornada = TipoJornada(request.jornada)
        salario = Decimal(str(request.salario)) if request.salario else None

        resultado = cct_service.calcular_custo_funcionario(
            cargo=tipo_cargo,
            salario_base=salario,
            jornada=tipo_jornada,
            incluir_encargos=request.incluir_encargos
        )

        return {
            "success": True,
            "data": resultado
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/cct/gerar-proposta", response_model=Dict[str, Any])
async def gerar_proposta(request: GerarPropostaRequest):
    """Gera proposta comercial baseada na CCT."""
    try:
        resultado = cct_service.gerar_proposta_comercial(
            cargos=request.cargos,
            margem_lucro_percentual=Decimal(str(request.margem))
        )

        return {
            "success": True,
            "data": resultado
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# Email Intelligence Endpoints
# ============================================================================

@router.post("/email/analisar", response_model=Dict[str, Any])
async def analisar_email(request: AnalisarEmailRequest):
    """Analisa um email e retorna classificacao, entidades e sugestoes."""
    try:
        email = EmailMessage(
            from_address=request.from_address,
            to_addresses=request.to_addresses,
            subject=request.subject,
            body_text=request.body_text,
            tenant_id=UUID(request.tenant_id)
        )

        resultado = await email_service.process_incoming_email(email)

        return {
            "success": True,
            "data": resultado
        }
    except Exception as e:
        logger.error(f"Erro ao analisar email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao analisar email"
        )


@router.get("/email/contexto/{email_address}", response_model=Dict[str, Any])
async def obter_contexto_email(
    email_address: str,
    tenant_id: str = Query(...)
):
    """Obtem contexto historico de um endereco de email."""
    try:
        contexto = await email_service.get_email_context(
            email_address,
            UUID(tenant_id)
        )

        return {
            "success": True,
            "data": contexto.model_dump()
        }
    except Exception as e:
        logger.error(f"Erro ao obter contexto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter contexto"
        )


# ============================================================================
# Quality Framework Endpoints
# ============================================================================

@router.post("/quality/validate", response_model=Dict[str, Any])
async def validar_qualidade(request: QualidadeRequest):
    """Executa validacao de qualidade do sistema."""
    try:
        report = await quality_validator.validate(
            component=request.component,
            phase=request.phase
        )

        summary = quality_validator.get_summary(report)

        return {
            "success": True,
            "data": summary,
            "passed": report.passed,
            "target": "99+/100"
        }
    except Exception as e:
        logger.error(f"Erro na validacao de qualidade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro na validacao de qualidade"
        )


# ============================================================================
# System Status Endpoints
# ============================================================================

@router.get("/status", response_model=Dict[str, Any])
async def status_fase5():
    """Retorna status da Fase 5."""
    return {
        "success": True,
        "data": {
            "phase": "Fase 5 - Grand Finale",
            "status": "operational",
            "components": {
                "cct_compliance": "active",
                "email_intelligence": "active",
                "quality_framework": "active",
                "mcp_servers": "configured"
            },
            "quality_target": "99+/100",
            "vigencia_cct": "SINDCOND 2026",
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_fase5():
    """Health check da Fase 5."""
    return {
        "status": "healthy",
        "phase": "fase5",
        "timestamp": datetime.utcnow().isoformat()
    }
