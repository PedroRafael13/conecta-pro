# Testes E2E - Conecta PRO

Este diretório contém os testes End-to-End do projeto Conecta PRO usando Playwright + TypeScript.

## Estrutura

```
e2e/
├── auth.setup.ts              # Setup de autenticação global
├── fixtures.ts                # Fixtures customizadas do Playwright
├── login.spec.ts              # Testes básicos de login (legacy)
├── README.md                  # Este arquivo
├── auth/
│   ├── login.spec.ts          # Testes completos de login
│   └── recuperar-senha.spec.ts # Testes de recuperação de senha
├── dashboard/
│   └── dashboard.spec.ts      # Testes do dashboard principal
└── helpers/
    ├── auth.ts                # Helper de autenticação via API
    └── bartolo.helpers.ts     # Helpers do Bartolo (IA)
```

## Convenções de Data-TestID

Para melhor manutenção dos testes, recomenda-se adicionar os seguintes data-testid nas páginas:

### Login (`/login`)
- `[data-testid="login-email"]` - Campo de email
- `[data-testid="login-password"]` - Campo de senha
- `[data-testid="login-submit"]` - Botão de login
- `[data-testid="login-error"]` - Mensagem de erro
- `[data-testid="login-forgot-password"]` - Link esqueci senha
- `[data-testid="login-remember-me"]` - Checkbox lembrar-me

### Dashboard (`/dashboard`)
- `[data-testid="dashboard-header"]` - Header do dashboard
- `[data-testid="dashboard-search"]` - Campo de busca
- `[data-testid="dashboard-notifications"]` - Botão de notificações
- `[data-testid="dashboard-user-menu"]` - Menu do usuário
- `[data-testid="dashboard-logout"]` - Botão de logout
- `[data-testid="module-{id}"]` - Cards de módulos
- `[data-testid="stat-{nome}"]` - Cards de estatísticas

## Executando os Testes

```bash
# Executar todos os testes
npx playwright test

# Executar testes de autenticação
npx playwright test auth/

# Executar testes do dashboard
npx playwright test dashboard/

# Executar com UI
npx playwright test --ui

# Executar em modo debug
npx playwright test --debug

# Executar em modo headed (mostra navegador)
npx playwright test --headed
```

## Autenticação nos Testes

Os testes usam duas estratégias de autenticação:

1. **Login via API** (`helpers/auth.ts`): Injeta token JWT diretamente no localStorage
2. **Storage State**: Usa arquivo `e2e/.auth/user.json` para persistir sessão entre testes

### Exemplo de uso do helper:

```typescript
import { test, expect } from '@playwright/test';
import { loginViaAPI } from './helpers/auth';

test('teste autenticado', async ({ page }) => {
  await loginViaAPI(page);
  await page.goto('/dashboard');
  // ...
});
```

## Credenciais de Teste

As credenciais padrão para testes são:
- Email: `admin@conectaplus.com.br`
- Senha: `admin123`

## Configuração

A configuração do Playwright está em `playwright.config.ts`:
- Base URL: `https://erp.conectamais.pro`
- Diretório de testes: `./e2e`
- Timeout: 30s
- Retry: 2 (CI) / 0 (local)

## Gerando Relatórios

```bash
# Relatório HTML
npx playwright show-report ../reports/playwright
```

## Boas Práticas

1. Sempre use o helper `loginViaAPI` para testes que precisam de autenticação
2. Use seletores semânticos (texto, aria-label) quando possível
3. Adicione timeouts explícitos apenas quando necessário
4. Mantenha os testes independentes entre si
5. Use `test.describe` para agrupar testes relacionados
