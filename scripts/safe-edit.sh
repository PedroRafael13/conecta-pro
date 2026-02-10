#!/bin/bash
# =============================================================================
# SAFE-EDIT.SH — Edição com verificação automática de regressão
# =============================================================================
# Uso: ./scripts/safe-edit.sh "comando de edição"
#      ./scripts/safe-edit.sh "sed -i 's/OLD/NEW/g' arquivo.py"
#
# Comportamento:
#   1. Captura baseline (verify-instant)
#   2. Executa o comando
#   3. Verifica regressão (verify-instant)
#   4. Se piorou: reverte automaticamente
#   5. Se OK: confirma sucesso
# =============================================================================

set -euo pipefail

BACKEND="/opt/conecta-pro/backend"
SCRIPTS="/opt/conecta-pro/scripts"

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 \"comando de edição\""
    echo ""
    echo "Exemplos:"
    echo "  $0 \"sed -i 's/ACTIVE/ATIVO/g' tests/test_config.py\""
    echo "  $0 \"cp novo_arquivo.py modules/destino/\""
    exit 1
fi

COMMAND="$*"

echo "═══════════════════════════════════════════"
echo "SAFE-EDIT"
echo "═══════════════════════════════════════════"
echo ""
echo "Comando: $COMMAND"
echo ""

# --- Identificar arquivos afetados (para possível revert) ---
# Extrair paths de arquivos do comando
AFFECTED_FILES=()
for word in $COMMAND; do
    if [[ -f "$word" ]]; then
        AFFECTED_FILES+=("$word")
    elif [[ -f "$BACKEND/$word" ]]; then
        AFFECTED_FILES+=("$BACKEND/$word")
    fi
done

# Criar backups dos arquivos afetados
BACKUP_DIR=$(mktemp -d /tmp/safe-edit-XXXXX)
for f in "${AFFECTED_FILES[@]}"; do
    cp "$f" "$BACKUP_DIR/$(basename "$f").bak" 2>/dev/null || true
done

# --- 1. Baseline ANTES ---
echo "[ANTES] Rodando verify-instant..."
BEFORE_OUTPUT=$("$SCRIPTS/verify-instant.sh" 2>&1 || true)

# Extrair métricas do output
BEFORE_RUFF=$(echo "$BEFORE_OUTPUT" | grep -oP 'Ruff: \K\d+' || echo "?")
BEFORE_COLLECTION=$(echo "$BEFORE_OUTPUT" | grep -oP 'Collection: \K\d+' || echo "?")
BEFORE_COLLECTION_ERRORS=$(echo "$BEFORE_OUTPUT" | grep -oP 'Collection:.*?(\d+) erros' | grep -oP '\d+ erros' | grep -oP '^\d+' || echo "0")
BEFORE_ALEMBIC=$(echo "$BEFORE_OUTPUT" | grep -oP 'Alembic: \K\d+' || echo "?")

echo "[ANTES] Ruff: $BEFORE_RUFF erros | Collection: $BEFORE_COLLECTION testes, $BEFORE_COLLECTION_ERRORS erros | Alembic: $BEFORE_ALEMBIC head(s)"
echo ""

# --- 2. Executar comando ---
echo "Executando: $COMMAND"
eval "$COMMAND"
EXEC_STATUS=$?

if [[ $EXEC_STATUS -ne 0 ]]; then
    echo ""
    echo "❌ Comando falhou (exit code: $EXEC_STATUS)"
    echo "   Nenhuma alteração verificada."
    rm -rf "$BACKUP_DIR"
    exit $EXEC_STATUS
fi
echo ""

# --- 3. Baseline DEPOIS ---
echo "[DEPOIS] Rodando verify-instant..."
AFTER_OUTPUT=$("$SCRIPTS/verify-instant.sh" 2>&1 || true)

AFTER_RUFF=$(echo "$AFTER_OUTPUT" | grep -oP 'Ruff: \K\d+' || echo "?")
AFTER_COLLECTION=$(echo "$AFTER_OUTPUT" | grep -oP 'Collection: \K\d+' || echo "?")
AFTER_COLLECTION_ERRORS=$(echo "$AFTER_OUTPUT" | grep -oP 'Collection:.*?(\d+) erros' | grep -oP '\d+ erros' | grep -oP '^\d+' || echo "0")
AFTER_ALEMBIC=$(echo "$AFTER_OUTPUT" | grep -oP 'Alembic: \K\d+' || echo "?")

echo "[DEPOIS] Ruff: $AFTER_RUFF erros | Collection: $AFTER_COLLECTION testes, $AFTER_COLLECTION_ERRORS erros | Alembic: $AFTER_ALEMBIC head(s)"
echo ""

# --- 4. Comparar ---
REGRESSED=0
DETAILS=""

# Ruff piorou?
if [[ "$BEFORE_RUFF" != "?" && "$AFTER_RUFF" != "?" ]]; then
    if [[ "$AFTER_RUFF" -gt "$BEFORE_RUFF" ]]; then
        REGRESSED=1
        DETAILS="$DETAILS  Ruff: $BEFORE_RUFF → $AFTER_RUFF (+$((AFTER_RUFF - BEFORE_RUFF)))\n"
    fi
fi

# Collection errors aumentaram?
if [[ "$BEFORE_COLLECTION_ERRORS" != "?" && "$AFTER_COLLECTION_ERRORS" != "?" ]]; then
    if [[ "$AFTER_COLLECTION_ERRORS" -gt "$BEFORE_COLLECTION_ERRORS" ]]; then
        REGRESSED=1
        DETAILS="$DETAILS  Collection errors: $BEFORE_COLLECTION_ERRORS → $AFTER_COLLECTION_ERRORS\n"
    fi
fi

# Collection total diminuiu?
if [[ "$BEFORE_COLLECTION" != "?" && "$AFTER_COLLECTION" != "?" ]]; then
    if [[ "$AFTER_COLLECTION" -lt "$BEFORE_COLLECTION" ]]; then
        REGRESSED=1
        DIFF=$((BEFORE_COLLECTION - AFTER_COLLECTION))
        DETAILS="$DETAILS  Collection: $BEFORE_COLLECTION → $AFTER_COLLECTION (-$DIFF testes)\n"
    fi
fi

# Alembic heads mudaram?
if [[ "$BEFORE_ALEMBIC" != "?" && "$AFTER_ALEMBIC" != "?" ]]; then
    if [[ "$AFTER_ALEMBIC" -gt "$BEFORE_ALEMBIC" ]]; then
        REGRESSED=1
        DETAILS="$DETAILS  Alembic: $BEFORE_ALEMBIC → $AFTER_ALEMBIC heads\n"
    fi
fi

echo "═══════════════════════════════════════════"

if [[ $REGRESSED -eq 1 ]]; then
    echo "❌ REGRESSÃO DETECTADA:"
    echo -e "$DETAILS"
    echo ""

    # Reverter
    echo "🔄 REVERTENDO alteração..."
    REVERTED=0
    for f in "${AFFECTED_FILES[@]}"; do
        BACKUP="$BACKUP_DIR/$(basename "$f").bak"
        if [[ -f "$BACKUP" ]]; then
            cp "$BACKUP" "$f"
            REVERTED=1
        fi
    done

    if [[ $REVERTED -eq 1 ]]; then
        echo "✓ Arquivo(s) restaurado(s) do backup"
    else
        echo "⚠️  Não foi possível reverter automaticamente."
        echo "   Use: git checkout -- <arquivo>"
    fi

    echo ""
    echo "Investigue antes de tentar novamente."
    echo "Use: $SCRIPTS/pre-flight.sh <arquivo>"
    echo "═══════════════════════════════════════════"
    rm -rf "$BACKUP_DIR"
    exit 1
else
    echo "✓ SEM REGRESSÃO — Alteração aplicada com sucesso"

    # Mostrar melhorias
    if [[ "$BEFORE_RUFF" != "?" && "$AFTER_RUFF" != "?" && "$AFTER_RUFF" -lt "$BEFORE_RUFF" ]]; then
        echo "  📈 Ruff melhorou: $BEFORE_RUFF → $AFTER_RUFF (-$((BEFORE_RUFF - AFTER_RUFF)))"
    fi
    if [[ "$BEFORE_COLLECTION" != "?" && "$AFTER_COLLECTION" != "?" && "$AFTER_COLLECTION" -gt "$BEFORE_COLLECTION" ]]; then
        echo "  📈 Collection melhorou: $BEFORE_COLLECTION → $AFTER_COLLECTION (+$((AFTER_COLLECTION - BEFORE_COLLECTION)))"
    fi

    echo "═══════════════════════════════════════════"
    rm -rf "$BACKUP_DIR"
    exit 0
fi
