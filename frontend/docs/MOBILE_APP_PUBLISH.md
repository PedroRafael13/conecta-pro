# Conecta PRO - Publicação nas Lojas de Apps

## Visão Geral

Este documento descreve o processo completo para publicar o Conecta PRO nas lojas oficiais:
- **Google Play Store** (Android)
- **Apple App Store** (iOS)

## Pré-requisitos

### Para Android (Google Play)
- [ ] Conta Google Play Console ($25 taxa única)
- [ ] Android Studio instalado
- [ ] JDK 17 ou superior
- [ ] Chave de assinatura (keystore)

### Para iOS (App Store)
- [ ] Conta Apple Developer ($99/ano)
- [ ] Mac com Xcode instalado
- [ ] Certificados de distribuição
- [ ] CocoaPods instalado

---

## Configuração Inicial

### 1. Informações do App

```
App ID: br.com.conectapro.app
Nome: Conecta PRO
Versão: 1.0.0
```

### 2. Gerar Ícones e Splash Screens

```bash
# Requer imagem source em resources/icon.png (1024x1024)
# E splash em resources/splash.png (2732x2732)
npm run cap:assets
```

---

## Build Android

### 1. Configurar Keystore (Primeira vez)

```bash
cd android

# Gerar keystore para assinatura
keytool -genkey -v -keystore release-key.keystore \
  -alias conectapro \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Guardar as senhas em local seguro!
```

### 2. Configurar Assinatura

Editar `android/app/build.gradle`:

```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file('../release-key.keystore')
            storePassword System.getenv("KEYSTORE_PASSWORD") ?: "sua_senha"
            keyAlias 'conectapro'
            keyPassword System.getenv("KEY_PASSWORD") ?: "sua_senha"
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 3. Build do APK/AAB

```bash
# Sincronizar projeto
npm run cap:build

# Entrar na pasta Android
cd android

# Build AAB (recomendado para Play Store)
./gradlew bundleRelease

# OU Build APK
./gradlew assembleRelease

# Arquivos gerados:
# AAB: android/app/build/outputs/bundle/release/app-release.aab
# APK: android/app/build/outputs/apk/release/app-release.apk
```

### 4. Publicar no Google Play

1. Acesse [Google Play Console](https://play.google.com/console)
2. Criar novo aplicativo
3. Preencher informações:
   - Nome: Conecta PRO
   - Descrição curta: Sistema de Gestão Empresarial Inteligente
   - Categoria: Negócios
   - Classificação: Todos
4. Upload do AAB em "Produção > Criar nova versão"
5. Adicionar screenshots (mínimo 2)
6. Preencher política de privacidade
7. Enviar para revisão

---

## Build iOS

### 1. Configurar Projeto no Xcode

```bash
# Sincronizar projeto
npm run cap:build

# Abrir no Xcode
npm run cap:ios
```

### 2. Configurações no Xcode

1. Selecionar "App" no navigator
2. Em "Signing & Capabilities":
   - Team: Selecionar sua conta Apple Developer
   - Bundle Identifier: `br.com.conectapro.app`
   - Automatically manage signing: ✓
3. Em "General":
   - Display Name: Conecta PRO
   - Version: 1.0.0
   - Build: 1

### 3. Configurar Capabilities

Em "Signing & Capabilities", adicionar:
- Push Notifications
- Background Modes (se necessário)

### 4. Build para App Store

1. Product > Archive
2. Aguardar build
3. Window > Organizer
4. Selecionar archive > Distribute App
5. App Store Connect > Upload

### 5. Publicar na App Store

1. Acesse [App Store Connect](https://appstoreconnect.apple.com)
2. Criar novo aplicativo
3. Preencher informações:
   - Nome: Conecta PRO
   - Descrição: Sistema completo de gestão empresarial
   - Categoria: Negócios
   - Classificação etária: 4+
4. Adicionar screenshots para cada device
5. Preencher informações de revisão
6. Enviar para revisão

---

## Configurações Específicas

### Push Notifications

#### Android (Firebase)
1. Criar projeto no [Firebase Console](https://console.firebase.google.com)
2. Baixar `google-services.json`
3. Colocar em `android/app/google-services.json`

#### iOS (APNs)
1. Criar certificado APNs no Apple Developer
2. Configurar no Xcode em Signing & Capabilities
3. Enviar certificado para o backend

### Deep Links

#### Android
Editar `android/app/src/main/AndroidManifest.xml`:

```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="conectapro" />
    <data android:scheme="https" android:host="app.conectapro.com.br" />
</intent-filter>
```

#### iOS
Editar `ios/App/App/Info.plist`:

```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>conectapro</string>
        </array>
    </dict>
</array>
```

---

## Atualizações

### Processo de Atualização

1. Atualizar versão em `package.json`
2. Atualizar versão em `capacitor.config.ts`
3. Build e sync: `npm run cap:build`
4. Build nativo (Android/iOS)
5. Upload para as lojas

### Versionamento

```
Formato: MAJOR.MINOR.PATCH
Exemplo: 1.2.3

Android: versionCode (inteiro incremental)
iOS: Build number (inteiro incremental)
```

---

## Checklist de Publicação

### Google Play Store
- [ ] Ícone 512x512 PNG
- [ ] Feature Graphic 1024x500 PNG
- [ ] Screenshots (mínimo 2, max 8) para cada device
- [ ] Descrição curta (80 caracteres)
- [ ] Descrição completa (4000 caracteres)
- [ ] Categoria selecionada
- [ ] Classificação de conteúdo preenchida
- [ ] Política de privacidade URL
- [ ] AAB assinado

### Apple App Store
- [ ] Ícone 1024x1024 PNG (sem alpha)
- [ ] Screenshots para iPhone 6.5" (1284x2778)
- [ ] Screenshots para iPhone 5.5" (1242x2208)
- [ ] Screenshots para iPad 12.9" (2048x2732)
- [ ] Descrição (até 4000 caracteres)
- [ ] Palavras-chave (100 caracteres)
- [ ] URL de suporte
- [ ] URL de política de privacidade
- [ ] Informações de contato do app review

---

## Scripts Disponíveis

```bash
# Build + Sync
npm run cap:build

# Abrir Android Studio
npm run cap:android

# Abrir Xcode
npm run cap:ios

# Rodar em device/emulador Android
npm run cap:android:run

# Rodar em device/simulador iOS
npm run cap:ios:run

# Gerar ícones e splash screens
npm run cap:assets

# Apenas sync (sem build)
npm run cap:sync
```

---

## Troubleshooting

### Android

**Erro de assinatura:**
```bash
# Verificar keystore
keytool -list -v -keystore release-key.keystore
```

**Erro de build Gradle:**
```bash
cd android
./gradlew clean
./gradlew bundleRelease
```

### iOS

**Erro de provisioning:**
1. Xcode > Preferences > Accounts
2. Baixar provisioning profiles manualmente
3. Reiniciar Xcode

**Erro de CocoaPods:**
```bash
cd ios/App
pod install --repo-update
```

---

## Suporte

Em caso de dúvidas sobre publicação:
- [Documentação Capacitor](https://capacitorjs.com/docs/guides/deploying-updates)
- [Google Play Help](https://support.google.com/googleplay/android-developer)
- [App Store Connect Help](https://developer.apple.com/help/app-store-connect)

---

*Última atualização: 18/01/2026*
