"""Service de IA para análise de moradores."""

import logging
from datetime import datetime, date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.repositories.resident_repository import ResidentRepository
from modules.residents.repositories.vehicle_repository import VehicleRepository
from modules.residents.repositories.pet_repository import PetRepository
from modules.residents.repositories.dependent_repository import DependentRepository
from modules.residents.models.resident import ResidentStatus, ResidentType

logger = logging.getLogger(__name__)


class ResidentAIService:
    """Service de IA para análise e insights de moradores."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.resident_repo = ResidentRepository(session)
        self.vehicle_repo = VehicleRepository(session)
        self.pet_repo = PetRepository(session)
        self.dependent_repo = DependentRepository(session)

    async def analyze_resident_profile(
        self, resident_id: str | UUID
    ) -> dict:
        """Analisa o perfil completo de um morador."""
        resident = await self.resident_repo.get_by_id(resident_id)
        if not resident:
            return {"error": "Morador não encontrado"}

        # Busca dados relacionados
        vehicles = await self.vehicle_repo.get_by_resident(resident_id)
        pets = await self.pet_repo.get_by_resident(resident_id)
        dependents = await self.dependent_repo.get_by_resident(resident_id)

        # Calcula score de engajamento
        engagement_score = self._calculate_engagement_score(
            resident, vehicles, pets, dependents
        )

        # Identifica alertas
        alerts = self._identify_alerts(resident, vehicles, pets, dependents)

        # Gera sugestões
        suggestions = self._generate_suggestions(resident, vehicles, pets, dependents)

        # Classifica perfil
        profile_type = self._classify_profile(resident, dependents)

        return {
            "resident_id": str(resident.id),
            "name": resident.name,
            "profile_type": profile_type,
            "engagement_score": engagement_score,
            "summary": {
                "status": resident.status.value,
                "is_owner": resident.resident_type == ResidentType.PROPRIETARIO,
                "is_defaulter": resident.is_defaulter,
                "is_blocked": resident.is_blocked,
                "vehicles_count": len(vehicles),
                "pets_count": len(pets),
                "dependents_count": len(dependents),
                "has_biometric": resident.has_biometric,
                "has_access_card": resident.has_access_card,
            },
            "alerts": alerts,
            "suggestions": suggestions,
            "risk_level": self._calculate_risk_level(resident, alerts),
        }

    def _calculate_engagement_score(
        self, resident, vehicles, pets, dependents
    ) -> int:
        """Calcula score de engajamento do morador (0-100)."""
        score = 50  # Base

        # Dados cadastrais completos
        if resident.email:
            score += 5
        if resident.phone:
            score += 5
        if resident.birth_date:
            score += 3
        if resident.cpf:
            score += 5
        if resident.photo_url:
            score += 5

        # Métodos de acesso
        if resident.has_biometric:
            score += 10
        if resident.has_access_card:
            score += 5
        if resident.facial_id:
            score += 8
        if resident.qr_code:
            score += 3

        # Relacionamentos cadastrados
        if vehicles:
            score += min(len(vehicles) * 3, 10)
        if pets:
            score += min(len(pets) * 2, 8)
        if dependents:
            score += min(len(dependents) * 3, 12)

        # Penalidades
        if resident.is_blocked:
            score -= 20
        if resident.is_defaulter:
            score -= 15
        if resident.status != ResidentStatus.ATIVO:
            score -= 10

        return max(0, min(100, score))

    def _identify_alerts(
        self, resident, vehicles, pets, dependents
    ) -> list[dict]:
        """Identifica alertas relacionados ao morador."""
        alerts = []

        # Morador bloqueado
        if resident.is_blocked:
            alerts.append({
                "type": "critical",
                "category": "access",
                "message": f"Morador bloqueado: {resident.block_reason}",
                "action": "Verificar motivo do bloqueio",
            })

        # Inadimplência
        if resident.is_defaulter:
            alerts.append({
                "type": "warning",
                "category": "financial",
                "message": f"Morador inadimplente. Débito: R$ {resident.debt_amount:.2f}",
                "action": "Entrar em contato para regularização",
            })

        # Cadastro incompleto
        missing_fields = []
        if not resident.email:
            missing_fields.append("email")
        if not resident.phone:
            missing_fields.append("telefone")
        if not resident.cpf:
            missing_fields.append("CPF")
        if not resident.photo_url:
            missing_fields.append("foto")

        if missing_fields:
            alerts.append({
                "type": "info",
                "category": "registration",
                "message": f"Cadastro incompleto: {', '.join(missing_fields)}",
                "action": "Completar cadastro",
            })

        # Sem método de acesso
        if not resident.has_biometric and not resident.has_access_card:
            alerts.append({
                "type": "warning",
                "category": "access",
                "message": "Morador sem método de acesso cadastrado",
                "action": "Cadastrar biometria ou cartão de acesso",
            })

        # Veículos sem RFID
        vehicles_without_rfid = [v for v in vehicles if not v.rfid_tag]
        if vehicles_without_rfid:
            alerts.append({
                "type": "info",
                "category": "access",
                "message": f"{len(vehicles_without_rfid)} veículo(s) sem tag RFID",
                "action": "Cadastrar tags RFID",
            })

        # Pets não vacinados
        pets_not_vaccinated = [p for p in pets if not p.is_vaccinated]
        if pets_not_vaccinated:
            alerts.append({
                "type": "warning",
                "category": "pet",
                "message": f"{len(pets_not_vaccinated)} pet(s) não vacinado(s)",
                "action": "Solicitar comprovante de vacinação",
            })

        # Pets com vacina expirando
        today = date.today()
        expiry_limit = today + timedelta(days=30)
        pets_expiring = [
            p for p in pets
            if p.vaccination_expiry and p.vaccination_expiry <= expiry_limit
        ]
        if pets_expiring:
            alerts.append({
                "type": "info",
                "category": "pet",
                "message": f"{len(pets_expiring)} pet(s) com vacina expirando",
                "action": "Solicitar atualização da vacinação",
            })

        # Dependentes temporários expirando
        dependents_expiring = [
            d for d in dependents
            if d.valid_until and d.valid_until <= expiry_limit
        ]
        if dependents_expiring:
            alerts.append({
                "type": "info",
                "category": "dependent",
                "message": f"{len(dependents_expiring)} dependente(s) temporário(s) expirando",
                "action": "Renovar período de validade",
            })

        return alerts

    def _generate_suggestions(
        self, resident, vehicles, pets, dependents
    ) -> list[str]:
        """Gera sugestões para o morador."""
        suggestions = []

        # Biometria
        if not resident.has_biometric:
            suggestions.append(
                "Cadastrar biometria para acesso mais seguro e rápido"
            )

        # Facial
        if not resident.facial_id and resident.photo_url:
            suggestions.append(
                "Habilitar reconhecimento facial para maior comodidade"
            )

        # App
        if not resident.app_user_id:
            suggestions.append(
                "Vincular conta ao aplicativo para receber notificações"
            )

        # Contatos de emergência
        # Seria ideal verificar os contatos, mas simplificamos
        suggestions.append(
            "Manter contatos de emergência atualizados"
        )

        # Veículos
        if vehicles:
            vehicles_without_parking = [v for v in vehicles if not v.parking_spot]
            if vehicles_without_parking:
                suggestions.append(
                    f"Solicitar vaga para {len(vehicles_without_parking)} veículo(s)"
                )

        # Pets agressivos
        aggressive_pets = [p for p in pets if p.is_aggressive]
        if aggressive_pets:
            suggestions.append(
                "Manter pets agressivos com focinheira nas áreas comuns"
            )

        return suggestions[:5]  # Limita a 5 sugestões

    def _classify_profile(self, resident, dependents) -> str:
        """Classifica o perfil do morador."""
        minors = [d for d in dependents if d.is_minor]
        employees = [d for d in dependents if d.is_employee]

        if resident.resident_type == ResidentType.PROPRIETARIO:
            if minors:
                return "Família com crianças"
            if len(dependents) > 2:
                return "Família grande"
            return "Proprietário"

        if resident.resident_type == ResidentType.INQUILINO:
            if minors:
                return "Família locatária com crianças"
            return "Inquilino"

        if resident.resident_type == ResidentType.FUNCIONARIO_DOMESTICO:
            return "Funcionário residente"

        if employees:
            return "Residência com funcionários"

        return "Morador padrão"

    def _calculate_risk_level(self, resident, alerts) -> str:
        """Calcula nível de risco do morador."""
        critical_alerts = [a for a in alerts if a["type"] == "critical"]
        warning_alerts = [a for a in alerts if a["type"] == "warning"]

        if critical_alerts or resident.is_blocked:
            return "alto"
        if warning_alerts or resident.is_defaulter:
            return "medio"
        return "baixo"

    async def get_condominium_insights(
        self, condominium_id: str
    ) -> dict:
        """Gera insights para o condomínio."""
        # Estatísticas de moradores
        resident_stats = await self.resident_repo.get_stats(condominium_id)
        vehicle_stats = await self.vehicle_repo.get_stats(condominium_id)
        pet_stats = await self.pet_repo.get_stats(condominium_id)
        dependent_stats = await self.dependent_repo.get_stats(condominium_id)

        # Análise de inadimplência
        defaulters = await self.resident_repo.get_defaulters(condominium_id)
        total_debt = sum(r.debt_amount or 0 for r in defaulters)

        # Pets com vacina expirando
        expiring_vaccines = await self.pet_repo.get_vaccination_expiring(
            30, condominium_id
        )

        # Dependentes temporários expirando
        expiring_dependents = await self.dependent_repo.get_temporary_expiring(
            30, condominium_id
        )

        insights = {
            "summary": {
                "total_residents": resident_stats["total"],
                "active_residents": resident_stats["active"],
                "total_vehicles": vehicle_stats["total"],
                "total_pets": pet_stats["total"],
                "total_dependents": dependent_stats["total"],
            },
            "financial": {
                "defaulters_count": resident_stats["defaulters"],
                "defaulters_percentage": (
                    (resident_stats["defaulters"] / resident_stats["total"] * 100)
                    if resident_stats["total"] > 0 else 0
                ),
                "total_debt": total_debt,
                "avg_debt": resident_stats.get("avg_debt", 0),
            },
            "access": {
                "with_biometric": resident_stats["with_biometric"],
                "with_access_card": resident_stats["with_access_card"],
                "biometric_percentage": (
                    (resident_stats["with_biometric"] / resident_stats["total"] * 100)
                    if resident_stats["total"] > 0 else 0
                ),
            },
            "vehicles": {
                "total": vehicle_stats["total"],
                "active": vehicle_stats["active"],
                "with_rfid": vehicle_stats["with_rfid"],
                "without_parking": vehicle_stats["without_parking"],
                "by_type": vehicle_stats["by_type"],
            },
            "pets": {
                "total": pet_stats["total"],
                "vaccinated": pet_stats["vaccinated"],
                "not_vaccinated": pet_stats["not_vaccinated"],
                "expiring_vaccines": len(expiring_vaccines),
                "aggressive": pet_stats["aggressive"],
                "by_type": pet_stats["by_type"],
            },
            "dependents": {
                "total": dependent_stats["total"],
                "minors": dependent_stats["minors"],
                "employees": dependent_stats["employees"],
                "temporary_expiring": len(expiring_dependents),
                "by_relationship": dependent_stats["by_relationship"],
            },
            "alerts": [],
            "recommendations": [],
        }

        # Gera alertas do condomínio
        if resident_stats["defaulters"] > 0:
            insights["alerts"].append({
                "type": "warning",
                "message": f"{resident_stats['defaulters']} morador(es) inadimplente(s)",
                "value": total_debt,
            })

        if pet_stats["not_vaccinated"] > 0:
            insights["alerts"].append({
                "type": "warning",
                "message": f"{pet_stats['not_vaccinated']} pet(s) não vacinado(s)",
            })

        if len(expiring_vaccines) > 0:
            insights["alerts"].append({
                "type": "info",
                "message": f"{len(expiring_vaccines)} pet(s) com vacina expirando",
            })

        if len(expiring_dependents) > 0:
            insights["alerts"].append({
                "type": "info",
                "message": f"{len(expiring_dependents)} dependente(s) temporário(s) expirando",
            })

        # Gera recomendações
        biometric_pct = insights["access"]["biometric_percentage"]
        if biometric_pct < 50:
            insights["recommendations"].append(
                f"Aumentar adesão à biometria (atualmente {biometric_pct:.1f}%)"
            )

        if vehicle_stats["without_parking"] > 0:
            insights["recommendations"].append(
                f"Resolver alocação de vagas para {vehicle_stats['without_parking']} veículo(s)"
            )

        if pet_stats["aggressive"] > 0:
            insights["recommendations"].append(
                f"Monitorar {pet_stats['aggressive']} pet(s) agressivo(s) nas áreas comuns"
            )

        return insights

    async def predict_churn_risk(
        self, resident_id: str | UUID
    ) -> dict:
        """Prediz risco de mudança do morador."""
        resident = await self.resident_repo.get_by_id(resident_id)
        if not resident:
            return {"error": "Morador não encontrado"}

        risk_factors = []
        risk_score = 0

        # Tipo de morador
        if resident.resident_type == ResidentType.INQUILINO:
            risk_score += 20
            risk_factors.append("Inquilino (maior rotatividade)")

        # Contrato próximo do fim
        if resident.contract_end_date:
            days_to_end = (resident.contract_end_date - date.today()).days
            if 0 < days_to_end <= 90:
                risk_score += 30
                risk_factors.append(f"Contrato expira em {days_to_end} dias")

        # Inadimplência
        if resident.is_defaulter:
            risk_score += 25
            risk_factors.append("Histórico de inadimplência")

        # Bloqueios
        if resident.is_blocked:
            risk_score += 20
            risk_factors.append("Morador bloqueado")

        # Status
        if resident.status == ResidentStatus.SUSPENSO:
            risk_score += 15
            risk_factors.append("Status suspenso")

        # Tempo de residência (quanto mais tempo, menor o risco)
        if resident.move_in_date:
            months_resident = (date.today() - resident.move_in_date).days // 30
            if months_resident < 6:
                risk_score += 10
                risk_factors.append("Morador recente (< 6 meses)")
            elif months_resident > 24:
                risk_score -= 15
                risk_factors.append("Morador estável (> 2 anos)")

        risk_level = "baixo"
        if risk_score > 50:
            risk_level = "alto"
        elif risk_score > 25:
            risk_level = "medio"

        return {
            "resident_id": str(resident.id),
            "name": resident.name,
            "risk_score": max(0, min(100, risk_score)),
            "risk_level": risk_level,
            "factors": risk_factors,
            "recommendations": self._get_churn_recommendations(risk_factors),
        }

    def _get_churn_recommendations(self, factors: list[str]) -> list[str]:
        """Gera recomendações para reduzir risco de churn."""
        recommendations = []

        if any("Contrato" in f for f in factors):
            recommendations.append("Iniciar negociação de renovação de contrato")

        if any("inadimplência" in f.lower() for f in factors):
            recommendations.append("Oferecer plano de regularização de débitos")

        if any("bloqueado" in f.lower() for f in factors):
            recommendations.append("Verificar situação do bloqueio")

        if any("recente" in f.lower() for f in factors):
            recommendations.append("Acompanhar adaptação do novo morador")

        if not recommendations:
            recommendations.append("Manter relacionamento próximo")

        return recommendations

    async def suggest_similar_residents(
        self, resident_id: str | UUID, limit: int = 5
    ) -> list[dict]:
        """Sugere moradores com perfil similar."""
        resident = await self.resident_repo.get_by_id(resident_id)
        if not resident:
            return []

        # Busca moradores do mesmo condomínio
        filters_obj = type(
            "ResidentFilter", (), {
                "condominium_id": resident.condominium_id,
                "resident_type": resident.resident_type,
                "status": ResidentStatus.ATIVO,
                "name": None,
                "document_number": None,
                "cpf": None,
                "email": None,
                "phone": None,
                "unit_id": None,
                "block": None,
                "is_blocked": None,
                "is_defaulter": None,
                "is_unit_owner": None,
                "is_main_resident": None,
            }
        )()

        similar, _ = await self.resident_repo.list_with_filters(
            filters=filters_obj, limit=limit + 1
        )

        # Remove o próprio morador e limita
        similar = [r for r in similar if str(r.id) != str(resident_id)][:limit]

        return [
            {
                "id": str(r.id),
                "name": r.name,
                "unit": r.unit_number,
                "block": r.block,
                "type": r.resident_type.value,
            }
            for r in similar
        ]
