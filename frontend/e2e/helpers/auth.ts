import { Page } from '@playwright/test';

/**
 * Injeta autenticação válida antes de qualquer navegação
 * Usa token JWT válido e mocka endpoint /auth/me
 */
export async function loginViaAPI(page: Page): Promise<void> {
  // Token JWT válido assinado com SECRET_KEY do backend (válido até 2055)
  const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBjb25lY3RhcGx1cy5jb20uYnIiLCJleHAiOjE3NzI2NTUyMzUsInVzZXJfaWQiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0ZW5hbnRfaWQiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJyb2xlIjoiYWRtaW4iLCJwZXJtaXNzaW9ucyI6WyIqIl19.lZ87J5aTHd9Ia3Gi1bKHOav2edxml12AtT6o_jf-umM';

  const userData = {
    id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    email: 'admin@conectaplus.com.br',
    name: 'Admin',
    role: 'admin',
    is_active: true,
  };

  // Mockar endpoint /auth/me para validação
  await page.route('**/api/v1/auth/**', (route) => {
    const method = route.request().method();
    const url = route.request().url();

    // GET /auth/me - retorna dados do usuário
    if (method === 'GET' && url.includes('/auth/me')) {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          email: 'admin@conectaplus.com.br',
          name: 'Admin',
          role: 'admin',
          is_active: true,
          permissions: ['*'],
          tenant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        }),
      });
    }
    // POST /auth/refresh - renova token
    else if (method === 'POST' && url.includes('/auth/refresh')) {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: validToken,
          refresh_token: 'refresh_' + validToken,
          token_type: 'bearer',
        }),
      });
    }
    // Outras rotas de auth continuam normalmente
    else {
      route.continue();
    }
  });

  // Injetar token no localStorage ANTES de qualquer navegação
  await page.addInitScript(({ token, user }) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
  }, { token: validToken, user: userData });
}
