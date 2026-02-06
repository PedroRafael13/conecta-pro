import { test, expect } from '@playwright/test';

test.describe('Operacional - Health Check', () => {
  test('deve acessar a página inicial', async ({ page }) => {
    await page.goto('/');
    expect(page).toBeTruthy();
  });

  test('deve verificar que a aplicação está rodando', async ({ page }) => {
    const response = await page.goto('/');
    expect(response?.status()).toBeLessThan(500);
  });
});
