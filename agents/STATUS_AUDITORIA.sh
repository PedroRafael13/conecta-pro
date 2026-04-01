#!/bin/bash
# Verifica status do sistema de auditoria

echo "📊 STATUS — SISTEMA DE AUDITORIA CONECTA PRO"
echo "=============================================="

# Verificar cron
CRON_ATIVO=$(crontab -l 2>/dev/null | grep -c "audit_orchestrator" || true)
if [ "$CRON_ATIVO" -gt 0 ]; then
    echo "🟢 Cron: ATIVO (ciclo semanal domingo 3h)"
else
    echo "🟡 Cron: STANDBY (não agendado)"
fi

echo ""

# Verificar arquivos core
echo "Arquivos core:"
for f in agents/core/code_reader.py \
          agents/core/code_fixer.py \
          agents/core/audit_orchestrator.py; do
    if [ -f "/opt/conecta-pro/$f" ]; then
        LINHAS=$(wc -l < "/opt/conecta-pro/$f")
        echo "  ✅ $f ($LINHAS linhas)"
    else
        echo "  ❌ $f — AUSENTE"
    fi
done

echo ""

# Último relatório de auditoria
ULTIMO=$(ls -t /opt/conecta-pro/reports/auditorias/*.json 2>/dev/null | head -1)
if [ -n "$ULTIMO" ]; then
    echo "Último ciclo executado:"
    python3 -c "
import json
with open('$ULTIMO') as f: r = json.load(f)
print(f'  Data:      {r[\"timestamp\"][:16]}')
print(f'  Bugs:      {r[\"total_bugs\"]} encontrados')
print(f'  Corrigidos:{r[\"total_corrigidos\"]} auto')
taxa = r['total_corrigidos'] / max(r['total_bugs'], 1) * 100
print(f'  Taxa:      {taxa:.1f}%')
" 2>/dev/null || echo "  (erro ao ler relatório)"
else
    echo "Nenhum ciclo executado ainda"
fi

echo ""
echo "=============================================="
if [ "$CRON_ATIVO" -gt 0 ]; then
    echo "STATUS: 🟢 ATIVO"
    echo ""
    echo "Para pausar: bash /opt/conecta-pro/agents/STOP_AUDITORIA.sh"
else
    echo "STATUS: 🟡 STANDBY"
    echo ""
    echo "Para ativar: bash /opt/conecta-pro/agents/START_AUDITORIA.sh"
fi
