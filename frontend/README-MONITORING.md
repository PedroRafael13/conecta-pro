# Performance Monitoring - README

Sistema completo de monitoramento de performance para Conecta PRO.

## Quick Start

```bash
# 1. Validar setup
npm run perf:validate

# 2. Criar baseline
npm run build
npm run perf:baseline

# 3. Executar análise
npm run perf:all
```

## Comandos

- `npm run analyze` - Bundle visual
- `npm run lighthouse` - Lighthouse CI
- `npm run perf:compare` - Comparar bundle
- `npm run perf:all` - Análise completa
- `npm run perf:validate` - Validar setup

## Documentação

- **Quick Start**: [PERFORMANCE-QUICKSTART.md](./PERFORMANCE-QUICKSTART.md)
- **Completa**: [PERFORMANCE-MONITORING.md](./PERFORMANCE-MONITORING.md)
- **Checklist**: [MONITORING-CHECKLIST.md](./MONITORING-CHECKLIST.md)
- **Índice**: [MONITORING-INDEX.md](./MONITORING-INDEX.md)

## Budgets

- Bundle growth: ≤ 5%
- Performance: ≥ 80%
- Accessibility: ≥ 90%
- FCP: ≤ 2000ms
- LCP: ≤ 3000ms

## CI/CD

Workflows configurados em `.github/workflows/`:
- `performance.yml` - PRs
- `performance-baseline.yml` - Main

## Suporte

Consulte [PERFORMANCE-MONITORING.md](./PERFORMANCE-MONITORING.md) seção Troubleshooting.

---

**Versão**: 2.0.0
