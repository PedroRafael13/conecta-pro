#!/usr/bin/env python3
"""
Script rápido para gerar escalas via execução direta do serviço.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar root ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from modules.operacional.services.auto_scale_service import AutoScaleService


async def main():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        service = AutoScaleService(session)
        print("Gerando escalas para o mês atual...")
        result = await service.generate_scales_for_current_month()

        print("\n" + "=" * 60)
        print("RESULTADO DA GERAÇÃO")
        print("=" * 60)
        print(f"Status: {'SUCESSO' if result['success'] else 'ERRO'}")
        print(f"Mensagem: {result['message']}")
        print(f"Escalas criadas: {result['scales_created']}")
        print(f"Turnos criados: {result['shifts_created']}")

        if result["errors"]:
            print("\nErros:")
            for error in result["errors"]:
                print(f"  - {error}")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
