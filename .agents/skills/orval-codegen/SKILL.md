---
title: Orval Codegen 7.13.2
description: Geração de APIs TypeScript a partir de OpenAPI para Conecta PRO
version: 7.13.2
---

# Orval Codegen

Geração automática de clientes HTTP TypeScript a partir de especificações OpenAPI para o ERP Conecta PRO.

## Pré-requisitos

```bash
node --version  # >= 18.0.0
npm list orval  # 7.13.2
```

## Comandos Principais

```bash
cd /opt/conecta-pro/frontend

# Gerar todos os clients
npm run api:generate

# Gerar módulo específico
npm run orval:crm
npm run orval:financial

# Ou diretamente
npx orval --config ./orval.config.ts
```

## Estrutura de Configuração Real

```typescript
// orval.config.ts — usa defineConfig do orval
import { defineConfig } from 'orval';

export default defineConfig({
  auth: {
    input: {
      target: './openapi-snapshot.json',  // Snapshot local do OpenAPI
      filters: { tags: ['Auth'] },        // Filtra por tags
    },
    output: {
      target: './src/api/generated/auth.ts',      // Hooks gerados
      schemas: './src/api/generated/models',       // Types gerados
      client: 'react-query',
      mode: 'single',
      override: {
        mutator: {
          path: './src/lib/api.ts',       // Axios instance customizada
          name: 'axiosInstance',
        },
        query: { useQuery: true, useMutation: true },
      },
    },
  },
  // ... mesmo padrão para crm, financial, operacional, etc.
});
```

## Arquivos Gerados (NUNCA editar manualmente)

```
src/api/generated/          # Hooks React Query gerados
├── auth.ts
├── crm.ts
├── financial.ts
├── operacional.ts
├── models/                 # Types TypeScript gerados
└── ...

src/types/generated/        # Types adicionais
```

## Custom Instance (mutator)

```typescript
// src/lib/api.ts — Axios instance com interceptors
// É referenciado pelo orval.config.ts como mutator
// Adiciona headers, auth token, tratamento de erros

// src/lib/api-client.ts — Wrapper customInstance
// Remove trailing slash, injeta condominio_id, tratamento de erros
```

## Regras CRÍTICAS

- ✅ Sempre usar hooks gerados pelo Orval (`useGet*`, `useCreate*`, etc.)
- ✅ Customização apenas via `src/lib/api.ts` (mutator)
- ✅ Input é `openapi-snapshot.json` (snapshot local, não URL direta)
- ❌ NUNCA editar arquivos em `src/api/generated/*`
- ❌ NUNCA editar arquivos em `src/types/generated/*`
- ❌ NUNCA editar `src/api/generated/models/*`

## Troubleshooting

```bash
# Regenerar tudo do zero
rm -rf src/api/generated && npx orval --config ./orval.config.ts

# Atualizar snapshot OpenAPI
curl http://localhost:8000/openapi.json > openapi-snapshot.json

# Type check após regeneração
npx tsc --noEmit
```
