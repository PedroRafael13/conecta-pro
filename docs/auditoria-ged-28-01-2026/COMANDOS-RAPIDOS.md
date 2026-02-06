# 🚀 COMANDOS RÁPIDOS - MÓDULO GED

## 📦 Setup Inicial (5min)

```bash
cd /opt/conecta-pro/frontend

# Copiar arquivos
cp /opt/conecta-pro/docs/auditoria-ged-28-01-2026/openapi-ged.json ./
cp /opt/conecta-pro/docs/auditoria-ged-28-01-2026/orval.config.ged.ts ./

# Instalar Orval
npm install -D orval

# Instalar React Query (se não tiver)
npm install @tanstack/react-query @tanstack/react-query-devtools

# Adicionar script no package.json:
# "orval:ged": "orval --config orval.config.ged.ts",
# "orval:ged:watch": "orval --config orval.config.ged.ts --watch"

# Gerar tipos
npm run orval:ged

# Verificar
npm run types:check
```

---

## 🔄 Desenvolvimento Diário

```bash
# Terminal 1: Watch mode (regera tipos automaticamente)
npm run orval:ged:watch

# Terminal 2: Dev server
npm run dev

# Terminal 3: Type checking em tempo real
npm run types:check -- --watch
```

---

## 🔧 Quando Backend Mudar

```bash
# 1. Baixar OpenAPI atualizado
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json

# 2. Extrair apenas GED
cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026
python3 extract-ged-spec.py

# 3. Copiar para frontend
cp /tmp/openapi-ged.json /opt/conecta-pro/frontend/

# 4. Regerar tipos
cd /opt/conecta-pro/frontend
npm run orval:ged

# 5. Verificar erros
npm run types:check

# 6. Build
npm run build
```

**Tempo total:** ~5 minutos

---

## 🧪 Testes

```bash
# Rodar todos os testes
npm run test

# Watch mode
npm run test:watch

# Cobertura
npm run test:coverage

# E2E
npm run test:e2e
```

---

## 🔍 Debugging

```bash
# Ver tipos gerados
ls -la src/types/generated/ged/

# Ver conteúdo de um arquivo de tipos
cat src/types/generated/ged/documents.ts

# Verificar erros detalhados
npm run types:check 2>&1 | less

# Build com log detalhado
npm run build --verbose
```

---

## 📦 Build e Deploy

```bash
# Build de produção
npm run build

# Preview do build
npm run preview

# Analisar bundle
npm run analyze
```

---

## 🚨 Solução de Problemas

### Erro: "Cannot find module '@/types/generated/ged'"

```bash
npm run orval:ged
```

### Erro: Tipos desatualizados

```bash
# Baixar OpenAPI atualizado e regerar
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json
cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026
python3 extract-ged-spec.py
cd /opt/conecta-pro/frontend
cp /tmp/openapi-ged.json ./
npm run orval:ged
```

### Build falhando

```bash
# Limpar cache e node_modules
rm -rf node_modules .next
npm install
npm run build
```

---

## 📚 Documentação

```bash
# Ver documentação completa
cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026
cat README.md

# Ver guia de execução
cat EXECUTE-AGORA-GED.md

# Ver auditoria
cat AUDITORIA-GED.md

# Ver plano
cat PLANO-COBERTURA-GED.md
```

---

## 🔗 Links Úteis

- **Orval:** https://orval.dev/
- **React Query:** https://tanstack.com/query/latest
- **OpenAPI:** https://swagger.io/specification/

---

Criado em: 28/01/2026
