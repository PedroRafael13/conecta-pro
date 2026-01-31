/**
 * Configuração Orval - Módulo CONTRACTS
 *
 * Gestão de Contratos CRM
 * 20 endpoints identificados
 *
 * Estratégia:
 * - Gera tipos TypeScript + api base
 * - Services e hooks customizados serão criados manualmente
 * - Mantém consistência com padrões do projeto
 *
 * Uso:
 *   npm run orval:contracts
 */

import { defineConfig } from 'orval';

export default defineConfig({
  contracts: {
    input: {
      target: './src/api/specs/openapi-contracts.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/contracts',
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
