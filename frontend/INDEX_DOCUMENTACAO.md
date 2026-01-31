# 📚 ÍNDICE DE DOCUMENTAÇÃO - MIGRAÇÃO ORVAL

**Conecta Plus - Frontend Next.js 16**
**Data:** 2026-01-31

---

## 🎯 NAVEGAÇÃO RÁPIDA

### Para começar agora:

1. **📊 [RESUMO_AUDITORIA.md](./RESUMO_AUDITORIA.md)** ← **COMECE AQUI**
   - Resumo executivo em 1 página
   - Situação atual e próximos passos
   - Métricas e prioridades

### Documentação Completa:

2. **📋 [AUDITORIA_SERVICES_MANUAIS.md](./AUDITORIA_SERVICES_MANUAIS.md)**
   - Mapeamento completo de todos services (143 arquivos)
   - Status: Com Orval / Sem Orval / Vazios
   - Priorização detalhada por módulo
   - Análise de uso (127 imports)

3. **🔧 [GUIA_MIGRACAO_SERVICES.md](./GUIA_MIGRACAO_SERVICES.md)**
   - Como identificar service a migrar
   - Padrão de migração step-by-step
   - 4 exemplos práticos completos:
     - Security LGPD - Encryption
     - Notifications - List & Mark as Read
     - Scheduler - Tasks
     - Reimbursement - CRUD completo
   - Checklist de migração
   - Troubleshooting

4. **📅 [PLANO_ACAO_MIGRACAO.md](./PLANO_ACAO_MIGRACAO.md)**
   - Cronograma de 10 fases (~19h total)
   - Comandos prontos para executar
   - Módulos para manter (sem Orval)
   - Critérios de sucesso
   - Fase 1: Deletar vazios (1h) ← **Executar primeiro**

5. **⚡ [QUICK_REFERENCE_ORVAL.md](./QUICK_REFERENCE_ORVAL.md)**
   - Referência rápida de hooks Orval
   - 6 padrões de uso com código
   - Tipos TypeScript
   - React Query - Cache & Revalidation
   - Tratamento de erros
   - Performance (paginação, debounce)
   - Tabela de módulos disponíveis

---

## 🚀 EXECUÇÃO

### Scripts:

6. **🔨 [scripts/fase1-deletar-vazios.sh](./scripts/fase1-deletar-vazios.sh)**
   - Script executável para Fase 1
   - Deleta 17 services vazios com backup
   - Validação automática

**Executar:**
```bash
./scripts/fase1-deletar-vazios.sh
```

---

## 📊 ARQUIVOS DE DADOS

7. **[AUDITORIA_SERVICES_RAW.md](./AUDITORIA_SERVICES_RAW.md)**
   - Dados brutos da auditoria
   - Gerado por `audit_services.sh`

8. **[audit_services.sh](./audit_services.sh)**
   - Script de auditoria automatizada

---

## 🗂️ ESTRUTURA DE LEITURA RECOMENDADA

### Gerente de Projeto / Tech Lead:

```
1. RESUMO_AUDITORIA.md          (5 min)
2. PLANO_ACAO_MIGRACAO.md       (10 min)
3. AUDITORIA_SERVICES_MANUAIS.md (20 min)
```

### Desenvolvedor Frontend (vai implementar):

```
1. RESUMO_AUDITORIA.md           (5 min)
2. GUIA_MIGRACAO_SERVICES.md     (30 min) ← IMPORTANTE
3. QUICK_REFERENCE_ORVAL.md      (15 min) ← Manter aberto
4. PLANO_ACAO_MIGRACAO.md        (10 min)
5. Executar: fase1-deletar-vazios.sh
```

### Revisão Rápida (desenvolvedor experiente):

```
1. QUICK_REFERENCE_ORVAL.md      (consulta)
2. PLANO_ACAO_MIGRACAO.md        (consulta)
```

---

## 📝 FLUXO DE TRABALHO

### Fase 1: Preparação (Hoje)

```bash
# 1. Ler documentação
cat RESUMO_AUDITORIA.md
cat PLANO_ACAO_MIGRACAO.md

# 2. Executar Fase 1
./scripts/fase1-deletar-vazios.sh

# 3. Validar
npm run build
npm run lint

# 4. Commit
git add .
git commit -m "chore: remove services vazios (Fase 1)"
```

### Fase 2-4: Migração Crítica (Esta Semana)

```bash
# Ler guia de migração
cat GUIA_MIGRACAO_SERVICES.md

# Consultar referência rápida
cat QUICK_REFERENCE_ORVAL.md

# Migrar:
# - security-lgpd (4h)
# - notifications (3h)
# - reimbursement (3h)
```

### Fase 5-10: Migração Secundária (Próxima Semana)

```bash
# Seguir PLANO_ACAO_MIGRACAO.md
# Completar módulos restantes (~8h)
```

---

## 🎯 MÓDULOS PARA MIGRAR (Com Orval)

| Prioridade | Módulo | Tempo | Impacto | Doc |
|-----------|--------|-------|---------|-----|
| 🔥🔥🔥 | **security-lgpd** | 4h | 20 imports | GUIA p.1 |
| 🔥🔥 | **notifications** | 3h | 5 imports | GUIA p.2 |
| 🔥🔥 | **reimbursement** | 3h | 5 imports | GUIA p.3 |
| 🔄 | **scheduler** | 2h | 6 imports | QUICK REF |
| 🔄 | **documents** | 2h | 4 imports | QUICK REF |
| 🔄 | **equipment** | 1.5h | 4 imports | QUICK REF |
| 🔄 | **mobile** | 1h | 4 imports | QUICK REF |
| 🔄 | **workflows** | 1h | 3 imports | QUICK REF |
| 🔄 | **search** | 0.5h | 1 import | QUICK REF |

---

## 🔧 MÓDULOS PARA MANTER (Sem Orval)

| Módulo | Motivo | Ação Futura |
|--------|--------|-------------|
| **ai** | Sem spec OpenAPI | Manter |
| **analytics** | Usa `/api/generated/` | Documentar |
| **config** | Usa `/types/generated/` | Documentar |
| **campo** | 12 imports, sem spec | Considerar spec |
| **diarists** | 9 imports, muito usado | **GERAR SPEC** 🔥 |
| **hr** | 6 imports | Considerar spec |
| **contracts** | 5 imports | Considerar spec |
| **audit** | Sem spec | Manter |
| **document-kits** | 0 imports | Manter |
| **bidding** | tenders funcional | Manter |
| **government** | esocial funcional | Manter |

---

## ✅ CHECKLIST GERAL

### Preparação:
- [ ] Ler RESUMO_AUDITORIA.md
- [ ] Ler PLANO_ACAO_MIGRACAO.md
- [ ] Executar scripts/fase1-deletar-vazios.sh
- [ ] Validar build e lint

### Migração:
- [ ] Migrar security-lgpd (Fase 2)
- [ ] Migrar notifications (Fase 3)
- [ ] Migrar reimbursement (Fase 4)
- [ ] Migrar módulos secundários (Fases 5-10)

### Validação:
- [ ] Build sem erros TypeScript
- [ ] Testes passando
- [ ] Funcionalidades validadas
- [ ] Performance OK
- [ ] Documentação atualizada

### Finalização:
- [ ] Deletar services obsoletos
- [ ] Revisar módulos mantidos
- [ ] Gerar specs para diarists (opcional)
- [ ] Atualizar README principal

---

## 📞 SUPORTE

### Dúvidas sobre migração:
- Ver GUIA_MIGRACAO_SERVICES.md (seção Troubleshooting)
- Consultar QUICK_REFERENCE_ORVAL.md

### Problemas técnicos:
- Build: `npm run build`
- Lint: `npm run lint`
- Regenerar Orval: `npm run orval`

### Planejamento:
- Ver PLANO_ACAO_MIGRACAO.md (cronograma detalhado)

---

## 📚 REFERÊNCIAS EXTERNAS

- [React Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [Orval Docs](https://orval.dev/)
- [TypeScript Docs](https://www.typescriptlang.org/)

---

## 📊 STATUS ATUAL

| Item | Status | Atualizado em |
|------|--------|---------------|
| Auditoria completa | ✅ Concluída | 2026-01-31 17:54 |
| Documentação | ✅ Completa | 2026-01-31 17:58 |
| Scripts | ✅ Prontos | 2026-01-31 17:57 |
| Fase 1 | ⏳ Pendente | - |
| Fases 2-10 | ⏳ Pendente | - |

---

**Última atualização:** 2026-01-31 18:00
**Responsável:** Equipe Frontend
**Status:** ✅ Pronto para execução

---

## 🎉 INÍCIO RÁPIDO

```bash
# 1. Ver resumo
cat RESUMO_AUDITORIA.md

# 2. Executar Fase 1
./scripts/fase1-deletar-vazios.sh

# 3. Começar migração
# Ler: GUIA_MIGRACAO_SERVICES.md
# Consultar: QUICK_REFERENCE_ORVAL.md

# Boa sorte! 🚀
```
