# T2 — Skills Injection: FinancialAdvisorAgent + CashflowPredictorAgent
**Data:** 2026-04-14
**Branch:** feature/people-management-reorganization
**Commit skills já em HEAD:** `6b0b116c` (feat(gedeon): Layer 2 Financial)

---

## Objetivo

Injetar skills do Grupo A dentro de `FinancialAdvisorAgent` e `CashflowPredictorAgent`
via `SkillLoader`, enriquecendo os system prompts com contexto especializado.

---

## Skills Injetadas

### FinancialAdvisorAgent
Arquivo: `backend/modules/financial/agents/financial_advisor.py`

```python
from modules.financial.agents.skill_loader import SkillLoader

class FinancialAdvisorAgent(BaseAgent):
    def _load_skills(self) -> str:
        return SkillLoader.load_multiple([
            "dre-gerencial",
            "kpis-financeiros",
            "analise-fluxo-caixa-real",
            "diagnostico-financeiro-completo",
        ])

    def _get_enriched_system_prompt(self, base_prompt: str = "") -> str:
        skills = self._load_skills()
        return f"""Você é o FinancialAdvisorAgent da Conecta Mais.
CNPJ: 35.710.481/0001-03 | Manaus/AM | Lucro Real desde jan/2026
...
SKILLS ESPECIALIZADAS:
{skills}
..."""
```

**Skills carregadas:** 20.756 chars ✅

### CashflowPredictorAgent
Arquivo: `backend/modules/financial/agents/cashflow_predictor.py`

```python
from modules.financial.agents.skill_loader import SkillLoader

class CashflowPredictorAgent(BaseAgent):
    def _load_skills(self) -> str:
        return SkillLoader.load_multiple([
            "projecao-fluxo-caixa-12-meses",
            "analise-fluxo-caixa-real",
            "metas-smart-financeiras",
        ])

    def _get_enriched_system_prompt(self, base_prompt: str = "") -> str:
        skills = self._load_skills()
        return f"""Você é o CashflowPredictorAgent da Conecta Mais.
ESTADO ATUAL DO CAIXA:
- Saldo Inter: R$36.476,27 (🔴 CRÍTICO — runway ~12 dias)
...
SKILLS DE PROJEÇÃO:
{skills}
..."""
```

**Skills carregadas:** 14.823 chars ✅

---

## SkillLoader

Arquivo: `backend/modules/financial/agents/skill_loader.py`

| Item | Valor |
|------|-------|
| Path primário | `/opt/conecta-pro/skills/financeiro` |
| Path fallback | `/tmp/skills/financeiro` (usado no container) |
| Skills disponíveis | **16 skills** |
| Método de cache | LRU (`functools.lru_cache`) |
| Resultado total | 35.579 chars de contexto especializado |

---

## Skills Disponíveis (16 arquivos)

| # | Nome |
|---|------|
| 01 | projecao-fluxo-caixa-12-meses |
| 02 | break-even |
| 03 | analise-margem |
| 04 | framework-precificacao |
| 05 | dre-gerencial |
| 06 | analise-fluxo-caixa-real |
| 07 | kpis-financeiros |
| 08 | gestao-inadimplencia |
| 09 | matriz-riscos |
| 10 | diagnostico-financeiro-completo |
| 11 | plano-acao-90-dias |
| 12 | planejamento-estrategico-anual |
| 13 | viabilidade-investimento |
| 14 | metas-smart-financeiras |
| 15 | benchmark-setorial |
| 16 | tributario-lucro-real |

---

## Validação

| Check | Resultado |
|-------|-----------|
| SkillLoader.load_multiple() — FinancialAdvisorAgent | **20.756 chars** ✅ |
| SkillLoader.load_multiple() — CashflowPredictorAgent | **14.823 chars** ✅ |
| SkillLoader.list_available() | **16 skills** ✅ |
| `/api/v1/financial/ai/advisor` | **200** ✅ |
| `/api/v1/financial/ai/cashflow` | **200** ✅ |
| `/api/v1/financial/ai/risk` | **200** ✅ |
| `/api/v1/financial/ai/billing` | **200** ✅ |
| `/api/v1/financial/ai/tax` | **200** ✅ |

---

## Observações

1. **Skills já estavam em HEAD** — O commit `6b0b116c` (feat(gedeon): Layer 2 Financial)
   já incluía a injeção de SkillLoader em ambos os agentes, feita pela sessão paralela
   do Gedeon Layer 2. A sessão T2 confirmou que o código está correto e funcionando.

2. **Container usa fallback path** — O container não tem permissão de escrita em
   `/opt/conecta-pro/`. As skills são servidas via `/tmp/skills/financeiro/`
   (fallback automático do SkillLoader).

3. **Agentes pendentes (T3)** — 7 agentes ainda não têm SkillLoader:
   - `base_agent.py`
   - `billing_automator.py`
   - `costing_analyzer.py`
   - `gedeon_financial_orchestrator.py`
   - `profitability_analyzer.py`
   - `risk_monitor.py`
   - `tax_calculator.py`

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_SKILLS_INJECTION_20260414.md ~/Downloads/RELATORIO_T2_SKILLS_INJECTION_20260414.md
```
