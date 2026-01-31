import { defineConfig } from 'orval';

/**
 * Configuração Orval - Módulo BIDDING (Licitações)
 *
 * Gera tipos TypeScript + clients a partir do OpenAPI spec
 * Service layer e hooks serão implementados manualmente
 *
 * Módulos:
 * - Tenders (Editais): 12 endpoints
 * - Proposals (Propostas): 25 endpoints
 * - Contracts (Contratos): 10 endpoints
 * - Certificates (Certidões): 14 endpoints
 * - Documents/PNCP: 8 endpoints
 *
 * Total: 69 endpoints de licitações públicas (Lei 14.133/2021)
 *
 * Uso:
 *   npm run orval:bidding
 */
export default defineConfig({
  bidding: {
    input: {
      target: './openapi-bidding.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/bidding',
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
