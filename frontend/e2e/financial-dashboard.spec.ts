/**
 * Testes E2E - Dashboard Financeiro
 *
 * Validações:
 * - Carregamento da página sem erros
 * - Renderização de 4 KPI cards (Receita, Despesa, Saldo, Inadimplência)
 * - Exibição correta de 12 cards de navegação para submódulos
 * - Funcionalidade de navegação para cada submódulo
 */

import { test, expect } from './fixtures';

test.describe('Dashboard Financeiro', () => {
  const KPI_LABELS = ['Receita', 'Despesa', 'Saldo', 'Inadimplência'];
  const NAVIGATION_MODULES = [
    'Contas a Pagar',
    'Contas a Receber',
    'Fluxo de Caixa',
    'Conciliação',
    'Fornecedores',
    'Clientes',
    'Compras',
    'Estoque',
    'Fiscal',
    'Contabilidade',
    'Faturamento',
    'Custeio ABC',
  ];

  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro', { waitUntil: 'load' });
  });

  test('deve carregar dashboard sem erros', async ({ page }) => {
    await test.step('Verificar ausência de erros 404 ou 500', async () => {
      const errors = await page.evaluate(() => {
        const consoleErrors = (window as any).__consoleErrors || [];
        return consoleErrors.filter((msg: string) => msg.includes('404') || msg.includes('500'));
      });
      expect(errors).toHaveLength(0);
    });

    await test.step('Verificar presença do header "Financeiro"', async () => {
      await expect(page.locator('h1')).toContainText('Financeiro');
    });
  });

  test('deve exibir 4 cards de KPI com valores válidos', async ({ page }) => {
    for (const label of KPI_LABELS) {
      await test.step(`Verificar KPI "${label}"`, async () => {
        const kpiCard = page.locator('text=' + label).first();
        await expect(kpiCard).toBeVisible({ timeout: 8000 });

        // Verificar que há um valor de moeda (R$ X,XX)
        const card = kpiCard.locator('..');
        const currencyValue = card.locator('text=/R\\$\\s+[\\d.,]+/');
        await expect(currencyValue).toBeVisible();
      });
    }
  });

  test('deve exibir 12 cards de navegação para submódulos', async ({ page }) => {
    for (const module of NAVIGATION_MODULES) {
      await test.step(`Verificar módulo "${module}"`, async () => {
        const moduleCard = page.locator('text=' + module).first();
        await expect(moduleCard).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve navegar para Contas a Pagar ao clicar no card', async ({ page }) => {
    // Os cards de navegação estão no main (não na sidebar)
    const mainContent = page.locator('main');

    await test.step('Clicar no card "Contas a Pagar" no painel principal', async () => {
      await mainContent.locator('text=Contas a Pagar').first().click();
      await page.waitForURL(/\/modulos\/financeiro\/contas-pagar/, { timeout: 8000 });
    });

    await test.step('Verificar conteúdo da página de Contas a Pagar', async () => {
      await expect(page.locator('h1')).toContainText('Contas a Pagar', { timeout: 8000 });
    });
  });

  test('deve navegar para Fluxo de Caixa ao clicar no card', async ({ page }) => {
    const mainContent = page.locator('main');

    await test.step('Clicar no card "Fluxo de Caixa" no painel principal', async () => {
      await mainContent.locator('text=Fluxo de Caixa').first().click();
      await page.waitForURL(/\/modulos\/financeiro\/fluxo-caixa/, { timeout: 8000 });
    });

    await test.step('Verificar conteúdo da página de Fluxo de Caixa', async () => {
      await expect(page.locator('h1')).toContainText('Fluxo de Caixa', { timeout: 8000 });
    });
  });

  test('deve navegar para Fiscal ao clicar no card', async ({ page }) => {
    const mainContent = page.locator('main');

    await test.step('Clicar no card "Fiscal" no painel principal', async () => {
      await mainContent.locator('text=Fiscal').first().click();
      await page.waitForURL(/\/modulos\/financeiro\/fiscal/, { timeout: 8000 });
    });

    await test.step('Verificar conteúdo da página de Fiscal', async () => {
      await expect(page.locator('h1')).toContainText('Fiscal', { timeout: 8000 });
    });
  });

  test('deve navegar para Fornecedores ao clicar no card', async ({ page }) => {
    await test.step('Clicar no card "Fornecedores" via h3 no painel principal', async () => {
      // Cards do dashboard usam h3 para o título; sidebar usa botões
      await page.locator('main h3:has-text("Fornecedores")').click();
      await page.waitForURL(/\/modulos\/financeiro\/fornecedores/, { timeout: 8000 });
    });

    await test.step('Verificar conteúdo da página de Fornecedores', async () => {
      await expect(page.locator('h1')).toContainText('Fornecedores', { timeout: 8000 });
    });
  });
});
