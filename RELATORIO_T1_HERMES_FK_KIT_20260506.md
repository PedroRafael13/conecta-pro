# T1 — FK kit_document_id + Linkagem HERMES bulk Inter → kit GED
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** FEAT — migration + linkagem bulk
**Commits:** `d42042f7` (feat), `3d450fa6` (docs §118)

---

## RESULTADO

| Métrica | Valor |
|---------|-------|
| Migration aplicada | ✅ `sprint89_inter_kit_fk` |
| Endpoint criado | ✅ `POST /api/v1/financeiro/inter/hermes/linkar` |
| Candidatos à linkagem | 615 |
| Vinculados | **41** |
| Completude GED antes | 24.3% (403/1656) |
| Completude GED depois | **26.8% (444/1656)** |
| Ganho | +2.5pp / +41 slots |

---

## STEP 1 — DIAGNÓSTICO

### Schema real das tabelas

| Tabela | Colunas relevantes |
|--------|-------------------|
| `inter_transactions` | id, data_lancamento, tipo_operacao, valor, raw_payload (JSONB), detalhes_destinatario (JSONB), matched_payroll_id |
| `inter_transaction_categorias` | transaction_id (FK), categoria, document_type, incluir_no_kit |
| `ged_kit_documents` | id, kit_id, employee_id, document_type, file_path, source_module, source_record_id |

`inter_transactions` **não tinha** `kit_document_id` — coluna criada pela migration.

### HERMES (modules/gedeon/agents/hermes.py)

HERMES é um agente de classificação/linking Onvio → kit. Já tinha lógica para
`TIPOS_INTER` mas sem mecanismo real de linkagem via FK. Apenas registrava
`resumo_kit_colaborador` nos logs.

### Linkagem existente em outras fontes

`file_path` preenchido via:
- `source_module = 'dp'` — folha de ponto, comprovantes benefícios
- `source_module = 'fiscal'` — certidões
- `source_module = 'gedeon'` — Onvio matching
- **NOVO:** `source_module = 'inter'` — comprovantes de pagamento Inter

---

## STEP 2 — MIGRATION ALEMBIC

### Arquivo: `alembic/versions/sprint89_inter_kit_fk.py`

```python
revision = "sprint89_inter_kit_fk"
down_revision = "sprint88_inter_cat"

def upgrade():
    op.add_column(
        "inter_transactions",
        sa.Column(
            "kit_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_kit_documents.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_inter_tx_kit_document", "inter_transactions", ["kit_document_id"])
```

**Nota:** `alembic revision --autogenerate` falhou (conflito de chain no container —
`KeyError: 'sprint79_justification_employee_uuid'`). Migration criada manualmente
seguindo padrão dos arquivos existentes e aplicada via psql diretamente.
Registrada em `alembic_version` tabela.

### Aplicação

```sql
ALTER TABLE inter_transactions
  ADD COLUMN IF NOT EXISTS kit_document_id UUID
  REFERENCES ged_kit_documents(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_inter_tx_kit_document ON inter_transactions(kit_document_id);
```

Confirmado: `column_name = kit_document_id, data_type = uuid, is_nullable = YES` ✅

---

## STEP 3 — IMPLEMENTAÇÃO LINKAGEM

### `InterCategorizacaoService.processar_linkagem_bulk()` (categorizacao_service.py)

Algoritmo:
1. Busca todas as transações com `categoria IN (salario, vale_transporte, vale_alimentacao, vt_va_combinado)` e `kit_document_id IS NULL`
2. Para cada transação: resolve beneficiário via `detalhes_destinatario->>'nome'` ou `raw_payload->>'counterpart_name'`
3. Encontra `employee` por ILIKE matching (primeiro + último nome)
4. Encontra `condominio` via `employee_alocacoes` (ativo = true)
5. Mapeia `condominio → ged_client` por interseção de palavras significativas
6. Encontra `ged_document_kits` pelo `reference_month` correspondente ao mês da transação
7. Encontra slot vazio `ged_kit_documents` para o employee + document_type
8. UPDATE `inter_transactions.kit_document_id = slot.id`
9. UPDATE `ged_kit_documents.file_path = '/inter/comprovante/{tx_id}'`, `source_record_id = tx.id`, `source_module = 'inter'`

### Endpoint

```python
@router.post("/hermes/linkar", status_code=200)
def hermes_linkar_bulk(mes_ref: str | None = Query(None), ...):
    svc = InterCategorizacaoService(db)
    return svc.processar_linkagem_bulk(mes_ref=mes_ref)
```

Rota completa: `POST /api/v1/financeiro/inter/hermes/linkar`

---

## STEP 4 — EXECUÇÃO

### Resultado da linkagem

```json
{
  "vinculados": 41,
  "sem_funcionario": 408,
  "sem_slot": 166,
  "total_candidatos": 615,
  "mes_ref": "todos"
}
```

### Análise dos não-vinculados

| Motivo | Qtd | Causa |
|--------|-----|-------|
| `sem_funcionario` | 408 | `detalhes_destinatario.nome` / `counterpart_name` não matcheia nome em `employees` — nomes abreviados, diferentes, ou transações sem beneficiário nominal |
| `sem_slot` | 166 | Employee encontrado mas kit do mês sem slot vazio para o `document_type` (slot já preenchido ou kit não criado para aquele mês/condomínio) |

### Completude GED

```
ANTES:  403/1656 = 24.3%
DEPOIS: 444/1656 = 26.8%
GANHO:  +41 slots / +2.5pp
```

### FK verificado no banco

```
vinculados: 41 | pendentes: 574 | total: 615
```

---

## STEP 5 — COMMITS

| Hash | Conteúdo |
|------|----------|
| `d42042f7` | `feat(hermes): FK kit_document_id + linkagem bulk Inter → kit GED (§118)` |
| `3d450fa6` | `docs: §118 — FK Inter→kit + HERMES bulk (41/615 vinculados, 24.3%→26.8%)` |

Push: `origin/feature/people-management-reorganization` ✅

---

## NOTAS TÉCNICAS

### uvicorn 0.34 não recarrega rotas via SIGHUP

SIGHUP sem `--reload` não recarrega o app object. `docker restart` foi necessário
para carregar a nova rota no FastAPI. Backend reiniciado às 18:44 e voltou healthy.

### alembic revision --autogenerate falhou

Conflito de chain: `KeyError: 'sprint79_justification_employee_uuid'` no container.
Migration criada manualmente e aplicada via psql — padrão idêntico às existentes.

---

## SELF-CHECK

| Item | Status |
|------|--------|
| INV-1 — leitura completa hermes.py, categorizacao_service.py, inter_controller.py | ✅ |
| INV-2 — migration ADD COLUMN apenas, sem DROP/ALTER TYPE | ✅ |
| INV-3 — arquivo migration em alembic/versions/ com nome descritivo | ✅ |
| INV-4 — hot-copy backend (SIGHUP → restart necessário para novas rotas) | ✅ |
| INV-5 — py_compile em todos os arquivos modificados | ✅ OK |
| STEP 1 — schema das 3 tabelas | ✅ |
| STEP 2 — migration criada e aplicada | ✅ |
| STEP 3 — processar_linkagem_bulk() implementado | ✅ |
| STEP 3 — endpoint POST /hermes/linkar criado | ✅ |
| STEP 4 — linkagem executada: 41/615 vinculados | ✅ |
| STEP 4 — verificação FK | ✅ |
| STEP 4 — completude GED verificada: 24.3% → 26.8% | ✅ |
| STEP 5 — git add backend/ + commit + push | ✅ d42042f7 |
| STEP 5 — CONTRACTS_GEDEON.md §118 + commit + push | ✅ 3d450fa6 |

---

**§118 concluído. Migration aplicada. 41/615 Inter comprovantes vinculados ao kit GED.
Completude: 24.3% → 26.8%. 408 transações pendentes por nome de beneficiário não mapeado — requer melhoria no matching ou enriquecimento dos dados de employee.**
