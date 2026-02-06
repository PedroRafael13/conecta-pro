#!/bin/bash
# Script para executar todas as correções automáticas em sequência

cd /opt/conecta-pro/frontend

echo "================================================================"
echo "INICIANDO CORREÇÃO AUTOMÁTICA DE ERROS TYPESCRIPT"
echo "================================================================"
echo ""

echo "Rodando correção inicial..."
npm run type-check 2>&1 | grep "error TS" | wc -l

echo ""
echo "1. Corrigindo erros TS2551 (nomes de métodos incorretos)..."
python3 fix_ts2551_errors.py 2>&1 | tail -5

echo ""
echo "2. Corrigindo erros TS2724 (tipos incorretos com sugestão)..."
python3 fix_ts2724_errors.py 2>&1 | tail -5

echo ""
echo "3. Comentando tipos que não existem (TS2305)..."
python3 fix_missing_types.py 2>&1 | tail -5

echo ""
echo "================================================================"
echo "CONTAGEM FINAL DE ERROS"
echo "================================================================"
npm run type-check 2>&1 | grep "error TS" | wc -l

echo ""
echo "================================================================"
echo "DISTRIBUIÇÃO DE ERROS RESTANTES"
echo "================================================================"
npm run type-check 2>&1 | grep "error TS" | sed 's/.*error TS\([0-9]*\):.*/TS\1/' | sort | uniq -c | sort -nr | head -15

echo ""
echo "Correção automática concluída!"
