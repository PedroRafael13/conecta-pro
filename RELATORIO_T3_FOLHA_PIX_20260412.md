# RELATÓRIO T3 — PAGAMENTO FOLHA VIA PIX INTER (51 FUNCIONÁRIOS)
**Data:** 2026-04-12
**Branch:** feature/people-management-reorganization
**Commit:** ede97284
**Módulo:** people_management/dp + banking [session: tmux-t1]

---

## RESULTADO FINAL

| Métrica | Valor |
|---------|-------|
| Funcionários ativos | **46** |
| Holerites março/2026 (published) | **51** |
| Funcionários com chave PIX | **46** (100%) |
| Total folha março/2026 | **R$ 66.677,59** |
| Endpoint preview | ✅ HTTP 200 |
| Service validado | ✅ via docker exec |
| Commit + push | ✅ ede97284 |

---

## PASSO 1 — DIAGNÓSTICO

### Colunas reais usadas
```
employees:   pix (varchar 100) — existia, vazia
             banco, agencia, conta, tipo_conta — existiam, vazias
hr_payslips: net_salary, status, reference_month, reference_year, employee_id
```

### hr_payslips março/2026
```
51 holerites | status: published | total: R$66.677,59
  mín: R$0,00 | máx: R$2.334,09
```

---

## PASSO 2 — COLUNAS E TABELAS

### employees — novas colunas
```sql
ADD COLUMN IF NOT EXISTS pix_key VARCHAR(150)
ADD COLUMN IF NOT EXISTS pix_key_type VARCHAR(20) DEFAULT 'CPF'
ADD COLUMN IF NOT EXISTS banco_codigo VARCHAR(10)
ADD COLUMN IF NOT EXISTS banco_agencia VARCHAR(10)
ADD COLUMN IF NOT EXISTS banco_conta VARCHAR(20)
ADD COLUMN IF NOT EXISTS banco_tipo VARCHAR(20) DEFAULT 'CORRENTE'
```

### Seed pix_key (46 funcionários)
```sql
UPDATE employees
SET pix_key = regexp_replace(cpf, '[^0-9]', '', 'g'),
    pix_key_type = 'CPF'
WHERE status = 'ativo' AND cpf IS NOT NULL;
-- → 46 rows updated
```

### payroll_payments — nova tabela
```sql
CREATE TABLE payroll_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    payslip_id UUID,
    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    valor_liquido NUMERIC(12,2) NOT NULL,
    metodo VARCHAR(20) NOT NULL DEFAULT 'PIX',
    pix_key VARCHAR(150),
    pix_e2e_id VARCHAR(100),
    pix_txid VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pendente',
    data_pagamento TIMESTAMP,
    comprovante_id VARCHAR(100),
    erro_msg TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_payroll_payment_emp_mes_ano UNIQUE (employee_id, mes, ano)
);
```

---

## PASSO 3 — SERVICE CRIADO

**Arquivo:** `backend/modules/people_management/services/folha_payment_service.py`

```python
def preparar_lote_folha(mes, ano) -> dict
async def pagar_funcionario_pix(employee_id, payslip_id, pix_key, valor, ...) -> dict
async def processar_folha_completa(mes, ano, apenas_preview=False) -> dict
def status_pagamentos_folha(mes, ano) -> dict
```

### Adaptações ao schema real
| Prompt original | Schema real | Solução |
|-----------------|-------------|---------|
| `InterBankAdapter` | `InterAdapter` | Importa classe correta |
| `initiate_pix(chave_pix, valor, descricao, txid)` | `initiate_pix(pix_key, amount: Decimal, description)` | Assinatura real |
| Schema simples | Adapter async (mTLS OAuth2) | Service async com await |
| `employees.pix_key` | `employees.pix` (existente) + `pix_key` (novo) | Seed CPF → pix_key |

### Credenciais Inter usadas
```
INTER_CLIENT_ID     = 17f9d0c0-f17c-4f1b-a8ba-b97158e3d923
INTER_CLIENT_SECRET = be3547d0-0f1e-46d7-a503-d7dca4709077
INTER_CERT_PATH     = /app/credentials/inter/Inter_API_Certificado.crt
INTER_KEY_PATH      = /app/credentials/inter/Inter_API_Chave.key
INTER_ENV           = production
```

---

## PASSO 4 — ENDPOINTS

**Arquivo:** `backend/modules/people_management/employee_portal/controllers/dp_payslips_controller.py`
**Prefixo registrado:** `/api/v1/people-management/dp/payslips`

| Endpoint | Método | Função |
|----------|--------|--------|
| `/folha/pagar-via-pix/{mes}/{ano}/preview` | GET | Simula sem pagar |
| `/folha/pagar-via-pix/{mes}/{ano}` | POST | Executa PIX real |
| `/folha/pagar-via-pix/{mes}/{ano}/status` | GET | Status pagamentos |
| `/folha/funcionario/{employee_id}/pix-key` | PUT | Atualizar chave PIX |

---

## PASSO 5 — VALIDAÇÃO

### Teste via docker exec (service direto)
```json
{
  "mes": 3,
  "ano": 2026,
  "total_funcionarios": 46,
  "total_valor": 66677.59,
  "sem_chave_pix": [],
  "prontos_para_pagar": 46,
  "modo": "preview",
  "aviso": "Nenhum pagamento realizado"
}
```

### Amostra funcionários (3 primeiros)
```
ADAILSON SERRA ALVES        | CPF: 03527554238 | R$ 1.539,74
ADEMIR SALUSTIANO DE SOUZA  | CPF: 00480990239 | R$ 1.784,61
AILTON CESAR VASCONCELOS    | CPF: 73909629253 | R$ 1.787,91
```

### Registro em main_production.py
```
DP Payslips: OK (criar/publicar/importar contracheques)
```

---

## COMMIT

| Hash | Descrição |
|------|-----------|
| `ede97284` | `feat(dp/banking): pagamento folha via PIX Inter — lote 51 funcionários` |

**Push:** `origin/feature/people-management-reorganization` ✅

---

## PARA EXECUTAR O PAGAMENTO REAL

```bash
# 1. Preview (sem pagar)
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/people-management/dp/payslips/folha/pagar-via-pix/3/2026/preview"

# 2. Pagar (PIX reais Inter)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/people-management/dp/payslips/folha/pagar-via-pix/3/2026"

# 3. Status
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/people-management/dp/payslips/folha/pagar-via-pix/3/2026/status"
```
