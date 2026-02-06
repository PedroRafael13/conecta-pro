"""
Script de Seed Simplificado para Módulo Operacional
Popula banco de dados com dados de teste usando SQL direto.

Usage:
    docker exec conecta-pro-backend python scripts/seed_simple.py
"""

import asyncio
import os
import sys

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings


SEED_SQL = """
-- Seed de Postos
INSERT INTO posts (id, code, name, post_type, status, shift_type, address, city, state, required_headcount, current_headcount, is_active, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'POST-2026-0001', 'Condomínio Jardim das Flores', 'vigilante', 'active', 'diurno', 'Rua das Flores, 123', 'Manaus', 'AM', 3, 2, true, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222', 'POST-2026-0002', 'Edifício Comercial Centro', 'porteiro', 'active', 'administrativo', 'Av. Central, 456', 'São Paulo', 'SP', 2, 2, true, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333', 'POST-2026-0003', 'Shopping Plaza', 'controlador_acesso', 'active', 'integral', 'Rua do Comércio, 789', 'Rio de Janeiro', 'RJ', 5, 4, true, NOW(), NOW()),
    ('44444444-4444-4444-4444-444444444444', 'POST-2026-0004', 'Hospital Municipal', 'recepcionista', 'active', 'diurno', 'Av. Saúde, 100', 'Brasília', 'DF', 4, 3, true, NOW(), NOW()),
    ('55555555-5555-5555-5555-555555555555', 'POST-2026-0005', 'Universidade Federal', 'vigilante', 'temporary', 'noturno', 'Campus Universitário', 'Curitiba', 'PR', 6, 5, true, NOW(), NOW()),
    ('66666666-6666-6666-6666-666666666666', 'POST-2026-0006', 'Fábrica Norte', 'rondante', 'active', 'integral', 'Distrito Industrial', 'Belo Horizonte', 'MG', 8, 6, true, NOW(), NOW()),
    ('77777777-7777-7777-7777-777777777777', 'POST-2026-0007', 'Banco Central', 'supervisor', 'active', 'administrativo', 'Setor Bancário, 200', 'Brasília', 'DF', 2, 2, true, NOW(), NOW()),
    ('88888888-8888-8888-8888-888888888888', 'POST-2026-0008', 'Aeroporto Internacional', 'vigilante', 'active', 'integral', 'Terminal 1', 'Manaus', 'AM', 10, 8, true, NOW(), NOW()),
    ('99999999-9999-9999-9999-999999999999', 'POST-2026-0009', 'Terminal Rodoviário', 'monitoramento', 'active', 'integral', 'Rodoviária Central', 'São Paulo', 'SP', 3, 3, true, NOW(), NOW()),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'POST-2026-0010', 'Parque Industrial Sul', 'servicos_gerais', 'inactive', 'manha', 'Zona Industrial', 'Rio de Janeiro', 'RJ', 4, 0, true, NOW(), NOW())
ON CONFLICT (code) DO NOTHING;

SELECT COUNT(*) as total_postos FROM posts WHERE is_active = true;
"""


async def run_seed():
    """Executa seed SQL."""
    print("\n🌱 Iniciando seed do banco de dados...\n")

    engine = create_async_engine(settings.database_url, echo=False)

    try:
        async with engine.begin() as conn:
            # Executar SQL
            await conn.execute(text("DELETE FROM posts WHERE code LIKE 'POST-2026-%'"))
            result = await conn.execute(text(SEED_SQL))

            print("\n✅ Seed concluído com sucesso!")
            print("""
📊 Resumo:
   - 10 postos de trabalho criados
            """)

    except Exception as e:
        print(f"\n❌ Erro durante seed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    from sqlalchemy import text
    asyncio.run(run_seed())
