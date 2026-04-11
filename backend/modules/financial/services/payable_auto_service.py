"""
Payable Auto Service
Cria contas a pagar automaticamente a partir de:
- NFS-e recebidas (nfse_entrada)
- NF-e de compra (nfe_entradas)
Vincula nota fiscal → conta a pagar → transação bancária
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

CONDOMINIO_ID = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


async def _get_or_create_supplier(
    db: AsyncSession,
    cnpj: str,
    nome: str,
) -> UUID | None:
    """Busca ou cria fornecedor; retorna UUID do supplier ou None em caso de erro."""
    cnpj_clean = "".join(c for c in (cnpj or "") if c.isdigit())
    if not cnpj_clean:
        return None

    await db.execute(
        text(
            "INSERT INTO suppliers (name, cpf_cnpj, condominio_id, status, created_at, updated_at) "
            "VALUES (:nome, :cnpj, :cond_id, 'ativo', NOW(), NOW()) "
            "ON CONFLICT (cpf_cnpj, condominio_id) DO NOTHING"
        ),
        {"nome": nome[:200], "cnpj": cnpj_clean, "cond_id": str(CONDOMINIO_ID)},
    )

    row = (
        await db.execute(
            text("SELECT id FROM suppliers WHERE cpf_cnpj = :cnpj AND condominio_id = :cond_id LIMIT 1"),
            {"cnpj": cnpj_clean, "cond_id": str(CONDOMINIO_ID)},
        )
    ).fetchone()

    return UUID(str(row[0])) if row else None


async def criar_payable_de_nfse_entrada(
    db: AsyncSession,
    nfse_entrada_id: str | None = None,
) -> dict:
    """
    Cria conta a pagar para NFS-e recebida não processada.
    Se nfse_entrada_id = None, processa todas pendentes.
    """
    where_extra = "AND id = :nfse_filter_id" if nfse_entrada_id else ""
    params: dict = {}
    if nfse_entrada_id:
        params["nfse_filter_id"] = nfse_entrada_id

    rows = (
        await db.execute(
            text(
                "SELECT id, prestador_cnpj, prestador_nome, valor_servico, "
                "valor_liquido, data_emissao, numero_nfse, chave_acesso, descricao_servico "
                "FROM nfse_entrada "
                f"WHERE payable_id IS NULL AND valor_servico > 0 {where_extra} "
                "ORDER BY data_emissao"
            ),
            params,
        )
    ).fetchall()

    criados = 0
    erros_list: list[str] = []
    detalhes: list[dict] = []

    for r in rows:
        nfse_id = r[0]
        prestador_cnpj = r[1] or ""
        prestador_nome = r[2] or "Fornecedor NFS-e"
        valor_servico = Decimal(str(r[3] or 0))
        data_emissao = r[5] or date.today()
        numero_nfse = r[6] or ""
        chave_acesso = r[7] or ""
        descricao_servico = r[8] or ""

        try:
            supplier_id = await _get_or_create_supplier(db, prestador_cnpj, prestador_nome)

            descricao = descricao_servico or (
                f"NFS-e {numero_nfse} - {prestador_nome}" if numero_nfse else f"NFS-e — {prestador_nome}"
            )
            due_date = (
                data_emissao + timedelta(days=30)
                if isinstance(data_emissao, date)
                else date.today() + timedelta(days=30)
            )
            issue_d = data_emissao if isinstance(data_emissao, date) else date.today()

            row = (
                await db.execute(
                    text(
                        "INSERT INTO payable_accounts "
                        "(condominio_id, supplier_id, description, gross_value, net_value, "
                        " issue_date, due_date, status, fiscal_document_type, fiscal_document_key, "
                        " nfse_entrada_id, nfse_numero, "
                        " nota_fiscal_id, nota_fiscal_tipo, nota_fiscal_numero, nota_fiscal_chave, "
                        " fornecedor_cnpj, fornecedor_nome, origem, categoria, "
                        " created_by, created_at, updated_at) "
                        "VALUES "
                        "(:cond_id, :sup_id, :desc, :gross, :gross, "
                        " :issue_d, :due_d, 'pendente', 'NFS-e', :fdk, "
                        " :nfse_uuid, :nfse_num, "
                        " :nfse_uuid_text, 'nfse', :nfse_num, :fdk, "
                        " :prest_cnpj, :prest_nome, 'nfse_entrada', 'servico', "
                        " :created_by, NOW(), NOW()) "
                        "RETURNING id"
                    ),
                    {
                        "cond_id": str(CONDOMINIO_ID),
                        "sup_id": str(supplier_id) if supplier_id else None,
                        "desc": descricao[:500],
                        "gross": float(valor_servico),
                        "issue_d": issue_d,
                        "due_d": due_date,
                        "fdk": chave_acesso[:50] if chave_acesso else None,
                        "nfse_uuid": str(nfse_id),
                        "nfse_uuid_text": str(nfse_id),
                        "nfse_num": numero_nfse[:20] if numero_nfse else None,
                        "prest_cnpj": prestador_cnpj[:20] if prestador_cnpj else None,
                        "prest_nome": prestador_nome[:200],
                        "created_by": str(SYSTEM_USER_ID),
                    },
                )
            ).fetchone()
            payable_id = row[0]

            await db.execute(
                text("UPDATE nfse_entrada SET payable_id = :pay_id, status = 'processada' WHERE id = :nfse_id"),
                {"pay_id": str(payable_id), "nfse_id": str(nfse_id)},
            )
            await db.commit()

            criados += 1
            detalhes.append(
                {
                    "nfse_id": str(nfse_id),
                    "payable_id": str(payable_id),
                    "prestador": prestador_nome,
                    "valor": float(valor_servico),
                    "vencimento": str(due_date),
                    "status": "criado",
                }
            )
            logger.info(f"Payable {payable_id} criado para NFS-e {nfse_id} ({prestador_nome})")

        except Exception as exc:
            await db.rollback()
            erros_list.append(f"{prestador_nome}: {exc}")
            detalhes.append(
                {
                    "nfse_id": str(nfse_id),
                    "prestador": prestador_nome,
                    "valor": float(valor_servico),
                    "status": "erro",
                    "erro": str(exc),
                }
            )
            logger.error(f"Erro ao criar payable para NFS-e {nfse_id}: {exc}")

    return {
        "processadas": len(rows),
        "criados": criados,
        "erros": len(erros_list),
        "detalhes_erros": erros_list[:3],
        "detalhes": detalhes,
    }


async def criar_payable_de_nfe_entrada(
    db: AsyncSession,
    nfe_entrada_id: str | None = None,
) -> dict:
    """
    Cria conta a pagar para NF-e de compra não processada.
    Se nfe_entrada_id = None, processa todas pendentes.
    """
    where_extra = "AND id = :nfe_filter_id" if nfe_entrada_id else ""
    params: dict = {}
    if nfe_entrada_id:
        params["nfe_filter_id"] = int(nfe_entrada_id)

    rows = (
        await db.execute(
            text(
                "SELECT id, emitente_cnpj, emitente_nome, valor_total, "
                "data_emissao, numero, chave_acesso "
                "FROM nfe_entradas "
                f"WHERE (processada IS NULL OR processada = false) AND valor_total > 0 {where_extra} "
                "ORDER BY data_emissao"
            ),
            params,
        )
    ).fetchall()

    criados = 0
    erros_list: list[str] = []
    detalhes: list[dict] = []

    for r in rows:
        nfe_id = r[0]
        emitente_cnpj = r[1] or ""
        emitente_nome = r[2] or "Fornecedor NF-e"
        valor_total = Decimal(str(r[3] or 0))
        data_emissao = r[4] or date.today()
        numero = r[5] or ""
        chave_acesso = r[6] or ""

        try:
            supplier_id = await _get_or_create_supplier(db, emitente_cnpj, emitente_nome)

            descricao = f"NF-e {numero} - {emitente_nome}" if numero else f"NF-e — {emitente_nome}"
            due_date = (
                data_emissao + timedelta(days=30)
                if isinstance(data_emissao, date)
                else date.today() + timedelta(days=30)
            )
            issue_d = data_emissao if isinstance(data_emissao, date) else date.today()

            row = (
                await db.execute(
                    text(
                        "INSERT INTO payable_accounts "
                        "(condominio_id, supplier_id, description, gross_value, net_value, "
                        " issue_date, due_date, status, fiscal_document_type, fiscal_document_key, "
                        " nota_fiscal_id, nota_fiscal_tipo, nota_fiscal_numero, nota_fiscal_chave, "
                        " fornecedor_cnpj, fornecedor_nome, origem, categoria, "
                        " created_by, created_at, updated_at) "
                        "VALUES "
                        "(:cond_id, :sup_id, :desc, :gross, :gross, "
                        " :issue_d, :due_d, 'pendente', 'NF-e', :fdk, "
                        " :nfe_id_text, 'nfe', :numero, :fdk, "
                        " :emit_cnpj, :emit_nome, 'nfe_entrada', 'material', "
                        " :created_by, NOW(), NOW()) "
                        "RETURNING id"
                    ),
                    {
                        "cond_id": str(CONDOMINIO_ID),
                        "sup_id": str(supplier_id) if supplier_id else None,
                        "desc": descricao[:500],
                        "gross": float(valor_total),
                        "issue_d": issue_d,
                        "due_d": due_date,
                        "fdk": chave_acesso[:50] if chave_acesso else None,
                        "nfe_id_text": str(nfe_id),
                        "numero": str(numero)[:20] if numero else None,
                        "emit_cnpj": emitente_cnpj[:20] if emitente_cnpj else None,
                        "emit_nome": emitente_nome[:200],
                        "created_by": str(SYSTEM_USER_ID),
                    },
                )
            ).fetchone()
            payable_id = row[0]

            await db.execute(
                text("UPDATE nfe_entradas SET processada = true WHERE id = :nfe_id"),
                {"nfe_id": nfe_id},
            )
            await db.commit()

            criados += 1
            detalhes.append(
                {
                    "nfe_id": str(nfe_id),
                    "payable_id": str(payable_id),
                    "emitente": emitente_nome,
                    "valor": float(valor_total),
                    "vencimento": str(due_date),
                    "status": "criado",
                }
            )
            logger.info(f"Payable {payable_id} criado para NF-e {nfe_id} ({emitente_nome})")

        except Exception as exc:
            await db.rollback()
            erros_list.append(f"{emitente_nome}: {exc}")
            detalhes.append(
                {
                    "nfe_id": str(nfe_id),
                    "emitente": emitente_nome,
                    "valor": float(valor_total),
                    "status": "erro",
                    "erro": str(exc),
                }
            )
            logger.error(f"Erro ao criar payable para NF-e {nfe_id}: {exc}")

    return {
        "processadas": len(rows),
        "criados": criados,
        "erros": len(erros_list),
        "detalhes_erros": erros_list[:3],
        "detalhes": detalhes,
    }


async def processar_todas_pendentes(db: AsyncSession) -> dict:
    """Processa todas as notas fiscais sem payable vinculado (NFS-e + NF-e)."""
    r1 = await criar_payable_de_nfse_entrada(db)
    r2 = await criar_payable_de_nfe_entrada(db)
    return {
        "nfse_entrada": r1,
        "nfe_entrada": r2,
        "total_criados": r1["criados"] + r2["criados"],
    }
