import { defineConfig } from 'orval';

export default defineConfig({
  equipment: {
    input: {
      target: './openapi/openapi-equipment.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/equipment',
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
