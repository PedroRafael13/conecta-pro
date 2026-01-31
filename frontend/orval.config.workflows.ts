/**
 * Configuração Orval - Módulo WORKFLOWS
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 9 endpoints
 * - Workflows (CRUD completo)
 * - Execuções (listagem, cancelamento)
 * - Ativação/Desativação
 * - Categorias e Status
 * - Métricas e Analytics
 *
 * Uso:
 *   npm run orval:workflows
 */

import { defineConfig } from 'orval';

export default defineConfig({
  workflows: {
    input: {
      target: './openapi/openapi-workflows.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/workflows',
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
