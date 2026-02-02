import { Page, expect, Locator } from '@playwright/test';

/**
 * Page Object Model para o chat flutuante do Bartolo (BartoloChat.tsx)
 */
export class BartoloFloatingChat {
  readonly page: Page;
  readonly openButton: Locator;
  readonly chatWindow: Locator;
  readonly closeButton: Locator;
  readonly minimizeButton: Locator;
  readonly resetButton: Locator;
  readonly messageInput: Locator;
  readonly submitButton: Locator;
  readonly typingIndicator: Locator;

  constructor(page: Page) {
    this.page = page;
    this.openButton = page.locator('button[aria-label="Abrir chat com Bartolo"]');
    this.chatWindow = page.locator('.fixed.bottom-6.right-6.z-50').filter({ has: page.locator('h3:has-text("Bartolo")') });
    this.closeButton = page.locator('button[title="Fechar"]');
    this.minimizeButton = page.locator('button[title="Minimizar"], button[title="Expandir"]');
    this.resetButton = page.locator('button[title="Reiniciar conversa"]');
    this.messageInput = page.locator('input[placeholder="Digite sua mensagem..."]');
    this.submitButton = page.locator('form button[type="submit"]');
    this.typingIndicator = page.locator('.animate-bounce');
  }

  async open() {
    await this.openButton.click();
    await expect(this.messageInput).toBeVisible({ timeout: 5000 });
  }

  async close() {
    await this.closeButton.click();
    await expect(this.openButton).toBeVisible({ timeout: 5000 });
  }

  async sendMessage(text: string) {
    await this.messageInput.fill(text);
    await this.submitButton.click();
  }

  /**
   * Envia mensagem e aguarda resposta da API /send
   * Retorna o body da resposta
   */
  async sendMessageAndWaitResponse(text: string): Promise<any> {
    const responsePromise = this.page.waitForResponse(
      (res) => res.url().includes('/api/v1/ai/bartolo/send') && res.status() === 200,
      { timeout: 30000 }
    );
    await this.sendMessage(text);
    const response = await responsePromise;
    return response.json();
  }

  /** Retorna todas as mensagens visíveis no chat (plain text e HTML) */
  getMessages() {
    return this.page.locator('.rounded-2xl.px-4 > .text-sm');
  }

  /** Retorna mensagens do assistente (plain text via p.whitespace-pre-wrap OU HTML via div.prose) */
  getAssistantMessages() {
    return this.page.locator('.bg-slate-800.rounded-2xl > .text-sm');
  }

  /** Retorna mensagens do usuario */
  getUserMessages() {
    return this.page.locator('.bg-amber-600 .text-sm.whitespace-pre-wrap');
  }

  /** Retorna botoes de sugestao */
  getSuggestions() {
    return this.page.locator('button').filter({ hasText: /Sugestoes/i }).locator('..').locator('button');
  }

  /** Botoes de feedback (thumbs up/down) */
  getThumbsUp(messageIndex: number) {
    return this.page.locator('button[title="Util"]').nth(messageIndex);
  }

  getThumbsDown(messageIndex: number) {
    return this.page.locator('button[title="Nao ajudou"]').nth(messageIndex);
  }
}

/**
 * Page Object para a pagina /modulos/assistente
 */
export class AssistentePage {
  readonly page: Page;
  readonly heading: Locator;
  readonly chatTab: Locator;
  readonly statsTab: Locator;
  readonly modulesTab: Locator;
  readonly wizardsTab: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.locator('h1:has-text("Bartolo - Assistente Inteligente")');
    this.chatTab = page.locator('button[role="tab"]:has-text("Chat")');
    this.statsTab = page.locator('button[role="tab"]:has-text("Estatísticas")');
    this.modulesTab = page.locator('button[role="tab"]:has-text("Módulos")');
    this.wizardsTab = page.locator('button[role="tab"]:has-text("Assistentes Guiados")');
  }

  async goto() {
    await mockAuthMe(this.page);
    await this.page.goto('/modulos/assistente');
    await expect(this.heading).toBeVisible({ timeout: 10000 });
  }

  async selectTab(tab: 'chat' | 'stats' | 'modules' | 'wizards') {
    const tabs = {
      chat: this.chatTab,
      stats: this.statsTab,
      modules: this.modulesTab,
      wizards: this.wizardsTab,
    };
    await tabs[tab].click();
  }
}

/**
 * Helpers utilitarios
 */

/**
 * Mocka GET /auth/me que retorna 500 no backend (bug: permissions=None).
 * Necessario para manter autenticacao client-side funcionando nos testes.
 */
export async function mockAuthMe(page: Page) {
  await page.route('**/api/v1/auth/me', (route) => {
    if (route.request().method() === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          email: 'admin@conectapro.com.br',
          name: 'Admin',
          role: 'admin',
          is_active: true,
          permissions: [],
        }),
      });
    } else {
      route.continue();
    }
  });
}

/** Navega para dashboard e aguarda o botao do Bartolo estar visivel */
export async function goToDashboardWithBartolo(page: Page) {
  await mockAuthMe(page);
  await page.goto('/dashboard');
  const bartoloButton = page.locator('button[aria-label="Abrir chat com Bartolo"]');
  await expect(bartoloButton).toBeVisible({ timeout: 10000 });
}

/** Intercepta chamada de feedback e retorna promise */
export function interceptFeedback(page: Page) {
  return page.waitForRequest(
    (req) => req.url().includes('/api/v1/ai/bartolo/feedback') && req.method() === 'POST',
    { timeout: 10000 }
  );
}

/** Intercepta chamada de send e retorna promise da response */
export function interceptSendResponse(page: Page) {
  return page.waitForResponse(
    (res) => res.url().includes('/api/v1/ai/bartolo/send') && res.status() === 200,
    { timeout: 30000 }
  );
}
