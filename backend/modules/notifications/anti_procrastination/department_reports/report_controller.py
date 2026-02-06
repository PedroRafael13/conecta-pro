"""
Report Controller - APIs dos Relatórios Departamentais
======================================================

Endpoints para gerar relatórios personalizados por departamento.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10  
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.auth import get_current_user
from core.models.user import User

from .report_generator import DepartmentReportGenerator
from ..dashboard.unified_dashboard import UnifiedDashboard
from ..integration.module_integrator import ModuleIntegrator
from ..models import Department

router = APIRouter(prefix="/api/v1/department-reports", tags=["Department Reports"])


def get_report_service(db: Session = Depends(get_db)) -> DepartmentReportGenerator:
    """Dependency para obter serviço de relatórios."""
    integrator = ModuleIntegrator(db)
    dashboard = UnifiedDashboard(db, integrator)
    return DepartmentReportGenerator(db, dashboard)


@router.get("/hr", summary="Relatório do RH")
async def get_hr_report(
    current_user: User = Depends(get_current_user),
    report_service: DepartmentReportGenerator = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Relatório completo do departamento de Recursos Humanos.
    
    Inclui:
    - Documentos faltantes de funcionários  
    - Contratos vencendo
    - Exames médicos pendentes
    - Treinamentos em atraso
    - Avaliações de performance pendentes
    - Plano de ação recomendado
    """
    try:
        if not _has_department_permission(current_user, "hr"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Sem permissão para relatórios do RH."
            )
        
        report = await report_service.generate_hr_report()
        report["generated_at"] = datetime.utcnow().isoformat()
        report["generated_by"] = str(current_user.id)
        
        return JSONResponse(content=report)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório do RH: {str(e)}"
        )


@router.get("/commercial", summary="Relatório do Comercial")
async def get_commercial_report(
    current_user: User = Depends(get_current_user),
    report_service: DepartmentReportGenerator = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Relatório completo do departamento Comercial.
    
    Inclui:
    - Orçamentos não enviados
    - Propostas atrasadas
    - Follow-ups necessários
    - Contratos pendentes de assinatura
    - Pipeline de vendas travado
    - Recomendações de melhoria
    """
    try:
        if not _has_department_permission(current_user, "commercial"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Sem permissão para relatórios do Comercial."
            )
        
        report = await report_service.generate_commercial_report()
        report["generated_at"] = datetime.utcnow().isoformat()
        
        return JSONResponse(content=report)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório do Comercial: {str(e)}"
        )


@router.get("/financial", summary="Relatório do Financeiro")
async def get_financial_report(
    current_user: User = Depends(get_current_user),
    report_service: DepartmentReportGenerator = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Relatório completo do departamento Financeiro.
    
    Inclui:
    - Contas a pagar vencidas
    - Aprovações pendentes
    - Recibos faltantes
    - Conciliações pendentes
    - Revisões de orçamento
    - Análise de fluxo de caixa
    """
    try:
        if not _has_department_permission(current_user, "financial"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Sem permissão para relatórios do Financeiro."
            )
        
        report = await report_service.generate_financial_report()
        report["generated_at"] = datetime.utcnow().isoformat()
        
        return JSONResponse(content=report)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório do Financeiro: {str(e)}"
        )


@router.get("/facilities", summary="Relatório do Facilities")
async def get_facilities_report(
    current_user: User = Depends(get_current_user),
    report_service: DepartmentReportGenerator = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Relatório completo do departamento de Facilities.
    
    Inclui:
    - Manutenções atrasadas
    - Inspeções pendentes
    - Problemas de equipamentos
    - Avaliações de fornecedores
    - Contratos de serviço vencendo
    - Plano de manutenção preventiva
    """
    try:
        if not _has_department_permission(current_user, "facilities"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Sem permissão para relatórios do Facilities."
            )
        
        report = await report_service.generate_facilities_report()
        report["generated_at"] = datetime.utcnow().isoformat()
        
        return JSONResponse(content=report)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório do Facilities: {str(e)}"
        )


@router.get("/executive-summary", summary="Resumo Executivo")
async def get_executive_summary(
    current_user: User = Depends(get_current_user),
    report_service: DepartmentReportGenerator = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Resumo executivo consolidado de todos os departamentos.
    
    Visão de alto nível com:
    - Métricas consolidadas de todos os departamentos
    - Departamentos com mais problemas
    - Saúde geral do sistema
    - Recomendações executivas prioritárias
    - KPIs de produtividade organizacional
    """
    try:
        if not _has_executive_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Requer permissão executiva."
            )
        
        summary = await report_service.generate_executive_summary()
        summary["generated_at"] = datetime.utcnow().isoformat()
        
        return JSONResponse(content=summary)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar resumo executivo: {str(e)}"
        )


@router.get("/all-departments", summary="Relatório Consolidado")
async def get_all_departments_report(
    current_user: User = Depends(get_current_user),
    report_service: DepartmentReportGenerator = Depends(get_report_service)
) -> Dict[str, Any]:
    """
    Relatório consolidado de todos os departamentos.
    
    Gera relatórios individuais de cada departamento
    em um único documento consolidado.
    """
    try:
        if not _has_management_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Requer permissão de gestão."
            )
        
        # Gera relatórios de todos os departamentos
        reports = {
            "hr": await report_service.generate_hr_report(),
            "commercial": await report_service.generate_commercial_report(),
            "financial": await report_service.generate_financial_report(),
            "facilities": await report_service.generate_facilities_report(),
            "executive_summary": await report_service.generate_executive_summary()
        }
        
        # Adiciona metadados
        consolidated_report = {
            "report_type": "consolidated",
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": str(current_user.id),
            "departments_included": ["hr", "commercial", "financial", "facilities"],
            "reports": reports
        }
        
        return JSONResponse(content=consolidated_report)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório consolidado: {str(e)}"
        )


# Funções auxiliares de permissão

def _has_department_permission(user: User, department: str) -> bool:
    """Verifica permissão para relatório departamental."""
    # Executivos veem todos os departamentos
    if _has_executive_permission(user):
        return True
    
    # Usuário do próprio departamento
    user_dept = getattr(user, "department", "").lower()
    return user_dept == department.lower()


def _has_executive_permission(user: User) -> bool:
    """Verifica permissão executiva."""
    return user.role in ["admin", "director", "ceo", "manager"]


def _has_management_permission(user: User) -> bool:
    """Verifica permissão de gestão."""
    return user.role in ["admin", "director", "ceo", "manager", "supervisor"]
