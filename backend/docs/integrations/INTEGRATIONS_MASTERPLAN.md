# INTEGRATIONS MASTERPLAN - Conecta PRO

## Integrações: SÓLIDES + DOMÍNIO SISTEMAS + BLING + GOV.BR

**Versão:** 1.0
**Data:** 2026-01-15
**Estratégia:** Rodar em paralelo por 3 meses, ingerindo dados, comparando, evoluindo sem interromper operação.

---

## 1. MAPA ARQUITETURAL ATUAL

### 1.1 Estrutura de modules/integrations/

```
modules/integrations/
├── __init__.py
├── controllers/
│   └── integration_controller.py      # Endpoints REST existentes
├── services/
│   ├── integration_service.py         # Lógica principal
│   └── webhook_service.py             # Webhooks
├── models/
│   ├── api_endpoint.py               # Documentação de endpoints
│   ├── api_key.py                    # Chaves API com rate limiting
│   ├── webhook_config.py             # Config de webhooks
│   ├── integration_log.py            # Logs de integrações
│   └── sync_queue.py                 # Fila de sincronização [ROBUSTO]
├── repositories/
│   └── integration_repository.py
├── schemas/
│   └── integration_schemas.py
├── banking/                          # [PADRÃO A SEGUIR]
│   ├── adapters/
│   │   ├── base.py                  # Interface abstrata
│   │   ├── bb.py                    # Banco do Brasil
│   │   ├── itau.py                  # Itaú
│   │   └── bradesco.py              # Bradesco
│   └── services/
│       └── banking_service.py
├── email/
└── whatsapp/
```

### 1.2 Estrutura de modules/government_integrations/

```
modules/government_integrations/
├── controllers/
│   ├── receita_federal_controller.py
│   ├── fgts_inss_controller.py
│   ├── esocial_controller.py
│   └── sefaz_controller.py
├── services/
│   ├── receita_federal_service.py   # Validação CPF/CNPJ, consultas
│   ├── fgts_inss_service.py         # Cálculos trabalhistas
│   ├── esocial_service.py
│   └── sefaz_service.py
└── utils.py                          # Validadores CPF/CNPJ
```

### 1.3 Padrão de Error Handling

```python
# Padrão estabelecido no projeto
try:
    result = await service.operation()
    return Response.model_validate(result)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Erro: {e}")
    raise HTTPException(status_code=500, detail="Erro interno")
```

### 1.4 Padrão de Logging

- **Formato:** JSON estruturado (loguru)
- **Níveis:** DEBUG, INFO, WARNING, ERROR
- **Campos:** timestamp, level, message, module, correlation_id

### 1.5 Autenticação e Middleware

| Componente | Localização | Descrição |
|------------|-------------|-----------|
| JWT Auth | `core/security/` | python-jose + bcrypt |
| Rate Limit | `main.py` | slowapi - 200/min default |
| CORS | `main.py` | Configurável via .env |
| Security Headers | `main.py` | X-Content-Type-Options, X-Frame-Options |
| GZIP | `main.py` | Compressão > 500 bytes |

### 1.6 Padrão de Schemas Pydantic

```python
class EntityBase(BaseModel):
    """Campos comuns."""
    nome: str = Field(..., min_length=1, max_length=100)

class EntityCreate(EntityBase):
    """Para POST."""
    pass

class EntityUpdate(BaseModel):
    """Para PATCH - todos opcionais."""
    nome: Optional[str] = None

class EntityResponse(EntityBase):
    """Resposta com ID e timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 1.7 Rotas em api/v1/

- Routers registrados em `api/v1/__init__.py`
- Prefixo padrão: `/api/v1/{module}`
- Tags para agrupamento no OpenAPI

---

## 2. DECISÕES ARQUITETURAIS

### 2.1 O que REUTILIZAR

| Componente Existente | Uso no Integration Framework |
|---------------------|------------------------------|
| `banking/adapters/base.py` | Base para `connectors/base.py` |
| `SyncQueue` model | Já tem Bling no enum - usar diretamente |
| `webhook_config.py` | Estender para webhooks de conectores |
| `integration_log.py` | Logs de sync runs |
| `security_lgpd/crypto_service.py` | Criptografia de credenciais |

### 2.2 O que CRIAR

| Novo Componente | Justificativa |
|-----------------|---------------|
| `integration_account` | Credenciais por tenant (multi-tenant) |
| `sync_run` | Histórico de execuções com métricas |
| `sync_state` | Estado incremental por entidade |
| `id_map` | Mapeamento ID externo ↔ interno |
| `connectors/` | Framework de conectores padronizado |
| `sync/engine.py` | Orquestrador de sincronizações |

### 2.3 Estrutura Final Proposta

```
modules/integrations/
├── [existente mantido]
├── connectors/                      # NOVO
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── connector.py            # Interface ABC
│   │   ├── auth.py                 # Strategies: API Key, OAuth2, mTLS
│   │   ├── http_client.py          # httpx async + retry + circuit breaker
│   │   ├── rate_limiter.py         # Rate limiting local
│   │   └── exceptions.py           # Exceções padronizadas
│   ├── bling/
│   │   ├── __init__.py
│   │   ├── connector.py            # BlingConnector
│   │   ├── mappers.py              # Mapeamento Bling ↔ Conecta
│   │   └── schemas.py              # Schemas Bling
│   ├── solides/
│   │   ├── __init__.py
│   │   ├── connector.py            # SolidesConnector
│   │   ├── mappers.py
│   │   └── schemas.py
│   └── dominio/
│       ├── __init__.py
│       ├── connector.py            # DominioConnector (se API existir)
│       └── README.md               # DOC GAP - documentar descobertas
├── sync/                            # NOVO
│   ├── __init__.py
│   ├── engine.py                   # SyncEngine - orquestrador
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── base.py                 # SyncJob ABC
│   │   ├── bling_jobs.py           # Jobs por entidade Bling
│   │   └── solides_jobs.py         # Jobs por entidade Sólides
│   ├── mappers/
│   │   ├── __init__.py
│   │   └── base.py                 # Interface de mapeamento
│   └── validators/
│       ├── __init__.py
│       └── base.py                 # Validadores de consistência
└── models/
    ├── [existentes mantidos]
    ├── integration_account.py       # NOVO - credenciais por tenant
    ├── sync_run.py                  # NOVO - histórico de execuções
    ├── sync_state.py                # NOVO - estado incremental
    └── id_map.py                    # NOVO - mapeamento IDs
```

---

## 3. ESPECIFICAÇÃO DE SISTEMAS EXTERNOS

### 3.1 BLING

| Aspecto | Detalhe |
|---------|---------|
| **API Base** | `https://www.bling.com.br/Api/v3/` |
| **Auth** | API Key (header `Authorization: Bearer {api_key}`) |
| **Rate Limit** | ~3 req/s (não documentado oficialmente) |
| **Webhooks** | Limitado - apenas alguns eventos |
| **Documentação** | https://developer.bling.com.br/ |

**Entidades prioritárias:**
1. Contatos (clientes/fornecedores)
2. Produtos
3. Estoques
4. Pedidos de venda
5. Notas fiscais (se disponível)

**DOC GAPs conhecidos:**
- Rate limit real não documentado
- Webhooks incompletos
- Paginação inconsistente em alguns endpoints

### 3.2 SÓLIDES

| Aspecto | Detalhe |
|---------|---------|
| **API Base** | `https://api.solides.com.br/` |
| **Auth** | OAuth2 (client_credentials) |
| **Rate Limit** | Documentado por endpoint |
| **Webhooks** | Sim - eventos de colaboradores |
| **Documentação** | Disponível mediante contrato |

**Entidades prioritárias:**
1. Colaboradores (cadastro completo)
2. Cargos e estruturas
3. Escalas/turnos
4. Ponto eletrônico (se disponível)
5. Indicadores RH

**DOC GAPs:**
- API completa requer contato comercial
- Alguns endpoints podem estar em beta

### 3.3 DOMÍNIO SISTEMAS

| Aspecto | Detalhe |
|---------|---------|
| **API Base** | **NÃO CONFIRMADA** |
| **Auth** | Desconhecido |
| **Documentação** | Não pública |

**PLANO A:** Contato comercial para API oficial
**PLANO B:** Provedor intermediário (Nibo, Omie, Contabilizei API)

**Entidades desejadas:**
1. Plano de contas
2. Centros de custo
3. Lançamentos contábeis
4. Obrigações/guias
5. Folha de pagamento

### 3.4 GOV.BR / Órgãos

| Sistema | Status Atual | Próximo Passo |
|---------|--------------|---------------|
| Receita Federal | Validação CPF/CNPJ implementada | Manter |
| eSocial | Service existe | Validar WS oficiais |
| SEFAZ | Service existe | Certificado A1 |
| FGTS/INSS | Cálculos implementados | Manter |
| NFS-e | Não implementado | Provedor ou WS municipal |

---

## 4. ENDPOINTS REST DO FRAMEWORK

### 4.1 Gerenciamento de Conectores

```
GET    /api/v1/integrations/connectors
       → Lista conectores disponíveis e capacidades

POST   /api/v1/integrations/accounts
       → Cria credenciais/config por tenant
       Body: { connector: "bling", credentials: {...}, tenant_id: "..." }

GET    /api/v1/integrations/accounts
       → Lista contas configuradas

GET    /api/v1/integrations/accounts/{id}
       → Detalhes de uma conta

PATCH  /api/v1/integrations/accounts/{id}
       → Atualiza credenciais/config

DELETE /api/v1/integrations/accounts/{id}
       → Remove conta (soft delete)
```

### 4.2 Sincronização

```
POST   /api/v1/integrations/sync/run
       → Dispara sync manual
       Body: { account_id: "...", entities: ["products", "clients"], mode: "incremental" }

GET    /api/v1/integrations/sync/runs
       → Histórico de execuções
       Query: ?account_id=...&status=...&from=...&to=...

GET    /api/v1/integrations/sync/runs/{id}
       → Detalhes + métricas + erros

POST   /api/v1/integrations/sync/runs/{id}/cancel
       → Cancela execução em andamento

POST   /api/v1/integrations/sync/runs/{id}/retry
       → Reprocessa execução falhada
```

### 4.3 Webhooks

```
POST   /api/v1/integrations/webhooks/{connector}
       → Inbox de webhooks (assinatura + idempotência)
       Headers: X-Webhook-Signature, X-Webhook-Id

GET    /api/v1/integrations/webhooks/logs
       → Logs de webhooks recebidos
```

### 4.4 Health e Diagnóstico

```
GET    /api/v1/integrations/health/{connector}
       → Teste de conexão/credenciais
       Response: { status: "ok", latency_ms: 123, details: {...} }

GET    /api/v1/integrations/metrics
       → Métricas Prometheus do framework
```

---

## 5. REGRAS TÉCNICAS

### 5.1 HTTP Client

```python
# Usar httpx async com:
- Timeout: connect=5s, read=30s, write=10s
- Retry: 3 tentativas com backoff exponencial
- Circuit Breaker: abrir após 5 falhas consecutivas
- Rate Limit: respeitar limites do fornecedor
```

### 5.2 Idempotência

- Toda sync deve ser idempotente
- Webhooks: validar X-Webhook-Id para evitar duplicatas
- ID Map: mapeamento determinístico

### 5.3 Sync Incremental

```python
# Priorizar sync incremental por:
- updated_at (campo de modificação)
- cursor/offset
- etag/last-modified headers
```

### 5.4 Multi-tenant

- Tudo com `tenant_id`
- Credenciais isoladas por tenant
- Logs e métricas por tenant

### 5.5 Segurança

- Tokens criptografados em banco (AES-256-GCM via security_lgpd)
- Nunca logar credenciais
- Audit trail de acessos

### 5.6 Logs Estruturados

```json
{
  "timestamp": "2026-01-15T10:00:00Z",
  "level": "INFO",
  "message": "Sync completed",
  "correlation_id": "abc123",
  "tenant_id": "tenant_xyz",
  "connector": "bling",
  "entity": "products",
  "sync_run_id": "run_456",
  "items_processed": 150,
  "duration_ms": 3200
}
```

### 5.7 Métricas Prometheus

```
# Métricas a expor:
conecta_integration_sync_duration_seconds{connector, entity, status}
conecta_integration_sync_items_total{connector, entity, direction}
conecta_integration_sync_errors_total{connector, error_type}
conecta_integration_api_requests_total{connector, endpoint, status_code}
conecta_integration_rate_limit_hits_total{connector}
```

---

## 6. DOC GAPS E PRÓXIMOS PASSOS

### 6.1 Bling

- [ ] Confirmar rate limit real (testar em sandbox)
- [ ] Mapear todos os endpoints disponíveis
- [ ] Verificar webhooks suportados
- [ ] Testar paginação de cada endpoint

### 6.2 Sólides

- [ ] Obter documentação completa da API
- [ ] Confirmar scopes OAuth2 necessários
- [ ] Mapear entidades disponíveis
- [ ] Verificar webhooks

### 6.3 Domínio Sistemas

- [ ] Contato comercial para API
- [ ] Se não houver API: avaliar Plano B (provedores)
- [ ] Documentar decisão final

### 6.4 GOV.BR

- [ ] Certificado A1 configurado
- [ ] Testar eSocial em homologação
- [ ] Avaliar provedores para NFS-e municipal

---

## 7. COMPATIBILIDADE

Este framework é 100% compatível com:
- Estrutura modular existente
- Padrões de código do projeto
- Security LGPD já implementado
- Multi-tenant existente
- Observabilidade (Prometheus/Grafana)

**Não quebra:**
- Módulos existentes
- APIs existentes
- Banking adapters
- Government integrations

---

*Documento criado em: 2026-01-15*
*Última atualização: 2026-01-15*
