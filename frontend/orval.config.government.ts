/**
 * Configuração Orval - Módulo GOVERNMENT INTEGRATIONS
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - 24 integrações: NFS-e, eSocial, SEFAZ, SPED, FGTS, etc.
 *
 * Total: 209 endpoints de integrações governamentais
 *
 * Uso:
 *   npm run orval:government
 */

import { defineConfig } from 'orval';

export default defineConfig({
  government: {
    input: {
      target: './openapi-government.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/government',
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