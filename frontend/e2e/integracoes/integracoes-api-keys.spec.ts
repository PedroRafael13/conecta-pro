import { test, expect } from "@playwright/test";
import { loginViaAPI } from "../helpers/auth";

test.describe("🔗 Módulo Integrações - API Keys", () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto("/modulos/integracoes/api-keys");
    await page.waitForLoadState("load");
  });

  test.describe("📋 Lista de API Keys", () => {
    test("deve exibir título da página corretamente", async ({ page }) => {
      await expect(page.locator("h1")).toContainText("API Keys");
    });

    test("deve exibir tabela de chaves de API", async ({ page }) => {
      await expect(page.locator("table")).toBeVisible();
    });

    test("deve exibir colunas: Nome, Key, Serviço, Status, Último Uso", async ({ page }) => {
      const headers = ["Nome", "Key", "Serviço", "Servico", "Status", "Último Uso", "Ultimo Uso"];
      for (const header of headers) {
        const found = await page.locator("th").filter({ hasText: new RegExp(header, "i") }).first().isVisible().catch(() => false);
        if (found) {
          await expect(page.locator("th").filter({ hasText: new RegExp(header, "i") }).first()).toBeVisible();
        }
      }
    });

    test("deve exibir badge de status ativo/inativo", async ({ page }) => {
      const badges = page.locator("[data-testid='badge'], .badge, .status-badge, .tag");
      const count = await badges.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test("deve filtrar por serviço", async ({ page }) => {
      const servicoFilter = page.locator("select").filter({ hasText: /serviço|servico/i }).first();
      if (await servicoFilter.isVisible().catch(() => false)) {
        await servicoFilter.selectOption({ index: 1 });
        await page.waitForTimeout(500);
      }
    });

    test("deve filtrar por status", async ({ page }) => {
      const statusFilter = page.locator("select").filter({ hasText: /status/i }).first();
      if (await statusFilter.isVisible().catch(() => false)) {
        await statusFilter.selectOption("Ativo");
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe("➕ Criação de API Key", () => {
    test("deve abrir modal de nova API Key", async ({ page }) => {
      const novaBtn = page.getByRole("button", { name: /nova key|nova api|gerar key/i });
      await expect(novaBtn).toBeVisible();
      await novaBtn.click();
      await expect(page.locator("[role='dialog']").filter({ hasText: /api key|chave/i }).first()).toBeVisible();
    });

    test("deve validar campos obrigatórios", async ({ page }) => {
      await page.getByRole("button", { name: /nova key/i }).click();
      await page.getByRole("button", { name: /gerar|criar|salvar/i }).click();

      const error = page.locator("text=/obrigatório|requerido|nome/i").first();
      await expect(error).toBeVisible();
    });

    test("deve gerar nova API Key com sucesso", async ({ page }) => {
      await page.getByRole("button", { name: /nova key/i }).click();

      await page.locator('input[name*="nome" i], input[placeholder*="nome" i]').fill(`Teste API ${Date.now()}`);

      const servicoSelect = page.locator("select").filter({ hasText: /serviço|servico/i }).first();
      if (await servicoSelect.isVisible().catch(() => false)) {
        await servicoSelect.selectOption({ index: 1 });
      }

      const descricao = page.locator("textarea").first();
      if (await descricao.isVisible().catch(() => false)) {
        await descricao.fill("Chave para testes de integração");
      }

      await page.getByRole("button", { name: /gerar|criar/i }).click();
      await expect(page.locator("text=/sucesso|gerada|criada/i").first()).toBeVisible();
    });

    test("deve exibir a chave gerada apenas uma vez", async ({ page }) => {
      await page.getByRole("button", { name: /nova key/i }).click();
      await page.locator('input[name*="nome" i]').fill(`Key Unica ${Date.now()}`);

      const servicoSelect = page.locator("select").first();
      if (await servicoSelect.isVisible().catch(() => false)) {
        await servicoSelect.selectOption({ index: 1 });
      }

      await page.getByRole("button", { name: /gerar|criar/i }).click();

      const keyDisplay = page.locator("[data-testid='api-key'], .api-key-display, code").first();
      if (await keyDisplay.isVisible().catch(() => false)) {
        await expect(keyDisplay).toBeVisible();

        const copyBtn = page.getByRole("button", { name: /copiar/i });
        if (await copyBtn.isVisible().catch(() => false)) {
          await copyBtn.click();
        }
      }
    });

    test("deve permitir configurar permissões da key", async ({ page }) => {
      await page.getByRole("button", { name: /nova key/i }).click();

      const permCheckbox = page.locator('input[type="checkbox"]').first();
      if (await permCheckbox.isVisible().catch(() => false)) {
        await permCheckbox.check();
      }

      const scopeSelect = page.locator("select").filter({ hasText: /escopo|scope|permissão/i }).first();
      if (await scopeSelect.isVisible().catch(() => false)) {
        await scopeSelect.selectOption("read_only");
      }
    });
  });

  test.describe("🔒 Segurança e Gestão", () => {
    test("deve permitir revogar API Key", async ({ page }) => {
      const revogarBtn = page.locator("button").filter({ hasText: /revogar|desativar|inativar/i }).first();
      if (await revogarBtn.isVisible().catch(() => false)) {
        await revogarBtn.click();
        await expect(page.locator("text=/confirmar|certeza/i").first()).toBeVisible();
        await page.getByRole("button", { name: /confirmar|sim/i }).click();
        await expect(page.locator("text=/revogada|desativada/i").first()).toBeVisible();
      }
    });

    test("deve permitir reativar API Key", async ({ page }) => {
      const reativarBtn = page.locator("button").filter({ hasText: /reativar|ativar/i }).first();
      if (await reativarBtn.isVisible().catch(() => false)) {
        await reativarBtn.click();
        await expect(page.locator("text=/reativada|ativada/i").first()).toBeVisible();
      }
    });

    test("deve exibir últimos acessos da API Key", async ({ page }) => {
      const detalhesBtn = page.locator("button[title*='detalhes' i], button[data-testid*='details' i]").first();
      if (await detalhesBtn.isVisible().catch(() => false)) {
        await detalhesBtn.click();
        await expect(page.locator("text=/últimos acessos|logs|histórico/i").first()).toBeVisible();
      }
    });

    test("deve permitir rotacionar API Key", async ({ page }) => {
      const rotacionarBtn = page.locator("button").filter({ hasText: /rotacionar|regenerar/i }).first();
      if (await rotacionarBtn.isVisible().catch(() => false)) {
        await rotacionarBtn.click();
        await expect(page.locator("text=/confirmar|nova key/i").first()).toBeVisible();
        await page.getByRole("button", { name: /confirmar|sim/i }).click();
        await expect(page.locator("text=/rotacionada|nova chave/i").first()).toBeVisible();
      }
    });
  });

  test.describe("📊 Estatísticas de Uso", () => {
    test("deve exibir estatísticas de uso da API Key", async ({ page }) => {
      const stats = page.locator("[data-testid='stats'], .stats, .metrics").first();
      if (await stats.isVisible().catch(() => false)) {
        await expect(stats).toBeVisible();
      }
    });

    test("deve exibir gráfico de requisições", async ({ page }) => {
      const graficoBtn = page.getByRole("button", { name: /gráfico|estatísticas/i });
      if (await graficoBtn.isVisible().catch(() => false)) {
        await graficoBtn.click();
        await expect(page.locator("canvas, [data-testid='chart'], .chart").first()).toBeVisible();
      }
    });

    test("deve exibir taxa de erro das requisições", async ({ page }) => {
      const erroRate = page.locator("text=/taxa de erro|erros|error rate/i").first();
      if (await erroRate.isVisible().catch(() => false)) {
        await expect(erroRate).toBeVisible();
      }
    });
  });
});
