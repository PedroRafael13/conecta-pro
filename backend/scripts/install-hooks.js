#!/usr/bin/env node
/**
 * Script para instalar git hooks
 *
 * Uso: node scripts/install-hooks.js
 *
 * Instala hooks que notificam sobre mudanças na API
 */

import { writeFileSync, chmodSync, existsSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const GIT_HOOKS_DIR = resolve(__dirname, '../../.git/hooks');
const POST_COMMIT_HOOK = resolve(GIT_HOOKS_DIR, 'post-commit');

const hookScript = `#!/bin/bash
#
# Git Hook: post-commit
# Notifica quando arquivos da API são modificados
#

# Cores
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color
BOLD='\\033[1m'

# Arquivos modificados no último commit
MODIFIED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Padrões de arquivos da API
API_PATTERNS=(
  "backend/routers/"
  "backend/models/"
  "backend/schemas/"
  "backend/api/"
)

# Verificar se algum arquivo da API foi modificado
API_MODIFIED=false
MODIFIED_API_FILES=""

for pattern in "\${API_PATTERNS[@]}"; do
  matches=$(echo "$MODIFIED_FILES" | grep "$pattern" || true)
  if [ -n "$matches" ]; then
    API_MODIFIED=true
    MODIFIED_API_FILES="$MODIFIED_API_FILES$matches\\n"
  fi
done

# Se arquivos da API foram modificados, mostrar notificação
if [ "$API_MODIFIED" = true ]; then
  echo ""
  echo -e "\${CYAN}╔══════════════════════════════════════════════════════════════╗\${NC}"
  echo -e "\${CYAN}║\${NC}  \${YELLOW}⚠  ATENÇÃO: Arquivos de API foram modificados!\${NC}              \${CYAN}║\${NC}"
  echo -e "\${CYAN}╠══════════════════════════════════════════════════════════════╣\${NC}"
  echo -e "\${CYAN}║\${NC}                                                              \${CYAN}║\${NC}"
  echo -e "\${CYAN}║\${NC}  \${BOLD}Arquivos alterados:\${NC}                                        \${CYAN}║\${NC}"

  # Listar arquivos modificados (formatados)
  echo -e "$MODIFIED_API_FILES" | while read -r file; do
    if [ -n "$file" ]; then
      printf "\${CYAN}║\${NC}    \${GREEN}→\${NC} %-54s \${CYAN}║\${NC}\\n" "$file"
    fi
  done

  echo -e "\${CYAN}║\${NC}                                                              \${CYAN}║\${NC}"
  echo -e "\${CYAN}║\${NC}  \${BOLD}Para sincronizar o frontend, execute:\${NC}                     \${CYAN}║\${NC}"
  echo -e "\${CYAN}║\${NC}                                                              \${CYAN}║\${NC}"
  echo -e "\${CYAN}║\${NC}    \${BLUE}cd /opt/conecta-pro/backend && npm run api:sync\${NC}         \${CYAN}║\${NC}"
  echo -e "\${CYAN}║\${NC}                                                              \${CYAN}║\${NC}"
  echo -e "\${CYAN}╚══════════════════════════════════════════════════════════════╝\${NC}"
  echo ""
fi
`;

function main() {
  console.log('\nInstalando git hooks...\n');

  // Verificar se existe diretório .git
  if (!existsSync(GIT_HOOKS_DIR)) {
    console.log('Criando diretório de hooks...');
    mkdirSync(GIT_HOOKS_DIR, { recursive: true });
  }

  // Escrever hook
  writeFileSync(POST_COMMIT_HOOK, hookScript);
  chmodSync(POST_COMMIT_HOOK, '755');

  console.log('✓ Hook post-commit instalado com sucesso!');
  console.log(`  Localização: ${POST_COMMIT_HOOK}\n`);
  console.log('Agora, ao commitar mudanças em arquivos da API, você');
  console.log('receberá uma notificação para sincronizar o frontend.\n');
}

main();
