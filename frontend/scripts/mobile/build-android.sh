#!/bin/bash
#===============================================================================
# CONECTA PRO - Build Android Automatizado
#===============================================================================
# Este script automatiza todo o processo de build do app Android
# Pode ser executado pelo Claude Code ou manualmente
#
# Uso:
#   ./scripts/mobile/build-android.sh [opcoes]
#
# Opcoes:
#   --release     Build de release (padrao)
#   --debug       Build de debug
#   --apk         Gerar APK ao inves de AAB
#   --install     Instalar no device conectado apos build
#   --clean       Limpar builds anteriores antes de buildar
#   --skip-sync   Pular npm install e cap sync
#   --sign        Assinar com keystore de producao
#
# Exemplos:
#   ./scripts/mobile/build-android.sh --release --sign
#   ./scripts/mobile/build-android.sh --debug --install
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
ANDROID_DIR="$PROJECT_DIR/android"

# Configuracoes padrao
BUILD_TYPE="release"
OUTPUT_FORMAT="bundle"  # bundle (AAB) ou apk
INSTALL_AFTER=false
CLEAN_BUILD=false
SKIP_SYNC=false
SIGN_BUILD=false

# Arquivo de output
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/scripts/mobile/logs/android_build_$TIMESTAMP.log"

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
    echo "  CONECTA PRO - Build Android"
    echo "  $(date)"
    echo "=============================================================="
    echo ""
}

check_requirements() {
    log_info "Verificando requisitos..."

    # Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js nao encontrado. Instale em https://nodejs.org"
        exit 1
    fi
    log_info "Node.js: $(node -v)"

    # npm
    if ! command -v npm &> /dev/null; then
        log_error "npm nao encontrado."
        exit 1
    fi
    log_info "npm: $(npm -v)"

    # Java
    if ! command -v java &> /dev/null; then
        log_error "Java nao encontrado. Instale JDK 17+."
        exit 1
    fi
    log_info "Java: $(java -version 2>&1 | head -1)"

    # ANDROID_HOME
    if [ -z "$ANDROID_HOME" ]; then
        # Tentar encontrar automaticamente
        if [ -d "$HOME/Android/Sdk" ]; then
            export ANDROID_HOME="$HOME/Android/Sdk"
        elif [ -d "$HOME/Library/Android/sdk" ]; then
            export ANDROID_HOME="$HOME/Library/Android/sdk"
        elif [ -d "/usr/local/android-sdk" ]; then
            export ANDROID_HOME="/usr/local/android-sdk"
        else
            log_error "ANDROID_HOME nao configurado. Configure a variavel de ambiente."
            exit 1
        fi
    fi
    log_info "ANDROID_HOME: $ANDROID_HOME"

    # Gradle
    if [ -f "$ANDROID_DIR/gradlew" ]; then
        log_info "Gradle Wrapper encontrado"
    else
        log_error "Gradle Wrapper nao encontrado em $ANDROID_DIR"
        exit 1
    fi

    log_success "Todos os requisitos atendidos!"
}

check_keystore() {
    if [ "$SIGN_BUILD" = true ]; then
        KEYSTORE_PATH="$ANDROID_DIR/release-key.keystore"

        if [ ! -f "$KEYSTORE_PATH" ]; then
            log_warning "Keystore nao encontrado em $KEYSTORE_PATH"
            log_info "Criando novo keystore..."

            read -p "Senha do keystore: " -s KEYSTORE_PASSWORD
            echo ""
            read -p "Confirme a senha: " -s KEYSTORE_PASSWORD_CONFIRM
            echo ""

            if [ "$KEYSTORE_PASSWORD" != "$KEYSTORE_PASSWORD_CONFIRM" ]; then
                log_error "Senhas nao conferem!"
                exit 1
            fi

            keytool -genkey -v \
                -keystore "$KEYSTORE_PATH" \
                -alias conectapro \
                -keyalg RSA \
                -keysize 2048 \
                -validity 10000 \
                -storepass "$KEYSTORE_PASSWORD" \
                -keypass "$KEYSTORE_PASSWORD" \
                -dname "CN=Conecta PRO, OU=Mobile, O=Jordan Santos de Jesus LTDA, L=Brasil, ST=SP, C=BR"

            log_success "Keystore criado com sucesso!"
            log_warning "IMPORTANTE: Guarde a senha em local seguro!"
        else
            log_info "Keystore encontrado: $KEYSTORE_PATH"
        fi
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
    npx cap sync android 2>&1 | tee -a "$LOG_FILE"

    log_success "Projeto sincronizado!"
}

clean_build() {
    if [ "$CLEAN_BUILD" = true ]; then
        log_info "Limpando builds anteriores..."
        cd "$ANDROID_DIR"
        ./gradlew clean 2>&1 | tee -a "$LOG_FILE"
        log_success "Build limpo!"
    fi
}

build_android() {
    cd "$ANDROID_DIR"

    # Determinar comando de build
    if [ "$OUTPUT_FORMAT" = "bundle" ]; then
        if [ "$BUILD_TYPE" = "release" ]; then
            BUILD_CMD="bundleRelease"
        else
            BUILD_CMD="bundleDebug"
        fi
    else
        if [ "$BUILD_TYPE" = "release" ]; then
            BUILD_CMD="assembleRelease"
        else
            BUILD_CMD="assembleDebug"
        fi
    fi

    log_info "Executando: ./gradlew $BUILD_CMD"

    # Build
    if [ "$SIGN_BUILD" = true ] && [ "$BUILD_TYPE" = "release" ]; then
        # Build com assinatura
        if [ -z "$KEYSTORE_PASSWORD" ]; then
            read -p "Senha do keystore: " -s KEYSTORE_PASSWORD
            echo ""
        fi

        KEYSTORE_PASSWORD="$KEYSTORE_PASSWORD" \
        KEY_PASSWORD="$KEYSTORE_PASSWORD" \
        ./gradlew $BUILD_CMD 2>&1 | tee -a "$LOG_FILE"
    else
        ./gradlew $BUILD_CMD 2>&1 | tee -a "$LOG_FILE"
    fi

    log_success "Build concluido!"
}

find_output() {
    cd "$ANDROID_DIR"

    if [ "$OUTPUT_FORMAT" = "bundle" ]; then
        if [ "$BUILD_TYPE" = "release" ]; then
            OUTPUT_PATH="app/build/outputs/bundle/release/app-release.aab"
        else
            OUTPUT_PATH="app/build/outputs/bundle/debug/app-debug.aab"
        fi
    else
        if [ "$BUILD_TYPE" = "release" ]; then
            OUTPUT_PATH="app/build/outputs/apk/release/app-release.apk"
        else
            OUTPUT_PATH="app/build/outputs/apk/debug/app-debug.apk"
        fi
    fi

    FULL_OUTPUT_PATH="$ANDROID_DIR/$OUTPUT_PATH"

    if [ -f "$FULL_OUTPUT_PATH" ]; then
        OUTPUT_SIZE=$(du -h "$FULL_OUTPUT_PATH" | cut -f1)
        log_success "Arquivo gerado: $FULL_OUTPUT_PATH"
        log_info "Tamanho: $OUTPUT_SIZE"

        # Copiar para pasta de releases
        RELEASES_DIR="$PROJECT_DIR/releases/android"
        mkdir -p "$RELEASES_DIR"

        if [ "$OUTPUT_FORMAT" = "bundle" ]; then
            FINAL_NAME="conecta-pro-$BUILD_TYPE-$TIMESTAMP.aab"
        else
            FINAL_NAME="conecta-pro-$BUILD_TYPE-$TIMESTAMP.apk"
        fi

        cp "$FULL_OUTPUT_PATH" "$RELEASES_DIR/$FINAL_NAME"
        log_success "Copiado para: $RELEASES_DIR/$FINAL_NAME"

        echo ""
        echo "=============================================================="
        echo "  BUILD ANDROID CONCLUIDO COM SUCESSO!"
        echo "=============================================================="
        echo ""
        echo "  Arquivo: $RELEASES_DIR/$FINAL_NAME"
        echo "  Tamanho: $OUTPUT_SIZE"
        echo "  Log: $LOG_FILE"
        echo ""
        if [ "$OUTPUT_FORMAT" = "bundle" ]; then
            echo "  Proximo passo: Upload no Google Play Console"
            echo "  https://play.google.com/console"
        fi
        echo ""
    else
        log_error "Arquivo de output nao encontrado: $FULL_OUTPUT_PATH"
        exit 1
    fi
}

install_on_device() {
    if [ "$INSTALL_AFTER" = true ]; then
        log_info "Instalando no device conectado..."

        # Verificar se tem device conectado
        if ! adb devices | grep -q "device$"; then
            log_warning "Nenhum device conectado. Pulando instalacao."
            return
        fi

        if [ "$OUTPUT_FORMAT" = "apk" ]; then
            adb install -r "$FULL_OUTPUT_PATH" 2>&1 | tee -a "$LOG_FILE"
            log_success "App instalado no device!"
        else
            log_warning "AAB nao pode ser instalado diretamente. Use --apk para instalar."
        fi
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
        --apk)
            OUTPUT_FORMAT="apk"
            shift
            ;;
        --install)
            INSTALL_AFTER=true
            OUTPUT_FORMAT="apk"  # Precisa ser APK para instalar
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
        --sign)
            SIGN_BUILD=true
            shift
            ;;
        --help|-h)
            head -35 "$0" | tail -30
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

print_header | tee "$LOG_FILE"

log_info "Configuracoes:"
log_info "  Build Type: $BUILD_TYPE"
log_info "  Output Format: $OUTPUT_FORMAT"
log_info "  Sign Build: $SIGN_BUILD"
log_info "  Clean Build: $CLEAN_BUILD"
log_info "  Install After: $INSTALL_AFTER"
echo ""

check_requirements
check_keystore
sync_project
clean_build
build_android
find_output
install_on_device

log_success "Processo finalizado!"
