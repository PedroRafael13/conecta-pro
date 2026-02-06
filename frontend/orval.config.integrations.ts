import { defineConfig } from 'orval';

export default defineConfig({
  integrations: {
    input: {
      target: './src/lib/api/specs/openapi-integrations.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/integrations',
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
