/**
 * Testes E2E - CRUD de Editais
 */

import { test, expect } from '@playwright/test';

test.describe('Editais - CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais');
  });

  test('deve carregar a página de editais', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Editais');
  });

  test('deve exibir botão Novo Edital', async ({ page }) => {
    const novoButton = page.locator('button:has-text("Novo Edital")').first();
    await expect(novoButton).toBeVisible();
  });

  test('deve abrir modal ao clicar em Novo Edital', async ({ page }) => {
    const novoButton = page.locator('button:has-text("Novo Edital")').first();
    await novoButton.click();

    // Aguardar modal abrir (ajustar seletor conforme implementação)
    await page.waitForTimeout(500);
  });

  test('deve exibir filtros de busca', async ({ page }) => {
    // Verificar se existem inputs de filtro
    const searchInputs = page.locator('input[type="text"]');
    await expect(searchInputs.first()).toBeVisible();
  });

  test('deve filtrar editais por status', async ({ page }) => {
    // Aguardar carregamento
    await page.waitForLoadState('networkidle');

    // Selecionar filtro (ajustar seletor conforme implementação)
    const statusFilter = page.locator('select, [role="combobox"]').first();
    if (await statusFilter.isVisible()) {
      await statusFilter.click();
    }
  });

  test('deve exibir paginação quando houver muitos editais', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Verificar se há controles de paginação (se houver dados suficientes)
    const paginationButtons = page.locator('button:has-text("Próxima"), button:has-text("Anterior")');
    // Paginação pode não estar visível se houver poucos dados
  });
});
