#!/bin/bash

# FASE 1: DELETAR SERVICES VAZIOS
# Data: 2026-01-31
# Tempo estimado: 1h

set -e

echo "=========================================="
echo "FASE 1: DELETAR SERVICES VAZIOS"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador
DELETED=0
ERRORS=0

# Função para deletar arquivo
delete_file() {
  local file=$1
  if [ -f "$file" ]; then
    # Verificar se arquivo está vazio ou tem apenas imports/exports vazios
    local lines=$(wc -l < "$file")
    local exports=$(grep -c "export" "$file" 2>/dev/null || echo "0")

    echo -e "${YELLOW}Analisando:${NC} $file"
    echo "  Linhas: $lines | Exports: $exports"

    # Backup
    cp "$file" "$file.backup"
    echo "  Backup criado: $file.backup"

    # Deletar
    rm "$file"
    echo -e "  ${GREEN}✓ Deletado${NC}"
    DELETED=$((DELETED + 1))
  else
    echo -e "${RED}✗ Arquivo não encontrado:${NC} $file"
    ERRORS=$((ERRORS + 1))
  fi
  echo ""
}

echo "1. Deletando services de CLIENTS (6 arquivos)..."
echo "--------------------------------------------------"
delete_file "src/services/clients/clientAIService.ts"
delete_file "src/services/clients/condominiumService.ts"
delete_file "src/services/clients/unitService.ts"
delete_file "src/services/clients/integrationService.ts"
delete_file "src/services/clients/contractService.ts"

echo ""
echo "2. Deletando services de GOVERNMENT (7 arquivos)..."
echo "--------------------------------------------------"
delete_file "src/services/government/fgts-simples.service.ts"
delete_file "src/services/government/govbr-ecac.service.ts"
delete_file "src/services/government/nfse.service.ts"
delete_file "src/services/government/receita-federal.service.ts"
delete_file "src/services/government/sefaz.service.ts"
delete_file "src/services/government/sped.service.ts"
delete_file "src/services/government/sync-certificates.service.ts"

echo ""
echo "3. Deletando services de BIDDING (4 arquivos)..."
echo "--------------------------------------------------"
delete_file "src/services/bidding/certificates.service.ts"
delete_file "src/services/bidding/contracts.service.ts"
delete_file "src/services/bidding/documents.service.ts"
delete_file "src/services/bidding/proposals.service.ts"

echo ""
echo "4. Deletando services de MOBILE (1 arquivo)..."
echo "--------------------------------------------------"
delete_file "src/services/mobile/pushNotificationService.ts"

echo ""
echo "=========================================="
echo "RESUMO"
echo "=========================================="
echo -e "${GREEN}Arquivos deletados: $DELETED${NC}"
echo -e "${RED}Erros: $ERRORS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✓ FASE 1 CONCLUÍDA COM SUCESSO${NC}"
  echo ""
  echo "Próximos passos:"
  echo "1. Verificar build:"
  echo "   npm run build"
  echo ""
  echo "2. Verificar lint:"
  echo "   npm run lint"
  echo ""
  echo "3. Se tudo OK, deletar backups:"
  echo "   find src/services -name '*.backup' -delete"
  echo ""
  echo "4. Commit:"
  echo "   git add ."
  echo "   git commit -m \"chore: remove services vazios (Fase 1)\""
else
  echo -e "${RED}✗ FASE 1 COM ERROS${NC}"
  echo "Revise os erros acima e execute novamente"
  echo ""
  echo "Para restaurar backups:"
  echo "  find src/services -name '*.backup' | while read f; do mv \"\$f\" \"\${f%.backup}\"; done"
fi

echo ""
echo "=========================================="
