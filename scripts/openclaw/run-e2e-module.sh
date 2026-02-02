#!/bin/bash
# Script para executar testes E2E de módulos específicos
# Uso: ./run-e2e-module.sh <modulo>

MODULE=$1

if [ -z "$MODULE" ]; then
    echo "Erro: módulo não especificado"
    exit 1
fi

cd /opt/conecta-pro/frontend
npm run test:e2e:$MODULE
