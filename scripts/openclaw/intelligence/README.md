# OpenClaw Intelligence - FASE 3

Módulo de inteligência artificial e automação para OpenClaw.

## 📚 Módulos

### 1. TrendAnalyzer
Análise de tendências baseada em histórico de relatórios.

**Funcionalidades:**
- Carrega relatórios dos últimos N dias
- Calcula tendência do Health Score (improving/declining/stable)
- Identifica checks que falham recorrentemente
- Detecta degradação de performance
- Gera insights e recomendações
- Sumário em linguagem natural (com suporte opcional a LLM)

**Exemplo de Uso:**
```python
from intelligence.trend_analyzer import TrendAnalyzer

analyzer = TrendAnalyzer(reports_dir=Path("/opt/conecta-pro/reports/openclaw"))
reports = analyzer.load_reports(days=30)
insights = analyzer.generate_insights(reports)
summary = analyzer.generate_ai_summary(insights)

print(summary)
```

**CLI:**
```bash
python3 scripts/openclaw/runner.py --analyze-trends
```

### 2. AutoHealer
Correções automáticas de problemas comuns.

**Checks Suportados:**

| Check | Auto-Fix | Descrição |
|-------|----------|-----------|
| Dependency Audit (Frontend) | ✅ Parcial | `npm audit fix` (apenas safe fixes) |
| Dependency Audit (Backend) | ❌ Manual | pip-audit não suporta auto-fix |
| Docker Status | ✅ Sim | Reinicia containers unhealthy |
| Backend Lint | ✅ Sim | `ruff format` + `ruff check --fix` |
| Frontend Lint | ✅ Sim | `npm run lint:fix` (eslint) |
| Disk Space | ✅ Sim | `docker system prune`, limpa caches |

**Exemplo de Uso:**
```python
from intelligence.auto_healer import AutoHealer

healer = AutoHealer(
    project_root=Path("/opt/conecta-pro"),
    dry_run=False,
    auto_fix_enabled=True
)

# Verificar se pode corrigir
if healer.can_fix("Docker Status", check_details):
    result = healer.heal("Docker Status", check_details)
    print(result)

# Ou processar relatório completo
results = healer.heal_report(openclaw_report)
```

**CLI:**
```bash
# Dry-run (simula sem executar)
python3 scripts/openclaw/runner.py --auto-heal --dry-run

# Executar correções reais
python3 scripts/openclaw/runner.py --auto-heal

# Combinar com checks específicos
python3 scripts/openclaw/runner.py --only health --auto-heal
```

## 📊 Análise de Tendências

### Métricas Calculadas

**Health Score Trend:**
- Compara média recente vs anterior
- Classifica: improving (📈), declining (📉), stable (➡️)
- Range: min, max, média

**Recurring Failures:**
- Identifica checks com failure rate > 20%
- Ranqueados por frequência de falhas
- Estatísticas detalhadas (passes/fails/errors/warnings)

**Performance Degradation:**
- Compara duração média recente vs anterior
- Alerta se degradação > 20%
- Recomenda otimizações

### Exemplo de Output

```
======================================================================
  ANÁLISE DE TENDÊNCIAS - OpenClaw Intelligence
======================================================================

📊 **Análise de 10 ciclos** (30 dias)

**Health Score**: 📉 Health score em declínio. Atual: 38/100 vs Média: 45.5/100
- Atual: 38/100
- Média: 45.5/100
- Range: 0-85/100

**Checks Problemáticos**:
- Backend Tests: 85.0% falhas (17/20 runs)
- Frontend Lint: 75.0% falhas (15/20 runs)
- Dependency Audit (Frontend): 100.0% falhas (20/20 runs)

**Performance**: ⚠️ Performance degradou 56.2%: 210.5s vs 134.8s

**Recomendações**:
- 🔴 Check 'Dependency Audit (Frontend)' falha 100.0% do tempo. Investigar causa raiz.
- 🐌 Performance degradou 56.2%. Considerar otimizações ou aumentar timeouts.

======================================================================
```

## 🔄 Auto-Healing

### Estratégias de Correção

#### NPM Vulnerabilities
```bash
npm audit fix  # Safe fixes apenas
```
- ✅ Aplica fixes seguros automaticamente
- ❌ Não usa --force (muito arriscado)
- 💡 Recomenda revisão manual para critical

#### Docker Unhealthy Containers
```bash
docker restart <container_name>
```
- ✅ Reinicia containers unhealthy
- 📋 Lista containers afetados
- 💡 Recomenda verificar logs após

#### Linting Issues
```bash
# Backend
ruff format .
ruff check --fix .

# Frontend
npm run lint:fix
```
- ✅ Aplica formatação automática
- ✅ Corrige issues auto-fixable
- 💡 Recomenda revisar com git diff

#### Disk Space
```bash
docker system prune -af --volumes
rm -rf frontend/.next frontend/node_modules/.cache
find . -type d -name __pycache__ -exec rm -rf {} +
```
- ✅ Limpa recursos Docker não usados
- ✅ Remove caches de build
- ✅ Limpa Python __pycache__

### Modo Dry-Run

Simula todas as ações sem executar:
```bash
python3 scripts/openclaw/runner.py --auto-heal --dry-run
```

Output:
```
[DRY RUN MODE] Simulando correções...
[DRY RUN] Executaria: docker restart conecta-pro-celery-beat
```

## 🎯 Integração com Bartolo

O módulo intelligence pode ser usado via chat:

```
@bartolo analisar tendências openclaw

@bartolo corrigir problemas openclaw (dry-run)

@bartolo executar auto-healing openclaw
```

## 📈 Insights JSON

O `--analyze-trends` salva insights em JSON:

```json
{
  "analysis_period_days": 30,
  "total_reports_analyzed": 20,
  "health_trend": {
    "trend": "declining",
    "trend_emoji": "📉",
    "current_score": 38,
    "average_score": 45.5,
    "min_score": 0,
    "max_score": 85
  },
  "recurring_failures": [
    {
      "name": "Backend Tests",
      "total_runs": 20,
      "failures": 15,
      "errors": 2,
      "warnings": 0,
      "passes": 3,
      "failure_rate": 85.0
    }
  ],
  "performance_analysis": {
    "degradation": true,
    "degradation_percentage": 56.2,
    "recent_avg_duration": 210.5,
    "older_avg_duration": 134.8
  },
  "recommendations": [
    "⚠️ URGENTE: Health score em declínio. Revisar checks falhando.",
    "🔴 Check 'Backend Tests' falha 85.0% do tempo. Investigar causa raiz.",
    "🐌 Performance degradou 56.2%. Considerar otimizações."
  ]
}
```

## 🚀 Roadmap

### Futuras Melhorias
- [ ] Integração com LLM (GPT-4, Claude) para análises mais sofisticadas
- [ ] Predição de falhas usando ML
- [ ] Auto-scaling de timeouts baseado em histórico
- [ ] Notificações proativas antes de falhas
- [ ] Dashboard web interativo com gráficos
- [ ] Exportação para Prometheus/Grafana
- [ ] Slack/Teams webhooks para healing reports

## 📝 Notas

- Auto-healing é **opt-in** (requer flag `--auto-heal`)
- Sempre use `--dry-run` primeiro para validar ações
- Revise mudanças com `git diff` antes de commitar
- Logs de healing ficam no log principal do runner
- Insights são salvos em `reports/openclaw/trends_*.json`

## 🔐 Segurança

- Nenhuma operação destrutiva sem confirmação
- Dry-run mode disponível para todas as operações
- Logs completos de todas as ações executadas
- Nenhum secret ou credencial exposto em logs

## 📄 Licença

Copyright © 2026 Conecta PRO Team. Todos os direitos reservados.
