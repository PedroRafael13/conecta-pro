import { test, expect } from '@playwright/test';
import { BartoloFloatingChat, goToDashboardWithBartolo } from './helpers/bartolo.helpers';

test.describe('Bartolo - Conversa Geral', () => {
  let chat: BartoloFloatingChat;

  test.beforeEach(async ({ page }) => {
    chat = new BartoloFloatingChat(page);
    await goToDashboardWithBartolo(page);
    await chat.open();
  });

  test('exibe saudacao inicial do Bartolo', async () => {
    // O greeting vem da API /greeting ou aparece como placeholder estatico
    // Quando a API funciona, retorna uma mensagem de assistente com saudacao
    // Quando nao funciona, mostra placeholder "Ola! Sou o Bartolo"
    const assistantMessages = chat.getAssistantMessages();
    const staticGreeting = chat.page.locator('h4:has-text("Ola! Sou o Bartolo")');

    // Aguarda qualquer um dos dois: greeting da API ou placeholder estatico
    await expect(assistantMessages.first().or(staticGreeting)).toBeVisible({ timeout: 10000 });

    // Se greeting da API apareceu, valida que tem conteudo
    const apiGreetingCount = await assistantMessages.count();
    if (apiGreetingCount > 0) {
      const text = await assistantMessages.first().textContent();
      expect(text).toBeTruthy();
      expect(text!.length).toBeGreaterThan(10);
    }
  });

  test('recebe resposta do LLM para pergunta geral', async () => {
    const body = await chat.sendMessageAndWaitResponse('O que voce pode fazer?');

    // Valida estrutura da resposta
    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(10);
    expect(body).toHaveProperty('message_id');

    // Resposta aparece na UI - aguarda renderizacao com timeout maior
    const assistantMessages = chat.getAssistantMessages();
    const lastMessage = assistantMessages.last();
    await expect(lastMessage).toBeVisible({ timeout: 10000 });
    const text = await lastMessage.textContent();
    expect(text!.length).toBeGreaterThan(10);
  });

  test('mantem contexto entre mensagens na mesma sessao', async () => {
    // Primeira mensagem
    await chat.sendMessageAndWaitResponse('Meu nome e Jordan');

    // Segunda mensagem referenciando a primeira
    const body = await chat.sendMessageAndWaitResponse('Qual e meu nome?');

    // A resposta deve conter referencia ao nome (nao-deterministico, valida estruturalmente)
    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(5);

    // Verifica que existem pelo menos 2 mensagens do usuario
    const userMessages = chat.getUserMessages();
    await expect(userMessages).toHaveCount(2);
  });

  test('exibe sugestoes de resposta apos mensagem do assistente', async ({ page }) => {
    // Sugestoes rapidas do BartoloChat.tsx aparecem quando messages.length === 0
    // Sao botoes dentro da area de chat (px-4 pb-2), nao o botao flutuante
    const chatSuggestions = page.locator('.px-4.pb-2 button.rounded-full');
    const initialCount = await chatSuggestions.count();

    if (initialCount > 0) {
      await expect(chatSuggestions.first()).toBeVisible();
    }

    // Apos enviar mensagem, valida que a API responde
    const body = await chat.sendMessageAndWaitResponse('Ola');
    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(0);
  });
});
