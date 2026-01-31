/**
 * Configuração Orval - Módulo CRM
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 73 endpoints de Gestão de Relacionamento com Cliente
 * - Leads: 6 endpoints (criação, listagem, atualização, score, ações recomendadas)
 * - Opportunities: 6 endpoints (criação, conversão de leads, pipeline, fechamento)
 * - Contratos: 20 endpoints (gestão completa, aditivos, templates, SLA)
 * - Comissões: 15 endpoints (cálculo, pagamento, estruturas de comissionamento)
 * - Propostas: 14 endpoints (criação, aprovação, conversão em contrato)
 * - Dashboard: 12 endpoints (KPIs, métricas, analytics de vendas)
 *
 * Uso:
 *   npm run orval:crm
 */

import { defineConfig } from 'orval';

export default defineConfig({
  crm: {
    input: {
      target: './openapi/openapi-crm.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/crm',
      schemas: './src/types/generated/crm/models',
      client: 'react-query',
      mock: false,
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
