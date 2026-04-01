# 🎭 MATRIZ DE TESTES E2E - CONECTA PRO

**Data:** 2026-02-11
**Framework:** Playwright (recomendado)
**Status:** 🟡 Em criação

---

## LEGENDA

| Status | Emoji | Significado |
|--------|-------|-------------|
| Existente | 🟢 | Teste já implementado |
| Criado | 🔵 | Teste criado nesta auditoria |
| Failing | 🔴 | Teste falhando (bug) |
| Blocked | ⚫ | Bloqueado (dependência) |
| Não Existe | ⚪ | Ainda não criado |

---

## MATRIZ POR MÓDULO

### 1. AUTENTICAÇÃO (Auth)

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| AUTH-001 | Login bem-sucedido | Usuário válido loga e redireciona | P0 | ⚪ | - |
| AUTH-002 | Login falho | Credenciais inválidas mostram erro | P0 | ⚪ | - |
| AUTH-003 | Logout | Usuário desloga e limpa token | P0 | ⚪ | - |
| AUTH-004 | JWT Refresh | Token expira e renova automaticamente | P0 | ⚪ | - |
| AUTH-005 | Permissões | Acesso negado a rotas sem permissão | P1 | ⚪ | - |
| AUTH-006 | Recuperar senha | Fluxo completo de reset | P1 | ⚪ | - |

---

### 2. REEMBOLSO (Reimbursement)

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| RMB-001 | Criar solicitação | Usuário cria reembolso em rascunho | P0 | ⚪ | - |
| RMB-002 | Adicionar item | Adicionar item à solicitação | P0 | ⚪ | - |
| RMB-003 | Upload comprovante | Anexar arquivo PDF/IMG | P0 | ⚪ | - |
| RMB-004 | Submeter | Enviar para aprovação | P0 | ⚪ | - |
| RMB-005 | Aprovar gestor | Gestor aprova solicitação | P0 | ⚪ | - |
| RMB-006 | Rejeitar | Gestor rejeita com motivo | P0 | ⚪ | - |
| RMB-007 | Processar pagamento | Financeiro processa pagamento | P0 | ⚪ | - |
| RMB-008 | Cancelar | Solicitante cancela rascunho | P1 | ⚪ | - |
| RMB-009 | Listar meus | Visualizar meus reembolsos | P1 | ⚪ | - |
| RMB-010 | Dashboard stats | Ver estatísticas no dashboard | P1 | ⚪ | - |

---

### 3. OPERACIONAL (Operational)

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| OPR-001 | Registrar ocorrência | Criar nova ocorrência | P0 | ⚪ | - |
| OPR-002 | Consultar rondas | Visualizar rondas do dia | P0 | ⚪ | - |
| OPR-003 | Registrar ponto | Bater ponto entrada/saída | P0 | ⚪ | - |
| OPR-004 | Escala de trabalho | Visualizar minha escala | P0 | ⚪ | - |
| OPR-005 | Aprovar escala | Gestor aprova escala | P1 | ⚪ | - |
| OPR-006 | Relatório diário | Gerar relatório de ocorrências | P1 | ⚪ | - |
| OPR-007 | Notificações | Receber alerta de ocorrência | P1 | ⚪ | - |

---

### 4. GED (Gestão Eletrônica de Documentos)

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| GED-001 | Upload documento | Enviar PDF para pasta | P1 | ⚪ | - |
| GED-002 | Versionamento | Criar nova versão | P1 | ⚪ | - |
| GED-003 | Download | Baixar documento | P1 | ⚪ | - |
| GED-004 | Permissões | Acesso por perfil | P1 | ⚪ | - |
| GED-005 | Busca | Encontrar por metadata | P2 | ⚪ | - |
| GED-006 | Assinatura digital | Assinar documento | P2 | ⚪ | - |

---

### 5. CRM

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| CRM-001 | Cadastrar cliente | Criar novo cliente | P1 | ⚪ | - |
| CRM-002 | Cadastrar condomínio | Vincular condomínio | P1 | ⚪ | - |
| CRM-003 | Contrato | Criar contrato | P1 | ⚪ | - |
| CRM-004 | Contato | Registrar interação | P1 | ⚪ | - |
| CRM-005 | Dashboard 360 | Visualizar resumo cliente | P2 | ⚪ | - |

---

### 6. FINANCEIRO

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| FIN-001 | Criar orçamento | Novo orçamento | P1 | ⚪ | - |
| FIN-002 | Aprovar orçamento | Gestor aprova | P1 | ⚪ | - |
| FIN-003 | Fatura | Gerar fatura mensal | P1 | ⚪ | - |
| FIN-004 | Contas a pagar | Registrar despesa | P2 | ⚪ | - |
| FIN-005 | Relatório DRE | Gerar relatório | P2 | ⚪ | - |

---

### 7. CONFIGURAÇÕES

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| CFG-001 | Gerenciar usuários | CRUD usuários | P1 | ⚪ | - |
| CFG-002 | Perfis e permissões | Configurar roles | P1 | ⚪ | - |
| CFG-003 | Integrações | Configurar webhook | P2 | ⚪ | - |
| CFG-004 | Notificações | Configurar canais | P2 | ⚪ | - |

---

### 8. MOBILE/RESPONSIVIDADE

| ID | Fluxo Crítico | Caso de Teste | Prioridade | Status | Arquivo |
|----|--------------|---------------|------------|--------|---------|
| MOB-001 | Login mobile | Tela login em 375px | P1 | ⚪ | - |
| MOB-002 | Menu hamburguer | Navegação mobile | P1 | ⚪ | - |
| MOB-003 | Registrar ocorrência | Form em mobile | P1 | ⚪ | - |
| MOB-004 | Tablets | iPad layout | P2 | ⚪ | - |

---

## RESUMO DE COBERTURA

| Módulo | Total Testes | P0 | P1 | P2 | Cobertura |
|--------|--------------|----|----|----|-----------|
| Auth | 6 | 4 | 2 | 0 | 0% |
| Reembolso | 10 | 7 | 2 | 1 | 0% |
| Operacional | 7 | 4 | 2 | 1 | 0% |
| GED | 6 | 0 | 4 | 2 | 0% |
| CRM | 5 | 0 | 4 | 1 | 0% |
| Financeiro | 5 | 0 | 3 | 2 | 0% |
| Configurações | 4 | 0 | 2 | 2 | 0% |
| Mobile | 4 | 0 | 3 | 1 | 0% |
| **TOTAL** | **47** | **15** | **22** | **10** | **0%** |

---

## TEMPLATE DE TESTE (Playwright)

```typescript
// e2e/reembolso/criar-solicitacao.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Reembolso - Criar Solicitação', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@conecta.pro');
    await page.fill('[data-testid="password"]', 'Test@123');
    await page.click('[data-testid="submit-login"]');
    await page.waitForURL('/dashboard');
  });

  test('deve criar solicitação em rascunho', async ({ page }) => {
    // Arrange
    await page.goto('/reembolsos/novo');

    // Act
    await page.fill('[data-testid="titulo"]', 'Despesa Viagem');
    await page.fill('[data-testid="descricao"]', 'Hotel SP');
    await page.fill('[data-testid="valor"]', '500,00');
    await page.click('[data-testid="salvar-rascunho"]');

    // Assert
    await expect(page.locator('[data-testid="success-toast"]'))
      .toContainText('Rascunho salvo');
    await expect(page).toHaveURL(/\/reembolsos\/\d+/);
  });

  test('deve validar campos obrigatórios', async ({ page }) => {
    // Act
    await page.goto('/reembolsos/novo');
    await page.click('[data-testid="salvar-rascunho"]');

    // Assert
    await expect(page.locator('[data-testid="error-titulo"]'))
      .toBeVisible();
  });
});
```

---

## COMANDOS ÚTEIS

```bash
# Instalar Playwright
cd /opt/conecta-pro/frontend
npm install -D @playwright/test
npx playwright install

# Rodar todos os testes E2E
npx playwright test

# Rodar com UI
npx playwright test --ui

# Debug
npx playwright test --debug

# Gerar relatório
npx playwright show-report
```

---

## PRÓXIMOS PASSOS

1. **Semana 1:** Criar testes P0 (Auth + Reembolso + Operacional)
2. **Semana 2:** Criar testes P1 restantes
3. **Semana 3:** Implementar CI/CD com E2E

---

*Matriz atualizada: 2026-02-11*
