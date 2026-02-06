#!/bin/bash
# ============================================================================
# OpenClaw - Script de Instalacao como Servico Systemd
# Conecta PRO - Monitor de Qualidade Continua
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="${SCRIPT_DIR}/openclaw.service"
PROJECT_ROOT="/opt/conecta-pro"
LOG_DIR="${PROJECT_ROOT}/logs/openclaw"
REPORT_DIR="${PROJECT_ROOT}/reports/openclaw"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERRO]${NC} $1"; }

echo "============================================================"
echo "  OpenClaw - Instalacao do Servico"
echo "  Conecta PRO Quality Monitor"
echo "============================================================"
echo ""

# Verificar se esta rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Este script precisa ser executado como root."
    echo "  Execute: sudo bash ${BASH_SOURCE[0]}"
    exit 1
fi

# Verificar se o arquivo de servico existe
if [ ! -f "${SERVICE_FILE}" ]; then
    error "Arquivo de servico nao encontrado: ${SERVICE_FILE}"
    exit 1
fi

# Verificar se o runner existe
if [ ! -f "${SCRIPT_DIR}/runner.py" ]; then
    error "Runner nao encontrado: ${SCRIPT_DIR}/runner.py"
    exit 1
fi

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    error "Python 3 nao encontrado. Instale com: apt install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
info "Python detectado: ${PYTHON_VERSION}"

# Criar diretorios necessarios
info "Criando diretorios..."
mkdir -p "${LOG_DIR}"
mkdir -p "${REPORT_DIR}"

# Dar permissao de execucao ao runner
chmod +x "${SCRIPT_DIR}/runner.py"

# Verificar se o servico ja esta instalado
if systemctl is-active --quiet openclaw 2>/dev/null; then
    warn "Servico OpenClaw ja esta ativo. Parando para atualizar..."
    systemctl stop openclaw
fi

# Copiar arquivo de servico
info "Copiando arquivo de servico para systemd..."
cp "${SERVICE_FILE}" /etc/systemd/system/openclaw.service

# Recarregar systemd
info "Recarregando configuracao do systemd..."
systemctl daemon-reload

# Habilitar servico para iniciar no boot
info "Habilitando servico para iniciar automaticamente..."
systemctl enable openclaw

# Iniciar servico
info "Iniciando servico OpenClaw..."
systemctl start openclaw

# Aguardar um momento e verificar status
sleep 2

echo ""
echo "============================================================"
if systemctl is-active --quiet openclaw; then
    info "OpenClaw instalado e ativo com sucesso!"
    echo ""
    systemctl status openclaw --no-pager
else
    error "OpenClaw falhou ao iniciar. Verificando logs..."
    echo ""
    journalctl -u openclaw --no-pager -n 20
fi

echo ""
echo "============================================================"
echo "  Comandos uteis:"
echo "    systemctl status openclaw    # Ver status"
echo "    systemctl stop openclaw      # Parar servico"
echo "    systemctl restart openclaw   # Reiniciar"
echo "    journalctl -u openclaw -f    # Logs em tempo real"
echo ""
echo "    python3 ${SCRIPT_DIR}/runner.py --report  # Ver ultimo relatorio"
echo "    python3 ${SCRIPT_DIR}/runner.py --only health  # Check rapido"
echo "============================================================"
