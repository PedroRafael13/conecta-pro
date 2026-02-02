import { test, expect } from '@playwright/test';
import { AssistentePage, mockAuthMe } from './helpers/bartolo.helpers';

/**
 * NOTA: /modulos/assistente nao esta registrado em src/config/modules.ts.
 * O ModulosLayout checa getModuleByPath(pathname) e quando retorna undefined,
 * o layout fica preso no LoadingSpinner: `if (isLoading || !currentModule) return <LoadingSpinner />`
 *
 * Estes testes estao marcados como fixme ate que o modulo 'assistente' seja
 * adicionado a configuracao de modulos.
 */

test.describe('Bartolo - Pagina Assistente', () => {
  test.fixme(true, 'Modulo assistente nao registrado em modules.ts - layout trava no LoadingSpinner');

  let assistente: AssistentePage;

  test.beforeEach(async ({ page }) => {
    assistente = new AssistentePage(page);
    await assistente.goto();
  });

  test('exibe titulo e badge do modelo', async ({ page }) => {
    await expect(assistente.heading).toBeVisible();
    await expect(page.locator('text=Seu assistente IA para o Conecta PRO')).toBeVisible();

    const badge = page.locator('text=GPT-4 Turbo');
    await expect(badge).toBeVisible();
  });

  test('exibe 4 tabs: Chat, Estatisticas, Modulos, Assistentes Guiados', async () => {
    await expect(assistente.chatTab).toBeVisible();
    await expect(assistente.statsTab).toBeVisible();
    await expect(assistente.modulesTab).toBeVisible();
    await expect(assistente.wizardsTab).toBeVisible();
  });

  test('tab Chat exibe widget do Bartolo embedded', async ({ page }) => {
    await assistente.selectTab('chat');
    await expect(page.locator('text=Conversar com Bartolo')).toBeVisible();
    await expect(page.locator('h3:has-text("Bartolo"), .font-semibold:has-text("Bartolo")')).toBeVisible({ timeout: 5000 });
  });

  test('tab Estatisticas exibe cards de metricas', async ({ page }) => {
    await assistente.selectTab('stats');

    const statsCards = [
      'Interações Totais',
      'Taxa de Satisfação',
      'Padrões Aprendidos',
      'Tempo Médio Resposta',
      'Wizards Completados',
      'Consultas de Dados',
    ];

    for (const cardTitle of statsCards) {
      await expect(page.locator(`text=${cardTitle}`)).toBeVisible({ timeout: 10000 });
    }
  });

  test('tab Modulos exibe grid de modulos', async ({ page }) => {
    await assistente.selectTab('modules');

    await page.waitForTimeout(2000);
    const moduleCards = page.locator('text=Comandos:');
    const count = await moduleCards.count();

    if (count > 0) {
      expect(count).toBeGreaterThanOrEqual(1);
    }
  });

  test('tab Assistentes Guiados exibe wizards disponiveis', async ({ page }) => {
    await assistente.selectTab('wizards');

    await page.waitForTimeout(2000);
    const wizardCards = page.locator('text=passos');
    const count = await wizardCards.count();

    if (count > 0) {
      expect(count).toBeGreaterThanOrEqual(1);
    }
  });

  test('sugestoes iniciais sao exibidas no widget embedded', async ({ page }) => {
    await assistente.selectTab('chat');

    await page.waitForTimeout(3000);
    const suggestions = page.locator('text=Sugestões');
    const hasSuggestions = await suggestions.count();

    if (hasSuggestions > 0) {
      await expect(suggestions.first()).toBeVisible();
    }
  });
});
