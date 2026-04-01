/**
 * Testes E2E - Relatórios Operacional
 *
 * Testa funcionalidades do relatório operacional:
 * - Efetividade de postos
 * - Ocorrências
 * - Escala vs Realizado
 * - Absenteísmo
 * - Exportação
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock data para relatório operacional
const mockExecutiveSummary = {
  escalas_ativas: 42,
  ocorrencias: 15,
  sla_cumprido: 0.94,
  postos_ativos: 28,
  items: [
    {
      titulo: 'Escalas do Dia',
      valor: '38',
      descricao: 'Escalas ativas hoje',
    },
    {
      titulo: 'Ocorrências Críticas',
      valor: '3',
      descricao: 'Requerem atenção imediata',
    },
    {
      titulo: 'Absenteísmo',
      valor: '4.2%',
      descricao: 'Média do último mês',
    },
    {
      titulo: 'Efetividade',
      valor: '96.8%',
      descricao: 'Média de cumprimento',
    },
    {
      titulo: 'Turnos Completos',
      valor: '156',
      descricao: 'Últimos 7 dias',
    },
    {
      titulo: 'Substituições',
      valor: '12',
      descricao: 'Efetuadas hoje',
    },
  ],
};

const mockMonitoringData = {
  active_scales: 42,
  incidents: 15,
  sla_compliance: 0.94,
  active_posts: 28,
  models: [
    {
      id: 'monitor-001',
      nome: 'Posto Alpha - Entrada Principal',
      status: 'ativo',
      metricas: { efetividade: 98, presencas: 45, faltas: 1 },
      ultima_atualizacao: '2025-02-05T14:30:00Z',
    },
    {
      id: 'monitor-002',
      nome: 'Posto Beta - Estacionamento',
      status: 'alerta',
      metricas: { efetividade: 85, presencas: 38, faltas: 6 },
      ultima_atualizacao: '2025-02-05T13:00:00Z',
    },
    {
      id: 'monitor-003',
      nome: 'Posto Gamma - Vigia Noturno',
      status: 'critico',
      metricas: { efetividade: 65, presencas: 26, faltas: 12 },
      ultima_atualizacao: '2025-02-05T12:00:00Z',
    },
    {
      id: 'monitor-004',
      nome: 'Posto Delta - Ronda',
      status: 'ativo',
      metricas: { efetividade: 95, presencas: 42, faltas: 2 },
      ultima_atualizacao: '2025-02-05T14:15:00Z',
    },
  ],
};

test.describe('⚙️ Relatórios - Operacional', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Mock endpoints
    await page.route('**/api/v1/analytics/executive-summary**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutiveSummary),
      });
    });

    await page.route('**/api/v1/analytics/monitoring**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMonitoringData),
      });
    });

    await page.goto('/modulos/relatorios/operacional');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO
  // ==========================================

  test('deve carregar a página de relatório operacional', async ({ page }) => {
    const heading = page.locator('h1');
    await expect(heading).toContainText('Relatório Operacional');
  });

  test('deve exibir descrição da página', async ({ page }) => {
    await expect(page.locator('text=Escalas, ocorrências e monitoramento')).toBeVisible();
  });

  test('deve exibir seletor de período', async ({ page }) => {
    const periodoSelect = page.locator('[role="combobox"]').first();
    await expect(periodoSelect).toBeVisible();
  });

  // ==========================================
  // TESTES DE EFETIVIDADE DE POSTOS
  // ==========================================

  test('deve exibir estatísticas principais nos cards', async ({ page }) => {
    await expect(page.locator('text=Escalas Ativas')).toBeVisible();
    await expect(page.locator('text=Ocorrências')).toBeVisible();
    await expect(page.locator('text=SLA Cumprido')).toBeVisible();
    await expect(page.locator('text=Postos Ativos')).toBeVisible();
  });

  test('deve exibir quantidade de escalas ativas', async ({ page }) => {
    await expect(page.locator('text=42').first()).toBeVisible();
  });

  test('deve exibir percentual de SLA cumprido', async ({ page }) => {
    const slaValue = page.locator('text=/94\\.?0?%/');
    await expect(slaValue).toBeVisible();
  });

  test('deve exibir seção de Monitoramento', async ({ page }) => {
    await expect(page.locator('text=Monitoramento')).toBeVisible();
  });

  // ==========================================
  // TESTES DE OCORRÊNCIAS
  // ==========================================

  test('deve exibir quantidade de ocorrências', async ({ page }) => {
    await expect(page.locator('text=15').first()).toBeVisible();
  });

  test('deve exibir tabela de monitoramento', async ({ page }) => {
    await expect(page.locator('th:has-text("Nome")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
    await expect(page.locator('th:has-text("Métricas")')).toBeVisible();
    await expect(page.locator('th:has-text("Última Atualização")')).toBeVisible();
  });

  test('deve exibir postos com status Ativo', async ({ page }) => {
    const ativoBadge = page.locator('text=Ativo').first();
    await expect(ativoBadge).toBeVisible();
  });

  test('deve exibir postos com status de Alerta', async ({ page }) => {
    const alertaBadge = page.locator('text=Alerta').first();
    await expect(alertaBadge).toBeVisible();
  });

  test('deve exibir postos com status Crítico', async ({ page }) => {
    const criticoBadge = page.locator('text=Crítico').first();
    await expect(criticoBadge).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESCALA VS REALIZADO
  // ==========================================

  test('deve exibir seção de Resumo Executivo', async ({ page }) => {
    await expect(page.locator('text=Resumo Executivo')).toBeVisible();
  });

  test('deve exibir cards de resumo executivo', async ({ page }) => {
    await expect(page.locator('text=Escalas do Dia')).toBeVisible();
    await expect(page.locator('text=Ocorrências Críticas')).toBeVisible();
    await expect(page.locator('text=Absenteísmo')).toBeVisible();
    await expect(page.locator('text=Efetividade')).toBeVisible();
  });

  test('deve exibir dados de turnos completos', async ({ page }) => {
    await expect(page.locator('text=Turnos Completos')).toBeVisible();
    await expect(page.locator('text=156')).toBeVisible();
  });

  test('deve exibir dados de substituições', async ({ page }) => {
    await expect(page.locator('text=Substituições')).toBeVisible();
    await expect(page.locator('text=12')).toBeVisible();
  });

  // ==========================================
  // TESTES DE ABSENTEÍSMO
  // ==========================================

  test('deve exibir percentual de absenteísmo', async ({ page }) => {
    const absenteismoValue = page.locator('text=/4\\.2%/');
    await expect(absenteismoValue).toBeVisible();
  });

  test('deve exibir métricas de efetividade', async ({ page }) => {
    const efetividadeValue = page.locator('text=/96\\.8%/');
    await expect(efetividadeValue).toBeVisible();
  });

  // ==========================================
  // TESTES DE FILTROS E EXPORTAÇÃO
  // ==========================================

  test('deve permitir alterar período para 7 dias', async ({ page }) => {
    const periodoSelect = page.locator('[role="combobox"]').first();
    await periodoSelect.click();

    await page.locator('[role="option"]:has-text("7 dias")').click();
    await page.waitForTimeout(500);

    // A página deve continuar funcionando
    await expect(page.locator('h1')).toContainText('Relatório Operacional');
  });

  test('deve permitir atualizar dados operacionais', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await expect(refreshButton).toBeVisible();
    await refreshButton.click();

    await page.waitForTimeout(500);
    await expect(page.locator('table')).toBeVisible();
  });

  test('deve navegar de volta para módulo de relatórios', async ({ page }) => {
    const backButton = page.locator('button:has-text("Relatórios")');
    await expect(backButton).toBeVisible();
    await backButton.click();
    await page.waitForTimeout(1000);

    expect(page.url()).toContain('/modulos/relatorios');
  });
});
