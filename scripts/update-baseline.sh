#!/bin/bash
# =============================================================================
# UPDATE-BASELINE.SH — Captura estado atual como baseline
# =============================================================================
# Roda verify-all.sh e salva o resultado como BASELINE.json
# O Kimi deve comparar contra esse baseline antes de reportar progresso.
#
# Uso: ./scripts/update-baseline.sh
# =============================================================================

set -euo pipefail

PROJECT_ROOT="/opt/conecta-pro"
REPORT_FILE="$PROJECT_ROOT/.comms/verification-report.json"
BASELINE_FILE="$PROJECT_ROOT/.comms/BASELINE.json"

echo "Capturando baseline atual..."
echo ""

# Rodar verificação completa
FULL_TEST=true "$PROJECT_ROOT/scripts/verify-all.sh" || true

echo ""
echo "─────────────────────────────────────────────"

# Copiar report como baseline
if [ -f "$REPORT_FILE" ]; then
    cp "$REPORT_FILE" "$BASELINE_FILE"
    echo "✓ Baseline salvo em: $BASELINE_FILE"
    echo ""
    echo "Conteúdo:"
    python3 -m json.tool "$BASELINE_FILE" 2>/dev/null || cat "$BASELINE_FILE"
else
    echo "✗ Erro: relatório não gerado"
    exit 1
fi
