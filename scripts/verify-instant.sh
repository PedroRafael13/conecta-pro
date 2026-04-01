#!/bin/bash
# =============================================================================
# VERIFY-INSTANT.SH — Verificação rápida (~45s)
# =============================================================================
# Checa apenas: Ruff, Pytest Collection, Alembic heads
# NÃO checa: test run, bandit, TypeScript, ESLint
#
# Uso: ./scripts/verify-instant.sh
#      verify-instant  (alias)
# =============================================================================

set -euo pipefail

BACKEND="/opt/conecta-pro/backend"
VENV="$BACKEND/venv/bin/activate"
TOTAL_START=$(date +%s%N)
ERRORS=0

echo "═══════════════════════════════════════════"
echo "VERIFY-INSTANT (~8s)"
echo "═══════════════════════════════════════════"
echo ""

# Ativar venv
source "$VENV" 2>/dev/null || { echo "❌ Falha ao ativar venv"; exit 1; }
cd "$BACKEND"

# --- 1. Ruff ---
STEP_START=$(date +%s%N)
RUFF_OUTPUT=$(ruff check . --select F401,F841,F821 2>&1 || true)
RUFF_ERRORS=$(echo "$RUFF_OUTPUT" | grep -c "^[^F]*F[0-9]" 2>/dev/null || echo "0")
if echo "$RUFF_OUTPUT" | grep -q "All checks passed"; then
    RUFF_ERRORS=0
fi
STEP_END=$(date +%s%N)
STEP_TIME=$(echo "scale=1; ($STEP_END - $STEP_START) / 1000000000" | bc 2>/dev/null || echo "?")

if [[ "$RUFF_ERRORS" == "0" ]]; then
    echo "✓ Ruff: 0 erros (${STEP_TIME}s)"
else
    echo "✗ Ruff: $RUFF_ERRORS erros (${STEP_TIME}s)"
    ERRORS=$((ERRORS + 1))
fi

# --- 2. Pytest Collection ---
STEP_START=$(date +%s%N)
COLLECTION_OUTPUT=$(python -m pytest --collect-only -q 2>&1 || true)
COLLECTION_TOTAL=$(echo "$COLLECTION_OUTPUT" | grep -oP '\d+(?= tests? collected)' | head -1 || echo "0")
COLLECTION_ERRORS=$(echo "$COLLECTION_OUTPUT" | grep -oP '\d+(?= errors?)' | head -1 || echo "0")
if [[ -z "$COLLECTION_TOTAL" || "$COLLECTION_TOTAL" == "" ]]; then
    COLLECTION_TOTAL=0
fi
if [[ -z "$COLLECTION_ERRORS" || "$COLLECTION_ERRORS" == "" ]]; then
    COLLECTION_ERRORS=0
fi
STEP_END=$(date +%s%N)
STEP_TIME=$(echo "scale=1; ($STEP_END - $STEP_START) / 1000000000" | bc 2>/dev/null || echo "?")

if [[ "$COLLECTION_ERRORS" == "0" ]]; then
    echo "✓ Collection: $COLLECTION_TOTAL testes, 0 erros (${STEP_TIME}s)"
else
    echo "✗ Collection: $COLLECTION_TOTAL testes, $COLLECTION_ERRORS erros (${STEP_TIME}s)"
    ERRORS=$((ERRORS + 1))
fi

# --- 3. Alembic Heads ---
STEP_START=$(date +%s%N)
ALEMBIC_HEADS=$(alembic heads 2>&1 | grep -c "(head)" || echo "0")
STEP_END=$(date +%s%N)
STEP_TIME=$(echo "scale=1; ($STEP_END - $STEP_START) / 1000000000" | bc 2>/dev/null || echo "?")

if [[ "$ALEMBIC_HEADS" == "1" ]]; then
    echo "✓ Alembic: 1 head (${STEP_TIME}s)"
else
    echo "✗ Alembic: $ALEMBIC_HEADS heads (${STEP_TIME}s)"
    ERRORS=$((ERRORS + 1))
fi

# --- Total ---
TOTAL_END=$(date +%s%N)
TOTAL_TIME=$(echo "scale=1; ($TOTAL_END - $TOTAL_START) / 1000000000" | bc 2>/dev/null || echo "?")

echo ""
echo "═══════════════════════════════════════════"
if [[ $ERRORS -eq 0 ]]; then
    echo "✓ TUDO OK — Total: ${TOTAL_TIME}s"
else
    echo "✗ $ERRORS PROBLEMAS — Total: ${TOTAL_TIME}s"
fi
echo "═══════════════════════════════════════════"

exit $ERRORS
