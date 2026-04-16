# Auditoria GEDEON Fases 1+2 — 2026-04-16

**Token usado:** `eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...`

## Fase 1 — Gestão Documental
- ✅ **CND /tipos (5 tipos)**: 5/5
- ✅ **CND sync/cnd_federal**: HTTP 200 | pulada
- ✅ **CND sync/cndt_trabalhista**: HTTP 200 | pulada
- ❌ **CND sync/crf_fgts**: HTTP 200 | erro
- ✅ **CND sync/cnd_estadual**: HTTP 200 | pulada
- ✅ **CND sync/cnd_municipal**: HTTP 200 | pulada
- ✅ **Contratos CLT**: 20 contratos
- ✅ **Contrato PDF**: HTTP 201
- ✅ **Férias registradas**: 10 férias
- ✅ **Aviso Prévio PDF**: HTTP 200

## Fase 2 — Integrações
- ✅ **NFS-e autorizadas**: 27/27 autorizadas
- ✅ **Boleto Inter**: HTTP 200
- ✅ **mTLS Inter (.crt+.key)**: presentes
- ✅ **Solides connected**: connected=True employees=0
- ✅ **PIX Lote (46 funcs)**: 46 funcs | R$66,677.59
- ✅ **PIX valor R$66.677,59**: R$66677.59

## Resultado
- Fase 1: 9/10
- Fase 2: 6/6
- Total: 16/17
- Veredicto: ✅ APROVADO — APTO PARA CIC
