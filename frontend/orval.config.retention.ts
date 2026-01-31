import { defineConfig } from 'orval';

export default defineConfig({
  retention: {
    input: {
      target: './openapi/retention_openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/generated/retention',
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
