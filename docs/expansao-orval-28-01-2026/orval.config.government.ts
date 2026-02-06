import { defineConfig } from 'orval';

export default defineConfig({
  government: {
    input: './openapi-government.json',
    output: {
      target: './src/types/generated/government/index.ts',
      schemas: './src/types/generated/government/models',
      client: 'axios',
      mode: 'tags-split',
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'api',
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
