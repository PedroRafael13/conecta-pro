# Setup Mobile Build - Conecta PRO

Prepara o ambiente local para builds de apps moveis.

## Verificar Requisitos

Execute estes comandos para verificar o ambiente:

```bash
# Node.js (requer 18+)
node -v

# npm
npm -v

# Java (requer 17+)
java -version

# Android SDK
echo $ANDROID_HOME

# Xcode (apenas Mac)
xcodebuild -version

# CocoaPods (apenas Mac)
pod --version
```

## Instalacao Android (Linux/Mac/Windows)

1. **Android Studio:**
   - Download: https://developer.android.com/studio
   - Instalar e abrir
   - SDK Manager > Instalar SDK 34

2. **Configurar ANDROID_HOME:**
```bash
# Linux/Mac - adicionar ao ~/.bashrc ou ~/.zshrc
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Recarregar
source ~/.bashrc
```

3. **Aceitar licencas:**
```bash
yes | sdkmanager --licenses
```

## Instalacao iOS (apenas Mac)

1. **Xcode:**
   - Mac App Store > Instalar Xcode
   - Aceitar licenca: `sudo xcodebuild -license accept`

2. **Command Line Tools:**
```bash
xcode-select --install
```

3. **CocoaPods:**
```bash
sudo gem install cocoapods
pod setup
```

4. **Configurar Apple Developer:**
   - Xcode > Preferences > Accounts
   - Adicionar Apple ID
   - Download provisioning profiles

## Preparar Projeto

```bash
# Clonar/navegar para o projeto
cd /caminho/para/conecta-pro/frontend

# Instalar dependencias
npm install

# Verificar build web
npm run build

# Adicionar plataformas
npx cap add android
npx cap add ios  # apenas Mac

# Sincronizar
npx cap sync
```

## Configurar Keystore Android

```bash
cd android

# Gerar keystore (primeira vez)
keytool -genkey -v -keystore release-key.keystore \
  -alias conectapro \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Guardar senha em local seguro!
```

## Testar Build

```bash
# Android
./scripts/mobile/build-android.sh --debug --apk

# iOS (Mac)
./scripts/mobile/build-ios.sh --simulator --debug
```

## Tornar Scripts Executaveis

```bash
chmod +x scripts/mobile/build-android.sh
chmod +x scripts/mobile/build-ios.sh
chmod +x scripts/mobile/release.sh
```

## Troubleshooting

**Node modules corrompidos:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Gradle cache corrompido:**
```bash
cd android
./gradlew clean
rm -rf ~/.gradle/caches
```

**Xcode DerivedData:**
```bash
rm -rf ~/Library/Developer/Xcode/DerivedData
```

**CocoaPods corrompido:**
```bash
cd ios/App
pod deintegrate
pod install
```
