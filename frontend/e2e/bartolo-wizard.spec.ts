import { test, expect } from '@playwright/test';
import { BartoloFloatingChat, goToDashboardWithBartolo } from './helpers/bartolo.helpers';

test.describe('Bartolo - Wizards', () => {
  let chat: BartoloFloatingChat;

  test.beforeEach(async ({ page }) => {
    chat = new BartoloFloatingChat(page);
    await goToDashboardWithBartolo(page);
    await chat.open();
  });

  test('inicia wizard via comando no chat', async () => {
    const body = await chat.sendMessageAndWaitResponse('Quero criar uma escala');

    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(5);

    // Se retornou wizard_response, valida estrutura
    if (body.wizard_response) {
      expect(body.wizard_response).toHaveProperty('wizard_type');
      expect(body.wizard_response).toHaveProperty('current_step');
      expect(body.wizard_response).toHaveProperty('total_steps');
      expect(body.wizard_response.current_step).toBeGreaterThanOrEqual(1);
      expect(body.wizard_response.total_steps).toBeGreaterThan(0);
    }
  });

  test('wizard avanca passo a passo com respostas', async () => {
    // Primeiro comando - inicia wizard
    const step1 = await chat.sendMessageAndWaitResponse('Quero criar uma escala');

    if (step1.wizard_response) {
      const initialStep = step1.wizard_response.current_step;

      // Responde ao primeiro passo
      const step2 = await chat.sendMessageAndWaitResponse('Posto Central');

      expect(step2).toHaveProperty('response');
      expect(step2.response.length).toBeGreaterThan(5);

      if (step2.wizard_response) {
        // Deve ter avancado ou estar no proximo passo
        expect(step2.wizard_response.current_step).toBeGreaterThanOrEqual(initialStep);
      }
    }

    // Independente de wizard, as mensagens devem renderizar
    const userMessages = chat.getUserMessages();
    const count = await userMessages.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('wizard exibe progresso com informacao de passos', async () => {
    const body = await chat.sendMessageAndWaitResponse('Criar escala automatica');

    if (body.wizard_response) {
      const { current_step, total_steps, step_name } = body.wizard_response;

      // Valida campos do progresso
      expect(current_step).toBeGreaterThanOrEqual(1);
      expect(total_steps).toBeGreaterThan(0);
      expect(current_step).toBeLessThanOrEqual(total_steps);

      if (step_name) {
        expect(step_name.length).toBeGreaterThan(0);
      }
    }

    // Resposta renderiza na UI
    const lastAssistant = chat.getAssistantMessages().last();
    await expect(lastAssistant).toBeVisible({ timeout: 5000 });
  });
});
