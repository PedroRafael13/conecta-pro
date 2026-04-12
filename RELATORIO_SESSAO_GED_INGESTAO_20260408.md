# RELATÓRIO FINAL DE SESSÃO — GED + Ingestão Histórica Google Drive
**Data:** 2026-04-08
**Branch:** feature/people-management-reorganization
**Módulo:** GED / Google Drive / Ingestão Histórica

---

## Resumo Executivo

Sessão completa de implementação e correção do pipeline de ingestão histórica do Google Drive para o GED do Conecta PRO. Todos os objetivos da sessão foram entregues com zero bugs ativos ao encerrar.

---

## Commits desta Sessão

| Hash | Descrição |
|------|-----------|
| `1dbbd875` | fix(ged): OAuth2 fallback + scope drive + singleton fix |
| `251074ab` | fix(ged): zero bugs no pipeline de ZIPs |
| `44a03bb6` | feat(ged): persistência completa no GED |
| `0caf8a91` | chore(agents): snapshots CTO + métricas |

---

## O Que Foi Feito

### 1. Correção: `IngestaoHistorica(db)` → singleton
`document_controller.py` instanciava `IngestaoHistorica(db)` mas o construtor não aceita argumento. Corrigido para usar o singleton `ingestao`.

### 2. Correção: OAuth2 fallback no `_get_drive_service`
`ingestao_historica._get_drive_service` só tentava service account (arquivo JSON). Adicionado fallback para o singleton `gdrive_service` (OAuth2 com tokens do banco), que é o modo de conexão ativo.

### 3. Correção: Escopo OAuth2 `drive.file` → `drive`
Escopo `drive.file` só permite acesso a arquivos criados pelo app — não aos ZIPs que Jordan fez upload manualmente. Atualizado para `https://www.googleapis.com/auth/drive`. Jordan re-autorizou com o novo escopo.

### 4. Correção: `await` em método síncrono do SOPHIA
`await sophia.indexar_acervo_completo()` falhava com `object dict can't be used in 'await' expression` porque o método é síncrono. Corrigido para `loop.run_in_executor(None, sophia.indexar_acervo_completo)`.

### 5. Correção: `_baixar_arquivo` sem tratamento de erro
`MediaIoBaseDownload.next_chunk()` podia levantar exceção não capturada, causando erro obscuro `NoneType.read` na camada acima. Adicionado try/except retornando `b""` + guard em `processar_zip`.

### 6. Correção: storage path `/opt/conecta-pro/storage/ged` → `/app/uploads/ged`
O container não tem mount para `/opt/conecta-pro/storage/`. O path correto dentro do container é `/app/uploads/ged` (bind mount de `/opt/conecta-pro/uploads/`).

### 7. Correção: `::uuid` em SQL via SQLAlchemy text()
`:cid::uuid` confundia o parser de parâmetros do SQLAlchemy. Corrigido para `CAST(:cid AS uuid)` em todos os lugares.

### 8. Feature: Persistência completa no GED
Segunda etapa da ingestão: após indexar no SOPHIA, cada PDF identificado é:
- Salvo em `/app/uploads/ged/historico/{ged_client_id}/{competencia}/`
- Registrado em `ged_document_kits` (ON CONFLICT idempotente)
- Registrado em `ged_kit_documents` com `source_module='historico_drive'`

Novas funções: `_exec_write_sync`, `_mapear_clients_para_ged`, `_persistir_docs_no_ged`.

---

## Resultado Final da Ingestão

```
POST /api/v1/people-management/ged/documents/ingestao/historica

ZIPs encontrados:    5
ZIPs processados:    5/5
PDFs extraídos:      227
Indexados (SOPHIA):  227
Salvos no GED:        24
Erros:                 0
```

### Kits criados no GED

| Cliente | Competência | Docs |
|---------|-------------|------|
| Condomínio Ideal Flores da Cidade | 2025-01 | 5 |
| Condomínio Ideal Flores da Cidade | 2025-09 | 3 |
| Condomínio Ideal Flores da Cidade | 2025-10 | 2 |
| Condomínio Ideal Flores da Cidade | 2025-11 | 2 |
| Condomínio Mirante das Flores | 2025-09 | 3 |
| Condomínio Parque Residencial Gelain | 2025-01 | 2 |
| Condomínio Prime Arena | 2025-01 | 1 |
| Condomínio Prime Arena | 2025-10 | 3 |
| Condomínio Prime Arena | 2025-11 | 3 |

---

## Pendências Registradas

### PENDÊNCIA #1 — Matching de cliente para 203 PDFs não vinculados
**Descrição:** 227 PDFs foram extraídos dos ZIPs e indexados no SOPHIA. Apenas 24 foram persistidos no GED com `client_id` identificado. Os 203 restantes existem em `gedeon_document_index` com `metadados->>'fonte' = 'historico_drive'` mas sem `client_id` válido.

**Causa:** O algoritmo de identificação (`_identificar_cliente_por_texto` + `_buscar_funcionarios`) não conseguiu associar o texto/nome do PDF a um cliente com certeza suficiente.

**Impacto:** Documentos históricos visíveis via busca SOPHIA mas não aparecendo no GED como kits/arquivos downloadáveis.

**Ação necessária:** Melhorar o matching — sugestões:
1. Expandir `_buscar_funcionarios` para incluir funcionários inativos
2. Adicionar matching por CNPJ extraído do texto do PDF
3. Adicionar matching por razão social parcial (regex fuzzy)
4. Interface manual: tela para associar PDFs não identificados a clientes

**Prioridade:** Média — os documentos estão seguros no SOPHIA, não há perda de dados.

---

### PENDÊNCIA #2 — `smtp_config.json` fora do git
**Descrição:** `config/smtp_config.json` contém credenciais SMTP e foi bloqueado pelo `detect-secrets`. Adicionado ao `.gitignore`.

**Ação necessária:** Mover as credenciais para variáveis de ambiente no `.env` do servidor.

---

## Estado Final do Sistema

| Componente | Estado |
|------------|--------|
| Google Drive OAuth2 | ✅ Conectado (`jordansjesus@gmail.com`, escopo `drive`) |
| `gdrive_config` no banco | ✅ `is_connected=true`, tokens válidos |
| Ingestão histórica endpoint | ✅ `POST .../ingestao/historica` — 0 erros |
| SOPHIA indexado | ✅ 227 docs históricos + 390 existentes = 617 total |
| GED kits históricos | ✅ 9 kits, 24 documentos, arquivos físicos no storage |
| Pipeline idempotente | ✅ Re-executar não duplica (ON CONFLICT) |

---

## Comando para Download deste Relatório (MacBook)

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_SESSAO_GED_INGESTAO_20260408.md ~/Downloads/
```

---

*Gerado por Claude Code — tmux-t1 — Módulo: GED / Ingestão Histórica*
