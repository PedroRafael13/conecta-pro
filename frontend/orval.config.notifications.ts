/**
 * Configuração Orval - Módulo NOTIFICATIONS
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 63+ endpoints
 * - Notificações multi-canal (email, SMS, push, WhatsApp, in-app)
 * - Intelligent Notifications (IA, timing, personalização)
 * - Push Notifications (dispositivos, campanhas, analytics)
 * - Templates e preferências
 * - WebSocket real-time
 * - Analytics e LGPD
 *
 * Uso:
 *   npm run orval:notifications
 */

import { defineConfig } from 'orval';

export default defineConfig({
  notifications: {
    input: {
      target: './openapi-notifications.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/notifications',
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
