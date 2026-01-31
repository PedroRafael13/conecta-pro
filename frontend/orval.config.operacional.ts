/**
 * Configuração Orval - Módulo OPERACIONAL
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Uso:
 *   npm run orval:operacional
 */

import { defineConfig } from 'orval';

export default defineConfig({
  operacional: {
    input: {
      target: './openapi-operacional.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/operacional',
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
