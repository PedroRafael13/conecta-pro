# Conecta PRO - Frontend

## Projeto
Sistema ERP completo para gestão empresarial com foco em vigilância e segurança patrimonial.

**Empresa:** JORDAN SANTOS DE JESUS LTDA
**CNPJ:** 35.710.481/0001-03
**Setor:** Vigilância e Segurança

## Stack Técnico

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 19.2 | Framework UI |
| TypeScript | 5.x | Tipagem estática |
| Vite | 7.x | Build tool |
| TailwindCSS | 3.x | Estilização |
| TanStack Query | 5.x | Data fetching |
| Zustand | 5.x | State management |
| React Router | 7.x | Roteamento |
| React Hook Form | 7.x | Formulários |
| Zod | 4.x | Validação |
| Framer Motion | 12.x | Animações |
| Recharts | 3.x | Gráficos |
| Lucide React | 0.562 | Ícones |
| **Capacitor** | **8.x** | **Apps nativos iOS/Android** |
| **VitePWA** | **1.x** | **Progressive Web App** |

## Estrutura do Projeto

```
frontend/
├── android/               # Projeto Android Studio (Capacitor)
├── ios/                   # Projeto Xcode (Capacitor)
├── resources/             # Ícones e splash source
├── public/                # Assets estáticos
│   ├── icons/            # Ícones PWA
│   └── manifest.json     # Manifest PWA
├── src/
│   ├── app/              # App principal e providers
│   ├── core/             # Funcionalidades core
│   │   ├── api/          # Cliente API + interceptors
│   │   ├── auth/         # Autenticação
│   │   ├── components/   # Componentes core
│   │   │   └── pwa/     # PWA + Capacitor components
│   │   ├── hooks/        # Hooks globais
│   │   ├── navigation/   # Rotas e navegação
│   │   ├── stores/       # Zustand stores
│   │   ├── types/        # Tipos globais
│   │   └── utils/        # Utilitários
│   ├── design-system/    # Design system
│   ├── features/         # Módulos por domínio
│   ├── layouts/          # Layouts da aplicação
│   ├── modules/          # Módulos legados
│   ├── pages/            # Páginas standalone
│   └── shared/           # Código compartilhado
├── docs/
│   └── MOBILE_APP_PUBLISH.md  # Guia publicação lojas
├── capacitor.config.ts   # Configuração Capacitor
├── vite.config.ts        # Configuração Vite + PWA
└── package.json
```

---

## Sessão 18/01/2026 - Trabalho Realizado

### Commits Realizados

| Hash | Descrição |
|------|-----------|
| `acd05d2` | feat(frontend): implementa suporte offline completo para PWA |
| `372bec8` | fix(frontend): inicializa interceptors de autenticação no main.tsx |
| `45945fd` | feat(frontend): configura Capacitor para apps nativos iOS/Android |

### 1. PWA - Suporte Offline Completo

#### Hooks Criados

| Hook | Arquivo | Função |
|------|---------|--------|
| `useOnlineStatus` | `core/hooks/useOnlineStatus.ts` | Detecta conexão online/offline |
| `usePWA` | `core/hooks/usePWA.ts` | Gerencia instalação e atualizações do PWA |

#### Componentes Criados

| Componente | Arquivo | Função |
|------------|---------|--------|
| `OfflineBanner` | `core/components/pwa/OfflineBanner.tsx` | Banner amarelo quando offline, verde ao reconectar |
| `InstallPrompt` | `core/components/pwa/InstallPrompt.tsx` | Prompt para instalar o app (aparece após 30s) |
| `UpdatePrompt` | `core/components/pwa/UpdatePrompt.tsx` | Notifica quando há nova versão disponível |

#### Configuração PWA (vite.config.ts)

```typescript
VitePWA({
  registerType: 'autoUpdate',
  workbox: {
    runtimeCaching: [
      { urlPattern: /^https:\/\/api\./i, handler: 'NetworkFirst' },  // API: 24h
      { urlPattern: /\.(?:png|jpg|jpeg|svg)$/, handler: 'CacheFirst' }, // Imagens: 30 dias
      { urlPattern: /\.(?:woff|woff2)$/, handler: 'CacheFirst' },    // Fontes: 1 ano
    ]
  }
})
```

### 2. Integração API Verificada

#### Interceptors Inicializados

Arquivo `src/main.tsx` agora inicializa os interceptors:

```typescript
import { setupInterceptors } from '@core/api/interceptors';
setupInterceptors(); // Token refresh automático
```

#### Autenticação Testada e Funcionando

```bash
# Login funcionando
POST /api/v1/auth/login → access_token + refresh_token ✅

# API CRM funcionando
GET /api/v1/crm/leads → Lista de leads ✅

# Credenciais de teste
Email: admin@conectapro.com.br
```

### 3. Capacitor - Apps Nativos iOS/Android

#### Configuração

| Item | Valor |
|------|-------|
| App ID | `br.com.conectapro.app` |
| Nome | Conecta PRO |
| Web Dir | `dist` |
| Background Color | `#0A2540` |

#### Plugins Instalados (11)

| Plugin | Função |
|--------|--------|
| `@capacitor/app` | Lifecycle, deep links, back button |
| `@capacitor/status-bar` | Customização da status bar |
| `@capacitor/splash-screen` | Splash screen nativa |
| `@capacitor/keyboard` | Controle do teclado virtual |
| `@capacitor/push-notifications` | Notificações push nativas |
| `@capacitor/camera` | Acesso à câmera |
| `@capacitor/geolocation` | GPS e localização |
| `@capacitor/network` | Status de conexão |
| `@capacitor/haptics` | Feedback tátil (vibração) |
| `@capacitor/browser` | Browser in-app |
| `@capacitor/preferences` | Storage local persistente |

#### Hook useCapacitor

```typescript
// core/hooks/useCapacitor.ts
const {
  isNative,           // true se está rodando como app nativo
  platform,           // 'ios' | 'android' | 'web'
  isOnline,           // status de conexão
  pushToken,          // token para push notifications
  requestPushPermission, // solicita permissão de push
  vibrate,            // feedback háptico
  openBrowser,        // abre URL no browser nativo
} = useCapacitor();
```

#### Componente CapacitorInit

Inicializa automaticamente no App.tsx:
- Configura status bar (cor #0A2540)
- Esconde splash screen
- Adiciona classes CSS para safe areas
- Configura listeners de teclado
- Monitora status de rede

#### Scripts NPM Disponíveis

```bash
npm run cap:build       # Build web + Sync com nativo
npm run cap:android     # Abre Android Studio
npm run cap:ios         # Abre Xcode
npm run cap:android:run # Roda em device/emulador Android
npm run cap:ios:run     # Roda em device/simulador iOS
npm run cap:assets      # Gera ícones e splash screens
npm run cap:sync        # Sincroniza web com nativo
```

#### Estilos Mobile Adicionados (index.css)

```css
/* Safe areas para notch/home indicator */
.capacitor {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}

/* Previne zoom em inputs iOS */
.platform-ios input { font-size: 16px !important; }

/* Ajuste quando teclado está aberto */
.keyboard-open { height: calc(100vh - 300px); }
```

---

## Arquitetura de Autenticação

### Fluxo de Login

```
1. Usuário envia email/senha
2. POST /api/v1/auth/login (form-urlencoded)
3. Backend retorna: { access_token, refresh_token }
4. Token salvo no Zustand (persist → localStorage)
5. Interceptor adiciona token em todas as requisições
```

### Refresh Token Automático

```
1. Requisição retorna 401
2. Interceptor captura o erro
3. POST /api/v1/auth/refresh com refresh_token
4. Novo access_token salvo
5. Requisição original refeita automaticamente
```

### Arquivos de Autenticação

| Arquivo | Função |
|---------|--------|
| `core/api/client.ts` | Axios client com baseURL `/api/v1` |
| `core/api/interceptors.ts` | Token refresh, error handling |
| `core/stores/authStore.ts` | Zustand store com persist |
| `core/auth/useAuth.ts` | Hook de autenticação |
| `core/auth/AuthProvider.tsx` | Provider de contexto |

---

## Módulos Implementados

### CRM (100%)
- Dashboard CRM
- Leads (CRUD completo + scoring IA)
- Oportunidades (pipeline visual)
- Propostas (com timeline de atividades)
- Contratos (com renovação automática)
- Comissões (cálculo automático)

### Financeiro (100%)
- Dashboard Financeiro
- Contas a Pagar
- Contas a Receber
- Fluxo de Caixa
- Banking (contas bancárias)
- Fornecedores
- Regras de Faturamento
- Conciliação Bancária

### RH (100%)
- Dashboard RH
- Colaboradores
- Folha de Pagamento
- Integração REP (ponto eletrônico)
- Portal do Colaborador
- Férias e Licenças

### Operações (100%)
- Postos de Trabalho
- Escalas (geração automática)
- Substituições
- Banco de Horas
- Diaristas

### Outros Módulos
- Autenticação (Login, Registro, Recuperação)
- Configurações (Feature Flags, Tenants)
- Notificações (Push, Templates, Canais)
- Compliance (LGPD, eSocial, SEFAZ)
- Licitações
- Saúde Ocupacional (PCMSO, PPRA, EPI)
- GED (Gestão Eletrônica de Documentos)
- Automação (Workflows)

---

## Comandos Úteis

```bash
# Desenvolvimento
npm run dev              # Inicia servidor dev (porta 3000)
npm run build            # Build de produção
npm run preview          # Preview do build
npm run lint             # ESLint

# Capacitor (Apps Nativos)
npm run cap:build        # Build + Sync
npm run cap:android      # Abre Android Studio
npm run cap:ios          # Abre Xcode

# Verificação
npx tsc --noEmit         # Verificar tipos TypeScript
```

---

## Publicação nas Lojas

### Pré-requisitos

**Android (Play Store):**
- Conta Google Play Console ($25 única)
- Android Studio instalado
- Keystore para assinatura

**iOS (App Store):**
- Conta Apple Developer ($99/ano)
- Mac com Xcode
- Certificados de distribuição

### Processo de Build

```bash
# Android
npm run cap:build
cd android
./gradlew bundleRelease
# → android/app/build/outputs/bundle/release/app-release.aab

# iOS (no Mac)
npm run cap:build
npm run cap:ios
# → Xcode > Product > Archive
```

### Documentação Completa
Ver `docs/MOBILE_APP_PUBLISH.md` para guia detalhado.

---

## Próximos Passos

### Concluídos ✅
- [x] Corrigir Selects com onChange vazio
- [x] Configurar PWA com suporte offline
- [x] Integrar APIs reais (CRM, Financial)
- [x] Verificar autenticação JWT
- [x] Configurar Capacitor para apps nativos
- [x] Criar documentação de publicação

### Pendentes
- [ ] Adicionar testes unitários com Vitest
- [ ] Adicionar i18n para internacionalização
- [ ] Configurar Firebase para push notifications
- [ ] Gerar builds de produção para as lojas
- [ ] Configurar CI/CD para builds automáticos
- [ ] Criar ícones e splash screens finais (design)

---

## Credenciais de Teste

```
Email: admin@conectapro.com.br
API: http://172.18.0.6:8080/api/v1
Swagger: http://172.18.0.6:8080/docs
```

---

*Última atualização: 18/01/2026 - Sessão PWA + Capacitor*
