/**
 * Configuração Orval - Módulo CLIENTS
 *
 * Gestão de Clientes e Condomínios
 * 38 endpoints identificados
 *
 * Estratégia:
 * - Gera tipos TypeScript + api base
 * - Services e hooks customizados serão criados manualmente
 * - Mantém consistência com padrões do projeto
 *
 * Uso:
 *   npm run orval:clients
 */

import { defineConfig } from 'orval';

export default defineConfig({
  clients: {
    input: {
      target: './openapi-clients.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/clients',
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
