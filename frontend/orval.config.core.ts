/**
 * Configuração Orval - Módulo CORE
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 18 endpoints do módulo Core
 * - Authentication: Login, Register, Refresh Token, Google OAuth (12 endpoints)
 * - Users: Gestão de Usuários, Roles, Ativação/Desativação (16 endpoints)
 *
 * Uso:
 *   npm run orval:core
 */

import { defineConfig } from 'orval';

export default defineConfig({
  core: {
    input: {
      target: './openapi/core-openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/core',
      schemas: './src/types/generated/core/models',
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
