import { test, expect } from '@playwright/test';
import {
  BartoloFloatingChat,
  goToDashboardWithBartolo,
  interceptFeedback,
} from './helpers/bartolo.helpers';

test.describe('Bartolo - Feedback', () => {
  let chat: BartoloFloatingChat;

  test.beforeEach(async ({ page }) => {
    chat = new BartoloFloatingChat(page);
    await goToDashboardWithBartolo(page);
    await chat.open();

    // Envia uma mensagem e aguarda resposta para ter botoes de feedback
    await chat.sendMessageAndWaitResponse('Ola Bartolo');
  });

  test('envia feedback positivo (thumbs up) via API', async ({ page }) => {
    // Intercepta a chamada de feedback
    const feedbackRequest = interceptFeedback(page);

    // Hover na mensagem para revelar botoes de feedback
    const assistantMsg = page.locator('.bg-slate-800').last();
    await assistantMsg.hover();

    // Clica thumbs up
    const thumbsUp = page.locator('button[title="Util"]').last();
    await thumbsUp.click({ force: true });

    // Valida que a requisicao foi feita com os dados corretos
    const request = await feedbackRequest;
    const requestBody = request.postDataJSON();
    expect(requestBody).toHaveProperty('interaction_id');
    expect(requestBody.feedback_type).toBe('helpful');
  });

  test('envia feedback negativo (thumbs down) via API', async ({ page }) => {
    const feedbackRequest = interceptFeedback(page);

    const assistantMsg = page.locator('.bg-slate-800').last();
    await assistantMsg.hover();

    const thumbsDown = page.locator('button[title="Nao ajudou"]').last();
    await thumbsDown.click({ force: true });

    const request = await feedbackRequest;
    const requestBody = request.postDataJSON();
    expect(requestBody).toHaveProperty('interaction_id');
    expect(requestBody.feedback_type).toBe('not_helpful');
  });

  test('botoes de feedback existem apenas em mensagens do assistente', async ({ page }) => {
    // Mensagens do usuario nao devem ter botoes de feedback
    const userMsgContainers = page.locator('.bg-amber-600').locator('..');
    const userFeedback = userMsgContainers.locator('button[title="Util"]');
    await expect(userFeedback).toHaveCount(0);

    // Mensagens do assistente devem ter botoes
    const assistantFeedback = page.locator('button[title="Util"]');
    const count = await assistantFeedback.count();
    expect(count).toBeGreaterThan(0);
  });
});
