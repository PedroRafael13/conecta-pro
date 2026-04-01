"""
Testes dos Models do modulo Config
Sprint 35: Configuracoes e Multi-tenant
"""

# pylint: disable=redefined-outer-name,unused-argument
import uuid
from datetime import UTC, datetime, timedelta, timezone

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


class TestTenantModel:
    """Testes do model Tenant."""

    def test_criar_tenant_basico(self):
        """Testa criacao de tenant basico."""
        tenant = Tenant(
            codigo="TENANT001",
            nome="Empresa Teste LTDA",
            cnpj="12345678000199",
            email="contato@empresa.com",
        )
        assert tenant.codigo == "TENANT001"
        assert tenant.nome == "Empresa Teste LTDA"
        assert tenant.cnpj == "12345678000199"
        assert tenant.email == "contato@empresa.com"
        # status/plan/tipo sao definidos pelo banco (default), nao no objeto Python
        # Verificamos os valores passados
        assert tenant.codigo == "TENANT001"
        assert tenant.nome == "Empresa Teste LTDA"
        assert tenant.cnpj == "12345678000199"
        assert tenant.email == "contato@empresa.com"

    def test_tenant_is_active(self):
        """Testa propriedade is_active."""
        tenant = Tenant(
            codigo="TENANT002",
            nome="Empresa Ativa",
            cnpj="12345678000100",
            email="ativo@empresa.com",
            status=TenantStatus.ATIVO,
            ativo=True,
        )
        assert tenant.is_active is True

        tenant.status = TenantStatus.SUSPENSO
        assert tenant.is_active is False

    def test_tenant_is_trial(self):
        """Testa propriedade is_trial."""
        tenant = Tenant(
            codigo="TENANT003",
            nome="Empresa Trial",
            cnpj="12345678000101",
            email="trial@empresa.com",
            status=TenantStatus.TRIAL,
            trial_ends_at=datetime.now(UTC) + timedelta(days=14),
        )
        # is_trial apenas verifica status == TRIAL
        assert tenant.is_trial is True

        # Mudar status para nao-trial
        tenant.status = TenantStatus.ATIVO
        assert tenant.is_trial is False

    def test_tenant_activate(self):
        """Testa ativacao de tenant."""
        tenant = Tenant(
            codigo="TENANT004",
            nome="Empresa Inativa",
            cnpj="12345678000102",
            email="inativo@empresa.com",
            status=TenantStatus.INATIVO,
        )
        tenant.activate()
        assert tenant.status == TenantStatus.ATIVO
        # activate() limpa suspended_at e suspension_reason
        assert tenant.suspended_at is None
        assert tenant.suspension_reason is None

    def test_tenant_suspend(self):
        """Testa suspensao de tenant."""
        tenant = Tenant(
            codigo="TENANT005",
            nome="Empresa a Suspender",
            cnpj="12345678000103",
            email="suspender@empresa.com",
            status=TenantStatus.ATIVO,
        )
        tenant.suspend("Pagamento pendente")
        assert tenant.status == TenantStatus.SUSPENSO
        assert "Pagamento pendente" in (tenant.suspension_reason or "")

    def test_tenant_cancel(self):
        """Testa cancelamento de tenant."""
        tenant = Tenant(
            codigo="TENANT006",
            nome="Empresa a Cancelar",
            cnpj="12345678000104",
            email="cancelar@empresa.com",
            status=TenantStatus.ATIVO,
        )
        tenant.cancel()
        assert tenant.status == TenantStatus.CANCELADO
        assert tenant.data_fim is not None

    def test_tenant_upgrade_plan(self):
        """Testa upgrade de plano."""
        tenant = Tenant(
            codigo="TENANT007",
            nome="Empresa Upgrade",
            cnpj="12345678000105",
            email="upgrade@empresa.com",
            plan=TenantPlan.FREE,
        )
        tenant.upgrade_plan(TenantPlan.PROFESSIONAL)
        assert tenant.plan == TenantPlan.PROFESSIONAL

    def test_tenant_enable_disable_feature(self):
        """Testa habilitar/desabilitar features."""
        tenant = Tenant(
            codigo="TENANT008",
            nome="Empresa Features",
            cnpj="12345678000106",
            email="features@empresa.com",
            features_enabled=[],
        )
        tenant.enable_feature("reports")
        assert "reports" in tenant.features_enabled

        tenant.disable_feature("reports")
        assert "reports" not in tenant.features_enabled

    def test_tenant_storage_usage_percent(self):
        """Testa calculo de uso de storage."""
        tenant = Tenant(
            codigo="TENANT009",
            nome="Empresa Storage",
            cnpj="12345678000107",
            email="storage@empresa.com",
            max_storage_gb=10,
            storage_usado_mb=5 * 1024,  # 5GB em MB = 5120 MB
        )
        assert tenant.storage_usage_percent == 50.0


class TestTenantSettingsModel:
    """Testes do model TenantSettings."""

    def test_criar_setting_basico(self):
        """Testa criacao de setting basico."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="notificacoes_email",
            nome="Notificacoes Email",
            valor="true",
            category=SettingCategory.NOTIFICACAO,
            setting_type=SettingType.BOOLEAN,
        )
        assert setting.chave == "notificacoes_email"
        assert setting.valor == "true"
        assert setting.category == SettingCategory.NOTIFICACAO
        assert setting.setting_type == SettingType.BOOLEAN

    def test_setting_typed_value_boolean(self):
        """Testa conversao de valor boolean via typed_value property."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="feature_enabled",
            nome="Feature Enabled",
            valor="true",
            setting_type=SettingType.BOOLEAN,
        )
        assert setting.typed_value is True

        setting.valor = "false"
        assert setting.typed_value is False

    def test_setting_typed_value_integer(self):
        """Testa conversao de valor integer via typed_value property."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="max_users",
            nome="Max Users",
            valor="100",
            setting_type=SettingType.INTEGER,
        )
        assert setting.typed_value == 100

    def test_setting_typed_value_float(self):
        """Testa conversao de valor float via typed_value property."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="taxa_desconto",
            nome="Taxa Desconto",
            valor="15.5",
            setting_type=SettingType.FLOAT,
        )
        assert setting.typed_value == 15.5

    def test_setting_typed_value_json(self):
        """Testa conversao de valor JSON via typed_value property."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="config_complex",
            nome="Config Complex",
            valor='{"key": "value", "number": 42}',
            setting_type=SettingType.JSON,
            valor_json={"key": "value", "number": 42},
        )
        result = setting.typed_value
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_setting_set_value_with_history(self):
        """Testa set_value com historico."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="config_test",
            nome="Config Test",
            valor="old_value",
            setting_type=SettingType.STRING,
            history=[],
        )
        modified_by = uuid.uuid4()
        setting.set_value("new_value", modified_by=modified_by)
        assert setting.valor == "new_value"
        assert len(setting.history) == 1
        assert setting.history[0]["old_value"] == "old_value"
        assert setting.history[0]["new_value"] == "new_value"

    def test_setting_validate_value_valid(self):
        """Testa validacao de valor valido."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="max_items",
            nome="Max Items",
            valor="50",
            setting_type=SettingType.INTEGER,
            min_value=1,
            max_value=100,
        )
        is_valid, error = setting.validate_value("50")
        assert is_valid is True

    def test_setting_validate_value_invalid(self):
        """Testa validacao de valor invalido."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="max_items",
            nome="Max Items",
            valor="50",
            setting_type=SettingType.INTEGER,
            min_value=1,
            max_value=100,
        )
        is_valid, error = setting.validate_value("150")
        assert is_valid is False


class TestSystemConfigModel:
    """Testes do model SystemConfig."""

    def test_criar_config_basico(self):
        """Testa criacao de config basico."""
        config = SystemConfig(
            chave="app_name",
            nome="App Name",
            valor="ERP Conecta Mais",
            valor_type="string",
            scope=ConfigScope.GLOBAL,
        )
        assert config.chave == "app_name"
        assert config.valor == "ERP Conecta Mais"
        assert config.scope == ConfigScope.GLOBAL

    def test_config_prioridades(self):
        """Testa diferentes prioridades."""
        config_low = SystemConfig(
            chave="log_level",
            nome="Log Level",
            valor="INFO",
            priority=ConfigPriority.LOW,
        )
        config_critical = SystemConfig(
            chave="maintenance_mode",
            nome="Maintenance Mode",
            valor="false",
            priority=ConfigPriority.CRITICAL,
        )
        assert config_low.priority == ConfigPriority.LOW
        assert config_critical.priority == ConfigPriority.CRITICAL


class TestFeatureFlagModel:
    """Testes do model FeatureFlag."""

    def test_criar_flag_basico(self):
        """Testa criacao de flag basico."""
        flag = FeatureFlag(
            codigo="NEW_DASHBOARD",
            nome="Novo Dashboard",
            descricao="Ativa o novo dashboard para usuarios",
            status=FlagStatus.INATIVO,
            rollout_strategy=RolloutStrategy.NONE,
        )
        assert flag.codigo == "NEW_DASHBOARD"
        assert flag.nome == "Novo Dashboard"
        assert flag.status == FlagStatus.INATIVO
        assert flag.rollout_strategy == RolloutStrategy.NONE

    def test_flag_enable_disable(self):
        """Testa ativar/desativar flag."""
        flag = FeatureFlag(
            codigo="FEATURE_X",
            nome="Feature X",
            status=FlagStatus.INATIVO,
            rollout_strategy=RolloutStrategy.NONE,
            rollout_percentage=0,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        flag.enable()
        assert flag.status == FlagStatus.ATIVO
        assert flag.rollout_strategy == RolloutStrategy.ALL

        flag.disable()
        assert flag.status == FlagStatus.INATIVO
        assert flag.rollout_strategy == RolloutStrategy.NONE

    def test_flag_set_percentage(self):
        """Testa definir percentual de rollout."""
        flag = FeatureFlag(
            codigo="GRADUAL_FEATURE",
            nome="Feature Gradual",
            status=FlagStatus.INATIVO,
            rollout_strategy=RolloutStrategy.NONE,
            rollout_percentage=0,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        flag.set_percentage(25)
        assert flag.rollout_percentage == 25
        assert flag.rollout_strategy == RolloutStrategy.PERCENTAGE
        assert flag.status == FlagStatus.ATIVO

    def test_flag_start_gradual_rollout(self):
        """Testa inicio de rollout gradual."""
        flag = FeatureFlag(
            codigo="GRADUAL_ROLLOUT",
            nome="Rollout Gradual",
            status=FlagStatus.INATIVO,
            rollout_strategy=RolloutStrategy.NONE,
            rollout_percentage=0,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        flag.start_gradual_rollout(start_percentage=0, end_percentage=100, duration_days=10)
        assert flag.gradual_end_percentage == 100
        assert flag.gradual_start_percentage == 0
        assert flag.rollout_strategy == RolloutStrategy.GRADUAL
        assert flag.status == FlagStatus.GRADUAL

    def test_flag_enable_disable_tenant(self):
        """Testa enable/disable de tenant."""
        tenant_id = str(uuid.uuid4())
        flag = FeatureFlag(
            codigo="TENANT_FEATURE",
            nome="Feature por Tenant",
            status=FlagStatus.INATIVO,
            rollout_strategy=RolloutStrategy.NONE,
            rollout_percentage=0,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
            enabled_tenants=[],
            disabled_tenants=[],
        )
        flag.enable_for_tenant(tenant_id)
        assert tenant_id in flag.enabled_tenants

        flag.disable_for_tenant(tenant_id)
        assert tenant_id in flag.disabled_tenants

    def test_flag_evaluate_all_strategy(self):
        """Testa avaliacao com estrategia ALL."""
        flag = FeatureFlag(
            codigo="ALL_USERS",
            nome="Todos os Usuarios",
            status=FlagStatus.ATIVO,
            rollout_strategy=RolloutStrategy.ALL,
            rollout_percentage=100,
            ativo=True,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        enabled, variant = flag.evaluate()
        assert enabled is True

    def test_flag_evaluate_none_strategy(self):
        """Testa avaliacao com estrategia NONE."""
        flag = FeatureFlag(
            codigo="NO_USERS",
            nome="Nenhum Usuario",
            status=FlagStatus.ATIVO,
            rollout_strategy=RolloutStrategy.NONE,
            rollout_percentage=0,
            ativo=True,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        enabled, variant = flag.evaluate()
        assert enabled is False

    def test_flag_evaluate_tenant_list(self):
        """Testa avaliacao com lista de tenants."""
        tenant_id = str(uuid.uuid4())
        flag = FeatureFlag(
            codigo="TENANT_LIST",
            nome="Lista de Tenants",
            status=FlagStatus.ATIVO,
            rollout_strategy=RolloutStrategy.TENANT_LIST,
            rollout_percentage=0,
            enabled_tenants=[tenant_id],
            disabled_tenants=[],
            ativo=True,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        enabled, variant = flag.evaluate(tenant_id=tenant_id)
        assert enabled is True

        other_tenant = str(uuid.uuid4())
        enabled, variant = flag.evaluate(tenant_id=other_tenant)
        assert enabled is False

    def test_flag_evaluate_inactive(self):
        """Testa avaliacao de flag inativo."""
        flag = FeatureFlag(
            codigo="INACTIVE_FLAG",
            nome="Flag Inativo",
            status=FlagStatus.INATIVO,
            rollout_strategy=RolloutStrategy.NONE,
            rollout_percentage=0,
            ativo=False,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        enabled, variant = flag.evaluate()
        assert enabled is False

    def test_flag_ab_test(self):
        """Testa flag como A/B test com variantes."""
        flag = FeatureFlag(
            codigo="AB_TEST",
            nome="Teste A/B",
            status=FlagStatus.ATIVO,
            rollout_strategy=RolloutStrategy.ALL,
            rollout_percentage=100,
            variants=[
                {"name": "control", "weight": 50},
                {"name": "variant_a", "weight": 50},
            ],
            default_variant="control",
            ativo=True,
            evaluation_count=0,
            enabled_count=0,
            disabled_count=0,
        )
        enabled, variant = flag.evaluate(user_id="user123")
        assert enabled is True
        assert variant in ["control", "variant_a"]


class TestNotificationTemplateModel:
    """Testes do model NotificationTemplate."""

    def test_criar_template_basico(self):
        """Testa criacao de template basico."""
        template = NotificationTemplate(
            codigo="WELCOME_EMAIL",
            nome="Email de Boas-vindas",
            notification_type=NotificationType.TRANSACIONAL,
            status=TemplateStatus.RASCUNHO,
            email_subject="Bem-vindo ao Sistema!",
            email_body_html="Ola {{nome}}, bem-vindo!",
            sent_count=0,
            delivered_count=0,
            opened_count=0,
            clicked_count=0,
            bounced_count=0,
            unsubscribed_count=0,
            version=1,
            priority=3,
            send_delay_minutes=0,
            batch_size=100,
        )
        assert template.codigo == "WELCOME_EMAIL"
        assert template.notification_type == NotificationType.TRANSACIONAL
        assert template.status == TemplateStatus.RASCUNHO

    def test_template_activate_deactivate(self):
        """Testa ativar/desativar template."""
        template = NotificationTemplate(
            codigo="TEMPLATE_1",
            nome="Template 1",
            notification_type=NotificationType.ALERTA,
            sms_body="Mensagem de teste",
        )
        template.activate()
        assert template.status == TemplateStatus.ATIVO

        template.deactivate()
        assert template.status == TemplateStatus.INATIVO

    def test_template_render_simples(self):
        """Testa renderizacao simples."""
        template = NotificationTemplate(
            codigo="SIMPLE_TEMPLATE",
            nome="Template Simples",
            notification_type=NotificationType.TRANSACIONAL,
            email_subject="Ola {{nome}}",
            email_body_html="Prezado(a) {{nome}}, seu pedido {{pedido_id}} foi confirmado.",
        )
        result = template.render({"nome": "Joao", "pedido_id": "12345"})
        assert result["subject"] == "Ola Joao"
        assert "Joao" in result["body_html"]
        assert "12345" in result["body_html"]

    def test_template_render_html(self):
        """Testa renderizacao HTML."""
        template = NotificationTemplate(
            codigo="HTML_TEMPLATE",
            nome="Template HTML",
            notification_type=NotificationType.TRANSACIONAL,
            email_subject="Notificacao",
            email_body_text="Texto simples",
            email_body_html="<h1>Ola {{nome}}</h1><p>Bem-vindo!</p>",
        )
        result = template.render({"nome": "Maria"})
        assert "<h1>Ola Maria</h1>" in result["body_html"]

    def test_template_clone(self):
        """Testa clonagem de template."""
        original = NotificationTemplate(
            codigo="ORIGINAL",
            nome="Template Original",
            notification_type=NotificationType.TRANSACIONAL,
            email_subject="Assunto Original",
            email_body_html="Corpo original",
            status=TemplateStatus.ATIVO,
            version=5,
            sent_count=0,
            delivered_count=0,
            opened_count=0,
            clicked_count=0,
            bounced_count=0,
            unsubscribed_count=0,
            priority=3,
            send_delay_minutes=0,
            batch_size=100,
        )
        clone = original.clone(new_codigo="CLONE")
        assert clone.codigo == "CLONE"
        assert clone.email_body_html == original.email_body_html
        assert clone.status == TemplateStatus.RASCUNHO
        assert clone.parent_template_id == original.id

    def test_template_record_metrics(self):
        """Testa incremento de metricas via record_send/record_open."""
        template = NotificationTemplate(
            codigo="METRICS_TEST",
            nome="Template Metricas",
            notification_type=NotificationType.LEMBRETE,
            email_body_html="Teste de metricas",
            sent_count=0,
            delivered_count=0,
            opened_count=0,
            clicked_count=0,
            bounced_count=0,
            unsubscribed_count=0,
            version=1,
            priority=3,
            send_delay_minutes=0,
            batch_size=100,
        )
        template.record_send()
        template.record_send()
        template.record_open()
        assert template.sent_count == 2
        assert template.opened_count == 1

    def test_template_multicanal(self):
        """Testa templates de diferentes canais."""
        channels = [
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
            NotificationChannel.PUSH,
            NotificationChannel.WHATSAPP,
            NotificationChannel.SLACK,
            NotificationChannel.WEBHOOK,
            NotificationChannel.IN_APP,
            NotificationChannel.TELEGRAM,
        ]
        for channel in channels:
            template = NotificationTemplate(
                codigo=f"TEMPLATE_{channel.value.upper()}",
                nome=f"Template {channel.value}",
                notification_type=NotificationType.SISTEMA,
            )
            assert template.notification_type == NotificationType.SISTEMA


class TestEnums:
    """Testes dos Enums do modulo."""

    def test_tenant_status_values(self):
        """Testa valores de TenantStatus."""
        assert TenantStatus.ATIVO.value == "ativo"
        assert TenantStatus.INATIVO.value == "inativo"
        assert TenantStatus.SUSPENSO.value == "suspenso"
        assert TenantStatus.BLOQUEADO.value == "bloqueado"
        assert TenantStatus.TRIAL.value == "trial"
        assert TenantStatus.CANCELADO.value == "cancelado"

    def test_tenant_plan_values(self):
        """Testa valores de TenantPlan."""
        assert TenantPlan.FREE.value == "free"
        assert TenantPlan.STARTER.value == "starter"
        assert TenantPlan.PROFESSIONAL.value == "professional"
        assert TenantPlan.ENTERPRISE.value == "enterprise"
        assert TenantPlan.CUSTOM.value == "custom"

    def test_rollout_strategy_values(self):
        """Testa valores de RolloutStrategy."""
        assert RolloutStrategy.ALL.value == "all"
        assert RolloutStrategy.NONE.value == "none"
        assert RolloutStrategy.PERCENTAGE.value == "percentage"
        assert RolloutStrategy.GRADUAL.value == "gradual"
        assert RolloutStrategy.TENANT_LIST.value == "tenant_list"
        assert RolloutStrategy.USER_LIST.value == "user_list"
        assert RolloutStrategy.ATTRIBUTE.value == "attribute"

    def test_notification_channel_values(self):
        """Testa valores de NotificationChannel."""
        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.SMS.value == "sms"
        assert NotificationChannel.PUSH.value == "push"
        assert NotificationChannel.WHATSAPP.value == "whatsapp"
        assert NotificationChannel.SLACK.value == "slack"
        assert NotificationChannel.WEBHOOK.value == "webhook"
        assert NotificationChannel.IN_APP.value == "in_app"
        assert NotificationChannel.TELEGRAM.value == "telegram"
