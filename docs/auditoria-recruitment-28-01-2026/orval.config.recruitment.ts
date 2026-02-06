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

module.exports = {
  recruitment: {
    input: {
      // OpenAPI spec apenas do módulo RECRUITMENT (79 endpoints)
      target: './openapi-recruitment.json',
    },
    output: {
      // Gerar arquivos separados por tag
      mode: 'tags-split',

      // Destino dos arquivos gerados
      target: './src/types/generated/recruitment',

      // Usar axios como client
      client: 'axios',

      // Não gerar mocks
      mock: false,

      // Opções de geração
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'customInstance',
        },
      },
    },
  },
};
