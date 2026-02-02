# Performance Monitoring - Checklist de Implementação

Checklist de validação para garantir que o monitoring está configurado corretamente.

## Setup Inicial

- [x] @lhci/cli instalado
- [x] @next/bundle-analyzer instalado
- [x] lighthouserc.json criado
- [x] performance-budgets.json criado
- [x] Scripts npm configurados

## Scripts Criados

- [x] scripts/compare-bundle-size.js
- [x] scripts/lighthouse-report.js
- [x] scripts/validate-monitoring-setup.js
- [x] Permissões de execução configuradas

## Configurações

- [x] Bundle Analyzer integrado no next.config.ts
- [x] optimizePackageImports configurado
- [x] .gitignore atualizado
- [x] .lighthouseci/ estrutura criada

## GitHub Actions

- [x] .github/workflows/performance.yml
- [x] .github/workflows/performance-baseline.yml
- [x] Jobs de bundle-size configurados
- [x] Jobs de lighthouse configurados
- [x] Comentários automáticos em PRs

## Performance Budgets

- [x] Bundle size budgets definidos
- [x] Core Web Vitals thresholds configurados
- [x] Lighthouse score thresholds definidos
- [x] Resource budgets configurados
- [x] Timings budgets configurados

## Documentação

- [x] PERFORMANCE-MONITORING.md (completo)
- [x] PERFORMANCE-QUICKSTART.md (quick start)
- [x] FASE4-MONITORING-REPORT.md (relatório)
- [x] MONITORING-CHECKLIST.md (este arquivo)

## Validação

- [x] npm run perf:validate executado
- [x] Todos os testes passaram
- [x] Sem erros ou warnings

## Testes Manuais

### Bundle Analysis
```bash
npm run build              # Build deve completar
npm run analyze            # Interface deve abrir
npm run perf:compare       # Deve mostrar análise
npm run perf:baseline      # Deve criar baseline
```

- [ ] Build completa sem erros
- [ ] Bundle analyzer abre interface
- [ ] compare-bundle-size gera relatório
- [ ] Baseline criado em scripts/bundle-baseline.json

### Lighthouse
```bash
npm run build              # Build primeiro
npm run lighthouse         # Executar auditorias
npm run lighthouse:report  # Gerar relatório
```

- [ ] Lighthouse executa sem erros
- [ ] Relatórios gerados em .lighthouseci/
- [ ] Summary.json criado
- [ ] Scores calculados corretamente

### Scripts Integrados
```bash
npm run perf:test          # Build + Lighthouse
npm run perf:all           # Análise completa
```

- [ ] perf:test executa sequencialmente
- [ ] perf:all executa bundle + lighthouse
- [ ] Sem erros em nenhum step

## CI/CD

### Pull Request Workflow

- [ ] Workflow trigger em PRs
- [ ] Bundle size job executa
- [ ] Lighthouse job executa
- [ ] Comentários aparecem no PR
- [ ] Artifacts são salvos

### Baseline Workflow

- [ ] Workflow trigger em push to main
- [ ] Baseline é atualizado
- [ ] Commit automático funciona

## Baseline Management

- [ ] Baseline inicial criado
- [ ] Baseline versionado no Git
- [ ] Update automático configurado
- [ ] Threshold de 5% validado

## Alertas e Notificações

- [ ] CI falha se bundle > 5%
- [ ] CI falha se performance < threshold
- [ ] Comentários informativos em PRs
- [ ] Issues identificados são listados

## Developer Experience

- [ ] Comandos são intuitivos
- [ ] Documentação é clara
- [ ] Troubleshooting está documentado
- [ ] Exemplos estão funcionando

## Segurança

- [ ] Relatórios não são commitados (.gitignore)
- [ ] Secrets não expostos em logs
- [ ] Artifacts têm retention apropriado
- [ ] Permissões de CI são mínimas

## Performance Targets

### Lighthouse Scores
- [ ] Performance: target ≥ 80%
- [ ] Accessibility: target ≥ 90%
- [ ] Best Practices: target ≥ 85%
- [ ] SEO: target ≥ 90%

### Core Web Vitals
- [ ] FCP: target ≤ 2000ms
- [ ] LCP: target ≤ 3000ms
- [ ] TTI: target ≤ 4000ms
- [ ] TBT: target ≤ 300ms
- [ ] CLS: target ≤ 0.1

### Bundle Size
- [ ] /_app: target ≤ 300 KB
- [ ] /dashboard: target ≤ 500 KB
- [ ] /crm: target ≤ 400 KB
- [ ] /financeiro: target ≤ 400 KB
- [ ] Chunks: target ≤ 150 KB

## Manutenção

- [ ] Processo de review documentado
- [ ] Baseline update process definido
- [ ] Escalation path documentado
- [ ] Responsáveis identificados

## Próximos Passos

### Imediato
- [ ] Executar primeiro build completo
- [ ] Criar baseline inicial
- [ ] Testar todos os scripts
- [ ] Validar CI workflows

### Curto Prazo
- [ ] Monitorar primeiros PRs
- [ ] Ajustar thresholds se necessário
- [ ] Treinar time
- [ ] Documentar casos especiais

### Médio Prazo
- [ ] Configurar Lighthouse CI Server (opcional)
- [ ] Integrar com dashboards
- [ ] Setup Real User Monitoring
- [ ] Automatizar relatórios periódicos

## Troubleshooting Checklist

Se algo não funcionar:

1. **Validar setup**:
   ```bash
   npm run perf:validate
   ```

2. **Verificar dependências**:
   ```bash
   npm list @lhci/cli @next/bundle-analyzer
   ```

3. **Limpar cache**:
   ```bash
   rm -rf .next .lighthouseci/*.json node_modules
   npm install
   ```

4. **Testar scripts individualmente**:
   ```bash
   node scripts/compare-bundle-size.js
   node scripts/lighthouse-report.js
   node scripts/validate-monitoring-setup.js
   ```

5. **Consultar documentação**:
   - PERFORMANCE-MONITORING.md (seção Troubleshooting)
   - PERFORMANCE-QUICKSTART.md (Problemas Comuns)

## Status Final

**Data de Validação**: _____________________

**Validado por**: _____________________

**Status**:
- [ ] Tudo funcionando
- [ ] Problemas identificados (listar abaixo)
- [ ] Requer ajustes

**Notas**:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

---

**Última atualização**: 2026-02-02
**Versão**: 2.0.0
