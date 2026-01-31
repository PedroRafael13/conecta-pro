# 🚀 EXECUTE AGORA: GOVERNMENT INTEGRATIONS 100%

**Tempo estimado:** 5 minutos para setup inicial
**Objetivo:** Gerar tipos TypeScript sincronizados para 209 endpoints

---

## ⚡ QUICK START (5 MINUTOS)

### Passo 1: Baixar OpenAPI Spec (1min)

```bash
# Verificar se backend está rodando
curl -s http://localhost:8080/health

# Baixar OpenAPI completo
cd /opt/conecta-pro/docs/expansao-orval-28-01-2026
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json

# Verificar tamanho (deve ter ~2MB)
ls -lh openapi-conecta-pro.json
```

**✅ Checkpoint:** Arquivo `openapi-conecta-pro.json` criado com ~2MB

---

### Passo 2: Extrair Apenas Government (1min)

```bash
# Executar script de extração
python3 extract-government-spec.py
```

**Saída esperada:**
```
📖 Lendo OpenAPI spec completo: openapi-conecta-pro.json
📊 Total de endpoints no spec completo: 1246
✅ Endpoints do módulo Government: 209
🔍 Coletando schemas referenciados...
📦 Schemas referenciados: 158
📦 Total de schemas copiados: 158

✨ EXTRAÇÃO CONCLUÍDA!
   Tamanho original: 2.28 MB
   Tamanho otimizado: 0.42 MB
   Redução: 81.6%

📄 Arquivo gerado: openapi-government.json
   Endpoints: 209
   Schemas: 158

📊 ENDPOINTS POR CONTROLLER:
   eSocial: 3 endpoints
   FGTS/INSS: 3 endpoints
   NFS-e Manaus: 8 endpoints
   NFS-e Nacional: 12 endpoints
   SEFAZ: 2 endpoints
   SEFAZ-AM: 8 endpoints
   SPED Fiscal: 13 endpoints
   SPED Contabil: 13 endpoints
   FGTS Digital: 11 endpoints
   EFD-Reinf: 9 endpoints
   DCTFWeb: 11 endpoints
   Simples Nacional: 10 endpoints
   e-CAC: 9 endpoints
   CT-e: 10 endpoints
   MDF-e: 14 endpoints
   NFC-e: 9 endpoints
   GOV.BR: 12 endpoints
   Certificado Digital: 7 endpoints
   Sincronização: 16 endpoints
   Jobs: 8 endpoints
   Dashboard: 6 endpoints
   Extração: 10 endpoints
   Receita Federal: 3 endpoints
   Status: 2 endpoints

✅ TOTAL: 209 endpoints
```

**✅ Checkpoint:** Arquivo `openapi-government.json` criado com ~420KB

---

### Passo 3: Copiar Arquivos para Frontend (30s)

```bash
# Copiar spec e config
cd /opt/conecta-pro/frontend
cp /opt/conecta-pro/docs/expansao-orval-28-01-2026/openapi-government.json ./
cp /opt/conecta-pro/docs/expansao-orval-28-01-2026/orval.config.government.ts ./

# Verificar
ls -lh openapi-government.json orval.config.government.ts
```

**✅ Checkpoint:** Arquivos copiados para `/opt/conecta-pro/frontend/`

---

### Passo 4: Instalar Orval (1min)

```bash
cd /opt/conecta-pro/frontend

# Instalar Orval
npm install -D orval

# Verificar instalação
npx orval --version
```

**✅ Checkpoint:** Orval instalado e funcionando

---

### Passo 5: Adicionar Script no package.json (30s)

```bash
# Abrir package.json e adicionar na seção "scripts":
# "orval:government": "orval --config orval.config.government.ts"
```

**Ou via comando:**

```bash
cd /opt/conecta-pro/frontend

# Backup
cp package.json package.json.backup

# Adicionar script (se não existir)
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
if (!pkg.scripts['orval:government']) {
  pkg.scripts['orval:government'] = 'orval --config orval.config.government.ts';
  fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
  console.log('✅ Script adicionado');
} else {
  console.log('⚠️  Script já existe');
}
"
```

**✅ Checkpoint:** Script `orval:government` adicionado

---

### Passo 6: Gerar Tipos (1min)

```bash
cd /opt/conecta-pro/frontend

# Gerar tipos
npm run orval:government
```

**Saída esperada:**
```
✨ Generated successfully!
   📁 src/types/generated/government/
   ├── index.ts (exports centralizados)
   ├── models/
   │   ├── nfse-manaus.ts
   │   ├── nfse-nacional.ts
   │   ├── esocial.ts
   │   ├── sefaz.ts
   │   ├── sped-fiscal.ts
   │   ├── sped-contabil.ts
   │   ├── fgts-digital.ts
   │   ├── fgts-inss.ts
   │   ├── efd-reinf.ts
   │   ├── dctfweb.ts
   │   ├── simples-nacional.ts
   │   ├── ecac.ts
   │   ├── cte.ts
   │   ├── mdfe.ts
   │   ├── nfce.ts
   │   ├── govbr.ts
   │   ├── certificate.ts
   │   ├── sync.ts
   │   ├── jobs.ts
   │   ├── dashboard.ts
   │   ├── extraction.ts
   │   ├── receita-federal.ts
   │   ├── status.ts
   │   └── common.ts

✅ 158 types generated!
```

**✅ Checkpoint:** Tipos gerados em `src/types/generated/government/`

---

### Passo 7: Verificar Tipos (30s)

```bash
cd /opt/conecta-pro/frontend

# Verificar estrutura
ls -la src/types/generated/government/models/

# Contar tipos gerados
grep -r "^export interface" src/types/generated/government/ | wc -l
grep -r "^export type" src/types/generated/government/ | wc -l
```

**Saída esperada:**
```
~158 interfaces e types
```

**✅ Checkpoint:** Tipos gerados corretamente

---

### Passo 8: Build Test (1min)

```bash
cd /opt/conecta-pro/frontend

# Type check
npm run types:check

# Build test (só compilação)
npm run build
```

**Se houver erros:**
- Verificar se todos os imports estão corretos
- Validar se o `api.ts` existe e exporta o mutator correto

**✅ Checkpoint:** Build sem erros

---

## 🎉 SETUP COMPLETO!

```
╔═══════════════════════════════════════════════════════════╗
║  ✅ SETUP CONCLUÍDO                                       ║
╠═══════════════════════════════════════════════════════════╣
║  📄 OpenAPI spec extraído:      420KB                     ║
║  🎯 Endpoints mapeados:         209                       ║
║  📦 Schemas gerados:            158 tipos                 ║
║  ⚙️  Orval configurado:          ✅                        ║
║  🔧 Build funcionando:          ✅                        ║
║                                                           ║
║  🚀 PRONTO PARA IMPLEMENTAR SERVICE LAYER                 ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📋 PRÓXIMOS PASSOS

### Fase 2: Service Layer (12h)

1. **Criar service base** (4h)
   ```bash
   cd /opt/conecta-pro/frontend/src/lib/services
   touch government.ts
   ```

2. **Implementar 209 métodos** (8h)
   - Seguir estrutura do `MISSAO-GOVERNMENT-INTEGRATIONS.md`
   - Usar tipos gerados do Orval
   - Um sub-service por controller (24 total)

**Estrutura:**
```typescript
// src/lib/services/government.ts
import type * as Gov from '@/types/generated/government';

export const nfseManausService = {
  emitir: (data: Gov.EmitirNFSeRequest) =>
    api.post('/api/v1/government/nfse-manaus/emitir', data),
  // ... 7 métodos
};

export const esocialService = {
  enviarEvento: (data: Gov.ESocialEventRequest) =>
    api.post('/api/v1/government/esocial/evento', data),
  // ... 2 métodos
};

// ... 22 services restantes

export const governmentService = {
  nfseManaus: nfseManausService,
  esocial: esocialService,
  // ... todos os services
};
```

---

### Fase 3: Hooks React Query (8h)

```bash
cd /opt/conecta-pro/frontend/src/hooks
touch useGovernment.ts
```

**Implementar:**
- Hooks para cada integração
- Polling para status
- Cache otimizado
- Invalidation strategies

---

### Fase 4: Componentes UI (8h)

```bash
cd /opt/conecta-pro/frontend/src/components
mkdir -p government
touch government/GovIntegrationsDashboard.tsx
```

**Implementar:**
- Dashboard de integrações
- Status cards
- Job monitor
- Logs viewer

---

### Fase 5: Página (3h)

```bash
cd /opt/conecta-pro/frontend/src/app/modulos/fiscal
# Refatorar page.tsx
```

**Substituir ComingSoon por:**
- Tabs de navegação
- Dashboard completo
- Todas integrações acessíveis

---

## 🔄 MANUTENÇÃO FUTURA

Quando backend mudar:

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
npm run build
```

**Tempo total:** ~3 minutos

---

## 🐛 TROUBLESHOOTING

### Erro: "Backend não responde"
```bash
# Verificar backend
docker ps | grep backend
docker logs conecta-backend -n 50

# Verificar saúde
curl http://localhost:8080/health
```

### Erro: "OpenAPI spec vazio"
```bash
# Verificar conteúdo
cat openapi-conecta-pro.json | jq '.paths | keys | length'
# Deve retornar >1000
```

### Erro: "Orval falha ao gerar"
```bash
# Verificar config
cat orval.config.government.ts

# Testar manualmente
npx orval --config orval.config.government.ts --verbose
```

### Erro: "Tipos com erro de import"
```bash
# Verificar se api.ts existe
ls -la src/lib/api.ts

# Verificar exports
grep "export" src/lib/api.ts
```

### Erro: "Build falha"
```bash
# Type check detalhado
npx tsc --noEmit --pretty

# Ver erros específicos
npm run types:check 2>&1 | grep -A 5 "error TS"
```

---

## 📚 REFERÊNCIAS

- **Documentação completa:** `MISSAO-GOVERNMENT-INTEGRATIONS.md`
- **Orval docs:** https://orval.dev/
- **OpenAPI spec:** https://swagger.io/specification/

---

## ✅ CHECKLIST DE PROGRESSO

### Setup (5 min)
- [ ] Backend rodando
- [ ] OpenAPI spec baixado (2.28 MB)
- [ ] Spec extraído (420 KB, 209 endpoints)
- [ ] Arquivos copiados para frontend
- [ ] Orval instalado
- [ ] Script adicionado ao package.json
- [ ] Tipos gerados (158 tipos)
- [ ] Build sem erros

### Service Layer (12h)
- [ ] Arquivo `government.ts` criado
- [ ] 24 sub-services implementados
- [ ] 209 métodos implementados
- [ ] Tipos do Orval usados
- [ ] Documentação inline

### Hooks (8h)
- [ ] Arquivo `useGovernment.ts` criado
- [ ] 24 hooks implementados
- [ ] Polling configurado
- [ ] Cache otimizado

### UI (8h)
- [ ] Dashboard implementado
- [ ] Componentes de integração
- [ ] Status e logs

### Página (3h)
- [ ] page.tsx refatorado
- [ ] Tabs funcionando
- [ ] Todas integrações visíveis

### Testes (4h)
- [ ] Testes de service
- [ ] Testes de hooks
- [ ] Cobertura >80%

### Documentação (2h)
- [ ] README do service
- [ ] Guia de configuração
- [ ] Exemplos

---

**🚀 BOA IMPLEMENTAÇÃO!**

---

**Criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Versão:** 1.0
