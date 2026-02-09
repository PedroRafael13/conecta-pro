"""
modules/fase5/mcp_servers/config.py - MCP Server Configuration
=============================================================
Configuracao dos servidores MCP
"""

from dataclasses import dataclass, field
from enum import StrEnum


class MCPServerType(StrEnum):
    """Tipos de servidores MCP."""

    EMAIL_INTELLIGENCE = "email_intelligence"
    CCT_COMPLIANCE = "cct_compliance"
    INTEGRATION_HUB = "integration_hub"
    ANALYTICS_ENGINE = "analytics_engine"
    SECURITY_MANAGER = "security_manager"


@dataclass
class MCPServerConfig:
    """Configuracao de um servidor MCP."""

    server_type: MCPServerType
    name: str
    description: str
    port: int
    host: str = "localhost"

    # Capabilities
    capabilities: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)

    # Auth
    requires_auth: bool = True
    api_key_header: str = "X-API-Key"

    # Limits
    max_requests_per_minute: int = 100
    max_tokens_per_request: int = 4096

    # Health
    health_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"


# Configuracoes dos servidores MCP Fase 5
MCP_SERVERS_CONFIG: dict[MCPServerType, MCPServerConfig] = {
    MCPServerType.EMAIL_INTELLIGENCE: MCPServerConfig(
        server_type=MCPServerType.EMAIL_INTELLIGENCE,
        name="Email Intelligence MCP Server",
        description="Servidor MCP para analise inteligente de emails",
        port=9001,
        capabilities=["email_analysis", "entity_extraction", "sentiment_analysis"],
        tools=["analyze_email", "generate_response", "get_email_context", "classify_email", "extract_entities"],
        resources=["email_templates", "classification_models", "entity_patterns"],
    ),
    MCPServerType.CCT_COMPLIANCE: MCPServerConfig(
        server_type=MCPServerType.CCT_COMPLIANCE,
        name="CCT Compliance MCP Server",
        description="Servidor MCP para compliance CCT SINDCOND 2026",
        port=9002,
        capabilities=["salary_validation", "benefit_check", "cost_calculation"],
        tools=["validate_salary", "validate_complete", "calculate_cost", "generate_proposal", "list_positions"],
        resources=["salary_table_2026", "benefits_table", "position_mapping"],
    ),
    MCPServerType.INTEGRATION_HUB: MCPServerConfig(
        server_type=MCPServerType.INTEGRATION_HUB,
        name="Integration Hub MCP Server",
        description="Servidor MCP para integracao cross-phase",
        port=9003,
        capabilities=["workflow_orchestration", "message_routing", "system_monitoring"],
        tools=["start_workflow", "route_message", "get_system_status", "aggregate_metrics", "health_check"],
        resources=["workflow_definitions", "phase_mappings", "agent_registry"],
    ),
    MCPServerType.ANALYTICS_ENGINE: MCPServerConfig(
        server_type=MCPServerType.ANALYTICS_ENGINE,
        name="Analytics Engine MCP Server",
        description="Servidor MCP para analytics e BI",
        port=9004,
        capabilities=["data_analysis", "report_generation", "predictions"],
        tools=["analyze_data", "generate_report", "predict_trend", "get_insights"],
        resources=["analytics_models", "report_templates", "historical_data"],
    ),
    MCPServerType.SECURITY_MANAGER: MCPServerConfig(
        server_type=MCPServerType.SECURITY_MANAGER,
        name="Security Manager MCP Server",
        description="Servidor MCP para seguranca e auditoria",
        port=9005,
        capabilities=["security_scan", "audit_trail", "compliance_check"],
        tools=["scan_security", "check_compliance", "audit_action", "validate_access"],
        resources=["security_rules", "audit_logs", "compliance_policies"],
    ),
}
