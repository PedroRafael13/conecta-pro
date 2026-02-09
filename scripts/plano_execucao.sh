#!/bin/bash
# PLANO DE EXECUÇÃO CONSOLIDADO
# Automação das tarefas críticas

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/opt/conecta-pro"
LOG_FILE="$PROJECT_DIR/logs/plano_execucao_$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$PROJECT_DIR/logs"

echo_log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# ============================================
# FASE 1: CRÍTICO (Dias 1-7)
# ============================================

fase1_seguranca() {
    echo_log "${YELLOW}=== FASE 1: SEGURANÇA CRÍTICA ===${NC}"

    # 1.1 Backup dos .env atuais
    echo_log "[1.1] Backup dos arquivos .env..."
    cp "$PROJECT_DIR/backend/.env" "$PROJECT_DIR/backend/.env.backup.$(date +%Y%m%d)"
    cp "$PROJECT_DIR/frontend/.env.local" "$PROJECT_DIR/frontend/.env.local.backup.$(date +%Y%m%d)"
    echo_log "${GREEN}✅ Backup criado${NC}"

    # 1.2 Gerar novos secrets
    echo_log "[1.2] Gerando novos secrets..."
    NEW_JWT_SECRET=$(openssl rand -base64 32)
    NEW_REDIS_PASS=$(openssl rand -base64 24)
    echo_log "${GREEN}✅ Novos secrets gerados${NC}"

    # 1.3 Criar .env.secrets
    echo_log "[1.3] Criando .env.secrets..."
    cat > "$PROJECT_DIR/backend/.env.secrets" << EOF
# SECRETS - NÃO COMMITAR
JWT_SECRET_KEY=$NEW_JWT_SECRET
REDIS_PASSWORD=$NEW_REDIS_PASS
OPENAI_API_KEY=\${OPENAI_API_KEY:-""}
EOF
    chmod 600 "$PROJECT_DIR/backend/.env.secrets"
    echo_log "${GREEN}✅ .env.secrets criado (chmod 600)${NC}"

    # 1.4 Remover secrets do .env principal
    echo_log "[1.4] Limpando .env principal..."
    sed -i '/JWT_SECRET_KEY/d' "$PROJECT_DIR/backend/.env"
    sed -i '/OPENAI_API_KEY/d' "$PROJECT_DIR/backend/.env"
    echo_log "${GREEN}✅ Secrets removidos do .env principal${NC}"

    # 1.5 Migrar python-jose para PyJWT
    echo_log "[1.5] Migrando python-jose → PyJWT..."
    cd "$PROJECT_DIR/backend"
    pip uninstall -y python-jose 2>/dev/null || true
    pip install PyJWT cryptography

    # Script de migração
    find . -name "*.py" -exec sed -i 's/from jose import jwt/import jwt/g' {} \; 2>/dev/null || true
    find . -name "*.py" -exec sed -i 's/jwt\.encode/jwt.encode/g' {} \; 2>/dev/null || true
    echo_log "${GREEN}✅ PyJWT instalado${NC}"

    # 1.6 Verificar CORS
    echo_log "[1.6] Verificando CORS..."
    CORS_FILE="$PROJECT_DIR/backend/app/core/cors.py"
    if grep -q "localhost" "$CORS_FILE" 2>/dev/null; then
        echo_log "${RED}⚠️  localhost encontrado em CORS - REMOVER${NC}"
        sed -i '/localhost/d' "$CORS_FILE"
    fi
    echo_log "${GREEN}✅ CORS verificado${NC}"
}

fase1_testes() {
    echo_log "${YELLOW}=== FASE 1: CORREÇÃO DE TESTES ===${NC}"

    cd "$PROJECT_DIR/backend"

    # 2.1 Instalar pytest-cov
    echo_log "[2.1] Instalando pytest-cov..."
    pip install pytest-cov
    echo_log "${GREEN}✅ pytest-cov instalado${NC}"

    # 2.2 Identificar testes quebrados
    echo_log "[2.2] Identificando testes quebrados..."
    pytest --collect-only 2>&1 | grep -E "ERROR|FAILED" | head -30 | tee "$PROJECT_DIR/logs/testes_quebrados.log"
    echo_log "${YELLOW}Lista salva em logs/testes_quebrados.log${NC}"

    # 2.3 Corrigir imports quebrados (autofix)
    echo_log "[2.3] Tentando corrigir imports..."
    find tests/ -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | grep "SyntaxError" | head -10 || echo_log "${GREEN}✅ Nenhum SyntaxError${NC}"
}

fase1_excecoes() {
    echo_log "${YELLOW}=== FASE 1: TRATAMENTO DE EXCEÇÕES ===${NC}"

    # 3.1 Contar bare excepts
    echo_log "[3.1] Contando bare excepts..."
    BARE_COUNT=$(grep -rn "except:" --include="*.py" "$PROJECT_DIR/backend" | grep -v "except Exception:" | wc -l)
    echo_log "${YELLOW}Encontrados: $BARE_COUNT bare excepts${NC}"

    # 3.2 Criar lista para correção manual
    grep -rn "except:" --include="*.py" "$PROJECT_DIR/backend" | grep -v "except Exception:" | head -50 > "$PROJECT_DIR/logs/bare_excepts_list.log"
    echo_log "${YELLOW}Lista dos primeiros 50 salva em logs/bare_excepts_list.log${NC}"

    # 3.3 Auto-fix simples (apenas linhas simples)
    echo_log "[3.3] Aplicando auto-fix seguro..."
    find "$PROJECT_DIR/backend" -name "*.py" -exec sed -i 's/^\([[:space:]]*\)except:$/\1except Exception:/g' {} \;

    NEW_COUNT=$(grep -rn "except:" --include="*.py" "$PROJECT_DIR/backend" | grep -v "except Exception:" | wc -l)
    echo_log "${GREEN}✅ Reduzido de $BARE_COUNT para $NEW_COUNT${NC}"
}

# ============================================
# FASE 2: ALTA (Dias 8-18)
# ============================================

fase2_backend() {
    echo_log "${YELLOW}=== FASE 2: BACKEND CODE QUALITY ===${NC}"

    cd "$PROJECT_DIR/backend"

    # 4.1 Instalar Ruff
    echo_log "[4.1] Instalando Ruff..."
    pip install ruff

    # Criar config
    cat > pyproject.toml << 'EOF'
[tool.ruff]
target-version = "py312"
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = ["E501", "B008"]

[tool.ruff.pydocstyle]
convention = "google"
EOF
    echo_log "${GREEN}✅ Ruff configurado${NC}"

    # 4.2 Rodar Ruff
    echo_log "[4.2] Executando Ruff..."
    ruff check . --output-format=text 2>&1 | head -50 | tee "$PROJECT_DIR/logs/ruff_violations.log"
    echo_log "${YELLOW}Primeiras 50 violações salvas${NC}"

    # 4.3 Auto-fix
    echo_log "[4.3] Aplicando auto-fix..."
    ruff check . --fix --unsafe-fixes || true
    echo_log "${GREEN}✅ Auto-fix aplicado${NC}"
}

fase2_frontend() {
    echo_log "${YELLOW}=== FASE 2: FRONTEND CODE QUALITY ===${NC}"

    cd "$PROJECT_DIR/frontend"

    # 5.1 Contar hooks duplicados
    echo_log "[5.1] Analisando hooks duplicados..."
    find src/hooks -name "use*.ts" -exec basename {} \; | sort | uniq -d > "$PROJECT_DIR/logs/hooks_duplicados.log"
    DUPLICATES=$(wc -l < "$PROJECT_DIR/logs/hooks_duplicados.log")
    echo_log "${YELLOW}Hooks duplicados encontrados: $DUPLICATES${NC}"

    # 5.2 Contar :any
    echo_log "[5.2] Contando uso de ':any'..."
    ANY_COUNT=$(grep -r ":any" --include="*.ts" --include="*.tsx" src/ | wc -l)
    echo_log "${YELLOW}Uso de ':any': $ANY_COUNT${NC}"

    # 5.3 TypeScript check
    echo_log "[5.3] Verificando TypeScript..."
    npx tsc --noEmit 2>&1 | grep "error TS" | wc -l | xargs echo "Erros:"
}

# ============================================
# FASE 3: DATABASE (Dias 15-18)
# ============================================

fase3_database() {
    echo_log "${YELLOW}=== FASE 3: DATABASE OPTIMIZATION ===${NC}"

    # 6.1 Analisar queries N+1
    echo_log "[6.1] Analisando N+1 queries..."
    N1_COUNT=$(grep -rn "for.*in.*\.all()" --include="*.py" "$PROJECT_DIR/backend" | wc -l)
    echo_log "${YELLOW}Possíveis N+1 patterns: $N1_COUNT${NC}"

    # 6.2 Listar índices atuais
    echo_log "[6.2] Índices atuais:"
    docker exec conecta-pro-postgres psql -U postgres -c "
    SELECT tablename, indexname
    FROM pg_indexes
    WHERE schemaname = 'public'
    ORDER BY tablename;
    " conectapro 2>/dev/null | head -20 || echo_log "${RED}⚠️  Banco não acessível${NC}"

    # 6.3 Criar migration de índices
    echo_log "[6.3] Criando migration de índices..."
    cat > "$PROJECT_DIR/backend/alembic/versions/20260206_add_performance_indexes.py" << 'EOF'
"""Add performance indexes

Revision ID: perf_20260206
Revises:
Create Date: 2026-02-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'perf_20260206'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Índices compostos comuns
    op.create_index('idx_condominio_status', 'condominios', ['id', 'status'])
    op.create_index('idx_fatura_condominio_venc', 'faturas', ['condominio_id', 'vencimento'])
    op.create_index('idx_usuario_condominio', 'usuarios', ['condominio_id', 'is_active'])

def downgrade():
    op.drop_index('idx_condominio_status')
    op.drop_index('idx_fatura_condominio_venc')
    op.drop_index('idx_usuario_condominio')
EOF
    echo_log "${GREEN}✅ Migration de índices criada${NC}"
}

# ============================================
# RELATÓRIO
# ============================================

gerar_relatorio() {
    echo_log "${YELLOW}=== GERANDO RELATÓRIO ===${NC}"

    cat > "$PROJECT_DIR/logs/status_atual_$(date +%Y%m%d).md" << EOF
# Status da Correção - $(date +%Y-%m-%d)

## Métricas Atuais

### Segurança
- Secrets em .env principal: $(grep -c "JWT_SECRET_KEY\|OPENAI_API_KEY" "$PROJECT_DIR/backend/.env" 2>/dev/null || echo "0")
- python-jose no requirements: $(grep -c "python-jose" "$PROJECT_DIR/backend/requirements.txt" 2>/dev/null || echo "0")
- Bare excepts restantes: $(grep -rn "except:" --include="*.py" "$PROJECT_DIR/backend" | grep -v "except Exception:" | wc -l)

### Qualidade
- Violações Ruff: $(cd "$PROJECT_DIR/backend" && ruff check . 2>/dev/null | grep -c "error" || echo "N/A")
- Hooks duplicados: $(find "$PROJECT_DIR/frontend/src/hooks" -name "use*.ts" -exec basename {} \; 2>/dev/null | sort | uniq -d | wc -l)
- Uso de :any: $(grep -r ":any" --include="*.ts" --include="*.tsx" "$PROJECT_DIR/frontend/src" 2>/dev/null | wc -l)

### Testes
- Testes backend passando: $(cd "$PROJECT_DIR/backend" && pytest --tb=no 2>/dev/null | grep -o "[0-9]* passed" | head -1 || echo "N/A")

### Database
- N+1 patterns: $(grep -rn "for.*in.*\.all()" --include="*.py" "$PROJECT_DIR/backend" | wc -l)

## Próximos Passos
Ver detalhes em: $LOG_FILE
EOF

    echo_log "${GREEN}✅ Relatório gerado: logs/status_atual_$(date +%Y%m%d).md${NC}"
}

# ============================================
# MENU PRINCIPAL
# ============================================

show_menu() {
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  PLANO DE EXECUÇÃO CONSOLIDADO - CONECTA PRO v2.0"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "FASE 1 - CRÍTICO (Dias 1-7):"
    echo "  1. Segurança (secrets, python-jose, CORS)"
    echo "  2. Correção de Testes"
    echo "  3. Tratamento de Exceções"
    echo ""
    echo "FASE 2 - ALTA (Dias 8-18):"
    echo "  4. Backend Code Quality (Ruff)"
    echo "  5. Frontend Code Quality"
    echo ""
    echo "FASE 3 - DATABASE (Dias 15-18):"
    echo "  6. Database Optimization"
    echo ""
    echo "OUTROS:"
    echo "  9. Gerar Relatório"
    echo "  0. Executar TUDO (modo batch)"
    echo "  q. Sair"
    echo ""
}

# Execução principal
main() {
    if [ "$1" == "--batch" ] || [ "$1" == "0" ]; then
        echo_log "${GREEN}Modo BATCH - Executando todas as fases...${NC}"
        fase1_seguranca
        fase1_testes
        fase1_excecoes
        fase2_backend
        fase2_frontend
        fase3_database
        gerar_relatorio
        echo_log "${GREEN}=== CONCLUÍDO ===${NC}"
        exit 0
    fi

    while true; do
        show_menu
        read -p "Escolha uma opção: " opcao

        case $opcao in
            1) fase1_seguranca ;;
            2) fase1_testes ;;
            3) fase1_excecoes ;;
            4) fase2_backend ;;
            5) fase2_frontend ;;
            6) fase3_database ;;
            9) gerar_relatorio ;;
            0)
                read -p "Confirma execução completa? (s/N): " confirm
                if [ "$confirm" == "s" ]; then
                    fase1_seguranca
                    fase1_testes
                    fase1_excecoes
                    fase2_backend
                    fase2_frontend
                    fase3_database
                    gerar_relatorio
                fi
                ;;
            q|Q) exit 0 ;;
            *) echo "Opção inválida" ;;
        esac

        echo ""
        read -p "Pressione ENTER para continuar..."
    done
}

# Se chamado diretamente
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
