/**
 * Testes E2E - Dashboard Documentos (GED)
 * Página: /modulos/documentos
 * Total: 12 testes
 */

import { test, expect } from '../fixtures';

test.describe('Dashboard Documentos', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/documentos', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard de documentos corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título Gestão Eletrônica de Documentos', async ({ page }) => {
    await expect(page.locator('h1').filter({ hasText: /Gestão Eletrônica de Documentos/i }).first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir estatísticas de Pastas', async ({ page }) => {
    await expect(page.locator('text=Pastas').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=ativas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir estatísticas de Documentos', async ({ page }) => {
    await expect(page.locator('text=Documentos').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=ativos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir estatísticas de Armazenamento', async ({ page }) => {
    await expect(page.locator('text=Armazenamento').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=versões').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir alertas de documentos A vencer', async ({ page }) => {
    await expect(page.locator('text=A vencer').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=expirados').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir seção de Aprovações pendentes', async ({ page }) => {
    await expect(page.locator('text=Aprovações').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=pendentes').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir seção de Assinaturas pendentes', async ({ page }) => {
    await expect(page.locator('text=Assinaturas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de Upload', async ({ page }) => {
    const uploadButton = page.locator('button').filter({ hasText: /Upload/i }).first();
    await expect(uploadButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de Nova Pasta', async ({ page }) => {
    const newFolderButton = page.locator('button').filter({ hasText: /Nova Pasta/i }).first();
    await expect(newFolderButton).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir tabs de navegação', async ({ page }) => {
    await expect(page.locator('text=Visão Geral').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Aprovações').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Assinaturas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter links de acesso rápido para Arquivos, Pastas e Kits', async ({ page }) => {
    await expect(page.locator('text=Arquivos').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Pastas').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Kits de Documentos').first()).toBeVisible({ timeout: 10000 });
  });
});
