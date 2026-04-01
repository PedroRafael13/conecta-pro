/**
 * Testes E2E - Dashboard Recrutamento
 * Página: /modulos/recrutamento
 * Total: 12 testes
 */

import { test, expect } from '../fixtures';

test.describe('Dashboard Recrutamento', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/recrutamento', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard de recrutamento corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título Recrutamento e Selecao', async ({ page }) => {
    await expect(page.locator('h1').filter({ hasText: /Recrutamento/i }).first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - Vagas Abertas', async ({ page }) => {
    await expect(page.locator('text=Vagas Abertas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - Candidatos Ativos', async ({ page }) => {
    await expect(page.locator('text=Candidatos Ativos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - Candidaturas', async ({ page }) => {
    await expect(page.locator('text=Candidaturas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - Entrevistas Hoje', async ({ page }) => {
    await expect(page.locator('text=Entrevistas Hoje').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Vagas', async ({ page }) => {
    await expect(page.locator('text=Vagas').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Gerenciar vagas e posicoes abertas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Candidatos', async ({ page }) => {
    await expect(page.locator('text=Candidatos').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Base de candidatos cadastrados').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Candidaturas', async ({ page }) => {
    await expect(page.locator('text=Candidaturas').nth(1)).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Acompanhar candidaturas e etapas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Entrevistas', async ({ page }) => {
    await expect(page.locator('text=Entrevistas').nth(1)).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Agenda de entrevistas e avaliacoes').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar dados', async ({ page }) => {
    const refreshButton = page.locator('button').filter({ hasText: /Atualizar/i }).first();
    await expect(refreshButton).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir descrição do módulo', async ({ page }) => {
    await expect(page.locator('text=Gerencie vagas, candidatos, candidaturas e entrevistas').first()).toBeVisible({ timeout: 10000 });
  });
});
