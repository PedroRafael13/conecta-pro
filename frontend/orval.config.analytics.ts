import { defineConfig } from 'orval';

export default defineConfig({
  analytics: {
    input: {
      target: './openapi/analytics_openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/generated/analytics',
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
