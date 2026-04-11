"""Controller de Justificativas — Saídas Sem Nota Fiscal (Lucro Real)"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.auth.dependencies import get_current_user

router = APIRouter(prefix="/justificativa", tags=["Justificativas Fiscais"])


class JustificativaRequest(BaseModel):
    transacao_id: str
    categoria: str
    descricao: str
    responsavel: str | None = "Jordan Jesus"


@router.post(
    "/registrar",
    summary="Registrar justificativa para saída sem nota fiscal",
)
async def registrar_justificativa(
    req: JustificativaRequest,
    _user=Depends(get_current_user),
):
    """
    Registra justificativa para transação bancária sem nota fiscal.
    Obrigatório para conformidade Lucro Real.

    Categorias: salario, adiantamento, reembolso, taxa_bancaria,
    imposto, servico_sem_nf, transferencia_interna, outros
    """
    from modules.financial.services.justificativa_service import (
        registrar_justificativa as _svc,
    )

    resultado = _svc(req.transacao_id, req.categoria, req.descricao, req.responsavel)
    if "erro" in resultado:
        raise HTTPException(status_code=400, detail=resultado["erro"])
    return resultado


@router.get(
    "/pendentes",
    summary="Listar saídas sem justificativa",
)
async def listar_pendentes(
    mes: int | None = None,
    ano: int | None = None,
    _user=Depends(get_current_user),
):
    """Lista transações de saída que ainda precisam de justificativa."""
    from modules.financial.services.justificativa_service import (
        listar_sem_justificativa,
    )

    return listar_sem_justificativa(mes, ano)


@router.get(
    "/verificar-fechamento/{mes}/{ano}",
    summary="Verificar se período pode ser fechado",
)
async def verificar_fechamento(
    mes: int,
    ano: int,
    _user=Depends(get_current_user),
):
    """
    Verifica se há saídas sem justificativa no período.
    Bloqueia fechamento contábil se houver pendências.
    Dispara alerta Telegram se bloqueado.
    """
    from modules.financial.services.justificativa_service import (
        verificar_fechamento_periodo,
    )

    return verificar_fechamento_periodo(mes, ano)


@router.post(
    "/alertar",
    summary="Disparar alerta Telegram sobre pendências",
)
async def alertar_pendentes(_user=Depends(get_current_user)):
    """Envia alerta Telegram sobre saídas sem justificativa."""
    from modules.financial.services.justificativa_service import alertar_pendentes

    return alertar_pendentes()


@router.get(
    "/categorias",
    summary="Listar categorias válidas de justificativa",
)
async def categorias():
    """Retorna categorias válidas para justificativa de saída sem nota."""
    return {
        "categorias": [
            {"id": "salario", "desc": "Pagamento de salário ou pró-labore"},
            {"id": "adiantamento", "desc": "Adiantamento a funcionário"},
            {"id": "reembolso", "desc": "Reembolso de despesas"},
            {"id": "taxa_bancaria", "desc": "Tarifas e taxas bancárias"},
            {"id": "imposto", "desc": "Pagamento de impostos e guias"},
            {"id": "servico_sem_nf", "desc": "Serviço sem obrigação fiscal"},
            {"id": "transferencia_interna", "desc": "Movimentação entre contas próprias"},
            {"id": "outros", "desc": "Outros (requer descrição detalhada)"},
        ]
    }
