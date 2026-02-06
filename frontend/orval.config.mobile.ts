/**
 * Configuração Orval - Módulo MOBILE
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 16+ endpoints
 * - Health & Config (2 endpoints)
 * - Dashboard mobile-optimized (1 endpoint)
 * - Sync Operations (3 endpoints - sync, status, resolve-conflict)
 * - Offline Data (1 endpoint)
 * - Batch Operations (1 endpoint)
 * - Device Registration (2 endpoints)
 * - Push Notifications (6 endpoints)
 * - Admin Notifications (2 endpoints)
 *
 * Features:
 * - Offline-first sync com resolução de conflitos
 * - Push notifications multi-plataforma (FCM/APNs)
 * - Batch operations para otimização de rede
 * - Dashboard lightweight para mobile
 * - Device management para notificações
 *
 * Uso:
 *   npm run orval:mobile
 */

import { defineConfig } from 'orval';

export default defineConfig({
  mobile: {
    input: {
      target: './openapi-mobile.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/mobile',
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
