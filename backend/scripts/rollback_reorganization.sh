#!/bin/bash
# =============================================================================
# Rollback Script - Reorganizacao Backend (35 → 9 modulos)
# Conecta PRO - 2026-03-11
#
# Este script reverte a reorganizacao do backend para o estado anterior
# usando a tag git pre-reorganizacao-backend-2026-03-11.
#
# Uso: bash scripts/rollback_reorganization.sh [--dry-run] [--force]
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROLLBACK_TAG="pre-reorganizacao-backend-2026-03-11"
BACKUP_BRANCH="backup-pre-rollback-$(date +%Y%m%d_%H%M%S)"
DRY_RUN=false
FORCE=false

for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --force) FORCE=true ;;
        --help|-h)
            echo "Uso: $0 [--dry-run] [--force]"
            echo ""
            echo "  --dry-run  Mostra o que seria feito sem executar"
            echo "  --force    Pula confirmacoes interativas"
            echo ""
            exit 0
            ;;
    esac
done

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verifica se estamos no diretorio correto
if [ ! -f "main.py" ] && [ ! -f "main_production.py" ]; then
    log_error "Execute este script do diretorio backend/"
    exit 1
fi

# Verifica se a tag existe
if ! git tag -l "$ROLLBACK_TAG" | grep -q "$ROLLBACK_TAG"; then
    log_error "Tag '$ROLLBACK_TAG' nao encontrada. Rollback impossivel."
    exit 1
fi

log_info "=== ROLLBACK DA REORGANIZACAO BACKEND ==="
log_info "Tag de rollback: $ROLLBACK_TAG"
log_info "Branch de backup: $BACKUP_BRANCH"

if $DRY_RUN; then
    log_warn "MODO DRY-RUN: Nenhuma alteracao sera feita"
fi

# 1. Verifica mudancas nao commitadas
if [ -n "$(git status --porcelain)" ]; then
    log_warn "Existem mudancas nao commitadas:"
    git status --short
    if ! $FORCE; then
        echo ""
        read -p "Deseja continuar mesmo assim? (s/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            log_info "Rollback cancelado."
            exit 0
        fi
    fi
fi

# 2. Cria branch de backup do estado atual
log_info "Criando branch de backup: $BACKUP_BRANCH"
if ! $DRY_RUN; then
    git branch "$BACKUP_BRANCH"
fi

# 3. Mostra diff entre estado atual e tag
log_info "Arquivos que serao revertidos:"
git diff --stat "$ROLLBACK_TAG"..HEAD -- modules/ api/ main_production.py tests/ | tail -5
echo ""

CHANGED_FILES=$(git diff --name-only "$ROLLBACK_TAG"..HEAD -- modules/ api/ main_production.py tests/ | wc -l)
log_info "Total de arquivos afetados: $CHANGED_FILES"

if ! $FORCE && ! $DRY_RUN; then
    echo ""
    read -p "Confirma o rollback? Esta acao e IRREVERSIVEL (use branch '$BACKUP_BRANCH' para desfazer). (s/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        log_info "Rollback cancelado."
        if ! $DRY_RUN; then
            git branch -d "$BACKUP_BRANCH" 2>/dev/null || true
        fi
        exit 0
    fi
fi

if $DRY_RUN; then
    log_info "[DRY-RUN] git checkout $ROLLBACK_TAG -- modules/ api/ main_production.py tests/"
    log_info "[DRY-RUN] Rollback concluido (simulacao)"
    exit 0
fi

# 4. Executa o rollback
log_info "Executando rollback..."
git checkout "$ROLLBACK_TAG" -- modules/ api/ main_production.py tests/

# 5. Commit do rollback
git add modules/ api/ main_production.py tests/
git commit -m "rollback: Reverte reorganizacao backend para tag $ROLLBACK_TAG

Branch de backup com estado anterior: $BACKUP_BRANCH
Para desfazer este rollback: git checkout $BACKUP_BRANCH -- modules/ api/ main_production.py tests/"

log_info "=== ROLLBACK CONCLUIDO ==="
log_info "Branch de backup: $BACKUP_BRANCH"
log_info ""
log_warn "ACOES NECESSARIAS APOS ROLLBACK:"
log_warn "1. Reiniciar o backend: docker restart conecta-backend"
log_warn "2. Verificar saude: curl http://localhost:8000/health"
log_warn "3. Rodar testes: cd backend && python -m pytest tests/ -x"
log_warn "4. Se tudo OK, deletar backup: git branch -d $BACKUP_BRANCH"
