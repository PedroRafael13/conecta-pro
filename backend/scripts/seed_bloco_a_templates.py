"""seed_bloco_a_templates.py

Seed canônico: 32 templates GEDEON (planilha GEDEON_Arquitetura_Modulos_032026.xlsx).
Executa: docker exec conecta-pro-backend python3 /app/scripts/seed_bloco_a_templates.py

Estratégia:
  - DELETE todos os rows antigos (38 → 0)
  - INSERT 32 canônicos com (num, modulo, slug, escopo, obrigatorio, status_origem, nome)
  - tipo_servico = NULL (coluna mantida por backward compat, não mais usada)
  - periodicidade = 'mensal' para todos (padrao)
"""

import asyncio
import os
import sys
import uuid

import asyncpg

TEMPLATES = [
    # (num, modulo, slug, nome, escopo, obrigatorio, status_origem)
    (1, "M1", "nfse", "NFS-e (nota fiscal XML)", "condominio", True, "GERA"),
    (2, "M1", "boleto", "Boleto de Cobrança", "condominio", True, "GERA"),
    (3, "M2", "folha_pagamento", "Folha de Pagamento", "condominio", True, "RECEBE"),
    (4, "M2", "contracheque", "Contracheques", "funcionario", True, "RECEBE"),
    (5, "M2", "folhas_ponto", "Folhas de Ponto", "funcionario", True, "RECEBE"),
    (6, "M3", "gfd_fgts_mensal", "GFD FGTS Mensal", "condominio", True, "RECEBE"),
    (7, "M3", "relatorio_gfd_fgts", "Relatório GFD FGTS", "condominio", True, "RECEBE"),
    (8, "M3", "comp_pag_fgts", "Comprovante Pagamento FGTS", "condominio", True, "GERA"),
    (9, "M3", "gfd_fgts_rescisao", "GFD FGTS Rescisão", "funcionario", False, "RECEBE"),
    (10, "M3", "relatorio_gfd_rescisao", "Relatório GFD FGTS Rescisão", "funcionario", False, "RECEBE"),
    (11, "M3", "comp_fgts_rescisao", "Comprovante Pagamento FGTS Rescisão", "funcionario", False, "GERA"),
    (12, "M4", "dctfweb_declaracao", "DCTFWEB — Declaração Completa", "condominio", True, "RECEBE"),
    (13, "M4", "dctfweb_recibo", "DCTFWEB — Recibo de Entrega", "condominio", True, "RECEBE"),
    (14, "M4", "dctfweb_extrato", "DCTFWEB — Relatório/Extrato", "condominio", True, "RECEBE"),
    (15, "M5", "cnd_rfb", "CND Receita Federal", "empresa_matriz", True, "BUSCA"),
    (16, "M5", "cnd_caixa", "CND FGTS/Caixa", "empresa_matriz", True, "BUSCA"),
    (17, "M5", "cnd_prefeitura", "CND Prefeitura", "empresa_matriz", True, "BUSCA"),
    (18, "M5", "cnd_sefaz", "CND Sefaz", "empresa_matriz", True, "BUSCA"),
    (19, "M5", "cnd_trabalhista", "CND Trabalhista (TST)", "empresa_matriz", True, "BUSCA"),
    (20, "M6", "comp_vt_individual", "Comprovante VT Individual", "funcionario", True, "RECEBE"),
    (21, "M6", "comp_va_solides", "Comprovante VA — Solides", "funcionario", True, "RECEBE"),
    (22, "M6", "comp_vt_va_combinado", "Comprovante VT+VA Combinado", "funcionario", True, "RECEBE"),
    (23, "M6", "recibo_vt_va", "Recibo VT e VA Geral", "condominio", True, "RECEBE"),
    (24, "M6", "relatorio_pedido_va", "Relatório Pedido VA — Solides", "condominio", True, "RECEBE"),
    (25, "M7", "aso", "ASO — Atestado Saúde Ocupacional", "condominio", False, "RECEBE"),
    (26, "M7", "contrato_trabalho", "Contrato de Trabalho", "funcionario", True, "GERA"),
    (27, "M7", "ficha_empregado", "Ficha de Empregado/Registro", "funcionario", True, "RECEBE"),
    (28, "M7", "aviso_previo_ferias", "Aviso Prévio de Férias", "funcionario", False, "GERA"),
    (29, "M7", "recibo_ferias", "Recibo Pagamento Férias", "funcionario", False, "RECEBE"),
    (30, "M7", "rescisao_contrato", "Rescisão de Contrato", "funcionario", False, "RECEBE"),
    (31, "M7", "comp_rescisao", "Comprovante Pagamento Rescisão", "funcionario", False, "GERA"),
    (32, "M8", "comp_salario_individual", "Comprovante Salário Individual", "funcionario", True, "GERA"),
]

assert len(TEMPLATES) == 32, f"Expected 32 templates, got {len(TEMPLATES)}"


async def run():
    db_url = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
    if not db_url:
        print("ERROR: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)

    conn = await asyncpg.connect(db_url)
    try:
        async with conn.transaction():
            # Backup count
            old_count = await conn.fetchval("SELECT COUNT(*) FROM kit_documental_templates")
            print(f"Templates antes: {old_count}")

            # DELETE all old templates
            await conn.execute("DELETE FROM kit_documental_templates")

            # INSERT 32 canonical templates
            for num, modulo, slug, nome, escopo, obrigatorio, status_origem in TEMPLATES:
                await conn.execute(
                    """
                    INSERT INTO kit_documental_templates
                        (id, tipo_documento, escopo, obrigatorio, periodicidade,
                         num, modulo, slug, status_origem, descricao)
                    VALUES ($1, $2, $3, $4, 'mensal', $5, $6, $7, $8, $9)
                    """,
                    uuid.uuid4(),
                    slug,
                    escopo,
                    obrigatorio,
                    num,
                    modulo,
                    slug,
                    status_origem,
                    nome,
                )

            new_count = await conn.fetchval("SELECT COUNT(*) FROM kit_documental_templates")
            print(f"Templates depois: {new_count}")
            assert new_count == 32, f"Expected 32, got {new_count}"

            # Verify slug uniqueness
            dup = await conn.fetchval(
                "SELECT COUNT(*) FROM (SELECT slug FROM kit_documental_templates GROUP BY slug HAVING COUNT(*)>1) x"
            )
            assert dup == 0, f"Duplicate slugs found: {dup}"

            print("SEED TEMPLATES: OK (32 rows, 0 duplicates)")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
