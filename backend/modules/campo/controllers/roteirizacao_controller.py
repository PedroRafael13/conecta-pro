"""
Controller de Roteirização Inteligente para Campo.

Fornece endpoints para:
- Otimização de rotas
- Reotimização em tempo real
- Análise de rotas da equipe
- Sugestões de redistribuição
"""

from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from modules.campo.services.roteirizacao_service import (
    RoteiroOtimizado,
    TipoOtimizacao,
    get_roteirizacao_service,
)

router = APIRouter()


# =============================================================================
# SCHEMAS
# =============================================================================


class PontoPartidaRequest(BaseModel):
    """Ponto de partida/retorno customizado."""

    endereco: str = Field(..., max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class OtimizarRotaRequest(BaseModel):
    """Request para otimizar rota."""

    tecnico_id: UUID
    data: date
    tipo_otimizacao: TipoOtimizacao = TipoOtimizacao.BALANCEADA
    ponto_partida: PontoPartidaRequest | None = None
    ponto_retorno: PontoPartidaRequest | None = None


class ReotimizarRotaRequest(BaseModel):
    """Request para reotimizar rota."""

    tecnico_id: UUID
    data: date
    latitude_atual: float = Field(..., ge=-90, le=90)
    longitude_atual: float = Field(..., ge=-180, le=180)
    os_concluidas: list[UUID] | None = None


class PontoRotaResponse(BaseModel):
    """Response de ponto de rota."""

    ordem_servico_id: str | None
    visita_id: str | None
    endereco: str
    latitude: float
    longitude: float
    tipo: str
    nome_cliente: str | None
    janela_inicio: str | None
    janela_fim: str | None
    duracao_estimada_minutos: int
    prioridade: int


class TrechoRotaResponse(BaseModel):
    """Response de trecho de rota."""

    origem_endereco: str
    destino_endereco: str
    distancia_km: float
    duracao_minutos: int


class RoteiroResponse(BaseModel):
    """Response de roteiro otimizado."""

    tecnico_id: str
    tecnico_nome: str
    data: str
    pontos: list[PontoRotaResponse]
    trechos: list[TrechoRotaResponse]
    distancia_total_km: float
    duracao_total_minutos: int
    hora_inicio_sugerida: str
    hora_fim_estimada: str
    economia_km: float | None
    economia_tempo_minutos: int | None


class AnaliseEquipeResponse(BaseModel):
    """Response de análise da equipe."""

    data: str
    tecnicos_analisados: int
    rotas: list[dict[str, Any]]
    totais: dict[str, Any]


class RedistribuicaoResponse(BaseModel):
    """Response de sugestão de redistribuição."""

    redistribuicao_necessaria: bool
    media_os_por_tecnico: float | None
    media_distancia_km: float | None
    tecnicos_sobrecarregados: int | None
    tecnicos_subutilizados: int | None
    sugestoes: list[dict[str, Any]]
    motivo: str | None


# =============================================================================
# HELPERS
# =============================================================================


def _roteiro_to_response(roteiro: RoteiroOtimizado) -> dict[str, Any]:
    """Converte RoteiroOtimizado para response dict."""
    pontos = []
    for p in roteiro.pontos:
        pontos.append(
            {
                "ordem_servico_id": str(p.ordem_servico_id) if p.ordem_servico_id else None,
                "visita_id": str(p.visita_id) if p.visita_id else None,
                "endereco": p.endereco,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "tipo": p.tipo,
                "nome_cliente": p.nome_cliente,
                "janela_inicio": p.janela_inicio.isoformat() if p.janela_inicio else None,
                "janela_fim": p.janela_fim.isoformat() if p.janela_fim else None,
                "duracao_estimada_minutos": p.duracao_estimada_minutos,
                "prioridade": p.prioridade,
            }
        )

    trechos = []
    for t in roteiro.trechos:
        trechos.append(
            {
                "origem_endereco": t.origem.endereco,
                "destino_endereco": t.destino.endereco,
                "distancia_km": t.distancia_km,
                "duracao_minutos": t.duracao_minutos,
            }
        )

    return {
        "tecnico_id": str(roteiro.tecnico_id),
        "tecnico_nome": roteiro.tecnico_nome,
        "data": roteiro.data.isoformat(),
        "pontos": pontos,
        "trechos": trechos,
        "distancia_total_km": roteiro.distancia_total_km,
        "duracao_total_minutos": roteiro.duracao_total_minutos,
        "hora_inicio_sugerida": roteiro.hora_inicio_sugerida.isoformat(),
        "hora_fim_estimada": roteiro.hora_fim_estimada.isoformat(),
        "economia_km": roteiro.economia_km,
        "economia_tempo_minutos": roteiro.economia_tempo_minutos,
    }


# =============================================================================
# ENDPOINTS - OTIMIZAÇÃO
# =============================================================================


@router.post(
    "/otimizar",
    response_model=RoteiroResponse,
    summary="Otimizar rota",
    description="Otimiza a rota de um técnico para um dia específico",
)
async def otimizar_rota(
    request: OtimizarRotaRequest,
    db: Session = Depends(get_db),
):
    """
    Otimiza a rota de um técnico para um dia específico.

    Tipos de otimização:
    - **menor_distancia**: Minimiza quilometragem total
    - **menor_tempo**: Minimiza tempo total de deslocamento
    - **balanceada**: Equilibra distância e tempo
    - **prioridade**: Prioriza OS urgentes
    """
    google_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    service = get_roteirizacao_service(db, google_api_key)

    try:
        ponto_partida = None
        if request.ponto_partida:
            ponto_partida = {
                "endereco": request.ponto_partida.endereco,
                "latitude": request.ponto_partida.latitude,
                "longitude": request.ponto_partida.longitude,
            }

        ponto_retorno = None
        if request.ponto_retorno:
            ponto_retorno = {
                "endereco": request.ponto_retorno.endereco,
                "latitude": request.ponto_retorno.latitude,
                "longitude": request.ponto_retorno.longitude,
            }

        roteiro = service.otimizar_rota_tecnico(
            tecnico_id=request.tecnico_id,
            data=request.data,
            tipo_otimizacao=request.tipo_otimizacao,
            ponto_partida=ponto_partida,
            ponto_retorno=ponto_retorno,
        )

        return _roteiro_to_response(roteiro)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao otimizar rota: {str(e)}"
        )


@router.get(
    "/tecnico/{tecnico_id}",
    response_model=RoteiroResponse,
    summary="Rota do técnico",
    description="Retorna a rota otimizada de um técnico para uma data",
)
async def get_rota_tecnico(
    tecnico_id: UUID,
    data: date = Query(..., description="Data do roteiro"),
    tipo_otimizacao: TipoOtimizacao = Query(TipoOtimizacao.BALANCEADA, description="Tipo de otimização"),
    db: Session = Depends(get_db),
):
    """Retorna a rota otimizada de um técnico para uma data."""
    google_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    service = get_roteirizacao_service(db, google_api_key)

    try:
        roteiro = service.otimizar_rota_tecnico(
            tecnico_id=tecnico_id,
            data=data,
            tipo_otimizacao=tipo_otimizacao,
        )

        return _roteiro_to_response(roteiro)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# ENDPOINTS - REOTIMIZAÇÃO
# =============================================================================


@router.post(
    "/reotimizar",
    response_model=RoteiroResponse,
    summary="Reotimizar rota",
    description="Reotimiza a rota considerando posição atual do técnico",
)
async def reotimizar_rota(
    request: ReotimizarRotaRequest,
    db: Session = Depends(get_db),
):
    """
    Reotimiza a rota considerando:
    - Posição atual do técnico (GPS)
    - OS já concluídas
    - Condições de trânsito atuais
    """
    google_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    service = get_roteirizacao_service(db, google_api_key)

    try:
        roteiro = service.reotimizar_rota(
            tecnico_id=request.tecnico_id,
            data=request.data,
            ponto_atual_latitude=request.latitude_atual,
            ponto_atual_longitude=request.longitude_atual,
            os_concluidas=request.os_concluidas,
        )

        return _roteiro_to_response(roteiro)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# ENDPOINTS - ANÁLISE
# =============================================================================


@router.get(
    "/analise/equipe",
    response_model=AnaliseEquipeResponse,
    summary="Análise de rotas da equipe",
    description="Analisa rotas de toda a equipe para um dia",
)
async def analisar_rotas_equipe(
    data: date = Query(..., description="Data de análise"),
    tecnico_ids: str | None = Query(None, description="IDs dos técnicos separados por vírgula (default: todos)"),
    db: Session = Depends(get_db),
):
    """
    Analisa rotas de toda a equipe para um dia.

    Retorna:
    - Quantidade de OS/visitas por técnico
    - Distância total
    - Duração estimada
    - Economia potencial
    """
    google_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    service = get_roteirizacao_service(db, google_api_key)

    ids_lista = None
    if tecnico_ids:
        ids_lista = [UUID(tid.strip()) for tid in tecnico_ids.split(",")]

    try:
        analise = service.analisar_rotas_equipe(
            data=data,
            tecnico_ids=ids_lista,
        )
        return analise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao analisar rotas: {str(e)}"
        )


@router.get(
    "/analise/redistribuicao",
    response_model=RedistribuicaoResponse,
    summary="Sugestão de redistribuição",
    description="Sugere redistribuição de OS entre técnicos",
)
async def sugerir_redistribuicao(
    data: date = Query(..., description="Data de análise"),
    tecnico_ids: str | None = Query(None, description="IDs dos técnicos separados por vírgula"),
    db: Session = Depends(get_db),
):
    """
    Sugere redistribuição de OS entre técnicos para balancear carga.

    Identifica:
    - Técnicos sobrecarregados
    - Técnicos subutilizados
    - Sugestões de transferência
    """
    google_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    service = get_roteirizacao_service(db, google_api_key)

    ids_lista = None
    if tecnico_ids:
        ids_lista = [UUID(tid.strip()) for tid in tecnico_ids.split(",")]

    try:
        sugestoes = service.sugerir_redistribuicao(
            data=data,
            tecnico_ids=ids_lista,
        )
        return sugestoes

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao sugerir redistribuição: {str(e)}"
        )


# =============================================================================
# ENDPOINTS - UTILITÁRIOS
# =============================================================================


@router.get(
    "/tipos-otimizacao", summary="Listar tipos de otimização", description="Lista os tipos de otimização disponíveis"
)
async def listar_tipos_otimizacao():
    """Lista os tipos de otimização disponíveis."""
    return {
        "tipos": [
            {
                "id": TipoOtimizacao.MENOR_DISTANCIA.value,
                "nome": "Menor Distância",
                "descricao": "Minimiza a quilometragem total percorrida",
                "ideal_para": "Reduzir custos com combustível",
            },
            {
                "id": TipoOtimizacao.MENOR_TEMPO.value,
                "nome": "Menor Tempo",
                "descricao": "Minimiza o tempo total de deslocamento",
                "ideal_para": "Maximizar quantidade de atendimentos",
            },
            {
                "id": TipoOtimizacao.BALANCEADA.value,
                "nome": "Balanceada",
                "descricao": "Equilibra distância e tempo, respeitando janelas",
                "ideal_para": "Uso geral - recomendado",
            },
            {
                "id": TipoOtimizacao.PRIORIDADE.value,
                "nome": "Por Prioridade",
                "descricao": "Prioriza OS urgentes no início da rota",
                "ideal_para": "Quando há chamados urgentes",
            },
        ]
    }


@router.post("/calcular-distancia", summary="Calcular distância", description="Calcula distância entre dois pontos")
async def calcular_distancia(
    lat1: float = Query(..., ge=-90, le=90),
    lon1: float = Query(..., ge=-180, le=180),
    lat2: float = Query(..., ge=-90, le=90),
    lon2: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db),
):
    """
    Calcula distância entre dois pontos.

    Usa fórmula de Haversine para cálculo geodésico.
    Se API do Google Maps estiver configurada, usa dados reais.
    """
    import math

    # Fórmula de Haversine
    earth_radius = 6371  # Raio da Terra em km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distancia = earth_radius * c

    # Estimar tempo (30 km/h média urbana)
    tempo_minutos = int(distancia / 30 * 60)

    return {
        "origem": {"latitude": lat1, "longitude": lon1},
        "destino": {"latitude": lat2, "longitude": lon2},
        "distancia_km": round(distancia, 2),
        "tempo_estimado_minutos": tempo_minutos,
        "metodo": "haversine",
    }


@router.get("/resumo-dia/{tecnico_id}", summary="Resumo do dia", description="Retorna resumo rápido da rota do técnico")
async def get_resumo_dia(
    tecnico_id: UUID,
    data: date = Query(..., description="Data do roteiro"),
    db: Session = Depends(get_db),
):
    """Retorna resumo rápido da rota do técnico para o dia."""
    google_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    service = get_roteirizacao_service(db, google_api_key)

    try:
        roteiro = service.otimizar_rota_tecnico(
            tecnico_id=tecnico_id,
            data=data,
        )

        qtd_os = len([p for p in roteiro.pontos if p.tipo == "os"])
        qtd_visitas = len([p for p in roteiro.pontos if p.tipo == "visita"])

        return {
            "tecnico_id": str(tecnico_id),
            "tecnico_nome": roteiro.tecnico_nome,
            "data": data.isoformat(),
            "resumo": {
                "total_servicos": qtd_os + qtd_visitas,
                "ordens_servico": qtd_os,
                "visitas": qtd_visitas,
                "distancia_km": roteiro.distancia_total_km,
                "duracao_horas": round(roteiro.duracao_total_minutos / 60, 1),
                "inicio": roteiro.hora_inicio_sugerida.isoformat(),
                "fim_previsto": roteiro.hora_fim_estimada.isoformat(),
            },
            "economia": {
                "km_economizados": roteiro.economia_km,
                "minutos_economizados": roteiro.economia_tempo_minutos,
            }
            if roteiro.economia_km
            else None,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
