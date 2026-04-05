#!/usr/bin/env bash
# governance-check.sh — Proteção contra commits multi-módulo por sessões autônomas
# Instalado em: 2026-04-05
# Motivo: 3 reverts automáticos (65c3ce14, f87e9c5b, f866cc6a)

STAGED=$(git diff --cached --name-only 2>/dev/null || true)
[ -z "$STAGED" ] && exit 0

MODULE_LIST=$(echo "$STAGED" | grep -oP '(?<=^frontend/src/app/modulos/)[^/]+(?=/)' || true)
MODULE_LIST+=$(echo "" && echo "$STAGED" | grep -oP '(?<=^backend/modules/)[^/]+(?=/)' || true)
UNIQUE_MODULES=$(echo "$MODULE_LIST" | sort -u | grep -v '^$' || true)
MODULE_COUNT=$(echo "$UNIQUE_MODULES" | grep -c '.' || true)

[ "$MODULE_COUNT" -le 1 ] && exit 0

MODULES_DISPLAY=$(echo "$UNIQUE_MODULES" | tr '\n' ',' | sed 's/,$//')
AUTHOR_NAME="${GIT_AUTHOR_NAME:-$(git config user.name 2>/dev/null || echo '')}"

IS_AUTONOMOUS=0
echo "$AUTHOR_NAME" | grep -qi "claude\|root@srv\|automated\|bot" && IS_AUTONOMOUS=1

if [ "$IS_AUTONOMOUS" -eq 1 ]; then
  echo ""
  echo "COMMIT BLOQUEADO — Sessao autonoma detectada com multiplos modulos em stage"
  echo ""
  echo "   Modulos: $MODULES_DISPLAY"
  echo "   Autor:   $AUTHOR_NAME"
  echo ""
  echo "   Regra (CLAUDE.md > Governanca): sessoes autonomas operam em 1 modulo por commit."
  echo "   Separe em commits distintos ou peca para Jordan commitar manualmente."
  echo ""
  exit 1
fi

echo ""
echo "AVISO: Este commit toca multiplos modulos: $MODULES_DISPLAY"
[ -t 0 ] && { echo "   Pressione Enter para continuar ou Ctrl+C para cancelar."; read -r _; }

exit 0
