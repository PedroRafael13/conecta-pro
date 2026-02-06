# 🎯 IMPLEMENTAÇÃO ORVAL + COBERTURA 100% - MÓDULO RECRUITMENT

**Data Criação:** 28/01/2026
**Status:** 📋 PLANO COMPLETO - AGUARDANDO EXECUÇÃO
**Módulo:** Recruitment (Recrutamento e Seleção)
**Estimativa:** 27 horas

---

## 📊 SITUAÇÃO ATUAL

```
Backend:  ✅ 79 endpoints (100%)
Frontend: ❌ 0% cobertura (NADA EXISTE)
```

**Endpoints por submódulo:**
- Job Positions (Vagas): 15 endpoints
- Candidates (Candidatos): 23 endpoints
- Applications (Candidaturas): 27 endpoints
- Interviews (Entrevistas): 24 endpoints

---

## 📁 ESTRUTURA DE ARQUIVOS

```
/opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/
├── README.md (este arquivo)
├── 01-ANALISE-RECRUITMENT.md (análise completa)
├── extract-recruitment-spec.py (script pronto)
├── orval.config.recruitment.ts (será criado)
├── openapi-conecta-pro.json (baixar do backend)
└── openapi-recruitment.json (será gerado)

/opt/conecta-pro/frontend/
├── src/
│   ├── types/generated/recruitment/ (gerado pelo Orval)
│   ├── lib/services/recruitment.ts (service completo - 79 métodos)
│   ├── hooks/recruitment/ (React Query hooks)
│   ├── components/recruitment/ (componentes UI)
│   └── app/modulos/recrutamento/page.tsx (página principal)
```

---

## ⚡ EXECUÇÃO RÁPIDA (QUANDO BACKEND ESTIVER ONLINE)

### Passo 1: Baixar OpenAPI Spec (5min)

```bash
cd /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026

# Verificar se backend está online
curl http://localhost:8080/health

# Baixar spec completo
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json

# Verificar se baixou corretamente
ls -lh openapi-conecta-pro.json
```

### Passo 2: Extrair Spec do Recruitment (5min)

```bash
# Executar script de extração
python3 extract-recruitment-spec.py

# Verificar resultado
ls -lh openapi-recruitment.json

# Deve mostrar:
# - 79 endpoints do recruitment
# - Redução de ~90% no tamanho do arquivo
```

### Passo 3: Copiar para Frontend e Configurar Orval (10min)

```bash
cd /opt/conecta-pro/frontend

# Copiar spec do recruitment
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/openapi-recruitment.json ./

# Criar arquivo de configuração Orval
cat > orval.config.recruitment.ts << 'EOF'
/**
 * Configuração Orval - Módulo RECRUITMENT (Recrutamento e Seleção)
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Uso:
 *   npm run orval:recruitment
 */

module.exports = {
  recruitment: {
    input: {
      // OpenAPI spec apenas do módulo RECRUITMENT (79 endpoints)
      target: './openapi-recruitment.json',
    },
    output: {
      // Gerar arquivos separados por tag
      mode: 'tags-split',

      // Destino dos arquivos gerados
      target: './src/types/generated/recruitment',

      // Usar axios como client
      client: 'axios',

      // Não gerar mocks
      mock: false,
    },
  },
};
EOF

# Adicionar script no package.json
# (adicionar manualmente ou via sed)
# "orval:recruitment": "orval --config orval.config.recruitment.ts"

# Instalar Orval se ainda não estiver instalado
npm install -D orval

# Gerar tipos
npm run orval:recruitment

# Verificar tipos gerados
ls -la src/types/generated/recruitment/
```

**Resultado esperado:**
```
src/types/generated/recruitment/
├── recruitment-vagas.ts       (Job Positions types)
├── recruitment-candidatos.ts  (Candidates types)
├── recruitment-candidaturas.ts (Applications types)
├── recruitment-entrevistas.ts (Interviews types)
└── common.ts                  (tipos compartilhados)
```

### Passo 4: Criar Service Layer (8h)

Criar `/opt/conecta-pro/frontend/src/lib/services/recruitment.ts`

Ver arquivo completo em: `02-SERVICE-RECRUITMENT.md` (será criado)

**Estrutura:**
```typescript
// 15 métodos Job Positions
// 23 métodos Candidates
// 27 métodos Applications
// 24 métodos Interviews
// Total: 79 métodos
```

### Passo 5: Criar Hooks React Query (4h)

Criar `/opt/conecta-pro/frontend/src/hooks/recruitment/`

**Arquivos:**
- `useJobPositions.ts` (vagas)
- `useCandidates.ts` (candidatos)
- `useApplications.ts` (candidaturas)
- `useInterviews.ts` (entrevistas)

### Passo 6: Criar Componentes UI (6h)

Criar `/opt/conecta-pro/frontend/src/components/recruitment/`

**Componentes principais:**
- VacancyForm, VacancyList, VacancyCard
- CandidateForm, CandidateList, CandidateCard
- ApplicationBoard (kanban de candidaturas)
- InterviewScheduler, InterviewCalendar

### Passo 7: Criar Página (3h)

Criar `/opt/conecta-pro/frontend/src/app/modulos/recrutamento/page.tsx`

Dashboard completo com:
- Resumo de métricas
- Vagas ativas
- Candidaturas em andamento
- Entrevistas agendadas

### Passo 8: Testes (4h)

- Testar cada endpoint
- Validar integração
- Documentar problemas encontrados

### Passo 9: Documentação (1h)

- README do módulo
- Exemplos de uso
- Guia de manutenção

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Setup Orval ✅ (CRIADO)
- [x] Script extract-recruitment-spec.py criado
- [x] Análise completa documentada
- [ ] Backend online
- [ ] OpenAPI spec baixado
- [ ] Spec do recruitment extraído
- [ ] Orval config criado
- [ ] Tipos TypeScript gerados

### Fase 2: Service Layer
- [ ] Criar `/src/lib/services/recruitment.ts`
- [ ] Implementar Job Positions service (15 métodos)
- [ ] Implementar Candidates service (23 métodos)
- [ ] Implementar Applications service (27 métodos)
- [ ] Implementar Interviews service (24 métodos)
- [ ] Validar tipos TypeScript

### Fase 3: React Query Hooks
- [ ] Criar `/src/hooks/recruitment/useJobPositions.ts`
- [ ] Criar `/src/hooks/recruitment/useCandidates.ts`
- [ ] Criar `/src/hooks/recruitment/useApplications.ts`
- [ ] Criar `/src/hooks/recruitment/useInterviews.ts`

### Fase 4: Componentes UI
- [ ] Job Positions components
- [ ] Candidates components
- [ ] Applications components (incluindo Kanban Board)
- [ ] Interviews components (incluindo Calendar)

### Fase 5: Página Principal
- [ ] Criar `/src/app/modulos/recrutamento/page.tsx`
- [ ] Dashboard com métricas
- [ ] Navegação entre submódulos

### Fase 6: Testes
- [ ] Testar CRUD de vagas
- [ ] Testar CRUD de candidatos
- [ ] Testar workflow de candidaturas
- [ ] Testar agendamento de entrevistas
- [ ] Testes de integração

### Fase 7: Documentação
- [ ] README do módulo
- [ ] Exemplos de código
- [ ] Guia de manutenção

---

## 🎯 PRÓXIMOS PASSOS

1. **Quando backend estiver online:**
   - Executar Passo 1 (baixar OpenAPI)
   - Executar Passo 2 (extrair spec recruitment)
   - Executar Passo 3 (gerar tipos Orval)

2. **Desenvolvimento:**
   - Seguir ordem: Service → Hooks → Componentes → Página
   - Testar incrementalmente
   - Documentar problemas encontrados

3. **Validação:**
   - Cada endpoint deve ser testado
   - Build sem erros TypeScript
   - Coverage de 100% dos 79 endpoints

---

## 📚 ARQUIVOS DE REFERÊNCIA

- `/opt/conecta-pro/docs/auditoria-ged-28-01-2026/` - Modelo GED completo
- `/opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/01-ANALISE-RECRUITMENT.md` - Análise do módulo
- `/opt/conecta-pro/backend/modules/recruitment/` - Código backend (referência de schemas)

---

## ⚠️ IMPORTANTE

**Backend precisa estar online para:**
- Gerar OpenAPI spec
- Extrair spec do recruitment
- Testar endpoints

**Após implementação completa:**
- 100% de cobertura dos 79 endpoints
- Tipos sincronizados automaticamente com backend
- Manutenção via `npm run orval:recruitment`

---

**Criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
