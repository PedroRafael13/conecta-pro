import { test, expect } from '@playwright/test';
import { BartoloFloatingChat, goToDashboardWithBartolo } from './helpers/bartolo.helpers';

test.describe('Bartolo - Consultas de Dados', () => {
  let chat: BartoloFloatingChat;

  test.beforeEach(async ({ page }) => {
    chat = new BartoloFloatingChat(page);
    await goToDashboardWithBartolo(page);
    await chat.open();
  });

  test('consulta funcionarios ativos retorna dados', async () => {
    const body = await chat.sendMessageAndWaitResponse('Funcionarios ativos');

    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(5);

    // Se retornou data_results, valida estrutura
    if (body.data_results) {
      expect(body.data_results).toHaveProperty('entity');
      expect(body.data_results).toHaveProperty('total_count');
      expect(typeof body.data_results.total_count).toBe('number');
    }

    // Resposta renderiza na UI
    const lastAssistant = chat.getAssistantMessages().last();
    await expect(lastAssistant).toBeVisible({ timeout: 5000 });
  });

  test('consulta postos sem cobertura', async () => {
    const body = await chat.sendMessageAndWaitResponse('Postos sem cobertura');

    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(5);

    // Resposta aparece na UI
    const lastAssistant = chat.getAssistantMessages().last();
    await expect(lastAssistant).toBeVisible({ timeout: 5000 });
  });

  test('consulta escalas da semana', async () => {
    const body = await chat.sendMessageAndWaitResponse('Escala da semana');

    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(5);

    const lastAssistant = chat.getAssistantMessages().last();
    await expect(lastAssistant).toBeVisible({ timeout: 5000 });
  });

  test('renderiza resposta com data_results quando disponivel', async () => {
    const body = await chat.sendMessageAndWaitResponse('Quantos funcionarios ativos temos?');

    // Valida a resposta da API
    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(5);

    // Se retornou data_results, valida a estrutura no JSON
    // NOTA: O BartoloChat.tsx (floating) renderiza apenas texto e HTML,
    // nao possui card visual para data_results (isso so existe no BartoloChatWidget)
    if (body.data_results) {
      expect(body.data_results).toHaveProperty('entity');
      expect(body.data_results).toHaveProperty('total_count');
      expect(typeof body.data_results.total_count).toBe('number');
    }

    // Resposta textual renderiza na UI
    const lastAssistant = chat.getAssistantMessages().last();
    await expect(lastAssistant).toBeVisible({ timeout: 10000 });
  });
});
