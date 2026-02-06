/**
 * Configuração Orval - Módulo RECRUITMENT (Recrutamento e Seleção)
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Uso:
 *   npm run orval:recruitment
 *
 * Submódulos:
 *   - Job Positions (Vagas): 15 endpoints
 *   - Candidates (Candidatos): 23 endpoints
 *   - Applications (Candidaturas): 27 endpoints
 *   - Interviews (Entrevistas): 24 endpoints
 *   - Total: 79 endpoints
 */

import { defineConfig } from 'orval';

export default defineConfig({
  recruitment: {
    input: {
      target: './openapi-recruitment.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/recruitment',
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
