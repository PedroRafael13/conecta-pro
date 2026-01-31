/**
 * Configuração Orval - Módulo SERVICES
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 54 endpoints
 * - Service Catalog Management (13 endpoints)
 * - Service Orders (15 endpoints)
 * - Service Execution (12 endpoints)
 * - Service Reports (8 endpoints)
 * - SLA Configuration (6 endpoints)
 *
 * Features:
 * - Catálogo de serviços completo
 * - Ordens de serviço com workflow
 * - Execução e tracking de serviços
 * - Relatórios de execução
 * - SLA tracking e compliance
 * - AI-powered analytics
 *
 * Uso:
 *   npm run orval:services
 */

import { defineConfig } from 'orval';

export default defineConfig({
  services: {
    input: {
      target: './src/lib/api/specs/openapi-services.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/services',
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
