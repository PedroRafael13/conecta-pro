"""seed_bloco_a_presenca.py

Seed 320 pares (template, condomínio) com presença da matriz 32×10.
Executa: docker exec conecta-pro-backend python3 /app/scripts/seed_bloco_a_presenca.py

Legenda: 'O'=obrigatorio | 'E'=eventual | '-'=na
"""

import asyncio
import os
import sys

import asyncpg

# Matriz 32 × 10: cada linha = doc#, cada coluna = condomínio
# Ordem das colunas: prime_arena, michelangelo, p_gelain, green_hills,
#                   ideal_flores, laranjeiras, mirante, parise, villa_dei_fiori, villa_passaros
# O=obrigatorio, E=eventual, -=na
MATRIZ = {
    # slug: [prime_arena, mich, p_gelain, green_hills, ideal_flores, lara, mirante, parise, vdf, vp]
    "nfse": ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
    "boleto": ["O", "-", "O", "O", "O", "O", "O", "O", "O", "-"],
    "folha_pagamento": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "contracheque": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "folhas_ponto": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "gfd_fgts_mensal": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "relatorio_gfd_fgts": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "comp_pag_fgts": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "gfd_fgts_rescisao": ["O", "-", "-", "-", "O", "O", "O", "-", "-", "-"],
    "relatorio_gfd_rescisao": ["O", "-", "-", "-", "O", "O", "O", "-", "-", "-"],
    "comp_fgts_rescisao": ["O", "-", "-", "-", "-", "O", "-", "-", "-", "-"],
    "dctfweb_declaracao": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "dctfweb_recibo": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "dctfweb_extrato": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "cnd_rfb": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "cnd_caixa": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "cnd_prefeitura": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "cnd_sefaz": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "cnd_trabalhista": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "comp_vt_individual": ["O", "-", "-", "-", "O", "O", "O", "-", "O", "O"],
    "comp_va_solides": ["O", "-", "-", "-", "O", "O", "O", "-", "O", "O"],
    "comp_vt_va_combinado": ["O", "-", "-", "-", "O", "O", "O", "-", "O", "-"],
    "recibo_vt_va": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
    "relatorio_pedido_va": ["O", "-", "-", "-", "O", "O", "O", "-", "O", "O"],
    "aso": ["O", "-", "-", "-", "O", "O", "-", "-", "-", "-"],
    "contrato_trabalho": ["O", "-", "-", "-", "O", "O", "O", "-", "O", "-"],
    "ficha_empregado": ["O", "-", "-", "-", "O", "O", "O", "-", "O", "-"],
    "aviso_previo_ferias": ["-", "-", "-", "-", "E", "-", "-", "-", "-", "-"],
    "recibo_ferias": ["-", "-", "-", "-", "E", "-", "-", "-", "-", "E"],
    "rescisao_contrato": ["E", "-", "-", "-", "E", "E", "E", "-", "-", "-"],
    "comp_rescisao": ["E", "-", "-", "-", "E", "E", "E", "-", "-", "-"],
    "comp_salario_individual": ["O", "O", "-", "-", "O", "O", "O", "-", "O", "O"],
}

# Coluna index → nome_normalizado
COND_COLS = [
    "prime_arena",
    "michelangelo",
    "p_gelain",
    "green_hills",
    "ideal_flores",
    "laranjeiras",
    "mirante",
    "parise",
    "villa_dei_fiori",
    "villa_passaros",
]

PRESENCA_MAP = {"O": "obrigatorio", "E": "eventual", "-": "na"}


async def run():
    db_url = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
    if not db_url:
        print("ERROR: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)

    conn = await asyncpg.connect(db_url)
    try:
        async with conn.transaction():
            # Load template IDs by slug
            rows = await conn.fetch("SELECT slug, id FROM kit_documental_templates WHERE slug IS NOT NULL")
            slug_to_id = {r["slug"]: r["id"] for r in rows}
            assert len(slug_to_id) == 32, f"Expected 32 templates with slugs, got {len(slug_to_id)}"

            # Load condominio IDs by nome_normalizado
            cond_rows = await conn.fetch(
                "SELECT nome_normalizado, id FROM condominios WHERE ativo=true AND nome_normalizado != 'escritorio'"
            )
            cond_map = {r["nome_normalizado"]: r["id"] for r in cond_rows}
            print(f"Condominios carregados: {list(cond_map.keys())}")
            assert len(cond_map) == 10, f"Expected 10 condominios (excl escritório), got {len(cond_map)}"

            # DELETE existing presenca rows
            deleted = await conn.fetchval("SELECT COUNT(*) FROM kit_template_presenca")
            if deleted > 0:
                await conn.execute("DELETE FROM kit_template_presenca")
                print(f"Deleted {deleted} presença rows")

            # INSERT 320 pairs
            count = 0
            for slug, presencas in MATRIZ.items():
                template_id = slug_to_id[slug]
                for col_idx, p_code in enumerate(presencas):
                    cond_name = COND_COLS[col_idx]
                    cond_id = cond_map[cond_name]
                    presenca_val = PRESENCA_MAP[p_code]
                    await conn.execute(
                        """
                        INSERT INTO kit_template_presenca (template_id, condominio_id, presenca)
                        VALUES ($1, $2, $3)
                        """,
                        template_id,
                        cond_id,
                        presenca_val,
                    )
                    count += 1

            total = await conn.fetchval("SELECT COUNT(*) FROM kit_template_presenca")
            print(f"Presença rows inseridos: {total}")
            assert total == 320, f"Expected 320 rows, got {total}"

            # Verify counts per presenca type
            obrig = await conn.fetchval("SELECT COUNT(*) FROM kit_template_presenca WHERE presenca='obrigatorio'")
            eventual = await conn.fetchval("SELECT COUNT(*) FROM kit_template_presenca WHERE presenca='eventual'")
            na = await conn.fetchval("SELECT COUNT(*) FROM kit_template_presenca WHERE presenca='na'")
            print(f"  obrigatorio: {obrig}, eventual: {eventual}, na: {na}")
            assert obrig + eventual + na == 320

            print("SEED PRESENCA: OK (320 rows)")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
