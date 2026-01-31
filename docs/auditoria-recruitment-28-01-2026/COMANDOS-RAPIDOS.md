# ⚡ COMANDOS RÁPIDOS - RECRUITMENT

Comandos prontos para copiar e executar.

---

## 🟢 INICIAR BACKEND

```bash
cd /opt/conecta-pro
docker compose up -d backend
docker logs -f conecta-pro-backend # ver logs em tempo real
```

---

## 📥 EXTRAIR OPENAPI SPEC

```bash
cd /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json
python3 extract-recruitment-spec.py
```

---

## 🔧 CONFIGURAR ORVAL NO FRONTEND

```bash
cd /opt/conecta-pro/frontend

# Copiar arquivos
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/openapi-recruitment.json ./
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/orval.config.recruitment.ts ./

# Instalar Orval
npm install -D orval

# Adicionar script no package.json (MANUAL)
# "orval:recruitment": "orval --config orval.config.recruitment.ts"
```

---

## 🎨 GERAR TIPOS

```bash
cd /opt/conecta-pro/frontend
npm run orval:recruitment
ls -la src/types/generated/recruitment/
```

---

## ✅ VALIDAR TIPOS

```bash
cd /opt/conecta-pro/frontend
npm run types:check
```

---

## 🏗️ BUILD

```bash
cd /opt/conecta-pro/frontend
npm run build
```

---

## 🔄 ATUALIZAR TIPOS (APÓS MUDANÇA NO BACKEND)

```bash
# 1. Atualizar spec
cd /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json
python3 extract-recruitment-spec.py

# 2. Copiar novo spec
cd /opt/conecta-pro/frontend
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/openapi-recruitment.json ./

# 3. Gerar novos tipos
npm run orval:recruitment

# 4. Validar
npm run types:check

# 5. Build
npm run build
```

---

## 📁 CRIAR ESTRUTURA DE ARQUIVOS

```bash
cd /opt/conecta-pro/frontend

# Diretórios
mkdir -p src/lib/services
mkdir -p src/hooks/recruitment
mkdir -p src/components/recruitment/vacancies
mkdir -p src/components/recruitment/candidates
mkdir -p src/components/recruitment/applications
mkdir -p src/components/recruitment/interviews
mkdir -p src/app/modulos/recrutamento

# Arquivos principais
touch src/lib/services/recruitment.ts
touch src/hooks/recruitment/useJobPositions.ts
touch src/hooks/recruitment/useCandidates.ts
touch src/hooks/recruitment/useApplications.ts
touch src/hooks/recruitment/useInterviews.ts
touch src/app/modulos/recrutamento/page.tsx
```

---

## 🧪 TESTAR ENDPOINT MANUALMENTE

```bash
# Health check
curl http://localhost:8080/health

# Listar vagas
curl http://localhost:8080/api/v1/recruitment/job-positions/

# Criar vaga (exemplo)
curl -X POST http://localhost:8080/api/v1/recruitment/job-positions/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Desenvolvedor Backend",
    "description": "Vaga para desenvolvedor Python",
    "position_type": "clt",
    "position_level": "mid"
  }'
```

---

## 📊 ESTATÍSTICAS

```bash
# Contar endpoints por submódulo
grep -r "@router\.(get|post|put|delete)" /opt/conecta-pro/backend/modules/recruitment/controllers/ | wc -l

# Listar todos os endpoints
grep -r "@router\.(get|post|put|delete)" /opt/conecta-pro/backend/modules/recruitment/controllers/ | grep -E "^\s*@router" | sort
```

---

## 🔍 VERIFICAR LOGS

```bash
# Logs do backend
docker logs -f conecta-pro-backend

# Logs com filtro
docker logs conecta-pro-backend 2>&1 | grep -i "recruitment"

# Últimas 50 linhas
docker logs --tail 50 conecta-pro-backend
```

---

## 🧹 LIMPAR E RECOMEÇAR

```bash
# Remover tipos gerados
cd /opt/conecta-pro/frontend
rm -rf src/types/generated/recruitment/

# Remover spec local
rm -f openapi-recruitment.json
rm -f orval.config.recruitment.ts

# Recriar tudo
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/openapi-recruitment.json ./
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/orval.config.recruitment.ts ./
npm run orval:recruitment
```

---

## 📋 CHECKLIST RÁPIDO

```bash
# ✅ Verificar se backend está online
curl http://localhost:8080/health

# ✅ Verificar se spec foi gerado
ls -lh /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/openapi-recruitment.json

# ✅ Verificar se tipos foram gerados
ls -la /opt/conecta-pro/frontend/src/types/generated/recruitment/

# ✅ Verificar se não há erros TypeScript
cd /opt/conecta-pro/frontend && npm run types:check

# ✅ Verificar se build passa
cd /opt/conecta-pro/frontend && npm run build
```

---

## 🚀 SEQUÊNCIA COMPLETA (COPY-PASTE)

```bash
# 1. Iniciar backend
cd /opt/conecta-pro
docker compose up -d backend
sleep 20

# 2. Extrair spec
cd /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json
python3 extract-recruitment-spec.py

# 3. Configurar frontend
cd /opt/conecta-pro/frontend
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/openapi-recruitment.json ./
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/orval.config.recruitment.ts ./

# 4. Instalar Orval (se necessário)
npm install -D orval

# 5. Gerar tipos
npm run orval:recruitment

# 6. Validar
npm run types:check

echo "✅ Setup completo! Agora implemente o service layer."
```

---

**Criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
