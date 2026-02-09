# Guia de Execução de Testes - Conecta PRO

Este documento descreve como executar os testes do projeto Conecta PRO.

---

## 📋 Pré-requisitos

### Ambiente de Desenvolvimento

- **Node.js**: 20.x ou superior
- **npm**: 10.x ou superior
- **Git**: Para controle de versão

### Instalação de Dependências

```bash
# Clone o repositório (se necessário)
git clone <repositorio>
cd /opt/conecta-pro/frontend

# Instalar dependências
npm install

# Instalar browsers do Playwright
npx playwright install

# Instalar dependências adicionais (se necessário)
npx playwright install-deps
```

### Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# URL base da aplicação
NEXT_PUBLIC_API_URL=https://api.conecta.pro
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Credenciais de teste (para CI/CD)
TEST_USER_EMAIL=qa@conecta.pro
TEST_USER_PASSWORD=senha_segura_test

# Configurações do Playwright
PLAYWRIGHT_BASE_URL=http://localhost:3000
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_WORKERS=4
```

---

## 🎭 Testes E2E (Playwright)

### Execução Completa

```bash
# Executar todos os testes E2E
npx playwright test

# Executar com relatório HTML
npx playwright test --reporter=html
```

### Execução por Módulo

```bash
# Módulo CRM
npx playwright test e2e/crm/

# Módulo Operacional
npx playwright test e2e/operacional/

# Módulo Financeiro
npx playwright test e2e/financial-*.spec.ts

# Módulo de Equipamentos
npx playwright test e2e/equipamentos/

# Módulo de Integrações
npx playwright test e2e/integracoes/

# Módulo Analytics
npx playwright test e2e/analytics/

# Módulo de Recrutamento
npx playwright test e2e/recrutamento/

# Módulo de Configurações
npx playwright test e2e/configuracoes/
```

### Execução por Tag

```bash
# Apenas testes de autenticação
npx playwright test --grep "Auth"

# Testes de criação (CREATE)
npx playwright test --grep "deve cadastrar|deve criar"

# Testes de listagem (READ)
npx playwright test --grep "deve exibir|deve listar"

# Testes de edição (UPDATE)
npx playwright test --grep "deve editar|deve atualizar"

# Testes de exclusão (DELETE)
npx playwright test --grep "deve excluir|deve deletar"
```

### Modo Visual (UI)

```bash
# Abrir interface visual do Playwright
npx playwright test --ui

# Modo headed (mostrar navegador)
npx playwright test --headed

# Modo debug
npx playwright test --debug
```

### Execução Específica

```bash
# Executar arquivo específico
npx playwright test e2e/crm/clientes-list.spec.ts

# Executar teste específico por linha
npx playwright test e2e/crm/clientes-list.spec.ts:15

# Executar com worker único (sequencial)
npx playwright test --workers=1

# Executar em modo paralelo máximo
npx playwright test --workers=8
```

### Relatórios

```bash
# Relatório HTML
npx playwright test --reporter=html
npx playwright show-report

# Relatório JSON
npx playwright test --reporter=json --output=results.json

# Relatório JUnit (para CI/CD)
npx playwright test --reporter=junit --output=results.xml

# Múltiplos relatórios
npx playwright test --reporter=html,json,junit
```

---

## 🧪 Testes Unitários (Vitest)

### Execução Completa

```bash
# Executar todos os testes unitários
npm test

# Ou
npx vitest run
```

### Execução com Coverage

```bash
# Executar com relatório de cobertura
npm run test:coverage

# Ver relatório de cobertura
open coverage/index.html
```

### Modo Watch

```bash
# Modo watch (re-executa ao salvar)
npm run test:watch

# Ou
npx vitest
```

### Execução por Arquivo

```bash
# Executar arquivo específico
npm run test:run -- src/components/ui/__tests__/button.test.tsx

# Executar por padrão
npx vitest run src/components/ui/__tests__/

# Executar testes de hooks
npx vitest run src/hooks/__tests__/

# Executar testes de utilitários
npx vitest run src/lib/__tests__/
```

### Filtros

```bash
# Filtrar por nome
npx vitest run --testNamePattern="deve renderizar"

# Filtrar por arquivo
npx vitest run --testPathPattern="button"
```

---

## 🔧 Configurações Avançadas

### Configuração de Browsers

```bash
# Executar apenas no Chrome
npx playwright test --project=chromium

# Executar apenas no Firefox
npx playwright test --project=firefox

# Executar apenas no WebKit
npx playwright test --project=webkit

# Executar em todos os browsers
npx playwright test --project="all"
```

### Configuração de Viewport

```bash
# Testes em mobile
npx playwright test --project="Mobile Chrome"
npx playwright test --project="Mobile Safari"

# Testes em tablet
npx playwright test --project="Tablet Chrome"
```

### Retry e Timeouts

```bash
# Configurar retries (tentativas em caso de falha)
npx playwright test --retries=3

# Configurar timeout global
npx playwright test --timeout=60000

# Configurar timeout de expectativa
npx playwright test --expect-timeout=10000
```

---

## 🚀 CI/CD - GitHub Actions

### Executar Testes Localmente (simulando CI)

```bash
# Instalar dependências
npm ci

# Executar lint
npm run lint

# Executar build
npm run build

# Executar testes unitários
npm run test:run

# Executar testes E2E
npx playwright test
```

### Pipeline Completa

Veja `.github/workflows/tests.yml` para a configuração completa da pipeline.

**Etapas da Pipeline:**
1. ✅ Checkout do código
2. ✅ Setup do Node.js
3. ✅ Instalação de dependências
4. ✅ Lint e formatação
5. ✅ Build da aplicação
6. ✅ Testes unitários
7. ✅ Testes E2E
8. ✅ Upload de relatórios

---

## 📊 Análise de Resultados

### Interpretando Resultados

```bash
# Sucesso
✓ e2e/crm/clientes-list.spec.ts (14 testes)

# Falha
✗ e2e/crm/clientes-create.spec.ts:45:10 › deve cadastrar novo cliente

# Skip (ignorado)
⊘ e2e/financial/faturamento.spec.ts:23:5 › deve exportar relatório
```

### Debug de Falhas

```bash
# Executar modo debug
npx playwright test --debug

# Traçar execução
npx playwright test --trace=on

# Ver trace
npx playwright show-trace trace.zip

# Screenshot em caso de falha
npx playwright test --screenshot=only-on-failure

# Video em caso de falha
npx playwright test --video=retain-on-failure
```

### Artefatos de Teste

Após execução, os seguintes artefatos são gerados:

- `playwright-report/` - Relatório HTML
- `test-results/` - Screenshots, videos e traces
- `coverage/` - Relatório de cobertura

---

## 🐛 Troubleshooting

### Problemas Comuns

#### Erro: Browser não encontrado

```bash
# Reinstalar browsers
npx playwright install --with-deps
```

#### Erro: Timeout em testes

```bash
# Aumentar timeout
npx playwright test --timeout=120000
```

#### Erro: Porta em uso

```bash
# Matar processos na porta 3000
npx kill-port 3000

# Ou usar porta diferente
PORT=3001 npm run dev
```

#### Erro: Dependências não encontradas

```bash
# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install
npx playwright install
```

### Logs Detalhados

```bash
# Ver logs detalhados
DEBUG=pw:api npx playwright test

# Ver logs de browser
DEBUG=pw:browser npx playwright test

# Ver todos os logs
DEBUG=* npx playwright test
```

---

## 📝 Comandos Rápidos

### Todos os Comandos em Um Lugar

```bash
# Instalação
npm install
npx playwright install

# Desenvolvimento
npm run dev

# Build
npm run build

# Testes
npm test                              # Unitários
npm run test:coverage                 # Unitários com coverage
npm run test:watch                    # Unitários modo watch
npx playwright test                   # E2E todos
npx playwright test --ui              # E2E modo visual
npx playwright test e2e/crm/          # E2E por módulo
npx playwright test --grep "Auth"     # E2E por tag

# Lint e Formatação
npm run lint
npm run lint:fix
npm run format

# Relatórios
npx playwright show-report
coverage/index.html
```

---

## 📚 Recursos Adicionais

- [Documentação Playwright](https://playwright.dev/)
- [Documentação Vitest](https://vitest.dev/)
- [Guia de Boas Práticas](./TEST_COVERAGE_ANALYSIS.md)
- [Relatório de Cobertura](./RELATORIO_FINAL_MISSAO_TESTES.md)

---

## 💡 Dicas

1. **Use o modo UI** para desenvolvimento de novos testes
2. **Execute testes por módulo** para iteração rápida
3. **Use `--grep`** para filtrar testes específicos
4. **Sempre verifique relatórios** após execução completa
5. **Mantenha os browsers atualizados** com `npx playwright install`
6. **Use modo headed** para debug visual

---

*Última atualização: 2026-02-05*
