# T4 — Saídas Sem Nota → Justificativa Obrigatória
**Data:** 2026-04-11
**Commit:** `88b341d9` | pushed → `feature/people-management-reorganization`
**Usuário de teste:** `jjesus@conectamais.pro` (Jordan Jesus, role: admin)
**Veredicto:** ✅ 100% IMPLEMENTADO — 5 endpoints funcionais, bloqueio de fechamento ativo, `requires_justification` atualizando corretamente

---

## PASSO 1 — Estado das Transações (resultado real)

```sql
SELECT COUNT(*) as total,
  SUM(CASE WHEN transaction_type='debit' THEN 1 ELSE 0 END) as saidas,
  SUM(CASE WHEN requires_justification=TRUE THEN 1 ELSE 0 END) as requer_justificativa
FROM bank_transactions;
--  total | saidas | requer_justificativa
--    649 |    616 |                  598
```

| Métrica | Valor |
|---------|-------|
| Total transações | 649 |
| Saídas (debit) | 616 |
| `requires_justification = TRUE` (pendentes) | 598 |
| Valor total pendente | **R$ 182.564,91** |
| Justificadas na sessão de testes | 3 |
| Pendentes ao final | **595** |

### Adaptação necessária — Schema real diverge do prompt

| Coluna no prompt | Coluna real na tabela | Observação |
|-----------------|-----------------------|-----------|
| `tipo` | `transaction_type` | valores: `debit`, `credit` |
| `valor` | `amount` | negativo para débitos |
| `data` | `transaction_date` | tipo `date` |
| `descricao` | `description` | varchar |
| `reconciliado` | `reconciliation_status` | varchar |
| `contraparte_nome` | `counterparty_name` | varchar |
| `contraparte_documento` | `counterparty_document` | varchar |

O service foi escrito com os nomes corretos em todos os lugares.

---

## PASSO 2 — Schema Migration

```sql
ALTER TABLE bank_transactions
  ADD COLUMN IF NOT EXISTS requires_justification   BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS justificativa            TEXT,
  ADD COLUMN IF NOT EXISTS justificativa_categoria  VARCHAR(50),
  ADD COLUMN IF NOT EXISTS justificativa_responsavel VARCHAR(200),
  ADD COLUMN IF NOT EXISTS justificativa_data       TIMESTAMP;

UPDATE bank_transactions
SET requires_justification = TRUE
WHERE transaction_type = 'debit'
  AND reconciliation_status = 'pendente'
  AND amount < 0;
-- → UPDATE 598
```

---

## PASSO 2 — `justificativa_service.py`

**Arquivo:** `backend/modules/financial/services/justificativa_service.py`

| Função | Comportamento |
|--------|---------------|
| `registrar_justificativa(tx_id, categoria, descricao, responsavel)` | UPDATE banco: `justificativa`, `requires_justification=FALSE`, `reconciliation_status='justificado'`; notifica Telegram |
| `listar_sem_justificativa(mes, ano)` | COUNT real via subconsulta (sem LIMIT artificial); 200 rows exibição |
| `verificar_fechamento_periodo(mes, ano)` | Bloqueia se `total > 0`; alerta Telegram com montante pendente |
| `alertar_pendentes()` | Resumo Telegram de todas as pendências |
| `_notificar_telegram(msg)` | Usa `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`; log silencioso se não configurado |

---

## PASSO 3 — `justificativa_controller.py` + Registro no main

**Arquivo:** `backend/modules/financial/controllers/justificativa_controller.py`

Todos os 5 endpoints com `Depends(get_current_user)`:

| Método | Endpoint | HTTP |
|--------|----------|------|
| GET | `/api/v1/justificativa/categorias` | 200 ✅ |
| GET | `/api/v1/justificativa/pendentes?mes=3&ano=2026` | 200 ✅ |
| GET | `/api/v1/justificativa/verificar-fechamento/3/2026` | 200 ✅ |
| POST | `/api/v1/justificativa/registrar` | 200 ✅ |
| POST | `/api/v1/justificativa/alertar` | 200 ✅ |

**Registro no `main_production.py`** — inserido após bloco Financeiro (linha 682):
```python
# Justificativas Fiscais — Saídas Sem NF (Lucro Real)
try:
    from modules.financial.controllers.justificativa_controller import (
        router as justificativa_router,
    )
    api_router.include_router(justificativa_router, tags=["Justificativas Fiscais"])
    logger.info("Justificativas Fiscais: OK")
except Exception as _e:
    logger.warning(f"Justificativas Fiscais: {_e}")
```
Log: `INFO | Justificativas Fiscais: OK` ✅

---

## PASSO 4 — Validação Completa (usuário `jjesus@conectamais.pro`)

### GET /categorias
```json
{"categorias": [
  {"id": "salario",               "desc": "Pagamento de salário ou pró-labore"},
  {"id": "adiantamento",          "desc": "Adiantamento a funcionário"},
  {"id": "reembolso",             "desc": "Reembolso de despesas"},
  {"id": "taxa_bancaria",         "desc": "Tarifas e taxas bancárias"},
  {"id": "imposto",               "desc": "Pagamento de impostos e guias"},
  {"id": "servico_sem_nf",        "desc": "Serviço sem obrigação fiscal"},
  {"id": "transferencia_interna", "desc": "Movimentação entre contas próprias"},
  {"id": "outros",                "desc": "Outros (requer descrição detalhada)"}
]}
```

### GET /pendentes?mes=4&ano=2026
```json
{"total": 0, "valor_total": 0.0, "transacoes": []}
```
Abril/2026: sem saídas pendentes — período pode ser fechado ✅

### GET /verificar-fechamento/3/2026
```json
{
  "pode_fechar": false,
  "pendentes": 453,
  "valor_pendente": 169317.71,
  "mes": 3,
  "ano": 2026,
  "mensagem": "Bloqueado: 453 saídas sem justificativa (R$ 169,317.71)"
}
```

### GET /verificar-fechamento/4/2026
```json
{
  "pode_fechar": true,
  "pendentes": 0,
  "valor_pendente": 0,
  "mensagem": "Período pode ser fechado"
}
```

### POST /registrar
```json
{
  "status": "justificado",
  "transacao_id": "33286846-dc13-48fa-91ed-c935aaa7fb25",
  "valor": 32.0,
  "categoria": "reembolso",
  "descricao": "Reembolso de despesas operacionais referente a março/2026 com comprovante"
}
```
**Verificação DB pós-registro:**
```
requires_justification = FALSE  ✅
justificativa_categoria = reembolso  ✅
reconciliation_status = justificado  ✅
```

### POST /alertar
```json
{"total": 595, "valor_total": 182424.91}
```
(Telegram: não configurado → log silencioso)

---

## Auditoria — Problemas Encontrados e Corrigidos

| # | Problema | Causa | Correção |
|---|----------|-------|---------|
| 1 | `requires_justification` não atualizado em 2 registros de teste iniciais | Bug de estado — container tinha versão PRÉ-ruff enquanto o ruff reformatou os arquivos no disco durante o pre-commit hook; container não foi resincronizado | `docker cp` das versões pós-ruff + `docker restart` |
| 2 | `listar_sem_justificativa` retornava `total=200` sempre | Query usava `len(rows)` com LIMIT 200 em vez de COUNT real | Adicionada subconsulta `SELECT COUNT(*), SUM(ABS(amount))` sem LIMIT |
| 3 | Schema do prompt usava colunas inexistentes (`tipo`, `valor`, `data`) | Schema real tem `transaction_type`, `amount`, `transaction_date` | Service reescrito com colunas reais; todas as queries adaptadas |

---

## Telegram — Configuração Necessária

```bash
# Adicionar ao /opt/conecta-pro/.env:
TELEGRAM_BOT_TOKEN=<token do BotFather>
TELEGRAM_CHAT_ID=<chat_id do Jordan>
```

Enquanto não configurado, logs aparecem como `INFO: Telegram (não configurado): ...` sem falha.

---

## PASSO 5 — Commit e Push

```
88b341d9  feat(financial): justificativa obrigatória saídas sem NF — Lucro Real
Branch: feature/people-management-reorganization → pushed ✅

3 files changed, 345 insertions(+):
  create: backend/modules/financial/controllers/justificativa_controller.py
  create: backend/modules/financial/services/justificativa_service.py
  modify: backend/main_production.py
```

---

## Estado Final do Banco

```
bank_transactions:
  total:                   649
  saídas (debit):          616
  requires_justification:  595 (pendentes)
  justificadas:            3 (testes funcionais)
  valor pendente total:    R$ 182.424,91
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T4_JUSTIFICATIVA_20260411.md ~/Downloads/
```
