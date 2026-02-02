/**
 * Testes E2E - Dashboard de Licitações
 */

import { test, expect } from '@playwright/test';

test.describe('Dashboard de Licitações', () => {
  test.beforeEach(async ({ page }) => {
    // Navegar para o dashboard
    await page.goto('/modulos/licitacoes');
  });

  test('deve carregar o dashboard corretamente', async ({ page }) => {
    // Verificar título
    await expect(page.locator('h1')).toContainText('Licitações');

    // Verificar descrição
    await expect(page.locator('text=Gestão de licitações públicas')).toBeVisible();
  });

  test('deve exibir os 4 cards de KPIs', async ({ page }) => {
    // Verificar presença dos KPIs
    await expect(page.locator('text=Editais Abertos')).toBeVisible();
    await expect(page.locator('text=Propostas em Análise')).toBeVisible();
    await expect(page.locator('text=Contratos Vigentes')).toBeVisible();
    await expect(page.locator('text=Certidões Pendentes')).toBeVisible();
  });

  test('deve exibir cards de acesso rápido', async ({ page }) => {
    await expect(page.locator('text=Editais Recentes')).toBeVisible();
    await expect(page.locator('text=Minhas Propostas')).toBeVisible();
    await expect(page.locator('text=Contratos Ativos')).toBeVisible();
  });

  test('deve navegar para editais ao clicar no card', async ({ page }) => {
    await page.click('text=Editais Abertos');
    await expect(page).toHaveURL(/\/modulos\/licitacoes\/editais/);
  });

  test('deve navegar para propostas ao clicar no card', async ({ page }) => {
    await page.click('text=Propostas em Análise');
    await expect(page).toHaveURL(/\/modulos\/licitacoes\/propostas/);
  });

  test('deve navegar para contratos ao clicar no card', async ({ page }) => {
    await page.click('text=Contratos Vigentes');
    await expect(page).toHaveURL(/\/modulos\/licitacoes\/contratos/);
  });
});
