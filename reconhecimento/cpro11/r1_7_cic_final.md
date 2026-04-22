# CIC E2E — Rodada 1.7 Validação Final
**Data:** 2026-04-21
**Branch:** feature/people-management-reorganization
**Versão contrato:** v1.8
**BUILD_ID:** `conecta-pro-1776814219707`

## Pré-requisito
Hard-refresh (Ctrl+Shift+R) em https://erp.conectamais.pro/

---

## 16 checks + sub-checks — comparar com r1_6_cic_final.md

### Dashboard (1-4)
- [ ] 1. Clientes = 11 ← manter R1.6
- [ ] 2. Win Rate > 0 ou sem dados (continua)
- [ ] 3. MRR formatado (não NaN)
- [ ] 4. Conversão sensata (< 1000%)

### Clientes (5-8)
- [ ] 5. Total = 11
- [ ] 6. Condomínios = **10** (pós D-1.7-7 frontend fix: RESIDENCIAL LARANJEIRAS VILLAGE agora conta)
- [ ] 7. Coluna Nome preenchida
- [ ] 8. Coluna Segmento badge PT-BR (Pequeno Porte, Grande Porte, Enterprise, etc.)

### Cliente detalhe (9-10)
- [ ] 9. Abre sem "Algo deu errado"
- [ ] 10. Modal Detalhes mostra **"Pequeno Porte"** em vez de "small" e **"Ativo"** em vez de "active" (D-1.7-3 ✅)
- [ ] 10b. Console sem React #31 (R1.6)

### Leads (11-12)
- [ ] 11. Status mostra **"Convertido"** em vez de "converted" (D-1.7-2 ✅)
- [ ] 12. Origem mostra **"Indicação"** em vez de "indicacao" (D-1.7-2 ✅)

### Modal Oportunidade (13-15)
- [ ] 13. 6 opções Stage PT-BR ← manter R1.6
- [ ] 14. Cliente dropdown ← manter R1.6
- [ ] 15. Responsável = input texto (D-1.7-6: /api/v1/users/ retorna 500 — documentado, não implementado)

### Contratos (16)
- [ ] 16. **MRR = R$ 270.586,96** (não NaN) (D-1.7-1 ✅)
- [ ] 16b. Coluna Cliente preenchida com nome real (D-1.7-4 ✅)
- [ ] 16c. Coluna Tipo = **"Recorrente"** (D-1.7-5 ✅)

---

## Fixes R1.7 que devem ser visíveis no CIC

| Débito | Fix | Evidência esperada |
|--------|-----|--------------------|
| D-1.7-1 MRR NaN | `Number(st?.total_monthly_revenue)` | R$ 270.586,96 (não NaN) |
| D-1.7-2 Leads labels | `converted` + `indicacao` adicionados ao map | "Convertido" / "Indicação" |
| D-1.7-3 Cliente modal | EN values adicionados ao segmentoConfig/statusConfig | "Pequeno Porte" / "Ativo" |
| D-1.7-4 Coluna Cliente | `clientMap[contract.client_id]?.name` | Nome real do condomínio |
| D-1.7-5 Coluna Tipo | `CONTRACT_TYPE_LABELS['recurring']` | "Recorrente" |
| D-1.7-6 Responsável | 500 no backend → NÃO implementado | Input texto mantido |
| D-1.7-7 Condomínios | Frontend filter + `crm_origin` check | Condomínios = 10 |
| D-1.7-8 React #418 | NÃO corrigido (fora de escopo) | Warning no console (não-bloqueante) |

---

## GATE FASE 5

Critério rigoroso (prompt R1.7):
- 16+/18 sub-checks = LIBERAR
- <16 = RETER com lista

**Validação pendente:** Opus ou Jordan via CIC browser.

Comando para download:
```
scp root@82.25.75.74:/opt/conecta-pro/reconhecimento/cpro11/r1_7_cic_final.md ~/Downloads/
```
