/**
 * Fixtures Playwright - Autenticação Global
 */

import { test as base } from '@playwright/test';

export const test = base.extend({
  page: async ({ page }, use) => {
    // Mock /auth/me em todas as páginas para evitar redirect para /login
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

    await use(page);
  },
});

export { expect } from '@playwright/test';
