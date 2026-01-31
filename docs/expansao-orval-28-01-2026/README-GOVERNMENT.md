# 📦 PACOTE COMPLETO - GOVERNMENT INTEGRATIONS 100%

**Data:** 28/01/2026
**Módulo:** GOVERNMENT INTEGRATIONS (Integrações Governamentais)
**Status Atual:** 🔴 26% COBERTURA (56/209 endpoints)
**Status Alvo:** ✅ 100% COBERTURA (209/209 endpoints)
**Prioridade:** 🔴 CRÍTICO (Compliance obrigatório)
**Estratégia:** HÍBRIDA (Orval + Manual)

---

## 🎯 SITUAÇÃO DO MÓDULO

```
╔════════════════════════════════════════════════════════════════╗
║  MÓDULO GOVERNMENT INTEGRATIONS                                ║
╠════════════════════════════════════════════════════════════════╣
║  📦 Endpoints Backend:           209                           ║
║  ✅ Endpoints Implementados:     56 (26%)                      ║
║  ❌ Endpoints FALTANTES:         153 (74%)                     ║
║  📁 Controllers:                 24                            ║
║  🎯 Prioridade:                  CRÍTICO (Compliance)          ║
║  ⏱️  Tempo Estimado:             40h (~1 semana)              ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 📁 ARQUIVOS DESTE PACOTE

### 1. 🚀 EXECUTE-AGORA-GOVERNMENT.md (COMECE AQUI!)
**Tamanho:** 11KB
**Descrição:** Guia passo-a-passo para setup inicial (5 minutos)

**Conteúdo:**
- Quick Start em 8 passos
- Comandos prontos para copiar/colar
- Checkpoints de validação
- Troubleshooting completo

**👉 LEIA ESTE PRIMEIRO!**

---

### 2. 🎯 MISSAO-GOVERNMENT-INTEGRATIONS.md
**Tamanho:** 32KB
**Descrição:** Plano completo de implementação (40h)

**Conteúdo:**
- Gap analysis detalhado (209 endpoints)
- Roadmap de 7 fases
- Estrutura completa do service layer
- Hooks React Query (24 hooks)
- Componentes UI
- Testes e documentação
- Pontos críticos de compliance

**Objetivo:** Documentação completa para implementação

---

### 3. 🐍 extract-government-spec.py
**Tamanho:** 6.3KB
**Descrição:** Script Python para extrair apenas endpoints Government

**Funcionalidade:**
- Filtra apenas `/api/v1/government/` do OpenAPI completo
- Inclui schemas referenciados recursivamente
- Reduz de 2.28MB para ~420KB (81.6% de redução)
- Estatísticas detalhadas por controller

**Uso:**
```bash
python3 extract-government-spec.py
```

**Saída esperada:**
```
✅ Endpoints extraídos: 209
📦 Schemas copiados: 158
📊 Redução: 81.6%
```

---

### 4. ⚙️ orval.config.government.ts
**Tamanho:** 503 bytes
**Descrição:** Configuração do Orval para Government

**Configuração:**
- Input: `./openapi-government.json`
- Output: `./src/types/generated/government/`
- Mode: `tags-split` (separa por tags/controllers)
- Client: `axios`
- Mutator: `./src/lib/api.ts`

**Uso:**
```bash
npm run orval:government
```

**Resultado:** 158 tipos TypeScript gerados automaticamente

---

## 🚀 QUICK START (5 MINUTOS)

### Requisitos
- Backend rodando em `http://localhost:8080`
- Python 3.8+ instalado
- Node.js 18+ instalado
- Frontend em `/opt/conecta-pro/frontend`

### Passos

```bash
# 1. Baixar OpenAPI completo (30s)
cd /opt/conecta-pro/docs/expansao-orval-28-01-2026
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json

# 2. Extrair apenas Government (30s)
python3 extract-government-spec.py

# 3. Copiar arquivos para frontend (10s)
cd /opt/conecta-pro/frontend
cp /opt/conecta-pro/docs/expansao-orval-28-01-2026/openapi-government.json ./
cp /opt/conecta-pro/docs/expansao-orval-28-01-2026/orval.config.government.ts ./

# 4. Instalar Orval (1min)
npm install -D orval

# 5. Adicionar script no package.json (30s)
# Adicione: "orval:government": "orval --config orval.config.government.ts"

# 6. Gerar tipos (1min)
npm run orval:government

# 7. Verificar (30s)
ls -la src/types/generated/government/models/
npm run types:check
```

**Resultado final:**
```
✅ 158 tipos TypeScript gerados
✅ Build sem erros
✅ Pronto para implementar service layer
```

---

## 📊 DISTRIBUIÇÃO DE ENDPOINTS

| Controller | Endpoints | Status | Prioridade |
|------------|-----------|--------|------------|
| **Sincronização** | 16 | ⚠️ Parcial | 🔴 Crítico |
| **SPED Fiscal** | 13 | ⚠️ Parcial | 🔴 Crítico |
| **SPED Contábil** | 13 | ⚠️ Parcial | 🔴 Crítico |
| **NFS-e Nacional** | 12 | ⚠️ Parcial | 🔴 Crítico |
| **GOV.BR** | 12 | ❌ Ausente | 🟢 Médio |
| **FGTS Digital** | 11 | ❌ Ausente | 🔴 Crítico |
| **DCTFWeb** | 11 | ❌ Ausente | 🟡 Alto |
| **Simples Nacional** | 10 | ❌ Ausente | 🟡 Alto |
| **CT-e** | 10 | ❌ Ausente | 🟢 Médio |
| **Extração** | 10 | ❌ Ausente | 🟢 Médio |
| **MDF-e** | 14 | ❌ Ausente | 🟢 Médio |
| **NFC-e** | 9 | ❌ Ausente | 🟡 Alto |
| **EFD-Reinf** | 9 | ❌ Ausente | 🟡 Alto |
| **e-CAC** | 9 | ❌ Ausente | 🟡 Alto |
| **NFS-e Manaus** | 8 | ⚠️ Parcial | 🔴 Crítico |
| **SEFAZ-AM** | 8 | ⚠️ Parcial | 🟡 Alto |
| **Jobs** | 8 | ❌ Ausente | 🟡 Alto |
| **Certificado** | 7 | ❌ Ausente | 🟡 Alto |
| **Dashboard** | 6 | ❌ Ausente | 🟢 Médio |
| **eSocial** | 3 | ⚠️ Parcial | 🔴 Crítico |
| **FGTS/INSS** | 3 | ⚠️ Parcial | 🔴 Crítico |
| **Receita Federal** | 3 | ✅ Completo | ✅ |
| **SEFAZ** | 2 | ⚠️ Parcial | 🔴 Crítico |
| **Status** | 2 | ✅ Completo | ✅ |

**TOTAL:** 209 endpoints

---

## 📋 ROADMAP DE IMPLEMENTAÇÃO

### FASE 1: ANÁLISE E SETUP (4h)
- [ ] Baixar OpenAPI spec completo
- [ ] Criar script de extração
- [ ] Configurar Orval
- [ ] Gerar tipos TypeScript

**Entregável:** 158 tipos gerados

---

### FASE 2: SERVICE LAYER (12h)
- [ ] Criar arquivo `government.ts`
- [ ] Implementar 24 sub-services
- [ ] 209 métodos usando tipos do Orval
- [ ] Documentação inline

**Entregável:** Service completo

---

### FASE 3: HOOKS REACT QUERY (8h)
- [ ] Criar `useGovernment.ts`
- [ ] 24 hooks (um por integração)
- [ ] Polling para status
- [ ] Cache inteligente

**Entregável:** Hooks para todas integrações

---

### FASE 4: COMPONENTES UI (8h)
- [ ] Dashboard de integrações
- [ ] Status cards por integração
- [ ] Job monitor em tempo real
- [ ] Logs viewer
- [ ] Conectividade status

**Entregável:** UI completa

---

### FASE 5: PÁGINA (3h)
- [ ] Refatorar `fiscal/page.tsx`
- [ ] Remover ComingSoon
- [ ] Implementar tabs de navegação
- [ ] Dashboard visível

**Entregável:** Página funcional

---

### FASE 6: TESTES (4h)
- [ ] Testes de service (209 métodos)
- [ ] Testes de hooks (24 hooks)
- [ ] Testes de integração
- [ ] Cobertura >80%

**Entregável:** Testes completos

---

### FASE 7: DOCUMENTAÇÃO (2h)
- [ ] README do service
- [ ] Guia de configuração por órgão
- [ ] Exemplos de uso
- [ ] Troubleshooting

**Entregável:** Documentação completa

---

**TOTAL:** 40 horas (~1 semana)

---

## 🚨 PONTOS CRÍTICOS

### 1. Compliance Obrigatório
- ⚠️ **NFS-e:** Obrigatório para prestadores de serviço
- ⚠️ **eSocial:** Obrigatório para folha de pagamento
- ⚠️ **SEFAZ:** Obrigatório para emissão de notas fiscais
- ⚠️ **SPED:** Obrigatório para escrituração fiscal

**Impacto:** Sem estas integrações, o sistema **NÃO pode ser usado em produção**.

---

### 2. Certificado Digital A1
- ⚠️ Obrigatório para: NFS-e, NF-e, CT-e, MDF-e
- ⚠️ Validação de expiração necessária
- ⚠️ Renovação automática recomendada
- ⚠️ Armazenamento seguro (criptografado)

**Implementar:**
- Validador de certificado
- Alerta de expiração (30 dias)
- Upload de novo certificado

---

### 3. Credenciais GOV.BR
- ⚠️ Obrigatório para: eSocial, FGTS Digital
- ⚠️ Token com expiração (geralmente 24h)
- ⚠️ Refresh automático necessário
- ⚠️ Autenticação Gov.BR Login

**Implementar:**
- OAuth2 flow
- Token refresh automático
- Fallback para manual

---

### 4. Rate Limiting
- ⚠️ **Receita Federal:** 20 requisições/minuto
- ⚠️ **eSocial:** 100 eventos/hora
- ⚠️ **SEFAZ:** Varia por estado
- ⚠️ **Prefeituras:** Varia por município

**Implementar:**
- Queue de requisições
- Retry com exponential backoff
- Circuit breaker

---

### 5. Ambientes (Produção/Homologação)
- ⚠️ URLs diferentes por ambiente
- ⚠️ Certificados diferentes
- ⚠️ Credenciais diferentes
- ⚠️ Toggle no frontend

**Implementar:**
- Seletor de ambiente
- Validação por ambiente
- Logs separados

---

### 6. Monitoramento
- ⚠️ Jobs de sincronização falhando
- ⚠️ Certificados expirando
- ⚠️ Conectividade com órgãos
- ⚠️ Erros de validação

**Implementar:**
- Dashboard de monitoramento
- Alertas automáticos
- Logs centralizados

---

## 🎯 RESULTADO ESPERADO

```
╔═══════════════════════════════════════════════════════════╗
║  MÓDULO GOVERNMENT - APÓS IMPLEMENTAÇÃO                   ║
╠═══════════════════════════════════════════════════════════╣
║  ✅ Cobertura:                209/209 (100%)              ║
║  ✅ Tipos sincronizados:      AUTOMÁTICO                  ║
║  ✅ Service completo:          24 sub-services            ║
║  ✅ Hooks React Query:         24 hooks                   ║
║  ✅ Dashboard:                 IMPLEMENTADO               ║
║  ✅ Monitoramento:             TEMPO REAL                 ║
║  ✅ Testes:                    >80% COBERTURA             ║
║  ✅ Documentação:              COMPLETA                   ║
║                                                           ║
║  🎯 COMPLIANCE GOVERNAMENTAL GARANTIDO                    ║
║  🎯 SISTEMA PRONTO PARA PRODUÇÃO                          ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🔄 MANUTENÇÃO FUTURA

Quando o backend mudar (tempo: ~3 minutos):

```bash
# 1. Baixar novo spec
cd /opt/conecta-pro/docs/expansao-orval-28-01-2026
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json

# 2. Extrair Government
python3 extract-government-spec.py

# 3. Copiar para frontend
cp openapi-government.json /opt/conecta-pro/frontend/

# 4. Regerar tipos
cd /opt/conecta-pro/frontend
npm run orval:government

# 5. Verificar
npm run types:check

# 6. Build
npm run build
```

**Benefício:** Sincronização automática entre backend e frontend!

---

## 📊 COMPARAÇÃO COM GED (MODELO DE REFERÊNCIA)

| Aspecto | GED | GOVERNMENT |
|---------|-----|------------|
| Endpoints Backend | 138 | **209** (+51%) |
| Cobertura Atual | 100% | 26% |
| Gap | 0 | **153 endpoints** |
| Complexidade | Médio | **Alto** |
| Compliance | Opcional | **Obrigatório** |
| Certificados | Não | **Sim (A1)** |
| Credenciais Gov | Não | **Sim (GOV.BR)** |
| Rate Limiting | Não | **Sim (variável)** |
| Prioridade | 🟢 Médio | 🔴 **Crítico** |
| Tempo para 100% | 0h | 40h |

**Conclusão:** Government tem **51% mais endpoints** que GED e é **crítico** para o negócio.

---

## 🔮 PRÓXIMOS MÓDULOS

Após concluir Government Integrations, replicar processo para:

1. **Operacional** (130 endpoints, 77% cobertura → 100%)
2. **Recruitment** (162 endpoints, 0% cobertura)
3. **AI** (85 endpoints, 0% cobertura)
4. **Audit** (54 endpoints, 0% cobertura)

**Processo padronizado:**
```bash
# 1. Criar script
cp extract-government-spec.py extract-operacional-spec.py
# Editar filtro: /api/v1/operacional/

# 2. Criar config
cp orval.config.government.ts orval.config.operacional.ts
# Editar paths

# 3. Gerar tipos
npm run orval:operacional

# 4. Implementar service
cp government.ts operacional.ts
```

---

## 💡 DICAS PRO

### 1. Watch Mode (desenvolvimento)
```bash
# Terminal 1: Regera tipos automaticamente
npm run orval:government:watch

# Terminal 2: Dev server
npm run dev

# Terminal 3: Type checking contínuo
npm run types:check -- --watch
```

### 2. VS Code Settings
```json
// .vscode/settings.json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.suggest.autoImports": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### 3. Git Hooks
```bash
# .husky/pre-commit
#!/bin/sh
npm run types:check
npm run build
```

### 4. CI/CD
```yaml
# .github/workflows/sync-types.yml
name: Sync Government Types

on:
  push:
    paths:
      - 'backend/modules/government_integrations/**'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Generate types
        run: npm run orval:government
      - name: Check types
        run: npm run types:check
      - name: Commit changes
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: 'chore: sync government types'
```

---

## 🎓 REFERÊNCIAS

### Documentação Técnica
- **Orval:** https://orval.dev/
- **React Query:** https://tanstack.com/query/latest
- **OpenAPI:** https://swagger.io/specification/
- **Axios:** https://axios-http.com/

### Documentação Governamental
- **NFS-e Nacional:** http://www.nfse.gov.br/
- **eSocial:** https://www.gov.br/esocial/
- **SEFAZ (NF-e):** http://www.nfe.fazenda.gov.br/
- **SPED:** http://sped.rfb.gov.br/
- **GOV.BR:** https://www.gov.br/governodigital/

### Backend Conecta PRO
- **Controllers:** `/opt/conecta-pro/backend/modules/government_integrations/controllers/`
- **Models:** `/opt/conecta-pro/backend/modules/government_integrations/models/`
- **Schemas:** `/opt/conecta-pro/backend/modules/government_integrations/schemas/`

### Frontend Conecta PRO (a criar)
- **Service:** `/opt/conecta-pro/frontend/src/lib/services/government.ts`
- **Hooks:** `/opt/conecta-pro/frontend/src/hooks/useGovernment.ts`
- **Tipos:** `/opt/conecta-pro/frontend/src/types/generated/government/`

---

## 📞 SUPORTE

### Problemas Comuns

**1. Backend não responde**
```bash
# Verificar containers
docker ps | grep backend

# Ver logs
docker logs conecta-backend -n 100

# Restart
docker compose restart backend
```

**2. OpenAPI spec vazio**
```bash
# Verificar endpoint
curl http://localhost:8080/openapi.json | jq '.paths | keys | length'
# Deve retornar >1000
```

**3. Orval falha ao gerar**
```bash
# Verificar config
cat orval.config.government.ts

# Modo verbose
npx orval --config orval.config.government.ts --verbose
```

**4. Tipos com erros**
```bash
# Type check detalhado
npx tsc --noEmit --pretty

# Ver erros específicos
npm run types:check 2>&1 | grep "error TS"
```

---

## 🏁 COMECE AGORA!

```bash
cd /opt/conecta-pro/docs/expansao-orval-28-01-2026
cat EXECUTE-AGORA-GOVERNMENT.md
```

**Boa implementação! 🚀**

---

**Pacote criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Versão:** 1.0
**Status:** ✅ PRONTO PARA USO
**Prioridade:** 🔴 CRÍTICO (Compliance obrigatório)
