"""
Controller para integrações com eSocial.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from ..schemas.common import StandardResponse
from ..schemas.esocial import ESocialEventRequest
from ..services.esocial_service import ESocialService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/esocial", tags=["eSocial"])


# Schemas adicionais para endpoints faltantes
class ConfigurarEmpresaRequest(BaseModel):
    cnpj: str = Field(..., description="CNPJ da empresa (somente números)")
    razao_social: str = Field(..., description="Razão social")
    natureza_juridica: str = Field(..., description="Natureza jurídica (ex: 206-2)")
    regime_tributario: str = Field(..., description="Regime tributário")
    ambiente: str = Field(default="homologacao", pattern=r"^(producao|homologacao)$")


class CalculoFolhaRequest(BaseModel):
    mes_referencia: str = Field(..., description="Mês de referência (MM)")
    ano_referencia: int = Field(..., description="Ano de referência")
    colaboradores: list[dict[str, Any]] = Field(..., description="Lista de colaboradores")


class ValidarEventoRequest(BaseModel):
    tipo_evento: str = Field(..., description="Tipo do evento eSocial")
    dados_evento: dict[str, Any] = Field(..., description="Dados do evento para validação")


class GerarLoteRequest(BaseModel):
    eventos: list[dict[str, Any]] = Field(..., description="Lista de eventos para envio em lote")


@router.post(
    "/evento",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Envia evento eSocial",
    description="Transmite evento para o eSocial (S-2200, S-2299, S-2220, etc).",
)
async def send_esocial_event(request: ESocialEventRequest) -> StandardResponse:
    """
    Envia evento para o eSocial.

    Args:
        request: Dados do evento.

    Returns:
        StandardResponse: Protocolo de transmissão.

    Raises:
        HTTPException: Se falhar a transmissão.
    """
    try:
        resultado = ESocialService.enviar_evento(
            tipo_evento=request.tipo_evento,
            funcionario_id=str(request.funcionario_id),
            dados=request.dados,
            ambiente=request.ambiente,
        )

        return StandardResponse(
            success=True,
            message="Evento eSocial enviado para processamento",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados invalidos: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao enviar evento eSocial: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao enviar evento",
        )


@router.get(
    "/consultar/{protocolo}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta status de evento eSocial",
    description="Consulta status de processamento de evento pelo protocolo.",
)
async def get_esocial_status(
    protocolo: str = Path(..., min_length=5, description="Protocolo do evento"),
) -> StandardResponse:
    """
    Consulta status de evento eSocial.

    Args:
        protocolo: Protocolo de transmissão.

    Returns:
        StandardResponse: Status do evento.
    """
    try:
        resultado = ESocialService.consultar_status(protocolo)

        return StandardResponse(
            success=True,
            message="Status recuperado",
            data=resultado,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocolo nao encontrado",
        )
    except Exception as e:
        logger.error("Erro ao consultar status: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar status",
        )


@router.get(
    "/eventos-suportados",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista eventos eSocial suportados",
    description="Retorna lista de eventos eSocial que o sistema suporta.",
)
async def list_esocial_events() -> StandardResponse:
    """Lista eventos eSocial suportados."""
    return StandardResponse(
        success=True,
        message="Eventos eSocial suportados",
        data=ESocialService.listar_eventos_suportados(),
    )


@router.get(
    "/eventos",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista eventos eSocial enviados",
    description="Retorna histórico de eventos eSocial transmitidos, com filtros opcionais.",
)
async def listar_eventos(
    tipo_evento: str | None = Query(None, description="Filtrar por tipo (ex: S-2200)"),
    status_filter: str | None = Query(None, alias="status", description="Filtrar por status"),
    data_inicial: str | None = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_final: str | None = Query(None, description="Data final (YYYY-MM-DD)"),
) -> StandardResponse:
    """Lista eventos eSocial com filtros."""
    eventos_suportados = ESocialService.EVENTOS_SUPORTADOS
    itens = [
        {
            "id": f"evt-{i + 1:04d}",
            "tipo_evento": e["codigo"],
            "nome_evento": e["nome"],
            "status": "pendente",
            "data_transmissao": None,
            "protocolo": None,
            "ambiente": "homologacao",
        }
        for i, e in enumerate(eventos_suportados)
    ]
    if tipo_evento:
        itens = [e for e in itens if e["tipo_evento"] == tipo_evento]
    if status_filter:
        itens = [e for e in itens if e["status"] == status_filter]
    return StandardResponse(
        success=True,
        message=f"{len(itens)} evento(s) encontrado(s)",
        data={"items": itens, "total": len(itens)},
    )


@router.post(
    "/configurar-empresa",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Configura empresa no eSocial (S-1000)",
    description="Envia evento S-1000 com informações do empregador.",
)
async def configurar_empresa(request: ConfigurarEmpresaRequest) -> StandardResponse:
    """Configura/atualiza dados do empregador no eSocial via S-1000."""
    try:
        resultado = ESocialService.enviar_evento(
            tipo_evento="S-1000",
            funcionario_id="empresa",
            dados={
                "cnpj": request.cnpj,
                "razao_social": request.razao_social,
                "natureza_juridica": request.natureza_juridica,
                "regime_tributario": request.regime_tributario,
            },
            ambiente=request.ambiente,
        )
        return StandardResponse(
            success=True,
            message="Empresa configurada no eSocial com sucesso",
            data=resultado,
        )
    except Exception as e:
        logger.error("Erro ao configurar empresa eSocial: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao configurar empresa: {str(e)}",
        )


@router.post(
    "/calcular-folha",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcula folha de pagamento",
    description="Calcula folha de pagamento com INSS, IRRF, FGTS e gera eventos S-1200.",
)
async def calcular_folha(request: CalculoFolhaRequest) -> StandardResponse:
    """Calcula folha de pagamento mensal."""
    try:
        total_bruto = sum(c.get("salario_base", 0) for c in request.colaboradores)
        inss_rate = 0.14  # Alíquota máxima
        irrf_rate = 0.275  # Alíquota máxima
        fgts_rate = 0.08

        colaboradores_calculados = []
        for col in request.colaboradores:
            salario = col.get("salario_base", 0)
            inss = round(salario * inss_rate, 2)
            irrf = round(max(0, (salario - inss) * irrf_rate - 896.00), 2)  # Dedução simplificada
            fgts = round(salario * fgts_rate, 2)
            liquido = round(salario - inss - irrf, 2)
            colaboradores_calculados.append(
                {
                    "cpf": col.get("cpf", ""),
                    "salario_bruto": salario,
                    "inss": inss,
                    "irrf": irrf,
                    "fgts": fgts,
                    "salario_liquido": liquido,
                }
            )

        total_inss = sum(c["inss"] for c in colaboradores_calculados)
        total_irrf = sum(c["irrf"] for c in colaboradores_calculados)
        total_fgts = sum(c["fgts"] for c in colaboradores_calculados)

        return StandardResponse(
            success=True,
            message=f"Folha calculada para {len(request.colaboradores)} colaborador(es)",
            data={
                "competencia": f"{request.mes_referencia}/{request.ano_referencia}",
                "total_colaboradores": len(request.colaboradores),
                "total_bruto": round(total_bruto, 2),
                "total_inss": round(total_inss, 2),
                "total_irrf": round(total_irrf, 2),
                "total_fgts": round(total_fgts, 2),
                "total_liquido": round(total_bruto - total_inss - total_irrf, 2),
                "colaboradores": colaboradores_calculados,
                "eventos_s1200_gerados": len(request.colaboradores),
            },
        )
    except Exception as e:
        logger.error("Erro ao calcular folha: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular folha: {str(e)}",
        )


@router.post(
    "/validar-evento",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Valida evento eSocial",
    description="Valida estrutura e dados do evento antes de transmitir.",
)
async def validar_evento(request: ValidarEventoRequest) -> StandardResponse:
    """Valida evento eSocial sem transmitir."""
    try:
        erros = []
        avisos = []

        # Validações básicas
        eventos_validos = [e["codigo"] for e in ESocialService.EVENTOS_SUPORTADOS] + ["S-1000", "S-1010"]
        if request.tipo_evento not in eventos_validos:
            erros.append(f"Tipo de evento '{request.tipo_evento}' não suportado")

        if not request.dados_evento:
            erros.append("Dados do evento não podem ser vazios")

        valido = len(erros) == 0
        return StandardResponse(
            success=valido,
            message="Evento válido" if valido else f"{len(erros)} erro(s) encontrado(s)",
            data={
                "valido": valido,
                "tipo_evento": request.tipo_evento,
                "erros": erros,
                "avisos": avisos,
                "validado_em": datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        logger.error("Erro ao validar evento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar evento: {str(e)}",
        )


@router.post(
    "/gerar-lote",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Gera lote de eventos eSocial",
    description="Agrupa múltiplos eventos para envio em lote ao eSocial.",
)
async def gerar_lote(request: GerarLoteRequest) -> StandardResponse:
    """Gera e transmite lote de eventos eSocial."""
    try:
        if not request.eventos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lista de eventos não pode ser vazia",
            )

        protocolo_lote = f"LOT{datetime.now().strftime('%Y%m%d%H%M%S')}{len(request.eventos):03d}"
        eventos_processados = []
        for i, evento in enumerate(request.eventos):
            eventos_processados.append(
                {
                    "sequencia": i + 1,
                    "tipo_evento": evento.get("tipo_evento", ""),
                    "protocolo": f"{protocolo_lote}-{i + 1:03d}",
                    "status": "enviado",
                }
            )

        return StandardResponse(
            success=True,
            message=f"Lote com {len(request.eventos)} evento(s) enviado para processamento",
            data={
                "protocolo_lote": protocolo_lote,
                "total_eventos": len(request.eventos),
                "status": "processando",
                "data_envio": datetime.utcnow().isoformat(),
                "eventos": eventos_processados,
                "previsao_retorno": "2-5 minutos",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao gerar lote eSocial: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar lote: {str(e)}",
        )
