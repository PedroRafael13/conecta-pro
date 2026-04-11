"""Service para criação automática de contas a pagar a partir de NFS-e/NF-e."""

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

    # Tenta inserir; se já existe (unique constraint), ignora
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


async def auto_criar_payables_nfse(db: AsyncSession) -> dict:
    """Cria contas a pagar para todas as NFS-e recebidas sem payable vinculado.

    Returns:
        dict com criadas, erros, total_valor
    """
    rows = (
        await db.execute(
            text(
                "SELECT id, prestador_cnpj, prestador_nome, valor_servico, "
                "valor_liquido, data_emissao, numero_nfse, chave_acesso "
                "FROM nfse_entrada "
                "WHERE payable_id IS NULL AND valor_servico > 0 "
                "ORDER BY data_emissao"
            )
        )
    ).fetchall()

    if not rows:
        return {"criadas": 0, "erros": 0, "total_valor": 0.0, "detalhes": []}

    criadas = 0
    erros = 0
    total_valor = Decimal("0")
    detalhes: list[dict] = []

    for r in rows:
        nfse_id = r[0]
        prestador_cnpj = r[1] or ""
        prestador_nome = r[2] or "Fornecedor NFS-e"
        valor_servico = Decimal(str(r[3] or 0))
        data_emissao = r[5] or date.today()
        numero_nfse = r[6] or ""
        chave_acesso = r[7] or ""

        try:
            supplier_id = await _get_or_create_supplier(db, prestador_cnpj, prestador_nome)

            desc_nfse = f"NFS-e {numero_nfse} — {prestador_nome}" if numero_nfse else f"NFS-e — {prestador_nome}"
            due_date = (
                data_emissao + timedelta(days=30)
                if isinstance(data_emissao, date)
                else date.today() + timedelta(days=30)
            )
            issue_d = data_emissao if isinstance(data_emissao, date) else date.today()
            notes_val = (
                f"Criado automaticamente via importação NFS-e. Chave: {chave_acesso}"
                if chave_acesso
                else "Criado automaticamente via importação NFS-e."
            )

            # Insert direto via SQL para evitar erros de FK quebrada no ORM
            row = (
                await db.execute(
                    text(
                        "INSERT INTO payable_accounts "
                        "(condominio_id, supplier_id, description, gross_value, net_value, "
                        " issue_date, due_date, status, fiscal_document_type, fiscal_document_key, "
                        " nfse_entrada_id, nfse_numero, notes, created_by, created_at, updated_at) "
                        "VALUES "
                        "(:cond_id, :sup_id, :desc, :gross, :gross, "
                        " :issue_d, :due_d, 'pendente', 'NFS-e', :fdk, "
                        " :nfse_id, :nfse_num, :notes, :created_by, NOW(), NOW()) "
                        "RETURNING id"
                    ),
                    {
                        "cond_id": str(CONDOMINIO_ID),
                        "sup_id": str(supplier_id) if supplier_id else None,
                        "desc": desc_nfse[:500],
                        "gross": float(valor_servico),
                        "issue_d": issue_d,
                        "due_d": due_date,
                        "fdk": chave_acesso[:50] if chave_acesso else None,
                        "nfse_id": str(nfse_id),
                        "nfse_num": numero_nfse[:50] if numero_nfse else None,
                        "notes": notes_val,
                        "created_by": str(SYSTEM_USER_ID),
                    },
                )
            ).fetchone()
            payable_id = row[0]

            # Marca nfse_entrada como processada com o payable_id
            await db.execute(
                text("UPDATE nfse_entrada SET payable_id = :pay_id, status = 'processada' WHERE id = :nfse_id"),
                {"pay_id": str(payable_id), "nfse_id": str(nfse_id)},
            )

            await db.commit()

            criadas += 1
            total_valor += valor_servico
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
            erros += 1
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
        "criadas": criadas,
        "erros": erros,
        "total_valor": float(total_valor),
        "detalhes": detalhes,
    }
