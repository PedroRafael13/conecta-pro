#!/bin/bash
# =============================================================================
# VERIFY-QUICK.SH — Verificação rápida (~30s) sem Bandit e sem test run
# =============================================================================
# Para verificações durante desenvolvimento. Checa:
#   - Ruff, Collection, Alembic, TypeScript, ESLint
# NÃO checa: Bandit (lento), pytest run (lento)
#
# Uso: ./scripts/verify-quick.sh
# =============================================================================

SKIP_BANDIT=true FULL_TEST=false /opt/conecta-pro/scripts/verify-all.sh
