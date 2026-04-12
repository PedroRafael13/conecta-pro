# RELATÓRIO — Mapa Completo: Módulo Fiscal / Certidões
**Data:** 2026-04-09
**Branch:** feature/people-management-reorganization
**Gerado por:** Claude Code (tmux-t1)
**Escopo:** Backend — módulo fiscal, certidões, integrações governamentais, agentes GEDEON

---

## 1. VISÃO GERAL

O ecossistema de certidões do Conecta PRO é distribuído em **5 camadas**:

```
┌─────────────────────────────────────────────────────────┐
│  CAMADA 1 — API REST                                    │
│  GET/POST/PUT/DELETE /certidoes                         │
├─────────────────────────────────────────────────────────┤
│  CAMADA 2 — BANCO                                       │
│  ged_certidoes (tabela central)                         │
├─────────────────────────────────────────────────────────┤
│  CAMADA 3 — TASKS/JOBS                                  │
│  ged_sync_cnds (Celery) + KRONOS (GEDEON daily)         │
├─────────────────────────────────────────────────────────┤
│  CAMADA 4 — EVENTOS                                     │
│  fiscal/publishers.py → ConectaEventBus                 │
├─────────────────────────────────────────────────────────┤
│  CAMADA 5 — INTEGRAÇÕES EXTERNAS                        │
│  Receita Federal (RFB) · TST · FGTS Digital             │
└─────────────────────────────────────────────────────────┘
```

---

## 2. ARQUIVOS ENVOLVIDOS

### 2.1 Arquivos principais (por responsabilidade)

| Arquivo | Responsabilidade |
|---------|-----------------|
| `modules/ged/models/ged_certidao.py` | Model ORM da tabela `ged_certidoes` |
| `modules/ged/controllers/ged_certidoes_controller.py` | Endpoints CRUD de certidões |
| `modules/fiscal/publishers.py` | Publicação de eventos no event bus |
| `modules/people_management/ged/tasks/cnd_sync_task.py` | Task Celery de sincronização diária |
| `modules/people_management/ged/events/handlers.py` | Handler `on_cnd_renewed()` |
| `modules/people_management/ged/models/kit_document.py` | Enum `DocumentType` (CND, CRF, CNDT) |
| `modules/bidding/integrations/receita_federal/cnd_client.py` | Client HTTP → Receita Federal |
| `modules/bidding/integrations/receita_federal/cndt_client.py` | Client HTTP → TST |
| `modules/gedeon/agents/kronos.py` | Agente de monitoramento de vencimentos |
| `modules/gedeon/agents/hermes.py` | Agente de classificação de documentos |
| `modules/gedeon/agents/sophia.py` | Agente de indexação semântica |
| `modules/government_integrations/controllers/sync_controller.py` | Endpoint `/dados/certidoes/{cnpj}` |
| `modules/government_integrations/sync/federal/receita_sync.py` | Sync federal (Receita/PGFN) |
| `modules/government_integrations/core/fgts_inss_manager.py` | Gestão CRF-FGTS |

### 2.2 Arquivos de suporte (bidding/licitações)

| Arquivo | Responsabilidade |
|---------|-----------------|
| `modules/bidding/agents/sentinel_agent.py` | Verifica aptidão para licitação |
| `modules/bidding/services/notification_service.py` | Notificações por certidão vencendo |
| `modules/bidding/services/certificate_service.py` | Serviço de gestão de certificados |
| `modules/bidding/models/certificate.py` | Model de certificados para licitação |

---

## 3. BANCO DE DADOS

### 3.1 Tabela principal: `ged_certidoes`

```sql
CREATE TABLE ged_certidoes (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name         VARCHAR(255),          -- nome de exibição
  document_type VARCHAR(100),          -- classificação (cnd_federal, crf_fgts...)
  issuing_body VARCHAR(255),          -- órgão emissor
  issue_date   DATE,                  -- data de emissão
  expiry_date  DATE,                  -- data de vencimento (INDEXADA)
  file_path    TEXT,                  -- caminho no storage
  file_url     TEXT,                  -- URL pública/interna
  notes        TEXT,
  created_at   TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at   TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_ged_certidoes_expiry ON ged_certidoes(expiry_date);
```

### 3.2 Status calculado (propriedade Python — não persiste)

| Status | Condição |
|--------|----------|
| `VALIDA` | `expiry_date > hoje + 30 dias` |
| `A_VENCER` | `hoje ≤ expiry_date ≤ hoje + 30 dias` |
| `VENCIDA` | `expiry_date < hoje` |
| `SEM_VENCIMENTO` | `expiry_date IS NULL` |

### 3.3 Tipos de documento (enum `DocumentType`)

| Valor | Descrição |
|-------|-----------|
| `CND_FEDERAL` | Certidão Negativa de Débitos — Receita Federal/PGFN |
| `CND_ESTADUAL` | Certidão Negativa de Débitos — Sefaz Estadual |
| `CND_MUNICIPAL` | Certidão Negativa de Débitos — Prefeitura |
| `CRF_FGTS` | Certificado de Regularidade do FGTS |
| `CNDT_TRABALHISTA` | Certidão Negativa de Débitos Trabalhistas — TST |

### 3.4 Tabelas relacionadas

| Tabela | Relação |
|--------|---------|
| `ged_document_kits` | Kits com `status = EM_MONTAGEM` recebem certidões via `on_cnd_renewed()` |
| `ged_kit_documents` | Documento individual com `source_module = FISCAL`, `document_type ∈ {cnd, crf, cndt}` |

---

## 4. ENDPOINTS REST

### 4.1 GED Certidões (`/api/v1/ged/certidoes` ou prefixo registrado)

| Método | Rota | Função | Retorno |
|--------|------|--------|---------|
| `GET` | `/certidoes` | `listar_certidoes()` | Lista completa + resumo `{validas, vencidas, a_vencer_30d}` |
| `POST` | `/certidoes` | `criar_certidao()` | Certidão criada (schema `CertidaoCreate`) |
| `PUT` | `/certidoes/{id}` | `atualizar_certidao()` | Certidão atualizada (schema `CertidaoUpdate`, todos opcionais) |
| `DELETE` | `/certidoes/{id}` | `remover_certidao()` | Confirmação de remoção |

**Schemas:**
- `CertidaoCreate`: `name, document_type, issuing_body, issue_date, expiry_date, file_path, file_url, notes`
- `CertidaoUpdate`: todos os campos opcionais (PATCH semântico)

### 4.2 Government Integrations

| Método | Rota | Função |
|--------|------|--------|
| `GET` | `/api/v1/government/dados/certidoes/{cnpj}` | Lista certidões sincronizadas por CNPJ |

---

## 5. SERVIÇOS E INTEGRAÇÕES EXTERNAS

### 5.1 CNDFederalClient — Receita Federal / PGFN

**Arquivo:** `modules/bidding/integrations/receita_federal/cnd_client.py`

| Item | Detalhe |
|------|---------|
| **URL** | `https://solucoes.receita.fazenda.gov.br/Servicos/CertidaoInternet/CND/Consulta` |
| **Método principal** | `consultar_cnd(cnpj)` |
| **Verificação** | `verificar_regularidade(cnpj)` → `{regular, tipo_certidao, apto_licitar, observacao}` |
| **Validade padrão** | 180 dias |
| **Retry** | 3× com backoff exponencial; trata 429 (rate-limit) |
| **Tipos de resultado** | `CND` (negativa) · `CPDEN` (positiva c/ efeito negativo) · `CPD` (positiva) |

### 5.2 CNDTTrabalhistaClient — TST

**Arquivo:** `modules/bidding/integrations/receita_federal/cndt_client.py`

| Item | Detalhe |
|------|---------|
| **URL** | `https://cndt-certidao.tst.jus.br/gerarCertidao` |
| **Método principal** | `consultar_cndt(cnpj)` |
| **Verificação** | `verificar_debitos(cnpj)` → `{possui_debitos, regular, apto_licitar, observacao}` |
| **Fluxo** | 2 etapas: GET (session) → POST `numCnpjCpf` |
| **Validade padrão** | 180 dias |
| **Base legal** | Lei 12.440/2011 · Art. 29, V da Lei 8.666/93 |
| **Tipos de resultado** | `CNDT` (negativa) · `CPDT-EN` (positiva c/ efeito neg.) · `CPDT` (positiva) |

### 5.3 Bidding Sentinel Agent

**Arquivo:** `modules/bidding/agents/sentinel_agent.py`

- Verifica aptidão para licitação consultando RFB e TST em tempo real
- Cache HTTPx com TTL de **6 horas**
- Retry com backoff: 2s → 4s → 8s
- **Status por documento:** `VALIDO · VENCENDO · VENCIDO · NAO_POSSUI · RENOVANDO · ERRO_CONSULTA`
- **Níveis de alerta:** `OK (>60d) · ATENCAO (30-60d) · URGENTE (15-30d) · CRITICO (<15d ou vencida)`
- **Retorno:** `SentinelResponse` com `apto_licitar: bool` e `motivo_inaptidao: list`

---

## 6. TASKS / JOBS

### 6.1 `ged_sync_cnds` — Celery Task

**Arquivo:** `modules/people_management/ged/tasks/cnd_sync_task.py`

| Item | Detalhe |
|------|---------|
| **Fila** | `ged` |
| **Frequência** | Diária (Celery Beat) |
| **Max retries** | 2 |
| **Retry delay** | 600s (10 min) |
| **Lógica** | Verifica `mtime` dos arquivos PDF em 5 paths de storage |
| **Janela de detecção** | ≤ 24 horas |
| **Ação ao detectar renovação** | Chama `on_cnd_renewed()` para cada CND renovada |
| **Paths monitorados** | `cnd_federal · cnd_estadual · cnd_municipal · crf_fgts · cndt_trabalhista` |
| **Retorno** | `{cnds_checked, cnds_renewed, documents_updated, documents_created, executed_at}` |

### 6.2 `KRONOS.executar_verificacao_diaria()` — GEDEON Agent

**Arquivo:** `modules/gedeon/agents/kronos.py`

| Item | Detalhe |
|------|---------|
| **Frequência** | Diária |
| **Fonte de dados** | Tabela `ged_certidoes` (campo `expiry_date`) + `gp_asos` (ASOs de funcionários) |
| **Janelas de alerta** | 60 · 30 · 15 · 7 · 0 dias antes do vencimento |
| **Eventos publicados** | `FISCAL_CERTIDAO_VENCIDA` · `"fiscal.certidao.vencendo"` |
| **Níveis de alerta** | `ok (verde) · baixo (azul) · medio (amarelo) · alto (laranja) · critico (vermelho)` |
| **Cálculo de renovação** | CND: ~5 dias processing + 2× buffer ≈ iniciar 10 dias antes do vencimento |

---

## 7. EVENTOS E PUBLISHERS

**Arquivo:** `modules/fiscal/publishers.py` → `ConectaEventBus`

### 7.1 Tipos de evento

| Evento | Trigger | Payload-chave |
|--------|---------|---------------|
| `FISCAL_CERTIDAO_VENCIDA` | `expiry_date ≤ hoje` | `certidao_id, tipo, data_vencimento, dias_restantes, nivel` |
| `FISCAL_CERTIDAO_RENOVADA` | Certidão renovada | `certidao_id, tipo, nova_validade, data_renovacao` |
| `"fiscal.certidao.vencendo"` | KRONOS preventivo | `certidao_id, tipo, dias_restantes, nivel, cor` |
| `FISCAL_NFS_EMITIDA` | NFS-e emitida | *(evento secundário)* |

### 7.2 Funções do publisher

| Função | Descrição |
|--------|-----------|
| `publish_certidao_vencida(certidao_id, tipo, data_vencimento, cliente_id, extra)` | Publica evento de vencimento |
| `publish_certidao_renovada(certidao_id, tipo, nova_validade, cliente_id, extra)` | Publica evento de renovação |
| `verificar_e_publicar_vencimentos(certidoes, cliente_id)` | Batch: verifica lista e publica todos |

---

## 8. AGENTES GEDEON

### 8.1 KRONOS — Monitoramento de Vencimentos

| Método | Função |
|--------|--------|
| `verificar_certidoes_sync()` | Consulta síncrona via psql (para use cases sem async) |
| `verificar_certidoes(db)` | Consulta assíncrona via SQLAlchemy |
| `verificar_asos_funcionarios()` | Monitora documentos de saúde ocupacional |
| `executar_verificacao_diaria()` | Job principal: lê + publica + escalada de alertas |

**Tabela de timing de renovação:**

| Tipo | Processamento | Início recomendado |
|------|---------------|-------------------|
| CND Federal | ~5 dias | 10 dias antes do vencimento |
| CNDT Trabalhista | ~5 dias | 10 dias antes do vencimento |
| CRF-FGTS | ~3 dias | 7 dias antes do vencimento |

### 8.2 HERMES — Classificação Automática

**Padrões regex para certidões:**

| Regex | Classificação | Reutilizável |
|-------|--------------|-------------|
| `cnd\|certidao.*negativa.*debito` | `cnd_federal` | ✅ Sim |
| `crf.*fgts\|regularidade.*fgts` | `crf_fgts` | ❌ Não (mensal) |
| `certidao.*trabalhista` | `certidao_trabalhista` | ✅ Sim |
| `alvara.*funcionamento` | `alvara_funcionamento` | ✅ Sim |

- Detecção de duplicatas: SHA-256 hash
- Reutilização entre competências: sim (exceto CRF-FGTS)
- Categoria: `"certidoes"` para todos os tipos CND/CNDT

### 8.3 SOPHIA — Indexação Semântica

Tipos reconhecidos e indexados automaticamente:
`cndt · cnd · cnd_federal · cnd_estadual · cnd_municipal · crf_fgts`

### 8.4 GEDEON Orchestrator — Context Redis

**Subscriptions relacionadas a certidões:**

| Evento | Handler | Ação no Redis |
|--------|---------|---------------|
| `FISCAL_CERTIDAO_VENCIDA` | `_on_certidao_vencida()` | `critico++` no contexto mensal |
| `FISCAL_CERTIDAO_RENOVADA` | `_on_certidao_renovada()` | `critico-- · ok++` |

---

## 9. FLUXO DE DADOS COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│  1. UPLOAD MANUAL                                           │
│  Usuário → POST /certidoes → ged_certidoes                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  2. MONITORAMENTO DIÁRIO (KRONOS)                           │
│  executar_verificacao_diaria()                              │
│  → lê expiry_date de ged_certidoes                          │
│  → publica fiscal.certidao.vencendo (60/30/15/7/0 dias)     │
│  → GEDEON atualiza Redis (cert_ok / alerta / critico)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  3. RENOVAÇÃO AUTOMÁTICA (ged_sync_cnds — Celery diário)    │
│  → verifica mtime dos arquivos PDF (janela 24h)             │
│  → detecta arquivo renovado → chama on_cnd_renewed()        │
│  → busca todos os kits EM_MONTAGEM                          │
│  → atualiza/cria KitDocument (source_module = FISCAL)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  4. VERIFICAÇÃO PARA LICITAÇÃO (Bidding Sentinel)           │
│  → consulta RFB e TST em tempo real (cache 6h)              │
│  → retorna apto_licitar + motivo_inaptidao                  │
│  → notificação via EMAIL / PUSH / INTERNAL                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. CONSTANTES E LIMITES OPERACIONAIS

| Constante | Valor | Uso |
|-----------|-------|-----|
| CND / CNDT — Validade | 180 dias | Expiração padrão |
| CRF-FGTS — Validade | ~30 dias | Renovação mensal obrigatória |
| Janelas de alerta KRONOS | 60 / 30 / 15 / 7 / 0 dias | Escalada de alertas |
| Tempo de renovação CND | ~5 dias | Cálculo de data ideal |
| Tempo de renovação CNDT | ~5 dias | Cálculo de data ideal |
| Tempo de renovação CRF | ~3 dias | Cálculo de data ideal |
| Cache Sentinel (RFB/TST) | 6 horas | Evita excesso de consultas |
| Janela de detecção de renovação | 24 horas | `mtime` do arquivo PDF |
| Retry CND client | 3× backoff exponencial | Rate-limit 429 |
| Retry Celery task | 2× com delay 600s | Falha de sincronização |

---

## 11. ESTRUTURA DE DIRETÓRIOS COMPLETA

```
backend/modules/
├── fiscal/
│   ├── controllers/              # Controllers do módulo fiscal
│   ├── services/                 # Serviços fiscais
│   └── publishers.py             # ← Eventos certidão (vencida/renovada)
│
├── fiscal_contabil/
│   ├── certidoes/                # ← Submódulo específico de certidões
│   ├── contabilidade/
│   ├── impostos/
│   ├── notas_fiscais/ (nfe/nfce/nfse)
│   ├── obrigacoes/
│   └── sped/
│
├── ged/
│   ├── controllers/
│   │   └── ged_certidoes_controller.py  # ← CRUD endpoints
│   └── models/
│       └── ged_certidao.py              # ← ORM + status enum
│
├── people_management/ged/
│   ├── tasks/
│   │   └── cnd_sync_task.py             # ← Celery task diária
│   ├── events/
│   │   └── handlers.py                  # ← on_cnd_renewed()
│   └── models/
│       └── kit_document.py              # ← DocumentType enum
│
├── gedeon/agents/
│   ├── kronos.py                        # ← Monitoramento de vencimentos
│   ├── hermes.py                        # ← Classificação por regex
│   └── sophia.py                        # ← Indexação semântica
│
├── bidding/
│   ├── integrations/receita_federal/
│   │   ├── cnd_client.py               # ← Client HTTP → RFB/PGFN
│   │   └── cndt_client.py             # ← Client HTTP → TST
│   ├── agents/
│   │   └── sentinel_agent.py           # ← Aptidão para licitação
│   └── services/
│       └── notification_service.py     # ← Alertas certidão vencendo
│
└── government_integrations/
    ├── controllers/
    │   └── sync_controller.py          # ← GET /dados/certidoes/{cnpj}
    ├── sync/federal/
    │   └── receita_sync.py             # ← Sync Receita Federal
    └── core/
        └── fgts_inss_manager.py        # ← Gestão CRF-FGTS
```

---

*Gerado por Claude Code — tmux-t1*
*2026-04-09*
