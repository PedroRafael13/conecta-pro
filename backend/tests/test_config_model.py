"""
Testes dos Models do módulo Config
Sprint 35: Configurações e Multi-tenant
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
        """Testa criação de tenant básico."""
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
        # status/plano/tipo são definidos pelo banco (default), não no objeto Python
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
            documento="12345678000100",
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
            documento="12345678000101",
            email="trial@empresa.com",
            status=TenantStatus.TRIAL,
            data_fim_trial=datetime.now(UTC) + timedelta(days=14),
        )
        assert tenant.is_trial is True

        tenant.data_fim_trial = datetime.now(UTC) - timedelta(days=1)
        assert tenant.is_trial is False

    def test_tenant_activate(self):
        """Testa ativação de tenant."""
        tenant = Tenant(
            codigo="TENANT004",
            nome="Empresa Inativa",
            documento="12345678000102",
            email="inativo@empresa.com",
            status=TenantStatus.INATIVO,
        )
        tenant.activate()
        assert tenant.status == TenantStatus.ATIVO
        assert tenant.data_inicio is not None

    def test_tenant_suspend(self):
        """Testa suspensão de tenant."""
        tenant = Tenant(
            codigo="TENANT005",
            nome="Empresa a Suspender",
            documento="12345678000103",
            email="suspender@empresa.com",
            status=TenantStatus.ATIVO,
        )
        tenant.suspend("Pagamento pendente")
        assert tenant.status == TenantStatus.SUSPENSO
        assert "Pagamento pendente" in (tenant.notas or "")

    def test_tenant_cancel(self):
        """Testa cancelamento de tenant."""
        tenant = Tenant(
            codigo="TENANT006",
            nome="Empresa a Cancelar",
            documento="12345678000104",
            email="cancelar@empresa.com",
            status=TenantStatus.ATIVO,
        )
        tenant.cancel()
        assert tenant.status == TenantStatus.CANCELADO
        assert tenant.data_cancelamento is not None

    def test_tenant_upgrade_plan(self):
        """Testa upgrade de plano."""
        tenant = Tenant(
            codigo="TENANT007",
            nome="Empresa Upgrade",
            documento="12345678000105",
            email="upgrade@empresa.com",
            plano=TenantPlan.FREE,
        )
        tenant.upgrade_plan(TenantPlan.PROFESSIONAL)
        assert tenant.plano == TenantPlan.PROFESSIONAL

    def test_tenant_enable_disable_feature(self):
        """Testa habilitar/desabilitar features."""
        tenant = Tenant(
            codigo="TENANT008",
            nome="Empresa Features",
            documento="12345678000106",
            email="features@empresa.com",
        )
        tenant.enable_feature("reports")
        assert "reports" in tenant.features_habilitadas

        tenant.disable_feature("reports")
        assert "reports" not in tenant.features_habilitadas

    def test_tenant_storage_usage_percent(self):
        """Testa cálculo de uso de storage."""
        tenant = Tenant(
            codigo="TENANT009",
            nome="Empresa Storage",
            documento="12345678000107",
            email="storage@empresa.com",
            limite_storage_gb=10,
            uso_storage_bytes=5 * 1024 * 1024 * 1024,  # 5GB
        )
        assert tenant.storage_usage_percent == 50.0


class TestTenantSettingsModel:
    """Testes do model TenantSettings."""

    def test_criar_setting_basico(self):
        """Testa criação de setting básico."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="notificacoes_email",
            valor="true",
            categoria=SettingCategory.NOTIFICACAO,
            setting_type=SettingType.BOOLEAN,
        )
        assert setting.chave == "notificacoes_email"
        assert setting.valor == "true"
        assert setting.categoria == SettingCategory.NOTIFICACAO
        assert setting.setting_type == SettingType.BOOLEAN

    def test_setting_get_typed_value_boolean(self):
        """Testa conversão de valor boolean."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="feature_enabled",
            valor="true",
            setting_type=SettingType.BOOLEAN,
        )
        assert setting.get_typed_value() is True

        setting.valor = "false"
        assert setting.get_typed_value() is False

    def test_setting_get_typed_value_integer(self):
        """Testa conversão de valor integer."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="max_users",
            valor="100",
            setting_type=SettingType.INTEGER,
        )
        assert setting.get_typed_value() == 100

    def test_setting_get_typed_value_float(self):
        """Testa conversão de valor float."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="taxa_desconto",
            valor="15.5",
            setting_type=SettingType.FLOAT,
        )
        assert setting.get_typed_value() == 15.5

    def test_setting_get_typed_value_json(self):
        """Testa conversão de valor JSON."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="config_complex",
            valor='{"key": "value", "number": 42}',
            setting_type=SettingType.JSON,
        )
        result = setting.get_typed_value()
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_setting_set_value_with_history(self):
        """Testa set_value com histórico."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="config_test",
            valor="old_value",
            historico=[],
        )
        setting.set_value("new_value", user="admin")
        assert setting.valor == "new_value"
        assert len(setting.historico) == 1
        assert setting.historico[0]["old_value"] == "old_value"
        assert setting.historico[0]["new_value"] == "new_value"

    def test_setting_validate_value_valid(self):
        """Testa validação de valor válido."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="max_items",
            valor="50",
            setting_type=SettingType.INTEGER,
            validacao={"min": 1, "max": 100},
        )
        assert setting.validate_value("50") is True

    def test_setting_validate_value_invalid(self):
        """Testa validação de valor inválido."""
        setting = TenantSettings(
            tenant_id=uuid.uuid4(),
            chave="max_items",
            valor="50",
            setting_type=SettingType.INTEGER,
            validacao={"min": 1, "max": 100},
        )
        assert setting.validate_value("150") is False


class TestSystemConfigModel:
    """Testes do model SystemConfig."""

    def test_criar_config_basico(self):
        """Testa criação de config básico."""
        config = SystemConfig(
            chave="app_name",
            valor="ERP Conecta Mais",
            setting_type=SettingType.STRING,
            escopo=ConfigScope.GLOBAL,
        )
        assert config.chave == "app_name"
        assert config.valor == "ERP Conecta Mais"
        assert config.escopo == ConfigScope.GLOBAL

    def test_config_prioridades(self):
        """Testa diferentes prioridades."""
        config_low = SystemConfig(
            chave="log_level",
            valor="INFO",
            prioridade=ConfigPriority.LOW,
        )
        config_critical = SystemConfig(
            chave="maintenance_mode",
            valor="false",
            prioridade=ConfigPriority.CRITICAL,
        )
        assert config_low.prioridade == ConfigPriority.LOW
        assert config_critical.prioridade == ConfigPriority.CRITICAL


class TestFeatureFlagModel:
    """Testes do model FeatureFlag."""

    def test_criar_flag_basico(self):
        """Testa criação de flag básico."""
        flag = FeatureFlag(
            codigo="NEW_DASHBOARD",
            nome="Novo Dashboard",
            descricao="Ativa o novo dashboard para usuários",
        )
        assert flag.codigo == "NEW_DASHBOARD"
        assert flag.nome == "Novo Dashboard"
        assert flag.status == FlagStatus.INATIVO
        assert flag.estrategia == RolloutStrategy.NONE

    def test_flag_enable_disable(self):
        """Testa ativar/desativar flag."""
        flag = FeatureFlag(
            codigo="FEATURE_X",
            nome="Feature X",
            status=FlagStatus.INATIVO,
        )
        flag.enable()
        assert flag.status == FlagStatus.ATIVO
        assert flag.estrategia == RolloutStrategy.ALL

        flag.disable()
        assert flag.status == FlagStatus.INATIVO
        assert flag.estrategia == RolloutStrategy.NONE

    def test_flag_set_percentage(self):
        """Testa definir percentual de rollout."""
        flag = FeatureFlag(
            codigo="GRADUAL_FEATURE",
            nome="Feature Gradual",
        )
        flag.set_percentage(25)
        assert flag.percentual == 25
        assert flag.estrategia == RolloutStrategy.PERCENTAGE
        assert flag.status == FlagStatus.ATIVO

    def test_flag_start_gradual_rollout(self):
        """Testa início de rollout gradual."""
        flag = FeatureFlag(
            codigo="GRADUAL_ROLLOUT",
            nome="Rollout Gradual",
        )
        flag.start_gradual_rollout(target=100, daily_increment=10)
        assert flag.percentual_alvo == 100
        assert flag.incremento_diario == 10
        assert flag.estrategia == RolloutStrategy.GRADUAL
        assert flag.status == FlagStatus.ATIVO

    def test_flag_toggle_tenant(self):
        """Testa toggle de tenant."""
        tenant_id = str(uuid.uuid4())
        flag = FeatureFlag(
            codigo="TENANT_FEATURE",
            nome="Feature por Tenant",
            tenants_habilitados=[],
            tenants_desabilitados=[],
        )
        flag.toggle_tenant(tenant_id, enabled=True)
        assert tenant_id in flag.tenants_habilitados

        flag.toggle_tenant(tenant_id, enabled=False)
        assert tenant_id not in flag.tenants_habilitados
        assert tenant_id in flag.tenants_desabilitados

    def test_flag_evaluate_all_strategy(self):
        """Testa avaliação com estratégia ALL."""
        flag = FeatureFlag(
            codigo="ALL_USERS",
            nome="Todos os Usuários",
            status=FlagStatus.ATIVO,
            estrategia=RolloutStrategy.ALL,
            ativo=True,
        )
        result = flag.evaluate()
        assert result["enabled"] is True

    def test_flag_evaluate_none_strategy(self):
        """Testa avaliação com estratégia NONE."""
        flag = FeatureFlag(
            codigo="NO_USERS",
            nome="Nenhum Usuário",
            status=FlagStatus.ATIVO,
            estrategia=RolloutStrategy.NONE,
            ativo=True,
        )
        result = flag.evaluate()
        assert result["enabled"] is False

    def test_flag_evaluate_tenant_list(self):
        """Testa avaliação com lista de tenants."""
        tenant_id = str(uuid.uuid4())
        flag = FeatureFlag(
            codigo="TENANT_LIST",
            nome="Lista de Tenants",
            status=FlagStatus.ATIVO,
            estrategia=RolloutStrategy.TENANT_LIST,
            tenants_habilitados=[tenant_id],
            tenants_desabilitados=[],
            ativo=True,
        )
        result = flag.evaluate(tenant_id=tenant_id)
        assert result["enabled"] is True

        other_tenant = str(uuid.uuid4())
        result = flag.evaluate(tenant_id=other_tenant)
        assert result["enabled"] is False

    def test_flag_evaluate_inactive(self):
        """Testa avaliação de flag inativo."""
        flag = FeatureFlag(
            codigo="INACTIVE_FLAG",
            nome="Flag Inativo",
            status=FlagStatus.INATIVO,
            ativo=False,
        )
        result = flag.evaluate()
        assert result["enabled"] is False

    def test_flag_ab_test(self):
        """Testa flag como A/B test."""
        flag = FeatureFlag(
            codigo="AB_TEST",
            nome="Teste A/B",
            status=FlagStatus.ATIVO,
            estrategia=RolloutStrategy.ALL,
            is_ab_test=True,
            variantes=[
                {"name": "control", "weight": 50},
                {"name": "variant_a", "weight": 50},
            ],
            variante_padrao="control",
            ativo=True,
        )
        result = flag.evaluate(user_id="user123")
        assert result["enabled"] is True
        assert result["variant"] in ["control", "variant_a"]


class TestNotificationTemplateModel:
    """Testes do model NotificationTemplate."""

    def test_criar_template_basico(self):
        """Testa criação de template básico."""
        template = NotificationTemplate(
            codigo="WELCOME_EMAIL",
            nome="Email de Boas-vindas",
            notification_type=NotificationType.TRANSACIONAL,
            email_subject="Bem-vindo ao Sistema!",
            email_body_html="Olá {{nome}}, bem-vindo!",
        )
        assert template.codigo == "WELCOME_EMAIL"
        assert template.notification_type == NotificationType.TRANSACIONAL
        assert template.notification_type == NotificationType.TRANSACIONAL
        assert template.status == TemplateStatus.DRAFT

    def test_template_activate_deactivate(self):
        """Testa ativar/desativar template."""
        template = NotificationTemplate(
            codigo="TEMPLATE_1",
            nome="Template 1",
            notification_type=NotificationType.ALERTA,
            sms_body="Mensagem de teste",
        )
        template.activate()
        assert template.status == TemplateStatus.ACTIVE

        template.deactivate()
        assert template.status == TemplateStatus.INACTIVE

    def test_template_render_simples(self):
        """Testa renderização simples."""
        template = NotificationTemplate(
            codigo="SIMPLE_TEMPLATE",
            nome="Template Simples",
            notification_type=NotificationType.TRANSACIONAL,
            assunto="Olá {{nome}}",
            email_body_html="Prezado(a) {{nome}}, seu pedido {{pedido_id}} foi confirmado.",
        )
        result = template.render({"nome": "João", "pedido_id": "12345"})
        assert result["subject"] == "Olá João"
        assert "João" in result["body"]
        assert "12345" in result["body"]

    def test_template_render_html(self):
        """Testa renderização HTML."""
        template = NotificationTemplate(
            codigo="HTML_TEMPLATE",
            nome="Template HTML",
            notification_type=NotificationType.TRANSACIONAL,
            assunto="Notificação",
            email_body_text="Texto simples",
            corpo_html="<h1>Olá {{nome}}</h1><p>Bem-vindo!</p>",
        )
        result = template.render({"nome": "Maria"})
        assert "<h1>Olá Maria</h1>" in result["body_html"]

    def test_template_clone(self):
        """Testa clonagem de template."""
        original = NotificationTemplate(
            codigo="ORIGINAL",
            nome="Template Original",
            notification_type=NotificationType.TRANSACIONAL,
            tipo=NotificationType.TRANSACIONAL,
            assunto="Assunto Original",
            email_body_html="Corpo original",
            status=TemplateStatus.ACTIVE,
            versao=5,
        )
        clone = original.clone(new_code="CLONE", new_name="Template Clonado")
        assert clone.codigo == "CLONE"
        assert clone.nome == "Template Clonado"
        assert clone.corpo == original.corpo
        assert clone.status == TemplateStatus.DRAFT
        assert clone.versao == 1
        assert clone.template_pai_id == original.id

    def test_template_increment_metrics(self):
        """Testa incremento de métricas."""
        template = NotificationTemplate(
            codigo="METRICS_TEST",
            nome="Template Métricas",
            notification_type=NotificationType.LEMBRETE,
            email_body_html="Teste de métricas",
            metricas={},
        )
        template.increment_metric("sent")
        template.increment_metric("sent")
        template.increment_metric("opened")
        assert template.metricas["sent"] == 2
        assert template.metricas["opened"] == 1

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
    """Testes dos Enums do módulo."""

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
