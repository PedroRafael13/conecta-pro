# 🤖 OpenClaw - Autonomous Software Engineer

> **Engenheiro de Software Sênior 24/7 para o Conecta PRO**

## 📁 Arquivos Criados

- `OPENCLAW_MISSION.md` - Missão, KPIs, regras
- `OPENCLAW_QUICKSTART.md` - Guia início rápido (15min)
- `docker-compose.staging.yml` - Ambiente staging
- `docker-compose.openclaw.yml` - Container OpenClaw
- `scripts/openclaw/main-loop.py` - Loop principal
- `scripts/openclaw/generate-backlog.py` - Gerador de backlog

## 🚀 INÍCIO RÁPIDO

```bash
# 1. Configure API Key
nano .env
# Adicione: ANTHROPIC_API_KEY=sk-ant-...

# 2. Suba staging
docker compose -f docker-compose.staging.yml up -d

# 3. Suba OpenClaw
docker compose -f docker-compose.openclaw.yml up -d

# 4. Acompanhe
docker logs -f openclaw-agent
```

Leia **OPENCLAW_QUICKSTART.md** para instruções completas.
