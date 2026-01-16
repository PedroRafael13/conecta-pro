# Conecta PRO - Frontend

<div align="center">
  <h3>Sistema de Gestao Empresarial Inteligente</h3>
  <p>Plataforma completa para gestao de seguranca patrimonial, facilities e operacoes</p>
</div>

---

## Sobre o Projeto

O Conecta PRO e uma plataforma SaaS enterprise para gestao integrada de operacoes empresariais, combinando modulos de compliance, CRM, operacoes de campo, facilities e gestao documental em uma interface moderna e responsiva.

## Stack Tecnologica

| Categoria | Tecnologia | Versao |
|-----------|------------|--------|
| **Framework** | React | 19.2 |
| **Linguagem** | TypeScript | 5.9 |
| **Build Tool** | Vite | 7.2 |
| **Estilizacao** | Tailwind CSS | 3.4 |
| **State Management** | Zustand | 5.0 |
| **Data Fetching** | TanStack React Query | 5.90 |
| **Roteamento** | React Router | 7.12 |
| **Forms** | React Hook Form + Zod | 7.71 / 4.3 |
| **UI Components** | Headless UI | 2.2 |
| **Animacoes** | Framer Motion | 12.26 |
| **Icones** | Lucide React | 0.562 |
| **Graficos** | Recharts | 3.6 |
| **HTTP Client** | Axios | 1.13 |

## Requisitos

- **Node.js** >= 20.0.0
- **npm** >= 10.0.0

## Instalacao

```bash
# Clonar o repositorio
git clone https://github.com/conecta-pro/frontend.git
cd frontend

# Instalar dependencias
npm install

# Copiar variaveis de ambiente
cp .env.example .env.local

# Iniciar servidor de desenvolvimento
npm run dev
```

## Scripts Disponiveis

| Comando | Descricao |
|---------|-----------|
| `npm run dev` | Inicia servidor de desenvolvimento na porta 3000 |
| `npm run build` | Compila TypeScript e gera build de producao |
| `npm run preview` | Visualiza build de producao localmente |
| `npm run lint` | Executa ESLint para verificacao de codigo |

## Estrutura de Pastas

```
src/
├── core/                    # Nucleo da aplicacao
│   ├── api/                 # Cliente HTTP e endpoints
│   │   ├── client.ts        # Configuracao Axios
│   │   ├── endpoints.ts     # Definicao de endpoints
│   │   └── interceptors.ts  # Interceptadores request/response
│   ├── auth/                # Autenticacao
│   │   ├── AuthProvider.tsx # Contexto de autenticacao
│   │   ├── LoginPage.tsx    # Pagina de login
│   │   ├── ProtectedRoute.tsx # Guard de rotas
│   │   └── useAuth.ts       # Hook de autenticacao
│   ├── components/          # Componentes reutilizaveis
│   │   ├── feedback/        # Toast, Skeleton, ErrorBoundary
│   │   ├── forms/           # FormField, Select, DatePicker
│   │   └── ui/              # Button, Card, Modal, Input
│   ├── hooks/               # Hooks customizados
│   ├── layout/              # Layout principal (Header, Sidebar)
│   ├── navigation/          # Rotas e navegacao
│   ├── stores/              # Zustand stores
│   ├── types/               # Tipos TypeScript globais
│   └── utils/               # Utilitarios e helpers
│
├── modules/                 # Modulos de dominio
│   ├── compliance/          # Auditoria, LGPD, Governo, Licitacoes
│   │   ├── audit/           # Sistema de auditoria
│   │   ├── bidding/         # Gestao de licitacoes
│   │   ├── government/      # Integracoes governamentais
│   │   └── lgpd/            # Conformidade LGPD
│   ├── crm/                 # CRM e Vendas
│   │   ├── contacts/        # Gestao de contatos
│   │   ├── deals/           # Pipeline de vendas
│   │   ├── marketplace/     # Marketplace de servicos
│   │   └── proposals/       # Propostas comerciais
│   ├── dashboards/          # Dashboards e Analytics
│   │   ├── analytics/       # Dashboard analitico
│   │   ├── executive/       # Dashboard executivo
│   │   ├── realtime/        # Metricas em tempo real
│   │   └── widgets/         # Widgets reutilizaveis
│   ├── facilities/          # Gestao de Facilities
│   │   ├── equipment/       # Equipamentos e ativos
│   │   ├── iot/             # Sensores IoT
│   │   └── maintenance/     # Manutencao preventiva
│   ├── field-service/       # Servico de Campo
│   │   ├── orders/          # Ordens de servico
│   │   └── technicians/     # Tecnicos e rotas
│   ├── ged/                 # Gestao Eletronica de Documentos
│   └── operations/          # Operacoes
│       ├── postos/          # Postos de trabalho
│       ├── schedules/       # Escalas e turnos
│       └── substitutions/   # Substituicoes
│
└── pages/                   # Paginas da aplicacao
    ├── DashboardPage.tsx
    ├── AnalyticsPage.tsx
    ├── AuditPage.tsx
    ├── CRMPage.tsx
    ├── FacilitiesPage.tsx
    ├── FieldServicePage.tsx
    ├── GEDPage.tsx
    ├── OperationsPage.tsx
    └── ...
```

## Modulos Implementados

### FASE 1: Core & Authentication
- [x] Sistema de autenticacao JWT
- [x] Rotas protegidas
- [x] Layout responsivo
- [x] Componentes UI base

### FASE 2: Dashboards & Analytics
- [x] Dashboard Executivo com KPIs
- [x] Dashboard Analitico com predicoes
- [x] Metricas em tempo real via WebSocket
- [x] Widgets de graficos interativos

### FASE 3: Compliance
- [x] Auditoria automatizada com IA
- [x] Gestao LGPD (consentimentos, direitos)
- [x] Integracoes governamentais (eSocial, SPED)
- [x] Gestao de licitacoes publicas

### FASE 4: GED (Gestao Documental)
- [x] Upload e classificacao de documentos
- [x] Visualizador de PDF integrado
- [x] Busca full-text
- [x] Classificacao automatica por IA

### FASE 5: CRM & Vendas
- [x] Pipeline de vendas Kanban
- [x] Gestao de contatos
- [x] Propostas comerciais dinamicas
- [x] Marketplace de servicos

### FASE 6: Operacoes
- [x] Gestao de postos de trabalho
- [x] Escalas e turnos
- [x] Ordens de servico
- [x] Tecnicos e otimizacao de rotas

### FASE 7: Facilities
- [x] Gestao de equipamentos
- [x] Monitoramento IoT
- [x] Manutencao preventiva e preditiva

## Convencoes de Codigo

### Nomenclatura
- **Componentes**: PascalCase (`UserProfile.tsx`)
- **Hooks**: camelCase com prefixo `use` (`useAuth.ts`)
- **Tipos**: PascalCase com sufixo descritivo (`user.types.ts`)
- **Utils**: camelCase (`formatters.ts`)

### Estrutura de Componentes
```typescript
// Imports externos
import { useState, useEffect } from 'react';

// Imports internos
import { Button } from '@components/ui';
import { useAuth } from '@core/auth';

// Tipos
interface Props {
  title: string;
  onSubmit: () => void;
}

// Componente
export function MyComponent({ title, onSubmit }: Props) {
  // Hooks
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  // Handlers
  const handleClick = () => {
    setLoading(true);
    onSubmit();
  };

  // Render
  return (
    <div className="p-4">
      <h1>{title}</h1>
      <Button onClick={handleClick} loading={loading}>
        Enviar
      </Button>
    </div>
  );
}
```

### Path Aliases
```typescript
// Configurados no vite.config.ts
import { Button } from '@components/ui';    // src/core/components/ui
import { useAuth } from '@core/auth';       // src/core/auth
import { api } from '@api/client';          // src/core/api
import { useUIStore } from '@stores';       // src/core/stores
```

## Variaveis de Ambiente

```env
# API
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Auth
VITE_AUTH_STORAGE_KEY=conecta_pro_auth

# Features
VITE_ENABLE_MOCK=false
VITE_ENABLE_ANALYTICS=true
```

## Build de Producao

```bash
# Gerar build otimizado
npm run build

# Arquivos gerados em dist/
dist/
├── index.html
├── assets/
│   ├── vendor-[hash].js      # React, React DOM, Router
│   ├── ui-[hash].js          # Framer Motion, Headless UI
│   ├── data-[hash].js        # React Query, Zustand
│   └── index-[hash].js       # Codigo da aplicacao
└── ...
```

O build utiliza code splitting automatico com chunks otimizados:
- **vendor**: React ecosystem (~150KB gzipped)
- **ui**: Componentes de UI e animacoes (~50KB gzipped)
- **data**: Gerenciamento de estado e dados (~30KB gzipped)

## Como Contribuir

1. Crie uma branch a partir de `develop`: `git checkout -b feature/nova-funcionalidade`
2. Faca commits semanticos: `git commit -m "feat: adiciona filtro de busca"`
3. Abra um Pull Request para `develop`

### Tipos de Commit
- `feat`: Nova funcionalidade
- `fix`: Correcao de bug
- `refactor`: Refatoracao sem mudanca de comportamento
- `style`: Formatacao, semicolons, etc
- `docs`: Documentacao
- `test`: Testes
- `chore`: Tarefas de manutencao

## Documentacao Adicional

- [Arquitetura](./docs/ARCHITECTURE.md)
- [Componentes](./docs/COMPONENTS.md)
- [Changelog](./CHANGELOG.md)

## Licenca

Proprietario - Conecta PRO - Todos os direitos reservados.

---

<div align="center">
  <sub>Desenvolvido com React 19 + TypeScript + Vite</sub>
</div>
