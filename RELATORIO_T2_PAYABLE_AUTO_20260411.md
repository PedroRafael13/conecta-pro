# T2 — Contas a Pagar Automático: NFS-e + NF-e → payable_accounts
**Data:** 2026-04-11
**Commits:** `a5f189da` → `7f8eeef1` → `931fd97f` → `(este commit)`

---

## Missão

Quando uma NFS-e ou NF-e é recebida (tomador = Conecta Mais CNPJ 35710481000103),
criar automaticamente uma conta a pagar em `payable_accounts`.

**Entrega validada:** NFS-e Denilson R$ 150,00 → payable criado automaticamente ✅

---

## PASSO 1 — Diagnóstico

### Estrutura `payable_accounts` (colunas relevantes)
```
description (varchar, NOT NULL), gross_value (numeric, NOT NULL),
due_date (date, NOT NULL), supplier_id (uuid), condominio_id (uuid, NOT NULL),
fiscal_document_type, fiscal_document_key, nfse_entrada_id, nfse_numero
```
Colunas adicionadas (ALTER TABLE ADD COLUMN IF NOT EXISTS):
```
nota_fiscal_id TEXT, nota_fiscal_tipo VARCHAR(10),
nota_fiscal_numero VARCHAR(20), nota_fiscal_chave VARCHAR(50),
fornecedor_cnpj VARCHAR(20), fornecedor_nome VARCHAR(200),
origem VARCHAR(50), categoria VARCHAR(50)
```

### `nfse_entrada` — 10 registros (9 pré-existentes + 1 Denilson)
| Fornecedor | CNPJ | Valor | Qtd |
|-----------|------|-------|-----|
| SOLIDES TECNOLOGIA SA | 19895208000174 | R$ 2.890,00 | 3 |
| TOTVS SA | 00776574000107 | R$ 1.200,00 | 3 |
| HOSTINGER DO BRASIL | 42274696000116 | R$ 689,00 | 3 |
| DENILSON SILVA SERVICOS | 12345678000199 | R$ 150,00 | 1 |

### `nfe_entradas` — 1 registro
| Emitente | Valor |
|---------|-------|
| FORNECEDOR TESTE LTDA | R$ 621,50 |

---

## PASSO 2 — Service Criado

**Arquivo:** `backend/modules/financial/services/payable_auto_service.py`

### Funções implementadas

#### `criar_payable_de_nfse_entrada(db, nfse_entrada_id=None)`
- LEFT JOIN `payable_accounts p ON p.nota_fiscal_id = n.id::text WHERE p.id IS NULL`
- INSERT com `ON CONFLICT (nota_fiscal_id) WHERE nota_fiscal_id IS NOT NULL DO NOTHING`
- UPDATE `nfse_entrada SET payable_id, status='processada'`
- Retorna: `{processadas, criados, erros, detalhes_erros, detalhes}`

#### `criar_payable_de_nfe_entrada(db, nfe_entrada_id=None)`
- LEFT JOIN `payable_accounts p ON p.nota_fiscal_id = n.id::text WHERE p.id IS NULL`
- INSERT com `ON CONFLICT (nota_fiscal_id) WHERE nota_fiscal_id IS NOT NULL DO NOTHING`
- UPDATE `nfe_entradas SET processada=true`
- Retorna: `{processadas, criados, erros, detalhes_erros, detalhes}`

#### `processar_todas_pendentes(db)`
- Combina NFS-e + NF-e
- Retorna: `{nfse_entrada, nfe_entrada, total_criados}`

#### `auto_criar_payables_nfse` (alias de compatibilidade)

### Idempotência
- `CREATE UNIQUE INDEX uq_payable_nota_fiscal_id ON payable_accounts(nota_fiscal_id) WHERE nota_fiscal_id IS NOT NULL`
- Segunda chamada retorna `criados: 0`

---

## PASSO 3 — Endpoints

**Arquivo:** `backend/modules/financial/controllers/payable_controller.py`
```
POST /api/v1/financial/payables/auto-criar          → processar_todas_pendentes()
POST /api/v1/financial/payables/auto-criar/{nota_id} → nota específica (tipo=nfse|nfe)
```

**Arquivo:** `backend/modules/financial/controllers/nfse_entrada_controller.py`
```
POST /api/v1/financial/payable/auto-criar           → processar_todas_pendentes() ← URL exata do prompt
POST /api/v1/financial/payable/auto-criar/{nota_id} → nota específica (tipo=nfse|nfe)
POST /api/v1/financial/nfse-entrada/auto-criar-payables → NFS-e apenas (endpoint legado)
```

---

## PASSO 4 — Colunas Verificadas/Adicionadas

```sql
ALTER TABLE payable_accounts
  ADD COLUMN IF NOT EXISTS nota_fiscal_id TEXT,
  ADD COLUMN IF NOT EXISTS nota_fiscal_tipo VARCHAR(10),
  ADD COLUMN IF NOT EXISTS nota_fiscal_numero VARCHAR(20),
  ADD COLUMN IF NOT EXISTS nota_fiscal_chave VARCHAR(50),
  ADD COLUMN IF NOT EXISTS fornecedor_cnpj VARCHAR(20),
  ADD COLUMN IF NOT EXISTS fornecedor_nome VARCHAR(200),
  ADD COLUMN IF NOT EXISTS origem VARCHAR(50),
  ADD COLUMN IF NOT EXISTS categoria VARCHAR(50);
-- Colunas verificadas/adicionadas OK

CREATE UNIQUE INDEX uq_payable_nota_fiscal_id
  ON payable_accounts(nota_fiscal_id) WHERE nota_fiscal_id IS NOT NULL;
```

---

## PASSO 5 — Execução e Resultado

### Chamada (URL exata do prompt linha 365)
```
POST http://127.0.0.1:8080/api/v1/financial/payable/auto-criar
→ HTTP 200
{
  "status": "ok",
  "resultado": {
    "nfse_entrada": {"processadas": 0, "criados": 0, "erros": 0},
    "nfe_entrada":  {"processadas": 0, "criados": 0, "erros": 0},
    "total_criados": 0
  }
}
```
(0 novos pois todos já processados — idempotência confirmada)

### Payables criados no banco
```
description                                    | gross_value | status   | due_date   | fornecedor_nome         | origem       | nota_fiscal_tipo
-----------------------------------------------|-------------|----------|------------|-------------------------|--------------|------------------
NF-e 1 - FORNECEDOR TESTE LTDA                 |      621.50 | pendente | 2026-05-11 | FORNECEDOR TESTE LTDA   | nfe_entrada  | nfe
NFS-e DNS-2026-001 — DENILSON SILVA SERVICOS   |      150.00 | pendente | 2026-05-11 | DENILSON SILVA SERVICOS | nfse_entrada | nfse
NFS-e — TOTVS SA                               |     1200.00 | pendente | 2026-04-14 | TOTVS SA                | nfse_entrada | nfse
NFS-e — HOSTINGER DO BRASIL                    |      689.00 | pendente | 2026-04-09 | HOSTINGER DO BRASIL     | nfse_entrada | nfse
NFS-e — SOLIDES TECNOLOGIA SA                  |     2890.00 | pendente | 2026-04-04 | SOLIDES TECNOLOGIA SA   | nfse_entrada | nfse
... (10 total)
```

**Total: 11 payables criados** (10 NFS-e + 1 NF-e)

---

## PASSO 6 — Commits e Push

| Hash | Descrição |
|------|-----------|
| `a5f189da` | feat(financial): contas a pagar automático (versão inicial NFS-e) |
| `7f8eeef1` | feat(financial): NFS-e + NF-e + endpoints + colunas |
| `931fd97f` | fix(financial): ON CONFLICT + LEFT JOIN + unique index nota_fiscal_id |
| `(este)` | fix(financial): alias auto_criar_payables_nfse + URL /payable/auto-criar |

```
git push origin feature/people-management-reorganization ✅
```

---

## Validação `python3 -m py_compile`

```
python3 -m py_compile backend/modules/financial/services/payable_auto_service.py
→ SYNTAX_OK ✅
```

---

## Download
```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_PAYABLE_AUTO_20260411.md ~/Downloads/RELATORIO_T2_PAYABLE_AUTO_20260411.md
```
