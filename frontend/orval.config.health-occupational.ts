/**
 * Configuração Orval - Módulo HEALTH_OCCUPATIONAL
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Compliance: NR-4, NR-6, NR-7, NR-9
 * Módulos: PCMSO (Exames Médicos), EPI (Equipamentos), PPRA/PGR (Riscos)
 *
 * Uso:
 *   npm run orval:health-occupational
 */

import { defineConfig } from 'orval';

export default defineConfig({
  healthOccupational: {
    input: {
      target: './openapi-health-occupational.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/health-occupational',
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
