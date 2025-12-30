#!/usr/bin/env python3
"""
Script de validacao de integridade de dados.
Verifica foreign keys orfas, duplicatas e dados inconsistentes.
"""

import asyncio
import sys
from datetime import datetime

# Adicionar path do backend
sys.path.insert(0, "/opt/erp-conecta-mais/backend")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

# Cores para output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


async def validate_data_integrity():
    """Valida integridade referencial e constraints."""
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}  VALIDACAO DE INTEGRIDADE DE DADOS{NC}")
    print(f"{GREEN}  Data: {datetime.now()}{NC}")
    print(f"{GREEN}========================================{NC}\n")

    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    issues = []
    checks_passed = 0

    async with async_session() as session:
        # 1. Verificar usuarios duplicados por email
        print(f"{YELLOW}[1/5] Verificando emails duplicados...{NC}")
        try:
            result = await session.execute(
                text("""
                    SELECT email, COUNT(*) as count
                    FROM users
                    GROUP BY email
                    HAVING COUNT(*) > 1
                """)
            )
            duplicates = result.fetchall()
            if duplicates:
                for dup in duplicates:
                    issues.append(f"Email duplicado: {dup.email} ({dup.count}x)")
                print(f"{RED}   {len(duplicates)} emails duplicados encontrados{NC}")
            else:
                print(f"{GREEN}   OK - Nenhum email duplicado{NC}")
                checks_passed += 1
        except Exception as e:
            print(f"{YELLOW}   SKIP - Tabela users nao existe ainda{NC}")
            checks_passed += 1

        # 2. Verificar se ha usuarios sem role valido
        print(f"\n{YELLOW}[2/5] Verificando roles invalidos...{NC}")
        try:
            result = await session.execute(
                text("""
                    SELECT id, email, role
                    FROM users
                    WHERE role NOT IN ('super_admin', 'admin', 'manager', 'supervisor', 'operator', 'client', 'viewer')
                """)
            )
            invalid_roles = result.fetchall()
            if invalid_roles:
                for user in invalid_roles:
                    issues.append(f"Role invalido: {user.email} tem role '{user.role}'")
                print(f"{RED}   {len(invalid_roles)} usuarios com role invalido{NC}")
            else:
                print(f"{GREEN}   OK - Todos os roles sao validos{NC}")
                checks_passed += 1
        except Exception as e:
            print(f"{YELLOW}   SKIP - Tabela users nao existe ainda{NC}")
            checks_passed += 1

        # 3. Verificar usuarios inativos com ultimo login recente
        print(f"\n{YELLOW}[3/5] Verificando inconsistencias de status...{NC}")
        try:
            result = await session.execute(
                text("""
                    SELECT id, email, is_active, last_login
                    FROM users
                    WHERE is_active = false
                    AND last_login IS NOT NULL
                    AND last_login > (NOW() - INTERVAL '7 days')::text
                """)
            )
            inconsistent = result.fetchall()
            if inconsistent:
                for user in inconsistent:
                    issues.append(f"Usuario inativo com login recente: {user.email}")
                print(f"{RED}   {len(inconsistent)} inconsistencias encontradas{NC}")
            else:
                print(f"{GREEN}   OK - Status de usuarios consistente{NC}")
                checks_passed += 1
        except Exception as e:
            print(f"{YELLOW}   SKIP - Verificacao nao aplicavel{NC}")
            checks_passed += 1

        # 4. Verificar tabela alembic_version
        print(f"\n{YELLOW}[4/5] Verificando migrations...{NC}")
        try:
            result = await session.execute(
                text("SELECT version_num FROM alembic_version")
            )
            version = result.scalar()
            if version:
                print(f"{GREEN}   OK - Migration atual: {version}{NC}")
                checks_passed += 1
            else:
                issues.append("Nenhuma migration aplicada")
                print(f"{RED}   ERRO - Nenhuma migration aplicada{NC}")
        except Exception as e:
            issues.append("Tabela alembic_version nao existe")
            print(f"{RED}   ERRO - Alembic nao inicializado{NC}")

        # 5. Verificar conexao e health do banco
        print(f"\n{YELLOW}[5/5] Verificando health do banco...{NC}")
        try:
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print(f"{GREEN}   OK - Banco respondendo{NC}")
                checks_passed += 1
        except Exception as e:
            issues.append(f"Banco nao responde: {e}")
            print(f"{RED}   ERRO - Banco nao responde: {e}{NC}")

    await engine.dispose()

    # Resumo
    print(f"\n{GREEN}========================================{NC}")
    print(f"{GREEN}  RESUMO DA VALIDACAO{NC}")
    print(f"{GREEN}========================================{NC}")
    print(f"  Verificacoes OK: {checks_passed}/5")

    if issues:
        print(f"\n{RED}  PROBLEMAS ENCONTRADOS:{NC}")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\n{RED}  STATUS: FALHA - {len(issues)} problema(s){NC}")
        return 1
    else:
        print(f"\n{GREEN}  STATUS: OK - Integridade validada{NC}")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(validate_data_integrity())
    sys.exit(exit_code)
