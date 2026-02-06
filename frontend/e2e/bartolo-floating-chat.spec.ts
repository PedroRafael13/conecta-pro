import { test, expect } from '@playwright/test';
import { BartoloFloatingChat, goToDashboardWithBartolo } from './helpers/bartolo.helpers';

test.describe('Bartolo - Chat Flutuante', () => {
  let chat: BartoloFloatingChat;

  test.beforeEach(async ({ page }) => {
    chat = new BartoloFloatingChat(page);
    await goToDashboardWithBartolo(page);
  });

  test('exibe botao flutuante no dashboard', async ({ page }) => {
    await expect(chat.openButton).toBeVisible();
    await expect(chat.openButton).toHaveAttribute('aria-label', 'Abrir chat com Bartolo');
  });

  test('abre chat ao clicar no botao flutuante', async () => {
    await chat.open();
    await expect(chat.messageInput).toBeVisible();
    await expect(chat.submitButton).toBeVisible();
  });

  test('fecha chat ao clicar no botao fechar', async ({ page }) => {
    await chat.open();
    await chat.close();
    await expect(chat.openButton).toBeVisible();
    // BartoloChat usa opacity-0 + pointer-events-none para esconder (nao unmount)
    // Verificar CSS do container ao inves de visibilidade do input
    const chatContainer = page.locator('.fixed.bottom-6.right-6.z-50').filter({
      has: page.locator('h3:has-text("Bartolo")')
    });
    await expect(chatContainer).toHaveCSS('opacity', '0');
  });

  test('minimiza e expande chat', async ({ page }) => {
    await chat.open();

    // Minimiza
    await page.locator('button[title="Minimizar"]').click();
    await expect(chat.messageInput).not.toBeVisible();

    // Header ainda visivel
    await expect(page.locator('h3:has-text("Bartolo")')).toBeVisible();

    // Expande
    await page.locator('button[title="Expandir"]').click();
    await expect(chat.messageInput).toBeVisible();
  });

  test('envia mensagem e exibe na conversa', async () => {
    await chat.open();
    await chat.sendMessage('Ola Bartolo');

    // Mensagem do usuario aparece
    const userMessages = chat.getUserMessages();
    await expect(userMessages.last()).toContainText('Ola Bartolo');
  });

  test('exibe indicador de digitacao enquanto aguarda resposta', async ({ page }) => {
    await chat.open();

    // Envia sem esperar resposta
    await chat.messageInput.fill('Teste de typing');
    await chat.submitButton.click();

    // Indicador de digitacao deve aparecer (bouncing dots)
    const typingDots = page.locator('.animate-bounce');
    await expect(typingDots.first()).toBeVisible({ timeout: 5000 });
  });

  test('reinicia conversa ao clicar no botao reset', async ({ page }) => {
    await chat.open();

    // Envia uma mensagem e aguarda resposta
    await chat.sendMessageAndWaitResponse('Ola');

    // Deve ter mensagens
    const messages = chat.getMessages();
    const countBefore = await messages.count();
    expect(countBefore).toBeGreaterThan(0);

    // Reinicia
    await chat.resetButton.click();

    // Apos reset, pode ter apenas o greeting ou nenhuma mensagem do usuario
    await page.waitForTimeout(500);
    const userMessages = chat.getUserMessages();
    await expect(userMessages).toHaveCount(0);
  });
});
