"""
IA para Scoring de Candidatos.

Implementa algoritmo de pontuacao de candidatos baseado em
multiplos criterios ponderados para auxiliar no processo seletivo.

Pesos:
    - experience_match: 25%
    - education_match: 15%
    - skills_match: 20%
    - availability: 15%
    - salary_expectation: 10%
    - location: 10%
    - references: 5%

Classificacao:
    - >= 80: excellent (excelente)
    - >= 60: good (bom)
    - >= 40: average (medio)
    - < 40: below_average (abaixo da media)
"""

import logging
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)

# Pesos dos criterios de avaliacao
SCORING_WEIGHTS: dict[str, float] = {
    "experience_match": 0.25,
    "education_match": 0.15,
    "skills_match": 0.20,
    "availability": 0.15,
    "salary_expectation": 0.10,
    "location": 0.10,
    "references": 0.05,
}


class CandidateScoringAI:
    """Servico de IA para scoring de candidatos.

    Calcula uma pontuacao de 0-100 para cada candidato em relacao
    a uma vaga especifica, considerando experiencia, educacao,
    habilidades, disponibilidade, pretensao salarial, localizacao
    e referencias.
    """

    def __init__(self) -> None:
        """Inicializa o servico de scoring."""
        self.weights = SCORING_WEIGHTS

    async def calculate_score(self, candidate: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
        """Calcula o score de um candidato para uma vaga."""
        breakdown = {}
        strengths = []
        weaknesses = []

        # 1. Experience Match (25%)
        exp_score = self._score_experience(candidate, job)
        breakdown["experience_match"] = round(exp_score, 1)
        if exp_score >= 80:
            strengths.append("Experiencia compativel com a vaga")
        elif exp_score < 40:
            weaknesses.append("Experiencia abaixo do requerido")

        # 2. Education Match (15%)
        edu_score = self._score_education(candidate, job)
        breakdown["education_match"] = round(edu_score, 1)
        if edu_score >= 80:
            strengths.append("Formacao academica adequada")
        elif edu_score < 40:
            weaknesses.append("Formacao academica insuficiente")

        # 3. Skills Match (20%)
        skills_score = self._score_skills(candidate, job)
        breakdown["skills_match"] = round(skills_score, 1)
        if skills_score >= 80:
            strengths.append("Habilidades alinham bem com a vaga")
        elif skills_score < 40:
            weaknesses.append("Habilidades nao atendem aos requisitos")

        # 4. Availability (15%)
        avail_score = self._score_availability(candidate, job)
        breakdown["availability"] = round(avail_score, 1)
        if avail_score >= 80:
            strengths.append("Disponibilidade imediata ou compativel")
        elif avail_score < 40:
            weaknesses.append("Disponibilidade nao compativel com urgencia")

        # 5. Salary Expectation (10%)
        salary_score = self._score_salary(candidate, job)
        breakdown["salary_expectation"] = round(salary_score, 1)
        if salary_score >= 80:
            strengths.append("Pretensao salarial dentro da faixa")
        elif salary_score < 40:
            weaknesses.append("Pretensao salarial acima do orcamento")

        # 6. Location (10%)
        loc_score = self._score_location(candidate, job)
        breakdown["location"] = round(loc_score, 1)
        if loc_score >= 80:
            strengths.append("Localizacao compativel")
        elif loc_score < 40:
            weaknesses.append("Localizacao distante da vaga")

        # 7. References (5%)
        ref_score = self._score_references(candidate)
        breakdown["references"] = round(ref_score, 1)
        if ref_score >= 80:
            strengths.append("Boas referencias profissionais")

        # Calcular score final ponderado
        final_score = sum(breakdown[dim] * weight for dim, weight in self.weights.items())
        final_score = round(min(100, max(0, final_score)), 1)

        classification = self._classify(final_score)
        recommendation = self._generate_recommendation(final_score, strengths, weaknesses)
        interview_questions = self._generate_interview_questions(candidate, job, weaknesses)

        result = {
            "score": final_score,
            "classification": classification,
            "breakdown": breakdown,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": recommendation,
            "interview_questions": interview_questions,
        }

        logger.info(f"Scoring calculado para candidato: score={final_score}, classification={classification}")
        return result

    @staticmethod
    def _classify(score: float) -> str:
        """Classifica o score em categoria."""
        if score >= 80:
            return "excellent"
        if score >= 60:
            return "good"
        if score >= 40:
            return "average"
        return "below_average"

    @staticmethod
    def _score_experience(candidate: dict, job: dict) -> float:
        """Pontua experiencia do candidato."""
        candidate_years = candidate.get("experience_years", 0)
        required_years = job.get("required_experience_years", 0)
        has_security = candidate.get("has_security_experience", False)

        if required_years == 0:
            base_score = 80.0
        elif candidate_years >= required_years:
            base_score = min(100, 80 + (candidate_years - required_years) * 5)
        elif candidate_years >= required_years * 0.5:
            ratio = candidate_years / max(required_years, 1)
            base_score = ratio * 80
        else:
            base_score = max(10, (candidate_years / max(required_years, 1)) * 60)

        # Bonus para experiencia em seguranca
        if has_security:
            base_score = min(100, base_score + 10)

        return base_score

    @staticmethod
    def _score_education(candidate: dict, job: dict) -> float:
        """Pontua formacao academica do candidato."""
        education_levels = {
            "fundamental": 1,
            "medio": 2,
            "tecnico": 3,
            "superior_incompleto": 4,
            "superior": 5,
            "pos_graduacao": 6,
            "mestrado": 7,
            "doutorado": 8,
        }

        candidate_edu = candidate.get("education_level", "medio")
        required_edu = job.get("required_education", "medio")

        candidate_level = education_levels.get(candidate_edu, 2)
        required_level = education_levels.get(required_edu, 2)

        if candidate_level >= required_level:
            return min(100, 80 + (candidate_level - required_level) * 5)
        elif candidate_level == required_level - 1:
            return 60.0
        else:
            return max(20, 40 - (required_level - candidate_level) * 10)

    @staticmethod
    def _score_skills(candidate: dict, job: dict) -> float:
        """Pontua habilidades do candidato."""
        candidate_skills = {s.lower() for s in (candidate.get("skills") or [])}
        required_skills = {s.lower() for s in (job.get("required_skills") or [])}
        desired_skills = {s.lower() for s in (job.get("desired_skills") or [])}

        if not required_skills and not desired_skills:
            return 70.0  # Score neutro se nao ha requisitos

        required_match = 0
        if required_skills:
            required_match = len(candidate_skills & required_skills) / len(required_skills)

        desired_match = 0
        if desired_skills:
            desired_match = len(candidate_skills & desired_skills) / len(desired_skills)

        # 70% peso para obrigatorias, 30% para desejaveis
        if required_skills and desired_skills:
            score = required_match * 70 + desired_match * 30
        elif required_skills:
            score = required_match * 100
        else:
            score = desired_match * 80 + 20  # Base de 20 se so tem desejaveis

        return min(100, score)

    @staticmethod
    def _score_availability(candidate: dict, job: dict) -> float:
        """Pontua disponibilidade do candidato."""
        available_immediately = candidate.get("available_immediately", False)
        urgency = job.get("urgency", "medium")

        if available_immediately:
            return 100.0

        available_date_str = candidate.get("available_date")
        if not available_date_str:
            # Sem data definida
            if urgency == "high":
                return 30.0
            return 60.0

        try:
            if isinstance(available_date_str, str):
                available_date = date.fromisoformat(available_date_str)
            else:
                available_date = available_date_str

            days_until = (available_date - date.today()).days
            if days_until <= 0:
                return 100.0
            elif days_until <= 7:
                return 90.0
            elif days_until <= 15:
                return 80.0
            elif days_until <= 30:
                score = 70.0 if urgency != "high" else 50.0
                return score
            elif days_until <= 60:
                return 50.0 if urgency != "high" else 30.0
            else:
                return 30.0 if urgency != "high" else 15.0
        except (ValueError, TypeError):
            return 50.0

    @staticmethod
    def _score_salary(candidate: dict, job: dict) -> float:
        """Pontua compatibilidade salarial."""
        expectation = candidate.get("salary_expectation")
        max_salary = job.get("max_salary")
        min_salary = job.get("min_salary")

        if not expectation:
            return 70.0  # Score neutro sem pretensao

        if not max_salary:
            return 70.0  # Score neutro sem teto

        expectation = float(expectation)
        max_salary = float(max_salary)
        min_salary = float(min_salary or 0)

        if expectation <= max_salary:
            if min_salary and expectation >= min_salary:
                return 100.0  # Dentro da faixa
            elif expectation < min_salary * 0.8:
                return 80.0  # Abaixo da faixa (pode ser bom)
            return 90.0
        else:
            over_ratio = (expectation - max_salary) / max_salary
            if over_ratio <= 0.1:
                return 70.0  # Ate 10% acima
            elif over_ratio <= 0.2:
                return 50.0  # Ate 20% acima
            elif over_ratio <= 0.3:
                return 30.0  # Ate 30% acima
            return 15.0  # Mais de 30% acima

    @staticmethod
    def _score_location(candidate: dict, job: dict) -> float:
        """Pontua compatibilidade de localizacao."""
        candidate_city = (candidate.get("city") or "").lower().strip()
        candidate_state = (candidate.get("state") or "").lower().strip()
        job_city = (job.get("city") or "").lower().strip()
        job_state = (job.get("state") or "").lower().strip()

        if not job_city and not job_state:
            return 80.0  # Vaga sem restricao de local

        if not candidate_city and not candidate_state:
            return 50.0  # Candidato sem local definido

        # Mesma cidade
        if candidate_city and job_city and candidate_city == job_city:
            return 100.0

        # Mesmo estado
        if candidate_state and job_state and candidate_state == job_state:
            return 70.0

        # Estados diferentes - verificar disposicao para mudanca
        if candidate.get("available_for_relocation"):
            return 60.0

        return 30.0

    @staticmethod
    def _score_references(candidate: dict) -> float:
        """Pontua referencias profissionais."""
        ref_count = candidate.get("references_count", 0)
        if ref_count >= 3:
            return 100.0
        elif ref_count == 2:
            return 80.0
        elif ref_count == 1:
            return 60.0
        return 30.0

    @staticmethod
    def _generate_recommendation(score: float, strengths: list[str], weaknesses: list[str]) -> str:
        """Gera recomendacao baseada no score e analise."""
        if score >= 80:
            return "Candidato altamente recomendado. Perfil excelente para a vaga. Priorizar agendamento de entrevista."
        elif score >= 60:
            return (
                "Candidato recomendado. Bom perfil geral com algumas areas de atencao. "
                "Explorar pontos fracos na entrevista."
            )
        elif score >= 40:
            weakness_text = "; ".join(weaknesses[:2]) if weaknesses else "diversos criterios"
            return (
                f"Candidato com perfil medio. Areas de preocupacao: {weakness_text}. "
                "Considerar apenas se houver poucos candidatos melhores."
            )
        else:
            return (
                "Candidato abaixo do perfil desejado. Nao recomendado para esta vaga. "
                "Considerar para outras vagas com requisitos menores."
            )

    @staticmethod
    def _generate_interview_questions(candidate: dict, job: dict, weaknesses: list[str]) -> list[str]:
        """Gera perguntas sugeridas para entrevista baseadas no perfil."""
        questions = [
            "Descreva sua experiencia anterior mais relevante para esta posicao.",
        ]

        # Perguntas baseadas em pontos fracos
        for weakness in weaknesses:
            if "experiencia" in weakness.lower():
                questions.append("Como voce pretende superar a falta de experiencia na area de seguranca patrimonial?")
            elif "formacao" in weakness.lower() or "academica" in weakness.lower():
                questions.append("Possui cursos ou certificacoes complementares a sua formacao academica?")
            elif "habilidades" in weakness.lower():
                questions.append("Como voce planeja desenvolver as habilidades requeridas para esta funcao?")
            elif "salarial" in weakness.lower():
                questions.append("Existe flexibilidade na sua pretensao salarial? Considera outros beneficios?")
            elif "localizacao" in weakness.lower():
                questions.append("Esta disposto a se mudar para a regiao da vaga? Em quanto tempo?")

        # Perguntas padrao para seguranca
        if candidate.get("has_security_experience"):
            questions.append("Relate uma situacao critica que enfrentou em servico de seguranca e como a resolveu.")
        else:
            questions.append("O que o motiva a trabalhar na area de seguranca patrimonial?")

        questions.append("Como voce lida com situacoes de pressao e trabalho em escalas?")

        return questions[:6]  # Limitar a 6 perguntas
