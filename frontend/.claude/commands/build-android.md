# Build Android - Conecta PRO

Execute o build do app Android para publicacao na Google Play Store.

## Instrucoes

1. Verifique os requisitos:
   - Android Studio ou SDK instalado
   - ANDROID_HOME configurado
   - JDK 17+ instalado

2. Execute o script de build:
```bash
./scripts/mobile/build-android.sh --release --sign
```

3. Se for build de debug para testes:
```bash
./scripts/mobile/build-android.sh --debug --apk --install
```

4. O arquivo gerado estara em:
   - Release: `releases/android/conecta-pro-release-*.aab`
   - Debug: `releases/android/conecta-pro-debug-*.apk`

5. Para upload na Play Store:
   - Acesse https://play.google.com/console
   - Upload do arquivo .aab

## Opcoes do Script

- `--release` - Build de release (padrao)
- `--debug` - Build de debug
- `--apk` - Gerar APK ao inves de AAB
- `--install` - Instalar no device apos build
- `--clean` - Limpar builds anteriores
- `--skip-sync` - Pular npm install e cap sync
- `--sign` - Assinar com keystore de producao

## Troubleshooting

Se ANDROID_HOME nao estiver configurado:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
```

Se der erro de assinatura, verificar keystore:
```bash
keytool -list -v -keystore android/release-key.keystore
```
