/**
 * Configuração Orval - Módulo REIMBURSEMENT
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 30 endpoints de Reembolso de Despesas
 * - Solicitações (8 endpoints)
 * - Itens (3 endpoints)
 * - Anexos (4 endpoints)
 * - Aprovações (4 endpoints)
 * - Processamento Financeiro (2 endpoints)
 * - Utilitários/Enums (3 endpoints)
 * - Stats e Filtros (2 endpoints)
 *
 * Uso:
 *   npm run orval:reimbursement
 */

import { defineConfig } from 'orval';

export default defineConfig({
  reimbursement: {
    input: {
      target: './openapi/reimbursement.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/reimbursement',
      schemas: './src/types/generated/reimbursement/models',
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
