import { defineConfig } from 'orval';

export default defineConfig({
  hr: {
    input: {
      target: './openapi/hr.openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/hr/generated',
      schemas: './src/api/hr/generated/models',
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
