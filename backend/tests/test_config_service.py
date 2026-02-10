"""
Testes do Service do módulo Config
Sprint 35: Configurações e Multi-tenant
"""

# pylint: disable=redefined-outer-name,unused-argument
import uuid
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.config.models import (
    ConfigPriority,
    ConfigScope,
    FeatureFlag,
    FlagStatus,
    FlagType,
    NotificationChannel,
    NotificationTemplate,
    NotificationType,
    RolloutStrategy,
    SettingCategory,
    SettingType,
    SystemConfig,
    TemplateStatus,
    Tenant,
    TenantPlan,
    TenantSettings,
    TenantStatus,
    TenantType,
)
from modules.config.schemas import (
    FeatureFlagCreate,
    FeatureFlagGradualRollout,
    NotificationTemplateCreate,
    SystemConfigCreate,
    TenantCreate,
    TenantSettingsCreate,
    TenantUpdate,
)
from modules.config.services import ConfigService


@pytest.fixture
def mock_db():
    """Fixture para mock do banco de dados."""
    db = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.add = MagicMock()
    db.delete = MagicMock()
    return db


@pytest.fixture
def config_service(mock_db):
    """Fixture para instância do service."""
    return ConfigService(mock_db)


@pytest.fixture
def sample_tenant():
    """Fixture para tenant de exemplo."""
    return Tenant(
        id=uuid.uuid4(),
        codigo="TEST001",
        nome="Empresa Teste",
        cnpj="12345678000199",
        email="teste@empresa.com",
        status=TenantStatus.ATIVO,
        plan=TenantPlan.PROFESSIONAL,
        tenant_type=TenantType.EMPRESA,
        max_usuarios=50,
        max_storage_gb=100,
        usuarios_ativos=10,
        storage_usado_mb=500,
        api_calls_mes=1000,
        max_api_calls_month=10000,
        features_enabled=["reports"],
        modules_enabled=["crm"],
        ativo=True,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_setting():
    """Fixture para setting de exemplo."""
    return TenantSettings(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        chave="notifications_enabled",
        nome="Notifications Enabled",
        valor="true",
        category=SettingCategory.NOTIFICACAO,
        setting_type=SettingType.BOOLEAN,
        ativo=True,
        history=[],
    )


@pytest.fixture
def sample_config():
    """Fixture para config de exemplo."""
    return SystemConfig(
        id=uuid.uuid4(),
        chave="app_version",
        nome="App Version",
        valor="2.0.0",
        valor_type="STRING",
        scope=ConfigScope.GLOBAL,
        priority=ConfigPriority.NORMAL,
        ativo=True,
        history=[],
    )


@pytest.fixture
def sample_flag():
    """Fixture para flag de exemplo."""
    return FeatureFlag(
        id=uuid.uuid4(),
        codigo="NEW_FEATURE",
        nome="Nova Feature",
        status=FlagStatus.ATIVO,
        flag_type=FlagType.RELEASE,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=50,
        enabled_tenants=[],
        disabled_tenants=[],
        enabled_users=[],
        disabled_users=[],
        tags=[],
        depends_on=[],
        evaluation_count=0,
        enabled_count=0,
        disabled_count=0,
        ativo=True,
    )


@pytest.fixture
def sample_template():
    """Fixture para template de exemplo."""
    return NotificationTemplate(
        id=uuid.uuid4(),
        codigo="ALERT_EMAIL",
        nome="Email de Alerta",
        notification_type=NotificationType.ALERTA,
        status=TemplateStatus.ATIVO,
        email_subject="Alerta: {{tipo}}",
        email_body_html="<p>Atenção: {{mensagem}}</p>",
        email_body_text="Atenção: {{mensagem}}",
        available_variables=[
            {"name": "tipo", "description": "Tipo do alerta", "required": True},
            {"name": "mensagem", "description": "Mensagem do alerta", "required": True},
        ],
        language="pt-BR",
        priority=1,
        send_delay_minutes=0,
        batch_size=1,
        track_opens=True,
        track_clicks=True,
        track_delivery=True,
        sent_count=0,
        delivered_count=0,
        opened_count=0,
        clicked_count=0,
        bounced_count=0,
        unsubscribed_count=0,
        version=1,
        tags=[],
        ativo=True,
    )


class TestConfigServiceTenant:
    """Testes do ConfigService para Tenant."""

    @pytest.mark.asyncio
    async def test_create_tenant(self, config_service, mock_db):
        """Testa criação de tenant."""
        with patch.object(config_service.repository, "create_tenant") as mock_create:
            tenant = Tenant(
                id=uuid.uuid4(),
                codigo="NEW001",
                nome="Novo Tenant",
                cnpj="12345678000199",
                email="novo@tenant.com",
            )
            mock_create.return_value = tenant

            data = TenantCreate(
                codigo="NEW001",
                nome="Novo Tenant",
                cnpj="12345678000199",
                email="novo@tenant.com",
                plan="starter",
                tenant_type="empresa",
            )
            result = await config_service.create_tenant(data)

            assert result.codigo == "NEW001"
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tenant(self, config_service, sample_tenant):
        """Testa busca de tenant."""
        with patch.object(config_service.repository, "get_tenant_by_id") as mock_get:
            mock_get.return_value = sample_tenant

            result = await config_service.get_tenant(sample_tenant.id)

            assert result == sample_tenant
            mock_get.assert_called_once_with(sample_tenant.id)

    @pytest.mark.asyncio
    async def test_list_tenants(self, config_service, sample_tenant):
        """Testa listagem de tenants."""
        with patch.object(config_service.repository, "list_tenants") as mock_list:
            mock_list.return_value = ([sample_tenant], 1)

            tenants, total = await config_service.list_tenants()

            assert len(tenants) == 1
            assert total == 1

    @pytest.mark.asyncio
    async def test_update_tenant(self, config_service, sample_tenant):
        """Testa atualização de tenant."""
        with (
            patch.object(config_service.repository, "get_tenant_by_id") as mock_get,
            patch.object(config_service.repository, "update_tenant") as mock_update,
        ):
            mock_get.return_value = sample_tenant
            sample_tenant.nome = "Tenant Atualizado"
            mock_update.return_value = sample_tenant

            data = TenantUpdate(nome="Tenant Atualizado")
            result = await config_service.update_tenant(sample_tenant.id, data)

            assert result.nome == "Tenant Atualizado"

    @pytest.mark.asyncio
    async def test_activate_tenant(self, config_service, sample_tenant):
        """Testa ativação de tenant."""
        sample_tenant.status = TenantStatus.INATIVO
        with (
            patch.object(config_service.repository, "get_tenant_by_id") as mock_get,
            patch.object(config_service.repository, "update_tenant") as mock_update,
        ):
            mock_get.return_value = sample_tenant
            sample_tenant.status = TenantStatus.ATIVO
            mock_update.return_value = sample_tenant

            result = await config_service.activate_tenant(sample_tenant.id)

            assert result.status == TenantStatus.ATIVO

    @pytest.mark.asyncio
    async def test_suspend_tenant(self, config_service, sample_tenant):
        """Testa suspensão de tenant."""
        with (
            patch.object(config_service.repository, "get_tenant_by_id") as mock_get,
            patch.object(config_service.repository, "update_tenant") as mock_update,
        ):
            mock_get.return_value = sample_tenant
            sample_tenant.status = TenantStatus.SUSPENSO
            mock_update.return_value = sample_tenant

            result = await config_service.suspend_tenant(
                sample_tenant.id,
                reason="Teste",
            )

            assert result.status == TenantStatus.SUSPENSO

    @pytest.mark.asyncio
    async def test_cancel_tenant(self, config_service, sample_tenant):
        """Testa cancelamento de tenant."""
        with (
            patch.object(config_service.repository, "get_tenant_by_id") as mock_get,
            patch.object(config_service.repository, "update_tenant") as mock_update,
        ):
            mock_get.return_value = sample_tenant
            sample_tenant.status = TenantStatus.CANCELADO
            mock_update.return_value = sample_tenant

            result = await config_service.cancel_tenant(sample_tenant.id)

            assert result.status == TenantStatus.CANCELADO


class TestConfigServiceSettings:
    """Testes do ConfigService para TenantSettings."""

    @pytest.mark.asyncio
    async def test_create_setting(self, config_service, sample_setting):
        """Testa criação de setting."""
        with patch.object(config_service.repository, "create_setting") as mock_create:
            mock_create.return_value = sample_setting

            data = TenantSettingsCreate(
                tenant_id=sample_setting.tenant_id,
                chave="notifications_enabled",
                nome="Notifications Enabled",
                category="notificacao",
                setting_type="boolean",
                valor="true",
            )
            result = await config_service.create_setting(data)

            assert result.chave == "notifications_enabled"

    @pytest.mark.asyncio
    async def test_get_setting(self, config_service, sample_setting):
        """Testa busca de setting."""
        with patch.object(config_service.repository, "get_setting_by_id") as mock_get:
            mock_get.return_value = sample_setting

            result = await config_service.get_setting(sample_setting.id)

            assert result == sample_setting

    @pytest.mark.asyncio
    async def test_update_setting_value(self, config_service, sample_setting):
        """Testa atualização de valor de setting."""
        with (
            patch.object(config_service.repository, "get_setting_by_key") as mock_get,
            patch.object(config_service.repository, "update_setting") as mock_update,
        ):
            mock_get.return_value = sample_setting
            # Use False (boolean) to set "false" string value for BOOLEAN type
            sample_setting.set_value(False)
            mock_update.return_value = sample_setting

            result = await config_service.set_setting_value(
                sample_setting.tenant_id,
                sample_setting.chave,
                valor=False,
            )

            assert result.valor == "false"

    @pytest.mark.asyncio
    async def test_reset_setting(self, config_service, sample_setting):
        """Testa reset de setting para valor padrão."""
        sample_setting.valor_default = "default_value"
        with (
            patch.object(config_service.repository, "get_setting_by_id") as mock_get,
            patch.object(config_service.repository, "update_setting") as mock_update,
        ):
            mock_get.return_value = sample_setting
            sample_setting.valor = sample_setting.valor_default
            mock_update.return_value = sample_setting

            result = await config_service.reset_setting(sample_setting.id)

            assert result.valor == "default_value"


class TestConfigServiceSystemConfig:
    """Testes do ConfigService para SystemConfig."""

    @pytest.mark.asyncio
    async def test_create_config(self, config_service, sample_config):
        """Testa criação de config."""
        with patch.object(config_service.repository, "create_system_config") as mock_create:
            mock_create.return_value = sample_config

            data = SystemConfigCreate(
                chave="app_version",
                nome="App Version",
                valor="2.0.0",
            )
            result = await config_service.create_system_config(data)

            assert result.chave == "app_version"

    @pytest.mark.asyncio
    async def test_get_config_by_key(self, config_service, sample_config):
        """Testa busca de config por chave."""
        with patch.object(config_service.repository, "get_system_config_by_key") as mock_get:
            mock_get.return_value = sample_config

            result = await config_service.get_system_config_by_key("app_version")

            assert result.valor == "2.0.0"

    @pytest.mark.asyncio
    async def test_list_configs_by_scope(self, config_service, sample_config):
        """Testa listagem de configs por escopo."""
        with patch.object(config_service.repository, "list_system_configs") as mock_list:
            mock_list.return_value = ([sample_config], 1)

            configs, total = await config_service.list_system_configs(scope=ConfigScope.GLOBAL)

            assert len(configs) == 1
            assert total == 1


class TestConfigServiceFeatureFlag:
    """Testes do ConfigService para FeatureFlag."""

    @pytest.mark.asyncio
    async def test_create_flag(self, config_service, sample_flag):
        """Testa criação de flag."""
        with patch.object(config_service.repository, "create_feature_flag") as mock_create:
            mock_create.return_value = sample_flag

            data = FeatureFlagCreate(
                codigo="NEW_FEATURE",
                nome="Nova Feature",
            )
            result = await config_service.create_feature_flag(data)

            assert result.codigo == "NEW_FEATURE"

    @pytest.mark.asyncio
    async def test_enable_flag(self, config_service, sample_flag):
        """Testa ativação de flag."""
        sample_flag.status = FlagStatus.INATIVO
        with (
            patch.object(config_service.repository, "get_feature_flag_by_id") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.status = FlagStatus.ATIVO
            sample_flag.rollout_strategy = RolloutStrategy.ALL
            mock_update.return_value = sample_flag

            result = await config_service.enable_flag(sample_flag.id)

            assert result.status == FlagStatus.ATIVO

    @pytest.mark.asyncio
    async def test_disable_flag(self, config_service, sample_flag):
        """Testa desativação de flag."""
        with (
            patch.object(config_service.repository, "get_feature_flag_by_id") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.status = FlagStatus.INATIVO
            sample_flag.rollout_strategy = RolloutStrategy.NONE
            mock_update.return_value = sample_flag

            result = await config_service.disable_flag(sample_flag.id)

            assert result.status == FlagStatus.INATIVO

    @pytest.mark.asyncio
    async def test_set_flag_percentage(self, config_service, sample_flag):
        """Testa definir percentual de flag."""
        with (
            patch.object(config_service.repository, "get_feature_flag_by_id") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.rollout_percentage = 75
            mock_update.return_value = sample_flag

            result = await config_service.set_flag_percentage(sample_flag.id, 75)

            assert result.rollout_percentage == 75

    @pytest.mark.asyncio
    async def test_start_gradual_rollout(self, config_service, sample_flag):
        """Testa início de rollout gradual."""
        with (
            patch.object(config_service.repository, "get_feature_flag_by_id") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.rollout_strategy = RolloutStrategy.GRADUAL
            mock_update.return_value = sample_flag

            data = FeatureFlagGradualRollout(
                start_percentage=0,
                end_percentage=100,
                duration_days=10,
            )
            result = await config_service.start_gradual_rollout(sample_flag.id, data)

            assert result.rollout_strategy == RolloutStrategy.GRADUAL

    @pytest.mark.asyncio
    async def test_enable_flag_for_tenant(self, config_service, sample_flag):
        """Testa habilitar flag para tenant."""
        tenant_id = str(uuid.uuid4())
        with (
            patch.object(config_service.repository, "get_feature_flag_by_id") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.enabled_tenants.append(tenant_id)
            mock_update.return_value = sample_flag

            result = await config_service.enable_flag_for_tenant(
                sample_flag.id,
                tenant_id=tenant_id,
            )

            assert tenant_id in result.enabled_tenants

    @pytest.mark.asyncio
    async def test_evaluate_flag(self, config_service, sample_flag):
        """Testa avaliação de flag."""
        with (
            patch.object(config_service.repository, "get_feature_flag_by_codigo") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            mock_update.return_value = sample_flag

            enabled, variant = await config_service.evaluate_flag(
                sample_flag.codigo,
                tenant_id=str(uuid.uuid4()),
                user_id="user123",
            )

            assert isinstance(enabled, bool)


class TestConfigServiceNotificationTemplate:
    """Testes do ConfigService para NotificationTemplate."""

    @pytest.mark.asyncio
    async def test_create_template(self, config_service, sample_template):
        """Testa criação de template."""
        with patch.object(config_service.repository, "create_notification_template") as mock_create:
            mock_create.return_value = sample_template

            data = NotificationTemplateCreate(
                codigo="ALERT_EMAIL",
                nome="Email de Alerta",
                notification_type="alerta",
            )
            result = await config_service.create_notification_template(data)

            assert result.codigo == "ALERT_EMAIL"

    @pytest.mark.asyncio
    async def test_activate_template(self, config_service, sample_template):
        """Testa ativação de template."""
        sample_template.status = TemplateStatus.RASCUNHO
        with (
            patch.object(config_service.repository, "get_notification_template_by_id") as mock_get,
            patch.object(config_service.repository, "update_notification_template") as mock_update,
        ):
            mock_get.return_value = sample_template
            sample_template.status = TemplateStatus.ATIVO
            mock_update.return_value = sample_template

            result = await config_service.activate_template(sample_template.id)

            assert result.status == TemplateStatus.ATIVO

    @pytest.mark.asyncio
    async def test_deactivate_template(self, config_service, sample_template):
        """Testa desativação de template."""
        with (
            patch.object(config_service.repository, "get_notification_template_by_id") as mock_get,
            patch.object(config_service.repository, "update_notification_template") as mock_update,
        ):
            mock_get.return_value = sample_template
            sample_template.status = TemplateStatus.INATIVO
            mock_update.return_value = sample_template

            result = await config_service.deactivate_template(sample_template.id)

            assert result.status == TemplateStatus.INATIVO

    @pytest.mark.asyncio
    async def test_render_template(self, config_service, sample_template):
        """Testa renderização de template."""
        with patch.object(config_service.repository, "get_notification_template_by_id") as mock_get:
            mock_get.return_value = sample_template

            result = await config_service.render_template(
                sample_template.id,
                variables={"tipo": "Urgente", "mensagem": "Sistema fora do ar"},
            )

            assert "Urgente" in result["subject"]
            assert "Sistema fora do ar" in result["body_html"]

    @pytest.mark.asyncio
    async def test_clone_template(self, config_service, sample_template):
        """Testa clonagem de template."""
        with (
            patch.object(config_service.repository, "get_notification_template_by_id") as mock_get,
            patch.object(config_service.repository, "create_notification_template") as mock_create,
        ):
            mock_get.return_value = sample_template
            cloned = NotificationTemplate(
                id=uuid.uuid4(),
                codigo="ALERT_EMAIL_V2",
                nome="Email de Alerta V2",
                notification_type=sample_template.notification_type,
                email_body_html=sample_template.email_body_html,
                status=TemplateStatus.RASCUNHO,
                version=1,
                parent_template_id=sample_template.id,
                priority=1,
                send_delay_minutes=0,
                batch_size=1,
                track_opens=True,
                track_clicks=True,
                track_delivery=True,
                sent_count=0,
                delivered_count=0,
                opened_count=0,
                clicked_count=0,
                bounced_count=0,
                unsubscribed_count=0,
                language="pt-BR",
            )
            mock_create.return_value = cloned

            result = await config_service.clone_template(
                sample_template.id,
                new_codigo="ALERT_EMAIL_V2",
            )

            assert result.codigo == "ALERT_EMAIL_V2"
            assert result.parent_template_id == sample_template.id


class TestConfigServiceDashboard:
    """Testes do ConfigService para Dashboard."""

    @pytest.mark.asyncio
    async def test_get_config_dashboard(self, config_service):
        """Testa obtenção do dashboard de configurações."""
        config_service.repository.get_config_dashboard_stats = AsyncMock(
            return_value={
                "total_tenants": 100,
                "active_tenants": 90,
                "trial_tenants": 10,
                "suspended_tenants": 5,
                "total_configs": 50,
                "total_feature_flags": 30,
                "active_feature_flags": 25,
                "total_notification_templates": 40,
            }
        )
        config_service.repository.get_recent_tenants = AsyncMock(return_value=[])

        result = await config_service.get_config_dashboard()

        assert result.total_tenants == 100

    @pytest.mark.asyncio
    async def test_get_tenant_dashboard(self, config_service, sample_tenant):
        """Testa obtenção do dashboard de tenant."""
        with (
            patch.object(config_service.repository, "get_tenant_by_id") as mock_get,
            patch.object(config_service.repository, "list_tenant_settings") as mock_list_settings,
            patch.object(config_service.repository, "list_notification_templates") as mock_list_templates,
        ):
            mock_get.return_value = sample_tenant
            mock_list_settings.return_value = ([], 0)
            mock_list_templates.return_value = ([], 0)

            result = await config_service.get_tenant_dashboard(sample_tenant.id)

            assert result.tenant.codigo == sample_tenant.codigo


class TestConfigServiceValidation:
    """Testes de validação do ConfigService."""

    @pytest.mark.asyncio
    async def test_validate_tenant_codigo_unico(self, config_service, sample_tenant):
        """Testa validação de código único de tenant."""
        with patch.object(config_service.repository, "get_tenant_by_codigo") as mock_get:
            mock_get.return_value = sample_tenant

            # Se código já existe, deve retornar o tenant existente
            result = await config_service.get_tenant_by_codigo(sample_tenant.codigo)

            assert result is not None
            assert result.codigo == sample_tenant.codigo

    @pytest.mark.asyncio
    async def test_validate_flag_codigo_unico(self, config_service, sample_flag):
        """Testa validação de código único de flag."""
        with patch.object(config_service.repository, "get_feature_flag_by_codigo") as mock_get:
            mock_get.return_value = sample_flag

            result = await config_service.get_feature_flag_by_codigo(sample_flag.codigo)

            assert result is not None
            assert result.codigo == sample_flag.codigo

    @pytest.mark.asyncio
    async def test_validate_setting_chave_unica_por_tenant(self, config_service, sample_setting):
        """Testa validação de chave única por tenant."""
        with patch.object(config_service.repository, "get_setting_by_key") as mock_get:
            mock_get.return_value = sample_setting

            result = await config_service.get_setting_by_key(
                sample_setting.tenant_id,
                sample_setting.chave,
            )

            assert result is not None
            assert result.chave == sample_setting.chave
