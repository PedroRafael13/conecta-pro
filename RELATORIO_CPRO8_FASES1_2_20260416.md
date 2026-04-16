# CPRO8 — Correções Fases 1 e 2
Data: 2026-04-16 19:50

## PLACAR FINAL — GEDEON FASES 1 E 2
╔══════════════════════════════════════════════════════╗
║       PLACAR FINAL — GEDEON FASES 1 E 2             ║
╠══════════════════════════════════════════════════════╣
║  Fase 1: 7/7 ✅                                      ║
║  Fase 2: 4/4 ✅                                      ║
║  Total:  11/11 ✅                                    ║
║  Aprovado para CIC T7: ✅ SIM — APTO PARA CIC T7   ║
╚══════════════════════════════════════════════════════╝

## Detalhes Fase 1 — M5 (Certidões)
- POST /ged/certidoes/sync/cnd_federal: 200 ✅
- POST /ged/certidoes/sync/cndt_trabalhista: 200 ✅
- POST /ged/certidoes/sync/crf_fgts: 200 ✅
- POST /ged/certidoes/sync/cnd_estadual: 200 ✅
- POST /ged/certidoes/sync/cnd_municipal: 200 ✅
- GET /ged/certidoes/tipos: 200 ✅ (não contada no placar, validação extra)

## Detalhes Fase 1 — M7 (RH)
- POST /people-management/hr/contracts/{id}/document (format:pdf): 201 ✅
  - Contract ID: 59577c1e-eeb1-4e20-a900-bcbbcbe50b00 (MALAQUIAS PEREIRA FERREIRA — CLT)
- GET /people-management/hr/vacations: 200 ✅

## Detalhes Fase 2 — M1 (Fiscal)
- GET /financial/nfse: 200 ✅ (27 NFS-e autorizadas)
- GET /integrations/banking/boleto/list: 200 ✅

## Detalhes Fase 2 — M6/M8
- GET /integrations/solides/status: 200 ✅
- POST /people-management/dp/payroll/pay-batch (dry_run): 200 ✅ (46 funcs / R$66.677,59)

## Boleto Inter
- POST /integrations/banking/boleto/generate: HTTP 200 ✅
- Inter API externa: retorna 400 (mTLS — certificado requer validação no portal Inter)

## Infraestrutura
- 14 containers healthy
- PM2: 3 processos online
- Branch: feature/people-management-reorganization
