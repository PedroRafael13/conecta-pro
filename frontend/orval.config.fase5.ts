import { defineConfig } from 'orval';

/**
 * Configuração Orval - Módulo FASE5
 *
 * Estratégia: React Query + Tags Split
 * - Gera hooks React Query prontos para uso
 * - Arquivos separados por tag (CCT, Email, Quality)
 * - Mutator customizado para autenticação
 *
 * Cobertura: 11 endpoints do Grand Finale
 * - CCT Compliance: 6 endpoints (validação de salários e propostas SINDCOND 2026)
 * - Email Intelligence: 2 endpoints (análise e contexto de emails com IA)
 * - Quality Framework: 1 endpoint (validação de qualidade target 99+/100)
 * - System Status: 2 endpoints (status e health check)
 *
 * Uso:
 *   npm run orval:fase5
 */
export default defineConfig({
  fase5: {
    input: {
      target: './openapi/fase5-openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/fase5',
      client: 'react-query',
      mock: false,
      clean: true,
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
      },
    },
  },
});
