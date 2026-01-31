/**
 * Configuração Orval - Módulo SCHEDULER
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 26 endpoints de Agendamento e Background Jobs
 * - Tasks (9 endpoints): CRUD, ativar, pausar, disparar, stats
 * - Executions (4 endpoints): listar, buscar, logs, cancelar
 * - Queue (4 endpoints): adicionar, listar, stats, remover
 * - Workers (3 endpoints): listar, buscar, stats
 * - Locks (4 endpoints): adquirir, liberar, renovar, listar
 * - Operations (2 endpoints): run-cycle, due-tasks
 *
 * Uso:
 *   npm run orval:scheduler
 */

import { defineConfig } from 'orval';

export default defineConfig({
  scheduler: {
    input: {
      target: './openapi-scheduler.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/scheduler',
      schemas: './src/types/generated/scheduler/models',
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
