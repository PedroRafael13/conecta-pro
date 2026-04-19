"""Seeder de condomínios — FASE 3.5 GEDEON (grafia oficial planilha 03/2026)

Idempotente: verifica nome_normalizado antes de inserir.
ESCRITÓRIO: usa UUID fixo a1b2c3d4-... (foi convertido da mock row pelo migration).
"""

import os
import sys
import uuid

sys.path.insert(0, "/app")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

CONDOMINIOS = [
    # ESCRITÓRIO — já existe no DB como a1b2c3d4-... (conversão do mock)
    # Seeder vai apenas linkar client_id (Conecta Mais / Matriz)
    # Kit Mensal (com folha CLT)
    {
        "nome": "PRIME ARENA",
        "nome_normalizado": "prime_arena",
        "tipo_servico": "kit_mensal",
        "tem_folha_clt": True,
        "match_client": "prime",
        "cnpj": None,
    },
    {
        "nome": "MICHELANGELO",
        "nome_normalizado": "michelangelo",
        "tipo_servico": "kit_mensal",
        "tem_folha_clt": True,
        "match_client": "michelang",
        "cnpj": None,
    },
    {
        "nome": "IDEAL FLORES",
        "nome_normalizado": "ideal_flores",
        "tipo_servico": "kit_mensal",
        "tem_folha_clt": True,
        "match_client": "ideal",
        "cnpj": None,
    },
    {
        "nome": "LARANJEIRAS",
        "nome_normalizado": "laranjeiras",
        "tipo_servico": "kit_mensal",
        "tem_folha_clt": True,
        "match_client": "laranjeir",
        "cnpj": None,
    },
    {
        "nome": "MIRANTE",
        "nome_normalizado": "mirante",
        "tipo_servico": "kit_mensal",
        "tem_folha_clt": True,
        "match_client": "mirante",
        "cnpj": None,
    },
    {
        "nome": "VILLA DEI FIORI",
        "nome_normalizado": "villa_dei_fiori",
        "tipo_servico": "kit_mensal",
        "tem_folha_clt": True,
        "match_client": "fiori",
        "cnpj": None,
    },
    {
        "nome": "VILLA PÁSSAROS",
        "nome_normalizado": "villa_passaros",
        "tipo_servico": "kit_mensal",
        "tem_folha_clt": True,
        "match_client": "pass",
        "cnpj": None,
    },
    # Serviços (sem folha CLT)
    {
        "nome": "P. GELAIN",
        "nome_normalizado": "p_gelain",
        "tipo_servico": "portaria_remota",
        "tem_folha_clt": False,
        "match_client": "gelain",
        "cnpj": None,
    },
    {
        "nome": "GREEN HILLS",
        "nome_normalizado": "green_hills",
        "tipo_servico": "manutencao_cftv",
        "tem_folha_clt": False,
        "match_client": "green",
        "cnpj": None,
    },
    {
        "nome": "PARISE",
        "nome_normalizado": "parise",
        "tipo_servico": "portaria_autonoma",
        "tem_folha_clt": False,
        "match_client": "parise",
        "cnpj": None,
    },
]

ESCRITORIO_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def seed(db_url: str | None = None) -> None:
    url = db_url or os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    engine = create_engine(url)
    nao_matchados = []

    with Session(engine) as session:
        # Link ESCRITÓRIO to client (Matriz escritório)
        escritorio_client = session.execute(
            text("SELECT id FROM clients WHERE name ILIKE '%matriz%escrit%' OR name ILIKE '%conecta mais%' LIMIT 1")
        ).first()
        if escritorio_client:
            session.execute(
                text("UPDATE condominios SET client_id = :cid WHERE nome_normalizado = 'escritorio'"),
                {"cid": str(escritorio_client[0])},
            )
            print(f"🔗 ESCRITÓRIO → client linked (id={escritorio_client[0]})")
        else:
            print("⚠️  ESCRITÓRIO: nenhum client match (mantém client_id=NULL)")

        criados = 0
        for c in CONDOMINIOS:
            exists = session.execute(
                text("SELECT id FROM condominios WHERE nome_normalizado = :slug"),
                {"slug": c["nome_normalizado"]},
            ).first()
            if exists:
                print(f"⏭️  {c['nome_normalizado']} já existe (id={exists[0]})")
                continue

            # Match client por nome
            client_id = None
            if c.get("match_client"):
                client = session.execute(
                    text("SELECT id FROM clients WHERE name ILIKE :pattern LIMIT 1"),
                    {"pattern": f"%{c['match_client']}%"},
                ).first()
                if client:
                    client_id = str(client[0])
                    print(f"🔗 {c['nome']} → client linked")
                else:
                    nao_matchados.append(c["nome"])
                    print(f"⚠️  {c['nome']}: sem match em clients")

            new_id = str(uuid.uuid4())
            session.execute(
                text(
                    "INSERT INTO condominios "
                    "(id, nome, nome_normalizado, cnpj, tipo_servico, tem_folha_clt, "
                    "client_id, ativo, created_at, updated_at) "
                    "VALUES (:id, :nome, :slug, :cnpj, :tipo, :folha, :cid, true, NOW(), NOW())"
                ),
                {
                    "id": new_id,
                    "nome": c["nome"],
                    "slug": c["nome_normalizado"],
                    "cnpj": c.get("cnpj"),
                    "tipo": c["tipo_servico"],
                    "folha": c["tem_folha_clt"],
                    "cid": client_id,
                },
            )
            criados += 1
            print(f"✅ {c['nome']} adicionado")

        session.commit()

        total = session.execute(text("SELECT COUNT(*) FROM condominios")).scalar()
        linked = session.execute(text("SELECT COUNT(*) FROM condominios WHERE client_id IS NOT NULL")).scalar()
        print(f"\n📊 Total condominios no DB: {total} ({linked} linked ao CRM)")

        if nao_matchados:
            print(f"\n⚠️  {len(nao_matchados)} sem match em clients:")
            for n in nao_matchados:
                print(f"  - {n}")


if __name__ == "__main__":
    seed()
