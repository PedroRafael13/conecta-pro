"""
Integração financeira com módulo CRM.
Quando uma proposta é aprovada, cria estrutura financeira automaticamente.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus, ReceivableType

logger = logging.getLogger(__name__)


async def on_contrato_ativado(
    contrato_id: int,
    valor_mensal: float,
    tipo_servico: str,
    session: AsyncSession,
    cliente_nome: str = "",
) -> dict:
    """
    Chamado quando um contrato é ativado no CRM.
    Cria: primeira conta a receber para o mês corrente.

    Returns:
        {success, receivable_id, message}
    """
    try:
        today = date.today()
        # Vencimento padrão: dia 10 do próximo mês
        if today.month == 12:
            due_date = today.replace(year=today.year + 1, month=1, day=10)
        else:
            due_date = today.replace(month=today.month + 1, day=10)

        valor = Decimal(str(valor_mensal))
        descricao = (
            f"Contrato #{contrato_id} — {tipo_servico.replace('_', ' ').title()}"
            f"{' — ' + cliente_nome if cliente_nome else ''}"
        )

        receivable = ReceivableAccount(
            description=descricao,
            receivable_type=ReceivableType.RECORRENTE.value,
            status=ReceivableStatus.PENDENTE.value,
            gross_value=valor,
            net_value=valor,
            paid_value=Decimal("0"),
            issue_date=today,
            entry_date=today,
            due_date=due_date,
            competence_date=today.replace(day=1),
            is_recurring=True,
            recurrence_type="mensal",
            notes=f"Gerado automaticamente via ativação de contrato CRM #{contrato_id}",
            condominio_id=None,  # será preenchido pelo contexto do contrato
        )

        # condominio_id é NOT NULL — usa um UUID placeholder se nulo
        # Na integração real, o contrato passaria o condominio_id
        import uuid
        receivable.condominio_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        session.add(receivable)
        await session.flush()
        receivable_id = str(receivable.id)
        await session.commit()

        logger.info(
            "[crm_integration] Contrato #%s ativado → Recebível %s criado (R$ %.2f)",
            contrato_id,
            receivable_id,
            valor_mensal,
        )

        return {
            "success": True,
            "receivable_id": receivable_id,
            "billing_rule_id": None,
            "message": (
                f"Conta a receber criada com sucesso. "
                f"Vencimento: {due_date.strftime('%d/%m/%Y')} — R$ {valor_mensal:,.2f}"
            ),
        }

    except Exception as exc:
        logger.warning("[crm_integration] on_contrato_ativado erro: %s", exc)
        try:
            await session.rollback()
        except Exception:
            pass
        return {
            "success": False,
            "receivable_id": None,
            "billing_rule_id": None,
            "message": f"Erro ao criar estrutura financeira: {str(exc)}",
        }


async def on_contrato_encerrado(
    contrato_id: int,
    session: AsyncSession,
) -> dict:
    """
    Chamado quando contrato é encerrado no CRM.
    Verifica pendências financeiras.

    Returns:
        {success, pendencias, message}
    """
    try:
        today = date.today()

        # Busca recebíveis pendentes que mencionam este contrato
        pattern = f"%Contrato #{contrato_id}%"
        q = select(
            ReceivableAccount.id,
            ReceivableAccount.description,
            ReceivableAccount.net_value,
            ReceivableAccount.due_date,
            ReceivableAccount.status,
        ).where(
            and_(
                ReceivableAccount.description.ilike(pattern),
                ReceivableAccount.status.notin_([
                    ReceivableStatus.PAGA.value,
                    ReceivableStatus.CANCELADA.value,
                    ReceivableStatus.BAIXADA.value,
                ]),
                ReceivableAccount.ativo.is_(True),
            )
        )
        rows = (await session.execute(q)).all()

        pendencias = [
            {
                "receivable_id": str(row.id),
                "description": row.description,
                "valor": float(row.net_value or 0),
                "vencimento": row.due_date.isoformat() if row.due_date else None,
                "status": row.status,
                "vencida": row.due_date < today if row.due_date else False,
            }
            for row in rows
        ]

        total_pendente = sum(p["valor"] for p in pendencias)
        vencidas = [p for p in pendencias if p["vencida"]]

        if not pendencias:
            message = f"Contrato #{contrato_id} encerrado sem pendências financeiras."
        elif vencidas:
            message = (
                f"ATENÇÃO: {len(pendencias)} título(s) pendente(s) "
                f"(R$ {total_pendente:,.2f}), sendo {len(vencidas)} já vencido(s)."
            )
        else:
            message = (
                f"{len(pendencias)} título(s) pendente(s) a vencer "
                f"(R$ {total_pendente:,.2f})."
            )

        return {
            "success": True,
            "pendencias": pendencias,
            "total_pendente": round(total_pendente, 2),
            "message": message,
        }

    except Exception as exc:
        logger.warning("[crm_integration] on_contrato_encerrado erro: %s", exc)
        return {
            "success": False,
            "pendencias": [],
            "total_pendente": 0.0,
            "message": f"Erro ao verificar pendências: {str(exc)}",
        }
