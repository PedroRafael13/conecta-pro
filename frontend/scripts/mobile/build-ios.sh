#!/bin/bash
#===============================================================================
# CONECTA PRO - Build iOS Automatizado
#===============================================================================
# Este script automatiza todo o processo de build do app iOS
# REQUER: macOS com Xcode instalado
#
# Uso:
#   ./scripts/mobile/build-ios.sh [opcoes]
#
# Opcoes:
#   --release       Build de release (padrao)
#   --debug         Build de debug
#   --archive       Criar archive para App Store
#   --simulator     Build para simulador
#   --device        Build para device fisico
#   --export-ipa    Exportar IPA apos archive
#   --clean         Limpar builds anteriores
#   --skip-sync     Pular npm install e cap sync
#   --skip-pods     Pular pod install
#   --open          Abrir Xcode apos sync
#
# Exemplos:
#   ./scripts/mobile/build-ios.sh --archive --export-ipa
#   ./scripts/mobile/build-ios.sh --simulator --debug
#   ./scripts/mobile/build-ios.sh --open
#===============================================================================

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretorio base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
IOS_DIR="$PROJECT_DIR/ios/App"

# Configuracoes padrao
BUILD_TYPE="release"
BUILD_TARGET="device"  # device, simulator, archive
EXPORT_IPA=false
CLEAN_BUILD=false
SKIP_SYNC=false
SKIP_PODS=false
OPEN_XCODE=false

# Configuracoes do projeto
SCHEME="App"
WORKSPACE="App.xcworkspace"
BUNDLE_ID="br.com.conectapro.app"
TEAM_ID=""  # Sera detectado automaticamente

# Arquivo de output
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/scripts/mobile/logs/ios_build_$TIMESTAMP.log"

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

print_header() {
    echo ""
    echo "=============================================================="
    echo "  CONECTA PRO - Build iOS"
    echo "  $(date)"
    echo "=============================================================="
    echo ""
}

check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "Este script requer macOS com Xcode instalado."
        log_error "Sistema detectado: $OSTYPE"
        exit 1
    fi
    log_info "macOS detectado: $(sw_vers -productVersion)"
}

check_requirements() {
    log_info "Verificando requisitos..."

    # Xcode
    if ! command -v xcodebuild &> /dev/null; then
        log_error "Xcode nao encontrado. Instale pela App Store."
        exit 1
    fi
    XCODE_VERSION=$(xcodebuild -version | head -1)
    log_info "Xcode: $XCODE_VERSION"

    # Xcode Command Line Tools
    if ! xcode-select -p &> /dev/null; then
        log_error "Xcode Command Line Tools nao instalado."
        log_info "Execute: xcode-select --install"
        exit 1
    fi

    # Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js nao encontrado. Instale em https://nodejs.org"
        exit 1
    fi
    log_info "Node.js: $(node -v)"

    # CocoaPods
    if ! command -v pod &> /dev/null; then
        log_warning "CocoaPods nao encontrado. Instalando..."
        sudo gem install cocoapods
    fi
    log_info "CocoaPods: $(pod --version)"

    # Verificar se aceita licenca do Xcode
    if ! xcodebuild -license check &> /dev/null; then
        log_warning "Licenca do Xcode nao aceita. Aceitando..."
        sudo xcodebuild -license accept
    fi

    log_success "Todos os requisitos atendidos!"
}

check_signing() {
    log_info "Verificando configuracao de assinatura..."

    # Listar identidades de assinatura disponiveis
    IDENTITIES=$(security find-identity -v -p codesigning 2>/dev/null | grep "Apple Distribution\|iPhone Distribution\|Apple Development" || true)

    if [ -z "$IDENTITIES" ]; then
        log_warning "Nenhum certificado de distribuicao encontrado."
        log_warning "Para builds de producao, configure sua conta Apple Developer no Xcode."
        log_warning "Xcode > Preferences > Accounts > Adicionar Apple ID"
    else
        log_info "Certificados disponiveis:"
        echo "$IDENTITIES" | while read line; do
            log_info "  $line"
        done
    fi

    # Detectar Team ID
    TEAM_ID=$(security find-identity -v -p codesigning 2>/dev/null | grep "Apple Distribution\|iPhone Distribution" | head -1 | sed 's/.*(\([A-Z0-9]*\)).*/\1/' || true)

    if [ -n "$TEAM_ID" ]; then
        log_info "Team ID detectado: $TEAM_ID"
    fi
}

sync_project() {
    if [ "$SKIP_SYNC" = true ]; then
        log_info "Pulando sincronizacao (--skip-sync)"
        return
    fi

    log_info "Instalando dependencias npm..."
    cd "$PROJECT_DIR"
    npm install 2>&1 | tee -a "$LOG_FILE"

    log_info "Buildando projeto web..."
    npm run build 2>&1 | tee -a "$LOG_FILE"

    log_info "Sincronizando com Capacitor..."
    npx cap sync ios 2>&1 | tee -a "$LOG_FILE"

    log_success "Projeto sincronizado!"
}

install_pods() {
    if [ "$SKIP_PODS" = true ]; then
        log_info "Pulando pod install (--skip-pods)"
        return
    fi

    log_info "Instalando CocoaPods..."
    cd "$IOS_DIR"

    # Verificar se Podfile existe
    if [ ! -f "Podfile" ]; then
        log_error "Podfile nao encontrado em $IOS_DIR"
        exit 1
    fi

    # Atualizar repos se necessario
    if [ ! -d "$HOME/.cocoapods/repos/trunk" ]; then
        log_info "Atualizando repositorio CocoaPods..."
        pod repo update 2>&1 | tee -a "$LOG_FILE"
    fi

    pod install 2>&1 | tee -a "$LOG_FILE"

    log_success "CocoaPods instalado!"
}

clean_build() {
    if [ "$CLEAN_BUILD" = true ]; then
        log_info "Limpando builds anteriores..."
        cd "$IOS_DIR"

        xcodebuild clean \
            -workspace "$WORKSPACE" \
            -scheme "$SCHEME" \
            2>&1 | tee -a "$LOG_FILE"

        # Limpar DerivedData
        rm -rf ~/Library/Developer/Xcode/DerivedData/App-* 2>/dev/null || true

        log_success "Build limpo!"
    fi
}

build_ios() {
    cd "$IOS_DIR"

    case $BUILD_TARGET in
        simulator)
            log_info "Buildando para Simulador..."
            DESTINATION="platform=iOS Simulator,name=iPhone 15 Pro"
            CONFIGURATION=$([ "$BUILD_TYPE" = "release" ] && echo "Release" || echo "Debug")

            xcodebuild build \
                -workspace "$WORKSPACE" \
                -scheme "$SCHEME" \
                -configuration "$CONFIGURATION" \
                -destination "$DESTINATION" \
                CODE_SIGN_IDENTITY="" \
                CODE_SIGNING_REQUIRED=NO \
                2>&1 | tee -a "$LOG_FILE"
            ;;

        device)
            log_info "Buildando para Device..."
            CONFIGURATION=$([ "$BUILD_TYPE" = "release" ] && echo "Release" || echo "Debug")

            xcodebuild build \
                -workspace "$WORKSPACE" \
                -scheme "$SCHEME" \
                -configuration "$CONFIGURATION" \
                -destination "generic/platform=iOS" \
                2>&1 | tee -a "$LOG_FILE"
            ;;

        archive)
            log_info "Criando Archive para App Store..."
            ARCHIVE_PATH="$PROJECT_DIR/releases/ios/ConectaPRO-$TIMESTAMP.xcarchive"
            mkdir -p "$(dirname "$ARCHIVE_PATH")"

            xcodebuild archive \
                -workspace "$WORKSPACE" \
                -scheme "$SCHEME" \
                -configuration Release \
                -destination "generic/platform=iOS" \
                -archivePath "$ARCHIVE_PATH" \
                2>&1 | tee -a "$LOG_FILE"

            if [ -d "$ARCHIVE_PATH" ]; then
                log_success "Archive criado: $ARCHIVE_PATH"
            else
                log_error "Falha ao criar archive"
                exit 1
            fi
            ;;
    esac

    log_success "Build concluido!"
}

export_ipa() {
    if [ "$EXPORT_IPA" = true ] && [ "$BUILD_TARGET" = "archive" ]; then
        log_info "Exportando IPA..."

        ARCHIVE_PATH="$PROJECT_DIR/releases/ios/ConectaPRO-$TIMESTAMP.xcarchive"
        EXPORT_PATH="$PROJECT_DIR/releases/ios"
        EXPORT_OPTIONS="$PROJECT_DIR/scripts/mobile/ExportOptions.plist"

        # Criar ExportOptions.plist se nao existir
        if [ ! -f "$EXPORT_OPTIONS" ]; then
            log_info "Criando ExportOptions.plist..."
            cat > "$EXPORT_OPTIONS" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>destination</key>
    <string>upload</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>uploadSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <false/>
</dict>
</plist>
PLIST
        fi

        xcodebuild -exportArchive \
            -archivePath "$ARCHIVE_PATH" \
            -exportPath "$EXPORT_PATH" \
            -exportOptionsPlist "$EXPORT_OPTIONS" \
            2>&1 | tee -a "$LOG_FILE"

        IPA_FILE=$(find "$EXPORT_PATH" -name "*.ipa" -newer "$ARCHIVE_PATH" | head -1)

        if [ -n "$IPA_FILE" ]; then
            log_success "IPA exportado: $IPA_FILE"
        else
            log_warning "IPA nao encontrado. Verifique as configuracoes de assinatura."
        fi
    fi
}

open_xcode() {
    if [ "$OPEN_XCODE" = true ]; then
        log_info "Abrindo Xcode..."
        open "$IOS_DIR/$WORKSPACE"
    fi
}

print_summary() {
    echo ""
    echo "=============================================================="
    echo "  BUILD iOS CONCLUIDO!"
    echo "=============================================================="
    echo ""
    echo "  Build Type: $BUILD_TYPE"
    echo "  Target: $BUILD_TARGET"
    echo "  Log: $LOG_FILE"
    echo ""

    if [ "$BUILD_TARGET" = "archive" ]; then
        echo "  Archive: $PROJECT_DIR/releases/ios/ConectaPRO-$TIMESTAMP.xcarchive"
        echo ""
        echo "  Proximos passos para App Store:"
        echo "  1. Abrir Xcode"
        echo "  2. Window > Organizer"
        echo "  3. Selecionar o archive"
        echo "  4. Distribute App > App Store Connect"
        echo ""
        echo "  Ou use Transporter app para upload direto."
        echo ""
    fi

    if [ "$BUILD_TARGET" = "simulator" ]; then
        echo "  Para rodar no simulador:"
        echo "  npm run cap:ios:run"
        echo ""
    fi
}

#===============================================================================
# Parse de argumentos
#===============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --release)
            BUILD_TYPE="release"
            shift
            ;;
        --debug)
            BUILD_TYPE="debug"
            shift
            ;;
        --archive)
            BUILD_TARGET="archive"
            shift
            ;;
        --simulator)
            BUILD_TARGET="simulator"
            shift
            ;;
        --device)
            BUILD_TARGET="device"
            shift
            ;;
        --export-ipa)
            EXPORT_IPA=true
            BUILD_TARGET="archive"
            shift
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --skip-sync)
            SKIP_SYNC=true
            shift
            ;;
        --skip-pods)
            SKIP_PODS=true
            shift
            ;;
        --open)
            OPEN_XCODE=true
            shift
            ;;
        --help|-h)
            head -40 "$0" | tail -35
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

# Criar diretorio de logs
mkdir -p "$PROJECT_DIR/scripts/mobile/logs"
mkdir -p "$PROJECT_DIR/releases/ios"

print_header | tee "$LOG_FILE"

log_info "Configuracoes:"
log_info "  Build Type: $BUILD_TYPE"
log_info "  Build Target: $BUILD_TARGET"
log_info "  Export IPA: $EXPORT_IPA"
log_info "  Clean Build: $CLEAN_BUILD"
log_info "  Open Xcode: $OPEN_XCODE"
echo ""

check_macos
check_requirements
check_signing
sync_project
install_pods
clean_build
build_ios
export_ipa
open_xcode
print_summary

log_success "Processo finalizado!"
