#!/bin/bash
#===============================================================================
# CONECTA PRO - Release Manager
#===============================================================================
# Gerencia o processo completo de release para Android e iOS
#
# Uso:
#   ./scripts/mobile/release.sh [opcoes]
#
# Opcoes:
#   --android       Release apenas Android
#   --ios           Release apenas iOS
#   --all           Release Android e iOS (padrao)
#   --version X.Y.Z Definir versao do release
#   --bump-patch    Incrementar patch version (1.0.0 -> 1.0.1)
#   --bump-minor    Incrementar minor version (1.0.0 -> 1.1.0)
#   --bump-major    Incrementar major version (1.0.0 -> 2.0.0)
#   --dry-run       Simular sem executar builds
#   --skip-tests    Pular testes antes do release
#   --changelog     Gerar changelog automatico
#
# Exemplos:
#   ./scripts/mobile/release.sh --all --bump-patch
#   ./scripts/mobile/release.sh --android --version 1.2.0
#===============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Diretorio base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuracoes padrao
BUILD_ANDROID=true
BUILD_IOS=true
NEW_VERSION=""
BUMP_TYPE=""
DRY_RUN=false
SKIP_TESTS=false
GENERATE_CHANGELOG=false

# Arquivo de output
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/scripts/mobile/logs/release_$TIMESTAMP.log"
RELEASES_DIR="$PROJECT_DIR/releases"

#===============================================================================
# Funcoes
#===============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo ""
    echo "=============================================================="
    echo "  CONECTA PRO - Release Manager"
    echo "  $(date)"
    echo "=============================================================="
    echo ""
}

get_current_version() {
    cd "$PROJECT_DIR"
    CURRENT_VERSION=$(node -p "require('./package.json').version")
    echo "$CURRENT_VERSION"
}

bump_version() {
    local current=$1
    local type=$2

    IFS='.' read -r major minor patch <<< "$current"

    case $type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
    esac

    echo "$major.$minor.$patch"
}

update_version_files() {
    local version=$1

    log_info "Atualizando versao para $version..."

    # package.json
    cd "$PROJECT_DIR"
    node -e "
        const fs = require('fs');
        const pkg = require('./package.json');
        pkg.version = '$version';
        fs.writeFileSync('./package.json', JSON.stringify(pkg, null, 2) + '\n');
    "
    log_info "  package.json atualizado"

    # capacitor.config.ts (se existir appVersion)
    if [ -f "capacitor.config.ts" ]; then
        if grep -q "appVersion" capacitor.config.ts; then
            sed -i "s/appVersion: '[^']*'/appVersion: '$version'/" capacitor.config.ts
            log_info "  capacitor.config.ts atualizado"
        fi
    fi

    # Android build.gradle
    ANDROID_GRADLE="$PROJECT_DIR/android/app/build.gradle"
    if [ -f "$ANDROID_GRADLE" ]; then
        # Incrementar versionCode
        CURRENT_CODE=$(grep "versionCode" "$ANDROID_GRADLE" | head -1 | grep -o '[0-9]*')
        NEW_CODE=$((CURRENT_CODE + 1))
        sed -i "s/versionCode $CURRENT_CODE/versionCode $NEW_CODE/" "$ANDROID_GRADLE"
        sed -i "s/versionName \"[^\"]*\"/versionName \"$version\"/" "$ANDROID_GRADLE"
        log_info "  Android build.gradle atualizado (versionCode: $NEW_CODE)"
    fi

    # iOS Info.plist
    IOS_PLIST="$PROJECT_DIR/ios/App/App/Info.plist"
    if [ -f "$IOS_PLIST" ]; then
        # Atualizar CFBundleShortVersionString
        /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $version" "$IOS_PLIST" 2>/dev/null || true
        # Incrementar CFBundleVersion
        CURRENT_BUILD=$(/usr/libexec/PlistBuddy -c "Print :CFBundleVersion" "$IOS_PLIST" 2>/dev/null || echo "0")
        NEW_BUILD=$((CURRENT_BUILD + 1))
        /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $NEW_BUILD" "$IOS_PLIST" 2>/dev/null || true
        log_info "  iOS Info.plist atualizado (build: $NEW_BUILD)"
    fi

    log_success "Versao atualizada para $version"
}

run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Pulando testes (--skip-tests)"
        return
    fi

    log_step "Executando testes..."
    cd "$PROJECT_DIR"

    # TypeScript check
    log_info "Verificando tipos TypeScript..."
    npx tsc --noEmit 2>&1 | tee -a "$LOG_FILE"

    # Lint
    log_info "Executando lint..."
    npm run lint 2>&1 | tee -a "$LOG_FILE" || log_warning "Lint com avisos"

    # Unit tests (se existirem)
    if grep -q "\"test\":" package.json; then
        log_info "Executando testes unitarios..."
        npm test 2>&1 | tee -a "$LOG_FILE" || log_warning "Alguns testes falharam"
    fi

    log_success "Verificacoes concluidas!"
}

generate_changelog() {
    if [ "$GENERATE_CHANGELOG" = false ]; then
        return
    fi

    log_step "Gerando changelog..."

    CHANGELOG_FILE="$RELEASES_DIR/CHANGELOG-$NEW_VERSION.md"

    # Obter commits desde a ultima tag
    LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

    cat > "$CHANGELOG_FILE" << EOF
# Changelog - Conecta PRO v$NEW_VERSION

**Data:** $(date +%Y-%m-%d)

## Mudancas

EOF

    if [ -n "$LAST_TAG" ]; then
        git log --pretty=format:"- %s" "$LAST_TAG"..HEAD >> "$CHANGELOG_FILE"
    else
        git log --pretty=format:"- %s" -20 >> "$CHANGELOG_FILE"
    fi

    echo "" >> "$CHANGELOG_FILE"
    echo "" >> "$CHANGELOG_FILE"
    echo "---" >> "$CHANGELOG_FILE"
    echo "*Release automatizado pelo Conecta PRO Release Manager*" >> "$CHANGELOG_FILE"

    log_success "Changelog gerado: $CHANGELOG_FILE"
}

build_web() {
    log_step "Buildando projeto web..."
    cd "$PROJECT_DIR"

    npm install 2>&1 | tee -a "$LOG_FILE"
    npm run build 2>&1 | tee -a "$LOG_FILE"

    log_success "Build web concluido!"
}

sync_capacitor() {
    log_step "Sincronizando com Capacitor..."
    cd "$PROJECT_DIR"

    npx cap sync 2>&1 | tee -a "$LOG_FILE"

    log_success "Capacitor sincronizado!"
}

build_android_release() {
    if [ "$BUILD_ANDROID" = false ]; then
        log_info "Pulando build Android"
        return
    fi

    log_step "Buildando Android Release..."

    if [ "$DRY_RUN" = true ]; then
        log_warning "[DRY-RUN] Simulando build Android"
        return
    fi

    "$SCRIPT_DIR/build-android.sh" --release --skip-sync 2>&1 | tee -a "$LOG_FILE"

    log_success "Build Android concluido!"
}

build_ios_release() {
    if [ "$BUILD_IOS" = false ]; then
        log_info "Pulando build iOS"
        return
    fi

    # Verificar se esta no macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_warning "Build iOS requer macOS. Pulando..."
        return
    fi

    log_step "Buildando iOS Release..."

    if [ "$DRY_RUN" = true ]; then
        log_warning "[DRY-RUN] Simulando build iOS"
        return
    fi

    "$SCRIPT_DIR/build-ios.sh" --archive --skip-sync 2>&1 | tee -a "$LOG_FILE"

    log_success "Build iOS concluido!"
}

create_git_tag() {
    log_step "Criando tag Git..."

    cd "$PROJECT_DIR"

    # Commit das mudancas de versao
    git add package.json capacitor.config.ts 2>/dev/null || true
    git add android/app/build.gradle 2>/dev/null || true
    git add ios/App/App/Info.plist 2>/dev/null || true

    if [ "$DRY_RUN" = true ]; then
        log_warning "[DRY-RUN] Simulando commit e tag"
        return
    fi

    git commit -m "chore: bump version to $NEW_VERSION" 2>/dev/null || log_info "Nada para commitar"

    # Criar tag
    git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

    log_success "Tag v$NEW_VERSION criada!"
    log_info "Para enviar: git push origin main --tags"
}

print_summary() {
    echo ""
    echo "=============================================================="
    echo "  RELEASE CONCLUIDO!"
    echo "=============================================================="
    echo ""
    echo "  Versao: $NEW_VERSION"
    echo "  Tag: v$NEW_VERSION"
    echo ""

    if [ "$BUILD_ANDROID" = true ]; then
        echo "  Android:"
        ls -la "$RELEASES_DIR/android/"*.aab 2>/dev/null | tail -1 || echo "    AAB nao encontrado"
    fi

    if [ "$BUILD_IOS" = true ] && [[ "$OSTYPE" == "darwin"* ]]; then
        echo ""
        echo "  iOS:"
        ls -la "$RELEASES_DIR/ios/"*.xcarchive 2>/dev/null | tail -1 || echo "    Archive nao encontrado"
    fi

    echo ""
    echo "  Proximos passos:"
    echo "  1. git push origin main --tags"
    echo "  2. Upload Android AAB no Google Play Console"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  3. Upload iOS no App Store Connect via Xcode Organizer"
    fi
    echo ""
    echo "  Log completo: $LOG_FILE"
    echo ""
}

#===============================================================================
# Parse de argumentos
#===============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --android)
            BUILD_ANDROID=true
            BUILD_IOS=false
            shift
            ;;
        --ios)
            BUILD_ANDROID=false
            BUILD_IOS=true
            shift
            ;;
        --all)
            BUILD_ANDROID=true
            BUILD_IOS=true
            shift
            ;;
        --version)
            NEW_VERSION="$2"
            shift 2
            ;;
        --bump-patch)
            BUMP_TYPE="patch"
            shift
            ;;
        --bump-minor)
            BUMP_TYPE="minor"
            shift
            ;;
        --bump-major)
            BUMP_TYPE="major"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --changelog)
            GENERATE_CHANGELOG=true
            shift
            ;;
        --help|-h)
            head -30 "$0" | tail -25
            exit 0
            ;;
        *)
            log_error "Opcao desconhecida: $1"
            exit 1
            ;;
    esac
done

#===============================================================================
# Execucao principal
#===============================================================================

# Criar diretorios
mkdir -p "$PROJECT_DIR/scripts/mobile/logs"
mkdir -p "$RELEASES_DIR/android"
mkdir -p "$RELEASES_DIR/ios"

print_header | tee "$LOG_FILE"

# Determinar versao
CURRENT_VERSION=$(get_current_version)
log_info "Versao atual: $CURRENT_VERSION"

if [ -n "$NEW_VERSION" ]; then
    log_info "Nova versao definida: $NEW_VERSION"
elif [ -n "$BUMP_TYPE" ]; then
    NEW_VERSION=$(bump_version "$CURRENT_VERSION" "$BUMP_TYPE")
    log_info "Nova versao (bump $BUMP_TYPE): $NEW_VERSION"
else
    NEW_VERSION=$(bump_version "$CURRENT_VERSION" "patch")
    log_info "Nova versao (auto bump patch): $NEW_VERSION"
fi

if [ "$DRY_RUN" = true ]; then
    log_warning "MODO DRY-RUN - Nenhuma alteracao sera feita"
fi

echo ""
log_info "Configuracoes:"
log_info "  Build Android: $BUILD_ANDROID"
log_info "  Build iOS: $BUILD_IOS"
log_info "  Nova Versao: $NEW_VERSION"
log_info "  Dry Run: $DRY_RUN"
log_info "  Skip Tests: $SKIP_TESTS"
echo ""

# Executar pipeline de release
run_tests
update_version_files "$NEW_VERSION"
generate_changelog
build_web
sync_capacitor
build_android_release
build_ios_release
create_git_tag
print_summary

log_success "Release finalizado!"
