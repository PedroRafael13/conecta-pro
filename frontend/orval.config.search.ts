/**
 * Configuração Orval - Módulo SEARCH
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 1 endpoint de Busca Global
 * - GET /api/v1/search/ - Busca global no sistema
 *
 * Busca em:
 * - Colaboradores (nome, CPF, matrícula)
 * - Postos (nome, código)
 * - Escalas (período, código)
 * - Ocorrências (descrição, responsável)
 * - Rondas (código, inspetor)
 *
 * Uso:
 *   npm run orval:search
 */

import { defineConfig } from 'orval';

export default defineConfig({
  search: {
    input: {
      target: './openapi-search.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/search',
      schemas: './src/types/generated/search/models',
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
