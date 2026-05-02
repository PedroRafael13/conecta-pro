# PROGRESSO D6 — T+2h

**Fase:** D6.2 concluída
**Timestamp:** 2026-04-30 T+2h

## ✅ Concluído nesta hora

### D6.2 — Conciliação de Folha
- `ConciliacaoService.preparar_competencia(competencia)` — cria registros `previsto` a partir de `hr_payslips`
- `ConciliacaoService.conciliar_folha(competencia)` — lógica FORTE/MÉDIO/FRACO/AMBÍGUO
  - FORTE: CPF + valor ≤ R$0,01 → `pago`
  - MÉDIO: CPF + valor ≤ R$0,50 → `pago`
  - FRACO: valor + nome em descrição → `pago`
  - AMBÍGUO: múltiplos funcionários na tolerância MÉDIO → `em_conciliacao`
- Endpoints: `POST /conciliacao/{competencia}/preparar`, `POST /conciliacao/{competencia}/conciliar`, `GET /conciliacao/{competencia}/pagamentos`, `GET /conciliacao/divergencias`
- Testes D6.2 (4/4): match_forte, match_medio, ambiguo_em_conciliacao, preparar_competencia_cria_registros

## 🐛 Bugs Corrigidos
- `::jsonb` sintaxe quebra asyncpg → fix: `cast(:pagador as jsonb)`
- `_parse_dt()` helper para string ISO 8601 `'2026-04-15T02:45:03.445Z'` → datetime

## 📊 Status
- Testes: 11/16 passando
- Tabela `inter_conciliacao_folha` separada de `payroll_payments` (incompatibilidade de schema, 46 registros existentes)
