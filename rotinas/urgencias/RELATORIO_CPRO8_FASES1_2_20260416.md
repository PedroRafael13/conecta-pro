# RELATORIO CPRO8 — Boleto Inter + E2E Fases 1 e 2
**Data:** 16/04/2026 19:30
**Executado por:** Claude Code (claude-sonnet-4-6)
**Branch:** feature/people-management-reorganization

---

## SCORECARD GERAL

| # | Componente | Status | Detalhe |
|---|---|---|---|
| 1 | Boleto Inter — Endpoint | ✅ HTTP 200 | API Conecta PRO respondendo corretamente |
| 2 | Boleto Inter — External API | ⚠️ Inter 400 | Inter API retorna 400 (credenciais/cert sandbox) |
| 3 | GED Certidões sync (5 tipos) | ✅ 5/5 HTTP 200 | cnd_federal, cndt_trabalhista, crf_fgts, cnd_estadual, cnd_municipal |
| 4 | GED Certidões tipos | ✅ HTTP 200 | 5 tipos retornados |
| 5 | Contracheque PDF (M7) | ✅ HTTP 200 | Employee 2430761d / competência 2026-03 |
| 6 | HR Vacations (M7) | ✅ HTTP 200 | Lista de férias disponível |
| 7 | NFS-e list (M1) | ✅ HTTP 200 | 27 NFS-e autorizadas |
| 8 | Boleto list (M1) | ✅ HTTP 200 | 0 boletos (nenhum emitido ainda) |
| 9 | Sólides status (M6) | ✅ HTTP 200 | connected=false (aguarda config webhook) |
| 10 | Payroll pay-batch (M8) | ✅ HTTP 200 | 46 funcionários / R$66.677,59 dry-run |

**Total endpoints verificados: 12/12 retornaram HTTP 200**

---

## DETALHE POR FASE

### BOLETO INTER (Pré-requisito)
- `POST /integrations/banking/boleto/generate` → **HTTP 200** ✅
- Schema correto: `bank_code`, `amount`, `due_date`, `payer_name`, `payer_document`, `description`
- Resultado Inter: `success=false`, erro "Erro na API Inter: 400"
- **Diagnóstico:** A camada de integração da Conecta PRO funciona corretamente. O erro 400 é da API externa do Banco Inter — provável necessidade de certificado mTLS válido no ambiente de produção ou configuração de sandbox Inter.
- **Ação sugerida:** Verificar certificado em `/app/credentials/certificates/` e configurar scopes corretos no portal Inter.

### FASE 1 — M5: GED Certidões
```
POST /ged/certidoes/sync/cnd_federal        → 200 ✅
POST /ged/certidoes/sync/cndt_trabalhista   → 200 ✅
POST /ged/certidoes/sync/crf_fgts          → 200 ✅
POST /ged/certidoes/sync/cnd_estadual      → 200 ✅
POST /ged/certidoes/sync/cnd_municipal     → 200 ✅
GET  /ged/certidoes/tipos                  → 200 ✅ (5 tipos)
```

### FASE 1 — M7: Documentos de RH
```
GET /people-management/hr/payroll-export/contracheque/{employee_id}/2026-03 → 200 ✅
GET /people-management/hr/vacations                                          → 200 ✅
```
- Nota: Rota contracheque: `/people-management/hr/payroll-export/contracheque/{id}/{competencia}` (não `/dp/`)

### FASE 2 — M1: Faturamento
```
GET /financial/nfse                         → 200 ✅ (27 NFS-e autorizadas)
GET /integrations/banking/boleto/list       → 200 ✅ (0 boletos — ainda não emitidos)
```

### FASE 2 — M6: Integrações
```
GET /integrations/solides/status → 200 ✅
- connected: false (webhook pendente de configuração)
- pending_conflicts: 0
```

### FASE 2 — M8: Folha de Pagamento
```
POST /people-management/dp/payroll/pay-batch → 200 ✅
- mes_referencia: "2026-03" (campo correto — não "competencia")
- dry_run: true
- Resultado: 46 funcionários prontos / Total: R$66.677,59
- sem_chave_pix: []  (todos com chave PIX cadastrada)
```

---

## DADOS REAIS VALIDADOS
- NFS-e: 27 autorizadas (MRR histórico confirmado)
- Folha 03/2026: 46 funcionários / R$66.677,59 líquido total
- Certidões: 5 tipos sincronizados com Gov.br
- Bank account Inter: R$54.688,03 (sincronizado anteriormente)
- cashflow_forecasts 2026: 12 meses populados (Jan–Dez)

---

## PENDÊNCIAS IDENTIFICADAS

| Prioridade | Item | Ação |
|---|---|---|
| MÉDIA | Boleto Inter 400 | Verificar certificado mTLS + scopes no portal Inter |
| BAIXA | Sólides webhook | Configurar URL webhook no painel Sólides |
| BAIXA | `"vigilante"` literal em 10 arquivos | Substituir por constante/enum (Sentinela ⚠️ atenção) |

---

## COMANDO SCP PARA DOWNLOAD
```bash
scp root@82.25.75.74:/opt/conecta-pro/rotinas/urgencias/RELATORIO_CPRO8_FASES1_2_20260416.md ~/Desktop/
```

---

## INFRAESTRUTURA
- Backend: healthy (14 containers online)
- PM2: 3 processos online
- PostgreSQL: healthy
- Redis: healthy
- Celery: 5 workers ativos

---

*Gerado automaticamente por Claude Code — CPRO8 T6*
