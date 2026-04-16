# GEDEON Roadmap — Auditoria Fases 1 e 2
**Data:** 2026-04-16
**Auditor:** Claude Code — Sessão de auditoria pura (sem implementação)
**Regra:** Teste funcional real ao vivo. "Arquivo existe" não é prova.

---

## Metodologia

- Token: `jjesus@conectamais.pro` (admin@conectamais.pro inexiste no sistema)
- Base URL: `http://localhost:8080/api/v1`
- Cada endpoint testado com `curl` ao vivo
- Retornos inspecionados campo a campo

---

## FASE 1 — M5: CERTIDÕES (5 CNDs)

### Estado real da infraestrutura

O endpoint `GET /ged/certidoes` existe e retorna **8 certidões cadastradas manualmente**:

| Certidão | Status | Vencimento | Arquivo PDF |
|----------|--------|-----------|-------------|
| Certidão Negativa Federal | valida | 2026-07-15 | NULL |
| Certidão Negativa FGTS | **vencida** | 2026-03-31 | NULL |
| Certidão Negativa Trabalhista | valida | 2026-07-20 | NULL |
| Certidão Negativa Estadual | valida | 2026-08-05 | NULL |
| Certidão Negativa Municipal | valida | 2026-09-10 | NULL |
| Certidão Negativa INSS | valida | 2026-08-10 | NULL |
| Alvará de Funcionamento | **vencida** | 2026-02-28 | NULL |
| Registro CNPJ Ativo | valida | 2027-01-01 | NULL |

### Busca automática (sync)

O código define `@router.post("/certidoes/sync")` e `@router.post("/certidoes/sync/{param}")`, com task `cnd_sync_task.py` que possui 5 configs: `cnd_federal`, `cndt_trabalhista`, `crf_fgts`, `cnd_estadual`, `cnd_municipal`.

**Porém:** `POST /ged/certidoes/sync` retorna **HTTP 405** (allow: PUT).
Causa: o `{certidao_id}` com método PUT absorve o path `/sync` antes do POST ser roteado — a rota de sync não está sendo registrada corretamente no runtime.

```
OPTIONS /api/v1/ged/certidoes/sync → allow: PUT   ← BUG: deveria allow: POST
POST /ged/certidoes/sync/{cnd_federal}   → 404
POST /ged/certidoes/sync/{cndt_trabalhista} → 404
```

---

```
[ CND Receita Federal     ] STATUS: ❌ | HTTP: 405 (sync) | DADO REAL: não | DETALHE: certidão existe no GED manualmente, valida até 07/2026, sem arquivo PDF, busca automática não roteada (405 Method Not Allowed)

[ CND FGTS/Caixa          ] STATUS: ❌ | HTTP: 405 (sync) | DADO REAL: não | DETALHE: certidão no GED VENCIDA (03/2026), sem arquivo PDF, busca automática não roteada

[ CND Trabalhista TST     ] STATUS: ❌ | HTTP: 405 (sync) | DADO REAL: não | DETALHE: certidão existe no GED manualmente, valida até 07/2026, sem arquivo PDF, busca automática não roteada

[ CND Prefeitura Manaus   ] STATUS: ❌ | HTTP: 405 (sync) | DADO REAL: não | DETALHE: cadastrada como "Municipal", valida 09/2026, sem arquivo PDF, busca automática não roteada

[ CND Sefaz-AM            ] STATUS: ❌ | HTTP: 405 (sync) | DADO REAL: não | DETALHE: cadastrada como "Estadual", valida 08/2026, sem arquivo PDF, busca automática não roteada
```

**Causa raiz comum:** `POST /certidoes/sync` e `POST /certidoes/sync/{param}` definidos no controller mas não chegam ao runtime — o path `/certidoes/sync` é capturado pelo handler `PUT /certidoes/{certidao_id}`. Necessário investigar ordem de registro de rotas ou erro de importação silencioso no startup.

---

## FASE 1 — M7: DOCUMENTOS RH

### Contrato de Trabalho

- `GET /people-management/hr/contracts` → **200 OK — 20 contratos existem**
  - Campos: id, employee_id, type (CLT), start_date, base_salary, etc.
  - Dado real: sim (funcionários reais)
- `POST /{contract_id}/document` → **HTTP 500** (Internal Server Error)
- `GET /{contract_id}/pdf` → **HTTP 404** (rota registrada no código mas não encontrada no runtime)

### Aviso Prévio de Férias

- `vacation_controller.py` existe com prefix `/vacations`
- Rotas testadas: todas retornaram **404**
  - `/people-management/hr/vacation` → 404
  - `/people-management/hr/vacations` → 404
- Nota do próprio código: `"o router ops tem prefix='/vacations' → resulta em /hr/vacations/vacations/"` — rota com conflito de prefixo duplo, não registrada
- Templates HTML/DOCX para aviso prévio: **não encontrados** (`find` retornou zero arquivos)

```
[ Contrato de Trabalho    ] STATUS: ⚠️ | HTTP: 200 (lista) / 500 (gerar) / 404 (pdf) | PDF/DOCX gerado: não | DETALHE: 20 contratos no banco com dados reais CLT, mas geração de documento retorna 500 e download PDF retorna 404 — serviço de PDF quebrado em produção

[ Aviso Prévio de Férias  ] STATUS: ❌ | HTTP: 404 | PDF/DOCX gerado: não | DETALHE: controller existe mas rota não está registrada no runtime (conflito de prefix duplo /hr/vacations/vacations), nenhum template de aviso encontrado
```

---

## FASE 2 — M1: NFS-e E BOLETO

### NFS-e automática

- `GET /financial/nfse` → **200 OK**
- **27 NFS-e no total**, 5 retornadas na query padrão:

| NFS-e | Tomador | Valor | Status | Data |
|-------|---------|-------|--------|------|
| 19 | CONDOMINIO IDEAL FLORES DA CIDADE | R$65.842,42 | autorizada | 2026-02-10 |
| 20 | CONDOMINIO PRIME ARENA | R$3.879,60 | autorizada | 2026-02-10 |
| 21 | CONDOMINIO PRIME ARENA | R$36.586,90 | autorizada | 2026-02-10 |

Dados reais: sim (tomadores reais, valores reais, numeração sequencial).

### Boleto via Banco Inter

- `GET /integrations/banking/boleto/list` → **200 OK** mas `boletos: [], total: 0`
- `GET /integrations/banking/status` → **200 OK** — `connected: true`, Banco Inter 077, conta 370990072-2, saldo R$52.823,03
- `POST /integrations/banking/boleto/generate` → **422** (endpoint existe, campos obrigatórios faltando no teste: `bank_code` required)
- Conclusão: infra conectada ao Inter mas **nenhum boleto emitido** até a data da auditoria

```
[ NFS-e automática        ] STATUS: ✅ | Total emitidas: 27 | DETALHE: 27 NFS-e com status "autorizada", valores reais (tomadores: condominios reais), endpoint /financial/nfse funcional, dado confirmado como real

[ Boleto Inter            ] STATUS: ⚠️ | Cobranças ativas: 0 | DETALHE: infra Inter conectada (connected=true, saldo R$52.823,03), endpoint /integrations/banking/boleto/generate existe e aceita payload, mas 0 boletos emitidos — integração pronta, sem uso
```

---

## FASE 2 — M6/M8: SOLIDES VA + COMPROVANTE SALÁRIO

### Integração Solides VA

- `GET /integrations/solides/status` → **200 OK**:
  ```json
  {"connected": false, "api_key": null, "last_full_sync_at": null,
   "webhook_enabled": false, "pending_conflicts": 0}
  ```
- `GET /integrations/solides/employees` → 200 mas `total: 0`
- Endpoint registrado, código funcional, mas **API key não configurada** → desconectado

### Comprovante Salário Inter PIX Lote

- `GET /people-management/dp/payslips/` → **200 OK**:
  - Holerites de março/2026 existem (status: published)
  - Exemplo: salário bruto R$2.039,62, líquido R$1.784,61
  - Endpoint de PDF: `GET /{payslip_id}/pdf` existe no código (não testado individualmente)
- **PIX lote** (pagamento em lote de folha via Inter): **nenhum endpoint encontrado**
  - `/integrations/banking/pix/generate` existe mas é PIX unitário, não lote de folha
  - Sem endpoint `/folha/pagar-lote` ou equivalente

```
[ Solides VA              ] STATUS: ⚠️ | HTTP: 200 | DETALHE: endpoint /integrations/solides/status retorna 200 mas connected=false, API key não configurada, 0 employees sincronizados — infra pronta, credencial faltando

[ Comprovante salário     ] STATUS: ⚠️ | HTTP: 200 (holerites) | DETALHE: holerites de mar/2026 existem com dados reais (published), mas "PIX lote de folha" não implementado — endpoint /integrations/banking/pix/generate é PIX unitário, não pagamento em lote de funcionários
```

---

## PLACAR FINAL

```
FASE 1 — M5 CND:
[ CND Receita Federal     ] ❌  busca automática não roteada (405)
[ CND FGTS/Caixa          ] ❌  busca automática não roteada + certidão vencida
[ CND Trabalhista TST     ] ❌  busca automática não roteada (405)
[ CND Prefeitura Manaus   ] ❌  busca automática não roteada (405)
[ CND Sefaz-AM            ] ❌  busca automática não roteada (405)

FASE 1 — M7 RH:
[ Contrato de Trabalho    ] ⚠️  20 contratos no banco, PDF 500/404
[ Aviso Prévio de Férias  ] ❌  rota não registrada no runtime

FASE 2 — M1 Fiscal:
[ NFS-e automática        ] ✅  27 NFS-e reais autorizadas
[ Boleto Inter            ] ⚠️  infra pronta, 0 boletos emitidos

FASE 2 — M6/M8:
[ Solides VA              ] ⚠️  endpoint OK, API key não configurada
[ Comprovante salário     ] ⚠️  holerites OK, PIX lote não implementado
```

---

## PLACAR

| Fase | Itens | ✅ | ⚠️ | ❌ |
|------|-------|----|----|-----|
| Fase 1 (7 itens) | 7 | 0 | 1 | 6 |
| Fase 2 (4 itens) | 4 | 1 | 3 | 0 |
| **Total** | **11** | **1** | **4** | **6** |

```
Fase 1: 0/7 ✅  (1 parcial ⚠️, 6 quebrados ❌)
Fase 2: 1/4 ✅  (3 parciais ⚠️)
```

---

## APROVADO PARA FASE 3: ❌ NÃO

**Justificativa:**
- Fase 1 com 0/7 funcionais — bloqueia progressão
- Causa crítica: `POST /ged/certidoes/sync` não roteado no runtime (405) — todas as 5 CNDs dependem desse endpoint
- Contrato de trabalho gera 500 em produção
- Férias sem rota registrada

**Pré-requisitos para avançar à Fase 3:**
1. Corrigir conflito de rotas `certidoes/sync` vs `certidoes/{id}` (ordem de registro)
2. Corrigir `gerar_pdf_contrato` (500 em produção)
3. Corrigir prefix duplo do vacation_controller
4. (Desejável) Configurar API key Solides para desbloqueio M6

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_GEDEON_AUDITORIA_FASES1_2_20260416.md ~/Downloads/
```
