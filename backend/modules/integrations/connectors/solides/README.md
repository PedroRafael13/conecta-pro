# Integração Sólides - Conecta PRO

## Visão Geral

A integração com Sólides permite sincronização bidirecional de dados de RH entre o Conecta PRO e as plataformas Sólides.

**Status Atual:** Sólides DP (Tangerino) integrado | Sólides RH (Profiler) pendente

---

## Plataformas Sólides

| Plataforma | Foco | API Base | Status |
|------------|------|----------|--------|
| **Sólides DP** (Tangerino) | Ponto eletrônico, Folha, Cadastro | `employer.tangerino.com.br` | ✅ Implementado |
| **Sólides RH** (Profiler) | Recrutamento, DISC, Clima, Talentos | `apigw.solides.com.br` | ❌ Pendente |

---

## Sólides DP - Funcionalidades Disponíveis

### Leitura de Dados (GET)

| Endpoint | Descrição | Implementado |
|----------|-----------|--------------|
| `GET /employees` | Listar colaboradores | ✅ |
| `GET /employees/{id}` | Detalhes do colaborador | ✅ |
| `GET /job_roles` | Listar cargos | ✅ |
| `GET /workplaces` | Listar locais de trabalho | ✅ |
| `GET /work_schedules` | Listar escalas/jornadas | ✅ |

### Escrita de Dados (POST/PUT/DELETE)

| Endpoint | Descrição | Implementado |
|----------|-----------|--------------|
| `POST /employees` | Criar colaborador | ✅ |
| `PUT /employees/{id}` | Atualizar colaborador | ✅ |
| `POST /employees/{id}/dismiss` | Demitir colaborador | ✅ |

### Webhooks

| Evento | Descrição | Implementado |
|--------|-----------|--------------|
| `novo_colaborador` | Novo funcionário cadastrado | ✅ |
| `edicao_colaborador` | Dados alterados | ✅ |
| `demissao_colaborador` | Funcionário demitido | ✅ |

### Campos Sincronizados

```
Colaborador:
├── id (solides_id)
├── name (nome completo)
├── cpf
├── email
├── phone
├── admissionDate (data admissão)
├── dismissalDate (data demissão)
├── jobRoleId → cargo
├── workplaceId → local de trabalho
├── workScheduleId → escala
└── status (ativo/inativo/demitido)
```

---

## Sólides DP - Limitações Conhecidas

### Endpoints NÃO disponíveis na API pública

| Funcionalidade | Status | Observação |
|----------------|--------|------------|
| Ocorrências (advertências, elogios) | ❌ | API não expõe |
| Absenteísmos (faltas, atrasos) | ❌ | API não expõe |
| Batidas de Ponto | ❌ | Não encontrado |
| Banco de Horas | ❌ | Não encontrado |
| Férias | ❌ | Não encontrado |
| Holerites | ❌ | Não encontrado |

> **Nota:** Estas funcionalidades podem estar disponíveis apenas via interface web do Tangerino ou requerem contato com suporte Sólides para liberação.

---

## Sólides RH - Funcionalidades Pendentes

### Requer API separada (não implementado)

| Módulo | Funcionalidades |
|--------|-----------------|
| **Passaporte Comportamental** | Perfil DISC, Competências, Pontos fortes/desenvolvimento |
| **Recrutamento & Seleção** | Vagas, Candidatos, Etapas do processo, Avaliações |
| **Pesquisa de Clima** | Aplicação, Resultados, Histórico |
| **Avaliação de Desempenho** | Ciclos, Metas, Feedback 360 |
| **Gestão de Talentos** | PDI, Sucessão, Nine Box |
| **Onboarding** | Checklists, Documentos, Treinamentos |

### Requisitos para implementação

1. Contratar acesso à API Sólides RH/Profiler
2. Obter token de autenticação separado
3. Implementar connector para `apigw.solides.com.br`

---

## Configuração

### Variáveis de Ambiente

```bash
# Sólides DP (Tangerino) - CONFIGURADO
SOLIDES_API_TOKEN=<token_base64>
SOLIDES_WEBHOOK_SECRET=<secret_para_validar_webhooks>

# Sólides RH (Profiler) - FUTURO
SOLIDES_RH_API_TOKEN=<token_rh>
SOLIDES_RH_CLIENT_ID=<client_id>
SOLIDES_RH_CLIENT_SECRET=<client_secret>
```

### Autenticação

**Sólides DP:** Basic Auth com token base64
```
Authorization: Basic <token_base64>
```

**Sólides RH:** OAuth2 (quando implementado)
```
Authorization: Bearer <access_token>
```

---

## Arquitetura

```
/backend/modules/integrations/connectors/solides/
├── __init__.py              # Exports do módulo
├── connector.py             # Connector principal (API DP)
├── schemas.py               # Schemas Pydantic (DP + RH)
├── models.py                # Models SQLAlchemy (sync, logs, conflitos)
├── mappers.py               # Mapeamento Sólides ↔ Conecta PRO
├── sync_service.py          # Serviço de sincronização
├── integration_service.py   # Integração com models locais
├── webhook_handler.py       # Processador de webhooks
├── conflict_resolver.py     # Resolução de conflitos
├── tasks.py                 # Celery tasks
└── README.md                # Esta documentação
```

---

## Endpoints REST

### Webhook (público)
```
POST /api/v1/integrations/solides/webhook
```

### Gerenciamento (autenticado)
```
GET  /api/v1/integrations/solides/status
GET  /api/v1/integrations/solides/health
POST /api/v1/integrations/solides/sync/trigger
POST /api/v1/integrations/solides/sync/full
POST /api/v1/integrations/solides/sync/incremental
GET  /api/v1/integrations/solides/logs
GET  /api/v1/integrations/solides/conflicts
POST /api/v1/integrations/solides/conflicts/{id}/resolve
GET  /api/v1/integrations/solides/config
POST /api/v1/integrations/solides/config
```

---

## Celery Tasks

| Task | Schedule | Descrição |
|------|----------|-----------|
| `solides.full_sync` | Manual / 3 AM diário | Sincronização completa |
| `solides.incremental_sync` | A cada 15 min | Sincronização incremental |
| `solides.health_check` | A cada 5 min | Verificar conexão |
| `solides.process_webhooks` | Contínuo | Processar fila de webhooks |
| `solides.cleanup_logs` | Diário | Limpar logs antigos |

---

## Tabelas no Banco

| Tabela | Descrição |
|--------|-----------|
| `solides_integration_config` | Configuração por condomínio |
| `solides_credential` | Credenciais criptografadas |
| `solides_sync_state` | Estado de sync por entidade |
| `solides_sync_log` | Histórico de sincronizações |
| `solides_sync_conflict` | Conflitos detectados |
| `solides_entity_mapping` | Mapeamento IDs Sólides ↔ Conecta |
| `solides_webhook_log` | Log de webhooks recebidos |

---

## Teste de Conexão

```bash
# Health check
curl -X GET http://localhost:8080/api/v1/integrations/solides/health \
  -H "Authorization: Bearer <token>"

# Teste de webhook
curl -X POST http://localhost:8080/api/v1/integrations/solides/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"novo_colaborador","data":{"id":"123","nome":"Teste"}}'
```

---

## Próximos Passos

1. [ ] Obter acesso à API Sólides RH
2. [ ] Implementar connector OAuth2 para RH
3. [ ] Adicionar endpoints de Passaporte Comportamental
4. [ ] Adicionar endpoints de Recrutamento
5. [ ] Integrar DISC com perfil de funcionário no Conecta PRO
6. [ ] Dashboard de Clima Organizacional

---

## Suporte

- **Documentação Sólides DP:** https://docs.tangerino.com.br
- **Documentação Sólides RH:** https://developers.solides.com (requer acesso)
- **Suporte Sólides:** suporte@solides.com.br

---

*Última atualização: Janeiro 2026*
*Sprint 33: Integration Framework*
