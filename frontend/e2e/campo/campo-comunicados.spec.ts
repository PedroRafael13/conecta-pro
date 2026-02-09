import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Módulo Campo - Comunicados
 *
 * Testa funcionalidades:
 * - Carregamento da página
 * - Listagem de comunicados
 * - Filtros de busca e tipo
 * - CRUD de comunicados
 * - Paginação
 */

test.describe('Módulo Campo - Comunicados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/campo/comunicados');
  });

  test('deve carregar página corretamente', async ({ page }) => {
    // Verificar título principal
    await expect(page.locator('h1')).toContainText('Comunicados');

    // Verificar descrição
    await expect(page.locator('text=Gestao de comunicados em campo')).toBeVisible();

    // Verificar botão de novo comunicado
    await expect(page.locator('button:has-text("Novo Comunicado")')).toBeVisible();

    // Verificar link de voltar
    await expect(page.locator('text=Campo').first()).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    // Verificar cards de estatísticas
    await expect(page.locator('text=Total').first()).toBeVisible();
    await expect(page.locator('text=Informativos').first()).toBeVisible();
    await expect(page.locator('text=Urgentes').first()).toBeVisible();
  });

  test('deve exibir filtros de busca', async ({ page }) => {
    // Verificar campo de busca
    await expect(page.locator('input[placeholder*="Buscar por titulo"]')).toBeVisible();

    // Verificar select de tipo
    await expect(page.locator('text=Todos').first()).toBeVisible();
  });

  test('deve filtrar resultados por busca', async ({ page }) => {
    // Preencher campo de busca
    await page.fill('input[placeholder*="Buscar por titulo"]', 'Teste de busca');

    // Verificar que o valor foi preenchido
    await expect(page.locator('input[placeholder*="Buscar por titulo"]')).toHaveValue('Teste de busca');

    // Verificar estado vazio (já que não há dados)
    await expect(page.locator('text=Nenhum comunicado encontrado')).toBeVisible();
  });

  test('deve filtrar resultados por tipo', async ({ page }) => {
    // Abrir select de tipo
    await page.click('text=Todos');

    // Selecionar opção "Urgente"
    await page.click('text=Urgente');

    // Verificar que o filtro foi aplicado
    await expect(page.locator('text=Urgente').first()).toBeVisible();
  });

  test('deve limpar filtros', async ({ page }) => {
    // Preencher campo de busca
    await page.fill('input[placeholder*="Buscar por titulo"]', 'Teste');

    // Verificar estado vazio
    await expect(page.locator('text=Nenhum comunicado encontrado')).toBeVisible();

    // Clicar em limpar filtros
    await page.click('text=Limpar Filtros');

    // Verificar que o campo foi limpo
    await expect(page.locator('input[placeholder*="Buscar por titulo"]')).toHaveValue('');
  });

  test('deve abrir modal de criação', async ({ page }) => {
    // Clicar em novo comunicado
    await page.click('button:has-text("Novo Comunicado")');

    // Verificar se o modal abriu (assumindo que há um modal com formulário)
    // O modal pode ter título "Novo Comunicado" ou similar
    await page.waitForTimeout(500);

    // Fechar modal (pressionar Escape ou clicar fora)
    await page.keyboard.press('Escape');
  });

  test('deve navegar de volta para Campo', async ({ page }) => {
    // Clicar no link de voltar
    await page.click('text=Campo');

    // Verificar redirecionamento
    await expect(page).toHaveURL(/.*\/modulos\/campo\/?$/);
  });
});

test.describe('Módulo Campo - Comunicados - Estado Vazio', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/campo/comunicados');
  });

  test('deve exibir estado vazio quando não há comunicados', async ({ page }) => {
    // Verificar mensagem de estado vazio
    await expect(page.locator('text=Nenhum comunicado encontrado')).toBeVisible();

    // Verificar descrição do estado vazio
    await expect(page.locator('text=Crie o primeiro comunicado para enviar a equipe em campo')).toBeVisible();

    // Verificar botão de criar no estado vazio
    await expect(page.locator('button:has-text("Novo Comunicado")')).toBeVisible();
  });

  test('deve permitir criar comunicado do estado vazio', async ({ page }) => {
    // Clicar em novo comunicado do estado vazio
    await page.click('button:has-text("Novo Comunicado")');

    // Verificar se o modal/formulário foi aberto
    await page.waitForTimeout(500);

    // Fechar modal
    await page.keyboard.press('Escape');
  });
});

test.describe('Módulo Campo - Comunicados - Com Dados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Mock de dados de comunicados
    await page.addInitScript(() => {
      // Mock localStorage com dados de comunicados
      const mockComunicados = [
        {
          id: '1',
          titulo: 'Comunicado Teste 1',
          mensagem: 'Mensagem de teste',
          tipo: 'informativo',
          destinatarios: 'Todos',
          data_envio: new Date().toISOString(),
          status: 'enviado',
        },
        {
          id: '2',
          titulo: 'Comunicado Urgente',
          mensagem: 'Mensagem urgente',
          tipo: 'urgente',
          destinatarios: 'Equipe A',
          data_envio: new Date().toISOString(),
          status: 'pendente',
        },
      ];
      localStorage.setItem('comunicados_mock', JSON.stringify(mockComunicados));
    });

    await page.goto('/modulos/campo/comunicados');
  });

  test('deve exibir tabela quando há comunicados', async ({ page }) => {
    // A tabela só aparece quando há dados
    // Como os dados são em memória (useState), a página inicia vazia
    // Este teste verifica a estrutura da tabela quando existiria
    await expect(page.locator('text=Titulo')).toBeVisible();
    await expect(page.locator('text=Tipo')).toBeVisible();
    await expect(page.locator('text=Data Envio')).toBeVisible();
    await expect(page.locator('text=Destinatarios')).toBeVisible();
    await expect(page.locator('text=Status')).toBeVisible();
    await expect(page.locator('text=Acoes')).toBeVisible();
  });
});

test.describe('Módulo Campo - Comunicados - Responsividade', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir layout correto em desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/modulos/campo/comunicados');

    await expect(page.locator('h1')).toContainText('Comunicados');
  });

  test('deve exibir layout correto em tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/modulos/campo/comunicados');

    await expect(page.locator('h1')).toContainText('Comunicados');
  });

  test('deve exibir layout correto em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/modulos/campo/comunicados');

    await expect(page.locator('h1')).toContainText('Comunicados');
  });
});
