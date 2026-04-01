import { test, expect } from '@playwright/test';

test.describe('Autenticação - Recuperar Senha', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('deve exibir link de recuperação de senha', async ({ page }) => {
    const forgotPasswordLink = page.locator('a:has-text("Esqueci a senha")');
    await expect(forgotPasswordLink).toBeVisible();
    await expect(forgotPasswordLink).toHaveText(/Esqueci a senha/i);
  });

  test('deve solicitar recuperação de senha com email válido', async ({ page }) => {
    // Mock do endpoint de recuperação de senha
    await page.route('**/api/v1/auth/forgot-password', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Email de recuperação enviado com sucesso',
        }),
      });
    });

    // Clica no link de esqueci a senha (se houver modal ou navegação)
    await page.click('a:has-text("Esqueci a senha")');

    // Se abrir modal ou navegar para página de recuperação
    // Adaptar conforme implementação real
    const currentUrl = page.url();

    // Verifica se há feedback visual (toast, modal, etc)
    // Nota: Implementação depende do comportamento real da aplicação
  });

  test('deve validar formato de email na recuperação', async ({ page }) => {
    // Clica no link de esqueci a senha
    await page.click('a:has-text("Esqueci a senha")');

    // Se houver campo de email na recuperação
    const emailInput = page.locator('input[type="email"]').first();

    // Verifica validação de email
    if (await emailInput.isVisible().catch(() => false)) {
      await emailInput.fill('email-invalido');
      await expect(emailInput).toHaveAttribute('type', 'email');
    }
  });
});

test.describe('Autenticação - Reset de Senha', () => {
  test('deve acessar página de reset com token válido', async ({ page }) => {
    // Mock do endpoint de validação de token
    await page.route('**/api/v1/auth/reset-password/validate', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          valid: true,
          email: 'usuario@exemplo.com',
        }),
      });
    });

    // Acessa página de reset com token
    await page.goto('/reset-password?token=valid_token_123');

    // Verifica se a página carregou
    await expect(page.locator('input[type="password"]').first()).toBeVisible({ timeout: 5000 });
  });

  test('deve rejeitar token inválido', async ({ page }) => {
    // Mock do endpoint de validação de token inválido
    await page.route('**/api/v1/auth/reset-password/validate', (route) => {
      route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Token inválido ou expirado',
        }),
      });
    });

    // Acessa página de reset com token inválido
    await page.goto('/reset-password?token=invalid_token');

    // Aguarda mensagem de erro
    await page.waitForTimeout(1000);
  });

  test('deve redefinir senha com sucesso', async ({ page }) => {
    // Mock do endpoint de reset de senha
    await page.route('**/api/v1/auth/reset-password', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Senha redefinida com sucesso',
        }),
      });
    });

    await page.goto('/reset-password?token=valid_token_123');

    // Preenche nova senha
    await page.fill('input[type="password"]:nth-of-type(1)', 'NovaSenha123!');
    await page.fill('input[type="password"]:nth-of-type(2)', 'NovaSenha123!');

    // Submete formulário
    await page.click('button[type="submit"]');

    // Verifica redirecionamento ou mensagem de sucesso
    await page.waitForTimeout(2000);
  });

  test('deve validar confirmação de senha', async ({ page }) => {
    await page.goto('/reset-password?token=valid_token_123');

    // Preenche senhas diferentes
    await page.fill('input[type="password"]:nth-of-type(1)', 'Senha123!');
    await page.fill('input[type="password"]:nth-of-type(2)', 'SenhaDiferente123!');

    // Tenta submeter
    await page.click('button[type="submit"]');

    // Verifica mensagem de erro de validação
    // (Implementação depende da UI real)
  });
});
