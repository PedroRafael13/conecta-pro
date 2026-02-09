#!/usr/bin/env python3
"""
Script para geração manual de escalas do mês atual.

Uso:
    python scripts/generate_current_month_scales.py

Para mês específico:
    python scripts/generate_current_month_scales.py --month 1 --year 2026
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.logging import logger
from modules.operacional.services.auto_scale_service import AutoScaleService


async def generate_scales(month: int = None, year: int = None):
    """
    Gera escalas para o mês atual ou especificado.

    Args:
        month: Mês (1-12), se None usa mês atual
        year: Ano, se None usa ano atual
    """
    # Criar engine e session
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        service = AutoScaleService(session)

        if month and year:
            logger.info(f"Gerando escalas para {month:02d}/{year}")
            result = await service.generate_scales_for_month(month, year)
        else:
            today = date.today()
            logger.info(f"Gerando escalas para o mês atual: {today.month:02d}/{today.year}")
            result = await service.generate_scales_for_current_month()

        # Exibir resultado
        print("\n" + "=" * 60)
        print("GERAÇÃO DE ESCALAS - RESULTADO")
        print("=" * 60)
        print(f"Status: {'SUCESSO' if result['success'] else 'ERRO'}")
        print(f"Mensagem: {result['message']}")
        print(f"Escalas criadas: {result['scales_created']}")
        print(f"Turnos criados: {result['shifts_created']}")

        if result["errors"]:
            print("\nErros:")
            for error in result["errors"]:
                print(f"  - {error}")

        print("=" * 60 + "\n")

    await engine.dispose()


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Gera escalas do mês atual ou especificado")
    parser.add_argument("--month", type=int, help="Mês (1-12)")
    parser.add_argument("--year", type=int, help="Ano")

    args = parser.parse_args()

    # Validar argumentos
    if (args.month and not args.year) or (args.year and not args.month):
        print("ERRO: Você deve especificar tanto --month quanto --year, ou nenhum dos dois")
        sys.exit(1)

    if args.month and (args.month < 1 or args.month > 12):
        print("ERRO: Mês deve estar entre 1 e 12")
        sys.exit(1)

    if args.year and (args.year < 2020 or args.year > 2100):
        print("ERRO: Ano deve estar entre 2020 e 2100")
        sys.exit(1)

    # Executar
    asyncio.run(generate_scales(args.month, args.year))


if __name__ == "__main__":
    main()
