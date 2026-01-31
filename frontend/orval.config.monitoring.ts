import { defineConfig } from 'orval';

export default defineConfig({
  monitoring: {
    input: {
      target: './openapi/monitoring_openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/generated/monitoring',
      client: 'react-query',
      mock: false,
      clean: true,
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
      },
    },
  },
});
