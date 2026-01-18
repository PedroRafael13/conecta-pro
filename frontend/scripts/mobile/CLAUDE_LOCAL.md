# Conecta PRO - Guia para Build Local

## Sobre Este Arquivo

Este arquivo contém instrucoes para o Claude Code/Claude Cowork executar builds de apps moveis localmente na sua maquina.

**Requisitos da Maquina:**
- macOS (para iOS) ou Linux/Windows (apenas Android)
- Android Studio instalado (para Android)
- Xcode instalado (para iOS, apenas macOS)
- Node.js 18+
- JDK 17+

---

## Comandos Rapidos

### Build Android (Google Play)

```bash
# Build completo para Play Store
cd /caminho/para/conecta-pro/frontend
./scripts/mobile/build-android.sh --release --sign

# Build debug para testes
./scripts/mobile/build-android.sh --debug --apk --install

# Build limpo (limpa cache)
./scripts/mobile/build-android.sh --release --clean --sign
```

### Build iOS (App Store)

```bash
# Build para App Store (requer Mac)
cd /caminho/para/conecta-pro/frontend
./scripts/mobile/build-ios.sh --archive --export-ipa

# Build para simulador
./scripts/mobile/build-ios.sh --simulator --debug

# Abrir Xcode para ajustes
./scripts/mobile/build-ios.sh --open
```

### Release Completo

```bash
# Release Android + iOS com bump de versao
./scripts/mobile/release.sh --all --bump-patch

# Release apenas Android
./scripts/mobile/release.sh --android --bump-patch

# Simular release (dry-run)
./scripts/mobile/release.sh --all --dry-run
```

---

## Fluxo de Trabalho Recomendado

### 1. Preparacao do Ambiente

```bash
# Clonar/atualizar repositorio
git clone <repo-url> conecta-pro
cd conecta-pro/frontend

# Instalar dependencias
npm install

# Verificar tipos e lint
npx tsc --noEmit
npm run lint
```

### 2. Build e Teste Local

```bash
# Testar no navegador primeiro
npm run dev

# Build de producao web
npm run build

# Sync com Capacitor
npm run cap:sync
```

### 3. Build Android

```bash
# Se primeira vez, criar keystore
cd android
keytool -genkey -v -keystore release-key.keystore \
  -alias conectapro -keyalg RSA -keysize 2048 -validity 10000

# Voltar e executar build
cd ..
./scripts/mobile/build-android.sh --release --sign

# Arquivo gerado em: releases/android/conecta-pro-release-*.aab
```

### 4. Build iOS (Mac apenas)

```bash
# Configurar certificados no Xcode primeiro
# Xcode > Preferences > Accounts > Adicionar Apple ID

# Build
./scripts/mobile/build-ios.sh --archive --export-ipa

# Ou abrir Xcode para upload manual
./scripts/mobile/build-ios.sh --open
# Depois: Product > Archive > Distribute App
```

### 5. Upload nas Lojas

**Google Play Console:**
1. Acesse https://play.google.com/console
2. Selecione o app Conecta PRO
3. Producao > Criar nova versao
4. Upload do arquivo .aab
5. Preencher notas de versao
6. Enviar para revisao

**App Store Connect:**
1. Via Xcode: Window > Organizer > Distribute App
2. Ou via Transporter app com o .ipa

---

## Solucao de Problemas

### Android

**ANDROID_HOME nao configurado:**
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

**Erro de assinatura:**
```bash
# Verificar keystore
keytool -list -v -keystore android/release-key.keystore

# Limpar e rebuildar
cd android && ./gradlew clean && cd ..
./scripts/mobile/build-android.sh --release --clean --sign
```

**Gradle falha:**
```bash
# Atualizar Gradle wrapper
cd android
./gradlew wrapper --gradle-version 8.5
```

### iOS

**Certificado nao encontrado:**
1. Xcode > Preferences > Accounts
2. Selecionar time > Download Manual Profiles
3. Reiniciar Xcode

**CocoaPods erro:**
```bash
cd ios/App
pod deintegrate
pod install --repo-update
```

**Archive falha:**
```bash
# Limpar DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/App-*

# Build limpo
./scripts/mobile/build-ios.sh --archive --clean
```

---

## Estrutura de Arquivos Gerados

```
releases/
├── android/
│   ├── conecta-pro-release-20260118_120000.aab  # Para Play Store
│   └── conecta-pro-debug-20260118_120000.apk    # Para testes
├── ios/
│   ├── ConectaPRO-20260118_120000.xcarchive     # Archive iOS
│   └── ConectaPRO.ipa                           # Para distribuicao
└── CHANGELOG-1.0.1.md                           # Gerado com --changelog

scripts/mobile/logs/
├── android_build_20260118_120000.log
├── ios_build_20260118_120000.log
└── release_20260118_120000.log
```

---

## Checklist Pre-Release

- [ ] Todos os testes passando
- [ ] Versao atualizada em package.json
- [ ] Changelog atualizado
- [ ] Icones e splash screens finais
- [ ] Screenshots atualizados para as lojas
- [ ] Descricao do app atualizada
- [ ] Politica de privacidade URL valido
- [ ] Build testado em device real
- [ ] Assinatura configurada corretamente

---

## Comandos Claude Code

O Claude Code pode executar estes comandos diretamente:

```
# Via comandos customizados (se configurados)
/build-android
/build-ios
/release

# Ou via bash
Bash: ./scripts/mobile/build-android.sh --release
Bash: ./scripts/mobile/build-ios.sh --archive
Bash: ./scripts/mobile/release.sh --all --bump-patch
```

---

## Variaveis de Ambiente

Para builds automatizados, configure estas variaveis:

```bash
# Android
export ANDROID_HOME=/path/to/Android/Sdk
export KEYSTORE_PASSWORD=sua_senha_segura
export KEY_PASSWORD=sua_senha_segura

# iOS (apenas Mac)
export APPLE_ID=seu@email.com
export TEAM_ID=XXXXXXXXXX
```

---

*Ultima atualizacao: 18/01/2026*
