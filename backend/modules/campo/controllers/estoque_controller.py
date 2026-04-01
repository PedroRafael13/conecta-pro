"""
Controller de Integração com Estoque para Campo.

Fornece endpoints para:
- Requisição de materiais
- Baixa de materiais
- Verificação de disponibilidade
- Alertas de estoque
"""

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.campo.services.estoque_integration import (
    get_estoque_integration_service,
)

router = APIRouter()


# =============================================================================
# SCHEMAS
# =============================================================================


class ItemRequisicaoRequest(BaseModel):
    """Item para requisição."""

    produto_id: UUID
    quantidade: Decimal = Field(..., gt=0)
    observacao: str | None = Field(None, max_length=200)


class CriarRequisicaoRequest(BaseModel):
    """Request para criar requisição."""

    ordem_servico_id: UUID
    tecnico_id: UUID
    itens: list[ItemRequisicaoRequest]
    observacoes: str | None = Field(None, max_length=500)


class AprovarRequisicaoRequest(BaseModel):
    """Request para aprovar requisição."""

    aprovador_id: UUID
    itens_aprovados: list[dict[str, Any]] | None = None
    observacoes: str | None = Field(None, max_length=500)


class EntregarRequisicaoRequest(BaseModel):
    """Request para registrar entrega."""

    itens_entregues: list[dict[str, Any]] | None = None


class ItemBaixaRequest(BaseModel):
    """Item para baixa."""

    produto_id: str
    quantidade_utilizada: Decimal = Field(..., ge=0)
    quantidade_requisitada: Decimal | None = None


class RegistrarBaixaRequest(BaseModel):
    """Request para registrar baixa."""

    itens_utilizados: list[ItemBaixaRequest]
    tecnico_id: UUID | None = None


class RequisicaoResponse(BaseModel):
    """Response de requisição."""

    id: str
    ordem_servico_id: str
    tecnico_id: str
    status: str
    itens: list[dict[str, Any]]
    data_solicitacao: str
    data_aprovacao: str | None
    data_entrega: str | None


# =============================================================================
# ENDPOINTS - REQUISIÇÕES
# =============================================================================


@router.post(
    "/requisicao", summary="Criar requisição", description="Cria requisição de materiais para uma OS", status_code=201
)
async def criar_requisicao(
    request: CriarRequisicaoRequest,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Cria requisição de materiais para uma Ordem de Serviço.

    O técnico pode solicitar materiais antes de ir ao campo.
    A requisição fica pendente até aprovação do gestor.
    """
    service = get_estoque_integration_service(db)

    try:
        requisicao = service.criar_requisicao(
            ordem_servico_id=request.ordem_servico_id,
            tecnico_id=request.tecnico_id,
            itens=[
                {
                    "produto_id": item.produto_id,
                    "quantidade": item.quantidade,
                    "observacao": item.observacao,
                }
                for item in request.itens
            ],
            observacoes=request.observacoes,
        )

        return {
            "id": str(requisicao.id),
            "ordem_servico_id": str(requisicao.ordem_servico_id),
            "tecnico_id": str(requisicao.tecnico_id),
            "status": requisicao.status.value,
            "itens": [
                {
                    "produto_id": str(item.produto_id),
                    "produto_nome": item.produto_nome,
                    "quantidade_solicitada": float(item.quantidade_solicitada),
                    "unidade": item.unidade,
                }
                for item in requisicao.itens
            ],
            "data_solicitacao": requisicao.data_solicitacao.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/requisicao/{requisicao_id}/aprovar",
    summary="Aprovar requisição",
    description="Aprova uma requisição de materiais",
)
async def aprovar_requisicao(
    requisicao_id: UUID,
    request: AprovarRequisicaoRequest,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Aprova uma requisição de materiais.

    O gestor pode aprovar total ou parcialmente.
    """
    service = get_estoque_integration_service(db)

    try:
        requisicao = service.aprovar_requisicao(
            requisicao_id=requisicao_id,
            aprovador_id=request.aprovador_id,
            itens_aprovados=request.itens_aprovados,
            observacoes=request.observacoes,
        )

        return {
            "message": "Requisição aprovada com sucesso",
            "requisicao_id": str(requisicao.id),
            "status": requisicao.status.value,
            "itens": [
                {
                    "produto_id": str(item.produto_id),
                    "quantidade_aprovada": float(item.quantidade_aprovada or 0),
                }
                for item in requisicao.itens
            ],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/requisicao/{requisicao_id}/entregar",
    summary="Registrar entrega",
    description="Registra entrega de materiais de uma requisição",
)
async def registrar_entrega(
    requisicao_id: UUID,
    request: EntregarRequisicaoRequest,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Registra a entrega de materiais ao técnico.

    Pode ser entrega total ou parcial.
    """
    service = get_estoque_integration_service(db)

    try:
        requisicao = service.registrar_entrega(
            requisicao_id=requisicao_id,
            itens_entregues=request.itens_entregues,
        )

        return {
            "message": "Entrega registrada com sucesso",
            "requisicao_id": str(requisicao.id),
            "status": requisicao.status.value,
            "data_entrega": requisicao.data_entrega.isoformat() if requisicao.data_entrega else None,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# ENDPOINTS - BAIXA
# =============================================================================


@router.post(
    "/baixa/{ordem_servico_id}",
    summary="Registrar baixa",
    description="Registra baixa de materiais utilizados em uma OS",
)
async def registrar_baixa(
    ordem_servico_id: UUID,
    request: RegistrarBaixaRequest,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Registra baixa de materiais efetivamente utilizados.

    Materiais não utilizados são automaticamente devolvidos ao estoque.
    """
    service = get_estoque_integration_service(db)

    try:
        resultado = service.registrar_baixa_os(
            ordem_servico_id=ordem_servico_id,
            itens_utilizados=[
                {
                    "produto_id": item.produto_id,
                    "quantidade_utilizada": float(item.quantidade_utilizada),
                    "quantidade_requisitada": float(item.quantidade_requisitada)
                    if item.quantidade_requisitada
                    else float(item.quantidade_utilizada),
                }
                for item in request.itens_utilizados
            ],
            tecnico_id=request.tecnico_id,
        )

        return resultado

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/baixa-automatica/{ordem_servico_id}",
    summary="Baixa automática",
    description="Realiza baixa automática ao concluir OS",
)
async def baixa_automatica(
    ordem_servico_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Realiza baixa automática quando OS é concluída.

    Baixa todos os materiais entregues que ainda não foram baixados.
    """
    service = get_estoque_integration_service(db)

    try:
        resultado = service.baixa_automatica_conclusao(
            ordem_servico_id=ordem_servico_id,
        )
        return resultado

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# ENDPOINTS - VERIFICAÇÕES
# =============================================================================


@router.get(
    "/disponibilidade/{produto_id}",
    summary="Verificar disponibilidade",
    description="Verifica disponibilidade de um produto",
)
async def verificar_disponibilidade(
    produto_id: UUID,
    current_user: CurrentActiveUser,
    quantidade: Decimal = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    """
    Verifica se um produto está disponível no estoque.

    Retorna informações sobre estoque atual e alertas.
    """
    service = get_estoque_integration_service(db)

    resultado = service.verificar_disponibilidade(
        produto_id=produto_id,
        quantidade=quantidade,
    )

    return resultado


@router.get(
    "/estoque-tecnico/{tecnico_id}",
    summary="Estoque do técnico",
    description="Verifica materiais em posse de um técnico",
)
async def verificar_estoque_tecnico(
    tecnico_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Verifica quais materiais estão em posse de um técnico.

    Útil para controle de inventário móvel.
    """
    service = get_estoque_integration_service(db)

    resultado = service.verificar_estoque_tecnico(
        tecnico_id=tecnico_id,
    )

    return resultado


@router.get("/alertas", summary="Alertas de estoque", description="Retorna alertas de produtos com estoque baixo")
async def alertas_estoque_baixo(
    current_user: CurrentActiveUser,
    threshold: float = Query(20, ge=0, le=100, description="Percentual mínimo"),
    db: Session = Depends(get_db),
):
    """
    Retorna produtos com estoque abaixo do mínimo.

    Útil para planejamento de compras.
    """
    service = get_estoque_integration_service(db)

    alertas = service.alertas_estoque_baixo(
        threshold_percentual=threshold,
    )

    return {
        "alertas": alertas,
        "total": len(alertas),
        "threshold_percentual": threshold,
    }


# =============================================================================
# ENDPOINTS - RELATÓRIOS
# =============================================================================


@router.get(
    "/relatorio/os/{ordem_servico_id}",
    summary="Relatório de consumo da OS",
    description="Relatório de materiais consumidos em uma OS",
)
async def relatorio_consumo_os(
    ordem_servico_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
):
    """
    Relatório detalhado de consumo de materiais de uma OS.

    Inclui requisitado, utilizado e devolvido.
    """
    service = get_estoque_integration_service(db)

    try:
        relatorio = service.relatorio_consumo_os(
            ordem_servico_id=ordem_servico_id,
        )
        return relatorio

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.get(
    "/relatorio/periodo",
    summary="Relatório de consumo por período",
    description="Relatório de materiais consumidos em um período",
)
async def relatorio_consumo_periodo(
    current_user: CurrentActiveUser,
    data_inicio: date = Query(..., description="Data inicial"),
    data_fim: date = Query(..., description="Data final"),
    tecnico_id: UUID | None = Query(None, description="Filtrar por técnico"),
    db: Session = Depends(get_db),
):
    """
    Relatório de consumo de materiais por período.

    Pode ser filtrado por técnico.
    """
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Data fim deve ser maior ou igual a data início"
        )

    service = get_estoque_integration_service(db)

    try:
        relatorio = service.relatorio_consumo_periodo(
            data_inicio=data_inicio,
            data_fim=data_fim,
            tecnico_id=tecnico_id,
        )
        return relatorio

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao gerar relatório: {str(e)}"
        )


# =============================================================================
# ENDPOINTS - KIT PADRÃO
# =============================================================================


@router.get("/kit-padrao", summary="Kits padrão", description="Lista kits padrão de materiais por tipo de OS")
async def listar_kits_padrao(current_user: CurrentActiveUser):
    """
    Lista kits padrão de materiais por tipo de serviço.

    Útil para requisições rápidas.
    """
    return {
        "kits": [
            {
                "tipo_servico": "INSTALACAO",
                "nome": "Kit Instalação Básico",
                "itens": [
                    {"codigo": "FI-001", "nome": "Fita Isolante", "quantidade": 1},
                    {"codigo": "PF-004", "nome": "Parafusos Philips 4mm", "quantidade": 10},
                    {"codigo": "CB-001", "nome": "Cabo de Rede Cat5e (metro)", "quantidade": 5},
                    {"codigo": "CN-001", "nome": "Conector RJ45", "quantidade": 4},
                ],
            },
            {
                "tipo_servico": "MANUTENCAO",
                "nome": "Kit Manutenção Básico",
                "itens": [
                    {"codigo": "FI-001", "nome": "Fita Isolante", "quantidade": 1},
                    {"codigo": "LB-001", "nome": "Limpa Contato", "quantidade": 1},
                    {"codigo": "FE-001", "nome": "Ferramentas", "quantidade": 1},
                ],
            },
            {
                "tipo_servico": "VISITA_TECNICA",
                "nome": "Kit Visita Técnica",
                "itens": [
                    {"codigo": "MT-001", "nome": "Multímetro", "quantidade": 1},
                    {"codigo": "LN-001", "nome": "Lanterna", "quantidade": 1},
                ],
            },
        ]
    }


@router.post("/requisitar-kit", summary="Requisitar kit", description="Cria requisição a partir de um kit padrão")
async def requisitar_kit(
    ordem_servico_id: UUID,
    tecnico_id: UUID,
    current_user: CurrentActiveUser,
    tipo_kit: str = Query(..., description="Tipo do kit (INSTALACAO, MANUTENCAO, etc)"),
    db: Session = Depends(get_db),
):
    """
    Cria requisição de materiais a partir de um kit padrão.

    Facilita requisições recorrentes.
    """
    kits_padrao = {
        "INSTALACAO": [
            {"produto_id": "00000000-0000-0000-0000-000000000001", "quantidade": 1},
            {"produto_id": "00000000-0000-0000-0000-000000000002", "quantidade": 10},
        ],
        "MANUTENCAO": [
            {"produto_id": "00000000-0000-0000-0000-000000000001", "quantidade": 1},
            {"produto_id": "00000000-0000-0000-0000-000000000003", "quantidade": 1},
        ],
    }

    kit = kits_padrao.get(tipo_kit.upper())
    if not kit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Kit '{tipo_kit}' não encontrado")

    service = get_estoque_integration_service(db)

    try:
        requisicao = service.criar_requisicao(
            ordem_servico_id=ordem_servico_id,
            tecnico_id=tecnico_id,
            itens=[
                {
                    "produto_id": UUID(item["produto_id"]),
                    "quantidade": Decimal(str(item["quantidade"])),
                }
                for item in kit
            ],
            observacoes=f"Requisição automática - Kit {tipo_kit}",
        )

        return {
            "message": f"Kit {tipo_kit} requisitado com sucesso",
            "requisicao_id": str(requisicao.id),
            "itens": len(requisicao.itens),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
