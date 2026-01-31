# PLANO DE AÇÃO: MIGRAÇÃO SERVICES → ORVAL

**Base:** AUDITORIA_SERVICES_MANUAIS.md
**Data:** 2026-01-31

---

## 🎯 OBJETIVO

Migrar services manuais para hooks Orval, eliminando duplicação e padronizando consumo da API.

---

## 📅 CRONOGRAMA

### FASE 1: DELETAR SERVICES VAZIOS (1h)
**Prioridade:** 🔥 URGENTE
**Impacto:** Zero (arquivos vazios)

```bash
# Total: 17 arquivos vazios

# Clients (6 arquivos)
rm src/services/clients/clientAIService.ts
rm src/services/clients/condominiumService.ts
rm src/services/clients/unitService.ts
rm src/services/clients/integrationService.ts
rm src/services/clients/contractService.ts
# MANTER: src/services/clients/clientService.ts (tem re-exports Orval)

# Government (7 arquivos vazios)
rm src/services/government/fgts-simples.service.ts
rm src/services/government/govbr-ecac.service.ts
rm src/services/government/nfse.service.ts
rm src/services/government/receita-federal.service.ts
rm src/services/government/sefaz.service.ts
rm src/services/government/sped.service.ts
rm src/services/government/sync-certificates.service.ts
# MANTER: src/services/government/esocial.service.ts (tem código)

# Bidding (4 arquivos vazios)
rm src/services/bidding/certificates.service.ts
rm src/services/bidding/contracts.service.ts
rm src/services/bidding/documents.service.ts
rm src/services/bidding/proposals.service.ts
# MANTER: src/services/bidding/tenders.service.ts (funcional)

# Mobile (1 arquivo vazio)
rm src/services/mobile/pushNotificationService.ts
```

**Validação:**
```bash
npm run build
npm run lint
```

---

### FASE 2: MIGRAR SECURITY-LGPD (4h)
**Prioridade:** 🔥🔥🔥 CRÍTICA
**Impacto:** ALTO (20 imports, módulo crítico LGPD)

#### Services a migrar:

| Service | Funções | Hook Orval | Novo Hook |
|---------|---------|------------|-----------|
| `encryptionService.ts` | 1 | `security-lgpd` | `useEncryption` |
| `maskingService.ts` | 1 | `security-lgpd` | `useMasking` |
| `consentService.ts` | 1 | `security-lgpd` | `useConsent` |
| `auditService.ts` | 1 | `security-lgpd` | `useAudit` |
| `erasureService.ts` | 1 | `security-lgpd` | `useErasure` |
| `statusService.ts` | 1 | `security-lgpd` | `useStatus` |
| `piaService.ts` | 1 | `security-lgpd` | `usePIA` |

#### Tarefas:

1. **Criar hooks** (2h)
   ```bash
   # Já existem em src/hooks/security-lgpd/
   # Verificar e atualizar para usar hooks Orval:
   - src/hooks/security-lgpd/useEncryption.ts
   - src/hooks/security-lgpd/useMasking.ts
   - src/hooks/security-lgpd/useConsent.ts
   - src/hooks/security-lgpd/useAudit.ts
   - src/hooks/security-lgpd/useErasure.ts
   - src/hooks/security-lgpd/useStatus.ts
   - src/hooks/security-lgpd/usePIA.ts
   ```

2. **Buscar e substituir imports** (1h)
   ```bash
   # Encontrar usos
   grep -r "from.*@/services/security-lgpd" src/

   # Substituir manualmente por:
   # import { useEncryption } from '@/hooks/security-lgpd/useEncryption'
   ```

3. **Marcar services como deprecated** (0.5h)
   ```typescript
   /**
    * @deprecated Use hooks de @/hooks/security-lgpd
    */
   ```

4. **Testar** (0.5h)
   ```bash
   npm run build
   npm run test
   ```

**Validação:**
- [ ] Build sem erros
- [ ] Testes passando
- [ ] Funcionalidades LGPD OK
- [ ] Performance OK

---

### FASE 3: MIGRAR NOTIFICATIONS (3h)
**Prioridade:** 🔥🔥 ALTA
**Impacto:** MÉDIO (5 imports, usado em hooks)

#### Services a migrar:

| Service | Funções | Uso |
|---------|---------|-----|
| `notification.service.ts` | 2 | Hooks |
| `preference.service.ts` | 2 | Hooks |
| `intelligent.service.ts` | 2 | Hooks |
| `template.service.ts` | 2 | Hooks |
| `push.service.ts` | 2 | Hooks |

#### Hooks Orval disponíveis:
```typescript
// src/types/generated/notifications/notifications
- useListNotificationsApiV1NotificationsGet
- useMarkAsReadApiV1NotificationsNotificationIdReadPut
- useMarkAllAsReadApiV1NotificationsMarkAllReadPost
- useListPreferencesApiV1NotificationsPreferencesGet
- useUpdatePreferenceApiV1NotificationsPreferencesPreferenceIdPut
// ... etc (5 arquivos, ~20 hooks)
```

#### Tarefas:

1. **Criar hooks custom** (1.5h)
   ```bash
   src/hooks/notifications/
   ├── useNotifications.ts       # Lista, mark as read
   ├── useNotificationPreferences.ts
   ├── useIntelligentNotifications.ts
   ├── useNotificationTemplates.ts
   └── usePushNotifications.ts
   ```

2. **Migrar imports** (1h)

3. **Testar** (0.5h)

**Validação:**
- [ ] Notificações funcionando
- [ ] Preferências salvando
- [ ] Push notifications OK

---

### FASE 4: MIGRAR REIMBURSEMENT (3h)
**Prioridade:** 🔥🔥 ALTA
**Impacto:** MÉDIO (5 imports, 112 hooks Orval)

#### Services a migrar:

| Service | Funções |
|---------|---------|
| `reimbursementRequestService.ts` | 1 |
| `reimbursementApprovalService.ts` | 1 |
| `reimbursementItemService.ts` | 1 |
| `reimbursementPaymentService.ts` | 1 |
| `reimbursementAttachmentService.ts` | 1 |

#### Hooks Orval: 112 arquivos em `src/types/generated/reimbursement/`

#### Tarefas:

1. **Criar hooks** (1.5h)
   ```bash
   src/hooks/reimbursement/
   ├── useReimbursementRequests.ts
   ├── useReimbursementApprovals.ts
   ├── useReimbursementItems.ts
   ├── useReimbursementPayments.ts
   └── useReimbursementAttachments.ts
   ```

2. **Migrar imports** (1h)

3. **Testar** (0.5h)

---

### FASE 5: MIGRAR SCHEDULER (2h)
**Prioridade:** 🔄 MÉDIA
**Impacto:** BAIXO (6 imports, sistema interno)

#### Services a migrar:

| Service | Funções |
|---------|---------|
| `tasks.service.ts` | 10 |
| `queue.service.ts` | 4 |
| `locks.service.ts` | 4 |
| `executions.service.ts` | 4 |
| `workers.service.ts` | 3 |
| `operations.service.ts` | 1 |

#### Hooks Orval: 145 arquivos

#### Tarefas:

1. **Criar hooks** (1h)
2. **Migrar** (0.5h)
3. **Testar** (0.5h)

---

### FASE 6: MIGRAR DOCUMENTS (2h)
**Prioridade:** 🔄 MÉDIA
**Impacto:** BAIXO (4 imports)

#### Services a migrar:

| Service | Funções |
|---------|---------|
| `upload.ts` | 2 |
| `processing.ts` | 5 |
| `metadata.ts` | 5 |
| `templates.ts` | 4 |

#### Verificar: `src/types/generated/documents.ts`

---

### FASE 7: MIGRAR EQUIPMENT (1.5h)
**Prioridade:** 🔄 BAIXA
**Impacto:** BAIXO (4 imports)

#### Services a migrar:

| Service | Funções |
|---------|---------|
| `equipmentService.ts` | 1 |
| `maintenanceService.ts` | 1 |
| `installationService.ts` | 1 |
| `comodatoService.ts` | 1 |

---

### FASE 8: MIGRAR MOBILE (1h)
**Prioridade:** 🔄 BAIXA
**Impacto:** BAIXO (4 imports)

---

### FASE 9: MIGRAR WORKFLOWS (1h)
**Prioridade:** 🔄 BAIXA
**Impacto:** BAIXO (3 imports)

---

### FASE 10: MIGRAR SEARCH (0.5h)
**Prioridade:** 🔄 BAIXA
**Impacto:** BAIXO (1 import)

---

## 🔧 MÓDULOS PARA MANTER (Sem Orval)

### AI (13 arquivos)
**Motivo:** Módulo IA sem spec OpenAPI
**Ação:** MANTER como está

### ANALYTICS (8 arquivos)
**Motivo:** Já usa hooks de `/api/generated/analytics/`
**Ação:** VERIFICAR e documentar padrão

### CONFIG (7 arquivos)
**Motivo:** Já usa schemas de `/types/generated/config/`
**Ação:** VERIFICAR estrutura

### CAMPO (11 arquivos)
**Motivo:** 12 imports, sem spec OpenAPI
**Ação:** MANTER ou GERAR SPEC (futuro)

### DIARISTS (3 arquivos)
**Motivo:** 9 imports, muito usado
**Ação:** 🔥 GERAR SPEC OPENAPI (priorizar)

### HR (6 arquivos)
**Motivo:** 6 imports
**Ação:** MANTER ou GERAR SPEC (futuro)

### CONTRACTS (5 arquivos)
**Motivo:** 5 imports
**Ação:** MANTER ou GERAR SPEC (futuro)

### AUDIT (6 arquivos)
**Motivo:** Sem spec
**Ação:** MANTER ou GERAR SPEC (futuro)

### DOCUMENT-KITS (6 arquivos)
**Motivo:** 0 imports diretos
**Ação:** MANTER

### BIDDING (1 arquivo)
**Motivo:** `tenders.service.ts` funcional
**Ação:** MANTER

### GOVERNMENT (1 arquivo)
**Motivo:** `esocial.service.ts` com 8 funções
**Ação:** MIGRAR para hooks Orval ou MANTER

---

## 📊 RESUMO DO PLANO

| Fase | Módulo | Tempo | Prioridade | Status |
|------|--------|-------|------------|--------|
| 1 | Deletar vazios | 1h | 🔥🔥🔥 | ⏳ Pendente |
| 2 | security-lgpd | 4h | 🔥🔥🔥 | ⏳ Pendente |
| 3 | notifications | 3h | 🔥🔥 | ⏳ Pendente |
| 4 | reimbursement | 3h | 🔥🔥 | ⏳ Pendente |
| 5 | scheduler | 2h | 🔄 | ⏳ Pendente |
| 6 | documents | 2h | 🔄 | ⏳ Pendente |
| 7 | equipment | 1.5h | 🔄 | ⏳ Pendente |
| 8 | mobile | 1h | 🔄 | ⏳ Pendente |
| 9 | workflows | 1h | 🔄 | ⏳ Pendente |
| 10 | search | 0.5h | 🔄 | ⏳ Pendente |

**Total estimado:** ~19 horas

---

## ✅ CRITÉRIOS DE SUCESSO

### Por Módulo:
- [ ] Hooks Orval identificados e documentados
- [ ] Hooks custom criados em `src/hooks/<modulo>/`
- [ ] Todos imports do service manual substituídos
- [ ] Service manual marcado como `@deprecated`
- [ ] Build sem erros TypeScript
- [ ] Testes passando
- [ ] Funcionalidade validada manualmente

### Global:
- [ ] Zero services vazios
- [ ] Services manuais apenas onde não há Orval
- [ ] Documentação atualizada
- [ ] Performance mantida ou melhorada
- [ ] Cobertura de testes OK

---

## 🚀 PRÓXIMOS PASSOS

1. **Imediato (Hoje):**
   - Executar FASE 1 (deletar vazios)
   - Iniciar FASE 2 (security-lgpd)

2. **Esta Semana:**
   - Completar FASE 2, 3, 4
   - Validar módulos críticos

3. **Próxima Semana:**
   - Completar FASE 5-10
   - Revisar módulos a manter

4. **Futuro:**
   - Gerar specs OpenAPI para diarists
   - Considerar gerar specs para campo, hr, contracts
   - Consolidar padrão de hooks Orval

---

## 📝 COMANDOS ÚTEIS

```bash
# Buscar imports de service específico
grep -r "from.*@/services/<modulo>" src/

# Contar imports
grep -r "from.*@/services/" src/ | wc -l

# Listar hooks Orval de módulo
ls -la src/types/generated/<modulo>/

# Verificar build
npm run build

# Rodar testes
npm run test

# Lint
npm run lint
```

---

**Criado em:** 2026-01-31
**Responsável:** Equipe Frontend
**Revisão:** Semanal
