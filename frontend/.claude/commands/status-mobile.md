# Status Mobile - Conecta PRO

Verifica o estado atual do projeto mobile e requisitos.

## Verificar Estado do Projeto

Execute estes comandos para diagnosticar o ambiente:

```bash
# Versao atual do projeto
node -p "require('./package.json').version"

# Status Git
git status

# Ultima tag
git describe --tags --abbrev=0 2>/dev/null || echo "Nenhuma tag"

# Capacitor instalado
npx cap --version

# Plataformas adicionadas
ls -la android/ ios/ 2>/dev/null || echo "Plataformas nao adicionadas"
```

## Verificar Requisitos Android

```bash
# ANDROID_HOME
echo "ANDROID_HOME: $ANDROID_HOME"

# Java
java -version 2>&1 | head -1

# Gradle
[ -f android/gradlew ] && android/gradlew --version | head -3 || echo "Gradle nao encontrado"

# Keystore
[ -f android/release-key.keystore ] && echo "Keystore: OK" || echo "Keystore: NAO ENCONTRADO"
```

## Verificar Requisitos iOS (Mac)

```bash
# macOS
sw_vers 2>/dev/null || echo "Nao e macOS"

# Xcode
xcodebuild -version 2>/dev/null || echo "Xcode nao instalado"

# CocoaPods
pod --version 2>/dev/null || echo "CocoaPods nao instalado"

# Certificados
security find-identity -v -p codesigning 2>/dev/null | head -5
```

## Verificar Builds Anteriores

```bash
# Android
echo "=== Builds Android ==="
ls -lh releases/android/ 2>/dev/null || echo "Nenhum build"

# iOS
echo "=== Builds iOS ==="
ls -lh releases/ios/ 2>/dev/null || echo "Nenhum build"

# Logs
echo "=== Logs Recentes ==="
ls -lt scripts/mobile/logs/ 2>/dev/null | head -5
```

## Verificar Configuracao Capacitor

```bash
# capacitor.config.ts
cat capacitor.config.ts 2>/dev/null | grep -E "appId|appName|webDir"
```

## Status Completo

Para um diagnostico completo, execute:

```bash
echo "=== CONECTA PRO - STATUS MOBILE ==="
echo ""
echo "Projeto: $(node -p \"require('./package.json').name\")"
echo "Versao: $(node -p \"require('./package.json').version\")"
echo ""
echo "=== Node/NPM ==="
echo "Node: $(node -v)"
echo "NPM: $(npm -v)"
echo ""
echo "=== Capacitor ==="
echo "CLI: $(npx cap --version 2>/dev/null || echo 'N/A')"
echo "Android: $([ -d android ] && echo 'Instalado' || echo 'Nao instalado')"
echo "iOS: $([ -d ios ] && echo 'Instalado' || echo 'Nao instalado')"
echo ""
echo "=== Android ==="
echo "ANDROID_HOME: ${ANDROID_HOME:-'NAO CONFIGURADO'}"
echo "Java: $(java -version 2>&1 | head -1)"
echo "Keystore: $([ -f android/release-key.keystore ] && echo 'OK' || echo 'Nao encontrado')"
echo ""
echo "=== iOS ==="
echo "macOS: $(sw_vers -productVersion 2>/dev/null || echo 'N/A')"
echo "Xcode: $(xcodebuild -version 2>/dev/null | head -1 || echo 'N/A')"
echo "CocoaPods: $(pod --version 2>/dev/null || echo 'N/A')"
echo ""
echo "=== Builds Disponiveis ==="
echo "Android: $(ls releases/android/*.aab 2>/dev/null | wc -l) AAB, $(ls releases/android/*.apk 2>/dev/null | wc -l) APK"
echo "iOS: $(ls releases/ios/*.xcarchive 2>/dev/null | wc -l) Archives"
echo ""
echo "================================"
```

## Proximos Passos

Baseado no status, as acoes recomendadas sao:

1. **Se plataformas nao adicionadas:**
   ```bash
   npx cap add android
   npx cap add ios  # Mac apenas
   ```

2. **Se keystore nao existe:**
   ```bash
   /setup-mobile  # Usar comando setup
   ```

3. **Se builds desatualizados:**
   ```bash
   /release-mobile  # Usar comando release
   ```
