#!/bin/bash
# ═══════════════════════════════════════════════════════
# START_AUDITORIA.sh — Ativa o sistema COMPLETO de agentes
# Nível 1 (Monitor) + Nível 2 (Audit) + Nível 3 (Especialistas)
# Executar APENAS após concluir o trabalho nos T1-T5
# Jordan: rode este script quando estiver pronto
# ═══════════════════════════════════════════════════════

set -e

echo "🚀 ATIVANDO SISTEMA COMPLETO DE AGENTES CONECTA PRO"
echo "======================================================"

# Verificar que não está já ativo
CRON_ATIVO=$(crontab -l 2>/dev/null | grep -c "audit_orchestrator\|master_orchestrator" || true)
if [ "$CRON_ATIVO" -gt 0 ]; then
    echo "⚠️  Sistema já está ativo. Para desativar: bash agents/STOP_AUDITORIA.sh"
    exit 0
fi

# 1. Criar diretórios
mkdir -p /opt/conecta-pro/logs
mkdir -p /opt/conecta-pro/reports/auditorias
mkdir -p /opt/conecta-pro/reports/master

echo "✅ Diretórios confirmados"

# 2. Limpar crons antigos de auditoria
crontab -l 2>/dev/null \
    | grep -v "orchestrator\|auditoria\|master" \
    | crontab - 2>/dev/null || true

# 3. Adicionar ciclos
(crontab -l 2>/dev/null; cat << 'CRONBLOCK'
# Nível 1 — Monitor 30min (mantido do sistema original)
*/30 * * * * MONITOR_BOT_TOKEN=$MONITOR_BOT_TOKEN  # pragma: allowlist secret TELEGRAM_CHAT_ID=5536961034 python3 /opt/conecta-pro/agents/orchestrator_geral.py >> /opt/conecta-pro/logs/monitor.log 2>&1
# Nível 2+3 — Auditoria diária (2h da manhã)
0 2 * * * cd /opt/conecta-pro && python3 -c "import sys; sys.path.insert(0,'agents/nivel3'); sys.path.insert(0,'agents/core'); from master_orchestrator import MasterOrchestrator; MasterOrchestrator(ciclo='diario').executar()" >> /opt/conecta-pro/logs/auditoria_diaria.log 2>&1
# Nível 2+3 — Auditoria semanal completa (domingo 3h)
0 3 * * 0 cd /opt/conecta-pro && python3 -c "import sys; sys.path.insert(0,'agents/nivel3'); sys.path.insert(0,'agents/core'); from master_orchestrator import MasterOrchestrator; MasterOrchestrator(ciclo='semanal').executar()" >> /opt/conecta-pro/logs/auditoria_semanal.log 2>&1
CRONBLOCK
) | crontab -

echo "✅ Ciclos configurados:"
echo "   • Monitor: a cada 30min (Telegram)"
echo "   • Auditoria diária: 2h — Perf, Security, Coverage, Contract"
echo "   • Auditoria semanal: domingo 3h — Business + Audit completo"

# 4. Rodar primeiro ciclo imediatamente
echo ""
echo "🔍 Rodando primeiro ciclo (30min)..."
cd /opt/conecta-pro
python3 -c "
import sys, json, subprocess
sys.path.insert(0, 'agents/nivel3')
sys.path.insert(0, 'agents/core')
from master_orchestrator import MasterOrchestrator
resultado = MasterOrchestrator(ciclo='30min').executar()
scores = {k: v.get('score', 0) for k, v in resultado.items()}
print('Scores:', scores)
print('Telegram notificado ✅')
"

echo ""
echo "======================================================"
echo "✅ SISTEMA COMPLETO ATIVO"
echo "   Monitor (N1): a cada 30min"
echo "   Diário  (N2+N3): 2h — Performance, Security, Coverage"
echo "   Semanal (todos): domingo 3h — Business, Audit código"
echo "   Telegram: @conecta_pro_monitor_bot"
echo "   Para parar: bash /opt/conecta-pro/agents/STOP_AUDITORIA.sh"
echo "======================================================"
