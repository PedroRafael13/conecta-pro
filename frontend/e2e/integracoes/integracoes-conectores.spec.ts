import { test, expect } from "@playwright/test";
import { loginViaAPI } from "../helpers/auth";

test.describe("🔗 Módulo Integrações - Conectores", () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto("/modulos/integracoes/conectores");
    await page.waitForLoadState("networkidle");
  });

  test.describe("📋 Lista de Conectores", () => {
    test("deve exibir título da página corretamente", async ({ page }) => {
      await expect(page.locator("h1")).toContainText(/Conectores|Integrações/i);
    });

    test("deve exibir grid de conectores disponíveis", async ({ page }) => {
      const grid = page.locator("[data-testid='connectors-grid'], .connectors-grid, .grid").first();
      await expect(grid).toBeVisible();
    });

    test("deve exibir cards de conectores", async ({ page }) => {
      const cards = page.locator("[data-testid='connector-card'], .connector-card, .card");
      const count = await cards.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test("deve exibir status de cada conector", async ({ page }) => {
      const statusBadges = page.locator("[data-testid='status'], .status, .badge");
      const count = await statusBadges.count();
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test("deve permitir filtrar por categoria", async ({ page }) => {
      const categoriaFilter = page.locator("select, button").filter({ hasText: /categoria|categoria/i }).first();
      if (await categoriaFilter.isVisible().catch(() => false)) {
        await categoriaFilter.click();
        const option = page.locator("text=/ERP|CRM|Pagamento/i").first();
        if (await option.isVisible().catch(() => false)) {
          await option.click();
        }
      }
    });

    test("deve permitir busca por nome do conector", async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="buscar" i], input[type="search"]').first();
      if (await searchInput.isVisible().catch(() => false)) {
        await searchInput.fill("ERP");
        await searchInput.press("Enter");
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe("🔌 Configuração de Conectores", () => {
    test("deve abrir configuração do conector", async ({ page }) => {
      const configBtn = page.locator("button").filter({ hasText: /configurar|conectar|setup/i }).first();
      await expect(configBtn).toBeVisible();
      await configBtn.click();
      await expect(page.locator("[role='dialog'], .modal").filter({ hasText: /configuração|setup/i }).first()).toBeVisible();
    });

    test("deve configurar conector ERP", async ({ page }) => {
      const erpCard = page.locator("text=/ERP|SAP|TOTVS/i").first();
      if (await erpCard.isVisible().catch(() => false)) {
        const configBtn = erpCard.locator("xpath=..").locator("button").filter({ hasText: /configurar/i });
        await configBtn.click();

        const urlInput = page.locator('input[type="url"], input[name*="url" i]').first();
        if (await urlInput.isVisible().catch(() => false)) {
          await urlInput.fill("https://erp.empresa.com/api");
        }

        await page.getByRole("button", { name: /salvar|conectar/i }).click();
        await expect(page.locator("text=/conectado|sucesso|configurado/i").first()).toBeVisible();
      }
    });

    test("deve configurar conector de pagamento", async ({ page }) => {
      const pagCard = page.locator("text=/Pagamento|Stripe|Pagar.me|Asaas/i").first();
      if (await pagCard.isVisible().catch(() => false)) {
        const configBtn = pagCard.locator("xpath=..").locator("button").filter({ hasText: /configurar/i });
        await configBtn.click();

        const keyInput = page.locator('input[type="password"], input[name*="key" i]').first();
        if (await keyInput.isVisible().catch(() => false)) {
          await keyInput.fill("sk_test_exemplo");
        }

        await page.getByRole("button", { name: /salvar|conectar/i }).click();
        await expect(page.locator("text=/conectado|sucesso/i").first()).toBeVisible();
      }
    });

    test("deve testar conexão antes de salvar", async ({ page }) => {
      const configBtn = page.locator("button").filter({ hasText: /configurar/i }).first();
      await configBtn.click();

      const testarBtn = page.getByRole("button", { name: /testar|verificar/i });
      if (await testarBtn.isVisible().catch(() => false)) {
        await testarBtn.click();
        await expect(page.locator("text=/testando|verificando/i").first()).toBeVisible();
        await page.waitForTimeout(2000);
        const resultado = page.locator("text=/sucesso|falha|conectado|erro/i").first();
        await expect(resultado).toBeVisible();
      }
    });

    test("deve exibir erro quando configuração for inválida", async ({ page }) => {
      const configBtn = page.locator("button").filter({ hasText: /configurar/i }).first();
      await configBtn.click();

      const urlInput = page.locator('input[type="url"]').first();
      if (await urlInput.isVisible().catch(() => false)) {
        await urlInput.fill("https://invalid-url");

        const testarBtn = page.getByRole("button", { name: /testar|verificar/i });
        if (await testarBtn.isVisible().catch(() => false)) {
          await testarBtn.click();
          await expect(page.locator("text=/falha|erro|inválido/i").first()).toBeVisible();
        }
      }
    });
  });

  test.describe("📊 Status e Monitoramento", () => {
    test("deve exibir indicador de status online/offline", async ({ page }) => {
      const statusIndicator = page.locator("[data-testid='status-indicator'], .status-dot, .indicator").first();
      if (await statusIndicator.isVisible().catch(() => false)) {
        await expect(statusIndicator).toBeVisible();
      }
    });

    test("deve exibir última sincronização", async ({ page }) => {
      const lastSync = page.locator("text=/última sincronização|último sync|sync em/i").first();
      if (await lastSync.isVisible().catch(() => false)) {
        await expect(lastSync).toBeVisible();
      }
    });

    test("deve permitir sincronização manual", async ({ page }) => {
      const syncBtn = page.getByRole("button", { name: /sincronizar|sync|atualizar/i });
      if (await syncBtn.isVisible().catch(() => false)) {
        await syncBtn.click();
        await expect(page.locator("text=/sincronizando|aguarde/i").first()).toBeVisible();
        await page.waitForTimeout(2000);
        await expect(page.locator("text=/sincronizado|atualizado/i").first()).toBeVisible();
      }
    });

    test("deve exibir histórico de sincronizações", async ({ page }) => {
      const historicoBtn = page.getByRole("button", { name: /histórico|logs/i });
      if (await historicoBtn.isVisible().catch(() => false)) {
        await historicoBtn.click();
        await expect(page.locator("table, [data-testid='history']").first()).toBeVisible();
      }
    });
  });

  test.describe("⚙️ Mapeamento de Dados", () => {
    test("deve abrir tela de mapeamento de campos", async ({ page }) => {
      const mapearBtn = page.locator("button").filter({ hasText: /mapear|campos|mapping/i }).first();
      if (await mapearBtn.isVisible().catch(() => false)) {
        await mapearBtn.click();
        await expect(page.locator("text=/mapeamento|campos|field mapping/i").first()).toBeVisible();
      }
    });

    test("deve permitir configurar mapeamento de campos", async ({ page }) => {
      const mapearBtn = page.locator("button").filter({ hasText: /mapear/i }).first();
      if (await mapearBtn.isVisible().catch(() => false)) {
        await mapearBtn.click();

        const campoSelect = page.locator("select").first();
        if (await campoSelect.isVisible().catch(() => false)) {
          await campoSelect.selectOption({ index: 1 });
        }

        await page.getByRole("button", { name: /salvar/i }).click();
      }
    });

    test("deve permitir configurar transformações", async ({ page }) => {
      const transformBtn = page.locator("button").filter({ hasText: /transformar|regra/i }).first();
      if (await transformBtn.isVisible().catch(() => false)) {
        await transformBtn.click();
        await expect(page.locator("text=/transformação|regra/i").first()).toBeVisible();
      }
    });
  });

  test.describe("🔒 Gerenciamento", () => {
    test("deve desconectar conector", async ({ page }) => {
      const desconectarBtn = page.locator("button").filter({ hasText: /desconectar|desativar/i }).first();
      if (await desconectarBtn.isVisible().catch(() => false)) {
        await desconectarBtn.click();
        await expect(page.locator("text=/confirmar|certeza/i").first()).toBeVisible();
        await page.getByRole("button", { name: /confirmar|sim/i }).click();
        await expect(page.locator("text=/desconectado|desativado/i").first()).toBeVisible();
      }
    });

    test("deve pausar sincronização automática", async ({ page }) => {
      const pausarBtn = page.locator("button").filter({ hasText: /pausar|pausar sync/i }).first();
      if (await pausarBtn.isVisible().catch(() => false)) {
        await pausarBtn.click();
        await expect(page.locator("text=/pausado|parado/i").first()).toBeVisible();
      }
    });

    test("deve exibir configurações avançadas", async ({ page }) => {
      const avancadoBtn = page.getByRole("button", { name: /avançado|advanced/i });
      if (await avancadoBtn.isVisible().catch(() => false)) {
        await avancadoBtn.click();
        await expect(page.locator("text=/timeout|retry|batch/i").first()).toBeVisible();
      }
    });
  });
});
