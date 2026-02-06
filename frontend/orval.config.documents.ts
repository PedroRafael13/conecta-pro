/**
 * Configuração Orval - Módulo DOCUMENTS
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Document Intelligence + OCR + Classificação + Extração
 *
 * Cobertura: 16 endpoints
 * - Upload e processamento de documentos
 * - OCR multi-provider (Tesseract, EasyOCR, Google Vision)
 * - Classificação automática de tipos
 * - Extração de dados estruturados
 * - Validação de campos e documentos (CPF/CNPJ)
 * - Templates de extração customizáveis
 * - Estatísticas de armazenamento
 *
 * Uso:
 *   npm run orval:documents
 */

import { defineConfig } from 'orval';

export default defineConfig({
  documents: {
    input: {
      target: './openapi-documents.json',
    },
    output: {
      mode: 'single',
      target: './src/types/generated/documents.ts',
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
