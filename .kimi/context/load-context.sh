#!/bin/bash
# Script para carregar contexto Kimi em nova sessão

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     KIMI K2.5 - CONTEXT LOADER                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ -f "/opt/conecta-pro/.kimi/context/KIMI_CONTEXT.md" ]; then
    echo "📂 Carregando contexto..."
    echo ""
    cat /opt/conecta-pro/.kimi/context/KIMI_CONTEXT.md
else
    echo "❌ Contexto não encontrado!"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     STATUS DO PROJETO                                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar containers
echo "🐳 Containers:"
docker ps --filter "name=conecta" --format "  {{.Names}}: {{.Status}}" 2>/dev/null || echo "  Docker não disponível"

echo ""
echo "📦 Módulos Backend: $(ls /opt/conecta-pro/backend/modules/ 2>/dev/null | wc -l)"
echo "📦 Módulos Frontend: $(ls /opt/conecta-pro/frontend/src/app/modulos/ 2>/dev/null | wc -l)"

echo ""
echo "✅ Contexto carregado! Pronto para trabalhar."
