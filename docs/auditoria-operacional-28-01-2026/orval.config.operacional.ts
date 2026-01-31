/**
 * Configuração Orval - Módulo OPERACIONAL
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Uso:
 *   npx orval --config orval.config.operacional.ts
 */

module.exports = {
  operacional: {
    input: {
      // OpenAPI spec apenas do módulo operacional (130 endpoints)
      target: './openapi-operacional.json',
    },
    output: {
      // Gerar arquivos separados por tag (comunicados, escalas, etc)
      mode: 'tags-split',

      // Destino dos arquivos gerados
      target: './src/types/generated/operacional',

      // Gerar apenas tipos, sem client
      // Usar 'axios' como client gera apenas tipos de request/response
      client: 'axios',

      // Não gerar mocks
      mock: false,

      // Configurações de override
      override: {
        // Mapeamento de tipos customizados
        mutator: {
          // Você pode definir um custom instance do axios aqui se necessário
          // path: './src/lib/api/custom-instance.ts',
          // name: 'customInstance',
        },

        // Operações de transformação
        operations: {
          // Adicionar prefixo nos nomes dos tipos se necessário
          // operationIdFn: (operation: any) => `Operacional${operation.operationId}`,
        },
      },
    },

    // Hooks de execução
    hooks: {
      // Formatar código gerado com Prettier
      afterAllFilesWrite: 'prettier --write',
    },
  },
};
