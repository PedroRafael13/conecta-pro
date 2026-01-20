import { defineConfig } from 'orval';

export default defineConfig({
  conectaPro: {
    input: {
      // URL do OpenAPI do backend FastAPI
      target: 'http://localhost:8080/openapi.json',
      validation: false,
    },
    output: {
      // Gera no frontend
      target: '../frontend/src/api/generated/endpoints.ts',
      schemas: '../frontend/src/api/generated/model',
      client: 'react-query',
      mode: 'tags-split',
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: '../frontend/src/api/generated/axios-instance.ts',
          name: 'axiosInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
          useInfinite: true,
          options: {
            staleTime: 30000,
          },
        },
        // Mapear tags para nomes de arquivos
        operations: {
          // Configurações específicas por operação se necessário
        },
      },
    },
  },
  // Fallback usando snapshot local (quando backend offline)
  conectaProLocal: {
    input: {
      target: './openapi-snapshot.json',
      validation: false,
    },
    output: {
      target: '../frontend/src/api/generated/endpoints.ts',
      schemas: '../frontend/src/api/generated/model',
      client: 'react-query',
      mode: 'tags-split',
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: '../frontend/src/api/generated/axios-instance.ts',
          name: 'axiosInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
          useInfinite: true,
          options: {
            staleTime: 30000,
          },
        },
      },
    },
  },
});
