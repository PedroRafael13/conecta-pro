"""Seeder de kit_documental_templates — FASE 3.5 BLOCO 2/T3

Dados 100% da planilha GEDEON_Arquitetura_Modulos_032026.xlsx.
Zero invenção (§13.1 Chesterton, §13.4 Escopo).

Regras:
- CNDs: escopo='empresa_matriz' MAS entram em kit_mensal (Jordan aprovou)
- Rescisões/Férias: obrigatorio=false (eventuais)
- ASO: obrigatorio=false (periódico)
- Administrativo NÃO tem kit (Jordan aprovou)
"""

import os
import sys
import uuid

sys.path.insert(0, "/app")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Estrutura: (tipo_documento, escopo, obrigatorio, periodicidade, descricao)
# Aplicado a kit_mensal (7 condomínios com folha CLT)

KIT_MENSAL: list[tuple[str, str, bool, str, str]] = [
    # M1 Fiscal
    ("nfse", "condominio", True, "mensal", "NFS-e emitida pela Conecta Mais"),
    ("boleto", "condominio", True, "mensal", "Boleto de cobrança do serviço prestado"),
    # M2 Contábil
    ("folha_pagamento", "condominio", True, "mensal", "Folha de pagamento do posto"),
    ("contracheque", "funcionario", True, "mensal", "Contracheque por funcionário"),
    ("folhas_ponto", "funcionario", True, "mensal", "Folha de ponto por funcionário"),
    # M3 FGTS (obrigatórios mensais)
    ("gfd_fgts_mensal", "condominio", True, "mensal", "GFD FGTS mensal (guia)"),
    ("relatorio_gfd_fgts", "condominio", True, "mensal", "Relatório GFD FGTS"),
    ("comp_pag_fgts", "condominio", True, "mensal", "Comprovante de pagamento FGTS"),
    # M3 FGTS Rescisão (eventuais)
    ("gfd_fgts_rescisao", "funcionario", False, "eventual", "GFD FGTS Rescisão (quando há demissão)"),
    ("relatorio_gfd_rescisao", "funcionario", False, "eventual", "Relatório GFD FGTS Rescisão"),
    ("comp_fgts_rescisao", "funcionario", False, "eventual", "Comprovante FGTS Rescisão"),
    # M4 DCTFWeb
    ("dctfweb_declaracao", "condominio", True, "mensal", "DCTFWeb declaração completa"),
    ("dctfweb_recibo", "condominio", True, "mensal", "DCTFWeb recibo de entrega"),
    ("dctfweb_extrato", "condominio", True, "mensal", "DCTFWeb extrato/relatório"),
    # M5 CNDs (escopo matriz MAS entram em kit — Jordan aprovou)
    ("cnd_rfb", "empresa_matriz", True, "mensal", "CND Receita Federal (Conecta Mais)"),
    ("cnd_caixa", "empresa_matriz", True, "mensal", "CND FGTS / Caixa (Conecta Mais)"),
    ("cnd_prefeitura", "empresa_matriz", True, "mensal", "CND Prefeitura Manaus"),
    ("cnd_sefaz", "empresa_matriz", True, "mensal", "CND Sefaz-AM"),
    ("cnd_trabalhista", "empresa_matriz", True, "mensal", "CND Trabalhista TST"),
    # M6 VT/VA
    ("comp_vt_individual", "funcionario", True, "mensal", "Comprovante VT individual"),
    ("comp_va_solides", "funcionario", True, "mensal", "Comprovante VA Solides"),
    ("comp_vt_va_combinado", "funcionario", False, "mensal", "Comprovante VT+VA combinado"),
    ("recibo_vt_va", "condominio", True, "mensal", "Recibo VT/VA geral"),
    ("relatorio_pedido_va", "condominio", True, "mensal", "Relatório de pedido VA Solides"),
    # M7 RH — eventos de vida
    ("aso", "funcionario", False, "eventual", "ASO (admissional/periódico/demissional)"),
    ("contrato_trabalho", "funcionario", False, "eventual", "Contrato de trabalho CLT"),
    ("ficha_empregado", "funcionario", False, "eventual", "Ficha de registro de empregado"),
    ("aviso_previo_ferias", "funcionario", False, "eventual", "Aviso prévio de férias"),
    ("recibo_ferias", "funcionario", False, "eventual", "Recibo de pagamento de férias"),
    ("rescisao_contrato", "funcionario", False, "eventual", "TRCT - rescisão de contrato"),
    ("comp_rescisao", "funcionario", False, "eventual", "Comprovante de pagamento rescisão"),
    # M8 Pagamentos
    ("comp_salario_individual", "funcionario", True, "mensal", "Comprovante de pagamento de salário"),
]

assert len(KIT_MENSAL) == 32, f"kit_mensal deve ter 32 docs, tem {len(KIT_MENSAL)}"

# Serviços SEM folha CLT: portaria_remota, portaria_autonoma, manutencao_cftv
# Só recebem NFS-e + Boleto (planilha GEDEON confirma)
KIT_SERVICO_SIMPLES: list[tuple[str, str, bool, str, str]] = [
    ("nfse", "condominio", True, "mensal", "NFS-e emitida pela Conecta Mais"),
    ("boleto", "condominio", True, "mensal", "Boleto de cobrança do serviço prestado"),
]


def seed(db_url: str | None = None) -> None:
    url = db_url or os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    if not url:
        print("❌ DATABASE_URL não definida")
        sys.exit(1)

    engine = create_engine(url)
    total = 0
    ja_existe = 0

    with Session(engine) as db:
        # kit_mensal — 32 docs
        for tipo_doc, escopo, obrig, period, desc in KIT_MENSAL:
            row = db.execute(
                text(
                    "SELECT id FROM kit_documental_templates "
                    "WHERE tipo_servico=:ts AND tipo_documento=:td AND escopo=:es"
                ),
                {"ts": "kit_mensal", "td": tipo_doc, "es": escopo},
            ).first()
            if row:
                ja_existe += 1
                continue
            db.execute(
                text(
                    "INSERT INTO kit_documental_templates "
                    "(id, tipo_servico, tipo_documento, escopo, obrigatorio, periodicidade, descricao) "
                    "VALUES (:id, :ts, :td, :es, :ob, :pe, :de)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "ts": "kit_mensal",
                    "td": tipo_doc,
                    "es": escopo,
                    "ob": obrig,
                    "pe": period,
                    "de": desc,
                },
            )
            total += 1
            print(f"  ✅ kit_mensal.{tipo_doc} ({escopo}, {period})")

        # Serviços simples — 2 docs × 3 tipos = 6 rows
        for tipo_servico in ("portaria_remota", "portaria_autonoma", "manutencao_cftv"):
            for tipo_doc, escopo, obrig, period, desc in KIT_SERVICO_SIMPLES:
                row = db.execute(
                    text(
                        "SELECT id FROM kit_documental_templates "
                        "WHERE tipo_servico=:ts AND tipo_documento=:td AND escopo=:es"
                    ),
                    {"ts": tipo_servico, "td": tipo_doc, "es": escopo},
                ).first()
                if row:
                    ja_existe += 1
                    continue
                db.execute(
                    text(
                        "INSERT INTO kit_documental_templates "
                        "(id, tipo_servico, tipo_documento, escopo, obrigatorio, periodicidade, descricao) "
                        "VALUES (:id, :ts, :td, :es, :ob, :pe, :de)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "ts": tipo_servico,
                        "td": tipo_doc,
                        "es": escopo,
                        "ob": obrig,
                        "pe": period,
                        "de": desc,
                    },
                )
                total += 1
                print(f"  ✅ {tipo_servico}.{tipo_doc}")

        # administrativo: SEM KIT (INV-6)
        print("  ⏭️  administrativo: sem template de kit (INV-6 — Jordan aprovou)")

        db.commit()

        total_db = db.execute(text("SELECT COUNT(*) FROM kit_documental_templates")).scalar()

        print(f"\n📊 Seeder concluído: {total} criados, {ja_existe} já existentes")
        print(f"📊 Total kit_documental_templates: {total_db}")
        print("📊 Esperado: 32 + 2 + 2 + 2 = 38 rows")

        # Validação estrutural por tipo_servico
        for ts in ("kit_mensal", "portaria_remota", "portaria_autonoma", "manutencao_cftv"):
            n = db.execute(
                text("SELECT COUNT(*) FROM kit_documental_templates WHERE tipo_servico=:ts"),
                {"ts": ts},
            ).scalar()
            exp = 32 if ts == "kit_mensal" else 2
            status = "✅" if n == exp else "⚠️ "
            print(f"    {status} {ts}: {n} rows (esperado: {exp})")

        if total_db != 38:
            print(f"\n❌ FALHA: total={total_db}, esperado=38 — NÃO commitar")
            sys.exit(1)

        print("\n✅ seed_kit_templates_fase_3_5 APROVADO")


if __name__ == "__main__":
    seed()
