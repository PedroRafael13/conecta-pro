"""
Script de Seed para Módulo Operacional
Popula banco de dados com dados de teste realistas.

Usage:
    python -m scripts.seed_operacional
"""

import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from modules.operacional.models.post import Post, PostType, PostStatus, ShiftType
from modules.operacional.models.scale import Scale, ScaleStatus
from modules.operacional.models.shift import Shift, ShiftStatus
from modules.operacional.inspection_rounds.models import (
    InspectionRound,
    InspectionRoundStatus,
    InspectorRole,
)

# Tenant padrão
TENANT_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
USER_ID = "00000000-0000-0000-0000-000000000001"

# Dados fake
CIDADES = ["Manaus", "São Paulo", "Rio de Janeiro", "Brasília", "Curitiba", "Belo Horizonte"]
ESTADOS = ["AM", "SP", "RJ", "DF", "PR", "MG"]

POSTOS_NOMES = [
    "Condomínio Residencial Jardim das Flores",
    "Edifício Comercial Centro Empresarial",
    "Shopping Center Plaza",
    "Hospital Municipal",
    "Universidade Federal",
    "Fábrica Metalúrgica Norte",
    "Banco Central - Sede",
    "Aeroporto Internacional",
    "Terminal Rodoviário",
    "Parque Industrial Sul",
]


async def create_posts(session: AsyncSession, count: int = 10):
    """Cria postos de trabalho."""
    print(f"Criando {count} postos de trabalho...")
    posts = []

    for i in range(count):
        cidade = random.choice(CIDADES)
        estado = random.choice(ESTADOS)

        post = Post(
            id=str(uuid4()),
            tenant_id=TENANT_ID,
            code=f"POST-{2026}-{str(i+1).zfill(4)}",
            name=POSTOS_NOMES[i] if i < len(POSTOS_NOMES) else f"Posto {i+1}",
            post_type=random.choice(list(PostType)).value,
            status=random.choices(
                [PostStatus.ACTIVE.value, PostStatus.INACTIVE.value, PostStatus.TEMPORARY.value],
                weights=[80, 10, 10]
            )[0],
            shift_type=random.choice(list(ShiftType)).value,
            headcount=random.randint(2, 10),
            filled_count=random.randint(0, 10),
            address=f"Rua {random.randint(1, 100)}, {random.randint(1, 999)}",
            city=cidade,
            state=estado,
            zipcode=f"{random.randint(10000, 99999):05d}-{random.randint(100, 999):03d}",
            latitude=random.uniform(-23.5, -3.1),
            longitude=random.uniform(-60.0, -43.2),
            created_by=USER_ID,
            is_active=True,
        )
        posts.append(post)
        session.add(post)

    await session.flush()
    print(f"✅ {count} postos criados")
    return posts


async def create_scales(session: AsyncSession, posts: list, count: int = 3):
    """Cria escalas."""
    print(f"Criando {count} escalas...")
    scales = []

    current_month = datetime.now().month
    current_year = datetime.now().year

    for i in range(count):
        month_offset = i
        month = (current_month + month_offset - 1) % 12 + 1
        year = current_year if (current_month + month_offset) <= 12 else current_year + 1

        scale = Scale(
            id=str(uuid4()),
            tenant_id=TENANT_ID,
            code=f"ESC-{year}-{str(month).zfill(2)}-{str(i+1).zfill(3)}",
            name=f"Escala {month:02d}/{year}",
            description=f"Escala do mês {month}/{year}",
            month=month,
            year=year,
            status=random.choice([
                ScaleStatus.DRAFT.value,
                ScaleStatus.APPROVED.value,
                ScaleStatus.IN_PROGRESS.value,
            ]),
            start_date=datetime(year, month, 1),
            end_date=datetime(year, month, 28 if month == 2 else 30),
            total_shifts=random.randint(50, 200),
            filled_shifts=random.randint(40, 180),
            total_hours=random.randint(1000, 5000),
            created_by=USER_ID,
            is_active=True,
        )
        scales.append(scale)
        session.add(scale)

    await session.flush()
    print(f"✅ {count} escalas criadas")
    return scales


async def create_shifts(session: AsyncSession, scales: list, posts: list, count: int = 50):
    """Cria turnos."""
    print(f"Criando {count} turnos...")

    for _ in range(count):
        scale = random.choice(scales)
        post = random.choice(posts)

        # Data aleatória dentro do mês da escala
        day = random.randint(1, 28)
        shift_date = datetime(scale.year, scale.month, day)

        # Horários
        start_hour = random.choice([6, 7, 8, 14, 22])
        start_time = datetime(scale.year, scale.month, day, start_hour, 0)
        end_time = start_time + timedelta(hours=random.choice([6, 8, 12]))

        shift = Shift(
            id=str(uuid4()),
            tenant_id=TENANT_ID,
            code=f"TRN-{scale.year}-{str(scale.month).zfill(2)}-{str(random.randint(1,999)).zfill(3)}",
            scale_id=scale.id,
            post_id=post.id,
            post_name=post.name,
            shift_date=shift_date.date(),
            start_time=start_time.time(),
            end_time=end_time.time(),
            status=random.choice([
                ShiftStatus.SCHEDULED.value,
                ShiftStatus.IN_PROGRESS.value,
                ShiftStatus.COMPLETED.value,
            ]),
            needs_substitution=random.random() < 0.1,  # 10% precisam substituição
            created_by=USER_ID,
            is_active=True,
        )
        session.add(shift)

    await session.flush()
    print(f"✅ {count} turnos criados")


async def create_inspection_rounds(session: AsyncSession, posts: list, count: int = 10):
    """Cria rondas de inspeção."""
    print(f"Criando {count} rondas de inspeção...")

    for i in range(count):
        scheduled_date = datetime.now() + timedelta(days=random.randint(-30, 30))

        round_obj = InspectionRound(
            id=str(uuid4()),
            tenant_id=TENANT_ID,
            code=f"RND-{2026}-{str(i+1).zfill(4)}",
            inspector_id=USER_ID,
            inspector_name="Inspetor Teste",
            inspector_role=random.choice(list(InspectorRole)).value,
            status=random.choice([
                InspectionRoundStatus.AGENDADA.value,
                InspectionRoundStatus.EM_ANDAMENTO.value,
                InspectionRoundStatus.CONCLUIDA.value,
            ]),
            scheduled_date=scheduled_date,
            posts_to_visit=[p.id for p in random.sample(posts, min(3, len(posts)))],
            total_checkpoints=random.randint(0, 10),
            total_occurrences=random.randint(0, 5),
            created_by=USER_ID,
            is_active=True,
        )

        # Se concluída, adicionar timestamps
        if round_obj.status == InspectionRoundStatus.CONCLUIDA.value:
            round_obj.started_at = scheduled_date
            round_obj.completed_at = scheduled_date + timedelta(hours=random.randint(2, 6))
            round_obj.duration_minutes = random.randint(120, 360)

        session.add(round_obj)

    await session.flush()
    print(f"✅ {count} rondas criadas")


async def seed_database():
    """Seed principal."""
    print("\n🌱 Iniciando seed do banco de dados...\n")

    # Criar engine
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Criar dados
            posts = await create_posts(session, count=10)
            scales = await create_scales(session, posts, count=3)
            await create_shifts(session, scales, posts, count=50)
            await create_inspection_rounds(session, posts, count=10)

            # Commit
            await session.commit()

            print("\n✅ Seed concluído com sucesso!")
            print(f"""
📊 Resumo:
   - {len(posts)} postos de trabalho
   - {len(scales)} escalas
   - 50 turnos
   - 10 rondas de inspeção
            """)

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Erro durante seed: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
