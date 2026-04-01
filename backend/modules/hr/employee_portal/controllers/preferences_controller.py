"""Controller para preferências do funcionário."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_async_session
from modules.hr.employee_portal.schemas import (
    DashboardSettingsUpdate,
    DeviceInfo,
    NotificationPreferencesUpdate,
    PreferencesResponse,
    PreferencesUpdate,
    PrivacySettingsUpdate,
    TwoFactorSetupResponse,
)
from modules.hr.employee_portal.services import PreferencesService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/preferences", tags=["Portal - Preferências"])


@router.get(
    "/",
    response_model=PreferencesResponse,
    summary="Obter preferências",
)
async def get_preferences(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Retorna preferências do funcionário."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    preferences = await service.get_or_create_preferences(employee_id)
    return PreferencesResponse.model_validate(preferences)


@router.patch(
    "/",
    response_model=PreferencesResponse,
    summary="Atualizar preferências",
)
async def update_preferences(
    data: PreferencesUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza preferências gerais."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    preferences = await service.update_preferences(employee_id, data)
    return PreferencesResponse.model_validate(preferences)


@router.patch(
    "/notifications",
    response_model=PreferencesResponse,
    summary="Atualizar notificações",
)
async def update_notification_settings(
    data: NotificationPreferencesUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza configurações de notificações."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    preferences = await service.update_notification_settings(employee_id, data)
    return PreferencesResponse.model_validate(preferences)


@router.patch(
    "/privacy",
    response_model=PreferencesResponse,
    summary="Atualizar privacidade",
)
async def update_privacy_settings(
    data: PrivacySettingsUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza configurações de privacidade."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    preferences = await service.update_privacy_settings(employee_id, data)
    return PreferencesResponse.model_validate(preferences)


@router.patch(
    "/dashboard",
    response_model=PreferencesResponse,
    summary="Atualizar dashboard",
)
async def update_dashboard_settings(
    data: DashboardSettingsUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza configurações do dashboard."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    preferences = await service.update_dashboard_widgets(employee_id, data.widgets)
    return PreferencesResponse.model_validate(preferences)


# --- 2FA ---


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse, summary="Configurar 2FA", status_code=201)
async def setup_two_factor(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Inicia configuração de autenticação em dois fatores."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    result = await service.setup_two_factor(employee_id)
    return TwoFactorSetupResponse(**result)


@router.post("/2fa/verify", summary="Verificar código 2FA", status_code=201)
async def verify_two_factor(
    code: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Verifica código e ativa 2FA."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    success = await service.verify_and_enable_two_factor(employee_id, code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido",
        )

    return {"message": "2FA ativado com sucesso", "enabled": True}


@router.post("/2fa/disable", summary="Desativar 2FA", status_code=201)
async def disable_two_factor(
    code: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Desativa autenticação em dois fatores."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    success = await service.disable_two_factor(employee_id, code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido",
        )

    return {"message": "2FA desativado", "enabled": False}


@router.get(
    "/2fa/backup-codes",
    summary="Gerar códigos de backup",
)
async def generate_backup_codes(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Gera novos códigos de backup para 2FA."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    codes = await service.generate_backup_codes(employee_id)
    return {
        "message": "Novos códigos gerados. Guarde em local seguro.",
        "codes": codes,
    }


# --- Dispositivos ---


@router.get(
    "/devices",
    summary="Listar dispositivos",
)
async def list_devices(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Lista dispositivos confiáveis."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    devices = await service.list_trusted_devices(employee_id)
    return {"devices": devices}


@router.post("/devices/trust", summary="Adicionar dispositivo confiável", status_code=201)
async def trust_device(
    request: Request,
    device_name: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Adiciona dispositivo atual como confiável."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    device_info = DeviceInfo(
        name=device_name,
        user_agent=request.headers.get("User-Agent", ""),
        ip_address=request.client.host if request.client else None,
    )

    device = await service.add_trusted_device(employee_id, device_info)
    return {
        "message": "Dispositivo adicionado",
        "device": device,
    }


@router.delete(
    "/devices/{device_id}",
    summary="Remover dispositivo",
)
async def remove_device(
    device_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Remove dispositivo confiável."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    success = await service.remove_trusted_device(employee_id, device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    return {"message": "Dispositivo removido"}


@router.post("/devices/revoke-all", summary="Revogar todos os dispositivos", status_code=201)
async def revoke_all_devices(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Revoga todos os dispositivos confiáveis (exceto atual)."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    count = await service.revoke_all_devices(employee_id)
    return {
        "message": f"Revogados {count} dispositivos",
        "count": count,
    }


# --- Reset ---


@router.post("/reset", response_model=PreferencesResponse, summary="Restaurar padrões", status_code=201)
async def reset_preferences(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Restaura preferências para valores padrão."""
    service = PreferencesService(db)
    employee_id = UUID(current_user["employee_id"])

    preferences = await service.reset_to_defaults(employee_id)
    return PreferencesResponse.model_validate(preferences)
