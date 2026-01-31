# ⚡ COMANDOS RÁPIDOS - Módulo GED + Orval

**Objetivo:** Lista de comandos copy-paste para implementação e manutenção do Orval no módulo GED

---

## 🚀 IMPLEMENTAÇÃO INICIAL (30 minutos)

### 1. Setup Orval

```bash
# Navegar para frontend
cd /opt/conecta-pro/frontend

# Copiar arquivos necessários
cp /opt/conecta-pro/docs/auditoria-ged-28-01-2026/openapi-ged.json ./
cp /opt/conecta-pro/docs/auditoria-ged-28-01-2026/orval.config.ged.ts ./

# Verificar Orval (já instalado)
npm list orval

# Se não estiver instalado:
# npm install -D orval
```

### 2. Adicionar Scripts no package.json

```bash
# Editar package.json manualmente e adicionar na seção "scripts":
```

```json
{
  "scripts": {
    "orval:ged": "orval --config orval.config.ged.ts",
    "orval:ged:watch": "orval --config orval.config.ged.ts --watch"
  }
}
```

### 3. Gerar Tipos pela Primeira Vez

```bash
cd /opt/conecta-pro/frontend
npm run orval:ged
```

### 4. Verificar Arquivos Gerados

```bash
ls -la src/types/generated/ged/
cat src/types/generated/ged/documents.ts | head -50
```

### 5. Validar Build

```bash
npm run type-check
npm run build
```

---

## 🔄 MANUTENÇÃO CONTÍNUA

### Quando Backend Mudar

```bash
# 1. Baixar OpenAPI completo do backend
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json

# 2. Extrair apenas módulo GED
cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026
python3 extract-ged-spec.py

# 3. Copiar spec atualizado para frontend
cp /tmp/openapi-ged.json /opt/conecta-pro/frontend/

# 4. Regerar tipos
cd /opt/conecta-pro/frontend
npm run orval:ged

# 5. Verificar erros TypeScript
npm run type-check

# 6. Build final
npm run build
```

**Tempo:** ~3-5 minutos

---

## 🛠️ DESENVOLVIMENTO

### Watch Mode (Regerar Automaticamente)

```bash
# Terminal 1: Watch Orval
cd /opt/conecta-pro/frontend
npm run orval:ged:watch

# Terminal 2: Dev Server
cd /opt/conecta-pro/frontend
npm run dev

# Terminal 3: Type Check
cd /opt/conecta-pro/frontend
npm run type-check -- --watch
```

---

## 🔍 VERIFICAÇÕES

### Verificar Endpoints Backend

```bash
# Contar endpoints em cada controller
cd /opt/conecta-pro/backend/modules/ged/controllers

grep -r "@router\." . | grep -E "\.(get|post|put|delete|patch)" | wc -l
```

### Verificar OpenAPI Spec

```bash
# Ver endpoints GED no OpenAPI
cd /opt/conecta-pro/frontend
cat openapi-snapshot.json | grep -o '"/api/v1/ged/[^"]*"' | wc -l

# Ver tags GED
cat openapi-snapshot.json | grep -o '"GED - [^"]*"' | sort -u
```

### Verificar Tipos Gerados

```bash
cd /opt/conecta-pro/frontend

# Listar todos os tipos
ls -la src/types/generated/ged/

# Ver exemplo de arquivo
cat src/types/generated/ged/documents.ts | head -100

# Buscar um tipo específico
grep -r "interface Document" src/types/generated/ged/
```

---

## 📊 ESTATÍSTICAS

### Backend Stats

```bash
cd /opt/conecta-pro/backend/modules/ged

# Contar controllers
ls -1 controllers/*.py | wc -l

# Contar endpoints por controller
for file in controllers/*.py; do
  echo "$(basename $file): $(grep -c '@router\.' $file) endpoints"
done

# Contar models
ls -1 models/*.py | grep -v __init__ | wc -l

# Contar schemas
ls -1 schemas/*.py | grep -v __init__ | wc -l
```

### Frontend Stats

```bash
cd /opt/conecta-pro/frontend

# Tamanho do service
wc -l src/lib/services/ged.ts

# Contar tipos gerados (após Orval)
find src/types/generated/ged -name "*.ts" | wc -l

# Tamanho do OpenAPI spec
ls -lh openapi-ged.json
```

---

## 🧹 LIMPEZA

### Remover Tipos Gerados

```bash
cd /opt/conecta-pro/frontend
rm -rf src/types/generated/ged/
```

### Limpar Cache do Orval

```bash
cd /opt/conecta-pro/frontend
rm -rf .orval/
rm -rf node_modules/.cache/orval/
```

---

## 🐛 TROUBLESHOOTING

### Erro: "Cannot find module '@/types/generated/ged'"

```bash
# Regerar tipos
cd /opt/conecta-pro/frontend
npm run orval:ged

# Verificar se foram gerados
ls -la src/types/generated/ged/
```

### Erro: Build falhando com erros de tipo

```bash
# Ver erros detalhados
cd /opt/conecta-pro/frontend
npm run type-check

# Limpar e rebuild
rm -rf .next/
npm run build
```

### Erro: Orval não encontrado

```bash
cd /opt/conecta-pro/frontend
npm install -D orval@7.13.2
```

### Erro: OpenAPI spec desatualizado

```bash
# Baixar novo OpenAPI do backend
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json

# Extrair GED novamente
cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026
python3 extract-ged-spec.py

# Copiar e regerar
cp /tmp/openapi-ged.json /opt/conecta-pro/frontend/
cd /opt/conecta-pro/frontend
npm run orval:ged
```

---

## 📦 EXTRAIR SPEC MANUALMENTE

### Usando Script Python

```bash
cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026

# Baixar OpenAPI completo primeiro
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json

# Extrair apenas GED
python3 extract-ged-spec.py

# Resultado em: /tmp/openapi-ged.json
```

### Parametros do Script

```python
# Editar extract-ged-spec.py para customizar:
path_filter = "/api/v1/ged/"  # Filtro de path
input_file = "/tmp/openapi-conecta-pro.json"
output_file = "/tmp/openapi-ged.json"
```

---

## 🔬 TESTES

### Testar Endpoints Backend

```bash
# Subir backend
cd /opt/conecta-pro/backend
docker compose up -d backend

# Testar endpoint de health
curl http://localhost:8080/health

# Testar endpoint GED
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8080/api/v1/ged/stats
```

### Testar Frontend

```bash
cd /opt/conecta-pro/frontend

# Type check
npm run type-check

# Build
npm run build

# Dev server
npm run dev

# Abrir no navegador
# http://localhost:3000
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

### Antes de Commitar

```bash
cd /opt/conecta-pro/frontend

# 1. Type check
npm run type-check
# ✅ Sem erros

# 2. Build
npm run build
# ✅ Build sucesso

# 3. Verificar tipos gerados
ls -la src/types/generated/ged/
# ✅ 8 arquivos gerados

# 4. Verificar imports
grep -r "from '@/types/generated/ged" src/lib/services/
# ✅ Usando tipos gerados
```

---

## 🚀 DEPLOY

### Atualizar Produção

```bash
# 1. Backend: Garantir que OpenAPI está atualizado
cd /opt/conecta-pro/backend
docker compose restart backend

# 2. Frontend: Regerar tipos
cd /opt/conecta-pro/frontend
npm run orval:ged
npm run build

# 3. Deploy
docker compose up -d frontend

# 4. Verificar
curl http://localhost:3000
```

---

## 🔄 REPLICAR PARA OUTROS MÓDULOS

### Template para Qualquer Módulo

```bash
# Exemplo: Módulo Financeiro

# 1. Baixar OpenAPI completo
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json

# 2. Copiar e adaptar script de extração
cp /opt/conecta-pro/docs/auditoria-ged-28-01-2026/extract-ged-spec.py \
   /tmp/extract-financeiro-spec.py

# Editar: path_filter = "/api/v1/financeiro/"

# 3. Executar extração
python3 /tmp/extract-financeiro-spec.py

# 4. Copiar e adaptar config Orval
cd /opt/conecta-pro/frontend
cp orval.config.ged.ts orval.config.financeiro.ts

# Editar:
#   target: './openapi-financeiro.json'
#   output.target: './src/types/generated/financeiro'

# 5. Copiar spec extraído
cp /tmp/openapi-financeiro.json ./

# 6. Gerar tipos
npm run orval:financeiro

# 7. Refatorar service
# src/lib/services/financeiro.ts

# 8. Validar
npm run type-check && npm run build
```

---

## 📚 REFERÊNCIAS RÁPIDAS

### URLs Úteis
- **Backend API:** http://localhost:8080
- **OpenAPI UI:** http://localhost:8080/docs
- **Frontend Dev:** http://localhost:3000

### Arquivos Importantes
```
/opt/conecta-pro/frontend/
├── openapi-ged.json             (spec extraído)
├── orval.config.ged.ts          (config Orval)
└── src/
    ├── lib/services/ged.ts      (service)
    └── types/generated/ged/     (tipos gerados)

/opt/conecta-pro/backend/modules/ged/
├── controllers/                 (7 arquivos)
├── models/                      (6 models)
├── schemas/                     (6 schemas)
└── services/                    (6 services)
```

---

## 💡 DICAS PRO

### Alias Úteis

```bash
# Adicionar ao ~/.bashrc

alias ged-frontend="cd /opt/conecta-pro/frontend"
alias ged-backend="cd /opt/conecta-pro/backend/modules/ged"
alias ged-docs="cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026"

alias ged-regen="cd /opt/conecta-pro/frontend && npm run orval:ged"
alias ged-check="cd /opt/conecta-pro/frontend && npm run type-check"
alias ged-build="cd /opt/conecta-pro/frontend && npm run build"

alias ged-extract="cd /opt/conecta-pro/docs/auditoria-ged-28-01-2026 && python3 extract-ged-spec.py"
alias ged-openapi="curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json"

# Reload bash
source ~/.bashrc
```

### One-liner Completo

```bash
# Atualizar tudo de uma vez
ged-openapi && ged-extract && cp /tmp/openapi-ged.json /opt/conecta-pro/frontend/ && ged-regen && ged-check && ged-build
```

---

## ✅ VALIDAÇÃO FINAL

### Checklist Completo

```bash
# 1. Backend rodando
curl http://localhost:8080/health
# ✅ {"status": "healthy"}

# 2. OpenAPI atualizado
curl -s http://localhost:8080/openapi.json | grep -o '"/api/v1/ged/' | wc -l
# ✅ > 100 endpoints

# 3. Spec extraído
ls -lh /opt/conecta-pro/frontend/openapi-ged.json
# ✅ ~310 KB

# 4. Tipos gerados
ls /opt/conecta-pro/frontend/src/types/generated/ged/ | wc -l
# ✅ 8 arquivos

# 5. Type check
cd /opt/conecta-pro/frontend && npm run type-check
# ✅ Sem erros

# 6. Build sucesso
cd /opt/conecta-pro/frontend && npm run build
# ✅ Build completed

# 7. Frontend rodando
curl http://localhost:3000
# ✅ HTML retornado
```

---

**Documento criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Versão:** 1.0
**Uso:** Copy-paste dos comandos conforme necessário
