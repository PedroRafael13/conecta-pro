# T4 CPRO12 — Diagnóstico Profundo GEDEON
Data: 2026-05-05
Tipo: READ-ONLY (INV-2: zero alterações de código)

---

## Agentes implementados

**KRONOS** (`backend/modules/gedeon/agents/kronos.py`, 401 linhas):
- `calcular_nivel_alerta(data_vencimento)` — 60d/30d/15d/7d/CRÍTICO
- `data_ideal_renovacao(tipo, vencimento)` — prazo por tipo de certidão
- `verificar_certidoes_sync()` — queries DB sync, retorna lista de alertas
- `verificar_asos_sync()` — queries `gp_asos` JOIN `employees`
- `verificar_certidoes()` — wrapper async
- `verificar_asos_funcionarios()` — wrapper async
- `executar_verificacao_completa()` — orquestra certidões + ASOs + publica eventos

**THEMIS** (`backend/modules/gedeon/agents/themis.py`, 192 linhas):
- `verificar_pendentes()` — lista `ged_kit_documents` com `is_signed=False` há > 48h
- `calcular_tempo_medio()` — média de tempo para assinatura dos fechados
- `verificar_e_alertar()` — detecta pendentes + publica `GED_ASSINATURA_PENDENTE`
- `resumo()` — totais para dashboard

**ATLAS** (`backend/modules/gedeon/agents/atlas.py`, 312 linhas):
- `registrar_kit_concluido(kit)` — UPSERT em `gedeon_kit_history` + `gedeon_client_patterns`
- `obter_contexto_historico(client_id, competencia)` — histórico de kits do cliente
- `detectar_anomalia(client_id, competencia, score)` — flag se score difere >30% da média
- `gerar_insights_mensais()` — insights agregados para dashboard ATLAS

> SOPHIA (`sophia.py`) referencia DP/alocação mas é assistente NLP — não é agente de matching.

---

## Como o kit é montado hoje

**Fluxo completo:**
```
Onvio sync → onvio_documents (605 docs)
     ↓
OnvioDocScopeClassifier (regex no nome_arquivo)
→ doc_scope = condominio | funcionario | empresa_matriz | NULL
→ condominio_id preenchido via match_condominio() (10 padrões fixos)
→ referente_a_employee_id via match_employee() (nome no filename)
     ↓
KitBuilderService (people_management/ged)
→ auto_build_all_kits(reference_month) → build_kit_for_client()
→ MAPA_TIPOS_ONVIO (19 categorias) → document_type em ged_kit_documents
→ coleta: payslips (DP) + certidões + escalas + benefícios
     ↓
ged_document_kits (kits) + ged_kit_documents (slots)
```

**Critério de matching atual — por que 0% fica preenchido em abr/2026:**
- Abr/2026: 10 docs Onvio, **todos com `doc_scope=NULL`** — scope classifier não foi executado
- Mar/2026: 353 slots, apenas 7 preenchidos (2%) — docs Onvio têm scope mas `file_path` não é gravado nos slots
- `referente_a_employee_id` preenchido em apenas 39/605 docs (6,4%)

---

## Lacunas para matching completo

| # | Lacuna | Impacto |
|---|--------|---------|
| L1 | `referente_a_employee_id` ausente em 566/605 docs | Docs `funcionario`-scope não vinculam ao funcionário correto |
| L2 | Abr/2026: 10 docs com `doc_scope=NULL` | Bloqueio total — nenhum doc pode ser casado ao kit |
| L3 | Sem `file_path` gravado no slot ao fazer match | `ged_kit_documents.file_path` fica NULL mesmo com doc Onvio disponível |
| L4 | `MAPA_TIPOS_ONVIO` cobre 19/38 categorias (~50%) | ~316 docs em categorias não mapeadas ignorados no matching |
| L5 | Matching por regex no `nome_arquivo` (frágil) | Novos condomínios exigem edição manual de `match_condominio()` |
| L6 | Nenhuma task de retroativo/backfill existe | `reprocess` aparece só em `enrichment_service.py` (extração PDF) — não em kits |
| L7 | Comprovante salário via Banco Inter: módulo `inter/` ausente no container | Bloqueio externo — Inter sync não funciona (ver §87) |

---

## Qual agente deve fazer o matching?

**Nenhum agente atual é adequado.** KRONOS é alertas temporais, THEMIS é assinaturas, ATLAS é aprendizado histórico.

**Recomendação: novo agente HERMES** (já existe esboço em `gedeon/agents/hermes.py`).

HERMES deve:
1. Receber `onvio_document_id` + `mes_ref`
2. Consultar `employee_alocacoes` para resolver `funcionario → condomínio`
3. Gravar `referente_a_employee_id` + `condominio_id` no `onvio_documents`
4. Executar `build_completude(condominio_id, mes_ref)` via `KitBuilderService` (gedeon)
5. Gravar `file_path` no slot correspondente em `ged_kit_documents`
6. Publicar evento `GED_KIT_DOCUMENTO_VINCULADO` no Event Bus

Task Celery: `hermes_vincular_docs_mes(mes_ref)` — agendado na 1ª do mês + disponível ad hoc para retroativos.

---

## Dados disponíveis para os 3 meses retroativos

| Mês | Docs Onvio | Kits | Slots | Preenchidos | Pct médio |
|-----|------------|------|-------|-------------|-----------|
| Fev/2026 | 29 (22 cond + 2 func + 4 matriz + 1 sem scope) | **0 kits** | — | — | N/A |
| Mar/2026 | 43 (26 cond + 3 func + 14 matriz) | 8 kits | 353 | 7 | 2,0% |
| Abr/2026 | 10 (10 sem scope — doc_digitalizado) | 10 kits | 884 | 0 | 0,0% |

**Categorias disponíveis Fev/2026:** folha_pagamento(7), recibo_folha(7), dctfweb_*×6, fgts_*×3, inss_guia(1), documento_digitalizado(3)
**Categorias disponíveis Mar/2026:** folha_pagamento(9), recibo_folha(9), dctfweb_*×6, fgts_*×3, atestado(1), documento_digitalizado(13)
**Categorias disponíveis Abr/2026:** documento_digitalizado(10) — todos sem scope, todos não mapeáveis

---

## Tipos de doc preenchidos vs faltantes (retroativos)

*(Filtro: `ged_document_kits.reference_month >= 2026-02-01`, todos os meses Mar+Abr)*

| document_type | Slots | Preenchidos | % |
|---------------|-------|-------------|---|
| contracheque | 186 | 51 | 27,4% |
| comprovante_vt | 153 | 51 | 33,3% |
| comprovante_vr | 153 | 51 | 33,3% |
| comprovante_va | 153 | 51 | 33,3% |
| folha_ponto | 153 | 51 | 33,3% |
| escala_mes | 153 | 51 | 33,3% |
| crf_fgts | 24 | 8 | 33,3% |
| cnd_municipal | 24 | 8 | 33,3% |
| cnd_estadual | 24 | 8 | 33,3% |
| cndt_trabalhista | 24 | 8 | 33,3% |
| cnd_federal | 24 | 8 | 33,3% |
| folha_pagamento | 14 | 7 | 50,0% |
| folhas_ponto | 47 | 0 | 0% |
| comp_salario_individual | 47 | 0 | 0% |
| comp_va_solides | 46 | 0 | 0% |
| comp_vt_individual | 46 | 0 | 0% |
| contrato_trabalho | 40 | 0 | 0% |
| comp_vt_va_combinado | 40 | 0 | 0% |
| ficha_empregado | 40 | 0 | 0% |
| gfd_fgts_rescisao | 34 | 0 | 0% |
| relatorio_gfd_rescisao | 34 | 0 | 0% |
| comp_fgts_rescisao | 13 | 0 | 0% |
| nfse | 10 | 0 | 0% |
| boleto | 8 | 0 | 0% |
| dctfweb_extrato | 7 | 0 | 0% |
| cnd_sefaz | 7 | 0 | 0% |
| comp_pag_fgts | 7 | 0 | 0% |
| dctfweb_recibo | 7 | 0 | 0% |
| cnd_caixa | 7 | 0 | 0% |
| relatorio_gfd_fgts | 7 | 0 | 0% |
| dctfweb_declaracao | 7 | 0 | 0% |
| gfd_fgts_mensal | 7 | 0 | 0% |
| cnd_rfb | 7 | 0 | 0% |
| cnd_prefeitura | 7 | 0 | 0% |
| cnd_trabalhista | 7 | 0 | 0% |
| recibo_vt_va | 7 | 0 | 0% |
| relatorio_pedido_va | 6 | 0 | 0% |
| aso | 3 | 0 | 0% |

> Nota: Mai/2026 (11 kits, 346 slots, 346 preenchidos = 100%) excluído da tabela pois é o mês corrente — não retroativo.

---

## Plano para homologar os 3 meses

**Pré-requisito:** scope classifier nos 169 docs com `doc_scope=NULL`
```
POST /api/v1/onvio/reclassify
```
Esperado: 10 docs de abr/2026 (documento_digitalizado) recebem scope após classificação.

**Fevereiro/2026** — Prioridade 1 (0 kits, 29 docs disponíveis):
```
POST /people-management/ged/auto-assemble?reference_month=2026-02-01
```
Esperado: até 8 novos kits criados + matching folha_pagamento + dctfweb + fgts.

**Março/2026** — Prioridade 2 (8 kits parciais, 43 docs disponíveis):
```
POST /people-management/ged/auto-assemble?reference_month=2026-03-01
```
Esperado: complementar kits existentes; slots folha_pagamento(9) e dctfweb devem ser preenchidos.

**Abril/2026** — Prioridade 3 (pós reclassify):
```
POST /people-management/ged/auto-assemble?reference_month=2026-04-01
```
Esperado: se `documento_digitalizado` receber scope=condominio, até 10 docs vinculados a kits existentes.

**Validação pós-execução:**
```sql
SELECT reference_month, COUNT(*) kits, COUNT(d.file_path) preenchidos
FROM ged_document_kits k LEFT JOIN ged_kit_documents d ON d.kit_id = k.id
WHERE k.reference_month >= '2026-02-01' AND k.reference_month < '2026-05-01'
GROUP BY k.reference_month ORDER BY k.reference_month;
```

---

Commit: bd6d021f

T4 CPRO12 DIAGNÓSTICO OK — GEDEON matching e retroativos mapeados.
