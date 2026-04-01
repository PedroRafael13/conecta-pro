#!/bin/bash
# PATCH 01: Atualização de Dependências Críticas (CVEs)
# Data: 2026-02-05
# Severidade: CRÍTICO
#
# CVEs Corrigidos:
# - python-jose: CVE-2024-33663, CVE-2024-33664 (Algorithm confusion)
# - Next.js: CVE-2025-66478, CVE-2025-55184 (RCE)
# - React: CVE-2025-55182 (React2Shell)

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════════"
echo " PATCH 01: Atualização de Dependências Críticas"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# BACKUP DOS ARQUIVOS ORIGINAIS
# ============================================
echo -e "${YELLOW}[1/6] Criando backups...${NC}"

BACKEND_DIR="/opt/conecta-pro/backend"
FRONTEND_DIR="/opt/conecta-pro/frontend"
BACKUP_DIR="/opt/conecta-pro/docs/patches/backups_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

cp "$BACKEND_DIR/requirements.txt" "$BACKUP_DIR/requirements.txt.bak"
cp "$FRONTEND_DIR/package.json" "$BACKUP_DIR/package.json.bak"
cp "$FRONTEND_DIR/package-lock.json" "$BACKUP_DIR/package-lock.json.bak" 2>/dev/null || true

echo -e "${GREEN}✓ Backups criados em: $BACKUP_DIR${NC}"
echo ""

# ============================================
# ATUALIZAÇÃO BACKEND (Python)
# ============================================
echo -e "${YELLOW}[2/6] Atualizando dependências Python...${NC}"

cd "$BACKEND_DIR"

# Ativa virtual environment se existir
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment ativado${NC}"
fi

# Backup do requirements original
cp requirements.txt requirements.txt.pre-patch

# Atualiza python-jose para versão segura (>=3.4.0)
# Nota: A versão 3.4.0+ corrige as CVEs de algorithm confusion
sed -i 's/python-jose\[cryptography\]==3.3.0/python-jose[cryptography]>=3.4.0/g' requirements.txt

# Outras atualizações de segurança recomendadas
# FastAPI - verificar se há versão mais recente sem CVEs
# sed -i 's/fastapi==0.115.6/fastapi>=0.115.8/g' requirements.txt

echo -e "${GREEN}✓ requirements.txt atualizado${NC}"
echo ""

# Instalação das dependências atualizadas
echo -e "${YELLOW}[3/6] Instalando dependências Python...${NC}"
pip install --upgrade "python-jose[cryptography]>=3.4.0" || {
    echo -e "${RED}✗ Falha ao instalar python-jose${NC}"
    echo "Restaurando backup..."
    cp requirements.txt.pre-patch requirements.txt
    exit 1
}

echo -e "${GREEN}✓ Dependências Python instaladas${NC}"
echo ""

# Verificação da instalação
echo -e "${YELLOW}[4/6] Verificando instalação Python...${NC}"
PYTHON_JOSE_VERSION=$(pip show python-jose | grep Version | cut -d' ' -f2)
echo -e "python-jose versão instalada: ${GREEN}$PYTHON_JOSE_VERSION${NC}"

# Valida se a versão é >= 3.4.0
if [ "$(printf '%s\n' "3.4.0" "$PYTHON_JOSE_VERSION" | sort -V | head -n1)" = "3.4.0" ]; then
    echo -e "${GREEN}✓ python-jose atualizado com sucesso (>= 3.4.0)${NC}"
else
    echo -e "${RED}✗ Versão do python-jose não atende requisito mínimo (3.4.0)${NC}"
    exit 1
fi
echo ""

# ============================================
# ATUALIZAÇÃO FRONTEND (Node.js)
# ============================================
echo -e "${YELLOW}[5/6] Atualizando dependências Node.js...${NC}"

cd "$FRONTEND_DIR"

# Backup do package.json original
cp package.json package.json.pre-patch

# Atualiza Next.js para 16.1.6 (correção de CVEs)
sed -i 's/"next": "\^16.1.3"/"next": "^16.1.6"/g' package.json

# Atualiza React para 19.2.4 (correção de CVEs)
sed -i 's/"react": "\^19.2.3"/"react": "^19.2.4"/g' package.json
sed -i 's/"react-dom": "\^19.2.3"/"react-dom": "^19.2.4"/g' package.json

echo -e "${GREEN}✓ package.json atualizado${NC}"
echo ""

echo -e "${YELLOW}[6/6] Instalando dependências Node.js...${NC}"
npm install next@16.1.6 react@19.2.4 react-dom@19.2.4 || {
    echo -e "${RED}✗ Falha ao instalar dependências Node.js${NC}"
    echo "Restaurando backup..."
    cp package.json.pre-patch package.json
    exit 1
}

echo -e "${GREEN}✓ Dependências Node.js instaladas${NC}"
echo ""

# ============================================
# VERIFICAÇÃO FINAL
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo " VERIFICAÇÃO FINAL"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Backend (Python):${NC}"
echo "  python-jose: $(pip show python-jose | grep Version)"
echo ""

echo -e "${YELLOW}Frontend (Node.js):${NC}"
echo "  next: $(npm list next --depth=0 2>/dev/null | grep next | cut -d'@' -f2 || echo 'N/A')"
echo "  react: $(npm list react --depth=0 2>/dev/null | grep react@ | head -1 | cut -d'@' -f2 || echo 'N/A')"
echo ""

echo -e "${YELLOW}Auditoria de segurança (npm audit):${NC}"
npm audit --audit-level=high 2>/dev/null || true
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ PATCH 01 APLICADO COM SUCESSO${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Backups disponíveis em: $BACKUP_DIR"
echo ""
echo "Próximos passos:"
echo "  1. Execute os testes: pytest (backend) e npm test (frontend)"
echo "  2. Verifique se a aplicação inicia corretamente"
echo "  3. Teste login JWT para validar python-jose"
echo "  4. Consulte PATCH_01_VERIFICATION.md para checklist completo"
echo ""
