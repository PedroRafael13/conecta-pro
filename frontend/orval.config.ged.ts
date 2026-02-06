/**
 * Configuração Orval - Módulo GED (Gestão Eletrônica de Documentos)
 *
 * Estratégia: React Query + Tags Split
 * - Gera hooks customizados para cada endpoint
 * - Organiza por tags (controllers)
 * - Suporte completo a mutations e queries
 * - Invalidação automática de cache
 *
 * Cobertura: 117 endpoints em 7 controllers
 *
 * Controllers:
 * - GED - Pastas (21 endpoints): Gestão hierárquica de pastas
 * - GED - Documentos (35 endpoints): Upload, versionamento, aprovação
 * - GED - Versões (10 endpoints): Controle de versões de documentos
 * - GED - Compartilhamento (21 endpoints): Links públicos, permissões
 * - GED - Tags (20 endpoints): Categorização e busca
 * - GED - Assinaturas (25 endpoints): Workflow de assinaturas digitais
 * - GED - Estatísticas (1 endpoint): Dashboard e métricas
 *
 * Features:
 * - Upload de arquivos com multipart/form-data
 * - Download de documentos e versões
 * - Compartilhamento seguro com tokens
 * - Assinaturas digitais com validação
 * - OCR e classificação por IA
 * - Controle de permissões granular
 *
 * Uso:
 *   npm run orval:ged
 */

module.exports = {
  ged: {
    input: {
      // OpenAPI spec do módulo GED (117 endpoints)
      target: './openapi/ged-openapi.json',
    },
    output: {
      // Modo tags-split: Um arquivo por tag (controller)
      mode: 'tags-split',

      // Destino dos arquivos gerados
      target: './src/types/generated/ged',

      // Schemas separados
      schemas: './src/types/generated/ged/schemas',

      // Client React Query
      client: 'react-query',

      // Usar mutator customizado
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
      },

      // Não gerar mocks
      mock: false,
    },
  },
};
