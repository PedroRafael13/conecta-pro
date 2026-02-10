#!/bin/bash
# =============================================================================
# VERIFY-ALL.SH — Verificação Completa Conecta PRO
# =============================================================================
# OBRIGATÓRIO rodar ANTES de qualquer report de conclusão.
# Gera JSON machine-readable + output humano.
# Compara automaticamente com BASELINE.md.
#
# Uso:
#   ./scripts/verify-all.sh              # Verificação padrão
#   FULL_TEST=true ./scripts/verify-all.sh  # Com test run completo (~15min)
#
# Output:
#   stdout: relatório legível
#   .comms/verification-report.json: dados machine-readable
#   exit code: 0 = tudo OK, 1 = alguma falha
# =============================================================================

set -euo pipefail

PROJECT_ROOT="/opt/conecta-pro"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
REPORT_FILE="$PROJECT_ROOT/.comms/verification-report.json"
BASELINE_FILE="$PROJECT_ROOT/.comms/BASELINE.json"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Contadores
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

check_pass() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo -e "  ${GREEN}✓${NC} $1"
}

check_fail() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo -e "  ${RED}✗${NC} $1"
}

check_warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

separator() {
    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────${NC}"
}

# =============================================================================
echo -e "${BOLD}══════════════════════════════════════════════"
echo "  VERIFICAÇÃO COMPLETA — CONECTA PRO"
echo -e "  $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo -e "══════════════════════════════════════════════${NC}"

# =============================================================================
# 0. AMBIENTE
# =============================================================================
separator
echo -e "${BOLD}[0/9] AMBIENTE${NC}"

if [ -f /.dockerenv ]; then
    ENVIRONMENT="container"
    check_warn "Executando em container Docker"
else
    ENVIRONMENT="host"
    echo -e "  Executando no host"
fi

# Detectar e ativar venv
VENV_ACTIVATED=false
if [ -d "$BACKEND_DIR/venv" ]; then
    source "$BACKEND_DIR/venv/bin/activate" 2>/dev/null && VENV_ACTIVATED=true
elif [ -d "$BACKEND_DIR/.venv" ]; then
    source "$BACKEND_DIR/.venv/bin/activate" 2>/dev/null && VENV_ACTIVATED=true
fi

if [ "$VENV_ACTIVATED" = true ]; then
    check_pass "Virtualenv ativado ($(which python))"
else
    check_fail "Virtualenv NÃO encontrado — resultados podem ser imprecisos"
fi

# Verificar dependências críticas
DEPS_OK=true
for dep in defusedxml faker pytest ruff; do
    if python -c "import $dep" 2>/dev/null; then
        true
    else
        check_fail "Dependência faltando: $dep"
        DEPS_OK=false
    fi
done
if [ "$DEPS_OK" = true ]; then
    check_pass "Todas as dependências Python presentes"
fi

# =============================================================================
# 1. GIT STATUS
# =============================================================================
separator
echo -e "${BOLD}[1/9] GIT STATUS${NC}"
cd "$PROJECT_ROOT"

GIT_MODIFIED=$(git diff --name-only 2>/dev/null | wc -l)
GIT_STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l)
GIT_UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)
GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

echo "  Branch: $GIT_BRANCH"
echo "  Modified: $GIT_MODIFIED | Staged: $GIT_STAGED | Untracked: $GIT_UNTRACKED"

if [ "$GIT_MODIFIED" -eq 0 ] && [ "$GIT_STAGED" -eq 0 ]; then
    check_pass "Working tree limpa"
else
    check_warn "Existem mudanças não commitadas"
fi

# =============================================================================
# 2. RUFF (Python Linting)
# =============================================================================
separator
echo -e "${BOLD}[2/9] RUFF (Python Linting)${NC}"
cd "$BACKEND_DIR"

RUFF_OUTPUT=$(ruff check . 2>&1) || true
if echo "$RUFF_OUTPUT" | grep -q "All checks passed"; then
    RUFF_ERRORS=0
    check_pass "Ruff: 0 erros"
else
    RUFF_ERRORS=$(echo "$RUFF_OUTPUT" | grep -oP 'Found (\d+) error' | grep -oP '\d+' || echo "0")
    if [ "$RUFF_ERRORS" = "0" ]; then
        # Fallback: contar linhas com erros
        RUFF_ERRORS=$(echo "$RUFF_OUTPUT" | grep -cE '^\S+:\d+:\d+' || echo "0")
    fi
    RUFF_FIXABLE=$(echo "$RUFF_OUTPUT" | grep -oP '\d+(?= fixable)' || echo "0")
    check_fail "Ruff: $RUFF_ERRORS erros ($RUFF_FIXABLE fixáveis)"
    echo "$RUFF_OUTPUT" | grep -E '^\S+:\d+:\d+' | head -5
fi

# =============================================================================
# 3. PYTEST COLLECTION
# =============================================================================
separator
echo -e "${BOLD}[3/9] PYTEST COLLECTION${NC}"
cd "$BACKEND_DIR"

COLLECT_OUTPUT=$(python -m pytest --collect-only -q 2>&1) || true
COLLECTED=$(echo "$COLLECT_OUTPUT" | grep -oP '\d+(?= test)' | head -1 || echo "0")
COLLECT_ERRORS=$(echo "$COLLECT_OUTPUT" | grep -oP '\d+(?= error)' | tail -1 || echo "0")

if [ "$COLLECT_ERRORS" = "" ] || [ "$COLLECT_ERRORS" = "0" ]; then
    COLLECT_ERRORS=0
    check_pass "Collection: $COLLECTED testes, 0 erros"
else
    check_fail "Collection: $COLLECTED testes, $COLLECT_ERRORS erros"
    echo "$COLLECT_OUTPUT" | grep "^ERROR" | head -5
fi

# Contar orphaned
ORPHANED_COUNT=$(ls "$BACKEND_DIR/tests/_orphaned/" 2>/dev/null | grep -c "test_" || echo "0")
if [ "$ORPHANED_COUNT" -gt 0 ]; then
    check_warn "$ORPHANED_COUNT arquivos em _orphaned (NÃO executados)"
fi

# =============================================================================
# 4. PYTEST RUN
# =============================================================================
separator
echo -e "${BOLD}[4/9] PYTEST RUN${NC}"
cd "$BACKEND_DIR"

if [ "${FULL_TEST:-false}" = "true" ]; then
    echo "  Executando suite completa (pode demorar ~15min)..."
    TEST_OUTPUT=$(python -m pytest --tb=no -q 2>&1) || true
else
    echo "  Executando amostra rápida (use FULL_TEST=true para suite completa)..."
    TEST_OUTPUT=$(python -m pytest --tb=no -q --timeout=60 -x --ignore=tests/_integration 2>&1) || true
fi

TEST_PASSED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' || echo "0")
TEST_FAILED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= failed)' || echo "0")
TEST_ERRORS=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= error)' || echo "0")
TEST_SKIPPED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= skipped)' || echo "0")
TEST_TOTAL=$((TEST_PASSED + TEST_FAILED + TEST_ERRORS))

if [ "$TEST_TOTAL" -gt 0 ]; then
    TEST_PASS_RATE=$(echo "scale=1; $TEST_PASSED * 100 / $TEST_TOTAL" | bc 2>/dev/null || echo "?")
else
    TEST_PASS_RATE="0"
fi

echo "  Passed: $TEST_PASSED | Failed: $TEST_FAILED | Errors: $TEST_ERRORS | Skipped: $TEST_SKIPPED"
echo "  Pass rate: ${TEST_PASS_RATE}%"

if [ "$TEST_FAILED" = "0" ] && [ "$TEST_ERRORS" = "0" ]; then
    check_pass "Testes: 100% pass ($TEST_PASSED passed)"
else
    check_fail "Testes: ${TEST_PASS_RATE}% pass ($TEST_FAILED failed, $TEST_ERRORS errors)"
fi

# =============================================================================
# 5. ALEMBIC
# =============================================================================
separator
echo -e "${BOLD}[5/9] ALEMBIC${NC}"
cd "$BACKEND_DIR"

ALEMBIC_HEADS=$(alembic heads 2>&1 | grep -c "head" || echo "0")
if [ "$ALEMBIC_HEADS" -eq 1 ]; then
    check_pass "Alembic: 1 head"
else
    check_fail "Alembic: $ALEMBIC_HEADS heads (esperado: 1)"
fi

# =============================================================================
# 6. BANDIT (Security)
# =============================================================================
separator
echo -e "${BOLD}[6/9] BANDIT (Security)${NC}"
cd "$BACKEND_DIR"

if [ "${SKIP_BANDIT:-false}" = "true" ]; then
    check_warn "Bandit: PULADO (SKIP_BANDIT=true)"
    BANDIT_HIGH="skip"
    BANDIT_MEDIUM="skip"
elif command -v bandit &>/dev/null; then
    echo "  (timeout 120s)..."
    BANDIT_OUTPUT=$(timeout 120 bandit -r modules/ -ll -q --format json 2>/dev/null) || true
    BANDIT_HIGH=$(echo "$BANDIT_OUTPUT" | python -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for r in d.get('results',[]) if r['issue_severity']=='HIGH'))" 2>/dev/null || echo "?")
    BANDIT_MEDIUM=$(echo "$BANDIT_OUTPUT" | python -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for r in d.get('results',[]) if r['issue_severity']=='MEDIUM'))" 2>/dev/null || echo "?")

    if [ "$BANDIT_HIGH" = "0" ]; then
        check_pass "Bandit: 0 HIGH severity"
    else
        check_fail "Bandit: $BANDIT_HIGH HIGH severity"
    fi
    echo "  HIGH: $BANDIT_HIGH | MEDIUM: $BANDIT_MEDIUM"
else
    check_warn "Bandit não instalado"
    BANDIT_HIGH="N/A"
    BANDIT_MEDIUM="N/A"
fi

# =============================================================================
# 7. TYPESCRIPT
# =============================================================================
separator
echo -e "${BOLD}[7/9] TYPESCRIPT${NC}"
cd "$FRONTEND_DIR"

TSC_OUTPUT=$(npx tsc --noEmit 2>&1) || true
TSC_ERRORS=$(echo "$TSC_OUTPUT" | grep -c "error TS" || echo "0")

if [ "$TSC_ERRORS" -eq 0 ]; then
    check_pass "TypeScript: 0 erros"
else
    check_fail "TypeScript: $TSC_ERRORS erros"
    echo "$TSC_OUTPUT" | grep "error TS" | head -5
fi

# =============================================================================
# 8. ESLINT
# =============================================================================
separator
echo -e "${BOLD}[8/9] ESLINT${NC}"
cd "$FRONTEND_DIR"

# IMPORTANTE: usar `npx eslint .` e NÃO `next lint`
ESLINT_OUTPUT=$(npx eslint . --no-error-on-unmatched-pattern 2>&1) || true
ESLINT_SUMMARY=$(echo "$ESLINT_OUTPUT" | grep "problems" | tail -1)
ESLINT_ERRORS=$(echo "$ESLINT_SUMMARY" | grep -oP '\d+(?= error)' || echo "0")
ESLINT_WARNINGS=$(echo "$ESLINT_SUMMARY" | grep -oP '\d+(?= warning)' || echo "0")

if [ "$ESLINT_ERRORS" = "" ]; then ESLINT_ERRORS=0; fi
if [ "$ESLINT_WARNINGS" = "" ]; then ESLINT_WARNINGS=0; fi

if [ "$ESLINT_ERRORS" -eq 0 ]; then
    check_pass "ESLint: 0 erros ($ESLINT_WARNINGS warnings)"
else
    check_fail "ESLint: $ESLINT_ERRORS erros ($ESLINT_WARNINGS warnings)"
    echo "$ESLINT_OUTPUT" | grep "error " | grep -v "warning" | head -5
fi

# =============================================================================
# 9. COMPARAÇÃO COM BASELINE
# =============================================================================
separator
echo -e "${BOLD}[9/9] COMPARAÇÃO COM BASELINE${NC}"

REGRESSIONS=0
if [ -f "$BASELINE_FILE" ]; then
    B_RUFF=$(python -c "import json; print(json.load(open('$BASELINE_FILE'))['backend']['ruff_errors'])" 2>/dev/null || echo "?")
    B_COLLECT=$(python -c "import json; print(json.load(open('$BASELINE_FILE'))['backend']['collection_errors'])" 2>/dev/null || echo "?")
    B_TSC=$(python -c "import json; print(json.load(open('$BASELINE_FILE'))['frontend']['tsc_errors'])" 2>/dev/null || echo "?")
    B_ESLINT=$(python -c "import json; print(json.load(open('$BASELINE_FILE'))['frontend']['eslint_errors'])" 2>/dev/null || echo "?")
    B_PASSED=$(python -c "import json; print(json.load(open('$BASELINE_FILE'))['backend']['tests_passed'])" 2>/dev/null || echo "?")
    B_FAILED=$(python -c "import json; print(json.load(open('$BASELINE_FILE'))['backend']['tests_failed'])" 2>/dev/null || echo "?")

    echo "  Métrica          | Baseline | Atual    | Delta"
    echo "  ─────────────────┼──────────┼──────────┼──────"

    compare() {
        local name="$1" base="$2" curr="$3" direction="$4"
        if [ "$base" = "?" ] || [ "$curr" = "?" ]; then
            printf "  %-17s | %-8s | %-8s | ?\n" "$name" "$base" "$curr"
            return
        fi
        local delta=$((curr - base))
        local sign=""
        local color="$NC"
        if [ "$delta" -gt 0 ]; then sign="+"; fi

        # direction: "lower_is_better" or "higher_is_better"
        if [ "$direction" = "lower_is_better" ]; then
            if [ "$delta" -gt 0 ]; then color="$RED"; REGRESSIONS=$((REGRESSIONS+1)); fi
            if [ "$delta" -lt 0 ]; then color="$GREEN"; fi
        else
            if [ "$delta" -lt 0 ]; then color="$RED"; REGRESSIONS=$((REGRESSIONS+1)); fi
            if [ "$delta" -gt 0 ]; then color="$GREEN"; fi
        fi
        printf "  %-17s | %-8s | %-8s | ${color}%s${NC}\n" "$name" "$base" "$curr" "${sign}${delta}"
    }

    compare "Ruff errors"       "$B_RUFF"    "$RUFF_ERRORS"    "lower_is_better"
    compare "Collection errors" "$B_COLLECT"  "$COLLECT_ERRORS" "lower_is_better"
    compare "Tests passed"      "$B_PASSED"   "$TEST_PASSED"    "higher_is_better"
    compare "Tests failed"      "$B_FAILED"   "$TEST_FAILED"    "lower_is_better"
    compare "TSC errors"        "$B_TSC"      "$TSC_ERRORS"     "lower_is_better"
    compare "ESLint errors"     "$B_ESLINT"   "$ESLINT_ERRORS"  "lower_is_better"

    echo ""
    if [ "$REGRESSIONS" -gt 0 ]; then
        check_fail "REGRESSÕES DETECTADAS: $REGRESSIONS métricas pioraram!"
        echo ""
        echo -e "  ${RED}${BOLD}⚠ AÇÃO OBRIGATÓRIA: Investigar regressões antes de reportar conclusão${NC}"
    else
        check_pass "Nenhuma regressão detectada"
    fi
else
    check_warn "Baseline não encontrado: $BASELINE_FILE"
    echo "  Execute: ./scripts/update-baseline.sh para criar"
fi

# =============================================================================
# RESUMO FINAL
# =============================================================================
separator
echo ""
echo -e "${BOLD}══════════════════════════════════════════════"
echo "  RESUMO FINAL"
echo -e "══════════════════════════════════════════════${NC}"
echo ""
echo "  Checks: $PASSED_CHECKS/$TOTAL_CHECKS passed | $FAILED_CHECKS failed"
echo "  Regressões: $REGRESSIONS"
echo ""
echo "  Backend:"
echo "    Ruff:       $RUFF_ERRORS erros"
echo "    Collection: $COLLECTED coletados, $COLLECT_ERRORS erros"
echo "    Tests:      $TEST_PASSED passed, $TEST_FAILED failed, $TEST_ERRORS errors (${TEST_PASS_RATE}%)"
echo "    Alembic:    $ALEMBIC_HEADS head(s)"
echo "    Bandit:     HIGH=$BANDIT_HIGH MEDIUM=$BANDIT_MEDIUM"
echo "    Orphaned:   $ORPHANED_COUNT arquivos"
echo ""
echo "  Frontend:"
echo "    TypeScript: $TSC_ERRORS erros"
echo "    ESLint:     $ESLINT_ERRORS erros, $ESLINT_WARNINGS warnings"
echo ""

# Salvar relatório JSON
cat > "$REPORT_FILE" << ENDJSON
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "$ENVIRONMENT",
  "venv_activated": $VENV_ACTIVATED,
  "overall": {
    "status": "$([ $FAILED_CHECKS -eq 0 ] && echo 'pass' || echo 'fail')",
    "checks_passed": $PASSED_CHECKS,
    "checks_failed": $FAILED_CHECKS,
    "regressions": $REGRESSIONS
  },
  "git": {
    "branch": "$GIT_BRANCH",
    "modified": $GIT_MODIFIED,
    "staged": $GIT_STAGED,
    "untracked": $GIT_UNTRACKED
  },
  "backend": {
    "ruff_errors": $RUFF_ERRORS,
    "collection_total": ${COLLECTED:-0},
    "collection_errors": ${COLLECT_ERRORS:-0},
    "tests_passed": ${TEST_PASSED:-0},
    "tests_failed": ${TEST_FAILED:-0},
    "tests_errors": ${TEST_ERRORS:-0},
    "tests_skipped": ${TEST_SKIPPED:-0},
    "test_pass_rate": "${TEST_PASS_RATE}",
    "alembic_heads": $ALEMBIC_HEADS,
    "bandit_high": "${BANDIT_HIGH}",
    "bandit_medium": "${BANDIT_MEDIUM}",
    "orphaned_count": $ORPHANED_COUNT
  },
  "frontend": {
    "tsc_errors": $TSC_ERRORS,
    "eslint_errors": $ESLINT_ERRORS,
    "eslint_warnings": $ESLINT_WARNINGS
  }
}
ENDJSON

echo "  Relatório: $REPORT_FILE"
echo ""

if [ $FAILED_CHECKS -gt 0 ] || [ $REGRESSIONS -gt 0 ]; then
    echo -e "${RED}${BOLD}  ✗ VERIFICAÇÃO FALHOU — NÃO reporte conclusão sem resolver${NC}"
    exit 1
else
    echo -e "${GREEN}${BOLD}  ✓ TODAS AS VERIFICAÇÕES PASSARAM${NC}"
    exit 0
fi
