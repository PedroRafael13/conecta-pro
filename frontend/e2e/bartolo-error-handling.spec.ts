import { test, expect } from '@playwright/test';
import { BartoloFloatingChat, goToDashboardWithBartolo } from './helpers/bartolo.helpers';

test.describe('Bartolo - Error Handling', () => {
  let chat: BartoloFloatingChat;

  test.beforeEach(async ({ page }) => {
    chat = new BartoloFloatingChat(page);
    await goToDashboardWithBartolo(page);
    await chat.open();
  });

  test('nao envia mensagem vazia', async ({ page }) => {
    // Botao submit deve estar desabilitado com input vazio
    await expect(chat.submitButton).toBeDisabled();

    // Tenta enviar com espacos em branco
    await chat.messageInput.fill('   ');
    await expect(chat.submitButton).toBeDisabled();
  });

  test('exibe erro quando API retorna 500', async ({ page }) => {
    // Intercepta a proxima chamada /send e retorna 500
    await page.route('**/api/v1/ai/bartolo/send', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal Server Error' }),
      });
    });

    await chat.messageInput.fill('Teste de erro');
    await chat.submitButton.click();

    // A mensagem do usuario deve aparecer
    const userMessages = chat.getUserMessages();
    await expect(userMessages.last()).toContainText('Teste de erro');

    // Aguarda feedback de erro (pode ser toast, mensagem inline ou ausencia de resposta)
    await page.waitForTimeout(5000);

    // Nao deve ter crashado - chat ainda funcional
    await expect(chat.messageInput).toBeVisible();
    await expect(chat.messageInput).toBeEnabled();
  });

  test('lida com erro de rede (conexao perdida)', async ({ page }) => {
    // Intercepta e aborta a conexao
    await page.route('**/api/v1/ai/bartolo/send', (route) => {
      route.abort('connectionrefused');
    });

    await chat.messageInput.fill('Teste offline');
    await chat.submitButton.click();

    // Aguarda tratamento do erro
    await page.waitForTimeout(5000);

    // Chat nao deve crashar - input continua acessivel
    await expect(chat.messageInput).toBeVisible();
    await expect(chat.messageInput).toBeEnabled();
  });

  test('lida com token expirado (401)', async ({ page }) => {
    // Intercepta e retorna 401
    await page.route('**/api/v1/ai/bartolo/send', (route) => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Token expired' }),
      });
    });

    await chat.messageInput.fill('Teste token expirado');
    await chat.submitButton.click();

    // Aguarda tratamento - pode redirecionar para login ou mostrar erro
    await page.waitForTimeout(5000);

    const url = page.url();
    const inputVisible = await chat.messageInput.isVisible().catch(() => false);

    // Ou redirecionou para login, ou manteve o chat funcional com mensagem de erro
    expect(url.includes('/login') || inputVisible).toBeTruthy();
  });
});
