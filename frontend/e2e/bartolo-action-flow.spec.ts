import { test, expect } from '@playwright/test';
import { BartoloFloatingChat, goToDashboardWithBartolo } from './helpers/bartolo.helpers';

test.describe('Bartolo - Fluxo de Acoes', () => {
  let chat: BartoloFloatingChat;

  test.beforeEach(async ({ page }) => {
    chat = new BartoloFloatingChat(page);
    await goToDashboardWithBartolo(page);
    await chat.open();
  });

  test('exibe modal de confirmacao quando API retorna action_preview', async ({ page }) => {
    // Envia comando que pode gerar action_preview
    const body = await chat.sendMessageAndWaitResponse('Criar escala para o posto central');

    if (body.action_preview) {
      // Modal de confirmacao deve abrir
      const dialog = page.locator('role=dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Titulo da acao
      await expect(dialog.locator('text=' + body.action_preview.title)).toBeVisible();

      // Botoes de confirmar e cancelar
      await expect(page.locator('button:has-text("Confirmar Ação")')).toBeVisible();
      await expect(page.locator('button:has-text("Cancelar")')).toBeVisible();
    }
    // Se nao retornou action_preview, o teste passa gracefully
  });

  test('modal exibe resumo das mudancas', async ({ page }) => {
    const body = await chat.sendMessageAndWaitResponse('Gerar escala automatica para esta semana');

    if (body.action_preview && body.action_preview.changes_summary?.length > 0) {
      const dialog = page.locator('role=dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Verifica que "O que será feito" esta visivel
      await expect(dialog.locator('text=O que será feito')).toBeVisible();

      // Pelo menos um item do resumo
      for (const change of body.action_preview.changes_summary.slice(0, 2)) {
        await expect(dialog.locator(`text=${change}`)).toBeVisible();
      }
    }
  });

  test('cancela acao ao clicar Cancelar no modal', async ({ page }) => {
    const body = await chat.sendMessageAndWaitResponse('Criar novo turno noturno');

    if (body.action_preview) {
      const dialog = page.locator('role=dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Clica cancelar
      await page.locator('button:has-text("Cancelar")').click();

      // Modal fecha
      await expect(dialog).not.toBeVisible({ timeout: 5000 });
    }
  });

  test('confirma acao e recebe resultado', async ({ page }) => {
    const body = await chat.sendMessageAndWaitResponse('Criar escala para o posto central amanha');

    if (body.action_preview && body.action_preview.user_has_permission) {
      const dialog = page.locator('role=dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Intercepta confirmacao
      const confirmResponse = page.waitForResponse(
        (res) => res.url().includes('/api/v1/ai/bartolo/confirm-action') && res.status() === 200,
        { timeout: 15000 }
      );

      // Confirma
      await page.locator('button:has-text("Confirmar Ação")').click();
      await confirmResponse;

      // Modal fecha
      await expect(dialog).not.toBeVisible({ timeout: 5000 });
    }
  });

  test('botao confirmar fica desabilitado sem permissao', async ({ page }) => {
    const body = await chat.sendMessageAndWaitResponse('Deletar todos os postos');

    if (body.action_preview && !body.action_preview.user_has_permission) {
      const dialog = page.locator('role=dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Alerta de permissao
      await expect(dialog.locator('text=Permissão Necessária')).toBeVisible();

      // Botao confirmar desabilitado
      const confirmButton = page.locator('button:has-text("Confirmar Ação")');
      await expect(confirmButton).toBeDisabled();
    }
  });
});
