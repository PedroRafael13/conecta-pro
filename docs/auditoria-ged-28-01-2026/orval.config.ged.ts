/**
 * Configuração Orval - Módulo GED (Gestão Eletrônica de Documentos)
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Uso:
 *   npm run orval:ged
 */

module.exports = {
  ged: {
    input: {
      // OpenAPI spec apenas do módulo GED (117 endpoints)
      target: './openapi-ged.json',
    },
    output: {
      // Gerar arquivos separados por tag
      mode: 'tags-split',

      // Destino dos arquivos gerados
      target: './src/types/generated/ged',

      // Usar axios como client
      client: 'axios',

      // Não gerar mocks
      mock: false,
    },
  },
};
