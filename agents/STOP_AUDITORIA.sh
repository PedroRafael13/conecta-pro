#!/bin/bash
# ═══════════════════════════════════════════════════════
# STOP_AUDITORIA.sh — Pausa o ciclo automático de auditoria
# O código permanece intacto; só suspende o cron
# ═══════════════════════════════════════════════════════

echo "⏸  PAUSANDO SISTEMA DE AUDITORIA"
echo "=============================================="

crontab -l 2>/dev/null | grep -v "audit_orchestrator" | crontab -

echo "✅ Cron de auditoria removido (sistema em STANDBY)"
echo "   Para reativar: bash agents/START_AUDITORIA.sh"
echo "=============================================="
