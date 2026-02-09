# GAP Analysis - Testes E2E

## Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de páginas** | 121 |
| **Testes E2E existentes** | 86 |
| **Páginas COM teste** | 77 |
| **Páginas SEM teste** | 44 |
| **Cobertura atual** | **63.6%** |

---

## 📊 Páginas com Teste E2E (77 páginas)

### Módulos com Cobertura Completa ou Parcial

<details>
<summary><strong>✅ Financeiro (14 páginas cobertas)</strong></summary>

| Rota | Tipo |
|------|------|
| `/modulos/financeiro` | Dashboard |
| `/modulos/financeiro/clientes` | List |
| `/modulos/financeiro/compras` | List |
| `/modulos/financeiro/conciliacao` | List |
| `/modulos/financeiro/contabilidade` | List |
| `/modulos/financeiro/contas-pagar` | List |
| `/modulos/financeiro/contas-receber` | List |
| `/modulos/financeiro/custeio` | List |
| `/modulos/financeiro/estoque` | List |
| `/modulos/financeiro/faturamento` | List |
| `/modulos/financeiro/fiscal` | List |
| `/modulos/financeiro/fluxo-caixa` | List |
| `/modulos/financeiro/fornecedores` | List |

**Arquivos de teste:**
- `financial-dashboard.spec.ts`
- `financial-clientes.spec.ts`
- `financial-compras.spec.ts`
- `financial-conciliacao.spec.ts`
- `financial-contabilidade.spec.ts`
- `financial-contas-pagar.spec.ts`
- `financial-contas-receber.spec.ts`
- `financial-custeio.spec.ts`
- `financial-estoque.spec.ts`
- `financial-faturamento.spec.ts`
- `financial-fiscal.spec.ts`
- `financial-fluxo-caixa.spec.ts`
- `financial-fornecedores.spec.ts`

</details>

<details>
<summary><strong>✅ CRM (6 páginas cobertas)</strong></summary>

| Rota | Tipo |
|------|------|
| `/modulos/crm/clientes` | List/CRUD |
| `/modulos/crm/contatos` | List |
| `/modulos/crm/leads` | List |
| `/modulos/crm/oportunidades` | List |
| `/modulos/crm/propostas` | List |

**Arquivos de teste:**
- `crm/clientes-create.spec.ts`
- `crm/clientes-edit.spec.ts`
- `crm/clientes-list.spec.ts`
- `crm/contatos.spec.ts`
- `crm/leads.spec.ts`
- `crm/oportunidades.spec.ts`
- `crm/propostas.spec.ts`

</details>

<details>
<summary><strong>✅ Operacional (9 páginas cobertas)</strong></summary>

| Rota | Tipo |
|------|------|
| `/modulos/operacional/colaboradores` | List |
| `/modulos/operacional/comunicados` | List |
| `/modulos/operacional/diaristas` | List |
| `/modulos/operacional/diaristas/escala` | Form |
| `/modulos/operacional/diaristas/fechamento` | Form |
| `/modulos/operacional/escalas` | List |
| `/modulos/operacional/ocorrencias` | List |
| `/modulos/operacional/postos` | List |
| `/modulos/operacional/rondas` | List |
| `/modulos/operacional/turnos` | List |

**Arquivos de teste:**
- `operacional/operacional-colaboradores.spec.ts`
- `operacional/operacional-comunicados.spec.ts`
- `operacional/operacional-diaristas.spec.ts`
- `operacional/operacional-rondas.spec.ts`
- `operacional/operacional-turnos.spec.ts`
- `operacional-escalas.spec.ts`
- `operacional-ocorrencias.spec.ts`
- `operacional-postos.spec.ts`

</details>

<details>
<summary><strong>✅ Fiscal (4 páginas cobertas)</strong></summary>

| Rota | Tipo |
|------|------|
| `/modulos/fiscal` | Dashboard |
| `/modulos/fiscal/certidoes` | List |
| `/modulos/fiscal/esocial` | Form |
| `/modulos/fiscal/nfse` | Form |

**Arquivos de teste:**
- `fiscal-dashboard.spec.ts`
- `fiscal-certidoes.spec.ts`
- `fiscal-esocial.spec.ts`
- `fiscal-nfse.spec.ts`

</details>

<details>
<summary><strong>✅ Licitações (3 páginas cobertas)</strong></summary>

| Rota | Tipo |
|------|------|
| `/modulos/licitacoes` | Dashboard |
| `/modulos/licitacoes/editais` | List |
| `/modulos/licitacoes/propostas` | List |

**Arquivos de teste:**
- `bidding-dashboard.spec.ts`
- `bidding-editais-crud.spec.ts`
- `bidding-propostas.spec.ts`

</details>

<details>
<summary><strong>✅ Outros Módulos Cobertos (41 páginas)</strong></summary>

| Módulo | Páginas Cobertas |
|--------|-----------------|
| **Configurações** | 4 (sistema, feature-flags, templates, tenants) |
| **Documentos** | 3 (arquivos, kits, pastas) |
| **Equipamentos** | 3 (comodatos, manutenções, patrimônio) |
| **Integrações** | 5 (api-keys, conectores, logs, solides, webhooks) |
| **Recrutamento** | 4 (candidatos, candidaturas, entrevistas, vagas) |
| **Reembolso** | 1 (aprovações) |
| **Saúde Ocupacional** | 3 (epi, exames, riscos) |
| **Segurança** | 5 (auditoria, consentimento, criptografia, esquecimento, mascaramento, pia-dpia) |
| **Serviços** | 3 (agendamentos, contratos, ordens) |
| **Agendador** | 2 (execuções, tarefas) |
| **Analytics** | 1 (dashboard) |
| **Assistente** | 1 (página principal + 8 testes de features) |
| **Automações** | 2 (execuções, workflows) |
| **Campo** | 2 (checkin, monitoramento) |
| **Dashboard** | 1 (principal) |
| **Login** | 1 (autenticação) |

</details>

---

## ⚠️ Páginas SEM Teste E2E (44 páginas)

### 🔴 Prioridade P0 - Críticas (18 páginas)

> **Módulos financeiros, fiscais e operacionais sem cobertura**

| # | Rota | Módulo | Tipo | Teste Sugerido |
|---|------|--------|------|----------------|
| 1 | `/modulos/fiscal/dctfweb` | Fiscal | form | `modulos-fiscal-dctfweb.spec.ts` |
| 2 | `/modulos/fiscal/reinf` | Fiscal | form | `modulos-fiscal-reinf.spec.ts` |
| 3 | `/modulos/fiscal/sped` | Fiscal | form | `modulos-fiscal-sped.spec.ts` |
| 4 | `/modulos/licitacoes/certidoes` | Licitações | list | `modulos-licitacoes-certidoes.spec.ts` |
| 5 | `/modulos/licitacoes/contratos` | Licitações | list | `modulos-licitacoes-contratos.spec.ts` |
| 6 | `/modulos/licitacoes/documentos` | Licitações | list | `modulos-licitacoes-documentos.spec.ts` |
| 7 | `/modulos/operacional` | Operacional | dashboard | `modulos-operacional.spec.ts` |
| 8 | `/modulos/operacional/agentes` | Operacional | list | `modulos-operacional-agentes.spec.ts` |
| 9 | `/modulos/operacional/alocacoes` | Operacional | list | `modulos-operacional-alocacoes.spec.ts` |
| 10 | `/modulos/operacional/banco-horas` | Operacional | list | `modulos-operacional-banco-horas.spec.ts` |
| 11 | `/modulos/operacional/disciplinar` | Operacional | list | `modulos-operacional-disciplinar.spec.ts` |
| 12 | `/modulos/operacional/escalas/templates` | Operacional | list | `modulos-operacional-escalas-templates.spec.ts` |
| 13 | `/modulos/operacional/medidas-administrativas` | Operacional | list | `modulos-operacional-medidas-administrativas.spec.ts` |
| 14 | `/modulos/operacional/notificacoes` | Operacional | list | `modulos-operacional-notificacoes.spec.ts` |
| 15 | `/modulos/operacional/reembolsos` | Operacional | list | `modulos-operacional-reembolsos.spec.ts` |
| 16 | `/modulos/operacional/relatorios` | Operacional | list | `modulos-operacional-relatorios.spec.ts` |
| 17 | `/modulos/operacional/substituicoes` | Operacional | list | `modulos-operacional-substituicoes.spec.ts` |
| 18 | `/modulos/recrutamento` | Recrutamento | dashboard | `modulos-recrutamento.spec.ts` |

### 🟡 Prioridade P1 - Importantes (10 páginas)

> **Módulos secundários importantes**

| # | Rota | Módulo | Tipo | Teste Sugerido |
|---|------|--------|------|----------------|
| 1 | `/modulos/integracoes` | Integrações | dashboard | `modulos-integracoes.spec.ts` |
| 2 | `/modulos/integracoes/sync` | Integrações | list | `modulos-integracoes-sync.spec.ts` |
| 3 | `/modulos/reembolso` | Reembolso | dashboard | `modulos-reembolso.spec.ts` |
| 4 | `/modulos/relatorios` | Relatórios | dashboard | `modulos-relatorios.spec.ts` |
| 5 | `/modulos/relatorios/comercial` | Relatórios | report | `modulos-relatorios-comercial.spec.ts` |
| 6 | `/modulos/relatorios/dashboards` | Relatórios | dashboard | `modulos-relatorios-dashboards.spec.ts` |
| 7 | `/modulos/relatorios/financeiro` | Relatórios | report | `modulos-relatorios-financeiro.spec.ts` |
| 8 | `/modulos/relatorios/operacional` | Relatórios | report | `modulos-relatorios-operacional.spec.ts` |
| 9 | `/modulos/saude-ocupacional` | Saúde Ocupacional | dashboard | `modulos-saude-ocupacional.spec.ts` |
| 10 | `/modulos/seguranca` | Segurança | dashboard | `modulos-seguranca.spec.ts` |

### 🟢 Prioridade P2 - Complementares (16 páginas)

> **Dashboards de módulos e páginas de configuração**

| # | Rota | Módulo | Tipo | Teste Sugerido |
|---|------|--------|------|----------------|
| 1 | `/` | Sistema | home | `.spec.ts` |
| 2 | `/modulos/agendador` | Agendador | list | `modulos-agendador.spec.ts` |
| 3 | `/modulos/automacoes` | Automações | list | `modulos-automacoes.spec.ts` |
| 4 | `/modulos/campo` | Campo | dashboard | `modulos-campo.spec.ts` |
| 5 | `/modulos/campo/comunicados` | Campo | list | `modulos-campo-comunicados.spec.ts` |
| 6 | `/modulos/configuracoes` | Configurações | dashboard | `modulos-configuracoes.spec.ts` |
| 7 | `/modulos/crm` | CRM | dashboard | `modulos-crm.spec.ts` |
| 8 | `/modulos/documentos` | Documentos | dashboard | `modulos-documentos.spec.ts` |
| 9 | `/modulos/equipamentos` | Equipamentos | dashboard | `modulos-equipamentos.spec.ts` |
| 10 | `/modulos/licitacoes/contratos/*` | Licitações | detail | `modulos-licitacoes-contratos-detail.spec.ts` |
| 11 | `/modulos/licitacoes/editais/*` | Licitações | detail | `modulos-licitacoes-editais-detail.spec.ts` |
| 12 | `/modulos/licitacoes/propostas/*` | Licitações | detail | `modulos-licitacoes-propostas-detail.spec.ts` |
| 13 | `/modulos/openclaw` | OpenClaw | dashboard | `modulos-openclaw.spec.ts` |
| 14 | `/modulos/operacional/escalas/*` | Operacional | detail | `modulos-operacional-escalas-detail.spec.ts` |
| 15 | `/modulos/servicos` | Serviços | dashboard | `modulos-servicos.spec.ts` |
| 16 | `/offline` | Sistema | page | `offline.spec.ts` |

---

## 🔌 APIs por Módulo (Endpoints que precisam ser mockados)

### Módulo Fiscal (Obrigatórios P0)
```typescript
// fiscal-dctfweb.spec.ts
const mockAPIs = {
  'GET /api/fiscal/dctfweb': { status: 200, data: { ... } },
  'POST /api/fiscal/dctfweb': { status: 201, data: { ... } },
  'GET /api/fiscal/dctfweb/:id': { status: 200, data: { ... } },
};

// fiscal-reinf.spec.ts
const mockAPIs = {
  'GET /api/fiscal/reinf': { status: 200, data: { ... } },
  'POST /api/fiscal/reinf': { status: 201, data: { ... } },
};

// fiscal-sped.spec.ts
const mockAPIs = {
  'GET /api/fiscal/sped': { status: 200, data: { ... } },
  'POST /api/fiscal/sped': { status: 201, data: { ... } },
};
```

### Módulo Operacional (Obrigatórios P0)
```typescript
// operacional-agentes.spec.ts
const mockAPIs = {
  'GET /api/operacional/agentes': { status: 200, data: [...] },
  'POST /api/operacional/agentes': { status: 201, data: { ... } },
  'PUT /api/operacional/agentes/:id': { status: 200, data: { ... } },
  'DELETE /api/operacional/agentes/:id': { status: 204 },
};

// operacional-banco-horas.spec.ts
const mockAPIs = {
  'GET /api/operacional/banco-horas': { status: 200, data: [...] },
  'POST /api/operacional/banco-horas/lancamento': { status: 201 },
};

// operacional-escalas-detail.spec.ts
const mockAPIs = {
  'GET /api/operacional/escalas/:id': { status: 200, data: { ... } },
  'PUT /api/operacional/escalas/:id': { status: 200, data: { ... } },
};
```

### Módulo Licitações (Obrigatórios P0)
```typescript
// licitacoes-contratos.spec.ts
const mockAPIs = {
  'GET /api/licitacoes/contratos': { status: 200, data: [...] },
  'POST /api/licitacoes/contratos': { status: 201, data: { ... } },
  'GET /api/licitacoes/contratos/:id': { status: 200, data: { ... } },
  'PUT /api/licitacoes/contratos/:id': { status: 200, data: { ... } },
};

// licitacoes-certidoes.spec.ts
const mockAPIs = {
  'GET /api/licitacoes/certidoes': { status: 200, data: [...] },
  'POST /api/licitacoes/certidoes/verificar': { status: 200, data: { ... } },
};
```

### Módulo Reembolso (Importante P1)
```typescript
// reembolso-dashboard.spec.ts
const mockAPIs = {
  'GET /api/reembolso': { status: 200, data: { ... } },
  'GET /api/reembolso/dashboard': { status: 200, data: { ... } },
};
```

### Módulo Relatórios (Importante P1)
```typescript
// relatorios-comercial.spec.ts
const mockAPIs = {
  'GET /api/relatorios/comercial': { status: 200, data: [...] },
  'POST /api/relatorios/comercial/export': { status: 200, blob: ... },
};

// relatorios-financeiro.spec.ts
const mockAPIs = {
  'GET /api/relatorios/financeiro': { status: 200, data: [...] },
};
```

### Módulo Segurança (Importante P1)
```typescript
// seguranca-dashboard.spec.ts
const mockAPIs = {
  'GET /api/seguranca': { status: 200, data: { ... } },
  'GET /api/seguranca/consentimentos': { status: 200, data: [...] },
};
```

### Módulo Integrações (Importante P1)
```typescript
// integracoes-sync.spec.ts
const mockAPIs = {
  'GET /api/integracoes/sync': { status: 200, data: { ... } },
  'POST /api/integracoes/sync/executar': { status: 200 },
};
```

---

## 📋 Plano de Ação

### Fase 1: Páginas P0 (Semanas 1-2) - {len(p0_sem_teste)} testes
Criar testes E2E para todas as páginas críticas sem cobertura:
- [ ] `fiscal-dctfweb.spec.ts` → `/modulos/fiscal/dctfweb`
- [ ] `fiscal-reinf.spec.ts` → `/modulos/fiscal/reinf`
- [ ] `fiscal-sped.spec.ts` → `/modulos/fiscal/sped`
- [ ] `licitacoes-certidoes.spec.ts` → `/modulos/licitacoes/certidoes`
- [ ] `licitacoes-contratos.spec.ts` → `/modulos/licitacoes/contratos`
- [ ] `licitacoes-documentos.spec.ts` → `/modulos/licitacoes/documentos`
- [ ] `operacional.spec.ts` → `/modulos/operacional`
- [ ] `operacional-agentes.spec.ts` → `/modulos/operacional/agentes`
- [ ] `operacional-alocacoes.spec.ts` → `/modulos/operacional/alocacoes`
- [ ] `operacional-banco-horas.spec.ts` → `/modulos/operacional/banco-horas`
- [ ] `operacional-disciplinar.spec.ts` → `/modulos/operacional/disciplinar`
- [ ] `operacional-escalas-templates.spec.ts` → `/modulos/operacional/escalas/templates`
- [ ] `operacional-medidas-administrativas.spec.ts` → `/modulos/operacional/medidas-administrativas`
- [ ] `operacional-notificacoes.spec.ts` → `/modulos/operacional/notificacoes`
- [ ] `operacional-reembolsos.spec.ts` → `/modulos/operacional/reembolsos`
- [ ] `operacional-relatorios.spec.ts` → `/modulos/operacional/relatorios`
- [ ] `operacional-substituicoes.spec.ts` → `/modulos/operacional/substituicoes`
- [ ] `recrutamento.spec.ts` → `/modulos/recrutamento`

**Cobertura após Fase 1:** 78.5%

### Fase 2: Páginas P1 (Semanas 3-4) - 10 testes
- [ ] `integracoes.spec.ts` → `/modulos/integracoes`
- [ ] `integracoes-sync.spec.ts` → `/modulos/integracoes/sync`
- [ ] `reembolso.spec.ts` → `/modulos/reembolso`
- [ ] `relatorios.spec.ts` → `/modulos/relatorios`
- [ ] `relatorios-comercial.spec.ts` → `/modulos/relatorios/comercial`
- [ ] `relatorios-dashboards.spec.ts` → `/modulos/relatorios/dashboards`
- [ ] `relatorios-financeiro.spec.ts` → `/modulos/relatorios/financeiro`
- [ ] `relatorios-operacional.spec.ts` → `/modulos/relatorios/operacional`
- [ ] `saude-ocupacional.spec.ts` → `/modulos/saude-ocupacional`
- [ ] `seguranca.spec.ts` → `/modulos/seguranca`

**Cobertura após Fase 2:** 86.8%

### Fase 3: Páginas P2 (Semanas 5-6) - 16 testes
- [ ] `.spec.ts` → `/`
- [ ] `agendador.spec.ts` → `/modulos/agendador`
- [ ] `automacoes.spec.ts` → `/modulos/automacoes`
- [ ] `campo.spec.ts` → `/modulos/campo`
- [ ] `campo-comunicados.spec.ts` → `/modulos/campo/comunicados`
- [ ] `configuracoes.spec.ts` → `/modulos/configuracoes`
- [ ] `crm.spec.ts` → `/modulos/crm`
- [ ] `documentos.spec.ts` → `/modulos/documentos`
- [ ] `equipamentos.spec.ts` → `/modulos/equipamentos`
- [ ] `licitacoes-contratos-detail.spec.ts` → `/modulos/licitacoes/contratos/*`
- [ ] `licitacoes-editais-detail.spec.ts` → `/modulos/licitacoes/editais/*`
- [ ] `licitacoes-propostas-detail.spec.ts` → `/modulos/licitacoes/propostas/*`
- [ ] `openclaw.spec.ts` → `/modulos/openclaw`
- [ ] `operacional-escalas-detail.spec.ts` → `/modulos/operacional/escalas/*`
- [ ] `servicos.spec.ts` → `/modulos/servicos`
- [ ] `offline.spec.ts` → `/offline`

**Cobertura final:** 100%

---

## 📁 Estrutura de Pastas Recomendada para Novos Testes

```
e2e/
├── fiscal/
│   ├── fiscal-dctfweb.spec.ts      # P0
│   ├── fiscal-reinf.spec.ts        # P0
│   └── fiscal-sped.spec.ts         # P0
├── licitacoes/
│   ├── licitacoes-contratos.spec.ts       # P0
│   ├── licitacoes-contratos-detail.spec.ts # P0
│   ├── licitacoes-certidoes.spec.ts       # P0
│   └── licitacoes-documentos.spec.ts      # P0
├── operacional/
│   ├── operacional-agentes.spec.ts        # P0
│   ├── operacional-alocacoes.spec.ts      # P0
│   ├── operacional-banco-horas.spec.ts    # P0
│   ├── operacional-dashboard.spec.ts      # P2
│   ├── operacional-disciplinar.spec.ts    # P0
│   ├── operacional-escalas-detail.spec.ts # P0
│   ├── operacional-escalas-templates.spec.ts # P0
│   ├── operacional-medidas-admin.spec.ts  # P0
│   ├── operacional-notificacoes.spec.ts   # P0
│   ├── operacional-reembolsos.spec.ts     # P0
│   ├── operacional-relatorios.spec.ts     # P0
│   └── operacional-substituicoes.spec.ts  # P0
├── reembolso/
│   └── reembolso-dashboard.spec.ts        # P1
├── relatorios/
│   ├── relatorios-comercial.spec.ts       # P1
│   ├── relatorios-dashboards.spec.ts      # P1
│   ├── relatorios-financeiro.spec.ts      # P1
│   └── relatorios-operacional.spec.ts     # P1
├── recrutamento/
│   └── recrutamento-dashboard.spec.ts     # P1
├── seguranca/
│   └── seguranca-dashboard.spec.ts        # P1
├── saude-ocupacional/
│   └── saude-dashboard.spec.ts            # P1
├── integracoes/
│   ├── integracoes-dashboard.spec.ts      # P2
│   └── integracoes-sync.spec.ts           # P1
├── servicos/
│   └── servicos-dashboard.spec.ts         # P2
├── campo/
│   └── campo-dashboard.spec.ts            # P2
├── agendador/
│   └── agendador-dashboard.spec.ts        # P2
├── automacoes/
│   └── automacoes-dashboard.spec.ts       # P2
├── documentos/
│   └── documentos-dashboard.spec.ts       # P2
├── equipamentos/
│   └── equipamentos-dashboard.spec.ts     # P2
├── crm/
│   └── crm-dashboard.spec.ts              # P2
├── configuracoes/
│   └── configuracoes-dashboard.spec.ts    # P2
└── sistema/
    ├── home.spec.ts                       # P2
    └── offline.spec.ts                    # P2
```

---

## 🎯 Template de Teste E2E

```typescript
// Exemplo: e2e/fiscal/fiscal-dctfweb.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Fiscal - DCTF Web', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="submit"]');
    await page.waitForURL('/dashboard');

    // Navegar para DCTF Web
    await page.goto('/modulos/fiscal/dctfweb');
  });

  test('deve exibir lista de declarações DCTF', async ({ page }) => {
    // Mock da API
    await page.route('**/api/fiscal/dctfweb', async route => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          data: [
            { id: 1, periodo: '2024-01', status: 'transmitida' },
            { id: 2, periodo: '2024-02', status: 'pendente' },
          ]
        })
      });
    });

    await expect(page.locator('[data-testid="dctfweb-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="dctfweb-item"]')).toHaveCount(2);
  });

  test('deve criar nova declaração', async ({ page }) => {
    await page.click('[data-testid="btn-novo"]');
    await page.fill('[data-testid="periodo"]', '2024-03');
    await page.click('[data-testid="btn-salvar"]');

    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });
});
```

---

*Relatório gerado em: 2026-02-06 00:44:29*
*Projeto: Conecta Pro Frontend*
*Versão: 1.0*
