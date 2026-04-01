#!/bin/bash
# =============================================================================
# PRE-FLIGHT.SH — Verificação de impacto cruzado antes de modificar arquivo
# =============================================================================
# Uso: ./scripts/pre-flight.sh <arquivo.py> [--no-confirm]
#
# Extrai classes/funções do arquivo e mostra todos os arquivos que as referenciam.
# Útil antes de renomear classes, mover arquivos ou alterar interfaces.
# =============================================================================

set -euo pipefail

BACKEND="/opt/conecta-pro/backend"

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 <arquivo.py> [--no-confirm]"
    echo ""
    echo "Exemplos:"
    echo "  $0 modules/mobile/models/push_notification.py"
    echo "  $0 modules/config/models/tenant.py --no-confirm"
    exit 1
fi

FILE="$1"
NO_CONFIRM="${2:-}"

# Resolver path absoluto
if [[ ! "$FILE" = /* ]]; then
    if [[ -f "$BACKEND/$FILE" ]]; then
        FILE="$BACKEND/$FILE"
    elif [[ -f "/opt/conecta-pro/$FILE" ]]; then
        FILE="/opt/conecta-pro/$FILE"
    fi
fi

if [[ ! -f "$FILE" ]]; then
    echo "❌ Arquivo não encontrado: $FILE"
    exit 1
fi

BASENAME=$(basename "$FILE" .py)

# Extrair nomes de classes definidas no arquivo
CLASSES=$(grep -oP '(?<=^class )\w+' "$FILE" 2>/dev/null || true)
# Extrair nomes de funções de nível superior
FUNCTIONS=$(grep -oP '(?<=^def )\w+|(?<=^async def )\w+' "$FILE" 2>/dev/null || true)

# Combinar todos os símbolos
SYMBOLS="$CLASSES"
if [[ -n "$FUNCTIONS" ]]; then
    SYMBOLS="$SYMBOLS
$FUNCTIONS"
fi

if [[ -z "$SYMBOLS" ]]; then
    echo "⚠️  Nenhuma classe ou função encontrada em: $FILE"
    exit 0
fi

echo "═══════════════════════════════════════════"
echo "PRE-FLIGHT CHECK: $(basename "$FILE")"
echo "═══════════════════════════════════════════"
echo ""

TOTAL_AFFECTED=0
ALL_FILES=""

while IFS= read -r SYMBOL; do
    [[ -z "$SYMBOL" ]] && continue

    # Buscar referências (excluindo o próprio arquivo e __pycache__)
    REFS=$(grep -rl "$SYMBOL" "$BACKEND" --include="*.py" 2>/dev/null | grep -v "__pycache__" | grep -v "$FILE" | sort -u || true)

    if [[ -n "$REFS" ]]; then
        COUNT=$(echo "$REFS" | wc -l)
        TOTAL_AFFECTED=$((TOTAL_AFFECTED + COUNT))

        echo "📌 $SYMBOL — referenciado em $COUNT arquivo(s):"
        I=1
        while IFS= read -r REF; do
            # Mostrar path relativo ao backend
            REL_PATH="${REF#$BACKEND/}"
            echo "   $I. $REL_PATH"
            ALL_FILES="$ALL_FILES
$REF"
            I=$((I + 1))
        done <<< "$REFS"
        echo ""
    fi
done <<< "$SYMBOLS"

# Deduplicate
UNIQUE_FILES=$(echo "$ALL_FILES" | sort -u | grep -v "^$" | wc -l)

echo "═══════════════════════════════════════════"
if [[ $TOTAL_AFFECTED -eq 0 ]]; then
    echo "✓ Nenhuma referência externa encontrada."
    echo "  Seguro para modificar sem impacto cruzado."
    exit 0
fi

echo "⚠️  TOTAL: $UNIQUE_FILES arquivo(s) únicos afetados"
echo ""
echo "AÇÃO: Modificar $(basename "$FILE") pode quebrar os"
echo "       imports/referências listados acima."
echo "═══════════════════════════════════════════"

if [[ "$NO_CONFIRM" == "--no-confirm" ]]; then
    exit 0
fi

# Em modo interativo (quando executado diretamente)
if [[ -t 0 ]]; then
    echo ""
    read -p "Confirma modificação? [s/N]: " -n 1 CONFIRM
    echo ""
    if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
        echo "Cancelado."
        exit 1
    fi
    echo "✓ Confirmado. Prosseguindo..."
    exit 0
else
    # Não-interativo: apenas reporta
    exit 0
fi
