"""
Controller para o módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""

# pylint: disable=unused-argument,too-many-locals,redefined-outer-name
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.config.schemas import (
    # Dashboard
    ConfigDashboard,
    # FeatureFlag
    FeatureFlagCreate,
    FeatureFlagEvaluate,
    FeatureFlagEvaluateResponse,
    FeatureFlagGradualRollout,
    FeatureFlagList,
    FeatureFlagResponse,
    FeatureFlagTenantToggle,
    FeatureFlagUpdate,
    # NotificationTemplate
    NotificationTemplateCreate,
    NotificationTemplateList,
    NotificationTemplateRender,
    NotificationTemplateRenderResponse,
    NotificationTemplateResponse,
    NotificationTemplateUpdate,
    # SystemConfig
    SystemConfigCreate,
    SystemConfigList,
    SystemConfigResponse,
    SystemConfigUpdate,
    TenantAddressUpdate,
    # Tenant
    TenantCreate,
    TenantDashboard,
    TenantList,
    TenantPlanUpdate,
    TenantResponse,
    # TenantSettings
    TenantSettingsCreate,
    TenantSettingsList,
    TenantSettingsResponse,
    TenantSettingsUpdate,
    TenantSettingsValueUpdate,
    TenantUpdate,
)
from modules.config.services import ConfigService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/config", tags=["Config"])


# ==================== Tenant Endpoints ====================
@router.get("/tenants", response_model=TenantList)
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str | None = None,
    plan: str | None = None,
    tenant_type: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantList:
    """Lista tenants com filtros."""
    service = ConfigService(db)
    items, total = await service.list_tenants(
        skip=skip, limit=limit, status=status, plan=plan, tenant_type=tenant_type, search=search
    )
    return TenantList(items=items, total=total, skip=skip, limit=limit)


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantResponse:
    """Cria novo tenant."""
    service = ConfigService(db)
    return await service.create_tenant(data)


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantResponse:
    """Busca tenant por ID."""
    service = ConfigService(db)
    tenant = await service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantResponse:
    """Atualiza tenant."""
    service = ConfigService(db)
    tenant = await service.update_tenant(tenant_id, data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.put("/tenants/{tenant_id}/plan", response_model=TenantResponse)
async def update_tenant_plan(
    tenant_id: UUID,
    data: TenantPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantResponse:
    """Atualiza plano do tenant."""
    service = ConfigService(db)
    tenant = await service.update_tenant_plan(tenant_id, data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.put("/tenants/{tenant_id}/address", response_model=TenantResponse)
async def update_tenant_address(
    tenant_id: UUID,
    data: TenantAddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantResponse:
    """Atualiza endereço do tenant."""
    service = ConfigService(db)
    tenant = await service.update_tenant_address(tenant_id, data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.post("/tenants/{tenant_id}/activate", response_model=TenantResponse)
async def activate_tenant(
    tenant_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantResponse:
    """Ativa tenant."""
    service = ConfigService(db)
    tenant = await service.activate_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.post("/tenants/{tenant_id}/suspend", response_model=TenantResponse)
async def suspend_tenant(
    tenant_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantResponse:
    """Suspende tenant."""
    service = ConfigService(db)
    tenant = await service.suspend_tenant(tenant_id, reason)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.post("/tenants/{tenant_id}/cancel", response_model=TenantResponse)
async def cancel_tenant(
    tenant_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantResponse:
    """Cancela tenant."""
    service = ConfigService(db)
    tenant = await service.cancel_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.post("/tenants/{tenant_id}/convert-trial", response_model=TenantResponse)
async def convert_trial(
    tenant_id: UUID,
    plan: str = "starter",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantResponse:
    """Converte trial para plano pago."""
    service = ConfigService(db)
    tenant = await service.convert_trial(tenant_id, plan)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.post("/tenants/{tenant_id}/features/{feature}/enable", response_model=TenantResponse)
async def enable_tenant_feature(
    tenant_id: UUID, feature: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantResponse:
    """Habilita feature para tenant."""
    service = ConfigService(db)
    tenant = await service.enable_feature(tenant_id, feature)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.post("/tenants/{tenant_id}/features/{feature}/disable", response_model=TenantResponse)
async def disable_tenant_feature(
    tenant_id: UUID, feature: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantResponse:
    """Desabilita feature para tenant."""
    service = ConfigService(db)
    tenant = await service.disable_feature(tenant_id, feature)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> None:
    """Remove tenant."""
    service = ConfigService(db)
    deleted = await service.delete_tenant(tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")


# ==================== TenantSettings Endpoints ====================
@router.get("/tenants/{tenant_id}/settings", response_model=TenantSettingsList)
async def list_tenant_settings(
    tenant_id: UUID,
    category: str | None = None,
    group: str | None = None,
    visible: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantSettingsList:
    """Lista configurações do tenant."""
    service = ConfigService(db)
    items, total = await service.list_tenant_settings(
        tenant_id=tenant_id, category=category, group=group, visible=visible
    )
    return TenantSettingsList(items=items, total=total)


@router.post(
    "/tenants/{tenant_id}/settings", response_model=TenantSettingsResponse, status_code=status.HTTP_201_CREATED
)
async def create_tenant_setting(
    tenant_id: UUID,
    data: TenantSettingsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantSettingsResponse:
    """Cria configuração do tenant."""
    data.tenant_id = tenant_id
    service = ConfigService(db)
    return await service.create_setting(data)


@router.get("/settings/{setting_id}", response_model=TenantSettingsResponse)
async def get_setting(
    setting_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantSettingsResponse:
    """Busca configuração por ID."""
    service = ConfigService(db)
    setting = await service.get_setting(setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return setting


@router.put("/settings/{setting_id}", response_model=TenantSettingsResponse)
async def update_setting(
    setting_id: UUID,
    data: TenantSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantSettingsResponse:
    """Atualiza configuração."""
    service = ConfigService(db)
    setting = await service.update_setting(setting_id, data)
    if not setting:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return setting


@router.put("/settings/{setting_id}/value", response_model=TenantSettingsResponse)
async def update_setting_value(
    setting_id: UUID,
    data: TenantSettingsValueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TenantSettingsResponse:
    """Atualiza valor da configuração."""
    service = ConfigService(db)
    setting = await service.get_setting(setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    setting = await service.set_setting_value(setting.tenant_id, setting.chave, data.valor)
    return setting


@router.post("/settings/{setting_id}/reset", response_model=TenantSettingsResponse)
async def reset_setting(
    setting_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantSettingsResponse:
    """Reseta configuração para valor padrão."""
    service = ConfigService(db)
    setting = await service.reset_setting(setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return setting


@router.delete("/settings/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(
    setting_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> None:
    """Remove configuração."""
    service = ConfigService(db)
    deleted = await service.delete_setting(setting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")


# ==================== SystemConfig Endpoints ====================
@router.get("/system", response_model=SystemConfigList)
async def list_system_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    scope: str | None = None,
    category: str | None = None,
    admin_only: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> SystemConfigList:
    """Lista configurações globais."""
    service = ConfigService(db)
    items, total = await service.list_system_configs(
        scope=scope, category=category, admin_only=admin_only, skip=skip, limit=limit
    )
    return SystemConfigList(items=items, total=total)


@router.post("/system", response_model=SystemConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_system_config(
    data: SystemConfigCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> SystemConfigResponse:
    """Cria configuração global."""
    service = ConfigService(db)
    return await service.create_system_config(data)


@router.get("/system/{config_id}", response_model=SystemConfigResponse)
async def get_system_config(
    config_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> SystemConfigResponse:
    """Busca configuração global por ID."""
    service = ConfigService(db)
    config = await service.get_system_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return config


@router.put("/system/{config_id}", response_model=SystemConfigResponse)
async def update_system_config(
    config_id: UUID,
    data: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> SystemConfigResponse:
    """Atualiza configuração global."""
    service = ConfigService(db)
    config = await service.update_system_config(config_id, data)
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return config


@router.delete("/system/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_config(
    config_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> None:
    """Remove configuração global."""
    service = ConfigService(db)
    deleted = await service.delete_system_config(config_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")


# ==================== FeatureFlag Endpoints ====================
@router.get("/flags", response_model=FeatureFlagList)
async def list_feature_flags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str | None = None,
    flag_type: str | None = None,
    category: str | None = None,
    owner_team: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> FeatureFlagList:
    """Lista feature flags."""
    service = ConfigService(db)
    items, total = await service.list_feature_flags(
        status=status, flag_type=flag_type, category=category, owner_team=owner_team, skip=skip, limit=limit
    )
    return FeatureFlagList(items=items, total=total, skip=skip, limit=limit)


@router.post("/flags", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_flag(
    data: FeatureFlagCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> FeatureFlagResponse:
    """Cria feature flag."""
    service = ConfigService(db)
    return await service.create_feature_flag(data)


@router.get("/flags/{flag_id}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    flag_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> FeatureFlagResponse:
    """Busca feature flag por ID."""
    service = ConfigService(db)
    flag = await service.get_feature_flag(flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")
    return flag


@router.put("/flags/{flag_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_id: UUID,
    data: FeatureFlagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> FeatureFlagResponse:
    """Atualiza feature flag."""
    service = ConfigService(db)
    flag = await service.update_feature_flag(flag_id, data)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")
    return flag


@router.post("/flags/{flag_id}/enable", response_model=FeatureFlagResponse)
async def enable_feature_flag(
    flag_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> FeatureFlagResponse:
    """Habilita feature flag."""
    service = ConfigService(db)
    flag = await service.enable_flag(flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")
    return flag


@router.post("/flags/{flag_id}/disable", response_model=FeatureFlagResponse)
async def disable_feature_flag(
    flag_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> FeatureFlagResponse:
    """Desabilita feature flag."""
    service = ConfigService(db)
    flag = await service.disable_flag(flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")
    return flag


@router.post("/flags/{flag_id}/percentage", response_model=FeatureFlagResponse)
async def set_flag_percentage(
    flag_id: UUID,
    percentage: float = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> FeatureFlagResponse:
    """Define percentual de rollout."""
    service = ConfigService(db)
    flag = await service.set_flag_percentage(flag_id, percentage)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")
    return flag


@router.post("/flags/{flag_id}/gradual-rollout", response_model=FeatureFlagResponse)
async def start_gradual_rollout(
    flag_id: UUID,
    data: FeatureFlagGradualRollout,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> FeatureFlagResponse:
    """Inicia rollout gradual."""
    service = ConfigService(db)
    flag = await service.start_gradual_rollout(flag_id, data)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")
    return flag


@router.post("/flags/{flag_id}/toggle-tenant", response_model=FeatureFlagResponse)
async def toggle_flag_for_tenant(
    flag_id: UUID,
    data: FeatureFlagTenantToggle,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> FeatureFlagResponse:
    """Toggle de flag para tenant."""
    service = ConfigService(db)
    if data.enabled:
        flag = await service.enable_flag_for_tenant(flag_id, data.tenant_id)
    else:
        flag = await service.disable_flag_for_tenant(flag_id, data.tenant_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")
    return flag


@router.post("/flags/evaluate", response_model=FeatureFlagEvaluateResponse)
async def evaluate_feature_flag(
    data: FeatureFlagEvaluate,
    codigo: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> FeatureFlagEvaluateResponse:
    """Avalia feature flag."""
    service = ConfigService(db)
    enabled, variant = await service.evaluate_flag(
        codigo=codigo, tenant_id=data.tenant_id, user_id=data.user_id, attributes=data.attributes
    )
    return FeatureFlagEvaluateResponse(enabled=enabled, variant=variant)


@router.delete("/flags/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_flag(
    flag_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> None:
    """Remove feature flag."""
    service = ConfigService(db)
    deleted = await service.delete_feature_flag(flag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feature flag não encontrada")


# ==================== NotificationTemplate Endpoints ====================
@router.get("/templates", response_model=NotificationTemplateList)
async def list_notification_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: UUID | None = None,
    channel: str | None = None,
    notification_type: str | None = None,
    status: str | None = None,
    category: str | None = None,
    include_global: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> NotificationTemplateList:
    """Lista templates de notificação."""
    service = ConfigService(db)
    items, total = await service.list_notification_templates(
        tenant_id=tenant_id,
        channel=channel,
        notification_type=notification_type,
        status=status,
        category=category,
        include_global=include_global,
        skip=skip,
        limit=limit,
    )
    return NotificationTemplateList(items=items, total=total, skip=skip, limit=limit)


@router.post("/templates", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_template(
    data: NotificationTemplateCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> NotificationTemplateResponse:
    """Cria template de notificação."""
    service = ConfigService(db)
    return await service.create_notification_template(data)


@router.get("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def get_notification_template(
    template_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> NotificationTemplateResponse:
    """Busca template por ID."""
    service = ConfigService(db)
    template = await service.get_notification_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return template


@router.put("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def update_notification_template(
    template_id: UUID,
    data: NotificationTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> NotificationTemplateResponse:
    """Atualiza template."""
    service = ConfigService(db)
    template = await service.update_notification_template(template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return template


@router.post("/templates/{template_id}/activate", response_model=NotificationTemplateResponse)
async def activate_notification_template(
    template_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> NotificationTemplateResponse:
    """Ativa template."""
    service = ConfigService(db)
    template = await service.activate_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return template


@router.post("/templates/{template_id}/deactivate", response_model=NotificationTemplateResponse)
async def deactivate_notification_template(
    template_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> NotificationTemplateResponse:
    """Desativa template."""
    service = ConfigService(db)
    template = await service.deactivate_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return template


@router.post("/templates/{template_id}/render", response_model=NotificationTemplateRenderResponse)
async def render_notification_template(
    template_id: UUID,
    data: NotificationTemplateRender,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> NotificationTemplateRenderResponse:
    """Renderiza template com variáveis."""
    service = ConfigService(db)
    try:
        result = await service.render_template(template_id, data.variables)
        return NotificationTemplateRenderResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/templates/{template_id}/clone", response_model=NotificationTemplateResponse)
async def clone_notification_template(
    template_id: UUID,
    new_codigo: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> NotificationTemplateResponse:
    """Clona template."""
    service = ConfigService(db)
    template = await service.clone_template(template_id, new_codigo)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_template(
    template_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> None:
    """Remove template."""
    service = ConfigService(db)
    deleted = await service.delete_notification_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template não encontrado")


# ==================== Dashboard Endpoints ====================
@router.get("/dashboard", response_model=ConfigDashboard)
async def get_config_dashboard(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> ConfigDashboard:
    """Retorna dashboard de configurações."""
    service = ConfigService(db)
    return await service.get_config_dashboard()


@router.get("/tenants/{tenant_id}/dashboard", response_model=TenantDashboard)
async def get_tenant_dashboard(
    tenant_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
) -> TenantDashboard:
    """Retorna dashboard do tenant."""
    service = ConfigService(db)
    dashboard = await service.get_tenant_dashboard(tenant_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return dashboard
