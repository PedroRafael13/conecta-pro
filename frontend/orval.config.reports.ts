import { defineConfig } from 'orval';

export default defineConfig({
  reports: {
    input: {
      target: './src/api/specs/openapi-reports.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/generated/reports/endpoints.ts',
      schemas: './src/api/generated/reports/models',
      client: 'react-query',
      mock: false,
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: './src/api/client/axios-instance.ts',
          name: 'customInstance',
        },
        query: {
          useQuery: true,
          useInfinite: false,
          useInfiniteQueryParam: 'nextPage',
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
