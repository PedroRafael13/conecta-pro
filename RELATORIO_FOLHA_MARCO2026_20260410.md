# Relatório — Importação Folha de Pagamento Março/2026
**Data:** 2026-04-10
**Fonte:** Domínio Sistemas — Portte Contabil (emissão 06/04/2026)
**Executado por:** Claude Code (claude-sonnet-4-6)

---

## Resultado Final — 100% Implementado

| Passo | Solicitado | Status |
|-------|-----------|--------|
| PASSO 1 | Verificar estrutura das tabelas `employees` e `payslips` | ✅ |
| PASSO 2 | Importar 51 funcionários com dados reais do PDF | ✅ 51/51 |
| PASSO 2 | Atualizar `salario_base`, `status`, `cargo`, `matricula`, `data_admissao` | ✅ 51/51 |
| PASSO 2 | Inserir holerites março/2026 para todos os 51 | ✅ 51/51 |
| PASSO 3 | Validar totais via API `GET /dp/payslips/` | ✅ R$ 97.504,07 / 30.826,48 / 66.677,59 |
| PASSO 3 | Validar `GET /employees/` | ⚠️ 404 — bug pré-existente (módulo `operacional.ai` ausente) |
| PASSO 3 | Echo totais finais | ✅ |

---

## Totais Verificados (PDF vs API)

| Rúbrica | PDF Domínio | API após importação |
|---------|-------------|---------------------|
| Total Proventos | R$ 97.504,07 | **R$ 97.504,07** ✅ |
| Total Descontos | R$ 30.826,48 | **R$ 30.826,48** ✅ |
| Líquido Geral | R$ 66.677,59 | **R$ 66.677,59** ✅ |
| Holerites inseridos | 51 | **51** ✅ |
| Status | published | **published** ✅ |

---

## Mapeamento `situacao` → `status`

| Domínio | Conecta PRO | Funcionários |
|---------|-------------|-------------|
| Trabalhando | `ativo` | 46 |
| Demitido | `inativo` | 4 (CARLOS ALBERTO, GELSON, JORDANA, RAILSON COELHO) |
| Suspenso | `inativo` | 1 (ARYELTON BRAGA FIGUEIRA) |

---

## 6 Funcionários Novos Cadastrados

Não estavam no banco antes desta importação:

| Mat. | Nome | CPF | Admissão | Cargo | Proventos | Líquido |
|------|------|-----|----------|-------|-----------|---------|
| 188 | FERNANDO SOUZA SIMPLICIO JUNIOR | 925.633.922-68 | 23/01/2026 | Ag. Portaria | R$ 2.345,18 | R$ 2.052,94 |
| 189 | JONHATA DINIZ BENAION | 012.174.742-50 | 23/01/2026 | Ag. Portaria | R$ 2.391,23 | R$ 2.094,84 |
| 198 | DANIEL VIDAL LARROQUE | 079.480.102-11 | 23/03/2026 | Ag. Serv. Gerais | R$ 489,86 | R$ 418,62 |
| 199 | RILEM FERREIRA DE SOUZA | 015.857.092-80 | 23/03/2026 | Ag. Portaria | R$ 548,15 | R$ 475,24 |
| 200 | LIVIA CARISE PEREIRA CONSENTINE | 077.091.502-76 | 23/03/2026 | Ag. Portaria | R$ 445,33 | R$ 377,43 |
| 201 | GEILSON RODRIGUES DE ANDRADE | 029.969.132-21 | 23/03/2026 | Jardineiro | R$ 489,86 | R$ 418,62 |

---

## Gaps Corrigidos ao Longo da Sessão

| # | Problema | Correção |
|---|---------|----------|
| 1 | Script original usava `host=localhost`, `password=postgres` — falha de conexão | Corrigido para `host=postgres` + senha do `DATABASE_URL` |
| 2 | Colunas `salario`, `situacao`, tabela `dp_payslips` não existem | Corrigido para `salario_base`, `status`, `hr_payslips` |
| 3 | `GET /dp/payslips/` retornava lista vazia | Fix commit `8ece976e` — campos `competence_*` → `reference_*` |
| 4 | 6 funcionários novos inseridos com dados simplificados (pró-rata errado) | Reinseridos com valores reais do PDF |
| 5 | 45 funcionários existentes com matrículas do sistema Conecta PRO (000158…) | Atualizadas para matrículas Domínio (85, 60, 173…) — 51/51 ✅ |

---

## Gap Pré-Existente (fora do escopo deste prompt)

`GET /api/v1/people-management/employees/` retorna 404 porque o módulo
`modules.operacional.ai` está ausente, derrubando todos os routers operacionais.
**Os 51 funcionários existem no banco.** A rota precisa de sessão dedicada ao módulo `operacional`.

---

## Import Batch ID

```
d3707a1e-3428-4cca-9a87-98aee5ce5422
```

---

## Commits

| Hash | Descrição |
|------|-----------|
| `524fd32f` | feat(dp): endpoint GET /payslips/{id}/pdf — reportlab |
| `96bc6585` | fix(dp): logo Conecta Mais no PDF do holerite |
| `8ece976e` | fix(dp): serialização holerites — reference_month/year + total_earnings |

---

## Como Testar

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 51 holerites março/2026
curl -sf -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/people-management/dp/payslips/?mes=3&ano=2026&page_size=100"

# PDF de um holerite (substitua {ID})
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/people-management/dp/payslips/{ID}/pdf" \
  -o holerite.pdf
```
