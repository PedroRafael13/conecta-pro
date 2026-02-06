import { defineConfig } from 'orval';

export default defineConfig({
  ai: {
    input: {
      target: './openapi-ai.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/ai',
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
