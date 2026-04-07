"""
Controller eSocial — Geração de eventos XML (S-2200, S-2299).

Endpoints para gerar XMLs de eventos eSocial para transmissão ao governo.
"""

import asyncio
import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field

from core.auth.dependencies import CurrentActiveUser
from modules.people_management.hr.publishers import publish_esocial_gerado
from modules.people_management.hr.services.esocial_service import ESocialEventService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/esocial", tags=["DP - eSocial"])

EMPRESA_CNPJ = "35710481000103"
EMPRESA_RAZAO = "Jordan Santos de Jesus Ltda"


class AdmissaoESocialRequest(BaseModel):
    """Dados para geração do evento S-2200 (Admissão)."""

    cpf: str = Field(..., description="CPF do trabalhador")
    nome: str = Field(..., description="Nome completo")
    data_nascimento: str | None = Field(None, description="Data de nascimento YYYY-MM-DD")
    sexo: str = Field("M", description="M ou F")
    data_admissao: str = Field(..., description="Data de admissão YYYY-MM-DD")
    cargo: str = Field("", description="Cargo")
    salario: float = Field(..., description="Salário base")
    matricula: str = Field(..., description="Matrícula eSocial")
    cbo: str = Field("", description="Código CBO")
    categoria: str = Field("101", description="Categoria do trabalhador")
    tipo_contrato: str = Field("1", description="1=Indeterminado, 2=Determinado")
    dados_complementares: dict[str, Any] | None = None


class DesligamentoESocialRequest(BaseModel):
    """Dados para geração do evento S-2299 (Desligamento)."""

    cpf: str = Field(..., description="CPF do trabalhador")
    matricula: str = Field(..., description="Matrícula eSocial")
    data_desligamento: date = Field(..., description="Data do desligamento")
    motivo: str = Field("02", description="Código do motivo (02=Sem justa causa)")
    verbas_rescisorias: list[dict[str, Any]] | None = None


@router.post(
    "/s2200/gerar",
    summary="Gerar XML S-2200 Admissao",
    description="Gera XML do evento eSocial S-2200 (Cadastramento Inicial / Admissão) para transmissão.",
    status_code=201,
)
async def gerar_s2200(
    request: AdmissaoESocialRequest,
    current_user: CurrentActiveUser,
) -> Response:
    """Gera XML do evento S-2200 (Cadastramento Inicial / Admissão).

    Retorna XML para download.
    """
    trabalhador = {
        "cpf": request.cpf,
        "nome": request.nome,
        "data_nascimento": request.data_nascimento,
        "sexo": request.sexo,
    }
    if request.dados_complementares:
        trabalhador.update(request.dados_complementares)

    contrato = {
        "data_admissao": request.data_admissao,
        "salario": request.salario,
        "matricula": request.matricula,
        "cod_cargo": request.cbo,
        "categoria": request.categoria,
        "tipo_contrato": request.tipo_contrato,
    }

    xml = ESocialEventService.gerar_s2200(
        empregador_cnpj=EMPRESA_CNPJ,
        empregador_razao=EMPRESA_RAZAO,
        trabalhador=trabalhador,
        contrato=contrato,
    )

    # Validar
    validacao = ESocialEventService.validar_xml(xml)
    if not validacao["valid"]:
        raise HTTPException(400, f"XML inválido: {validacao['errors']}")

    asyncio.create_task(publish_esocial_gerado(cpf=request.cpf, matricula=request.matricula, evento_tipo="S2200"))
    return Response(
        content=xml,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="S2200_{request.matricula}.xml"'},
    )


@router.post(
    "/s2299/gerar",
    summary="Gerar XML S-2299 Desligamento",
    description="Gera XML do evento eSocial S-2299 (Desligamento) com verbas rescisórias.",
    status_code=201,
)
async def gerar_s2299(
    request: DesligamentoESocialRequest,
    current_user: CurrentActiveUser,
) -> Response:
    """Gera XML do evento S-2299 (Desligamento).

    Retorna XML para download.
    """
    xml = ESocialEventService.gerar_s2299(
        empregador_cnpj=EMPRESA_CNPJ,
        trabalhador_cpf=request.cpf,
        matricula=request.matricula,
        data_desligamento=request.data_desligamento,
        motivo_desligamento=request.motivo,
        verbas_rescisorias=request.verbas_rescisorias,
    )

    validacao = ESocialEventService.validar_xml(xml)
    if not validacao["valid"]:
        raise HTTPException(400, f"XML inválido: {validacao['errors']}")

    asyncio.create_task(publish_esocial_gerado(cpf=request.cpf, matricula=request.matricula, evento_tipo="S2299"))
    return Response(
        content=xml,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="S2299_{request.matricula}.xml"'},
    )


@router.post(
    "/validar",
    summary="Validar XML eSocial",
    status_code=201,
    description="Valida a estrutura de um XML eSocial antes da transmissão.",
)
async def validar_xml_esocial(
    xml_content: str,
    current_user: CurrentActiveUser,
) -> Any:
    """Valida estrutura de um XML eSocial."""
    return ESocialEventService.validar_xml(xml_content)


@router.get(
    "/events",
    summary="Listar Eventos eSocial",
    description="Lista eventos eSocial gerados com status de transmissão (histórico).",
)
async def listar_eventos_esocial(
    current_user: CurrentActiveUser,
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    """Lista eventos eSocial gerados (placeholder para histórico futuro)."""
    return {
        "items": [],
        "total": 0,
        "message": "Histórico de eventos eSocial — integração em desenvolvimento",
    }
