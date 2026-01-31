import { defineConfig } from 'orval';

export default defineConfig({
  diarists: {
    input: {
      target: './openapi-diarists.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/diarists/generated',
      schemas: './src/api/diarists/generated/models',
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
