# PROGRESSO D6 — T+0h (19:16 UTC)

**Branch:** feature/people-management-reorganization
**Início:** 2026-04-30 19:16 UTC

## Estado Base
- Saldo Inter: R$ 1.220,11 (mTLS funcionando ✅)
- `inter_transactions`: NÃO existe ❌
- `inter_cobrancas`: NÃO existe ❌
- `inter_pix_recebidos`: NÃO existe ❌
- `payroll_payments`: EXISTE (mas schema diferente — PIX-focused)
- `/financeiro/banking/page.tsx`: EXISTE (básico)
- `InterAdapter`: EXISTE completo em `banking/adapters/inter.py`
- Redis token cache: NÃO implementado ❌

## O que JÁ EXISTE (não reconstruir)
- `InterAdapter` com OAuth2 + mTLS completo
- `GET /api/v1/integrations/banking/balances` → saldo ✅
- `GET /api/v1/integrations/banking/statement` → extrato ✅
- `POST /api/v1/integrations/banking/boleto/generate` → emissão boleto ✅
- `POST /api/v1/integrations/banking/pix/generate` → PIX charge ✅
- `GET /api/v1/integrations/banking/pix/received` → PIX recebidos ✅
- `folha_payment_service.py` → pagamento salários via PIX ✅
- `banking/page.tsx` → UI básica ✅

## O que FALTA (D6)
- D6.0: Redis cache token Inter (InterAdapter.authenticate)
- D6.1: `inter_transactions` table + migration + InterSyncService + endpoints
- D6.2: `inter_conciliacao_folha` table + ConciliacaoService (NÃO usar payroll_payments existente)
- D6.3: `inter_cobrancas` table + migration + persist boletos
- D6.4: `inter_pix_recebidos` table + UI consolidada `/financeiro/inter/`

## Próximo passo
→ D6.0: patch Redis cache em InterAdapter
→ D6.1: migration inter_transactions + InterSyncService
