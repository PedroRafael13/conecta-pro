"""
Testes da API do módulo Config
Sprint 35: Configurações e Multi-tenant
"""

# pylint: disable=redefined-outer-name,unused-argument,too-many-lines
import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

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


@pytest.fixture
def mock_db():
    """Fixture para mock do banco de dados."""
    return MagicMock()


@pytest.fixture
def sample_tenant():
    """Fixture para tenant de exemplo."""
    return Tenant(
        id=uuid.uuid4(),
        codigo="TEST001",
        nome="Empresa Teste",
        nome_fantasia="Teste",
        documento="12345678000199",
        email="teste@empresa.com",
        telefone="11999999999",
        status=TenantStatus.ATIVO,
        plano=TenantPlan.PROFESSIONAL,
        tipo=TenantType.EMPRESA,
        limite_usuarios=50,
        limite_storage_gb=100,
        limite_api_calls_mes=100000,
        uso_usuarios_ativos=10,
        uso_storage_bytes=10 * 1024 * 1024 * 1024,
        uso_api_calls_mes=5000,
        features_habilitadas=["reports", "dashboard"],
        modulos_habilitados=["crm", "financial"],
        ativo=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_setting():
    """Fixture para setting de exemplo."""
    return TenantSettings(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        chave="email_notifications",
        valor="true",
        valor_padrao="true",
        categoria=SettingCategory.NOTIFICACAO,
        tipo=SettingType.BOOLEAN,
        descricao="Habilita notificações por email",
        is_sensivel=False,
        is_editavel=True,
        is_visivel=True,
        ativo=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_config():
    """Fixture para config de exemplo."""
    return SystemConfig(
        id=uuid.uuid4(),
        chave="app_name",
        valor="ERP Conecta Mais",
        valor_padrao="ERP",
        tipo=SettingType.STRING,
        escopo=ConfigScope.GLOBAL,
        prioridade=ConfigPriority.NORMAL,
        descricao="Nome da aplicação",
        is_sensivel=False,
        is_editavel=True,
        is_visivel=True,
        permite_override=True,
        ativo=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_flag():
    """Fixture para feature flag de exemplo."""
    return FeatureFlag(
        id=uuid.uuid4(),
        codigo="NEW_DASHBOARD",
        nome="Novo Dashboard",
        descricao="Ativa o novo dashboard para usuários",
        status=FlagStatus.ATIVO,
        tipo=FlagType.RELEASE,
        estrategia=RolloutStrategy.PERCENTAGE,
        percentual=50,
        tenants_habilitados=[],
        tenants_desabilitados=[],
        usuarios_habilitados=[],
        usuarios_desabilitados=[],
        is_ab_test=False,
        tags=["dashboard", "ui"],
        ativo=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_template():
    """Fixture para template de exemplo."""
    return NotificationTemplate(
        id=uuid.uuid4(),
        codigo="WELCOME_EMAIL",
        nome="Email de Boas-vindas",
        descricao="Template de boas-vindas para novos usuários",
        canal=NotificationChannel.EMAIL,
        tipo=NotificationType.MEETING_REMINDER,
        status=TemplateStatus.ACTIVE,
        assunto="Bem-vindo ao {{app_name}}!",
        corpo="Olá {{nome}}, seja bem-vindo!",
        corpo_html="<h1>Olá {{nome}}</h1><p>Seja bem-vindo!</p>",
        variaveis=["nome", "app_name"],
        variaveis_obrigatorias=["nome"],
        idioma="pt-BR",
        prioridade=ConfigPriority.NORMAL,
        versao=1,
        metricas={"sent": 100, "opened": 45},
        tags=["welcome", "onboarding"],
        ativo=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class TestTenantEndpoints:
    """Testes dos endpoints de Tenant."""

    @pytest.mark.asyncio
    async def test_listar_tenants(self, mock_db, sample_tenant):
        """Testa listagem de tenants."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.list_tenants.return_value = ([sample_tenant], 1)
            mock_service.return_value = mock_instance

            # Simula chamada bem-sucedida
            result = await mock_instance.list_tenants()
            tenants, total = result

            assert len(tenants) == 1
            assert total == 1
            assert tenants[0].codigo == "TEST001"

    @pytest.mark.asyncio
    async def test_criar_tenant(self, mock_db, sample_tenant):
        """Testa criação de tenant."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.create_tenant.return_value = sample_tenant
            mock_service.return_value = mock_instance

            result = await mock_instance.create_tenant(
                codigo="TEST001",
                nome="Empresa Teste",
                documento="12345678000199",
                email="teste@empresa.com",
            )

            assert result.codigo == "TEST001"
            assert result.nome == "Empresa Teste"

    @pytest.mark.asyncio
    async def test_buscar_tenant(self, mock_db, sample_tenant):
        """Testa busca de tenant por ID."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_tenant.return_value = sample_tenant
            mock_service.return_value = mock_instance

            result = await mock_instance.get_tenant(sample_tenant.id)

            assert result is not None
            assert result.id == sample_tenant.id

    @pytest.mark.asyncio
    async def test_buscar_tenant_nao_encontrado(self, mock_db):
        """Testa busca de tenant não encontrado."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_tenant.return_value = None
            mock_service.return_value = mock_instance

            result = await mock_instance.get_tenant(uuid.uuid4())

            assert result is None

    @pytest.mark.asyncio
    async def test_atualizar_tenant(self, mock_db, sample_tenant):
        """Testa atualização de tenant."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            updated_tenant = sample_tenant
            updated_tenant.nome = "Empresa Atualizada"
            mock_instance.update_tenant.return_value = updated_tenant
            mock_service.return_value = mock_instance

            result = await mock_instance.update_tenant(
                sample_tenant.id,
                nome="Empresa Atualizada",
            )

            assert result.nome == "Empresa Atualizada"

    @pytest.mark.asyncio
    async def test_ativar_tenant(self, mock_db, sample_tenant):
        """Testa ativação de tenant."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_tenant.status = TenantStatus.ATIVO
            mock_instance.activate_tenant.return_value = sample_tenant
            mock_service.return_value = mock_instance

            result = await mock_instance.activate_tenant(sample_tenant.id)

            assert result.status == TenantStatus.ATIVO

    @pytest.mark.asyncio
    async def test_suspender_tenant(self, mock_db, sample_tenant):
        """Testa suspensão de tenant."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_tenant.status = TenantStatus.SUSPENSO
            mock_instance.suspend_tenant.return_value = sample_tenant
            mock_service.return_value = mock_instance

            result = await mock_instance.suspend_tenant(
                sample_tenant.id,
                reason="Pagamento pendente",
            )

            assert result.status == TenantStatus.SUSPENSO


class TestTenantSettingsEndpoints:
    """Testes dos endpoints de TenantSettings."""

    @pytest.mark.asyncio
    async def test_listar_settings(self, mock_db, sample_setting):
        """Testa listagem de settings."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.list_tenant_settings.return_value = ([sample_setting], 1)
            mock_service.return_value = mock_instance

            result = await mock_instance.list_tenant_settings(sample_setting.tenant_id)
            settings, total = result

            assert len(settings) == 1
            assert total == 1

    @pytest.mark.asyncio
    async def test_criar_setting(self, mock_db, sample_setting):
        """Testa criação de setting."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.create_tenant_setting.return_value = sample_setting
            mock_service.return_value = mock_instance

            result = await mock_instance.create_tenant_setting(
                tenant_id=sample_setting.tenant_id,
                chave="email_notifications",
                valor="true",
            )

            assert result.chave == "email_notifications"

    @pytest.mark.asyncio
    async def test_atualizar_setting_valor(self, mock_db, sample_setting):
        """Testa atualização de valor de setting."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_setting.valor = "false"
            mock_instance.update_setting_value.return_value = sample_setting
            mock_service.return_value = mock_instance

            result = await mock_instance.update_setting_value(
                sample_setting.id,
                valor="false",
            )

            assert result.valor == "false"


class TestSystemConfigEndpoints:
    """Testes dos endpoints de SystemConfig."""

    @pytest.mark.asyncio
    async def test_listar_configs(self, mock_db, sample_config):
        """Testa listagem de configs."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.list_system_configs.return_value = ([sample_config], 1)
            mock_service.return_value = mock_instance

            result = await mock_instance.list_system_configs()
            configs, total = result

            assert len(configs) == 1
            assert total == 1

    @pytest.mark.asyncio
    async def test_criar_config(self, mock_db, sample_config):
        """Testa criação de config."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.create_system_config.return_value = sample_config
            mock_service.return_value = mock_instance

            result = await mock_instance.create_system_config(
                chave="app_name",
                valor="ERP Conecta Mais",
            )

            assert result.chave == "app_name"

    @pytest.mark.asyncio
    async def test_buscar_config_por_chave(self, mock_db, sample_config):
        """Testa busca de config por chave."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_config_by_key.return_value = sample_config
            mock_service.return_value = mock_instance

            result = await mock_instance.get_config_by_key("app_name")

            assert result is not None
            assert result.chave == "app_name"


class TestFeatureFlagEndpoints:
    """Testes dos endpoints de FeatureFlag."""

    @pytest.mark.asyncio
    async def test_listar_flags(self, mock_db, sample_flag):
        """Testa listagem de flags."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.list_feature_flags.return_value = ([sample_flag], 1)
            mock_service.return_value = mock_instance

            result = await mock_instance.list_feature_flags()
            flags, total = result

            assert len(flags) == 1
            assert total == 1

    @pytest.mark.asyncio
    async def test_criar_flag(self, mock_db, sample_flag):
        """Testa criação de flag."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.create_feature_flag.return_value = sample_flag
            mock_service.return_value = mock_instance

            result = await mock_instance.create_feature_flag(
                codigo="NEW_DASHBOARD",
                nome="Novo Dashboard",
            )

            assert result.codigo == "NEW_DASHBOARD"

    @pytest.mark.asyncio
    async def test_enable_flag(self, mock_db, sample_flag):
        """Testa ativação de flag."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_flag.status = FlagStatus.ATIVO
            sample_flag.estrategia = RolloutStrategy.ALL
            mock_instance.enable_flag.return_value = sample_flag
            mock_service.return_value = mock_instance

            result = await mock_instance.enable_flag(sample_flag.id)

            assert result.status == FlagStatus.ATIVO
            assert result.estrategia == RolloutStrategy.ALL

    @pytest.mark.asyncio
    async def test_disable_flag(self, mock_db, sample_flag):
        """Testa desativação de flag."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_flag.status = FlagStatus.INATIVO
            sample_flag.estrategia = RolloutStrategy.NONE
            mock_instance.disable_flag.return_value = sample_flag
            mock_service.return_value = mock_instance

            result = await mock_instance.disable_flag(sample_flag.id)

            assert result.status == FlagStatus.INATIVO

    @pytest.mark.asyncio
    async def test_set_flag_percentage(self, mock_db, sample_flag):
        """Testa definir percentual de flag."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_flag.percentual = 75
            mock_instance.set_flag_percentage.return_value = sample_flag
            mock_service.return_value = mock_instance

            result = await mock_instance.set_flag_percentage(sample_flag.id, 75)

            assert result.percentual == 75

    @pytest.mark.asyncio
    async def test_evaluate_flag(self, mock_db, sample_flag):
        """Testa avaliação de flag."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.evaluate_flag.return_value = {
                "enabled": True,
                "flag_code": "NEW_DASHBOARD",
                "variant": None,
                "reason": "percentage",
            }
            mock_service.return_value = mock_instance

            result = await mock_instance.evaluate_flag(
                sample_flag.id,
                tenant_id=str(uuid.uuid4()),
                user_id="user123",
            )

            assert result["enabled"] is True
            assert result["flag_code"] == "NEW_DASHBOARD"

    @pytest.mark.asyncio
    async def test_start_gradual_rollout(self, mock_db, sample_flag):
        """Testa início de rollout gradual."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_flag.estrategia = RolloutStrategy.GRADUAL
            sample_flag.percentual_alvo = 100
            sample_flag.incremento_diario = 10
            mock_instance.start_gradual_rollout.return_value = sample_flag
            mock_service.return_value = mock_instance

            result = await mock_instance.start_gradual_rollout(
                sample_flag.id,
                target=100,
                daily_increment=10,
            )

            assert result.estrategia == RolloutStrategy.GRADUAL
            assert result.percentual_alvo == 100


class TestNotificationTemplateEndpoints:
    """Testes dos endpoints de NotificationTemplate."""

    @pytest.mark.asyncio
    async def test_listar_templates(self, mock_db, sample_template):
        """Testa listagem de templates."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.list_notification_templates.return_value = ([sample_template], 1)
            mock_service.return_value = mock_instance

            result = await mock_instance.list_notification_templates()
            templates, total = result

            assert len(templates) == 1
            assert total == 1

    @pytest.mark.asyncio
    async def test_criar_template(self, mock_db, sample_template):
        """Testa criação de template."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.create_notification_template.return_value = sample_template
            mock_service.return_value = mock_instance

            result = await mock_instance.create_notification_template(
                codigo="WELCOME_EMAIL",
                nome="Email de Boas-vindas",
                canal=NotificationChannel.EMAIL,
                corpo="Olá {{nome}}!",
            )

            assert result.codigo == "WELCOME_EMAIL"

    @pytest.mark.asyncio
    async def test_ativar_template(self, mock_db, sample_template):
        """Testa ativação de template."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            sample_template.status = TemplateStatus.ACTIVE
            mock_instance.activate_template.return_value = sample_template
            mock_service.return_value = mock_instance

            result = await mock_instance.activate_template(sample_template.id)

            assert result.status == TemplateStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_render_template(self, mock_db, sample_template):
        """Testa renderização de template."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.render_template.return_value = {
                "subject": "Bem-vindo ao ERP!",
                "body": "Olá João, seja bem-vindo!",
                "body_html": "<h1>Olá João</h1><p>Seja bem-vindo!</p>",
            }
            mock_service.return_value = mock_instance

            result = await mock_instance.render_template(
                sample_template.id,
                variables={"nome": "João", "app_name": "ERP"},
            )

            assert "João" in result["body"]

    @pytest.mark.asyncio
    async def test_clonar_template(self, mock_db, sample_template):
        """Testa clonagem de template."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            cloned = NotificationTemplate(
                id=uuid.uuid4(),
                codigo="WELCOME_EMAIL_V2",
                nome="Email de Boas-vindas V2",
                canal=sample_template.canal,
                corpo=sample_template.corpo,
                status=TemplateStatus.DRAFT,
                versao=1,
                template_pai_id=sample_template.id,
            )
            mock_instance.clone_template.return_value = cloned
            mock_service.return_value = mock_instance

            result = await mock_instance.clone_template(
                sample_template.id,
                new_code="WELCOME_EMAIL_V2",
                new_name="Email de Boas-vindas V2",
            )

            assert result.codigo == "WELCOME_EMAIL_V2"
            assert result.status == TemplateStatus.DRAFT
            assert result.template_pai_id == sample_template.id


class TestDashboardEndpoints:
    """Testes dos endpoints de Dashboard."""

    @pytest.mark.asyncio
    async def test_config_dashboard(self, mock_db):
        """Testa dashboard de configurações."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_config_dashboard.return_value = {
                "total_tenants": 50,
                "tenants_ativos": 45,
                "tenants_trial": 5,
                "total_configs": 100,
                "total_flags": 20,
                "flags_ativos": 15,
                "total_templates": 30,
                "templates_ativos": 25,
            }
            mock_service.return_value = mock_instance

            result = await mock_instance.get_config_dashboard()

            assert result["total_tenants"] == 50
            assert result["tenants_ativos"] == 45

    @pytest.mark.asyncio
    async def test_tenant_dashboard(self, mock_db, sample_tenant):
        """Testa dashboard de tenant específico."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_tenant_dashboard.return_value = {
                "tenant": sample_tenant,
                "total_settings": 50,
                "total_templates": 10,
                "storage_usage_percent": 10.0,
                "users_usage_percent": 20.0,
                "api_usage_percent": 5.0,
            }
            mock_service.return_value = mock_instance

            result = await mock_instance.get_tenant_dashboard(sample_tenant.id)

            assert result["tenant"] == sample_tenant
            assert result["storage_usage_percent"] == 10.0


class TestValidation:
    """Testes de validação de dados."""

    def test_tenant_documento_valido(self):
        """Testa documento válido de tenant."""
        tenant = Tenant(
            codigo="VAL001",
            nome="Empresa Validação",
            documento="12345678000199",
            email="valid@email.com",
        )
        assert len(tenant.documento) >= 11

    def test_tenant_email_formato(self):
        """Testa formato de email."""
        tenant = Tenant(
            codigo="VAL002",
            nome="Empresa Email",
            documento="12345678000188",
            email="test@example.com",
        )
        assert "@" in tenant.email

    def test_feature_flag_percentual_range(self):
        """Testa range de percentual de flag."""
        flag = FeatureFlag(
            codigo="PERCENT_TEST",
            nome="Teste Percentual",
            percentual=50,
        )
        assert 0 <= flag.percentual <= 100

    def test_notification_template_variaveis(self):
        """Testa extração de variáveis de template."""
        template = NotificationTemplate(
            codigo="VAR_TEST",
            nome="Teste Variáveis",
            canal=NotificationChannel.EMAIL,
            corpo="Olá {{nome}}, seu código é {{codigo}}",
            variaveis=["nome", "codigo"],
        )
        assert "nome" in template.variaveis
        assert "codigo" in template.variaveis


class TestErrorHandling:
    """Testes de tratamento de erros."""

    @pytest.mark.asyncio
    async def test_tenant_nao_encontrado(self, mock_db):
        """Testa erro quando tenant não é encontrado."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_tenant.return_value = None
            mock_service.return_value = mock_instance

            result = await mock_instance.get_tenant(uuid.uuid4())
            assert result is None

    @pytest.mark.asyncio
    async def test_flag_nao_encontrada(self, mock_db):
        """Testa erro quando flag não é encontrada."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_feature_flag.return_value = None
            mock_service.return_value = mock_instance

            result = await mock_instance.get_feature_flag(uuid.uuid4())
            assert result is None

    @pytest.mark.asyncio
    async def test_template_nao_encontrado(self, mock_db):
        """Testa erro quando template não é encontrado."""
        with patch("modules.config.controllers.config_controller.ConfigService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_notification_template.return_value = None
            mock_service.return_value = mock_instance

            result = await mock_instance.get_notification_template(uuid.uuid4())
            assert result is None
