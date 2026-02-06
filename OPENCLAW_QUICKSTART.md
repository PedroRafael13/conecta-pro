# 🚀 OPENCLAW QUICKSTART - COMEÇE EM 15 MINUTOS

> **Objetivo:** Colocar o OpenClaw rodando 24/7 no Conecta PRO em menos de 15 minutos

---

## 📋 PRÉ-REQUISITOS

Você precisa apenas de:
- ✅ Acesso ao VPS (já tem)
- ✅ Docker + Docker Compose rodando (já tem)
- ✅ **API Key do Claude (Anthropic)** ou GPT-4 (OpenAI)

---

## 💳 PASSO 0: OBTER API KEY (5 MIN)

### Opção A: Claude (Anthropic) - RECOMENDADO 🏆

Claude 3.5 Sonnet é o melhor modelo para coding.

1. Acessar: https://console.anthropic.com/
2. Criar conta (se não tiver)
3. Menu: **API Keys** → **Create Key**
4. Copiar a key: `sk-ant-api03-...`

**Preço:** ~$3 por 1M tokens input / $15 por 1M tokens output
**Estimativa:** $50-100/mês para OpenClaw 24/7

### Opção B: OpenAI (GPT-4)

1. Acessar: https://platform.openai.com/api-keys
2. **Create new secret key**
3. Copiar: `sk-...`

**Preço:** Mais caro que Claude (~2-3x)

---

## 🔧 PASSO 1: CONFIGURAR VARIÁVEIS DE AMBIENTE (2 MIN)

```bash
cd /opt/conecta-pro

# Abrir .env
nano .env

# Adicionar no final:
# =========================
# OpenClaw Configuration
# =========================
ANTHROPIC_API_KEY=sk-ant-api03-SUA_KEY_AQUI
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Notificações (opcional mas recomendado)
DISCORD_WEBHOOK=https://discord.com/api/webhooks/SEU_WEBHOOK

# OpenClaw Settings
OPENCLAW_ENABLED=true
OPENCLAW_INTERVAL=3600
OPENCLAW_MIN_COVERAGE=70
OPENCLAW_NOTIFY_ON=success,fail,milestone,critical

# Salvar: Ctrl+O, Enter, Ctrl+X
```

### 📢 Como criar Discord Webhook (OPCIONAL - 2min)

1. Discord → Server Settings → Integrations → Webhooks
2. **New Webhook** → Nome: "OpenClaw Conecta PRO"
3. **Copy Webhook URL**
4. Colar no .env como `DISCORD_WEBHOOK=...`

---

## 🏗️ PASSO 2: CRIAR AMBIENTE STAGING (3 MIN)

```bash
cd /opt/conecta-pro

# 1. Criar branch staging no Git
git checkout -b staging
git push -u origin staging

# 2. Criar networks Docker
docker network create conecta-staging-network 2>/dev/null || true
docker network create conecta-pro-network 2>/dev/null || true

# 3. Subir ambiente staging
docker compose -f docker-compose.staging.yml up -d

# 4. Aguardar staging ficar healthy (~2min)
echo "Aguardando staging inicializar..."
sleep 120

# 5. Verificar se está rodando
docker compose -f docker-compose.staging.yml ps
```

**Esperado:**
```
conecta-pro-postgres-staging   Up (healthy)
conecta-pro-redis-staging      Up (healthy)
conecta-pro-backend-staging    Up (healthy)
conecta-pro-frontend-staging   Up (healthy)
```

---

## 🤖 PASSO 3: INICIAR OPENCLAW (2 MIN)

```bash
cd /opt/conecta-pro

# Gerar backlog inicial
python3 scripts/openclaw/generate-backlog.py

# Subir OpenClaw Agent
docker compose -f docker-compose.openclaw.yml up -d

# Verificar logs (primeiros 30s)
docker compose -f docker-compose.openclaw.yml logs -f openclaw-agent

# Ver status
docker ps | grep openclaw
```

**Esperado nos logs:**
```
🤖 OpenClaw Agent iniciado!
📁 Workspace: /workspace
⏱️ Intervalo: 60min
🎯 Cobertura mínima: 70%
📊 Max tarefas por ciclo: 8
🚀 OPENCLAW CYCLE INICIADO
📋 Gerando backlog de tarefas...
✅ Backlog gerado: XXX tarefas
```

---

## ✅ PASSO 4: VERIFICAR QUE ESTÁ FUNCIONANDO (3 MIN)

### 1. Ver Backlog Gerado

```bash
cat /opt/conecta-pro/scripts/openclaw/backlog.json | jq '.total_tasks, .by_priority'
```

Deve mostrar algo como:
```json
{
  "total_tasks": 6158,
  "by_priority": {
    "P0": 5,
    "P1": 234,
    "P2": 5419,
    "P3": 500
  }
}
```

### 2. Acompanhar OpenClaw Trabalhando

```bash
# Logs em tempo real
docker logs -f openclaw-agent

# Ver últimos 50 commits do OpenClaw
git log --author="OpenClaw" --oneline -50

# Dashboard web (se habilitou)
# Abrir: http://SEU_IP:8082
```

### 3. Ver Notificações Discord

Se configurou webhook, deve receber:
```
🤖 OpenClaw Agent
OpenClaw Agent iniciado!
• Intervalo: 60min
• Meta cobertura: 70%
• Max tarefas/ciclo: 8
```

---

## 📊 PASSO 5: MONITORAR PROGRESSO (DIÁRIO)

### Ver Estatísticas

```bash
# Backlog atual
python3 scripts/openclaw/generate-backlog.py

# Commits do OpenClaw (últimas 24h)
git log --author="OpenClaw" --since="24 hours ago" --oneline | wc -l

# Cobertura de testes atual
cd backend && pytest --cov=backend --cov-report=term | grep TOTAL
cd ../frontend && npm run test:coverage 2>&1 | grep "All files"

# Status dos containers
docker ps --filter "name=openclaw"
docker ps --filter "name=staging"
```

### Dashboard Web (Opcional)

Se subiu o `openclaw-dashboard`:
```
http://SEU_VPS_IP:8082
```

Mostra:
- 📈 Progresso vs metas
- 🐛 TODOs resolvidos
- 📊 Cobertura de testes
- 🏆 Conquistas

---

## 🎯 O QUE ESPERAR

### Primeira Hora
- ✅ 8-10 tarefas concluídas
- ✅ 20-50 TODOs resolvidos
- ✅ Alguns lint errors corrigidos
- ✅ 3-5 commits no Git

### Primeiro Dia (24h)
- ✅ 150-200 tarefas concluídas
- ✅ 300-500 TODOs resolvidos
- ✅ +1-2% cobertura de testes
- ✅ 60-80 commits

### Primeira Semana
- ✅ 1000-1500 tarefas concluídas
- ✅ 2000-3000 TODOs resolvidos
- ✅ +5-8% cobertura de testes
- ✅ 300-500 commits
- ✅ 2-3 módulos 100% completos

### Primeiro Mês
- ✅ 50-70% dos TODOs resolvidos
- ✅ Cobertura 80%+ alcançada
- ✅ 10+ módulos completos
- ✅ 2000+ commits
- ✅ Sistema significativamente mais robusto

---

## 🛠️ COMANDOS ÚTEIS

### Controlar OpenClaw

```bash
# Parar
docker compose -f docker-compose.openclaw.yml down

# Reiniciar
docker compose -f docker-compose.openclaw.yml restart openclaw-agent

# Ver logs
docker logs -f openclaw-agent

# Ver uso de recursos
docker stats openclaw-agent
```

### Controlar Staging

```bash
# Status
docker compose -f docker-compose.staging.yml ps

# Logs backend
docker logs -f conecta-pro-backend-staging

# Rebuild (após mudanças no código)
docker compose -f docker-compose.staging.yml build backend-staging
docker compose -f docker-compose.staging.yml up -d backend-staging

# Parar tudo
docker compose -f docker-compose.staging.yml down
```

### Git / Progresso

```bash
# Ver todos os commits do OpenClaw
git log --author="OpenClaw" --oneline

# Ver mudanças do OpenClaw hoje
git log --author="OpenClaw" --since="today" --stat

# Ver diff de um commit específico
git show COMMIT_HASH

# Criar PR manualmente de staging→main
git checkout staging
git pull
gh pr create --title "OpenClaw Weekly Sync" --body "Trabalho do OpenClaw da última semana"
```

---

## 🚨 TROUBLESHOOTING

### OpenClaw não está commitando

```bash
# Verificar config Git
docker exec openclaw-agent git config --list

# Configurar se necessário
docker exec openclaw-agent git config user.name "OpenClaw Agent"
docker exec openclaw-agent git config user.email "openclaw@conectapro.local"
```

### OpenClaw parando/crashando

```bash
# Ver logs de erro
docker logs openclaw-agent 2>&1 | grep -i error

# Ver uso de memória (pode estar sem RAM)
docker stats openclaw-agent --no-stream

# Aumentar memória no docker-compose.openclaw.yml:
#   deploy:
#     resources:
#       limits:
#         memory: 8192M  # 8GB ao invés de 4GB
```

### API Key inválida

```bash
# Testar API Key manualmente
docker exec openclaw-agent python3 -c "
import anthropic
client = anthropic.Anthropic(api_key='$ANTHROPIC_API_KEY')
response = client.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'ping'}]
)
print('✅ API Key válida!')
print(response.content[0].text)
"
```

### Staging não subindo

```bash
# Ver logs
docker compose -f docker-compose.staging.yml logs

# Verificar portas (8081 e 3002 devem estar livres)
netstat -tlnp | grep -E '8081|3002'

# Matar processos se necessário
kill $(lsof -t -i:8081)
kill $(lsof -t -i:3002)

# Rebuild forçado
docker compose -f docker-compose.staging.yml build --no-cache
docker compose -f docker-compose.staging.yml up -d
```

### Notificações não chegando

```bash
# Testar webhook
curl -X POST "$DISCORD_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "🧪 Teste de notificação do OpenClaw"
  }'

# Deve aparecer no Discord imediatamente
```

---

## ⚙️ AJUSTES FINOS

### Aumentar/Diminuir Intervalo

```env
# .env
OPENCLAW_INTERVAL=1800  # 30min (mais agressivo)
OPENCLAW_INTERVAL=7200  # 2h (mais conservador)
```

```bash
# Aplicar mudança
docker compose -f docker-compose.openclaw.yml restart openclaw-agent
```

### Mudar Prioridades

```env
# .env
OPENCLAW_MIN_COVERAGE=85  # Meta mais alta
MAX_TASKS_PER_CYCLE=16    # Mais tarefas por ciclo
MAX_TIME_PER_TASK=3600    # 1h por tarefa (ao invés de 30min)
```

### Mudar Modelo AI

```env
# Claude 3.5 Sonnet (Padrão - Recomendado)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Claude 3 Opus (Mais inteligente, mais caro)
ANTHROPIC_MODEL=claude-3-opus-20240229

# GPT-4 Turbo (OpenAI - se preferir)
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-...
# Comentar ANTHROPIC_API_KEY
```

---

## 📈 ACOMPANHAMENTO SEMANAL

### Toda Segunda-feira

```bash
# 1. Ver progresso da semana
python3 scripts/openclaw/generate-backlog.py

# 2. Ver relatório semanal
cat reports/openclaw/weekly-report-$(date +%Y-%W).json | jq

# 3. Criar PR staging→main (se satisfeito)
git checkout staging
git pull
gh pr create \
  --title "🤖 OpenClaw Week $(date +%W) Sync" \
  --body "$(git log --author='OpenClaw' --since='7 days ago' --oneline)"

# 4. Revisar e mergear
# Testar em staging primeiro!
```

---

## 🎓 PRÓXIMOS PASSOS

Depois que OpenClaw estiver rodando bem:

### 1. Ajustar Missão (Opcional)
```bash
nano /opt/conecta-pro/OPENCLAW_MISSION.md
# Editar KPIs, prioridades, regras
# OpenClaw vai ler este arquivo em cada ciclo
```

### 2. Criar Regras Customizadas

```bash
# Exemplo: Focar em módulo específico
echo "PRIORITY_MODULE=operacional" >> .env

# Exemplo: Só trabalhar em horários específicos
echo "OPENCLAW_WORK_HOURS=22-06" >> .env  # 22h às 6h
```

### 3. Configurar CI/CD (GitHub Actions)

Criar `.github/workflows/openclaw-sync.yml`:
```yaml
name: OpenClaw Daily Sync

on:
  schedule:
    - cron: '0 */6 * * *'  # A cada 6h
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: staging

      - name: Generate Report
        run: python3 scripts/openclaw/generate-backlog.py

      - name: Notify
        run: |
          curl -X POST ${{ secrets.DISCORD_WEBHOOK }} \
            -d "OpenClaw sync completed"
```

---

## 💰 CUSTOS ESTIMADOS

### Com Claude 3.5 Sonnet (Recomendado)

| Uso | Tokens/dia | Custo/dia | Custo/mês |
|-----|------------|-----------|-----------|
| **Leve** (8 tarefas/ciclo, 12 ciclos/dia) | ~500K | $2-3 | $60-90 |
| **Médio** (12 tarefas/ciclo, 16 ciclos/dia) | ~1M | $4-5 | $120-150 |
| **Pesado** (16 tarefas/ciclo, 24 ciclos/dia) | ~2M | $8-10 | $240-300 |

### Com GPT-4 Turbo

~2-3x mais caro que Claude.

### Reduzir Custos

1. **Aumentar intervalo:** `OPENCLAW_INTERVAL=7200` (2h)
2. **Menos tarefas/ciclo:** `MAX_TASKS_PER_CYCLE=5`
3. **Trabalhar só à noite:** `OPENCLAW_WORK_HOURS=22-08`
4. **Modelo mais barato:** `gpt-4o-mini` ou `claude-3-haiku`

---

## 🏆 MÉTRICAS DE SUCESSO

### Primeira Semana - SUCESSO se:
- ✅ OpenClaw rodando 24/7 sem crashes
- ✅ 300+ commits criados
- ✅ 2000+ TODOs resolvidos
- ✅ +3-5% cobertura de testes
- ✅ 0 vulnerabilidades High/Critical

### Primeiro Mês - SUCESSO se:
- ✅ 2000+ commits criados
- ✅ 50%+ TODOs resolvidos
- ✅ Cobertura 80%+ alcançada
- ✅ 10+ módulos 100% completos
- ✅ Sistema notavelmente mais robusto

### 3 Meses - SUCESSO se:
- ✅ 5000+ commits criados
- ✅ 90%+ TODOs resolvidos
- ✅ Cobertura 85%+ mantida
- ✅ 25+ módulos completos
- ✅ 0 bugs críticos
- ✅ Performance score 90+

---

## 🆘 SUPORTE

### Problemas Técnicos

1. Ler logs: `docker logs openclaw-agent 2>&1 | tail -100`
2. Ver `TROUBLESHOOTING` acima
3. Verificar issues do projeto
4. Abrir issue no GitHub com logs

### Dúvidas sobre o OpenClaw

- Ler: `/opt/conecta-pro/OPENCLAW_MISSION.md`
- Ver exemplos de commits: `git log --author="OpenClaw"`
- Analisar backlog: `cat scripts/openclaw/backlog.json | jq`

---

## ✅ CHECKLIST FINAL

Antes de considerar "DONE":

- [ ] API Key configurada (Anthropic ou OpenAI)
- [ ] .env atualizado com todas as vars
- [ ] Discord/Slack webhook configurado (opcional)
- [ ] Network Docker criadas
- [ ] Staging rodando e healthy
- [ ] OpenClaw rodando e healthy
- [ ] Primeiro backlog gerado com sucesso
- [ ] Primeiro ciclo completado
- [ ] Notificações recebidas (se configurou)
- [ ] Logs mostrando trabalho normal
- [ ] Git mostrando commits do OpenClaw

---

## 🎉 PRONTO!

**Parabéns!** 🎊 Você agora tem um **engenheiro de software sênior trabalhando 24/7** no Conecta PRO!

O OpenClaw vai:
- 💤 Trabalhar enquanto você dorme
- 📈 Melhorar o código continuamente
- 🐛 Corrigir bugs automaticamente
- 🧪 Aumentar cobertura de testes
- 📊 Reportar progresso diariamente

**Relaxe e deixe o OpenClaw fazer o trabalho pesado!** 🤖✨

---

**Criado em:** 03/02/2026
**Versão:** 1.0.0
**Tempo estimado:** 15 minutos
