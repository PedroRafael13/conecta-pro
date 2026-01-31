#!/bin/bash

echo "# AUDITORIA DE SERVICES MANUAIS"
echo ""
echo "Data: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Estatísticas gerais
TOTAL_SERVICES=$(find src/services -type f \( -name "*.service.ts" -o -name "*Service.ts" \) ! -name "*.test.ts" | wc -l)
TOTAL_FILES=$(find src/services -type f -name "*.ts" ! -name "*.test.ts" | wc -l)
TOTAL_ORVAL=$(ls -1 src/types/generated/ 2>/dev/null | wc -l)

echo "## Estatísticas"
echo "- Total de arquivos em src/services: $TOTAL_FILES"
echo "- Total de services (.service.ts): $TOTAL_SERVICES"
echo "- Total de módulos Orval: $TOTAL_ORVAL"
echo ""

echo "## Módulos Orval Disponíveis"
echo ""
for module in $(ls -1 src/types/generated/); do
  if [ -d "src/types/generated/$module" ]; then
    HOOKS_COUNT=$(find "src/types/generated/$module" -name "*.ts" 2>/dev/null | wc -l)
    echo "- **$module**: $HOOKS_COUNT arquivos"
  else
    echo "- **$module**: arquivo único"
  fi
done
echo ""

echo "## Mapeamento por Módulo"
echo ""

# Agrupar services por diretório
for dir in $(find src/services -type d -mindepth 1 -maxdepth 1 | sort); do
  MODULE=$(basename "$dir")
  echo "### Módulo: $MODULE"
  echo ""

  # Contar arquivos
  SERVICE_FILES=$(find "$dir" -name "*.service.ts" -o -name "*Service.ts" | wc -l)
  TOTAL_MODULE_FILES=$(find "$dir" -name "*.ts" ! -name "*.test.ts" | wc -l)

  echo "- **Arquivos totais**: $TOTAL_MODULE_FILES"
  echo "- **Services**: $SERVICE_FILES"

  # Verificar se existe módulo Orval equivalente
  if [ -d "src/types/generated/$MODULE" ] || [ -f "src/types/generated/$MODULE.ts" ]; then
    echo "- **Orval**: ✅ Disponível"
  else
    echo "- **Orval**: ❌ Não disponível"
  fi

  # Listar arquivos do módulo
  echo "- **Arquivos**:"
  find "$dir" -name "*.ts" ! -name "*.test.ts" -type f | while read file; do
    FUNCS=$(grep -c -E "export\s+(const|function|class)" "$file" 2>/dev/null || echo "0")
    echo "  - $(basename $file): $FUNCS exports"
  done

  echo ""
done

echo "## Análise de Uso"
echo ""
echo "Buscando imports de services no código..."
echo ""

# Encontrar services mais usados
for service in $(find src/services -name "*.service.ts" -o -name "*Service.ts" | sort); do
  SERVICE_NAME=$(basename "$service" .ts)
  MODULE_NAME=$(dirname "$service" | xargs basename)

  # Contar imports deste service
  USAGE_COUNT=$(grep -r "from.*services/$MODULE_NAME.*$SERVICE_NAME" src/app src/components src/features 2>/dev/null | wc -l)

  if [ "$USAGE_COUNT" -gt 0 ]; then
    echo "- **$MODULE_NAME/$SERVICE_NAME**: $USAGE_COUNT imports"
  fi
done

echo ""
echo "## Análise Completa"
