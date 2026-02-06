# Sprint 05: Marketplace de Integrações

## 🎯 Objetivo Principal
Implementar um marketplace completo de integrações que permita conectar o Conecta PRO com dezenas de serviços externos através de conectores pré-construídos e personalizáveis, facilitando a expansão do ecossistema.

## 📋 Especificações Técnicas

### Funcionalidades Core
- **Catálogo de Integrações**: Browser de conectores disponíveis
- **Gerenciador de Conectores**: Instalação, configuração e monitoramento
- **API Gateway Unificada**: Proxy para todos os serviços externos
- **Sistema de Autenticação**: OAuth2, API Keys, Basic Auth por conector
- **Transformation Engine**: Mapeamento e transformação de dados entre APIs
- **Monitoring & Logs**: Observabilidade completa das integrações
- **Marketplace SDK**: Kit para desenvolvedores criarem novos conectores
- **Version Control**: Versionamento e rollback de conectores
- **Rate Limiting**: Controle de taxa por conector e por cliente
- **Error Handling**: Sistema robusto de retry e fallback

### Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CONECTA PRO MARKETPLACE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │   FRONTEND  │    │  ADMIN API  │    │ PUBLIC API  │                │
│  │  DASHBOARD  │    │             │    │             │                │
│  └─────────────┘    └─────────────┘    └─────────────┘                │
│         │                   │                   │                       │
│         └─────────────────────┼───────────────────┘                       │
│                               │                                           │
│  ┌─────────────────────────────┼─────────────────────────────────────┐   │
│  │              MARKETPLACE CORE ENGINE                              │   │
│  │                             │                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ CONNECTOR   │  │ INTEGRATION │  │ EXECUTION   │              │   │
│  │  │ REGISTRY    │  │ MANAGER     │  │ ENGINE      │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ AUTH        │  │ TRANSFORM   │  │ MONITORING  │              │   │
│  │  │ MANAGER     │  │ ENGINE      │  │ & ALERTS    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│  ┌─────────────────────────────┼─────────────────────────────────────┐   │
│  │                    API GATEWAY                                   │   │
│  │                             │                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ RATE        │  │ REQUEST     │  │ RESPONSE    │              │   │
│  │  │ LIMITER     │  │ ROUTER      │  │ TRANSFORMER │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ CIRCUIT     │  │ RETRY       │  │ TIMEOUT     │              │   │
│  │  │ BREAKER     │  │ HANDLER     │  │ MANAGER     │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│                               ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │                     EXTERNAL SERVICES                            │     │
│  │                                                                   │     │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │     │
│  │  │ SALESFORCE│ │   SLACK   │ │  ZAPIER   │ │   TEAMS   │        │     │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │     │
│  │                                                                   │     │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │     │
│  │  │  HUBSPOT  │ │ WHATSAPP  │ │  MAILGUN  │ │ TYPEFORM  │        │     │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │     │
│  │                                                                   │     │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │     │
│  │  │   JIRA    │ │  GITHUB   │ │  STRIPE   │ │   ZOOM    │        │     │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │     │
│  └─────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🗄️ Modelos de Dados

### Connector Registry
```sql
-- Catálogo de conectores
CREATE TABLE connector_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL, -- 'CRM', 'Communication', 'Marketing', etc
    version VARCHAR(20) NOT NULL,
    logo_url VARCHAR(500),
    
    -- Configuração do conector
    endpoint_base_url VARCHAR(500),
    auth_type VARCHAR(50) NOT NULL, -- 'oauth2', 'api_key', 'basic', 'bearer'
    auth_config JSONB,
    
    -- Capabilities
    supports_webhooks BOOLEAN DEFAULT false,
    supports_realtime BOOLEAN DEFAULT false,
    rate_limit_per_minute INTEGER DEFAULT 60,
    
    -- Metadata
    provider VARCHAR(100),
    documentation_url VARCHAR(500),
    support_email VARCHAR(100),
    tags TEXT[],
    
    -- Status e controle
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'deprecated', 'beta'
    is_official BOOLEAN DEFAULT false,
    requires_approval BOOLEAN DEFAULT false,
    
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Instalações de conectores por usuário/empresa
CREATE TABLE user_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    connector_id UUID REFERENCES connector_registry(id) ON DELETE CASCADE,
    
    -- Configuração específica da instalação
    instance_name VARCHAR(100) NOT NULL,
    configuration JSONB,
    credentials JSONB, -- Encrypted
    
    -- Estado da integração
    status VARCHAR(20) DEFAULT 'configuring', -- 'configuring', 'active', 'paused', 'error'
    last_sync_at TIMESTAMPTZ,
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    
    -- Estatísticas
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, connector_id, instance_name)
);

-- Webhook endpoints para integrações
CREATE TABLE integration_webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES user_integrations(id) ON DELETE CASCADE,
    
    -- Configuração do webhook
    event_type VARCHAR(100) NOT NULL,
    endpoint_url VARCHAR(500) NOT NULL,
    secret_token VARCHAR(100),
    
    -- Controle
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMPTZ,
    trigger_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Log de execuções de integrações
CREATE TABLE integration_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES user_integrations(id) ON DELETE CASCADE,
    
    -- Dados da execução
    execution_type VARCHAR(50) NOT NULL, -- 'sync', 'webhook', 'manual'
    method VARCHAR(10) NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    
    -- Request/Response
    request_headers JSONB,
    request_body TEXT,
    response_status INTEGER,
    response_headers JSONB,
    response_body TEXT,
    
    -- Timing e performance
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    
    -- Status
    status VARCHAR(20) NOT NULL, -- 'pending', 'success', 'failed', 'timeout'
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transformações de dados
CREATE TABLE data_transformations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES user_integrations(id) ON DELETE CASCADE,
    
    -- Configuração da transformação
    name VARCHAR(100) NOT NULL,
    source_format VARCHAR(50), -- 'json', 'xml', 'csv'
    target_format VARCHAR(50),
    
    -- Mapeamento
    field_mappings JSONB, -- {"source_field": "target_field", ...}
    transformation_rules JSONB, -- Regras de transformação complexas
    
    -- Controle
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Marketplace analytics
CREATE TABLE marketplace_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificadores
    event_type VARCHAR(50) NOT NULL, -- 'install', 'uninstall', 'execution', 'error'
    connector_id UUID REFERENCES connector_registry(id),
    user_id UUID REFERENCES users(id),
    integration_id UUID REFERENCES user_integrations(id),
    
    -- Dados do evento
    event_data JSONB,
    user_agent VARCHAR(500),
    ip_address INET,
    
    -- Metadata
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_connector_registry_category ON connector_registry(category);
CREATE INDEX idx_connector_registry_status ON connector_registry(status);
CREATE INDEX idx_user_integrations_user_id ON user_integrations(user_id);
CREATE INDEX idx_user_integrations_status ON user_integrations(status);
CREATE INDEX idx_integration_executions_integration_id ON integration_executions(integration_id);
CREATE INDEX idx_integration_executions_started_at ON integration_executions(started_at);
CREATE INDEX idx_marketplace_analytics_event_type ON marketplace_analytics(event_type);
CREATE INDEX idx_marketplace_analytics_occurred_at ON marketplace_analytics(occurred_at);
```

## 🚀 Implementação Core

### 1. Marketplace Engine Principal

```python
# app/marketplace/engine.py
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import aiohttp
from cryptography.fernet import Fernet

@dataclass
class ConnectorSpec:
    """Especificação de um conector"""
    id: str
    name: str
    display_name: str
    category: str
    version: str
    auth_type: str
    auth_config: Dict
    capabilities: Dict
    endpoints: Dict
    transformations: Dict

@dataclass
class IntegrationInstance:
    """Instância de uma integração configurada"""
    id: str
    user_id: str
    connector_id: str
    instance_name: str
    configuration: Dict
    credentials: Dict
    status: str
    
class MarketplaceEngine:
    """Engine principal do marketplace de integrações"""
    
    def __init__(self):
        self.connector_registry: Dict[str, ConnectorSpec] = {}
        self.active_integrations: Dict[str, IntegrationInstance] = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.session = aiohttp.ClientSession()
        
    async def initialize(self):
        """Inicializa o marketplace engine"""
        await self._load_connectors()
        await self._load_active_integrations()
        await self._start_health_monitor()
        
    async def _load_connectors(self):
        """Carrega conectores do registry"""
        # Conectores built-in
        self.connector_registry.update({
            "salesforce": ConnectorSpec(
                id="salesforce",
                name="salesforce",
                display_name="Salesforce CRM",
                category="CRM",
                version="1.0.0",
                auth_type="oauth2",
                auth_config={
                    "authorization_url": "https://login.salesforce.com/services/oauth2/authorize",
                    "token_url": "https://login.salesforce.com/services/oauth2/token",
                    "scopes": ["api", "refresh_token"]
                },
                capabilities={
                    "webhooks": True,
                    "realtime": False,
                    "rate_limit": 1000
                },
                endpoints={
                    "leads": "/services/data/v58.0/sobjects/Lead",
                    "accounts": "/services/data/v58.0/sobjects/Account",
                    "opportunities": "/services/data/v58.0/sobjects/Opportunity"
                },
                transformations={
                    "lead_to_contact": {
                        "firstName": "first_name",
                        "lastName": "last_name", 
                        "email": "email",
                        "company": "company_name"
                    }
                }
            ),
            
            "slack": ConnectorSpec(
                id="slack",
                name="slack",
                display_name="Slack",
                category="Communication",
                version="1.0.0",
                auth_type="oauth2",
                auth_config={
                    "authorization_url": "https://slack.com/oauth/v2/authorize",
                    "token_url": "https://slack.com/api/oauth.v2.access",
                    "scopes": ["chat:write", "channels:read", "users:read"]
                },
                capabilities={
                    "webhooks": True,
                    "realtime": True,
                    "rate_limit": 100
                },
                endpoints={
                    "send_message": "/api/chat.postMessage",
                    "channels": "/api/conversations.list",
                    "users": "/api/users.list"
                },
                transformations={}
            ),
            
            "hubspot": ConnectorSpec(
                id="hubspot",
                name="hubspot",
                display_name="HubSpot",
                category="CRM",
                version="1.0.0",
                auth_type="oauth2",
                auth_config={
                    "authorization_url": "https://app.hubspot.com/oauth/authorize",
                    "token_url": "https://api.hubapi.com/oauth/v1/token",
                    "scopes": ["contacts", "content"]
                },
                capabilities={
                    "webhooks": True,
                    "realtime": False,
                    "rate_limit": 150
                },
                endpoints={
                    "contacts": "/crm/v3/objects/contacts",
                    "companies": "/crm/v3/objects/companies",
                    "deals": "/crm/v3/objects/deals"
                },
                transformations={}
            )
        })
        
    async def install_connector(self, user_id: str, connector_id: str, 
                               instance_name: str, configuration: Dict) -> IntegrationInstance:
        """Instala e configura um conector para um usuário"""
        
        if connector_id not in self.connector_registry:
            raise ValueError(f"Connector {connector_id} not found")
            
        connector = self.connector_registry[connector_id]
        
        # Cria instância da integração
        integration = IntegrationInstance(
            id=f"{user_id}_{connector_id}_{instance_name}",
            user_id=user_id,
            connector_id=connector_id,
            instance_name=instance_name,
            configuration=configuration,
            credentials={},
            status="configuring"
        )
        
        # Salva no banco de dados
        await self._save_integration_to_db(integration)
        
        # Adiciona ao cache ativo
        self.active_integrations[integration.id] = integration
        
        return integration
        
    async def configure_authentication(self, integration_id: str, 
                                     auth_data: Dict) -> bool:
        """Configura autenticação para uma integração"""
        
        integration = self.active_integrations.get(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
            
        connector = self.connector_registry[integration.connector_id]
        
        # Processa diferentes tipos de autenticação
        if connector.auth_type == "oauth2":
            credentials = await self._handle_oauth2_auth(connector, auth_data)
        elif connector.auth_type == "api_key":
            credentials = {"api_key": auth_data["api_key"]}
        elif connector.auth_type == "bearer":
            credentials = {"token": auth_data["token"]}
        else:
            raise ValueError(f"Unsupported auth type: {connector.auth_type}")
        
        # Encrypta e salva credenciais
        encrypted_credentials = self._encrypt_credentials(credentials)
        integration.credentials = encrypted_credentials
        integration.status = "active"
        
        await self._update_integration_in_db(integration)
        
        return True
        
    async def execute_integration_call(self, integration_id: str, 
                                     endpoint: str, method: str = "GET",
                                     data: Optional[Dict] = None) -> Dict:
        """Executa uma chamada para uma integração"""
        
        integration = self.active_integrations.get(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
            
        if integration.status != "active":
            raise ValueError(f"Integration {integration_id} is not active")
            
        connector = self.connector_registry[integration.connector_id]
        
        # Descriptografa credenciais
        credentials = self._decrypt_credentials(integration.credentials)
        
        # Constrói URL completa
        base_url = integration.configuration.get("base_url", "")
        full_url = f"{base_url}{endpoint}"
        
        # Prepara headers de autenticação
        headers = await self._prepare_auth_headers(connector, credentials)
        
        # Executa chamada
        execution_start = datetime.utcnow()
        
        try:
            async with self.session.request(
                method=method,
                url=full_url,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                execution_end = datetime.utcnow()
                duration_ms = int((execution_end - execution_start).total_seconds() * 1000)
                
                response_data = await response.json()
                
                # Log da execução
                await self._log_execution(
                    integration_id=integration_id,
                    method=method,
                    endpoint=endpoint,
                    request_data=data,
                    response_status=response.status,
                    response_data=response_data,
                    duration_ms=duration_ms,
                    status="success" if response.status < 400 else "failed"
                )
                
                return {
                    "status": response.status,
                    "data": response_data,
                    "duration_ms": duration_ms
                }
                
        except Exception as e:
            execution_end = datetime.utcnow()
            duration_ms = int((execution_end - execution_start).total_seconds() * 1000)
            
            await self._log_execution(
                integration_id=integration_id,
                method=method,
                endpoint=endpoint,
                request_data=data,
                response_status=0,
                response_data=None,
                duration_ms=duration_ms,
                status="failed",
                error_message=str(e)
            )
            
            raise
    
    async def sync_integration_data(self, integration_id: str, 
                                   sync_config: Dict) -> Dict:
        """Executa sincronização de dados de uma integração"""
        
        integration = self.active_integrations.get(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        connector = self.connector_registry[integration.connector_id]
        
        # Obtém dados da fonte
        source_data = await self.execute_integration_call(
            integration_id=integration_id,
            endpoint=sync_config["source_endpoint"],
            method="GET"
        )
        
        # Aplica transformações se configuradas
        if sync_config.get("apply_transformations", False):
            transformed_data = await self._apply_data_transformations(
                integration_id, source_data["data"], sync_config.get("transformation_id")
            )
        else:
            transformed_data = source_data["data"]
        
        # Salva dados localmente se configurado
        if sync_config.get("save_local", False):
            await self._save_synced_data(integration_id, transformed_data)
        
        # Atualiza timestamp da última sincronização
        integration.status = "active"
        await self._update_integration_in_db(integration)
        
        return {
            "synced_records": len(transformed_data) if isinstance(transformed_data, list) else 1,
            "last_sync": datetime.utcnow().isoformat(),
            "status": "success"
        }
    
    async def _apply_data_transformations(self, integration_id: str, 
                                        data: Any, transformation_id: Optional[str] = None) -> Any:
        """Aplica transformações de dados configuradas"""
        
        if not transformation_id:
            return data
        
        # Carrega regras de transformação do banco
        transformation_rules = await self._get_transformation_rules(integration_id, transformation_id)
        
        if not transformation_rules:
            return data
        
        # Aplica transformações
        if isinstance(data, list):
            return [self._transform_record(record, transformation_rules) for record in data]
        else:
            return self._transform_record(data, transformation_rules)
    
    def _transform_record(self, record: Dict, rules: Dict) -> Dict:
        """Transforma um registro individual"""
        transformed = {}
        
        for source_field, target_field in rules.get("field_mappings", {}).items():
            if source_field in record:
                transformed[target_field] = record[source_field]
        
        # Aplica regras de transformação complexas
        for rule in rules.get("transformation_rules", []):
            if rule["type"] == "concat":
                transformed[rule["target"]] = " ".join([
                    str(record.get(field, "")) for field in rule["sources"]
                ])
            elif rule["type"] == "format":
                transformed[rule["target"]] = rule["format"].format(**record)
        
        return transformed
    
    async def _handle_oauth2_auth(self, connector: ConnectorSpec, auth_data: Dict) -> Dict:
        """Processa autenticação OAuth2"""
        
        auth_config = connector.auth_config
        
        # Troca authorization code por access token
        token_data = {
            "grant_type": "authorization_code",
            "code": auth_data["code"],
            "client_id": auth_data["client_id"],
            "client_secret": auth_data["client_secret"],
            "redirect_uri": auth_data.get("redirect_uri")
        }
        
        async with self.session.post(
            auth_config["token_url"],
            data=token_data
        ) as response:
            
            if response.status != 200:
                raise ValueError(f"OAuth2 token exchange failed: {response.status}")
            
            token_response = await response.json()
            
            return {
                "access_token": token_response["access_token"],
                "refresh_token": token_response.get("refresh_token"),
                "token_type": token_response.get("token_type", "Bearer"),
                "expires_in": token_response.get("expires_in"),
                "scope": token_response.get("scope")
            }
    
    async def _prepare_auth_headers(self, connector: ConnectorSpec, credentials: Dict) -> Dict:
        """Prepara headers de autenticação para uma chamada"""
        
        headers = {"Content-Type": "application/json"}
        
        if connector.auth_type == "oauth2":
            token_type = credentials.get("token_type", "Bearer")
            access_token = credentials["access_token"]
            headers["Authorization"] = f"{token_type} {access_token}"
            
        elif connector.auth_type == "api_key":
            headers["Authorization"] = f"Bearer {credentials['api_key']}"
            
        elif connector.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {credentials['token']}"
        
        return headers
    
    def _encrypt_credentials(self, credentials: Dict) -> Dict:
        """Encrypta credenciais sensíveis"""
        encrypted = {}
        for key, value in credentials.items():
            if isinstance(value, str):
                encrypted[key] = self.cipher_suite.encrypt(value.encode()).decode()
            else:
                encrypted[key] = value
        return encrypted
    
    def _decrypt_credentials(self, encrypted_credentials: Dict) -> Dict:
        """Descriptografa credenciais"""
        decrypted = {}
        for key, value in encrypted_credentials.items():
            if isinstance(value, str) and key in ["access_token", "refresh_token", "api_key", "token"]:
                try:
                    decrypted[key] = self.cipher_suite.decrypt(value.encode()).decode()
                except:
                    decrypted[key] = value  # Fallback se não conseguir descriptografar
            else:
                decrypted[key] = value
        return decrypted

# Singleton do marketplace engine
marketplace_engine = MarketplaceEngine()
```

### 2. API Gateway para Integrações

```python
# app/marketplace/gateway.py
import asyncio
import time
from typing import Dict, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass
import aiohttp
from datetime import datetime, timedelta

@dataclass
class RateLimit:
    """Configuração de rate limiting"""
    requests_per_minute: int
    requests_per_hour: int
    burst_size: int

class CircuitBreakerState:
    """Estado do circuit breaker"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def record_success(self):
        """Registra uma execução bem-sucedida"""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Registra uma falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def can_execute(self) -> bool:
        """Verifica se pode executar uma operação"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "half_open"
                return True
            return False
        else:  # half_open
            return True

class IntegrationGateway:
    """Gateway unificado para todas as integrações"""
    
    def __init__(self):
        self.rate_limiters = defaultdict(lambda: deque())
        self.circuit_breakers = defaultdict(CircuitBreakerState)
        self.session = aiohttp.ClientSession()
        self.request_queue = asyncio.Queue()
        self.workers = []
        
    async def start(self, num_workers: int = 5):
        """Inicia o gateway com workers para processar requisições"""
        for _ in range(num_workers):
            worker = asyncio.create_task(self._process_requests())
            self.workers.append(worker)
    
    async def stop(self):
        """Para o gateway"""
        for worker in self.workers:
            worker.cancel()
        await self.session.close()
    
    async def execute_request(self, integration_id: str, request_data: Dict) -> Dict:
        """Executa uma requisição através do gateway"""
        
        # Verifica rate limiting
        if not self._check_rate_limit(integration_id, request_data.get("rate_limit", {})):
            raise Exception("Rate limit exceeded")
        
        # Verifica circuit breaker
        circuit_breaker = self.circuit_breakers[integration_id]
        if not circuit_breaker.can_execute():
            raise Exception("Circuit breaker open - service unavailable")
        
        # Adiciona à fila de processamento
        future = asyncio.Future()
        await self.request_queue.put({
            "integration_id": integration_id,
            "request_data": request_data,
            "future": future
        })
        
        # Aguarda resultado
        return await future
    
    async def _process_requests(self):
        """Worker para processar requisições da fila"""
        while True:
            try:
                # Pega próxima requisição da fila
                item = await self.request_queue.get()
                integration_id = item["integration_id"]
                request_data = item["request_data"]
                future = item["future"]
                
                try:
                    # Executa a requisição
                    result = await self._execute_single_request(integration_id, request_data)
                    
                    # Registra sucesso no circuit breaker
                    self.circuit_breakers[integration_id].record_success()
                    
                    # Retorna resultado
                    future.set_result(result)
                    
                except Exception as e:
                    # Registra falha no circuit breaker
                    self.circuit_breakers[integration_id].record_failure()
                    
                    # Retorna erro
                    future.set_exception(e)
                
                # Marca tarefa como concluída
                self.request_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in request worker: {e}")
    
    async def _execute_single_request(self, integration_id: str, request_data: Dict) -> Dict:
        """Executa uma única requisição HTTP"""
        
        method = request_data.get("method", "GET")
        url = request_data["url"]
        headers = request_data.get("headers", {})
        data = request_data.get("data")
        timeout = request_data.get("timeout", 30)
        
        # Adiciona headers padrão do gateway
        headers.update({
            "User-Agent": "ConectaPRO-Gateway/1.0",
            "X-Integration-ID": integration_id,
            "X-Request-ID": request_data.get("request_id", "")
        })
        
        start_time = time.time()
        
        try:
            # Executa requisição com retry automático
            result = await self._execute_with_retry(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=timeout),
                max_retries=request_data.get("max_retries", 3)
            )
            
            duration = time.time() - start_time
            
            return {
                "status": "success",
                "data": result,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            return {
                "status": "error",
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_with_retry(self, method: str, url: str, headers: Dict,
                                 json: Optional[Dict], timeout: aiohttp.ClientTimeout,
                                 max_retries: int) -> Any:
        """Executa requisição com retry automático"""
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    timeout=timeout
                ) as response:
                    
                    if response.status < 500:  # Não retenta para erros 4xx
                        if response.status < 400:
                            return await response.json()
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message=f"HTTP {response.status}",
                                headers=response.headers
                            )
                    
                    # Para erros 5xx, retenta
                    if attempt == max_retries:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status} - Max retries exceeded",
                            headers=response.headers
                        )
                    
                    # Aguarda antes de tentar novamente (exponential backoff)
                    await asyncio.sleep(2 ** attempt)
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                
                if attempt == max_retries:
                    raise last_exception
                
                # Aguarda antes de tentar novamente
                await asyncio.sleep(2 ** attempt)
        
        # Se chegou aqui, todas as tentativas falharam
        raise last_exception
    
    def _check_rate_limit(self, integration_id: str, rate_limit_config: Dict) -> bool:
        """Verifica se a requisição está dentro do rate limit"""
        
        if not rate_limit_config:
            return True
        
        now = time.time()
        window = rate_limit_config.get("window", 60)  # 1 minuto por padrão
        max_requests = rate_limit_config.get("max_requests", 60)
        
        # Obtém fila de timestamps para esta integração
        request_times = self.rate_limiters[integration_id]
        
        # Remove requisições fora da janela de tempo
        while request_times and now - request_times[0] > window:
            request_times.popleft()
        
        # Verifica se pode fazer mais uma requisição
        if len(request_times) >= max_requests:
            return False
        
        # Adiciona timestamp da requisição atual
        request_times.append(now)
        return True

# Singleton do gateway
integration_gateway = IntegrationGateway()
```

### 3. APIs REST do Marketplace

```python
# app/marketplace/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..auth.dependencies import get_current_user
from ..models.user import User
from .engine import marketplace_engine
from .gateway import integration_gateway

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

# Modelos Pydantic para requests/responses
class ConnectorInstallRequest(BaseModel):
    connector_id: str
    instance_name: str
    configuration: Dict[str, Any]

class AuthConfigurationRequest(BaseModel):
    auth_data: Dict[str, Any]

class IntegrationCallRequest(BaseModel):
    endpoint: str
    method: str = "GET"
    data: Optional[Dict[str, Any]] = None

class SyncConfigurationRequest(BaseModel):
    source_endpoint: str
    apply_transformations: bool = False
    transformation_id: Optional[str] = None
    save_local: bool = False
    schedule: Optional[str] = None  # Cron expression

class ConnectorResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    category: str
    version: str
    logo_url: Optional[str]
    provider: str
    auth_type: str
    capabilities: Dict[str, Any]
    tags: List[str]
    is_official: bool
    documentation_url: Optional[str]

class IntegrationResponse(BaseModel):
    id: str
    connector_id: str
    instance_name: str
    status: str
    created_at: str
    last_sync_at: Optional[str]
    configuration: Dict[str, Any]

@router.get("/connectors", response_model=List[ConnectorResponse])
async def list_connectors(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    current_user: User = Depends(get_current_user)
):
    """Lista todos os conectores disponíveis no marketplace"""
    
    connectors = []
    
    for connector_id, connector in marketplace_engine.connector_registry.items():
        # Aplica filtros
        if category and connector.category.lower() != category.lower():
            continue
            
        if search and search.lower() not in f"{connector.display_name} {connector.description or ''}".lower():
            continue
        
        connectors.append(ConnectorResponse(
            id=connector.id,
            name=connector.name,
            display_name=connector.display_name,
            description=connector.description or "",
            category=connector.category,
            version=connector.version,
            logo_url=connector.logo_url,
            provider=connector.provider or "ConectaPRO",
            auth_type=connector.auth_type,
            capabilities=connector.capabilities,
            tags=getattr(connector, 'tags', []),
            is_official=getattr(connector, 'is_official', True),
            documentation_url=getattr(connector, 'documentation_url', None)
        ))
    
    return connectors

@router.get("/connectors/{connector_id}")
async def get_connector_details(
    connector_id: str,
    current_user: User = Depends(get_current_user)
):
    """Obtém detalhes completos de um conector"""
    
    if connector_id not in marketplace_engine.connector_registry:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    connector = marketplace_engine.connector_registry[connector_id]
    
    return {
        "connector": ConnectorResponse(
            id=connector.id,
            name=connector.name,
            display_name=connector.display_name,
            description=connector.description or "",
            category=connector.category,
            version=connector.version,
            logo_url=connector.logo_url,
            provider=connector.provider or "ConectaPRO",
            auth_type=connector.auth_type,
            capabilities=connector.capabilities,
            tags=getattr(connector, 'tags', []),
            is_official=getattr(connector, 'is_official', True),
            documentation_url=getattr(connector, 'documentation_url', None)
        ),
        "auth_config": connector.auth_config,
        "endpoints": connector.endpoints,
        "transformations": connector.transformations
    }

@router.post("/integrations/install")
async def install_integration(
    request: ConnectorInstallRequest,
    current_user: User = Depends(get_current_user)
):
    """Instala um conector para o usuário atual"""
    
    try:
        integration = await marketplace_engine.install_connector(
            user_id=str(current_user.id),
            connector_id=request.connector_id,
            instance_name=request.instance_name,
            configuration=request.configuration
        )
        
        return {
            "integration_id": integration.id,
            "status": integration.status,
            "message": "Connector installed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to install connector")

@router.post("/integrations/{integration_id}/configure-auth")
async def configure_integration_auth(
    integration_id: str,
    request: AuthConfigurationRequest,
    current_user: User = Depends(get_current_user)
):
    """Configura autenticação para uma integração"""
    
    try:
        success = await marketplace_engine.configure_authentication(
            integration_id=integration_id,
            auth_data=request.auth_data
        )
        
        if success:
            return {"status": "authenticated", "message": "Authentication configured successfully"}
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to configure authentication")

@router.get("/integrations", response_model=List[IntegrationResponse])
async def list_user_integrations(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user)
):
    """Lista todas as integrações do usuário"""
    
    user_integrations = []
    
    for integration_id, integration in marketplace_engine.active_integrations.items():
        if integration.user_id != str(current_user.id):
            continue
            
        if status and integration.status != status:
            continue
        
        user_integrations.append(IntegrationResponse(
            id=integration.id,
            connector_id=integration.connector_id,
            instance_name=integration.instance_name,
            status=integration.status,
            created_at=datetime.utcnow().isoformat(),  # Temporário - deveria vir do banco
            last_sync_at=None,  # Temporário - deveria vir do banco
            configuration=integration.configuration
        ))
    
    return user_integrations

@router.post("/integrations/{integration_id}/execute")
async def execute_integration_call(
    integration_id: str,
    request: IntegrationCallRequest,
    current_user: User = Depends(get_current_user)
):
    """Executa uma chamada para uma integração"""
    
    try:
        result = await marketplace_engine.execute_integration_call(
            integration_id=integration_id,
            endpoint=request.endpoint,
            method=request.method,
            data=request.data
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration call failed: {str(e)}")

@router.post("/integrations/{integration_id}/sync")
async def sync_integration_data(
    integration_id: str,
    request: SyncConfigurationRequest,
    current_user: User = Depends(get_current_user)
):
    """Executa sincronização de dados de uma integração"""
    
    try:
        result = await marketplace_engine.sync_integration_data(
            integration_id=integration_id,
            sync_config={
                "source_endpoint": request.source_endpoint,
                "apply_transformations": request.apply_transformations,
                "transformation_id": request.transformation_id,
                "save_local": request.save_local
            }
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data sync failed: {str(e)}")

@router.get("/integrations/{integration_id}/logs")
async def get_integration_logs(
    integration_id: str,
    limit: int = Query(50, description="Number of logs to return"),
    offset: int = Query(0, description="Pagination offset"),
    current_user: User = Depends(get_current_user)
):
    """Obtém logs de execução de uma integração"""
    
    # TODO: Implementar busca no banco de dados
    # Por agora, retorna dados mock
    
    logs = [
        {
            "id": "log_1",
            "timestamp": "2024-01-01T10:00:00Z",
            "method": "GET",
            "endpoint": "/api/contacts",
            "status": "success",
            "duration_ms": 150,
            "response_status": 200
        },
        {
            "id": "log_2", 
            "timestamp": "2024-01-01T09:30:00Z",
            "method": "POST",
            "endpoint": "/api/leads",
            "status": "failed",
            "duration_ms": 2000,
            "response_status": 500,
            "error_message": "Internal server error"
        }
    ]
    
    return {
        "logs": logs[offset:offset + limit],
        "total": len(logs),
        "has_more": offset + limit < len(logs)
    }

@router.get("/analytics/overview")
async def get_marketplace_analytics(
    current_user: User = Depends(get_current_user)
):
    """Obtém analytics do marketplace para o usuário"""
    
    # TODO: Implementar analytics reais do banco de dados
    
    return {
        "total_integrations": 5,
        "active_integrations": 3,
        "total_api_calls": 1250,
        "successful_calls": 1180,
        "failed_calls": 70,
        "average_response_time": 285,
        "top_connectors": [
            {"name": "Salesforce", "calls": 450},
            {"name": "Slack", "calls": 320},
            {"name": "HubSpot", "calls": 480}
        ],
        "recent_activity": [
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "action": "sync_completed",
                "connector": "Salesforce",
                "records": 150
            }
        ]
    }

@router.delete("/integrations/{integration_id}")
async def uninstall_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove uma integração"""
    
    try:
        # TODO: Implementar remoção real
        if integration_id in marketplace_engine.active_integrations:
            del marketplace_engine.active_integrations[integration_id]
        
        return {"status": "success", "message": "Integration removed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to remove integration")
```

### 4. SDK para Desenvolvedores

```python
# app/marketplace/sdk.py
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio

@dataclass
class ConnectorMetadata:
    """Metadata de um conector customizado"""
    name: str
    display_name: str
    description: str
    category: str
    version: str
    author: str
    logo_url: Optional[str] = None
    documentation_url: Optional[str] = None
    support_email: Optional[str] = None

class ConnectorSDK(ABC):
    """SDK base para desenvolvimento de conectores customizados"""
    
    def __init__(self, metadata: ConnectorMetadata):
        self.metadata = metadata
        self.auth_config: Dict = {}
        self.endpoints: Dict = {}
        self.transformations: Dict = {}
        self.webhooks: Dict = {}
        
    @abstractmethod
    async def authenticate(self, auth_data: Dict) -> Dict:
        """Implementa autenticação específica do serviço"""
        pass
    
    @abstractmethod
    async def test_connection(self, credentials: Dict) -> bool:
        """Testa se a conexão está funcionando"""
        pass
    
    @abstractmethod
    async def get_data(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Obtém dados do serviço externo"""
        pass
    
    @abstractmethod
    async def send_data(self, endpoint: str, data: Dict) -> Any:
        """Envia dados para o serviço externo"""
        pass
    
    def add_endpoint(self, name: str, path: str, method: str = "GET",
                    parameters: Optional[Dict] = None):
        """Adiciona um endpoint ao conector"""
        self.endpoints[name] = {
            "path": path,
            "method": method,
            "parameters": parameters or {}
        }
    
    def add_transformation(self, name: str, field_mappings: Dict,
                          transformation_rules: Optional[List] = None):
        """Adiciona uma transformação de dados"""
        self.transformations[name] = {
            "field_mappings": field_mappings,
            "transformation_rules": transformation_rules or []
        }
    
    def add_webhook(self, event_type: str, handler: Callable):
        """Adiciona um handler para webhook"""
        self.webhooks[event_type] = handler
    
    async def handle_webhook(self, event_type: str, payload: Dict) -> Dict:
        """Processa um webhook recebido"""
        if event_type in self.webhooks:
            return await self.webhooks[event_type](payload)
        else:
            return {"status": "ignored", "reason": "No handler for event type"}

# Exemplo de conector customizado
class CustomCRMConnector(ConnectorSDK):
    """Exemplo de conector customizado para um CRM"""
    
    def __init__(self):
        metadata = ConnectorMetadata(
            name="custom_crm",
            display_name="Custom CRM",
            description="Conector para CRM personalizado da empresa",
            category="CRM",
            version="1.0.0",
            author="Equipe de Desenvolvimento",
            documentation_url="https://docs.company.com/crm-connector"
        )
        
        super().__init__(metadata)
        
        # Configuração de autenticação
        self.auth_config = {
            "auth_type": "api_key",
            "api_key_header": "X-API-Key",
            "base_url": "https://api.customcrm.com"
        }
        
        # Adiciona endpoints disponíveis
        self.add_endpoint("contacts", "/v1/contacts", "GET")
        self.add_endpoint("create_contact", "/v1/contacts", "POST")
        self.add_endpoint("companies", "/v1/companies", "GET")
        
        # Adiciona transformações
        self.add_transformation("contact_sync", {
            "firstName": "first_name",
            "lastName": "last_name",
            "email": "email_address",
            "company": "company_name"
        })
    
    async def authenticate(self, auth_data: Dict) -> Dict:
        """Valida API key do Custom CRM"""
        api_key = auth_data.get("api_key")
        
        if not api_key:
            raise ValueError("API key is required")
        
        # Testa a API key fazendo uma chamada simples
        test_result = await self.test_connection({"api_key": api_key})
        
        if test_result:
            return {"api_key": api_key, "status": "authenticated"}
        else:
            raise ValueError("Invalid API key")
    
    async def test_connection(self, credentials: Dict) -> bool:
        """Testa conexão com o Custom CRM"""
        try:
            # Simula teste de conexão
            await asyncio.sleep(0.1)  # Simula latência da rede
            return True
        except Exception:
            return False
    
    async def get_data(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Obtém dados do Custom CRM"""
        # Simula chamada para API externa
        if endpoint == "contacts":
            return {
                "data": [
                    {
                        "id": "1",
                        "firstName": "João",
                        "lastName": "Silva", 
                        "email": "joao.silva@email.com",
                        "company": "Empresa ABC"
                    }
                ],
                "total": 1
            }
        else:
            return {"data": [], "total": 0}
    
    async def send_data(self, endpoint: str, data: Dict) -> Any:
        """Envia dados para o Custom CRM"""
        # Simula criação de registro
        if endpoint == "create_contact":
            return {
                "id": "new_contact_id",
                "status": "created",
                "data": data
            }

class ConnectorRegistry:
    """Registry para conectores customizados"""
    
    def __init__(self):
        self.connectors: Dict[str, ConnectorSDK] = {}
    
    def register(self, connector: ConnectorSDK):
        """Registra um conector customizado"""
        self.connectors[connector.metadata.name] = connector
    
    def get_connector(self, name: str) -> Optional[ConnectorSDK]:
        """Obtém um conector pelo nome"""
        return self.connectors.get(name)
    
    def list_connectors(self) -> List[ConnectorMetadata]:
        """Lista metadados de todos os conectores"""
        return [connector.metadata for connector in self.connectors.values()]

# Registry global para conectores customizados
custom_connector_registry = ConnectorRegistry()

# Registra conectores built-in
custom_connector_registry.register(CustomCRMConnector())
```

## 🔧 Implementação de Fases

### Fase 1: Core Engine (Semanas 1-2)
- [ ] Implementar MarketplaceEngine básico
- [ ] Criar modelos de dados no PostgreSQL  
- [ ] Implementar ConnectorRegistry com conectores básicos
- [ ] Sistema básico de autenticação (OAuth2, API Key)
- [ ] Testes unitários do core engine

### Fase 2: API Gateway (Semanas 3-4)
- [ ] Implementar IntegrationGateway
- [ ] Sistema de rate limiting
- [ ] Circuit breaker pattern
- [ ] Queue de processamento com workers
- [ ] Retry automático e error handling
- [ ] Testes de carga do gateway

### Fase 3: APIs REST (Semanas 5-6)
- [ ] Endpoints para gerenciar conectores
- [ ] APIs de instalação e configuração
- [ ] Endpoints de execução de integrações
- [ ] Sistema de logs e analytics
- [ ] Documentação das APIs (OpenAPI/Swagger)

### Fase 4: SDK e Conectores (Semanas 7-8)
- [ ] SDK para desenvolvedores
- [ ] Conectores para Salesforce, HubSpot, Slack
- [ ] Sistema de transformação de dados
- [ ] Webhooks e eventos em tempo real
- [ ] Documentação do SDK

### Fase 5: Interface e Monitoramento (Semanas 9-10)
- [ ] Dashboard do marketplace
- [ ] Interface de configuração de integrações
- [ ] Sistema de monitoramento e alertas
- [ ] Analytics e métricas de uso
- [ ] Testes de aceitação do usuário

## 📊 Métricas e Monitoramento

### KPIs do Marketplace
```python
# app/marketplace/metrics.py
import time
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict

class MarketplaceMetrics:
    """Coleta e processa métricas do marketplace"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
    
    async def track_connector_install(self, connector_id: str, user_id: str):
        """Rastreia instalação de conector"""
        self.counters[f"connector_installs_{connector_id}"] += 1
        self.counters["total_installs"] += 1
        
        self.metrics["installs"].append({
            "timestamp": time.time(),
            "connector_id": connector_id,
            "user_id": user_id
        })
    
    async def track_api_call(self, integration_id: str, endpoint: str,
                           status: str, duration_ms: int):
        """Rastreia chamadas de API"""
        self.counters[f"api_calls_{status}"] += 1
        self.counters["total_api_calls"] += 1
        
        self.metrics["api_calls"].append({
            "timestamp": time.time(),
            "integration_id": integration_id,
            "endpoint": endpoint,
            "status": status,
            "duration_ms": duration_ms
        })
    
    async def get_usage_stats(self, period_days: int = 30) -> Dict:
        """Obtém estatísticas de uso"""
        cutoff_time = time.time() - (period_days * 24 * 60 * 60)
        
        # Filtra métricas do período
        recent_installs = [
            m for m in self.metrics["installs"] 
            if m["timestamp"] > cutoff_time
        ]
        
        recent_api_calls = [
            m for m in self.metrics["api_calls"]
            if m["timestamp"] > cutoff_time
        ]
        
        # Calcula estatísticas
        total_installs = len(recent_installs)
        total_api_calls = len(recent_api_calls)
        successful_calls = len([c for c in recent_api_calls if c["status"] == "success"])
        
        # Top conectores por instalações
        connector_installs = defaultdict(int)
        for install in recent_installs:
            connector_installs[install["connector_id"]] += 1
        
        top_connectors = sorted(
            connector_installs.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Tempo médio de resposta
        durations = [c["duration_ms"] for c in recent_api_calls if c["duration_ms"]]
        avg_response_time = sum(durations) / len(durations) if durations else 0
        
        return {
            "period_days": period_days,
            "total_installs": total_installs,
            "total_api_calls": total_api_calls,
            "successful_calls": successful_calls,
            "success_rate": (successful_calls / total_api_calls) if total_api_calls > 0 else 0,
            "average_response_time_ms": round(avg_response_time, 2),
            "top_connectors": [
                {"connector_id": connector_id, "installs": installs}
                for connector_id, installs in top_connectors
            ]
        }

# Singleton das métricas
marketplace_metrics = MarketplaceMetrics()
```

### Dashboard de Analytics
```python
# app/marketplace/dashboard.py
from typing import Dict, List
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

class MarketplaceDashboard:
    """Gera dashboards e relatórios do marketplace"""
    
    async def generate_usage_report(self, days: int = 30) -> Dict:
        """Gera relatório de uso do marketplace"""
        
        # Obtém dados das métricas
        stats = await marketplace_metrics.get_usage_stats(days)
        
        # Simula dados temporais para gráficos
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days),
            end=datetime.now(),
            freq='D'
        )
        
        # Gráfico de instalações ao longo do tempo
        installs_chart = {
            "type": "line",
            "data": {
                "x": [d.strftime("%Y-%m-%d") for d in dates],
                "y": [5, 8, 12, 6, 15, 20, 18] * (len(dates) // 7 + 1)[:len(dates)],
                "title": "Instalações de Conectores por Dia"
            }
        }
        
        # Gráfico de chamadas de API
        api_calls_chart = {
            "type": "bar",
            "data": {
                "x": ["Salesforce", "Slack", "HubSpot", "Teams", "Zapier"],
                "y": [450, 320, 480, 180, 250],
                "title": "Chamadas de API por Conector"
            }
        }
        
        # Distribuição por categoria
        category_chart = {
            "type": "pie",
            "data": {
                "labels": ["CRM", "Communication", "Marketing", "Automation"],
                "values": [40, 25, 20, 15],
                "title": "Conectores por Categoria"
            }
        }
        
        return {
            "summary": stats,
            "charts": {
                "installs_over_time": installs_chart,
                "api_calls_by_connector": api_calls_chart,
                "connectors_by_category": category_chart
            },
            "generated_at": datetime.utcnow().isoformat()
        }
```

## 🛡️ Segurança e Compliance

### Criptografia de Credenciais
```python
# app/marketplace/security.py
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CredentialsManager:
    """Gerencia criptografia segura de credenciais"""
    
    def __init__(self):
        # Gera chave de criptografia a partir de password master
        password = os.getenv("MARKETPLACE_MASTER_PASSWORD", "default-password").encode()
        salt = os.getenv("MARKETPLACE_SALT", "default-salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Criptografa dados sensíveis"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografa dados"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

# Auditoria de acesso
class AccessAuditor:
    """Auditoria de acessos e operações do marketplace"""
    
    async def log_access(self, user_id: str, action: str, resource: str,
                        success: bool, details: Optional[Dict] = None):
        """Log de acesso para auditoria"""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "success": success,
            "details": details or {},
            "ip_address": "0.0.0.0",  # Deveria vir do request
            "user_agent": "ConectaPRO/1.0"  # Deveria vir do request
        }
        
        # TODO: Salvar no banco de dados de auditoria
        print(f"AUDIT: {audit_entry}")
```

## ✅ Checklist de Entrega

### Funcionalidades Core
- [ ] Engine de marketplace funcional
- [ ] Registry de conectores com Salesforce, Slack, HubSpot
- [ ] Sistema de autenticação OAuth2/API Key
- [ ] Gateway unificado com rate limiting
- [ ] APIs REST completas
- [ ] SDK para desenvolvedores

### Infraestrutura
- [ ] Banco de dados configurado com migrations
- [ ] Sistema de logs estruturados
- [ ] Monitoramento e métricas
- [ ] Criptografia de credenciais
- [ ] Rate limiting e circuit breaker

### Integração
- [ ] Testes automatizados (unit, integration, e2e)
- [ ] Documentação técnica completa
- [ ] Dashboard de analytics
- [ ] Sistema de webhooks
- [ ] API documentation (OpenAPI)

### Segurança
- [ ] Auditoria de acessos
- [ ] Validação de inputs
- [ ] Criptografia de dados sensíveis
- [ ] Rate limiting por usuário
- [ ] Logs de segurança

## 📈 Critérios de Sucesso

### Métricas Técnicas
- **Disponibilidade**: > 99.5%
- **Tempo de resposta**: < 500ms (p95)
- **Taxa de erro**: < 1%
- **Throughput**: > 1000 req/min por conector

### Métricas de Produto
- **Conectores ativos**: 10+ conectores funcionais
- **Integrações por usuário**: Média de 3+ por usuário ativo
- **Tempo de configuração**: < 5 minutos por integração
- **Taxa de sucesso de sync**: > 98%

### KPIs de Negócio
- **Adoção**: 60% dos usuários ativos usando marketplace
- **Retenção**: 80% dos usuários mantêm integrações ativas
- **Expansão**: 40% dos usuários instalam > 1 conector
- **Satisfação**: NPS > 8.0 para funcionalidades de integração

---

*Este documento serve como especificação completa para implementação do Marketplace de Integrações. Todas as funcionalidades descritas são essenciais para criar um ecossistema robusto e escalável de integrações no Conecta PRO.*
EOF"