/**
 * Configuração Orval - Módulo AUTOMATION
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 9 endpoints de Workflows e Automações
 * - Workflows (CRUD completo)
 * - Execuções (listagem, cancelamento)
 * - Ativação/Desativação
 * - Categorias e Status
 *
 * NOTA: Módulo automation contém apenas workflows.
 * Este config é um alias para facilitar referência por módulo.
 *
 * Uso:
 *   npm run orval:automation
 */

import { defineConfig } from 'orval';

export default defineConfig({
  automation: {
    input: {
      target: './openapi/openapi-workflows.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/automation',
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
