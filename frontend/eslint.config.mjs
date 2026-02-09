import next from 'eslint-config-next';

const config = [
  {
    ignores: ['.next/**', 'node_modules/**', 'public/**', 'src/types/generated/**'],
  },
  ...next,
];

export default config;
