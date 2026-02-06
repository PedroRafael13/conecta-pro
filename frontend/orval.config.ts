import { defineConfig } from 'orval';

export default defineConfig({
  // Configuração por módulo para evitar travamento
  auth: {
    input: {
      target: './openapi-snapshot.json',
      filters: {
        tags: ['Auth'],
      },
    },
    output: {
      target: './src/api/generated/auth.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      mode: 'single',
      prettier: false,
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'axiosInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
        },
      },
    },
  },

  crm: {
    input: {
      target: './openapi-snapshot.json',
      filters: {
        tags: ['CRM', 'Leads', 'Opportunities', 'Clients'],
      },
    },
    output: {
      target: './src/api/generated/crm.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      mode: 'single',
      prettier: false,
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'axiosInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
        },
      },
    },
  },

  financial: {
    input: {
      target: './openapi-snapshot.json',
      filters: {
        tags: ['Financial', 'Accounts', 'Invoices', 'Payments'],
      },
    },
    output: {
      target: './src/api/generated/financial.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      mode: 'single',
      prettier: false,
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'axiosInstance',
        },
      },
    },
  },

  government: {
    input: {
      target: './openapi-snapshot.json',
      filters: {
        tags: ['Government', 'NFSe', 'eSocial', 'SPED'],
      },
    },
    output: {
      target: './src/api/generated/government.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      mode: 'single',
      prettier: false,
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'axiosInstance',
        },
      },
    },
  },

  operacional: {
    input: {
      target: './openapi-snapshot.json',
      filters: {
        tags: ['Operacional', 'Escalas', 'Postos', 'Vigilantes'],
      },
    },
    output: {
      target: './src/api/generated/operacional.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      mode: 'single',
      prettier: false,
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'axiosInstance',
        },
      },
    },
  },

  services: {
    input: {
      target: './openapi-snapshot.json',
      filters: {
        tags: ['Services', 'Contracts', 'WorkOrders'],
      },
    },
    output: {
      target: './src/api/generated/services.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      mode: 'single',
      prettier: false,
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'axiosInstance',
        },
      },
    },
  },
});
