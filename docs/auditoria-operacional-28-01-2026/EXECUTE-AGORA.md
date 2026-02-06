# 🚀 EXECUTE AGORA - COBERTURA 100% OPERACIONAL

## ✨ ESTRATÉGIA ESCOLHIDA: HÍBRIDA (O SUPRASUMO!)

**Por que é excepcional:**
- ✅ **Tipos TypeScript 100% sincronizados** com backend (zero erro)
- ✅ **Services e hooks no padrão do projeto** (familiar para a equipe)
- ✅ **Geração automática** de tipos via Orval
- ✅ **Implementação manual** de lógica de negócio
- ✅ **Manutenção facilitada** - regeerar tipos é trivial
- ✅ **Escalável** para outros módulos

---

## 📦 ARTEFATOS PRONTOS

Todos os arquivos estão em:
```
/tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/
```

### 1. OpenAPI Spec do Módulo OPERACIONAL ✅
```
openapi-operacional.json (620 KB)
- 130 endpoints extraídos
- 164 schemas incluídos
- Redução de 73% do tamanho original
```

### 2. Configuração Orval ✅
```
orval.config.operacional.ts
- Configurado para gerar apenas tipos
- Separação por tags (announcements, scales, etc)
- Prettier automático após geração
```

### 3. Script de Extração ✅
```
extract-operacional-spec.py
- Extrai apenas módulo OPERACIONAL
- Inclui schemas referenciados recursivamente
- Reutilizável para outros módulos
```

### 4. Documentação Completa ✅
```
plano-cobertura-100-operacional.md (8KB)
- 3 estratégias detalhadas
- Comparação completa
- Roadmap de 4 semanas

auditoria-operacional.md (35KB)
- Gap analysis completo
- 130 endpoints mapeados
- Priorização de implementação

README-implementacao.md (15KB)
- Quick start step-by-step
- Exemplos de código prontos
- Checklist completo
```

---

## 🎯 PRÓXIMOS PASSOS (EXECUTE NA ORDEM)

### PASSO 1: Copiar Arquivos para o Frontend (2min)

```bash
cd /opt/conecta-pro/frontend

# Copiar spec do operacional
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/openapi-operacional.json ./

# Copiar config do Orval
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/orval.config.operacional.ts ./

# Verificar
ls -lh openapi-operacional.json orval.config.operacional.ts
```

---

### PASSO 2: Instalar Dependências (3min)

```bash
cd /opt/conecta-pro/frontend

# Instalar Orval
npm install -D orval

# Verificar se já tem React Query
npm list @tanstack/react-query

# Se não tiver, instalar
npm install @tanstack/react-query

# Instalar Recharts para gráficos
npm install recharts
```

---

### PASSO 3: Adicionar Scripts no package.json (1min)

```bash
cd /opt/conecta-pro/frontend

# Editar package.json e adicionar na seção "scripts":
```

```json
{
  "scripts": {
    "orval:operacional": "orval --config orval.config.operacional.ts",
    "orval:watch": "orval --config orval.config.operacional.ts --watch",
    "types:check": "tsc --noEmit"
  }
}
```

---

### PASSO 4: Gerar Tipos pela Primeira Vez (30seg)

```bash
cd /opt/conecta-pro/frontend

npm run orval:operacional
```

**Resultado esperado:**
```
✨ Gerados em src/types/generated/operacional/
   - announcements.ts
   - notifications.ts
   - allocations.ts
   - posts.ts
   - scales.ts
   - shifts.ts
   - occurrences.ts
   - patrol-rounds.ts
   - disciplinary.ts
   - diarists.ts
   ... (mais arquivos)
```

---

### PASSO 5: Verificar Tipos Gerados (1min)

```bash
cd /opt/conecta-pro/frontend

# Listar arquivos gerados
ls -la src/types/generated/operacional/

# Ver exemplo de um arquivo
head -50 src/types/generated/operacional/announcements.ts

# Verificar se há erros de TypeScript
npm run types:check
```

---

## 📋 IMPLEMENTAÇÃO DOS GAPS (64 HORAS)

Agora você tem TUDO pronto para implementar os 30 endpoints faltantes!

### PRIORIDADE 1: Módulo de Comunicação (40h) 🔴

#### Comunicados (20h)

**1.1 Service (4h)**
```typescript
// src/lib/services/announcements.ts
import type {
  Announcement,
  AnnouncementCreate,
  AnnouncementUpdate,
  AnnouncementFilter,
} from '@/types/generated/operacional/announcements'; // <-- TIPOS GERADOS!

export const announcementsService = {
  list: async (filters?: AnnouncementFilter) => {
    return api.get('/api/v1/operacional/comunicados', { params: filters });
  },
  // ... 8 métodos restantes
};
```

**1.2 Hooks (4h)**
```typescript
// src/hooks/useAnnouncements.ts
import type { AnnouncementFilter } from '@/types/generated/operacional/announcements';

export function useAnnouncements(filters?: AnnouncementFilter) {
  return useQuery({
    queryKey: ['announcements', filters],
    queryFn: () => announcementsService.list(filters),
  });
}
// ... 4 hooks restantes
```

**1.3 Componentes (8h)**
- AnnouncementFormModal.tsx (3h)
- AnnouncementDetailModal.tsx (2h)
- AnnouncementCard.tsx (1h)
- AnnouncementList.tsx (2h)

**1.4 Página (4h)**
```typescript
// src/app/modulos/operacional/comunicados/page.tsx
'use client';

import { useAnnouncements, useAnnouncementMutations } from '@/hooks/useAnnouncements';

export default function ComunicadosPage() {
  const { data, isLoading } = useAnnouncements();
  const { create, update, remove } = useAnnouncementMutations();

  // ... implementação
}
```

#### Notificações e Alertas (20h)

Mesma estrutura:
- Services (6h): notifications.ts, alerts.ts
- Hooks (4h): useNotifications.ts, useAlerts.ts
- Componentes (6h): NotificationCenter, AlertBadge
- Página (4h): /operacional/notificacoes/page.tsx

---

### PRIORIDADE 2: WebSocket (16h) 🟡

```typescript
// src/lib/websocket/operacional-ws.ts
class OperacionalWebSocket {
  private wsAlerts: WebSocket | null = null;
  private wsNotifications: WebSocket | null = null;

  connect(token: string) {
    // Conexão com autenticação
    // Heartbeat automático (30s)
    // Reconexão automática (5s)
  }

  // ... métodos de gerenciamento
}

export const operacionalWS = new OperacionalWebSocket();
```

**Integração com React:**
```typescript
// src/hooks/useOperacionalWebSocket.ts
export function useOperacionalWebSocket() {
  useEffect(() => {
    const token = getAuthToken();
    operacionalWS.connect(token);

    // Event listeners
    window.addEventListener('operacional:alert', handleAlert);
    window.addEventListener('operacional:notification', handleNotification);

    return () => {
      operacionalWS.disconnect();
      window.removeEventListener('operacional:alert', handleAlert);
      window.removeEventListener('operacional:notification', handleNotification);
    };
  }, []);
}
```

---

### PRIORIDADE 3: Completar Disciplinar (8h) 🟢

**3.1 Botão Validar Conformidade CLT (2h)**
```typescript
// Adicionar em DisciplinaryFormModal.tsx
const { mutate: validateCompliance } = useMutation({
  mutationFn: disciplinaryService.validateCompliance,
  onSuccess: (data) => {
    toast.success(data.is_compliant ? 'Conforme CLT' : 'Não conforme');
  },
});

<Button onClick={() => validateCompliance(formData)}>
  Validar Conformidade CLT
</Button>
```

**3.2 Botão Verificar Proporcionalidade (2h)**
```typescript
const { mutate: checkProportionality } = useMutation({
  mutationFn: disciplinaryService.checkProportionality,
  onSuccess: (data) => {
    toast.success(data.is_proportional ? 'Proporcional' : 'Desproporcional');
  },
});

<Button onClick={() => checkProportionality(formData)}>
  Verificar Proporcionalidade
</Button>
```

**3.3 Visualização de Assinaturas (4h)**
```typescript
// Componente SignatureVerification.tsx
export function SignatureVerification({ documentId }) {
  const { data: signatures } = useQuery({
    queryKey: ['signatures', documentId],
    queryFn: () => disciplinaryService.getSignatures(documentId),
  });

  return (
    <div>
      {signatures?.map(sig => (
        <SignatureCard
          key={sig.id}
          signature={sig}
          verified={sig.verified}
        />
      ))}
    </div>
  );
}
```

---

## 📊 CHECKLIST VISUAL DE PROGRESSO

### ✅ Setup Completo
- [x] OpenAPI spec extraído (130 endpoints)
- [x] Configuração Orval criada
- [x] Scripts de extração prontos
- [x] Documentação completa gerada

### ⏳ Próximos Passos (Sua Execução)
- [ ] Copiar arquivos para o frontend
- [ ] Instalar dependências
- [ ] Gerar tipos pela primeira vez
- [ ] Verificar tipos gerados

### 🔴 Implementação Crítica (40h)
- [ ] Service announcements.ts (4h)
- [ ] Hooks useAnnouncements.ts (4h)
- [ ] Componentes comunicados (8h)
- [ ] Página comunicados (4h)
- [ ] Service notifications.ts (3h)
- [ ] Service alerts.ts (3h)
- [ ] Hooks useNotifications.ts (4h)
- [ ] Componentes notificações (6h)
- [ ] Página notificações (4h)

### 🟡 Implementação Alta (16h)
- [ ] Classe OperacionalWebSocket (8h)
- [ ] Hook useOperacionalWebSocket (4h)
- [ ] Integração com UI (4h)

### 🟢 Implementação Média (8h)
- [ ] Botão Validar CLT (2h)
- [ ] Botão Verificar Proporcionalidade (2h)
- [ ] Visualização Assinaturas (4h)

---

## 🎯 MÉTRICAS DE SUCESSO

### Cobertura de Endpoints
```
Antes:   100/130 endpoints (77%)
Depois:  130/130 endpoints (100%) ✅
Gap:     30 endpoints
```

### Qualidade de Código
- ✅ Zero erros TypeScript
- ✅ 100% tipos sincronizados
- ✅ 100% tratamento de erro
- ✅ 100% loading states

### Testes End-to-End
- ✅ Fluxo de comunicados completo
- ✅ WebSocket com reconexão
- ✅ Notificações em tempo real
- ✅ Workflow disciplinar CLT

---

## 💡 DICAS PRO

### Ao Gerar Tipos
```bash
# Se o backend mudou, basta refazer:
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json
python3 extract-operacional-spec.py
npm run orval:operacional
```

### Watch Mode
```bash
# Regera automaticamente ao detectar mudanças
npm run orval:watch &
```

### Validação Contínua
```bash
# Verificar erros de tipo em tempo real
npm run types:check -- --watch
```

### CI/CD Integration
```yaml
# .github/workflows/check-types.yml
- name: Validate Types
  run: |
    npm run orval:operacional
    npm run types:check
```

---

## 🚀 COMANDOS RÁPIDOS

```bash
# Setup completo (executar uma vez)
cd /opt/conecta-pro/frontend
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/openapi-operacional.json ./
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/orval.config.operacional.ts ./
npm install -D orval
npm install @tanstack/react-query recharts
npm run orval:operacional

# Desenvolvimento diário
npm run orval:watch  # Terminal 1
npm run dev          # Terminal 2
npm run types:check -- --watch  # Terminal 3
```

---

## 📚 DOCUMENTAÇÃO DE REFERÊNCIA

| Documento | Localização | Descrição |
|-----------|-------------|-----------|
| **Plano Completo** | `plano-cobertura-100-operacional.md` | 3 estratégias, roadmap 4 semanas |
| **Auditoria** | `auditoria-operacional.md` | Gap analysis, 130 endpoints |
| **Quick Start** | `README-implementacao.md` | Exemplos de código, checklist |
| **OpenAPI Spec** | `openapi-operacional.json` | 130 endpoints, 164 schemas |
| **Config Orval** | `orval.config.operacional.ts` | Configuração de geração |
| **Script Extração** | `extract-operacional-spec.py` | Reutilizável para outros módulos |

---

## 🎓 PRÓXIMA FASE: EXPANSÃO

Após alcançar 100% no OPERACIONAL, use o mesmo processo para:

1. **Módulo Financeiro** (se for o próximo prioritário)
2. **Módulo Comercial**
3. **Módulo Integrations**
4. Etc.

**Processo padronizado:**
```bash
# 1. Extrair spec do módulo
python3 extract-modulo-spec.py --module financeiro

# 2. Gerar tipos
npm run orval:financeiro

# 3. Implementar services manualmente

# 4. Criar UI
```

---

## 🏆 RESULTADO FINAL

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   MÓDULO OPERACIONAL: 100% COBERTURA                      ║
║                                                           ║
║   ✅ 130 endpoints implementados                          ║
║   ✅ Tipos TypeScript sincronizados automaticamente       ║
║   ✅ Services e hooks no padrão do projeto               ║
║   ✅ WebSocket com reconexão automática                   ║
║   ✅ Sistema de comunicação completo                      ║
║   ✅ Workflow disciplinar CLT-compliant                   ║
║   ✅ Notificações em tempo real                           ║
║                                                           ║
║   🎯 OBJETIVO ALCANÇADO!                                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

**COMECE AGORA! 🚀**

Execute o Passo 1 e siga em frente!

```bash
cd /opt/conecta-pro/frontend
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/openapi-operacional.json ./
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/orval.config.operacional.ts ./
```