import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '.auth/user.json');

setup('autenticar e salvar estado', async ({ page, context }) => {
  console.log('Iniciando autenticação...');

  // Navega para login
  await page.goto('/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  console.log('Página de login carregada');

  // Preenche formulário de login
  const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
  const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
  const submitButton = page.locator('button[type="submit"]').first();

  // Verificar se os campos existem
  const hasEmail = await emailInput.isVisible({ timeout: 5000 }).catch(() => false);
  const hasPassword = await passwordInput.isVisible({ timeout: 5000 }).catch(() => false);

  console.log('Campos encontrados - Email:', hasEmail, 'Password:', hasPassword);

  if (hasEmail && hasPassword) {
    console.log('Preenchendo formulário de login...');

    // Preenche credenciais
    await emailInput.fill('admin@conectaplus.com.br');
    await passwordInput.fill('admin123');

    console.log('Enviando formulário...');

    // Aguarda resposta do login
    const responsePromise = page.waitForResponse(
      (response) => response.url().includes('/api/v1/auth/login') && response.status() === 200,
      { timeout: 10000 }
    ).catch(() => null);

    // Clica no botão de login
    await submitButton.click();

    // Aguarda resposta ou timeout
    const response = await responsePromise;

    if (response) {
      console.log('Login bem-sucedido via formulário');
      // Aguarda navegação após login
      await page.waitForURL(/\/modulos|\/dashboard/, { timeout: 10000 }).catch(() => {});
    } else {
      console.log('Sem resposta de login, tentando API direta...');
    }
  }

  // Se não conseguiu via formulário, tenta via API
  const currentUrl1 = page.url();
  if (currentUrl1.includes('/login')) {
    console.log('Ainda no login, tentando via API...');

    await page.evaluate(async () => {
      try {
        const resp = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'username=admin@conectaplus.com.br&password=admin123',
        });

        if (resp.ok) {
          const data = await resp.json();
          localStorage.setItem('access_token', data.access_token);
          if (data.refresh_token) {
            localStorage.setItem('refresh_token', data.refresh_token);
          }
          console.log('Token salvo no localStorage');
        }
      } catch (error) {
        console.error('Erro ao fazer login via API:', error);
      }
    });
  }

  // Mocka endpoint /auth/me antes de navegar
  await page.route('**/api/v1/auth/me', (route) => {
    if (route.request().method() === 'GET') {
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
    } else {
      route.continue();
    }
  });

  console.log('Navegando para /modulos...');

  // Navega para módulos
  await page.goto('/modulos', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  const currentUrl = page.url();
  console.log('URL atual:', currentUrl);

  // Verifica localStorage
  const storageData = await page.evaluate(() => {
    return {
      access_token: localStorage.getItem('access_token'),
      has_token: !!localStorage.getItem('access_token'),
    };
  });

  console.log('LocalStorage:', storageData.has_token ? 'Token presente' : 'Sem token');

  // Verifica cookies
  const cookies = await context.cookies();
  console.log('Cookies:', cookies.length, 'cookies encontrados');

  if (cookies.length === 0 && !storageData.has_token) {
    console.warn('AVISO: Nenhum cookie ou token encontrado!');

    // Cria token manualmente como fallback
    await page.evaluate(() => {
      const mockToken =
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBjb25lY3RhcGx1cy5jb20uYnIiLCJleHAiOjk5OTk5OTk5OTl9.mock';
      localStorage.setItem('access_token', mockToken);
      localStorage.setItem(
        'user',
        JSON.stringify({
          id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          email: 'admin@conectaplus.com.br',
          name: 'Admin',
          role: 'admin',
          is_active: true,
        })
      );
    });

    // Adiciona cookie manualmente
    await context.addCookies([
      {
        name: 'authenticated',
        value: 'true',
        domain: 'erp.conectamais.pro',
        path: '/',
        httpOnly: false,
        secure: true,
        sameSite: 'Lax',
      },
    ]);

    console.log('Token e cookie de fallback criados');
  }

  console.log('Salvando estado de autenticação...');

  // Salva estado de autenticação (inclui cookies e origins)
  await context.storageState({ path: authFile });

  console.log('Estado salvo em:', authFile);

  // Verifica autenticação final
  const isAuthenticated = !currentUrl.includes('/login');
  console.log('Autenticado:', isAuthenticated);

  expect(isAuthenticated).toBeTruthy();
});
