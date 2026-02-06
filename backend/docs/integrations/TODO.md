# TODO: Implementação do Integration Framework

**Status:** Em andamento
**Última atualização:** 2026-01-15

---

## FASE A: Fundação (Semana 1-2)

### Models e Banco de Dados

- [ ] Criar model `integration_account.py` (credenciais por tenant)
- [ ] Criar model `sync_run.py` (histórico de execuções)
- [ ] Criar model `sync_state.py` (estado incremental)
- [ ] Criar model `id_map.py` (mapeamento IDs)
- [ ] Criar migration Alembic `sprint33_integration_framework.py`
- [ ] Testar migrations em staging

### Framework Base

- [ ] Criar `connectors/base/connector.py` (interface ABC)
- [ ] Criar `connectors/base/auth.py` (API Key, OAuth2, mTLS strategies)
- [ ] Criar `connectors/base/http_client.py` (httpx + retry + circuit breaker)
- [ ] Criar `connectors/base/rate_limiter.py` (rate limiting local)
- [ ] Criar `connectors/base/exceptions.py` (exceções padronizadas)
- [ ] Criar `sync/engine.py` (orquestrador)
- [ ] Criar `sync/jobs/base.py` (SyncJob ABC)

### Endpoints REST

- [ ] Endpoint GET `/api/v1/integrations/connectors`
- [ ] Endpoints CRUD `/api/v1/integrations/accounts`
- [ ] Endpoints `/api/v1/integrations/sync/run` e `/sync/runs`
- [ ] Endpoint POST `/api/v1/integrations/webhooks/{connector}`
- [ ] Endpoint GET `/api/v1/integrations/health/{connector}`

### Observabilidade

- [ ] Métricas Prometheus para sync duration/items/errors
- [ ] Logs estruturados com correlation_id
- [ ] Healthcheck endpoints

### Testes Fase A

- [ ] Unit tests para base connector
- [ ] Unit tests para auth strategies
- [ ] Unit tests para http_client retry logic
- [ ] Integration tests para endpoints REST

---

## FASE B: Bling (Semana 3-4)

### Discovery

- [ ] Testar API Bling em sandbox
- [ ] Documentar rate limits reais
- [ ] Mapear endpoints disponíveis
- [ ] Verificar webhooks suportados

### Implementação

- [ ] Criar `connectors/bling/connector.py`
- [ ] Criar `connectors/bling/schemas.py` (schemas da API Bling)
- [ ] Criar `connectors/bling/mappers.py` (Bling ↔ Conecta)
- [ ] Criar `sync/jobs/bling_jobs.py`

### Entidades (Pull Mode)

- [ ] Sync de Contatos/Clientes
- [ ] Sync de Produtos
- [ ] Sync de Estoques
- [ ] Sync de Pedidos de Venda
- [ ] Sync de Notas Fiscais (se disponível)

### Testes Fase B

- [ ] Unit tests para mappers Bling
- [ ] Integration tests com mock (respx)
- [ ] Contract tests para schemas
- [ ] Testes de paginação e incremental sync

---

## FASE C: Sólides (Semana 5-6)

### Discovery

- [ ] Obter documentação completa da API
- [ ] Configurar OAuth2 client
- [ ] Testar em sandbox
- [ ] Mapear entidades disponíveis

### Implementação

- [ ] Criar `connectors/solides/connector.py`
- [ ] Criar `connectors/solides/schemas.py`
- [ ] Criar `connectors/solides/mappers.py`
- [ ] Criar `sync/jobs/solides_jobs.py`

### Entidades (Pull Mode)

- [ ] Sync de Colaboradores
- [ ] Sync de Cargos/Estruturas
- [ ] Sync de Escalas/Turnos (se disponível)
- [ ] Sync de Ponto (se disponível)

### Testes Fase C

- [ ] Unit tests para OAuth2 flow
- [ ] Unit tests para mappers Sólides
- [ ] Integration tests
- [ ] Testes de token refresh

---

## FASE D: Domínio Sistemas (Semana 7-8)

### Discovery

- [ ] Contato comercial para API oficial
- [ ] Avaliar provedores alternativos (Omie, Nibo)
- [ ] Documentar decisão Plano A vs Plano B

### Implementação (se API disponível)

- [ ] Criar `connectors/dominio/connector.py`
- [ ] Criar `connectors/dominio/schemas.py`
- [ ] Criar `connectors/dominio/mappers.py`

### Implementação Plano B (se necessário)

- [ ] Avaliar Omie como ponte contábil
- [ ] Avaliar Nibo como ponte contábil
- [ ] Implementar connector do provedor escolhido

---

## FASE E: GOV.BR (Semanas 2-12, paralelo)

### Certificado Digital

- [ ] Configurar certificado A1
- [ ] Criar módulo de assinatura XML
- [ ] Testar cadeia ICP Brasil
- [ ] Implementar alertas de expiração

### eSocial

- [ ] Validar services existentes
- [ ] Testar em ambiente de homologação
- [ ] Implementar envio de eventos (se viável)

### SEFAZ

- [ ] Validar services existentes
- [ ] Testar NFe em homologação
- [ ] Documentar fluxo completo

### NFS-e

- [ ] Pesquisar padrão nacional vs municipal (Manaus)
- [ ] Avaliar provedores (Focus, TecnoSpeed)
- [ ] Implementar ou documentar Plano B

---

## CRITÉRIOS DE ACEITE POR FASE

### Fase A - Foundation
- [x] Migrations executam sem erro
- [ ] Endpoints respondem corretamente
- [ ] Health check funciona
- [ ] Cobertura de testes > 85%

### Fase B - Bling
- [ ] Autenticação funciona (healthcheck ok)
- [ ] Sync incremental sem duplicatas
- [ ] Rate limiting respeitado
- [ ] Logs estruturados sem dados sensíveis

### Fase C - Sólides
- [ ] OAuth2 flow completo
- [ ] Token refresh automático
- [ ] Sync de colaboradores funcional
- [ ] LGPD compliance verificado

### Fase D - Domínio
- [ ] Decisão Plano A/B documentada
- [ ] Pelo menos 1 entidade sincronizando (ou Plano B implementado)

### Fase E - GOV
- [ ] Certificado A1 configurado e testado
- [ ] 1 fluxo ponta-a-ponta em homologação

---

## COMANDOS ÚTEIS

```bash
# Rodar migrations
cd /opt/conecta-pro/backend
alembic upgrade head

# Rodar testes de integrações
pytest tests/integrations/ -v --cov=modules/integrations

# Verificar health do Bling
curl -X GET http://localhost:8080/api/v1/integrations/health/bling \
  -H "Authorization: Bearer $TOKEN"

# Disparar sync manual
curl -X POST http://localhost:8080/api/v1/integrations/sync/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "...", "entities": ["products"], "mode": "incremental"}'
```

---

*Atualizar este documento conforme progresso*
