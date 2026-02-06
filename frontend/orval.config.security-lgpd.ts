/**
 * Configuração Orval - Módulo SECURITY LGPD
 *
 * Compliance LGPD - Lei 13.709/2018
 * - Gestão de Consentimentos (Art. 7, 8, 9)
 * - Criptografia e Mascaramento
 * - Direito ao Esquecimento (Art. 18)
 * - Avaliação de Impacto PIA/DPIA (Art. 38)
 * - Trilha de Auditoria (Art. 46)
 *
 * Total: 21 endpoints LGPD
 *
 * Uso:
 *   npm run orval:security-lgpd
 */

import { defineConfig } from 'orval';

export default defineConfig({
  'security-lgpd': {
    input: {
      target: './openapi-security-lgpd.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/security-lgpd',
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
