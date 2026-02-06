#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# CONECTA MAIS - SISTEMA DE AUDITORIA CUSTOMIZADO
# Auditoria específica para os 21 módulos do ERP Conecta Mais
# Meta: 10.00/10 em todos os módulos
# ═══════════════════════════════════════════════════════════════════════════

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DOS MÓDULOS
# ═══════════════════════════════════════════════════════════════════════════

# 21 Módulos do Conecta Mais
MODULES=(
    "core:26:9.64:CORE"
    "crm:32:9.73:CRM"
    "operations:33:9.68:OPERACOES"
    "facilities:29:9.95:OPERACOES"
    "equipment_management:27:9.60:OPERACOES"
    "occurrences:27:9.78:OPERACOES"
    "ged:36:9.87:OPERACOES"
    "recruitment:33:9.68:RH"
    "residents:33:9.64:RH"
    "visitors:27:9.94:RH"
    "hr:167:9.65:RH"
    "financial:137:9.60:FINANCEIRO"
    "document_kits:12:10.00:SERVICOS"
    "diarists:12:10.00:SERVICOS"
    "clients:16:9.98:GESTAO"
    "services:16:9.97:GESTAO"
    "integrations:16:10.00:GESTAO"
    "audit:15:10.00:GESTAO"
    "reports:15:10.00:GESTAO"
    "config:15:10.00:GESTAO"
    "field_service:30:9.52:CAMPO"
)

# Configurações
PROJECT_ROOT="${1:-/opt/erp-conecta-mais}"
MODULE_FILTER="${2:-all}"
REPORT_DIR="$PROJECT_ROOT/docs/quality-reports"

# Criar diretório de reports
mkdir -p "$REPORT_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

print_header() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $1${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
}

print_module_header() {
    echo -e "\n${MAGENTA}▶ MÓDULO: $1${NC}"
    echo -e "${MAGENTA}  Score Atual: $2 | Arquivos: $3 | Categoria: $4${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════
# AUDITORIA POR MÓDULO
# ═══════════════════════════════════════════════════════════════════════════

audit_module() {
    local module_name=$1
    local files_count=$2
    local current_score=$3
    local category=$4
    
    print_module_header "$module_name" "$current_score" "$files_count" "$category"
    
    local module_path="$PROJECT_ROOT/backend/modules/$module_name"
    
    # Verificar se módulo existe
    if [ ! -d "$module_path" ]; then
        if [ "$module_name" == "core" ]; then
            module_path="$PROJECT_ROOT/backend/core"
        fi
        
        if [ ! -d "$module_path" ]; then
            print_error "Módulo não encontrado: $module_path"
            return 1
        fi
    fi
    
    # Executar Pylint
    echo -e "${BLUE}  ├─ Executando Pylint...${NC}"
    
    local pylint_output
    pylint_output=$(pylint "$module_path" --recursive=y \
        --output-format=text \
        --score=yes \
        --reports=no \
        2>&1 || true)
    
    # Salvar output completo
    echo "$pylint_output" > "$REPORT_DIR/${module_name}_pylint.txt"
    
    # Extrair score
    local new_score
    new_score=$(echo "$pylint_output" | grep -oP 'rated at \K[0-9.]+' || echo "0.00")
    
    # Contar issues por tipo
    local unused_arg
    local too_many_locals
    local singleton_comp
    local unused_import
    local line_too_long
    local import_outside
    local todo_fixme
    
    unused_arg=$(echo "$pylint_output" | grep -c "unused-argument" || echo "0")
    too_many_locals=$(echo "$pylint_output" | grep -c "too-many-locals\|too-many-branches" || echo "0")
    singleton_comp=$(echo "$pylint_output" | grep -c "singleton-comparison" || echo "0")
    unused_import=$(echo "$pylint_output" | grep -c "unused-import" || echo "0")
    line_too_long=$(echo "$pylint_output" | grep -c "line-too-long" || echo "0")
    import_outside=$(echo "$pylint_output" | grep -c "import-outside-toplevel" || echo "0")
    todo_fixme=$(echo "$pylint_output" | grep -c "fixme" || echo "0")
    
    local total_issues=$((unused_arg + too_many_locals + singleton_comp + unused_import + line_too_long + import_outside + todo_fixme))
    
    # Exibir resultados
    echo -e "${BLUE}  ├─ Score: $new_score/10${NC}"
    
    if (( $(echo "$new_score >= 10.00" | bc -l) )); then
        print_success "  └─ PERFEITO! 10.00/10 ✨"
    elif (( $(echo "$new_score >= 9.90" | bc -l) )); then
        print_warning "  └─ Muito bom! Faltam $(echo "10.00 - $new_score" | bc) pontos para 10.00"
    elif (( $(echo "$new_score >= 9.70" | bc -l) )); then
        print_warning "  └─ Bom. Faltam $(echo "10.00 - $new_score" | bc) pontos para 10.00"
    else
        print_error "  └─ Precisa melhorar! Faltam $(echo "10.00 - $new_score" | bc) pontos"
    fi
    
    # Exibir breakdown de issues
    if [ "$total_issues" -gt 0 ]; then
        echo -e "${YELLOW}  Issues encontrados ($total_issues total):${NC}"
        [ "$unused_arg" -gt 0 ] && echo -e "    - unused-argument: $unused_arg"
        [ "$too_many_locals" -gt 0 ] && echo -e "    - too-many-locals/branches: $too_many_locals"
        [ "$singleton_comp" -gt 0 ] && echo -e "    - singleton-comparison: $singleton_comp"
        [ "$unused_import" -gt 0 ] && echo -e "    - unused-import: $unused_import"
        [ "$line_too_long" -gt 0 ] && echo -e "    - line-too-long: $line_too_long"
        [ "$import_outside" -gt 0 ] && echo -e "    - import-outside-toplevel: $import_outside"
        [ "$todo_fixme" -gt 0 ] && echo -e "    - TODO/FIXME: $todo_fixme"
    fi
    
    # Gerar relatório JSON
    cat > "$REPORT_DIR/${module_name}_report.json" <<EOF
{
  "module": "$module_name",
  "category": "$category",
  "files_count": $files_count,
  "score_previous": $current_score,
  "score_current": $new_score,
  "gap_to_perfect": $(echo "10.00 - $new_score" | bc),
  "total_issues": $total_issues,
  "issues_breakdown": {
    "unused_argument": $unused_arg,
    "too_many_locals_branches": $too_many_locals,
    "singleton_comparison": $singleton_comp,
    "unused_import": $unused_import,
    "line_too_long": $line_too_long,
    "import_outside_toplevel": $import_outside,
    "todo_fixme": $todo_fixme
  },
  "timestamp": "$(date -Iseconds)"
}
EOF
    
    echo "$new_score"
}

# ═══════════════════════════════════════════════════════════════════════════
# AUDITORIA COMPLETA
# ═══════════════════════════════════════════════════════════════════════════

run_full_audit() {
    print_header "AUDITORIA COMPLETA - ERP CONECTA MAIS"
    
    echo -e "${BLUE}Projeto: $PROJECT_ROOT${NC}"
    echo -e "${BLUE}Total de Módulos: ${#MODULES[@]}${NC}"
    echo -e "${BLUE}Meta: 10.00/10 em TODOS os módulos${NC}\n"
    
    local total_score=0
    local modules_count=0
    local modules_perfect=0
    local modules_very_good=0
    local modules_good=0
    local modules_improve=0
    
    # Arrays para tracking
    declare -a perfect_modules=()
    declare -a very_good_modules=()
    declare -a good_modules=()
    declare -a improve_modules=()
    
    # Auditar cada módulo
    for module_info in "${MODULES[@]}"; do
        IFS=':' read -r module files score category <<< "$module_info"
        
        # Filtrar por módulo se especificado
        if [ "$MODULE_FILTER" != "all" ] && [ "$MODULE_FILTER" != "$module" ]; then
            continue
        fi
        
        local new_score
        new_score=$(audit_module "$module" "$files" "$score" "$category")
        
        total_score=$(echo "$total_score + $new_score" | bc)
        modules_count=$((modules_count + 1))
        
        # Categorizar
        if (( $(echo "$new_score >= 10.00" | bc -l) )); then
            modules_perfect=$((modules_perfect + 1))
            perfect_modules+=("$module:$new_score")
        elif (( $(echo "$new_score >= 9.90" | bc -l) )); then
            modules_very_good=$((modules_very_good + 1))
            very_good_modules+=("$module:$new_score")
        elif (( $(echo "$new_score >= 9.70" | bc -l) )); then
            modules_good=$((modules_good + 1))
            good_modules+=("$module:$new_score")
        else
            modules_improve=$((modules_improve + 1))
            improve_modules+=("$module:$new_score")
        fi
    done
    
    # Calcular média
    local avg_score
    avg_score=$(echo "scale=2; $total_score / $modules_count" | bc)
    
    # Gerar relatório final
    print_header "RESULTADO FINAL"
    
    echo -e "${CYAN}Média Geral: $avg_score/10.00${NC}"
    echo -e "${CYAN}Módulos Auditados: $modules_count${NC}\n"
    
    echo -e "${GREEN}✅ Perfeito (10.00):      $modules_perfect módulos ($(echo "scale=1; $modules_perfect * 100 / $modules_count" | bc)%)${NC}"
    for mod in "${perfect_modules[@]}"; do
        IFS=':' read -r name score <<< "$mod"
        echo -e "   - $name: $score"
    done
    
    echo -e "\n${YELLOW}⚡ Muito Bom (9.90-9.99): $modules_very_good módulos ($(echo "scale=1; $modules_very_good * 100 / $modules_count" | bc)%)${NC}"
    for mod in "${very_good_modules[@]}"; do
        IFS=':' read -r name score <<< "$mod"
        echo -e "   - $name: $score"
    done
    
    echo -e "\n${BLUE}🔧 Bom (9.70-9.89):      $modules_good módulos ($(echo "scale=1; $modules_good * 100 / $modules_count" | bc)%)${NC}"
    for mod in "${good_modules[@]}"; do
        IFS=':' read -r name score <<< "$mod"
        echo -e "   - $name: $score"
    done
    
    echo -e "\n${RED}🔴 Melhorar (<9.70):     $modules_improve módulos ($(echo "scale=1; $modules_improve * 100 / $modules_count" | bc)%)${NC}"
    for mod in "${improve_modules[@]}"; do
        IFS=':' read -r name score <<< "$mod"
        gap=$(echo "10.00 - $score" | bc)
        echo -e "   - $name: $score (gap: $gap)"
    done
    
    # Gerar relatório consolidado
    cat > "$REPORT_DIR/AUDIT_SUMMARY.json" <<EOF
{
  "project": "ERP Conecta Mais",
  "timestamp": "$(date -Iseconds)",
  "modules_total": $modules_count,
  "average_score": $avg_score,
  "target_score": 10.00,
  "gap_to_target": $(echo "10.00 - $avg_score" | bc),
  "distribution": {
    "perfect": {
      "count": $modules_perfect,
      "percentage": $(echo "scale=1; $modules_perfect * 100 / $modules_count" | bc)
    },
    "very_good": {
      "count": $modules_very_good,
      "percentage": $(echo "scale=1; $modules_very_good * 100 / $modules_count" | bc)
    },
    "good": {
      "count": $modules_good,
      "percentage": $(echo "scale=1; $modules_good * 100 / $modules_count" | bc)
    },
    "improve": {
      "count": $modules_improve,
      "percentage": $(echo "scale=1; $modules_improve * 100 / $modules_count" | bc)
    }
  }
}
EOF
    
    echo -e "\n${GREEN}✓ Relatórios salvos em: $REPORT_DIR/${NC}"
    
    # Determinar status
    if [ "$modules_perfect" -eq "$modules_count" ]; then
        echo -e "\n${GREEN}🏆 EXCELÊNCIA ATINGIDA! Todos os módulos em 10.00/10!${NC}"
        return 0
    else
        echo -e "\n${YELLOW}📊 Progresso: $modules_perfect/$modules_count módulos perfeitos${NC}"
        echo -e "${YELLOW}🎯 Meta: $(echo "$modules_count - $modules_perfect" | bc) módulos restantes para 100%${NC}"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# AUDITORIA POR SPRINT DE QUALIDADE
# ═══════════════════════════════════════════════════════════════════════════

audit_sprint_q1() {
    echo -e "${CYAN}Sprint Q1: Wins Rápidos${NC}"
    echo -e "Módulos: clients, services, facilities, visitors\n"
    
    audit_module "clients" "16" "9.98" "GESTAO"
    audit_module "services" "16" "9.97" "GESTAO"
    audit_module "facilities" "29" "9.95" "OPERACOES"
    audit_module "visitors" "27" "9.94" "RH"
}

audit_sprint_q2() {
    echo -e "${CYAN}Sprint Q2: Intermediários${NC}"
    echo -e "Módulos: ged, occurrences, crm, operations\n"
    
    audit_module "ged" "36" "9.87" "OPERACOES"
    audit_module "occurrences" "27" "9.78" "OPERACOES"
    audit_module "crm" "32" "9.73" "CRM"
    audit_module "operations" "33" "9.68" "OPERACOES"
}

audit_sprint_q3() {
    echo -e "${CYAN}Sprint Q3: Complexos${NC}"
    echo -e "Módulos: recruitment, hr, core, residents, financial\n"
    
    audit_module "recruitment" "33" "9.68" "RH"
    audit_module "hr" "167" "9.65" "RH"
    audit_module "core" "26" "9.64" "CORE"
    audit_module "residents" "33" "9.64" "RH"
    audit_module "financial" "137" "9.60" "FINANCEIRO"
}

audit_sprint_q4() {
    echo -e "${CYAN}Sprint Q4: Críticos${NC}"
    echo -e "Módulos: equipment_management, field_service\n"
    
    audit_module "equipment_management" "27" "9.60" "OPERACOES"
    audit_module "field_service" "30" "9.52" "CAMPO"
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

main() {
    case "${3:-full}" in
        "full")
            run_full_audit
            ;;
        "q1")
            audit_sprint_q1
            ;;
        "q2")
            audit_sprint_q2
            ;;
        "q3")
            audit_sprint_q3
            ;;
        "q4")
            audit_sprint_q4
            ;;
        *)
            echo "Uso: $0 <PROJECT_ROOT> <MODULE|all> <full|q1|q2|q3|q4>"
            exit 1
            ;;
    esac
}

main "$@"
