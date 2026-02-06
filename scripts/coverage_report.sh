#!/bin/bash
# Script de cobertura de testes - Conecta PRO
set -e

cd /opt/conecta-pro/backend
source venv/bin/activate

echo "=== Rodando testes com cobertura ==="
python -m pytest tests/ \
  --cov=modules --cov=core --cov=api \
  --cov-config=.coveragerc \
  --cov-report=term-missing \
  --cov-report=html:../reports/coverage_html \
  --cov-report=json:../reports/coverage.json \
  --cov-report=xml:../reports/coverage.xml \
  --timeout=120 \
  -q 2>&1 | tee ../reports/coverage_$(date +%Y%m%d).log

echo ""
echo "=== Relatorios gerados ==="
echo "  HTML: /opt/conecta-pro/reports/coverage_html/index.html"
echo "  JSON: /opt/conecta-pro/reports/coverage.json"
echo "  XML:  /opt/conecta-pro/reports/coverage.xml"
echo "  Log:  /opt/conecta-pro/reports/coverage_$(date +%Y%m%d).log"
