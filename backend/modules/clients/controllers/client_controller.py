"""
Client Controller - REST API Endpoints
Sprint 30: Cadastro de Clientes/Condomínios
"""

import logging
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from modules.clients.services.client_service import ClientService
from modules.clients.services.client_ai_service import ClientAIService
from modules.clients.schemas.client_schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse,
    ClientStats, ClientFilter,
    CondominiumCreate, CondominiumUpdate, CondominiumResponse,
    CondominiumListResponse, CondominiumStats,
    UnitCreate, UnitUpdate, UnitResponse, UnitListResponse, UnitStats,
    ClientContractCreate, ClientContractUpdate, ClientContractResponse,
    IntegrationSettingsCreate, IntegrationSettingsUpdate, IntegrationSettingsResponse,
)
from modules.clients.models.client import ClientType, ClientStatus, ClientSegment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/clients", tags=["Clients"])


def get_service(db: Session = Depends(get_db)) -> ClientService:
    """Dependency para obter ClientService."""
    return ClientService(db)


def get_ai_service(db: Session = Depends(get_db)) -> ClientAIService:
    """Dependency para obter ClientAIService."""
    return ClientAIService(db)


# =============================================================================
# CLIENT ENDPOINTS
# =============================================================================

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    service: ClientService = Depends(get_service)
):
    """Cria um novo cliente."""
    try:
        client = service.create_client(data)
        return client
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[ClientListResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    client_type: Optional[ClientType] = Query(None, alias="type"),
    status_filter: Optional[ClientStatus] = Query(None, alias="status"),
    segment: Optional[ClientSegment] = None,
    is_defaulter: Optional[bool] = None,
    is_vip: Optional[bool] = None,
    guardian_enabled: Optional[bool] = None,
    plus_enabled: Optional[bool] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    order_by: str = Query("created_at"),
    order_desc: bool = Query(True),
    service: ClientService = Depends(get_service)
):
    """Lista clientes com filtros."""
    filters = ClientFilter(
        type=client_type,
        status=status_filter,
        segment=segment,
        is_defaulter=is_defaulter,
        is_vip=is_vip,
        guardian_enabled=guardian_enabled,
        plus_enabled=plus_enabled,
        city=city,
        state=state,
        search=search
    )
    clients, _ = service.list_clients(filters, skip, limit, order_by, order_desc)
    return clients


@router.get("/stats", response_model=ClientStats)
async def get_client_stats(service: ClientService = Depends(get_service)):
    """Retorna estatísticas de clientes."""
    return service.get_client_stats()


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Obtém um cliente por ID."""
    client = service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.get("/{client_id}/full", response_model=ClientResponse)
async def get_client_full(
    client_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Obtém um cliente com todas as relações."""
    client = service.get_client_full(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    data: ClientUpdate,
    service: ClientService = Depends(get_service)
):
    """Atualiza um cliente."""
    client = service.update_client(client_id, data)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Remove um cliente."""
    if not service.delete_client(client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")


@router.post("/{client_id}/activate", response_model=ClientResponse)
async def activate_client(
    client_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Ativa um cliente."""
    client = service.activate_client(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.post("/{client_id}/suspend", response_model=ClientResponse)
async def suspend_client(
    client_id: UUID,
    reason: Optional[str] = None,
    service: ClientService = Depends(get_service)
):
    """Suspende um cliente."""
    client = service.suspend_client(client_id, reason)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.post("/{client_id}/block", response_model=ClientResponse)
async def block_client(
    client_id: UUID,
    reason: Optional[str] = None,
    service: ClientService = Depends(get_service)
):
    """Bloqueia um cliente."""
    client = service.block_client(client_id, reason)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.post("/{client_id}/set-defaulter", response_model=ClientResponse)
async def set_defaulter(
    client_id: UUID,
    debt_amount: Decimal = Query(..., gt=0),
    service: ClientService = Depends(get_service)
):
    """Marca cliente como inadimplente."""
    client = service.set_defaulter(client_id, debt_amount)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.post("/{client_id}/clear-defaulter", response_model=ClientResponse)
async def clear_defaulter(
    client_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Remove status de inadimplente."""
    client = service.clear_defaulter(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.post("/{client_id}/enable-guardian", response_model=ClientResponse)
async def enable_guardian(
    client_id: UUID,
    guardian_client_id: str = Query(..., min_length=1),
    service: ClientService = Depends(get_service)
):
    """Habilita integração com Guardian."""
    client = service.enable_guardian(client_id, guardian_client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


@router.post("/{client_id}/enable-plus", response_model=ClientResponse)
async def enable_plus(
    client_id: UUID,
    plus_client_id: str = Query(..., min_length=1),
    service: ClientService = Depends(get_service)
):
    """Habilita integração com Conecta Plus."""
    client = service.enable_plus(client_id, plus_client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client


# =============================================================================
# CONDOMINIUM ENDPOINTS
# =============================================================================

@router.post("/{client_id}/condominiums", response_model=CondominiumResponse,
             status_code=status.HTTP_201_CREATED)
async def create_condominium(
    client_id: UUID,
    data: CondominiumCreate,
    service: ClientService = Depends(get_service)
):
    """Cria um novo condomínio para o cliente."""
    data.client_id = client_id
    try:
        condominium = service.create_condominium(data)
        return condominium
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{client_id}/condominiums", response_model=List[CondominiumListResponse])
async def list_condominiums(
    client_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ClientService = Depends(get_service)
):
    """Lista condomínios do cliente."""
    condominiums, _ = service.list_condominiums(client_id, skip, limit)
    return condominiums


@router.get("/condominiums/{condominium_id}", response_model=CondominiumResponse)
async def get_condominium(
    condominium_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Obtém um condomínio por ID."""
    condominium = service.get_condominium(condominium_id)
    if not condominium:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Condomínio não encontrado"
        )
    return condominium


@router.put("/condominiums/{condominium_id}", response_model=CondominiumResponse)
async def update_condominium(
    condominium_id: UUID,
    data: CondominiumUpdate,
    service: ClientService = Depends(get_service)
):
    """Atualiza um condomínio."""
    condominium = service.update_condominium(condominium_id, data)
    if not condominium:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Condomínio não encontrado"
        )
    return condominium


@router.delete("/condominiums/{condominium_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_condominium(
    condominium_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Remove um condomínio."""
    if not service.delete_condominium(condominium_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Condomínio não encontrado"
        )


@router.post("/condominiums/{condominium_id}/activate", response_model=CondominiumResponse)
async def activate_condominium(
    condominium_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Ativa um condomínio."""
    condominium = service.activate_condominium(condominium_id)
    if not condominium:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Condomínio não encontrado"
        )
    return condominium


@router.post("/condominiums/{condominium_id}/start-implantation",
             response_model=CondominiumResponse)
async def start_implantation(
    condominium_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Inicia implantação do condomínio."""
    condominium = service.start_implantation(condominium_id)
    if not condominium:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Condomínio não encontrado"
        )
    return condominium


@router.post("/condominiums/{condominium_id}/finish-implantation",
             response_model=CondominiumResponse)
async def finish_implantation(
    condominium_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Finaliza implantação do condomínio."""
    condominium = service.finish_implantation(condominium_id)
    if not condominium:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Condomínio não encontrado"
        )
    return condominium


@router.get("/condominiums/stats", response_model=CondominiumStats)
async def get_condominium_stats(
    client_id: Optional[UUID] = None,
    service: ClientService = Depends(get_service)
):
    """Retorna estatísticas de condomínios."""
    return service.get_condominium_stats(client_id)


# =============================================================================
# UNIT ENDPOINTS
# =============================================================================

@router.post("/condominiums/{condominium_id}/units", response_model=UnitResponse,
             status_code=status.HTTP_201_CREATED)
async def create_unit(
    condominium_id: UUID,
    data: UnitCreate,
    service: ClientService = Depends(get_service)
):
    """Cria uma nova unidade no condomínio."""
    data.condominium_id = condominium_id
    try:
        unit = service.create_unit(data)
        return unit
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/condominiums/{condominium_id}/units", response_model=List[UnitListResponse])
async def list_units(
    condominium_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ClientService = Depends(get_service)
):
    """Lista unidades do condomínio."""
    units, _ = service.list_units(condominium_id, skip, limit)
    return units


@router.get("/units/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Obtém uma unidade por ID."""
    unit = service.get_unit(unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada"
        )
    return unit


@router.put("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: UUID,
    data: UnitUpdate,
    service: ClientService = Depends(get_service)
):
    """Atualiza uma unidade."""
    unit = service.update_unit(unit_id, data)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada"
        )
    return unit


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(
    unit_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Remove uma unidade."""
    if not service.delete_unit(unit_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada"
        )


@router.post("/units/{unit_id}/set-owner", response_model=UnitResponse)
async def set_unit_owner(
    unit_id: UUID,
    name: str = Query(..., min_length=2),
    document: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    service: ClientService = Depends(get_service)
):
    """Define o proprietário da unidade."""
    unit = service.set_unit_owner(unit_id, name, document, phone, email)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada"
        )
    return unit


@router.post("/units/{unit_id}/set-resident", response_model=UnitResponse)
async def set_unit_resident(
    unit_id: UUID,
    name: str = Query(..., min_length=2),
    document: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    is_tenant: bool = False,
    service: ClientService = Depends(get_service)
):
    """Define o morador/inquilino da unidade."""
    unit = service.set_unit_resident(unit_id, name, document, phone, email, is_tenant)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada"
        )
    return unit


@router.post("/units/{unit_id}/clear-resident", response_model=UnitResponse)
async def clear_unit_resident(
    unit_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Remove o morador da unidade."""
    unit = service.clear_unit_resident(unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada"
        )
    return unit


@router.get("/condominiums/{condominium_id}/units/stats", response_model=UnitStats)
async def get_unit_stats(
    condominium_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Retorna estatísticas de unidades do condomínio."""
    return service.get_unit_stats(condominium_id)


# =============================================================================
# CONTRACT ENDPOINTS
# =============================================================================

@router.post("/{client_id}/contracts", response_model=ClientContractResponse,
             status_code=status.HTTP_201_CREATED)
async def create_contract(
    client_id: UUID,
    data: ClientContractCreate,
    service: ClientService = Depends(get_service)
):
    """Cria um novo contrato de serviço."""
    data.client_id = client_id
    contract = service.create_contract(data)
    return contract


@router.get("/{client_id}/contracts", response_model=List[ClientContractResponse])
async def list_contracts(
    client_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ClientService = Depends(get_service)
):
    """Lista contratos do cliente."""
    contracts, _ = service.list_contracts(client_id, skip, limit)
    return contracts


@router.get("/contracts/{contract_id}", response_model=ClientContractResponse)
async def get_contract(
    contract_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Obtém um contrato por ID."""
    contract = service.get_contract(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado"
        )
    return contract


@router.put("/contracts/{contract_id}", response_model=ClientContractResponse)
async def update_contract(
    contract_id: UUID,
    data: ClientContractUpdate,
    service: ClientService = Depends(get_service)
):
    """Atualiza um contrato."""
    contract = service.update_contract(contract_id, data)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado"
        )
    return contract


@router.post("/contracts/{contract_id}/activate", response_model=ClientContractResponse)
async def activate_contract(
    contract_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Ativa um contrato."""
    contract = service.activate_contract(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado"
        )
    return contract


@router.post("/contracts/{contract_id}/suspend", response_model=ClientContractResponse)
async def suspend_contract(
    contract_id: UUID,
    reason: Optional[str] = None,
    service: ClientService = Depends(get_service)
):
    """Suspende um contrato."""
    contract = service.suspend_contract(contract_id, reason)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado"
        )
    return contract


@router.post("/contracts/{contract_id}/cancel", response_model=ClientContractResponse)
async def cancel_contract(
    contract_id: UUID,
    reason: Optional[str] = None,
    service: ClientService = Depends(get_service)
):
    """Cancela um contrato."""
    contract = service.cancel_contract(contract_id, reason)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado"
        )
    return contract


# =============================================================================
# INTEGRATION ENDPOINTS
# =============================================================================

@router.post("/{client_id}/integrations", response_model=IntegrationSettingsResponse,
             status_code=status.HTTP_201_CREATED)
async def create_integration(
    client_id: UUID,
    data: IntegrationSettingsCreate,
    service: ClientService = Depends(get_service)
):
    """Cria configuração de integração."""
    data.client_id = client_id
    integration = service.create_integration(data)
    return integration


@router.get("/{client_id}/integrations", response_model=List[IntegrationSettingsResponse])
async def list_integrations(
    client_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Lista integrações do cliente."""
    return service.list_integrations(client_id)


@router.get("/integrations/{settings_id}", response_model=IntegrationSettingsResponse)
async def get_integration(
    settings_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Obtém configuração de integração por ID."""
    integration = service.get_integration(settings_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integração não encontrada"
        )
    return integration


@router.put("/integrations/{settings_id}", response_model=IntegrationSettingsResponse)
async def update_integration(
    settings_id: UUID,
    data: IntegrationSettingsUpdate,
    service: ClientService = Depends(get_service)
):
    """Atualiza configuração de integração."""
    integration = service.update_integration(settings_id, data)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integração não encontrada"
        )
    return integration


@router.post("/integrations/{settings_id}/enable", response_model=IntegrationSettingsResponse)
async def enable_integration(
    settings_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Habilita uma integração."""
    integration = service.enable_integration(settings_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integração não encontrada"
        )
    return integration


@router.post("/integrations/{settings_id}/disable", response_model=IntegrationSettingsResponse)
async def disable_integration(
    settings_id: UUID,
    service: ClientService = Depends(get_service)
):
    """Desabilita uma integração."""
    integration = service.disable_integration(settings_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integração não encontrada"
        )
    return integration


# =============================================================================
# AI ENDPOINTS
# =============================================================================

@router.get("/{client_id}/ai/profile")
async def analyze_client_profile(
    client_id: UUID,
    ai_service: ClientAIService = Depends(get_ai_service)
):
    """Analisa perfil do cliente com IA."""
    result = ai_service.analyze_client_profile(client_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get("/{client_id}/ai/segmentation")
async def suggest_segmentation(
    client_id: UUID,
    ai_service: ClientAIService = Depends(get_ai_service)
):
    """Sugere segmentação para o cliente."""
    result = ai_service.suggest_segmentation(client_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get("/{client_id}/ai/churn-risk")
async def predict_churn_risk(
    client_id: UUID,
    ai_service: ClientAIService = Depends(get_ai_service)
):
    """Prediz risco de churn do cliente."""
    result = ai_service.predict_churn_risk(client_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get("/{client_id}/ai/recommendations")
async def recommend_services(
    client_id: UUID,
    ai_service: ClientAIService = Depends(get_ai_service)
):
    """Recomenda serviços para o cliente."""
    result = ai_service.recommend_services(client_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get("/condominiums/{condominium_id}/ai/health")
async def analyze_condominium_health(
    condominium_id: UUID,
    ai_service: ClientAIService = Depends(get_ai_service)
):
    """Analisa saúde do condomínio."""
    result = ai_service.analyze_condominium_health(condominium_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get("/ai/dashboard")
async def get_dashboard_insights(
    ai_service: ClientAIService = Depends(get_ai_service)
):
    """Retorna insights para o dashboard."""
    return ai_service.get_dashboard_insights()
