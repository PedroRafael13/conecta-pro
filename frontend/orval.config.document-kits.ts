/**
 * Configuração Orval - Módulo DOCUMENT KITS
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Kits documentais + Templates + IA + Integração Operacional
 *
 * Total: 58 endpoints
 * - 12 endpoints de Kits (CRUD, templates, stats)
 * - 7 endpoints de Items (gerenciamento de itens)
 * - 13 endpoints de Assignments (atribuições e workflow)
 * - 6 endpoints de Item Status (status de documentos)
 * - 6 endpoints de AI (sugestões, compliance, predições)
 * - 4 endpoints de Operational Integration (integração com operacional)
 * - 10 endpoints de Operational (geração mensal, scheduler)
 *
 * Uso:
 *   npm run orval:document-kits
 */

import { defineConfig } from 'orval';

export default defineConfig({
  'document-kits': {
    input: {
      target: './openapi/document-kits-snapshot.json',
    },
    output: {
      mode: 'single',
      target: './src/types/generated/document-kits.ts',
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
