# CIC E2E — Rodada 2 BrasilAPI
**Data:** 2026-04-22 — Aguardando validação browser por Opus/Jordan
**Hard-refresh obrigatório:** Ctrl+Shift+R em https://erp.conectamais.pro/

---

## UC-03: Widget Taxas Dashboard (3 checks)
- [ ] 1. Dashboard CRM carrega sem erros em `/modulos/crm`
- [ ] 2. Widget "Taxas do dia" aparece com Selic/CDI/IPCA valores numéricos (ex.: 14.75%)
- [ ] 3. Refresh: widget mostra badge "cached" (HIT no 2º load)

## UC-02: CEP AutoFill (3 checks)
- [ ] 4. Modal Novo Cliente → preencher CEP `69073488` → on blur autofila Manaus/AM
- [ ] 5. CEP inválido (`123`) não mostra erro barulhento — silencioso
- [ ] 6. CEP inexistente (`99999999`) mostra toast "CEP não encontrado"

## UC-01: Buscar CNPJ (5 checks)
- [ ] 7. Modal Novo Cliente → digitar CNPJ `35710481000103` → clicar "🔍 Buscar CNPJ"
- [ ] 8. Spinner visível durante request (~500ms)
- [ ] 9. Razão social autopreenchida: "CONECTAMAIS ELETRONICA LTDA" ou similar
- [ ] 10. Endereço autopreenchido com dados de Manaus/AM
- [ ] 11. CNPJ inválido (`123`) mostra erro "CNPJ deve ter 14 dígitos"

## Checks de regressão (R1.7)
- [ ] 12. Dashboard Clientes = 11
- [ ] 13. Modal Detalhes cliente: "Pequeno Porte" (não "small")
- [ ] 14. Leads: "Convertido" (não "converted")
- [ ] 15. Contratos: MRR R$ 272.086,96 (não NaN)
- [ ] 16. Contratos: coluna Cliente com nomes preenchidos

---

**GATE FASE 6:** ≥14/16 = LIBERAR | <14 = RETER
