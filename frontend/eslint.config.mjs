import next from 'eslint-config-next';

const config = [
  {
    ignores: ['.next/**', 'node_modules/**', 'public/**', 'src/types/generated/**', 'src/api/**/generated/**'],
  },
  ...next,
  {
    rules: {
      // React 19 strict immutability - warn only, não são bugs reais.
      // Refatorar 322 instâncias de mutação em hooks é dívida técnica planejada.
      'react-hooks/immutability': 'warn',

      // exhaustive-deps: warn para permitir omissões intencionais com justificativa
      'react-hooks/exhaustive-deps': 'warn',

      // set-state-in-effect: warn - setState em construção de objetos dentro de hooks
      // não é um anti-pattern quando o setState é passado como callback, não chamado diretamente
      'react-hooks/set-state-in-effect': 'warn',

      // static-components: warn - componentes que poderiam ser extraídos
      'react-hooks/static-components': 'warn',

      // refs: warn - padrões de ref que podem ser melhorados
      'react-hooks/refs': 'warn',

      // purity: warn - side effects detectados em render
      'react-hooks/purity': 'warn',
    },
  },
];

export default config;
