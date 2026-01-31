/**
 * Configuração Orval - Módulo AUDIT
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 31 endpoints de Auditoria e Compliance LGPD
 * - AuditLog (6 endpoints)
 * - ComplianceRule (6 endpoints)
 * - ComplianceCheck (6 endpoints)
 * - DataRetention (6 endpoints)
 * - AccessHistory (5 endpoints)
 * - Dashboard (3 endpoints)
 *
 * Uso:
 *   npm run orval:audit
 */

import { defineConfig } from 'orval';

export default defineConfig({
  audit: {
    input: {
      target: './openapi-audit.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/audit',
      schemas: './src/types/generated/audit/models',
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
