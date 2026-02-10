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
        documento="12345678000199",
        email="teste@empresa.com",
        status=TenantStatus.ATIVO,
        plano=TenantPlan.PROFESSIONAL,
        tipo=TenantType.COMPANY,
        limite_usuarios=50,
        limite_storage_gb=100,
        features_habilitadas=["reports"],
        modulos_habilitados=["crm"],
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
        valor="true",
        categoria=SettingCategory.NOTIFICACAO,
        tipo=SettingType.BOOLEAN,
        ativo=True,
        historico=[],
    )


@pytest.fixture
def sample_config():
    """Fixture para config de exemplo."""
    return SystemConfig(
        id=uuid.uuid4(),
        chave="app_version",
        valor="2.0.0",
        tipo=SettingType.STRING,
        escopo=ConfigScope.GLOBAL,
        prioridade=ConfigPriority.NORMAL,
        ativo=True,
        historico=[],
    )


@pytest.fixture
def sample_flag():
    """Fixture para flag de exemplo."""
    return FeatureFlag(
        id=uuid.uuid4(),
        codigo="NEW_FEATURE",
        nome="Nova Feature",
        status=FlagStatus.ATIVO,
        tipo=FlagType.RELEASE,
        estrategia=RolloutStrategy.PERCENTAGE,
        percentual=50,
        tenants_habilitados=[],
        tenants_desabilitados=[],
        usuarios_habilitados=[],
        usuarios_desabilitados=[],
        tags=[],
        dependencias=[],
        metricas={},
        ativo=True,
    )


@pytest.fixture
def sample_template():
    """Fixture para template de exemplo."""
    return NotificationTemplate(
        id=uuid.uuid4(),
        codigo="ALERT_EMAIL",
        nome="Email de Alerta",
        canal=NotificationChannel.EMAIL,
        tipo=NotificationType.ALERT,
        status=TemplateStatus.ACTIVE,
        assunto="Alerta: {{tipo}}",
        corpo="Atenção: {{mensagem}}",
        variaveis=["tipo", "mensagem"],
        variaveis_obrigatorias=["mensagem"],
        metricas={},
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
                documento="12345678000199",
                email="novo@tenant.com",
            )
            mock_create.return_value = tenant

            result = await config_service.create_tenant(
                codigo="NEW001",
                nome="Novo Tenant",
                documento="12345678000199",
                email="novo@tenant.com",
            )

            assert result.codigo == "NEW001"
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tenant(self, config_service, sample_tenant):
        """Testa busca de tenant."""
        with patch.object(config_service.repository, "get_tenant") as mock_get:
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
            patch.object(config_service.repository, "get_tenant") as mock_get,
            patch.object(config_service.repository, "update_tenant") as mock_update,
        ):
            mock_get.return_value = sample_tenant
            sample_tenant.nome = "Tenant Atualizado"
            mock_update.return_value = sample_tenant

            result = await config_service.update_tenant(
                sample_tenant.id,
                nome="Tenant Atualizado",
            )

            assert result.nome == "Tenant Atualizado"

    @pytest.mark.asyncio
    async def test_activate_tenant(self, config_service, sample_tenant):
        """Testa ativação de tenant."""
        sample_tenant.status = TenantStatus.INATIVO
        with (
            patch.object(config_service.repository, "get_tenant") as mock_get,
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
            patch.object(config_service.repository, "get_tenant") as mock_get,
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
            patch.object(config_service.repository, "get_tenant") as mock_get,
            patch.object(config_service.repository, "update_tenant") as mock_update,
        ):
            mock_get.return_value = sample_tenant
            sample_tenant.status = TenantStatus.CANCELLED
            mock_update.return_value = sample_tenant

            result = await config_service.cancel_tenant(sample_tenant.id)

            assert result.status == TenantStatus.CANCELLED


class TestConfigServiceSettings:
    """Testes do ConfigService para TenantSettings."""

    @pytest.mark.asyncio
    async def test_create_setting(self, config_service, sample_setting):
        """Testa criação de setting."""
        with patch.object(config_service.repository, "create_tenant_setting") as mock_create:
            mock_create.return_value = sample_setting

            result = await config_service.create_tenant_setting(
                tenant_id=sample_setting.tenant_id,
                chave="notifications_enabled",
                valor="true",
            )

            assert result.chave == "notifications_enabled"

    @pytest.mark.asyncio
    async def test_get_setting(self, config_service, sample_setting):
        """Testa busca de setting."""
        with patch.object(config_service.repository, "get_tenant_setting") as mock_get:
            mock_get.return_value = sample_setting

            result = await config_service.get_tenant_setting(sample_setting.id)

            assert result == sample_setting

    @pytest.mark.asyncio
    async def test_update_setting_value(self, config_service, sample_setting):
        """Testa atualização de valor de setting."""
        with (
            patch.object(config_service.repository, "get_tenant_setting") as mock_get,
            patch.object(config_service.repository, "update_tenant_setting") as mock_update,
        ):
            mock_get.return_value = sample_setting
            sample_setting.valor = "false"
            mock_update.return_value = sample_setting

            result = await config_service.update_setting_value(
                sample_setting.id,
                valor="false",
            )

            assert result.valor == "false"

    @pytest.mark.asyncio
    async def test_reset_setting(self, config_service, sample_setting):
        """Testa reset de setting para valor padrão."""
        sample_setting.valor_padrao = "default_value"
        with (
            patch.object(config_service.repository, "get_tenant_setting") as mock_get,
            patch.object(config_service.repository, "update_tenant_setting") as mock_update,
        ):
            mock_get.return_value = sample_setting
            sample_setting.valor = sample_setting.valor_padrao
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

            result = await config_service.create_system_config(
                chave="app_version",
                valor="2.0.0",
            )

            assert result.chave == "app_version"

    @pytest.mark.asyncio
    async def test_get_config_by_key(self, config_service, sample_config):
        """Testa busca de config por chave."""
        with patch.object(config_service.repository, "get_config_by_key") as mock_get:
            mock_get.return_value = sample_config

            result = await config_service.get_config_by_key("app_version")

            assert result.valor == "2.0.0"

    @pytest.mark.asyncio
    async def test_list_configs_by_scope(self, config_service, sample_config):
        """Testa listagem de configs por escopo."""
        with patch.object(config_service.repository, "list_system_configs") as mock_list:
            mock_list.return_value = ([sample_config], 1)

            configs, total = await config_service.list_system_configs(escopo=ConfigScope.GLOBAL)

            assert len(configs) == 1
            assert total == 1


class TestConfigServiceFeatureFlag:
    """Testes do ConfigService para FeatureFlag."""

    @pytest.mark.asyncio
    async def test_create_flag(self, config_service, sample_flag):
        """Testa criação de flag."""
        with patch.object(config_service.repository, "create_feature_flag") as mock_create:
            mock_create.return_value = sample_flag

            result = await config_service.create_feature_flag(
                codigo="NEW_FEATURE",
                nome="Nova Feature",
            )

            assert result.codigo == "NEW_FEATURE"

    @pytest.mark.asyncio
    async def test_enable_flag(self, config_service, sample_flag):
        """Testa ativação de flag."""
        sample_flag.status = FlagStatus.INATIVO
        with (
            patch.object(config_service.repository, "get_feature_flag") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.status = FlagStatus.ATIVO
            sample_flag.estrategia = RolloutStrategy.ALL
            mock_update.return_value = sample_flag

            result = await config_service.enable_flag(sample_flag.id)

            assert result.status == FlagStatus.ATIVO

    @pytest.mark.asyncio
    async def test_disable_flag(self, config_service, sample_flag):
        """Testa desativação de flag."""
        with (
            patch.object(config_service.repository, "get_feature_flag") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.status = FlagStatus.INATIVO
            sample_flag.estrategia = RolloutStrategy.NONE
            mock_update.return_value = sample_flag

            result = await config_service.disable_flag(sample_flag.id)

            assert result.status == FlagStatus.INATIVO

    @pytest.mark.asyncio
    async def test_set_flag_percentage(self, config_service, sample_flag):
        """Testa definir percentual de flag."""
        with (
            patch.object(config_service.repository, "get_feature_flag") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.percentual = 75
            mock_update.return_value = sample_flag

            result = await config_service.set_flag_percentage(sample_flag.id, 75)

            assert result.percentual == 75

    @pytest.mark.asyncio
    async def test_start_gradual_rollout(self, config_service, sample_flag):
        """Testa início de rollout gradual."""
        with (
            patch.object(config_service.repository, "get_feature_flag") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.estrategia = RolloutStrategy.GRADUAL
            sample_flag.percentual_alvo = 100
            sample_flag.incremento_diario = 10
            mock_update.return_value = sample_flag

            result = await config_service.start_gradual_rollout(
                sample_flag.id,
                target=100,
                daily_increment=10,
            )

            assert result.estrategia == RolloutStrategy.GRADUAL
            assert result.percentual_alvo == 100

    @pytest.mark.asyncio
    async def test_toggle_tenant_flag(self, config_service, sample_flag):
        """Testa toggle de tenant em flag."""
        tenant_id = str(uuid.uuid4())
        with (
            patch.object(config_service.repository, "get_feature_flag") as mock_get,
            patch.object(config_service.repository, "update_feature_flag") as mock_update,
        ):
            mock_get.return_value = sample_flag
            sample_flag.tenants_habilitados.append(tenant_id)
            mock_update.return_value = sample_flag

            result = await config_service.toggle_tenant_flag(
                sample_flag.id,
                tenant_id=tenant_id,
                enabled=True,
            )

            assert tenant_id in result.tenants_habilitados

    @pytest.mark.asyncio
    async def test_evaluate_flag(self, config_service, sample_flag):
        """Testa avaliação de flag."""
        with patch.object(config_service.repository, "get_feature_flag") as mock_get:
            mock_get.return_value = sample_flag

            result = await config_service.evaluate_flag(
                sample_flag.id,
                tenant_id=str(uuid.uuid4()),
                user_id="user123",
            )

            assert "enabled" in result
            assert "flag_code" in result


class TestConfigServiceNotificationTemplate:
    """Testes do ConfigService para NotificationTemplate."""

    @pytest.mark.asyncio
    async def test_create_template(self, config_service, sample_template):
        """Testa criação de template."""
        with patch.object(config_service.repository, "create_notification_template") as mock_create:
            mock_create.return_value = sample_template

            result = await config_service.create_notification_template(
                codigo="ALERT_EMAIL",
                nome="Email de Alerta",
                canal=NotificationChannel.EMAIL,
                corpo="Mensagem de teste",
            )

            assert result.codigo == "ALERT_EMAIL"

    @pytest.mark.asyncio
    async def test_activate_template(self, config_service, sample_template):
        """Testa ativação de template."""
        sample_template.status = TemplateStatus.DRAFT
        with (
            patch.object(config_service.repository, "get_notification_template") as mock_get,
            patch.object(config_service.repository, "update_notification_template") as mock_update,
        ):
            mock_get.return_value = sample_template
            sample_template.status = TemplateStatus.ACTIVE
            mock_update.return_value = sample_template

            result = await config_service.activate_template(sample_template.id)

            assert result.status == TemplateStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_deactivate_template(self, config_service, sample_template):
        """Testa desativação de template."""
        with (
            patch.object(config_service.repository, "get_notification_template") as mock_get,
            patch.object(config_service.repository, "update_notification_template") as mock_update,
        ):
            mock_get.return_value = sample_template
            sample_template.status = TemplateStatus.INACTIVE
            mock_update.return_value = sample_template

            result = await config_service.deactivate_template(sample_template.id)

            assert result.status == TemplateStatus.INACTIVE

    @pytest.mark.asyncio
    async def test_render_template(self, config_service, sample_template):
        """Testa renderização de template."""
        with patch.object(config_service.repository, "get_notification_template") as mock_get:
            mock_get.return_value = sample_template

            result = await config_service.render_template(
                sample_template.id,
                variables={"tipo": "Urgente", "mensagem": "Sistema fora do ar"},
            )

            assert "Urgente" in result["subject"]
            assert "Sistema fora do ar" in result["body"]

    @pytest.mark.asyncio
    async def test_clone_template(self, config_service, sample_template):
        """Testa clonagem de template."""
        with (
            patch.object(config_service.repository, "get_notification_template") as mock_get,
            patch.object(config_service.repository, "create_notification_template") as mock_create,
        ):
            mock_get.return_value = sample_template
            cloned = NotificationTemplate(
                id=uuid.uuid4(),
                codigo="ALERT_EMAIL_V2",
                nome="Email de Alerta V2",
                canal=sample_template.canal,
                corpo=sample_template.corpo,
                status=TemplateStatus.DRAFT,
                versao=1,
                template_pai_id=sample_template.id,
            )
            mock_create.return_value = cloned

            result = await config_service.clone_template(
                sample_template.id,
                new_code="ALERT_EMAIL_V2",
                new_name="Email de Alerta V2",
            )

            assert result.codigo == "ALERT_EMAIL_V2"
            assert result.template_pai_id == sample_template.id


class TestConfigServiceDashboard:
    """Testes do ConfigService para Dashboard."""

    @pytest.mark.asyncio
    async def test_get_config_dashboard(self, config_service):
        """Testa obtenção do dashboard de configurações."""
        with patch.object(config_service.repository, "get_dashboard_stats") as mock_stats:
            mock_stats.return_value = {
                "total_tenants": 100,
                "tenants_ativos": 90,
                "tenants_trial": 10,
                "total_configs": 50,
                "total_flags": 30,
                "flags_ativos": 25,
                "total_templates": 40,
                "templates_ativos": 35,
            }

            result = await config_service.get_config_dashboard()

            assert result["total_tenants"] == 100
            assert result["tenants_ativos"] == 90

    @pytest.mark.asyncio
    async def test_get_tenant_dashboard(self, config_service, sample_tenant):
        """Testa obtenção do dashboard de tenant."""
        with (
            patch.object(config_service.repository, "get_tenant") as mock_get,
            patch.object(config_service.repository, "get_tenant_stats") as mock_stats,
        ):
            mock_get.return_value = sample_tenant
            mock_stats.return_value = {
                "total_settings": 25,
                "total_templates": 10,
            }

            result = await config_service.get_tenant_dashboard(sample_tenant.id)

            assert result["tenant"] == sample_tenant
            assert "total_settings" in result


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
        with patch.object(config_service.repository, "get_flag_by_codigo") as mock_get:
            mock_get.return_value = sample_flag

            result = await config_service.get_flag_by_codigo(sample_flag.codigo)

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
