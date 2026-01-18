# Release Mobile - Conecta PRO

Gerencia o processo completo de release para Android e iOS.

## Instrucoes

1. Para release completo com bump de versao:
```bash
./scripts/mobile/release.sh --all --bump-patch
```

2. Para release apenas Android:
```bash
./scripts/mobile/release.sh --android --bump-patch
```

3. Para release apenas iOS (requer Mac):
```bash
./scripts/mobile/release.sh --ios --bump-patch
```

4. Para simular sem executar (dry-run):
```bash
./scripts/mobile/release.sh --all --dry-run
```

5. Para definir versao especifica:
```bash
./scripts/mobile/release.sh --all --version 1.2.0
```

## O que o Release faz

1. Executa testes (tsc, lint)
2. Atualiza versao em todos os arquivos
3. Gera changelog (se --changelog)
4. Build web (npm run build)
5. Sync Capacitor
6. Build Android (AAB)
7. Build iOS (Archive) - se Mac
8. Cria tag Git

## Opcoes do Script

- `--android` - Release apenas Android
- `--ios` - Release apenas iOS
- `--all` - Release Android e iOS (padrao)
- `--version X.Y.Z` - Definir versao especifica
- `--bump-patch` - Incrementar patch (1.0.0 -> 1.0.1)
- `--bump-minor` - Incrementar minor (1.0.0 -> 1.1.0)
- `--bump-major` - Incrementar major (1.0.0 -> 2.0.0)
- `--dry-run` - Simular sem executar builds
- `--skip-tests` - Pular testes
- `--changelog` - Gerar changelog automatico

## Apos o Release

1. Push das mudancas:
```bash
git push origin main --tags
```

2. Upload Android:
   - Google Play Console
   - Producao > Nova versao
   - Upload do .aab

3. Upload iOS:
   - Xcode > Organizer
   - Distribute App

## Arquivos Gerados

- `releases/android/conecta-pro-release-*.aab`
- `releases/ios/ConectaPRO-*.xcarchive`
- `releases/CHANGELOG-*.md`
- `scripts/mobile/logs/release_*.log`
