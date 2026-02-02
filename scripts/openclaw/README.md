# OpenClaw V2.0 - Quality Monitor

Sistema de monitoramento contínuo de qualidade para Conecta PRO.

## 🚀 Recursos

### FASE 1 - Foundation (✅ Concluída)
- ⚡ **Execução Paralela**: Reduz tempo de ciclo em ~56% (432s → 191s)
- 📊 **Health Score**: Métrica visual 0-100 baseada em status dos checks
- 🔔 **Notificações Discord**: Webhooks com rich embeds e alertas inteligentes
- 🎯 **ParallelExecutor**: Engine assíncrono para checks concorrentes

### FASE 2 - Expansion (✅ Concluída)
- 🔍 **Novos Checks**:
  - `npm audit` - Vulnerabilidades em dependências frontend
  - `pip-audit` - Vulnerabilidades em dependências backend
  - `gitleaks` - Detecção de secrets expostos
  - `lighthouse` - Performance web (habilitado)
- 🤖 **GitHub Actions**: Workflow CI/CD completo
- 📦 **Artifacts**: Relatórios persistidos por 30-90 dias
- 💬 **PR Comments**: Relatórios automáticos em pull requests

## 📋 Checks Disponíveis

### Tests
- **Backend Tests**: pytest com cobertura
- **Frontend Tests**: vitest

### Lint
- **Backend Lint**: ruff check + format
- **Frontend Lint**: eslint + prettier

### Security
- **Bandit**: SAST para Python
- **Gitleaks**: Secret scanning

### Audit
- **NPM Audit**: Vulnerabilidades npm
- **Pip Audit**: Vulnerabilidades pip

### Coverage
- **Code Coverage**: Análise de cobertura de testes

### Health
- **Health Check**: Status dos serviços
- **Docker Status**: Containers ativos/unhealthy
- **Disk Space**: Espaço em disco

### Performance
- **Lighthouse**: Métricas de performance web

## 🛠️ Uso

### CLI Local

```bash
# Ciclo completo (sequencial)
python3 scripts/openclaw/runner.py

# Ciclo completo (paralelo)
python3 scripts/openclaw/runner.py --parallel

# Apenas um grupo de checks
python3 scripts/openclaw/runner.py --only tests
python3 scripts/openclaw/runner.py --only security --parallel

# Grupos disponíveis:
# - tests
# - lint
# - security
# - audit
# - coverage
# - health
# - performance
```

### GitHub Actions

O workflow roda automaticamente em:
- **Push**: branches main, develop, feature/*, release/*
- **Pull Request**: para main e develop
- **Schedule**: diariamente às 00:00 UTC
- **Manual**: via workflow_dispatch

```yaml
# Trigger manual com opções
on:
  workflow_dispatch:
    inputs:
      check_group: 'all'  # ou tests, lint, security, audit
      parallel: true      # executar em paralelo
```

### Via Chat Bartolo

```
@bartolo executar openclaw completo
@bartolo rodar checks de segurança
@bartolo analisar relatório openclaw
```

## ⚙️ Configuração

### Arquivo de Config

Criar `/opt/conecta-pro/config/openclaw.json`:

```json
{
  "cycle_interval_seconds": 3600,
  "checks": {
    "backend_tests": {"enabled": true, "timeout": 120},
    "frontend_tests": {"enabled": true, "timeout": 120},
    "backend_lint": {"enabled": true, "timeout": 60},
    "frontend_lint": {"enabled": true, "timeout": 60},
    "security_bandit": {"enabled": true, "timeout": 60},
    "gitleaks": {"enabled": true, "timeout": 60},
    "npm_audit": {"enabled": true, "timeout": 60},
    "pip_audit": {"enabled": true, "timeout": 60},
    "coverage": {"enabled": true, "timeout": 180, "min_coverage": 60},
    "health": {"enabled": true, "timeout": 30},
    "docker_status": {"enabled": true, "timeout": 15},
    "disk_space": {"enabled": true, "timeout": 5, "min_free_gb": 5},
    "lighthouse": {"enabled": true, "timeout": 120}
  },
  "notifications": {
    "discord_webhook": "https://discord.com/api/webhooks/...",
    "notify_on": ["fail", "error"]
  },
  "retention": {
    "reports_days": 30,
    "logs_days": 14
  }
}
```

### Variáveis de Ambiente (GitHub Actions)

```bash
# Secrets necessários
DISCORD_WEBHOOK_OPENCLAW  # Webhook Discord para notificações
```

## 📊 Relatórios

### Estrutura JSON

```json
{
  "cycle_id": "20260202_123045",
  "started_at": "2026-02-02T12:30:45Z",
  "ended_at": "2026-02-02T12:33:56Z",
  "duration_seconds": 191.2,
  "overall_status": "pass",
  "health_score": 85,
  "environment": "production",
  "checks": [
    {
      "name": "Backend Tests",
      "status": "pass",
      "duration_seconds": 23.4,
      "message": "45 testes passaram",
      "details": {
        "passed": 45,
        "failed": 0
      }
    }
  ],
  "summary": {
    "total_checks": 13,
    "status_counts": {
      "pass": 10,
      "warn": 2,
      "fail": 1,
      "error": 0,
      "skip": 0
    }
  }
}
```

### Localização

- **Relatórios**: `/opt/conecta-pro/reports/openclaw/cycle_*.json`
- **Logs**: `/opt/conecta-pro/logs/openclaw/runner_*.log`
- **GitHub Artifacts**: Disponíveis por 30-90 dias

## 🔔 Notificações

### Discord Webhook

Notificações são enviadas quando:
1. Status é `fail` ou `error`
2. Status mudou do último relatório
3. Checks críticos (security, health, tests) falharam

Formato do embed:
- 🎨 **Color-coded**: Verde (pass), Vermelho (fail), Laranja (warn)
- 📊 **Campos**: Duração, Resultados, Health Score, Falhas Críticas
- 🔗 **Link**: Para relatório completo

### Configurar Discord Webhook

1. No Discord: Server Settings → Integrations → Webhooks → New Webhook
2. Copiar Webhook URL
3. Adicionar em `config/openclaw.json`:
   ```json
   "notifications": {
     "discord_webhook": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
   }
   ```

## 🧪 Instalação de Ferramentas

### Dependências Python

```bash
pip install pip-audit bandit ruff pytest pytest-cov
```

### Dependências Node.js

```bash
npm install -g @lhci/cli
```

### Gitleaks (Secret Scanning)

```bash
# Linux
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.2/gitleaks_8.18.2_linux_x64.tar.gz
tar -xzf gitleaks_8.18.2_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/

# macOS
brew install gitleaks
```

## 🏗️ Arquitetura

```
scripts/openclaw/
├── runner.py                    # Orquestrador principal
├── checks/
│   └── parallel_executor.py    # Engine de execução paralela
├── README.md                    # Esta documentação
└── config.example.json          # Exemplo de configuração

backend/modules/ai/bartolo/services/
└── notification_service.py      # Serviço de notificações

.github/workflows/
└── openclaw.yml                 # CI/CD workflow

reports/openclaw/                # Relatórios JSON
logs/openclaw/                   # Logs de execução
```

## 📈 Health Score

Fórmula:
```
score = 100 - (fail × 15) - (error × 10) - (warn × 5) - (skip × 2)
score = max(0, min(100, score))
```

Interpretação:
- **90-100**: ✅ Excelente
- **70-89**: 🟢 Bom
- **50-69**: 🟡 Atenção
- **30-49**: 🟠 Crítico
- **0-29**: 🔴 Emergência

## 🔮 Roadmap

### FASE 3 - Intelligence (Pendente)
- 🤖 Análise de trends com IA
- 📊 Predição de falhas
- 🔄 Auto-healing para problemas comuns
- 📈 Dashboards interativos

### FASE 4 - Polish (Pendente)
- 🎨 UI web para visualização
- 📱 Notificações mobile
- 🔍 Busca e filtros avançados
- 📦 Exportação para formatos diversos

## 🤝 Contribuindo

1. Criar branch: `feature/melhoria-openclaw`
2. Implementar mudanças
3. Adicionar testes
4. Commit: `feat(openclaw): adicionar novo check XYZ`
5. Pull request para `develop`

## 📝 Changelog

### v2.0.0 (2026-02-02)
- ✨ FASE 2 completa: Novos checks + CI/CD
- ✨ Dependency audit (npm + pip)
- ✨ Secret scanning (gitleaks)
- ✨ GitHub Actions workflow
- ✨ Lighthouse habilitado por padrão

### v1.5.0 (2026-02-02)
- ✨ FASE 1 completa: Foundation
- ⚡ Execução paralela (56% mais rápido)
- 📊 Health Score calculation
- 🔔 Discord notifications com rich embeds
- 🎯 ParallelExecutor engine

### v1.0.0 (2026-01-30)
- 🎉 Release inicial
- ✅ Checks básicos (tests, lint, security)
- 📋 Relatórios JSON
- 🔄 Ciclos automáticos

## 📄 Licença

Copyright © 2026 Conecta PRO Team. Todos os direitos reservados.
