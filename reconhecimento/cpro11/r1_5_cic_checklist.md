# CIC E2E Checklist — Rodada 1.5 Validação Final
**Data:** 2026-04-21
**Branch:** feature/people-management-reorganization
**Versão contrato:** v1.6
**Executor:** Jordan Jesus

---

## Preparação
1. Hard-refresh no navegador (Ctrl+Shift+Del → Cached images)
2. DevTools aberto em Console + Network
3. Logar como jjesus@conectamais.pro

---

## 16 Checks — cada um deve ser ✅

### Dashboard (/modulos/crm)
- [ ] 1. KPI Clientes = 11 (não 0, não 3)
- [ ] 2. KPI Win Rate > 0 (ou evidência clara de "sem dados")
- [ ] 3. KPI MRR R$ 272.086,96 (ou valor formatado não-NaN)
- [ ] 4. % conversão > 0 (esperado ~90.9%)

### Clientes (/modulos/crm/clientes)
- [ ] 5. Total Clientes = 11
- [ ] 6. Condomínios = 11 (ou 10)
- [ ] 7. Coluna Nome preenchida em TODAS as 11 rows
- [ ] 8. Coluna Tipo mostra "Condomínio" (label PT-BR)

### Cliente detalhe (/modulos/crm/clientes/[id])
- [ ] 9. Abrir qualquer row → sem "Algo deu errado"
- [ ] 10. Console SEM React error #31

### Leads (/modulos/crm/leads)
- [ ] 11. Status variados (Convertido, Novo, Qualificado) — NÃO todos "Novo"
- [ ] 12. Origem com labels reais — NÃO "-"

### Oportunidades Modal "Nova Oportunidade"
- [ ] 13. Select Stage com 6 opções incluindo "Análise de necessidades"
- [ ] 14. Campo Cliente é DROPDOWN (não input de texto)
- [ ] 15. Campo Responsável é DROPDOWN

### Contratos (/modulos/crm/contratos)
- [ ] 16. MRR = R$ 272.086,96 (não NaN, não R$0)

---

## Resultado (preencher após execução)

| # | Check | Resultado | Evidência |
|---|-------|-----------|-----------|
| 1 | KPI Clientes = 11 | ⬜ | |
| 2 | Win Rate > 0 | ⬜ | |
| 3 | MRR formatado não-NaN | ⬜ | |
| 4 | % conversão > 0 | ⬜ | |
| 5 | Total Clientes = 11 | ⬜ | |
| 6 | Condomínios = 11 | ⬜ | |
| 7 | Coluna Nome preenchida | ⬜ | |
| 8 | Coluna Tipo PT-BR | ⬜ | |
| 9 | Sem "Algo deu errado" | ⬜ | |
| 10 | Console sem React #31 | ⬜ | |
| 11 | Status variados (não todos "Novo") | ⬜ | |
| 12 | Origem com labels reais | ⬜ | |
| 13 | Stage dropdown 6 opções | ⬜ | |
| 14 | Campo Cliente é dropdown | ⬜ | |
| 15 | Campo Responsável é dropdown | ⬜ | |
| 16 | MRR contratos não-NaN | ⬜ | |

**RESULTADO FINAL:** ___/16 — LIBERAR / RETER
