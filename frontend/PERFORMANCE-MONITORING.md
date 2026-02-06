# Performance Monitoring - Conecta PRO

Documentação completa sobre monitoramento de performance, budgets e processos de CI/CD.

## Sumário

- [Visão Geral](#visão-geral)
- [Ferramentas](#ferramentas)
- [Performance Budgets](#performance-budgets)
- [Lighthouse CI](#lighthouse-ci)
- [Bundle Size Tracking](#bundle-size-tracking)
- [Scripts Disponíveis](#scripts-disponíveis)
- [CI/CD Integration](#cicd-integration)
- [Processo de Review](#processo-de-review)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

O sistema de monitoramento de performance do Conecta PRO garante que a aplicação mantenha altos padrões de performance através de:

- **Lighthouse CI**: Auditorias automatizadas de performance, acessibilidade e SEO
- **Bundle Size Tracking**: Monitoramento contínuo do tamanho do bundle
- **Performance Budgets**: Limites definidos para métricas críticas
- **CI/CD Integration**: Validação automática em pull requests

### Objetivos

- Performance Score: **≥ 80%**
- Accessibility Score: **≥ 90%**
- First Contentful Paint (FCP): **≤ 2s**
- Largest Contentful Paint (LCP): **≤ 3s**
- Total Blocking Time (TBT): **≤ 300ms**
- Cumulative Layout Shift (CLS): **≤ 0.1**
- Bundle Size Growth: **≤ 5%** por release

---

## Ferramentas

### 1. Lighthouse CI

Ferramenta oficial do Google para auditorias automatizadas de performance web.

**Configuração**: `lighthouserc.json`

**URLs Testadas**:
- Home (`/`)
- Dashboard (`/dashboard`)
- CRM Leads (`/crm/leads`)
- Financeiro Clientes (`/financeiro/clientes`)

**Métricas Avaliadas**:
- Performance
- Accessibility
- Best Practices
- SEO
- Core Web Vitals

### 2. Bundle Analyzer

Análise visual da composição do bundle JavaScript.

**Como usar**:
```bash
npm run analyze
```

Abre interface interativa mostrando:
- Tamanho de cada módulo
- Dependências importadas
- Oportunidades de otimização

### 3. Custom Scripts

Scripts Node.js customizados para análises específicas:

- **compare-bundle-size.js**: Compara tamanho atual com baseline
- **lighthouse-report.js**: Gera relatórios formatados do Lighthouse

---

## Performance Budgets

Definidos em `performance-budgets.json`.

### Budgets por Rota

| Rota | Script Budget | CSS Budget | Total Budget |
|------|---------------|------------|--------------|
| `/_app` | 200 KB | 50 KB | 300 KB |
| `/dashboard` | 350 KB | 70 KB | 500 KB |
| `/crm/**` | 300 KB | - | 400 KB |
| `/financeiro/**` | 300 KB | - | 400 KB |
| Chunks | 150 KB | - | 150 KB |

### Timings Budget

| Métrica | Budget |
|---------|--------|
| FCP | 2000ms |
| LCP | 3000ms |
| TTI | 4000ms |
| CLS | 0.1 |
| TBT | 300ms |

### Quando os Budgets São Violados

1. **Em desenvolvimento**: Warning no console
2. **Em PRs**: Comentário automático com detalhes
3. **Em CI**: Build falha se ultrapassar 5% do baseline

---

## Lighthouse CI

### Executar Localmente

```bash
# Executar apenas Lighthouse
npm run lighthouse

# Executar e gerar relatório formatado
npm run lighthouse:report

# Executar tudo (build + lighthouse + report)
npm run perf:test
```

### Interpretar Resultados

#### Scores

- **90-100**: 🟢 Excelente
- **50-89**: 🟡 Precisa melhorias
- **0-49**: 🔴 Crítico

#### Core Web Vitals

**FCP (First Contentful Paint)**
- Tempo até o primeiro conteúdo ser renderizado
- ✅ Bom: < 1.8s
- ⚠️ Precisa melhorias: 1.8s - 3s
- ❌ Ruim: > 3s

**LCP (Largest Contentful Paint)**
- Tempo até o maior elemento ser renderizado
- ✅ Bom: < 2.5s
- ⚠️ Precisa melhorias: 2.5s - 4s
- ❌ Ruim: > 4s

**TBT (Total Blocking Time)**
- Tempo total em que a thread principal está bloqueada
- ✅ Bom: < 200ms
- ⚠️ Precisa melhorias: 200ms - 600ms
- ❌ Ruim: > 600ms

**CLS (Cumulative Layout Shift)**
- Quantidade de mudanças inesperadas no layout
- ✅ Bom: < 0.1
- ⚠️ Precisa melhorias: 0.1 - 0.25
- ❌ Ruim: > 0.25

### Arquivos Gerados

```
.lighthouseci/
├── lhr-*.json          # Relatórios completos
├── manifest.json       # Manifesto dos runs
└── summary.json        # Resumo agregado
```

---

## Bundle Size Tracking

### Executar Análise

```bash
# Comparar com baseline
npm run perf:compare

# Atualizar baseline (após otimizações aprovadas)
npm run perf:baseline

# Executar análise completa
npm run perf:all
```

### Entender o Output

```
📊 ANÁLISE DE BUNDLE SIZE
══════════════════════════════════════════════════════════════════════

⚠️  Total          : 2.45 MB (+125 KB / +5.3%)
✅ Static Files   : 1.89 MB (-50 KB / -2.6%)
⚠️  JS Chunks      : 1.45 MB (+150 KB / +11.5%)
➡️  CSS            : 89 KB (+2 KB / +2.3%)
➡️  Media          : 345 KB (0 KB / 0%)
```

**Símbolos**:
- ⚠️  Cresceu mais que 5%
- ✅ Diminuiu mais que 5%
- ➡️  Mudança menor que 5%

### Baseline

O baseline é armazenado em `scripts/bundle-baseline.json` e representa o "estado aprovado" do bundle.

**Quando atualizar**:
- Após otimizações bem-sucedidas
- Após adicionar features essenciais
- Após aprovar crescimento intencional

**Não atualizar quando**:
- Bundle cresceu sem justificativa
- Testes ainda em andamento
- Otimizações pendentes

---

## Scripts Disponíveis

### Performance

```bash
# Análise visual do bundle
npm run analyze

# Lighthouse CI
npm run lighthouse

# Relatório Lighthouse formatado
npm run lighthouse:report

# Build + Lighthouse + Report
npm run perf:test

# Comparar bundle com baseline
npm run perf:compare

# Atualizar baseline
npm run perf:baseline

# Análise completa (build + bundle + lighthouse)
npm run perf:all
```

### Build e Deploy

```bash
# Build padrão
npm run build

# Build com análise
ANALYZE=true npm run build

# Build de produção
NODE_ENV=production npm run build
```

---

## CI/CD Integration

### Workflows Configurados

#### 1. Performance Check (`performance.yml`)

**Trigger**: Pull Requests para `main` ou `develop`

**Jobs**:
1. **Bundle Size Analysis**
   - Compara tamanho do bundle com baseline
   - Gera comentário no PR com comparação
   - Falha se crescimento > 5%

2. **Lighthouse CI**
   - Executa auditorias em múltiplas páginas
   - Gera relatório de scores
   - Comenta no PR com Core Web Vitals

3. **Performance Summary**
   - Agrega resultados
   - Disponibiliza artifacts

#### 2. Update Baseline (`performance-baseline.yml`)

**Trigger**: Push para `main`

**Job**:
- Atualiza baseline automaticamente após merge
- Commit o novo baseline no repositório

### Artifacts Gerados

Disponíveis por 30 dias:

1. **bundle-stats**: Análise detalhada do bundle
2. **lighthouse-results**: Relatórios completos do Lighthouse

### Secrets Necessários

```bash
# Opcional: Token para Lighthouse CI Server
LHCI_GITHUB_APP_TOKEN=xxx
```

---

## Processo de Review

### Checklist para Reviewers

Ao revisar um PR, verificar:

#### 1. Bundle Size

- [ ] Crescimento dentro do limite (5%)
- [ ] Crescimento justificado (nova feature, etc)
- [ ] Lazy loading aplicado quando apropriado
- [ ] Imports otimizados (tree-shaking)

#### 2. Lighthouse Scores

- [ ] Performance ≥ 80%
- [ ] Accessibility ≥ 90%
- [ ] Nenhum regression em métricas críticas
- [ ] Core Web Vitals dentro dos limites

#### 3. Code Quality

- [ ] Componentes grandes estão code-split
- [ ] Imagens otimizadas
- [ ] Fonts carregados eficientemente
- [ ] Sem blocking resources

### Quando Aprovar com Ressalvas

Casos onde crescimento é aceitável:

- Nova feature essencial
- Dependência crítica
- Melhoria de UX que justifica o tamanho
- Crescimento compensado por melhorias futuras

**Importante**: Documentar a justificativa no PR.

### Quando Rejeitar

Rejeitar se:

- Crescimento > 10% sem justificativa clara
- Performance score caiu significativamente
- Accessibility score abaixo do threshold
- Otimizações óbvias não foram aplicadas

---

## Troubleshooting

### Lighthouse CI Falha Localmente

**Problema**: Servidor não inicia

**Solução**:
```bash
# Verificar se porta 3000 está livre
lsof -ti:3000 | xargs kill -9

# Build primeiro
npm run build

# Executar lighthouse
npm run lighthouse
```

### Bundle Size Cresceu Inesperadamente

**Investigar**:

1. **Verificar imports**:
   ```bash
   npm run analyze
   ```
   Procurar por módulos grandes não utilizados.

2. **Verificar dependências novas**:
   ```bash
   git diff package.json
   ```

3. **Revisar code-splitting**:
   - Componentes grandes devem ser lazy loaded
   - Rotas devem ser automaticamente split

**Soluções comuns**:
- Usar dynamic imports
- Otimizar imports (ex: Lucide icons)
- Remover dependências não utilizadas
- Usar bibliotecas mais leves

### Performance Score Baixo

**Diagnosticar**:

```bash
npm run lighthouse:report
```

**Problemas comuns e soluções**:

| Problema | Causa | Solução |
|----------|-------|---------|
| FCP alto | Renderização bloqueada | Lazy load, critical CSS |
| LCP alto | Imagem pesada | Otimizar imagens, usar Next Image |
| TBT alto | JavaScript pesado | Code splitting, Web Workers |
| CLS alto | Elementos sem dimensões | Definir width/height |

### CI Falhando mas Local OK

**Possíveis causas**:

1. **Baseline desatualizado**:
   ```bash
   git pull origin main
   npm run perf:baseline
   git push
   ```

2. **Cache do CI**:
   - Limpar cache do GitHub Actions
   - Re-run workflow

3. **Dependências diferentes**:
   ```bash
   # No CI sempre usa npm ci (lock file)
   rm -rf node_modules package-lock.json
   npm install
   ```

### Memory Issues durante Build

**Problema**: Build falha com "JavaScript heap out of memory"

**Solução**:
```json
{
  "scripts": {
    "build": "NODE_OPTIONS='--max-old-space-size=4096' next build"
  }
}
```

---

## Melhores Práticas

### Development

1. **Execute análises regularmente**:
   ```bash
   # Semanalmente ou após grandes mudanças
   npm run perf:all
   ```

2. **Monitore durante desenvolvimento**:
   ```bash
   # Next.js mostra tamanhos na build
   npm run build
   ```

3. **Use análise visual**:
   ```bash
   npm run analyze
   ```

### Code Reviews

1. **Sempre verificar comentário do bot** no PR
2. **Questionar crescimentos > 3%**
3. **Aprovar baseline updates** apenas após validação

### Otimização

1. **Code-split agressivamente**:
   - Usar dynamic imports
   - Lazy load componentes pesados
   - Split por rota automaticamente

2. **Otimizar dependências**:
   - Preferir bibliotecas leves
   - Usar tree-shaking
   - Importar apenas o necessário

3. **Otimizar assets**:
   - Comprimir imagens (WebP, AVIF)
   - Usar Next Image
   - Lazy load imagens below-the-fold

4. **Monitorar terceiros**:
   - Limitar scripts externos
   - Usar Partytown para web workers
   - Self-host quando possível

---

## Recursos Adicionais

### Documentação

- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)
- [Web Vitals](https://web.dev/vitals/)
- [Next.js Performance](https://nextjs.org/docs/advanced-features/measuring-performance)

### Ferramentas Online

- [PageSpeed Insights](https://pagespeed.web.dev/)
- [WebPageTest](https://www.webpagetest.org/)
- [Lighthouse Scoring Calculator](https://googlechrome.github.io/lighthouse/scorecalc/)

### Comandos Úteis

```bash
# Análise rápida de bundle
npm run build && ls -lh .next/static/chunks/*.js

# Verificar tamanho de dependências
npx cost-of-modules

# Analisar package.json
npx depcheck

# Verificar duplicatas
npx find-duplicate-files .next/static
```

---

## Changelog

### v2.0.0 - 2026-02-02

- Setup inicial de monitoring
- Lighthouse CI configurado
- Bundle size tracking implementado
- GitHub Actions workflows criados
- Performance budgets definidos
- Documentação completa

---

## Contato

Dúvidas ou sugestões sobre performance monitoring:

- Abrir issue no repositório
- Contatar time de DevOps
- Consultar documentação do Next.js

---

**Última atualização**: 2026-02-02
**Versão**: 2.0.0
**Mantido por**: Equipe Conecta PRO
