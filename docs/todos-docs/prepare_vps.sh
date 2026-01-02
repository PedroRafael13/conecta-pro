#!/bin/bash
# Script de preparação do VPS para ERP Conecta Mais

set -e

echo "🚀 Preparando VPS para ERP Conecta Mais"
echo "========================================"

# Verificar se Conecta Plus existe e está rodando
echo "1. Verificando Conecta Plus..."
if [ -d "/var/www/conecta-plus" ] || [ -d "/opt/conecta-plus" ]; then
    echo "✅ Conecta Plus encontrado - NÃO mexeremos nele!"
else
    echo "⚠️  Conecta Plus não encontrado no caminho padrão"
    echo "   Se estiver em outro local, está seguro!"
fi

# Criar estrutura do ERP
echo ""
echo "2. Criando estrutura do ERP..."
mkdir -p /opt/erp-conecta-mais/{backend,frontend,docs,logs,sessions,backups}
mkdir -p /opt/erp-conecta-mais/backend/{api,core,modules,tests,scripts}
mkdir -p /opt/erp-conecta-mais/backend/core/{auth,database,cache,logging}
mkdir -p /opt/erp-conecta-mais/backend/modules/{commercial,hr,financial,operations}

# Criar gerenciador de sessões
echo "3. Criando gerenciador de sessões..."
cat > /opt/erp-conecta-mais/sessions/SESSION_MANAGER.md << 'SESSIONEOF'
# HISTÓRICO DE SESSÕES - ERP CONECTA MAIS

## Instruções
Cada sessão do Claude Code deve ser registrada aqui.
Formato: veja PROMPT_CLAUDE_CODE_DEFINITIVO.md

---

## SESSÃO 000 - $(date +%Y-%m-%d)
Status: PREPARAÇÃO

### Executado:
- ✅ Estrutura de diretórios criada
- ✅ Gerenciador de sessões iniciado
- ✅ Pronto para primeira sessão real

### Próximos Passos:
1. Upload da documentação completa
2. Iniciar Claude Code
3. Executar Sprint 0 - Setup

---
SESSIONEOF

# Criar rastreador de progresso
echo "4. Criando rastreador de progresso..."
cat > /opt/erp-conecta-mais/docs/PROGRESSO_GERAL.md << 'PROGRESSEOF'
# 📊 PROGRESSO GERAL DO PROJETO ERP CONECTA MAIS

Última atualização: $(date +%Y-%m-%d)

---

## Sprint Atual: Sprint 0 - Preparação

### Progresso Geral: 0%

---

## Fases do Projeto

### Fase 1: Infraestrutura (0%)
- [ ] Estrutura de diretórios
- [ ] Python venv
- [ ] PostgreSQL
- [ ] Redis
- [ ] Git

### Fase 2: Core (0%)
- [ ] Autenticação
- [ ] User model + RBAC
- [ ] Error handling
- [ ] Logging
- [ ] Cache

### Fase 3: Módulos (0/38)
- [ ] CRM
- [ ] Contratos
- [ ] RH
- [ ] Financeiro
- [ ] ... (34 módulos restantes)

---

## Métricas Atuais

**Sessões realizadas:** 0
**Linhas de código:** 0
**Arquivos criados:** 0
**Testes escritos:** 0
**Coverage:** 0%
**Commits:** 0

---

## Histórico de Atualizações

- $(date +%Y-%m-%d): Estrutura inicial criada

PROGRESSEOF

# Criar .gitignore
echo "5. Criando .gitignore..."
cat > /opt/erp-conecta-mais/.gitignore << 'GITIGNOREEOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db

# Project specific
sessions/SESSION_*.bak
backups/*.sql
GITIGNOREEOF

# Criar README inicial
echo "6. Criando README..."
cat > /opt/erp-conecta-mais/README.md << 'READMEEOF'
# ERP Conecta Mais V2.0

Sistema ERP completo para gestão de empresas de segurança.

## Status do Projeto

🚧 Em desenvolvimento - Sprint 0

## Documentação

Ver `/opt/erp-conecta-mais/docs/` para documentação completa.

## Desenvolvimento

Este projeto é desenvolvido com assistência do Claude Code.
Ver `sessions/SESSION_MANAGER.md` para histórico de desenvolvimento.

## Progresso

Ver `docs/PROGRESSO_GERAL.md` para progresso detalhado.

READMEEOF

# Verificar espaço em disco
echo ""
echo "7. Verificando recursos..."
df -h /opt/erp-conecta-mais
free -h

# Verificar versões de ferramentas
echo ""
echo "8. Verificando ferramentas disponíveis..."
python3 --version 2>/dev/null || echo "⚠️  Python3 não encontrado - será instalado depois"
git --version 2>/dev/null || echo "⚠️  Git não encontrado - será instalado depois"

# Permissões
echo ""
echo "9. Ajustando permissões..."
chown -R root:root /opt/erp-conecta-mais
chmod -R 755 /opt/erp-conecta-mais

echo ""
echo "✅ PREPARAÇÃO CONCLUÍDA!"
echo ""
echo "Estrutura criada em: /opt/erp-conecta-mais/"
echo ""
echo "Próximos passos:"
echo "1. Upload da documentação para /opt/erp-conecta-mais/docs/"
echo "2. Iniciar Claude Code"
echo "3. Colar o PROMPT VERSÃO 1"
echo ""
echo "Documentação dos prompts: PROMPT_CLAUDE_CODE_DEFINITIVO.md"
