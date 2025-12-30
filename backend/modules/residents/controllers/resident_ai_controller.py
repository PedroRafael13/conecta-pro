"""Controller de IA para Residents."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.auth.dependencies import get_current_user
from modules.residents.services.resident_ai_service import ResidentAIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/residents/ai", tags=["IA de Moradores"])


def get_service(session: AsyncSession = Depends(get_session)) -> ResidentAIService:
    """Retorna instância do service."""
    return ResidentAIService(session)


@router.get(
    "/profile/{resident_id}",
    summary="Análise de perfil do morador",
)
async def analyze_resident_profile(
    resident_id: UUID,
    service: ResidentAIService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """
    Analisa o perfil completo de um morador.

    Retorna:
    - Classificação do perfil
    - Score de engajamento
    - Resumo do morador
    - Alertas identificados
    - Sugestões de melhoria
    - Nível de risco
    """
    result = await service.analyze_resident_profile(resident_id)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"],
        )
    return result


@router.get(
    "/condominium-insights/{condominium_id}",
    summary="Insights do condomínio",
)
async def get_condominium_insights(
    condominium_id: str,
    service: ResidentAIService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """
    Gera insights sobre os moradores do condomínio.

    Retorna:
    - Resumo geral
    - Análise financeira (inadimplência)
    - Estatísticas de acesso
    - Estatísticas de veículos
    - Estatísticas de pets
    - Estatísticas de dependentes
    - Alertas gerais
    - Recomendações
    """
    return await service.get_condominium_insights(condominium_id)


@router.get(
    "/churn-risk/{resident_id}",
    summary="Risco de mudança",
)
async def predict_churn_risk(
    resident_id: UUID,
    service: ResidentAIService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """
    Prediz o risco de mudança do morador.

    Retorna:
    - Score de risco (0-100)
    - Nível de risco (baixo, medio, alto)
    - Fatores de risco identificados
    - Recomendações para retenção
    """
    result = await service.predict_churn_risk(resident_id)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"],
        )
    return result


@router.get(
    "/similar/{resident_id}",
    summary="Moradores similares",
)
async def get_similar_residents(
    resident_id: UUID,
    limit: int = 5,
    service: ResidentAIService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """
    Sugere moradores com perfil similar.

    Útil para:
    - Networking entre moradores
    - Grupos de interesse
    - Comunicação segmentada
    """
    return await service.suggest_similar_residents(resident_id, limit)


@router.get(
    "/dashboard/{condominium_id}",
    summary="Dashboard de IA",
)
async def get_ai_dashboard(
    condominium_id: str,
    service: ResidentAIService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """
    Dashboard consolidado com análises de IA.

    Combina múltiplas análises em uma visão única.
    """
    insights = await service.get_condominium_insights(condominium_id)

    # Adiciona métricas derivadas
    dashboard = {
        "insights": insights,
        "health_score": _calculate_health_score(insights),
        "key_metrics": _extract_key_metrics(insights),
        "priority_actions": _get_priority_actions(insights),
    }

    return dashboard


def _calculate_health_score(insights: dict) -> dict:
    """Calcula score de saúde geral do condomínio."""
    score = 100
    details = []

    # Penaliza por inadimplência
    defaulter_pct = insights.get("financial", {}).get("defaulters_percentage", 0)
    if defaulter_pct > 0:
        penalty = min(defaulter_pct * 2, 30)
        score -= penalty
        details.append(f"Inadimplência: -{penalty:.0f} pontos")

    # Penaliza por pets não vacinados
    not_vaccinated = insights.get("pets", {}).get("not_vaccinated", 0)
    total_pets = insights.get("pets", {}).get("total", 1)
    if not_vaccinated > 0 and total_pets > 0:
        pct = (not_vaccinated / total_pets) * 100
        penalty = min(pct, 15)
        score -= penalty
        details.append(f"Pets não vacinados: -{penalty:.0f} pontos")

    # Bonifica por adesão à biometria
    biometric_pct = insights.get("access", {}).get("biometric_percentage", 0)
    if biometric_pct >= 80:
        bonus = 10
        score += bonus
        details.append(f"Alta adesão biometria: +{bonus} pontos")
    elif biometric_pct < 30:
        penalty = 10
        score -= penalty
        details.append(f"Baixa adesão biometria: -{penalty} pontos")

    # Penaliza por alertas críticos
    alerts = insights.get("alerts", [])
    warning_count = sum(1 for a in alerts if a.get("type") == "warning")
    if warning_count > 0:
        penalty = min(warning_count * 5, 20)
        score -= penalty
        details.append(f"Alertas: -{penalty} pontos")

    level = "excelente"
    if score < 60:
        level = "critico"
    elif score < 75:
        level = "atencao"
    elif score < 90:
        level = "bom"

    return {
        "score": max(0, min(100, score)),
        "level": level,
        "details": details,
    }


def _extract_key_metrics(insights: dict) -> list[dict]:
    """Extrai métricas-chave para exibição."""
    metrics = []

    # Total de moradores
    total_residents = insights.get("summary", {}).get("total_residents", 0)
    metrics.append({
        "name": "Moradores Ativos",
        "value": insights.get("summary", {}).get("active_residents", 0),
        "total": total_residents,
        "icon": "users",
    })

    # Inadimplência
    metrics.append({
        "name": "Inadimplência",
        "value": insights.get("financial", {}).get("defaulters_count", 0),
        "percentage": insights.get("financial", {}).get("defaulters_percentage", 0),
        "icon": "alert-triangle",
        "color": "red" if insights.get("financial", {}).get("defaulters_count", 0) > 0 else "green",
    })

    # Biometria
    metrics.append({
        "name": "Com Biometria",
        "value": insights.get("access", {}).get("with_biometric", 0),
        "percentage": insights.get("access", {}).get("biometric_percentage", 0),
        "icon": "fingerprint",
    })

    # Veículos
    metrics.append({
        "name": "Veículos",
        "value": insights.get("vehicles", {}).get("active", 0),
        "total": insights.get("vehicles", {}).get("total", 0),
        "icon": "car",
    })

    # Pets
    metrics.append({
        "name": "Pets Vacinados",
        "value": insights.get("pets", {}).get("vaccinated", 0),
        "total": insights.get("pets", {}).get("total", 0),
        "icon": "heart",
    })

    return metrics


def _get_priority_actions(insights: dict) -> list[dict]:
    """Retorna ações prioritárias baseadas nos insights."""
    actions = []

    # Ações de inadimplência
    defaulters = insights.get("financial", {}).get("defaulters_count", 0)
    if defaulters > 0:
        actions.append({
            "priority": 1,
            "category": "financial",
            "title": "Regularizar inadimplência",
            "description": f"{defaulters} morador(es) inadimplente(s)",
            "action_type": "contact",
        })

    # Ações de vacinação
    not_vaccinated = insights.get("pets", {}).get("not_vaccinated", 0)
    if not_vaccinated > 0:
        actions.append({
            "priority": 2,
            "category": "pet",
            "title": "Solicitar vacinação de pets",
            "description": f"{not_vaccinated} pet(s) sem vacina em dia",
            "action_type": "notification",
        })

    # Ações de biometria
    biometric_pct = insights.get("access", {}).get("biometric_percentage", 0)
    if biometric_pct < 50:
        actions.append({
            "priority": 3,
            "category": "access",
            "title": "Aumentar adesão à biometria",
            "description": f"Apenas {biometric_pct:.1f}% dos moradores com biometria",
            "action_type": "campaign",
        })

    # Ações de vagas
    without_parking = insights.get("vehicles", {}).get("without_parking", 0)
    if without_parking > 0:
        actions.append({
            "priority": 4,
            "category": "vehicle",
            "title": "Alocar vagas de estacionamento",
            "description": f"{without_parking} veículo(s) sem vaga atribuída",
            "action_type": "allocation",
        })

    # Ordena por prioridade
    actions.sort(key=lambda x: x["priority"])

    return actions[:5]  # Retorna top 5 ações
