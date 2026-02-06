/**
 * Configuração Orval - Módulo CONFIG
 *
 * Estratégia COMPLETA:
 * - Gera tipos TypeScript a partir do OpenAPI
 * - Gera service layer com axios
 * - Gera hooks React Query customizados
 *
 * Recursos:
 * - Tenants (Multi-tenant): 13 endpoints
 * - Tenant Settings: 7 endpoints
 * - System Config: 5 endpoints
 * - Feature Flags: 11 endpoints
 * - Notification Templates: 9 endpoints
 * - Dashboards: 2 endpoints
 *
 * Total: 47 operações HTTP em 32 paths
 *
 * Uso:
 *   npm run orval:config
 */

import { defineConfig } from 'orval';

export default defineConfig({
  config: {
    input: {
      // OpenAPI spec do módulo CONFIG (47 operações)
      target: './openapi-config.json',
    },
    output: {
      // Gerar arquivos por tag
      mode: 'tags-split',

      // Destino base
      target: './src/types/generated/config',

      // Client HTTP
      client: 'react-query',

      // Configuração do cliente axios
      override: {
        mutator: {
          path: './src/lib/axios-instance.ts',
          name: 'customInstance',
        },
      },

      // Não gerar mocks
      mock: false,
    },

    // Hooks específicos
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
