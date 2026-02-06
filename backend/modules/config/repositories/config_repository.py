"""
ConfigRepository - Repositório para Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""
# pylint: disable=too-many-public-methods,singleton-comparison

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.config.models import (
    Tenant,
    TenantSettings,
    SystemConfig,
    FeatureFlag,
    NotificationTemplate,
    TenantStatus,
    TenantPlan,
    TenantType,
    SettingCategory,
    ConfigScope,
    FlagStatus,
    FlagType,
    NotificationChannel,
    NotificationType,
    TemplateStatus,
)

logger = logging.getLogger(__name__)


class ConfigRepository:
    """Repositório para operações de configurações e multi-tenant."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Tenant ====================

    async def create_tenant(self, tenant: Tenant) -> Tenant:
        """Cria um novo tenant."""
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant

    async def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Busca tenant por ID."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_tenant_by_codigo(self, codigo: str) -> Optional[Tenant]:
        """Busca tenant por código."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.codigo == codigo)
        )
        return result.scalar_one_or_none()

    async def get_tenant_by_cnpj(self, cnpj: str) -> Optional[Tenant]:
        """Busca tenant por CNPJ."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.cnpj == cnpj)
        )
        return result.scalar_one_or_none()

    async def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Busca tenant por domínio ou subdomínio."""
        result = await self.db.execute(
            select(Tenant).where(
                or_(
                    Tenant.dominio_personalizado == domain,
                    Tenant.subdominio == domain
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_tenants(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TenantStatus = None,
        plan: TenantPlan = None,
        tenant_type: TenantType = None,
        search: str = None,
        ativo: bool = True
    ) -> Tuple[List[Tenant], int]:
        """Lista tenants com filtros."""
        query = select(Tenant).where(Tenant.ativo == ativo)

        if status:
            query = query.where(Tenant.status == status)
        if plan:
            query = query.where(Tenant.plan == plan)
        if tenant_type:
            query = query.where(Tenant.tenant_type == tenant_type)
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Tenant.nome.ilike(search_filter),
                    Tenant.codigo.ilike(search_filter),
                    Tenant.email.ilike(search_filter),
                    Tenant.cnpj.ilike(search_filter)
                )
            )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()

        # Results
        query = query.order_by(Tenant.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_tenant(self, tenant: Tenant) -> Tenant:
        """Atualiza tenant."""
        tenant.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant

    async def delete_tenant(self, tenant_id: UUID) -> bool:
        """Remove tenant (soft delete)."""
        tenant = await self.get_tenant_by_id(tenant_id)
        if tenant:
            tenant.ativo = False
            tenant.status = TenantStatus.CANCELADO
            tenant.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def get_active_tenants_count(self) -> int:
        """Conta tenants ativos."""
        result = await self.db.execute(
            select(func.count(Tenant.id)).where(
                and_(
                    Tenant.status == TenantStatus.ATIVO,
                    Tenant.ativo == True
                )
            )
        )
        return result.scalar() or 0

    async def get_trial_tenants(self) -> List[Tenant]:
        """Lista tenants em trial."""
        result = await self.db.execute(
            select(Tenant).where(
                and_(
                    Tenant.status == TenantStatus.TRIAL,
                    Tenant.ativo == True
                )
            ).order_by(Tenant.trial_ends_at)
        )
        return list(result.scalars().all())

    async def get_expiring_trials(self, days: int = 7) -> List[Tenant]:
        """Lista trials expirando em X dias."""
        cutoff = datetime.utcnow() + timedelta(days=days)
        result = await self.db.execute(
            select(Tenant).where(
                and_(
                    Tenant.status == TenantStatus.TRIAL,
                    Tenant.trial_ends_at <= cutoff,
                    Tenant.trial_ends_at > datetime.utcnow(),
                    Tenant.ativo == True
                )
            ).order_by(Tenant.trial_ends_at)
        )
        return list(result.scalars().all())

    # ==================== TenantSettings ====================

    async def create_setting(self, setting: TenantSettings) -> TenantSettings:
        """Cria configuração de tenant."""
        self.db.add(setting)
        await self.db.commit()
        await self.db.refresh(setting)
        return setting

    async def get_setting_by_id(self, setting_id: UUID) -> Optional[TenantSettings]:
        """Busca configuração por ID."""
        result = await self.db.execute(
            select(TenantSettings).where(TenantSettings.id == setting_id)
        )
        return result.scalar_one_or_none()

    async def get_setting_by_key(
        self,
        tenant_id: UUID,
        chave: str
    ) -> Optional[TenantSettings]:
        """Busca configuração por chave."""
        result = await self.db.execute(
            select(TenantSettings).where(
                and_(
                    TenantSettings.tenant_id == tenant_id,
                    TenantSettings.chave == chave
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_tenant_settings(
        self,
        tenant_id: UUID,
        category: SettingCategory = None,
        group: str = None,
        visible: bool = None
    ) -> Tuple[List[TenantSettings], int]:
        """Lista configurações do tenant."""
        query = select(TenantSettings).where(
            and_(
                TenantSettings.tenant_id == tenant_id,
                TenantSettings.ativo == True
            )
        )

        if category:
            query = query.where(TenantSettings.category == category)
        if group:
            query = query.where(TenantSettings.group == group)
        if visible is not None:
            query = query.where(TenantSettings.visible == visible)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()

        # Results
        query = query.order_by(
            TenantSettings.category,
            TenantSettings.group,
            TenantSettings.display_order
        )
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_setting(self, setting: TenantSettings) -> TenantSettings:
        """Atualiza configuração."""
        setting.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(setting)
        return setting

    async def delete_setting(self, setting_id: UUID) -> bool:
        """Remove configuração."""
        setting = await self.get_setting_by_id(setting_id)
        if setting:
            setting.ativo = False
            setting.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def get_settings_by_category(
        self,
        tenant_id: UUID,
        category: SettingCategory
    ) -> List[TenantSettings]:
        """Lista configurações por categoria."""
        result = await self.db.execute(
            select(TenantSettings).where(
                and_(
                    TenantSettings.tenant_id == tenant_id,
                    TenantSettings.category == category,
                    TenantSettings.ativo == True
                )
            ).order_by(TenantSettings.display_order)
        )
        return list(result.scalars().all())

    # ==================== SystemConfig ====================

    async def create_system_config(self, config: SystemConfig) -> SystemConfig:
        """Cria configuração global."""
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def get_system_config_by_id(
        self,
        config_id: UUID
    ) -> Optional[SystemConfig]:
        """Busca configuração global por ID."""
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    async def get_system_config_by_key(self, chave: str) -> Optional[SystemConfig]:
        """Busca configuração global por chave."""
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.chave == chave)
        )
        return result.scalar_one_or_none()

    async def list_system_configs(
        self,
        scope: ConfigScope = None,
        category: str = None,
        admin_only: bool = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SystemConfig], int]:
        """Lista configurações globais."""
        query = select(SystemConfig).where(SystemConfig.ativo == True)

        if scope:
            query = query.where(SystemConfig.scope == scope)
        if category:
            query = query.where(SystemConfig.category == category)
        if admin_only is not None:
            query = query.where(SystemConfig.admin_only == admin_only)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()

        # Results
        query = query.order_by(SystemConfig.category, SystemConfig.display_order)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_system_config(self, config: SystemConfig) -> SystemConfig:
        """Atualiza configuração global."""
        config.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def delete_system_config(self, config_id: UUID) -> bool:
        """Remove configuração global."""
        config = await self.get_system_config_by_id(config_id)
        if config:
            config.ativo = False
            config.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def get_cacheable_configs(self) -> List[SystemConfig]:
        """Lista configurações cacheáveis."""
        result = await self.db.execute(
            select(SystemConfig).where(
                and_(
                    SystemConfig.cacheable == True,
                    SystemConfig.ativo == True
                )
            )
        )
        return list(result.scalars().all())

    # ==================== FeatureFlag ====================

    async def create_feature_flag(self, flag: FeatureFlag) -> FeatureFlag:
        """Cria feature flag."""
        self.db.add(flag)
        await self.db.commit()
        await self.db.refresh(flag)
        return flag

    async def get_feature_flag_by_id(
        self,
        flag_id: UUID
    ) -> Optional[FeatureFlag]:
        """Busca feature flag por ID."""
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.id == flag_id)
        )
        return result.scalar_one_or_none()

    async def get_feature_flag_by_codigo(
        self,
        codigo: str
    ) -> Optional[FeatureFlag]:
        """Busca feature flag por código."""
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.codigo == codigo)
        )
        return result.scalar_one_or_none()

    async def list_feature_flags(
        self,
        status: FlagStatus = None,
        flag_type: FlagType = None,
        category: str = None,
        owner_team: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[FeatureFlag], int]:
        """Lista feature flags."""
        query = select(FeatureFlag).where(FeatureFlag.ativo == True)

        if status:
            query = query.where(FeatureFlag.status == status)
        if flag_type:
            query = query.where(FeatureFlag.flag_type == flag_type)
        if category:
            query = query.where(FeatureFlag.category == category)
        if owner_team:
            query = query.where(FeatureFlag.owner_team == owner_team)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()

        # Results
        query = query.order_by(FeatureFlag.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_feature_flag(self, flag: FeatureFlag) -> FeatureFlag:
        """Atualiza feature flag."""
        flag.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(flag)
        return flag

    async def delete_feature_flag(self, flag_id: UUID) -> bool:
        """Remove feature flag."""
        flag = await self.get_feature_flag_by_id(flag_id)
        if flag:
            flag.ativo = False
            flag.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def get_active_feature_flags(self) -> List[FeatureFlag]:
        """Lista feature flags ativas."""
        result = await self.db.execute(
            select(FeatureFlag).where(
                and_(
                    FeatureFlag.status == FlagStatus.ATIVO,
                    FeatureFlag.ativo == True
                )
            )
        )
        return list(result.scalars().all())

    async def get_scheduled_flags(self) -> List[FeatureFlag]:
        """Lista flags com agendamento pendente."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(FeatureFlag).where(
                and_(
                    FeatureFlag.ativo == True,
                    or_(
                        and_(
                            FeatureFlag.scheduled_enable_at != None,
                            FeatureFlag.scheduled_enable_at <= now
                        ),
                        and_(
                            FeatureFlag.scheduled_disable_at != None,
                            FeatureFlag.scheduled_disable_at <= now
                        )
                    )
                )
            )
        )
        return list(result.scalars().all())

    # ==================== NotificationTemplate ====================

    async def create_notification_template(
        self,
        template: NotificationTemplate
    ) -> NotificationTemplate:
        """Cria template de notificação."""
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_notification_template_by_id(
        self,
        template_id: UUID
    ) -> Optional[NotificationTemplate]:
        """Busca template por ID."""
        result = await self.db.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.id == template_id
            )
        )
        return result.scalar_one_or_none()

    async def get_notification_template_by_codigo(
        self,
        tenant_id: UUID,
        codigo: str
    ) -> Optional[NotificationTemplate]:
        """Busca template por código (tenant ou global)."""
        # Primeiro busca específico do tenant
        result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.tenant_id == tenant_id,
                    NotificationTemplate.codigo == codigo,
                    NotificationTemplate.ativo == True
                )
            )
        )
        template = result.scalar_one_or_none()

        if not template:
            # Se não encontrou, busca global
            result = await self.db.execute(
                select(NotificationTemplate).where(
                    and_(
                        NotificationTemplate.tenant_id == None,
                        NotificationTemplate.codigo == codigo,
                        NotificationTemplate.ativo == True
                    )
                )
            )
            template = result.scalar_one_or_none()

        return template

    async def list_notification_templates(
        self,
        tenant_id: UUID = None,
        channel: NotificationChannel = None,
        notification_type: NotificationType = None,
        status: TemplateStatus = None,
        category: str = None,
        include_global: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[NotificationTemplate], int]:
        """Lista templates de notificação."""
        query = select(NotificationTemplate).where(
            NotificationTemplate.ativo == True
        )

        # Filtro de tenant
        if tenant_id:
            if include_global:
                query = query.where(
                    or_(
                        NotificationTemplate.tenant_id == tenant_id,
                        NotificationTemplate.tenant_id == None
                    )
                )
            else:
                query = query.where(
                    NotificationTemplate.tenant_id == tenant_id
                )
        else:
            # Apenas globais
            query = query.where(NotificationTemplate.tenant_id == None)

        if channel:
            query = query.where(NotificationTemplate.channel == channel)
        if notification_type:
            query = query.where(
                NotificationTemplate.notification_type == notification_type
            )
        if status:
            query = query.where(NotificationTemplate.status == status)
        if category:
            query = query.where(NotificationTemplate.category == category)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()

        # Results
        query = query.order_by(
            NotificationTemplate.channel,
            NotificationTemplate.notification_type,
            NotificationTemplate.nome
        )
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_notification_template(
        self,
        template: NotificationTemplate
    ) -> NotificationTemplate:
        """Atualiza template."""
        template.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def delete_notification_template(self, template_id: UUID) -> bool:
        """Remove template."""
        template = await self.get_notification_template_by_id(template_id)
        if template:
            template.ativo = False
            template.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    async def get_active_templates_by_channel(
        self,
        channel: NotificationChannel,
        tenant_id: UUID = None
    ) -> List[NotificationTemplate]:
        """Lista templates ativos por canal."""
        query = select(NotificationTemplate).where(
            and_(
                NotificationTemplate.channel == channel,
                NotificationTemplate.status == TemplateStatus.ATIVO,
                NotificationTemplate.ativo == True
            )
        )

        if tenant_id:
            query = query.where(
                or_(
                    NotificationTemplate.tenant_id == tenant_id,
                    NotificationTemplate.tenant_id == None
                )
            )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ==================== Dashboard Stats ====================

    async def get_config_dashboard_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas para dashboard."""
        # Tenants
        total_tenants = await self.db.execute(
            select(func.count(Tenant.id)).where(Tenant.ativo == True)
        )
        active_tenants = await self.db.execute(
            select(func.count(Tenant.id)).where(
                and_(
                    Tenant.status == TenantStatus.ATIVO,
                    Tenant.ativo == True
                )
            )
        )
        trial_tenants = await self.db.execute(
            select(func.count(Tenant.id)).where(
                and_(
                    Tenant.status == TenantStatus.TRIAL,
                    Tenant.ativo == True
                )
            )
        )
        suspended_tenants = await self.db.execute(
            select(func.count(Tenant.id)).where(
                and_(
                    Tenant.status.in_([
                        TenantStatus.SUSPENSO,
                        TenantStatus.BLOQUEADO
                    ]),
                    Tenant.ativo == True
                )
            )
        )

        # Configs
        total_configs = await self.db.execute(
            select(func.count(SystemConfig.id)).where(SystemConfig.ativo == True)
        )

        # Feature Flags
        total_flags = await self.db.execute(
            select(func.count(FeatureFlag.id)).where(FeatureFlag.ativo == True)
        )
        active_flags = await self.db.execute(
            select(func.count(FeatureFlag.id)).where(
                and_(
                    FeatureFlag.status == FlagStatus.ATIVO,
                    FeatureFlag.ativo == True
                )
            )
        )

        # Templates
        total_templates = await self.db.execute(
            select(func.count(NotificationTemplate.id)).where(
                NotificationTemplate.ativo == True
            )
        )

        return {
            "total_tenants": total_tenants.scalar() or 0,
            "active_tenants": active_tenants.scalar() or 0,
            "trial_tenants": trial_tenants.scalar() or 0,
            "suspended_tenants": suspended_tenants.scalar() or 0,
            "total_configs": total_configs.scalar() or 0,
            "total_feature_flags": total_flags.scalar() or 0,
            "active_feature_flags": active_flags.scalar() or 0,
            "total_notification_templates": total_templates.scalar() or 0
        }

    async def get_recent_tenants(self, limit: int = 5) -> List[Tenant]:
        """Lista tenants recentes."""
        result = await self.db.execute(
            select(Tenant)
            .where(Tenant.ativo == True)
            .order_by(Tenant.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
