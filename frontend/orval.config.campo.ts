import { defineConfig } from 'orval';

export default defineConfig({
  campo: {
    input: {
      target: './src/api/campo/campo.openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/campo/generated',
      schemas: './src/api/campo/generated/models',
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
