"""
DisciplinaryAdvisor - Servico de IA para Recomendacoes Disciplinares.

Implementa algoritmos inteligentes para:
- Recomendar tipo de medida baseado no historico
- Validar conformidade com CLT
- Verificar proporcionalidade
- Gerar texto para motivos

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operacional.disciplinary.models import (
    DisciplinaryActionStatus,
    DisciplinaryActionType,
    ReasonCategory,
)
from modules.operacional.disciplinary.repositories import DisciplinaryRepository
from modules.operacional.disciplinary.schemas import (
    LegalComplianceRequest,
    LegalComplianceResponse,
    ProportionalityCheckRequest,
    ProportionalityCheckResponse,
    RecommendationRequest,
    RecommendationResponse,
)


class DisciplinaryAdvisor:
    """
    Servico de IA para recomendacoes em medidas disciplinares.

    Utiliza regras baseadas na CLT e jurisprudencia trabalhista
    para recomendar a medida mais adequada e validar conformidade.
    """

    # Mapeamento de categorias graves que podem justificar justa causa direta
    GRAVE_CATEGORIES = {
        ReasonCategory.ATO_IMPROBIDADE,
        ReasonCategory.EMBRIAGUEZ,
        ReasonCategory.ABANDONO_EMPREGO,
        ReasonCategory.VIOLACAO_SEGREDO,
        ReasonCategory.OFENSA_FISICA,
        ReasonCategory.PERDA_HABILITACAO,
    }

    # Mapeamento de categorias medias
    MEDIUM_CATEGORIES = {
        ReasonCategory.INSUBORDINACAO,
        ReasonCategory.INDISCIPLINA,
        ReasonCategory.DANO_PATRIMONIO,
        ReasonCategory.NEGLIGENCIA,
    }

    # Artigos da CLT relacionados
    CLT_ARTICLES = {
        "art_474": "Art. 474 CLT - Suspensao disciplinar nao pode exceder 30 dias",
        "art_482": "Art. 482 CLT - Constituem justa causa para rescisao do contrato",
        "art_482_a": "Art. 482, a) - Ato de improbidade",
        "art_482_b": "Art. 482, b) - Incontinencia de conduta ou mau procedimento",
        "art_482_e": "Art. 482, e) - Desidia no desempenho das funcoes",
        "art_482_f": "Art. 482, f) - Embriaguez habitual ou em servico",
        "art_482_h": "Art. 482, h) - Ato de indisciplina ou de insubordinacao",
        "art_482_i": "Art. 482, i) - Abandono de emprego",
        "art_482_j": "Art. 482, j) - Ato lesivo da honra ou boa fama",
        "art_482_k": "Art. 482, k) - Ofensas fisicas",
    }

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o advisor.

        Args:
            db: Sessao async do SQLAlchemy
        """
        self.db = db
        self.repo = DisciplinaryRepository(db)

    async def recommend_action(
        self,
        request: RecommendationRequest,
        tenant_id: str,
    ) -> RecommendationResponse:
        """
        Recomenda tipo de medida disciplinar baseado no historico e contexto.

        Args:
            request: Dados do incidente
            tenant_id: ID do tenant

        Returns:
            Recomendacao com justificativa
        """
        # Buscar historico do funcionario
        history = await self.repo.get_by_employee(request.employee_id, tenant_id)
        applied_history = [h for h in history if h.status == DisciplinaryActionStatus.APLICADA.value]

        warnings = [
            h
            for h in applied_history
            if h.action_type
            in [
                DisciplinaryActionType.ADVERTENCIA_VERBAL.value,
                DisciplinaryActionType.ADVERTENCIA_ESCRITA.value,
            ]
        ]
        suspensions = [h for h in applied_history if h.action_type == DisciplinaryActionType.SUSPENSAO.value]

        # Determinar ultima ocorrencia
        last_incident_date = None
        if applied_history:
            last_incident_date = max(h.incident_date for h in applied_history)

        # Analisar gravidade da categoria
        category = request.reason_category
        is_grave = category in self.GRAVE_CATEGORIES
        is_medium = category in self.MEDIUM_CATEGORIES

        # Logica de recomendacao
        recommended, confidence, reasoning, alternatives = self._calculate_recommendation(
            warnings_count=len(warnings),
            suspensions_count=len(suspensions),
            is_grave=is_grave,
            is_medium=is_medium,
            category=category,
            last_incident_date=last_incident_date,
            incident_date=request.incident_date,
        )

        # Referencias legais
        legal_references = self._get_legal_references(category, recommended)

        logger.info(
            f"Recomendacao gerada para funcionario {request.employee_id}",
            extra={
                "recommended": recommended.value,
                "confidence": confidence,
                "warnings": len(warnings),
                "suspensions": len(suspensions),
                "category": category.value,
            },
        )

        return RecommendationResponse(
            recommended_action=recommended,
            confidence_score=confidence,
            reasoning=reasoning,
            previous_warnings=len(warnings),
            previous_suspensions=len(suspensions),
            last_incident_date=last_incident_date,
            alternative_actions=alternatives,
            legal_references=legal_references,
        )

    def _calculate_recommendation(
        self,
        warnings_count: int,
        suspensions_count: int,
        is_grave: bool,
        is_medium: bool,
        category: ReasonCategory,
        last_incident_date: date | None,
        incident_date: date,
    ) -> tuple[DisciplinaryActionType, float, str, list[DisciplinaryActionType]]:
        """
        Calcula a recomendacao baseada em regras.

        Returns:
            Tupla (tipo_recomendado, confianca, justificativa, alternativas)
        """
        reasoning_parts: list[str] = []

        # 1. Falta grave pode justificar justa causa direta
        if is_grave:
            if category == ReasonCategory.ABANDONO_EMPREGO:
                # Abandono requer 30 dias consecutivos
                reasoning_parts.append(
                    "Abandono de emprego requer mais de 30 dias de ausencia consecutiva "
                    "para caracterizar justa causa imediata."
                )
                if warnings_count >= 1 or suspensions_count >= 1:
                    return (
                        DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA,
                        0.75,
                        " ".join(reasoning_parts),
                        [DisciplinaryActionType.SUSPENSAO],
                    )
                return (
                    DisciplinaryActionType.SUSPENSAO,
                    0.70,
                    " ".join(reasoning_parts) + " Recomenda-se suspensao enquanto se aguarda prazo legal.",
                    [DisciplinaryActionType.ADVERTENCIA_ESCRITA],
                )

            if category in {ReasonCategory.ATO_IMPROBIDADE, ReasonCategory.OFENSA_FISICA}:
                reasoning_parts.append(
                    f"A categoria '{category.value}' e considerada falta grave e pode "
                    "justificar demissao por justa causa direta conforme Art. 482 CLT."
                )
                return (
                    DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA,
                    0.85,
                    " ".join(reasoning_parts),
                    [DisciplinaryActionType.SUSPENSAO],
                )

            # Outras graves
            if suspensions_count >= 1:
                reasoning_parts.append(
                    f"Funcionario ja possui {suspensions_count} suspensao(oes) e cometeu falta grave."
                )
                return (
                    DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA,
                    0.80,
                    " ".join(reasoning_parts),
                    [DisciplinaryActionType.SUSPENSAO],
                )

            if warnings_count >= 2:
                reasoning_parts.append(f"Funcionario possui {warnings_count} advertencias e cometeu falta grave.")
                return (
                    DisciplinaryActionType.SUSPENSAO,
                    0.85,
                    " ".join(reasoning_parts),
                    [DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA],
                )

        # 2. Progressao disciplinar padrao
        if suspensions_count >= 2:
            reasoning_parts.append(
                f"Funcionario ja possui {suspensions_count} suspensoes aplicadas. Proxima medida seria justa causa."
            )
            return (
                DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA,
                0.75,
                " ".join(reasoning_parts),
                [DisciplinaryActionType.SUSPENSAO],
            )

        if suspensions_count >= 1:
            reasoning_parts.append(
                f"Funcionario ja possui {suspensions_count} suspensao. Nova suspensao ou justa causa sao aplicaveis."
            )
            if is_medium:
                return (
                    DisciplinaryActionType.SUSPENSAO,
                    0.80,
                    " ".join(reasoning_parts),
                    [DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA, DisciplinaryActionType.ADVERTENCIA_ESCRITA],
                )
            return (
                DisciplinaryActionType.ADVERTENCIA_ESCRITA,
                0.70,
                " ".join(reasoning_parts),
                [DisciplinaryActionType.SUSPENSAO],
            )

        if warnings_count >= 3:
            reasoning_parts.append(
                f"Funcionario ja possui {warnings_count} advertencias. "
                "Suspensao e a proxima medida na escala disciplinar."
            )
            return (
                DisciplinaryActionType.SUSPENSAO,
                0.85,
                " ".join(reasoning_parts),
                [DisciplinaryActionType.ADVERTENCIA_ESCRITA],
            )

        if warnings_count >= 1:
            reasoning_parts.append(f"Funcionario possui {warnings_count} advertencia(s) anterior(es). ")

            # Verificar reincidencia recente (menos de 6 meses)
            if last_incident_date:
                days_since_last = (incident_date - last_incident_date).days
                if days_since_last < 180:
                    reasoning_parts.append(f"Reincidencia em {days_since_last} dias. Advertencia escrita recomendada.")
                    if is_medium:
                        return (
                            DisciplinaryActionType.SUSPENSAO,
                            0.70,
                            " ".join(reasoning_parts),
                            [DisciplinaryActionType.ADVERTENCIA_ESCRITA],
                        )
                    return (
                        DisciplinaryActionType.ADVERTENCIA_ESCRITA,
                        0.85,
                        " ".join(reasoning_parts),
                        [DisciplinaryActionType.SUSPENSAO, DisciplinaryActionType.ADVERTENCIA_VERBAL],
                    )

            return (
                DisciplinaryActionType.ADVERTENCIA_ESCRITA,
                0.80,
                " ".join(reasoning_parts) + "Advertencia escrita e apropriada.",
                [DisciplinaryActionType.ADVERTENCIA_VERBAL, DisciplinaryActionType.SUSPENSAO],
            )

        # Primeira ocorrencia
        reasoning_parts.append("Primeira ocorrencia do funcionario. ")

        if is_grave:
            return (
                DisciplinaryActionType.ADVERTENCIA_ESCRITA,
                0.75,
                " ".join(reasoning_parts) + "Por ser falta grave, advertencia escrita direta.",
                [DisciplinaryActionType.SUSPENSAO, DisciplinaryActionType.ADVERTENCIA_VERBAL],
            )

        if is_medium:
            return (
                DisciplinaryActionType.ADVERTENCIA_ESCRITA,
                0.80,
                " ".join(reasoning_parts) + "Advertencia escrita recomendada devido a gravidade.",
                [DisciplinaryActionType.ADVERTENCIA_VERBAL],
            )

        return (
            DisciplinaryActionType.ADVERTENCIA_VERBAL,
            0.90,
            " ".join(reasoning_parts) + "Advertencia verbal e adequada para primeira ocorrencia.",
            [DisciplinaryActionType.ADVERTENCIA_ESCRITA],
        )

    def _get_legal_references(
        self,
        category: ReasonCategory,
        action_type: DisciplinaryActionType,
    ) -> list[str]:
        """
        Obtem referencias legais aplicaveis.

        Args:
            category: Categoria do motivo
            action_type: Tipo da medida

        Returns:
            Lista de referencias
        """
        references = []

        # Sempre incluir art 482 para justa causa
        if action_type == DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA:
            references.append(self.CLT_ARTICLES["art_482"])

        # Sempre incluir art 474 para suspensao
        if action_type == DisciplinaryActionType.SUSPENSAO:
            references.append(self.CLT_ARTICLES["art_474"])

        # Alineas especificas
        category_articles = {
            ReasonCategory.ATO_IMPROBIDADE: "art_482_a",
            ReasonCategory.NEGLIGENCIA: "art_482_e",
            ReasonCategory.EMBRIAGUEZ: "art_482_f",
            ReasonCategory.INSUBORDINACAO: "art_482_h",
            ReasonCategory.INDISCIPLINA: "art_482_h",
            ReasonCategory.ABANDONO_EMPREGO: "art_482_i",
            ReasonCategory.OFENSA_MORAL: "art_482_j",
            ReasonCategory.OFENSA_FISICA: "art_482_k",
        }

        if category in category_articles:
            art_key = category_articles[category]
            if art_key in self.CLT_ARTICLES:
                references.append(self.CLT_ARTICLES[art_key])

        return references

    async def validate_legal_compliance(
        self,
        request: LegalComplianceRequest,
        tenant_id: str,
    ) -> LegalComplianceResponse:
        """
        Valida conformidade legal de uma medida.

        Args:
            request: Dados da medida
            tenant_id: ID do tenant

        Returns:
            Resultado da validacao
        """
        issues: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []
        clt_articles: list[str] = []

        # 1. Validar principio da imediaticidade
        days_since_incident = (request.application_date - request.incident_date).days
        if days_since_incident > 30:
            issues.append(
                f"IMEDIATICIDADE: Medida aplicada {days_since_incident} dias apos o incidente. "
                "Jurisprudencia recomenda aplicacao em ate 30 dias."
            )
            recommendations.append(
                "Aplique medidas disciplinares o mais proximo possivel do fato para evitar alegacao de perdao tacito."
            )

        # 2. Validar limite de suspensao
        if request.action_type == DisciplinaryActionType.SUSPENSAO:
            clt_articles.append(self.CLT_ARTICLES["art_474"])
            if request.suspension_days and request.suspension_days > 30:
                issues.append(f"SUSPENSAO: {request.suspension_days} dias excede limite de 30 dias (Art. 474 CLT)")

        # 3. Validar progressao disciplinar
        if request.action_type == DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA:
            clt_articles.append(self.CLT_ARTICLES["art_482"])
            if request.previous_warnings == 0 and request.previous_suspensions == 0:
                # Verificar se e falta grave
                if request.reason_category not in self.GRAVE_CATEGORIES:
                    warnings.append(
                        "PROGRESSAO: Justa causa sem medidas anteriores e falta nao classificada como grave. "
                        "Pode ser revertida em acao trabalhista."
                    )
                    recommendations.append(
                        "Considere aplicar advertencia ou suspensao primeiro, "
                        "exceto em casos de falta grave comprovada."
                    )

        if request.action_type == DisciplinaryActionType.SUSPENSAO:
            if request.previous_warnings == 0:
                warnings.append("PROGRESSAO: Suspensao sem advertencia previa. Recomenda-se progressao gradativa.")

        # 4. Validar dupla punicao
        # (Nao implementado aqui - precisaria verificar se ja existe medida para o mesmo incidente)

        is_compliant = len(issues) == 0

        return LegalComplianceResponse(
            is_compliant=is_compliant,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
            clt_articles=clt_articles,
        )

    async def check_proportionality(
        self,
        request: ProportionalityCheckRequest,
    ) -> ProportionalityCheckResponse:
        """
        Verifica proporcionalidade da medida.

        Args:
            request: Dados para verificacao

        Returns:
            Resultado da verificacao
        """
        score = 1.0
        analysis_parts: list[str] = []
        suggested_action: DisciplinaryActionType | None = None

        # Pontuacao baseada em historico
        expected_action = self._get_expected_action(
            request.previous_warnings,
            request.previous_suspensions,
            request.reason_category in self.GRAVE_CATEGORIES,
        )

        if request.action_type == expected_action:
            analysis_parts.append(
                f"Medida proporcional ao historico ({request.previous_warnings} advertencias, "
                f"{request.previous_suspensions} suspensoes)."
            )
        elif self._is_more_severe(request.action_type, expected_action):
            score -= 0.3
            suggested_action = expected_action
            analysis_parts.append(f"Medida mais severa que o esperado. Sugestao: {expected_action.value}.")
        else:
            score -= 0.1
            analysis_parts.append("Medida menos severa que o esperado, mas aceitavel.")

        # Ajuste por tempo de empresa
        if request.employee_tenure_days > 365 * 5:  # Mais de 5 anos
            if request.action_type == DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA:
                score -= 0.1
                analysis_parts.append(
                    "Funcionario com mais de 5 anos de empresa. Considerar historico completo antes de justa causa."
                )

        # Ajuste por gravidade
        if request.reason_category in self.GRAVE_CATEGORIES:
            if request.action_type in [
                DisciplinaryActionType.ADVERTENCIA_VERBAL,
                DisciplinaryActionType.ADVERTENCIA_ESCRITA,
            ]:
                score -= 0.2
                analysis_parts.append("Falta classificada como grave. Medida pode ser insuficiente.")

        is_proportional = score >= 0.6

        return ProportionalityCheckResponse(
            is_proportional=is_proportional,
            score=max(0, min(1, score)),
            analysis=" ".join(analysis_parts),
            suggested_action=suggested_action,
            reasoning=" ".join(analysis_parts),
        )

    def _get_expected_action(
        self,
        warnings: int,
        suspensions: int,
        is_grave: bool,
    ) -> DisciplinaryActionType:
        """Determina acao esperada baseada no historico."""
        if suspensions >= 2 or (suspensions >= 1 and is_grave):
            return DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA
        if suspensions >= 1 or warnings >= 3 or (warnings >= 1 and is_grave):
            return DisciplinaryActionType.SUSPENSAO
        if warnings >= 1:
            return DisciplinaryActionType.ADVERTENCIA_ESCRITA
        return DisciplinaryActionType.ADVERTENCIA_VERBAL

    def _is_more_severe(
        self,
        action1: DisciplinaryActionType,
        action2: DisciplinaryActionType,
    ) -> bool:
        """Verifica se action1 e mais severa que action2."""
        severity = {
            DisciplinaryActionType.ADVERTENCIA_VERBAL: 1,
            DisciplinaryActionType.ADVERTENCIA_ESCRITA: 2,
            DisciplinaryActionType.SUSPENSAO: 3,
            DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA: 4,
        }
        return severity.get(action1, 0) > severity.get(action2, 0)

    def generate_reason_text(
        self,
        category: ReasonCategory,
        incident_description: str,
        incident_date: date,
    ) -> str:
        """
        Gera texto sugerido para o motivo da medida.

        Args:
            category: Categoria do motivo
            incident_description: Descricao do incidente
            incident_date: Data do incidente

        Returns:
            Texto sugerido
        """
        category_templates = {
            ReasonCategory.FALTA: (
                f"O(A) funcionario(a) faltou ao trabalho no dia {incident_date.strftime('%d/%m/%Y')} "
                f"sem apresentar justificativa legal. {incident_description}"
            ),
            ReasonCategory.ATRASO: (
                f"O(A) funcionario(a) apresentou atraso injustificado no dia {incident_date.strftime('%d/%m/%Y')}. "
                f"{incident_description}"
            ),
            ReasonCategory.INSUBORDINACAO: (
                f"O(A) funcionario(a) cometeu ato de insubordinacao no dia {incident_date.strftime('%d/%m/%Y')}, "
                f"descumprindo ordens diretas de superior hierarquico. {incident_description}"
            ),
            ReasonCategory.NEGLIGENCIA: (
                f"O(A) funcionario(a) demonstrou negligencia no desempenho de suas funcoes "
                f"no dia {incident_date.strftime('%d/%m/%Y')}. {incident_description}"
            ),
            ReasonCategory.ABANDONO_EMPREGO: (
                f"O(A) funcionario(a) encontra-se ausente do trabalho desde {incident_date.strftime('%d/%m/%Y')}, "
                f"sem qualquer justificativa, caracterizando abandono de emprego. {incident_description}"
            ),
        }

        if category in category_templates:
            return category_templates[category]

        return (
            f"No dia {incident_date.strftime('%d/%m/%Y')}, o(a) funcionario(a) cometeu "
            f"a seguinte infração: {incident_description}"
        )


def get_disciplinary_advisor(db: AsyncSession) -> DisciplinaryAdvisor:
    """
    Factory para criar instancia do advisor.

    Args:
        db: Sessao do banco de dados

    Returns:
        Instancia do DisciplinaryAdvisor
    """
    return DisciplinaryAdvisor(db)
