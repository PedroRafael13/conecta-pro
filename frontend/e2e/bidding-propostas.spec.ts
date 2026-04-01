/**
 * Testes E2E - Propostas
 */

import { test, expect } from './fixtures';

test.describe('Propostas', () => {
  test('deve carregar página de propostas', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas');
    await expect(page.locator('h1')).toContainText('Propostas');
  });

  test('deve ter botão Nova Proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas');
    const novoButton = page.locator('button:has-text("Nova Proposta")').first();
    await expect(novoButton).toBeVisible();
  });

  test('deve ter filtros disponíveis', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas');
    await page.waitForLoadState('load');

    // Verificar presença de inputs de filtro
    const inputs = page.locator('input');
    await expect(inputs.first()).toBeVisible();
  });
});

test.describe('Contratos', () => {
  test('deve carregar página de contratos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos');
    await expect(page.locator('h1')).toContainText('Contratos');
  });

  test('deve exibir lista de contratos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos');
    await page.waitForLoadState('load');
  });
});

test.describe('Certidões', () => {
  test('deve carregar página de certidões', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await expect(page.locator('h1')).toContainText('Certidões');
  });

  test('deve ter botão Nova Certidão', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    const novoButton = page.locator('button:has-text("Nova Certidão"), button:has-text("Upload")').first();
    await expect(novoButton).toBeVisible();
  });
});

test.describe('Documentos', () => {
  test('deve carregar página de documentos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await expect(page.locator('h1')).toContainText('Documentos');
  });

  test('deve ter botão Upload Documento', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    const uploadButton = page.locator('button:has-text("Upload"), button:has-text("Novo")').first();
    await expect(uploadButton).toBeVisible();
  });
});
