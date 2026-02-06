# 🔍 AUDITORIA MÓDULO OPERACIONAL - 28/01/2026

## 📋 OBJETIVO

Alcançar **100% de cobertura** do backend no frontend do módulo OPERACIONAL.

**Status Atual:** 77% (100/130 endpoints implementados)
**Meta:** 100% (130/130 endpoints)

---

## 📦 ARTEFATOS NESTA PASTA

| Arquivo | Descrição | Uso |
|---------|-----------|-----|
| **EXECUTE-AGORA.md** | 🚀 **COMECE POR AQUI!** Guia passo-a-passo | Próxima sessão - Quick Start |
| **auditoria-operacional.md** | Gap analysis completo endpoint-por-endpoint | Referência detalhada |
| **plano-cobertura-100-operacional.md** | 3 estratégias + roadmap 4 semanas | Visão estratégica |
| **README-implementacao.md** | Exemplos de código + checklist | Durante implementação |
| **openapi-operacional.json** | Spec OpenAPI (130 endpoints, 164 schemas) | Input para Orval |
| **orval.config.operacional.ts** | Configuração Orval | Copiar para frontend |
| **extract-operacional-spec.py** | Script de extração | Reutilizar em outros módulos |

---

## 🎯 ESTRATÉGIA ESCOLHIDA: HÍBRIDA

**Conceito:**
- ✅ Orval gera **tipos TypeScript automaticamente**
- ✅ Services/hooks **implementados manualmente** (padrão do projeto)
- ✅ Melhor dos dois mundos!

**Benefícios:**
- Tipos sempre sincronizados (zero erro)
- Código no padrão familiar
- Manutenção facilitada
- Escalável para outros módulos

---

## 🚀 QUICK START (5 MINUTOS)

```bash
cd /opt/conecta-pro/frontend

# 1. Copiar arquivos
cp /opt/conecta-pro/docs/auditoria-operacional-28-01-2026/openapi-operacional.json ./
cp /opt/conecta-pro/docs/auditoria-operacional-28-01-2026/orval.config.operacional.ts ./

# 2. Instalar dependências
npm install -D orval
npm install recharts

# 3. Adicionar ao package.json scripts:
#    "orval:operacional": "orval --config orval.config.operacional.ts"

# 4. Gerar tipos
npm run orval:operacional

# 5. Verificar
ls -la src/types/generated/operacional/
```

---

## 📊 GAPS CRÍTICOS

### 🔴 PRIORIDADE 1: Módulo de Comunicação (40h)
**Impacto:** CRÍTICO - 18 endpoints ausentes

- ❌ Comunicados (9 endpoints)
- ❌ Notificações (9 endpoints)
- ❌ WebSocket (alertas + notificações em tempo real)

**Consequência:** Sem interface para comunicação interna operacional.

### 🟡 PRIORIDADE 2: WebSocket (16h)
**Impacto:** ALTO - Notificações em tempo real

- ❌ Conexão autenticada
- ❌ Heartbeat automático
- ❌ Reconexão automática

### 🟢 PRIORIDADE 3: Disciplinar (8h)
**Impacto:** BAIXO - Features avançadas

- ⚠️ Validar conformidade CLT
- ⚠️ Verificar proporcionalidade
- ⚠️ Visualização de assinaturas

---

## 📅 ROADMAP (64 HORAS TOTAIS)

| Sprint | Foco | Tempo | Prioridade |
|--------|------|-------|------------|
| **1** | Comunicação (comunicados + notificações) | 40h | 🔴 Crítica |
| **2** | WebSocket (tempo real) | 16h | 🟡 Alta |
| **3** | Disciplinar + Polimento | 8h | 🟢 Média |

**Cronograma sugerido:** 4 semanas (16h/semana)

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- `/opt/conecta-pro/CLAUDE.md` - Atualizado com esta auditoria
- `/opt/conecta-pro/backend/modules/operacional/` - Código backend
- `/opt/conecta-pro/frontend/src/app/modulos/operacional/` - Código frontend
- `http://localhost:8080/docs` - Swagger UI do backend

---

## 🔄 PRÓXIMA SESSÃO

**Checklist para retomar:**
1. ✅ Ler `EXECUTE-AGORA.md`
2. ✅ Executar Quick Start (5min)
3. ✅ Verificar tipos gerados
4. ✅ Começar Sprint 1 (Comunicação)
5. ✅ Consultar `auditoria-operacional.md` para detalhes

**Comandos úteis:**
```bash
# Regerar tipos (quando backend mudar)
npm run orval:operacional

# Verificar erros TypeScript
npm run types:check

# Watch mode
npm run orval:watch
```

---

## 🎓 EXPANSÃO FUTURA

Após OPERACIONAL 100%, expandir para:
1. **Financeiro**
2. **Comercial/CRM**
3. **Integrations**
4. Outros módulos

Usar o **mesmo processo** (extrair spec → gerar tipos → implementar).

---

**📝 Criado em:** 28/01/2026
**🎯 Meta:** Cobertura 100% do módulo OPERACIONAL
**⏱️ Estimativa:** 64 horas (~4 semanas)

**COMECE PELO `EXECUTE-AGORA.md`! 🚀**