# Build iOS - Conecta PRO

Execute o build do app iOS para publicacao na Apple App Store.

**IMPORTANTE:** Este comando requer macOS com Xcode instalado.

## Instrucoes

1. Verifique os requisitos:
   - macOS
   - Xcode instalado
   - Conta Apple Developer configurada no Xcode
   - CocoaPods instalado

2. Execute o script de build:
```bash
./scripts/mobile/build-ios.sh --archive --export-ipa
```

3. Para build de simulador (testes):
```bash
./scripts/mobile/build-ios.sh --simulator --debug
```

4. Para abrir Xcode e fazer upload manual:
```bash
./scripts/mobile/build-ios.sh --open
# Depois: Product > Archive > Distribute App
```

5. O arquivo gerado estara em:
   - Archive: `releases/ios/ConectaPRO-*.xcarchive`
   - IPA: `releases/ios/*.ipa`

## Opcoes do Script

- `--release` - Build de release (padrao)
- `--debug` - Build de debug
- `--archive` - Criar archive para App Store
- `--simulator` - Build para simulador
- `--device` - Build para device fisico
- `--export-ipa` - Exportar IPA apos archive
- `--clean` - Limpar builds anteriores
- `--skip-sync` - Pular npm install e cap sync
- `--skip-pods` - Pular pod install
- `--open` - Abrir Xcode apos sync

## Upload na App Store

1. Via Xcode:
   - Window > Organizer
   - Selecionar archive
   - Distribute App > App Store Connect

2. Via Transporter:
   - Baixar app Transporter na Mac App Store
   - Arrastar arquivo .ipa

## Troubleshooting

Se certificado nao encontrado:
1. Xcode > Preferences > Accounts
2. Download Manual Profiles
3. Reiniciar Xcode

Se CocoaPods com erro:
```bash
cd ios/App && pod install --repo-update
```
