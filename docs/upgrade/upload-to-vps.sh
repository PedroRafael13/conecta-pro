#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# CONECTA MAIS - SCRIPT DE UPLOAD (Mac → VPS)
# Upload automático dos arquivos de qualidade para o servidor
# ═══════════════════════════════════════════════════════════════════════════

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configurações do servidor
VPS_IP="82.25.75.74"
VPS_USER="root"
VPS_PASS="JsJ618908@#82"
VPS_PATH="/opt/erp-conecta-mais/docs"

# Pasta local (Mac)
LOCAL_PATH="$HOME/jjesus/projetos/erp"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  CONECTA MAIS - Upload para VPS                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se pasta local existe
if [ ! -d "$LOCAL_PATH" ]; then
    echo -e "${RED}✗ Pasta local não encontrada: $LOCAL_PATH${NC}"
    echo -e "${YELLOW}  Criando pasta...${NC}"
    mkdir -p "$LOCAL_PATH"
    echo -e "${GREEN}✓ Pasta criada!${NC}"
fi

# Verificar se arquivos existem
cd "$LOCAL_PATH" || exit 1

FILES=(
    "conecta-mais-audit-system.sh"
    "conecta-mais-quality-skills.md"
    "conecta-mais-quality-prompts.md"
    ".pylintrc.conecta-mais"
    "GUIA-COMPLETO-CONECTA-MAIS.md"
    "GUIA-EXECUCAO-VPS.md"
    "RESUMO-EXECUTIVO.md"
)

echo -e "${BLUE}Verificando arquivos locais...${NC}"
MISSING=0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - ${YELLOW}FALTANDO!${NC}"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo -e "\n${RED}✗ Faltam $MISSING arquivos!${NC}"
    echo -e "${YELLOW}  Baixe todos os arquivos primeiro e coloque em:${NC}"
    echo -e "${YELLOW}  $LOCAL_PATH${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Todos os arquivos encontrados!${NC}"

# Upload via SCP
echo -e "\n${BLUE}Iniciando upload para VPS...${NC}"
echo -e "${YELLOW}IP: $VPS_IP${NC}"
echo -e "${YELLOW}Usuário: $VPS_USER${NC}"
echo -e "${YELLOW}Destino: $VPS_PATH${NC}"
echo ""

# Criar pasta no VPS se não existir
echo -e "${BLUE}1. Criando pasta no VPS (se necessário)...${NC}"
ssh "$VPS_USER@$VPS_IP" "mkdir -p $VPS_PATH" 2>/dev/null

# Upload dos arquivos
echo -e "\n${BLUE}2. Uploading arquivos...${NC}"
scp -r "${FILES[@]}" "$VPS_USER@$VPS_IP:$VPS_PATH/" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Upload concluído com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro no upload!${NC}"
    exit 1
fi

# Configurar permissões
echo -e "\n${BLUE}3. Configurando permissões...${NC}"
ssh "$VPS_USER@$VPS_IP" "chmod +x $VPS_PATH/conecta-mais-audit-system.sh" 2>/dev/null
echo -e "${GREEN}✓ Permissões configuradas!${NC}"

# Copiar .pylintrc para backend
echo -e "\n${BLUE}4. Copiando configuração Pylint...${NC}"
ssh "$VPS_USER@$VPS_IP" "cp $VPS_PATH/.pylintrc.conecta-mais /opt/erp-conecta-mais/backend/.pylintrc" 2>/dev/null
echo -e "${GREEN}✓ Pylint configurado!${NC}"

# Criar pasta de reports
echo -e "\n${BLUE}5. Criando pasta de relatórios...${NC}"
ssh "$VPS_USER@$VPS_IP" "mkdir -p $VPS_PATH/quality-reports" 2>/dev/null
echo -e "${GREEN}✓ Pasta criada!${NC}"

# Verificar arquivos no VPS
echo -e "\n${BLUE}6. Verificando arquivos no VPS...${NC}"
ssh "$VPS_USER@$VPS_IP" "ls -la $VPS_PATH" 2>/dev/null

echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ UPLOAD COMPLETO!                                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}Próximos passos:${NC}"
echo -e "1. Conectar no VPS:"
echo -e "   ${YELLOW}ssh $VPS_USER@$VPS_IP${NC}"
echo -e ""
echo -e "2. Navegar para a pasta:"
echo -e "   ${YELLOW}cd $VPS_PATH${NC}"
echo -e ""
echo -e "3. Executar teste:"
echo -e "   ${YELLOW}./conecta-mais-audit-system.sh /opt/erp-conecta-mais config full${NC}"
echo -e ""
echo -e "${GREEN}Boa sorte nos sprints! 🚀${NC}"
