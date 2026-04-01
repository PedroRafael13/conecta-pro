"""
Servico de Analise de Risco de Turnover.

Implementa analises avancadas de fatores de risco, deteccao de
mudancas, geracao de recomendacoes e comparativos para o
dashboard de turnover.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.retention.turnover.models.turnover_models import (
    CategoriaFator,
    RiskAlert,
    RiskFactor,
    TurnoverPrediction,
)
from modules.retention.turnover.repositories.turnover_repository import (
    TurnoverRepository,
)
from modules.retention.turnover.schemas.turnover_schemas import (
    DashboardDistribuicaoNivel,
    DashboardFatorFrequente,
    DashboardResponse,
    DashboardTendencia,
    FatorAgregadoResponse,
    HistoricoItemResponse,
    HistoricoResponse,
    RiskFactorSummary,
)

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """
    Servico de analise de risco de turnover.

    Fornece analises detalhadas, recomendacoes, deteccao de mudancas
    e dados para o dashboard de turnover.
    """

    # Mapeamento de recomendacoes por tipo de fator
    RECOMENDACOES_PADRAO: dict[str, list[str]] = {
        "faltas_ultimo_mes": [
            "Agendar conversa individual com o funcionario",
            "Verificar situacao pessoal e familiar",
            "Avaliar adequacao do posto de trabalho",
            "Considerar programa de flexibilidade de horarios",
        ],
        "atrasos_ultimo_mes": [
            "Avaliar problemas de transporte",
            "Verificar distancia residencia-trabalho",
            "Considerar ajuste de escala",
            "Oferecer suporte para questoes pessoais",
        ],
        "ocorrencias_trimestre": [
            "Revisar historico completo de ocorrencias",
            "Aplicar feedback construtivo",
            "Avaliar necessidade de treinamento",
            "Verificar adequacao ao cargo/funcao",
        ],
        "advertencias_total": [
            "Avaliar historico disciplinar",
            "Elaborar plano de desenvolvimento individual",
            "Considerar coaching ou mentoria",
            "Verificar questoes de ambiente de trabalho",
        ],
        "score_clima_atual": [
            "Analisar detalhadamente respostas da pesquisa",
            "Identificar areas de insatisfacao",
            "Promover conversa aberta sobre expectativas",
            "Implementar melhorias pontuais identificadas",
        ],
        "tendencia_clima": [
            "Investigar causas da queda de engajamento",
            "Realizar reuniao de feedback",
            "Verificar mudancas recentes no ambiente",
            "Implementar acoes corretivas rapidas",
        ],
        "distancia_casa_posto_km": [
            "Avaliar realocacao para posto mais proximo",
            "Considerar auxilio transporte adicional",
            "Verificar opcoes de home office parcial",
            "Otimizar escalas para reduzir deslocamentos",
        ],
        "horas_extras_media": [
            "Revisar distribuicao de carga de trabalho",
            "Avaliar necessidade de contratacao",
            "Verificar eficiencia operacional",
            "Monitorar riscos de burnout",
        ],
        "tempo_empresa_meses": [
            "Fortalecer processo de onboarding",
            "Designar mentor/padrinho",
            "Acompanhamento frequente nos primeiros meses",
            "Criar programa de integracao social",
        ],
        "dias_sem_aumento": [
            "Revisar politica de remuneracao",
            "Avaliar mercado para o cargo",
            "Considerar beneficios nao salariais",
            "Planejar reconhecimento e promocoes",
        ],
    }

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa o servico.

        Args:
            session: Sessao do banco de dados
        """
        self.session = session
        self.repository = TurnoverRepository(session)

    # =========================================================================
    # Factor Analysis
    # =========================================================================

    async def analisar_fatores(
        self,
        prediction: TurnoverPrediction,
    ) -> list[dict[str, Any]]:
        """
        Analisa os fatores de risco de uma predicao.

        Args:
            prediction: Predicao a ser analisada

        Returns:
            Lista de fatores com analise detalhada
        """
        analises = []

        for fator in prediction.fatores:
            analise = {
                "id": str(fator.id),
                "nome": fator.nome,
                "nome_legivel": self._formatar_nome_fator(fator.nome),
                "categoria": fator.categoria.value,
                "valor_atual": float(fator.valor_atual),
                "valor_normalizado": float(fator.valor_normalizado),
                "contribuicao_score": float(fator.contribuicao_score),
                "threshold_violado": fator.threshold_violado,
                "descricao": fator.descricao,
                "impacto": self._classificar_impacto(fator.contribuicao_score),
                "recomendacoes": self._get_recomendacoes_fator(fator.nome),
                "prioridade_acao": self._calcular_prioridade_acao(fator),
            }
            analises.append(analise)

        # Ordenar por contribuicao
        analises.sort(key=lambda x: x["contribuicao_score"], reverse=True)

        return analises

    async def gerar_recomendacoes(
        self,
        fatores: list[RiskFactor],
        max_recomendacoes: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Gera lista priorizada de recomendacoes baseada nos fatores.

        Args:
            fatores: Lista de fatores de risco
            max_recomendacoes: Maximo de recomendacoes a retornar

        Returns:
            Lista de recomendacoes priorizadas
        """
        recomendacoes_todas = []

        for fator in fatores:
            if not fator.threshold_violado:
                continue

            recs = self._get_recomendacoes_fator(fator.nome)
            for rec in recs[:2]:  # Pegar top 2 de cada fator
                recomendacoes_todas.append(
                    {
                        "texto": rec,
                        "fator_origem": fator.nome,
                        "categoria": fator.categoria.value,
                        "prioridade": self._calcular_prioridade_acao(fator),
                        "impacto_estimado": self._estimar_impacto_acao(fator),
                    }
                )

        # Ordenar por prioridade e impacto
        recomendacoes_todas.sort(key=lambda x: (x["prioridade"], -x["impacto_estimado"]))

        # Remover duplicatas mantendo ordem
        textos_vistos = set()
        recomendacoes_unicas = []
        for rec in recomendacoes_todas:
            if rec["texto"] not in textos_vistos:
                textos_vistos.add(rec["texto"])
                recomendacoes_unicas.append(rec)

        return recomendacoes_unicas[:max_recomendacoes]

    def _formatar_nome_fator(self, nome: str) -> str:
        """Formata nome do fator para exibicao."""
        mapeamento = {
            "faltas_ultimo_mes": "Faltas no Ultimo Mes",
            "atrasos_ultimo_mes": "Atrasos no Ultimo Mes",
            "ocorrencias_trimestre": "Ocorrencias no Trimestre",
            "advertencias_total": "Total de Advertencias",
            "score_clima_atual": "Score de Clima Organizacional",
            "tendencia_clima": "Tendencia do Clima",
            "distancia_casa_posto_km": "Distancia Casa-Trabalho",
            "horas_extras_media": "Media de Horas Extras",
            "tempo_empresa_meses": "Tempo de Empresa",
            "dias_sem_aumento": "Dias sem Reajuste Salarial",
        }
        return mapeamento.get(nome, nome.replace("_", " ").title())

    def _classificar_impacto(
        self,
        contribuicao: Decimal,
    ) -> str:
        """Classifica o impacto do fator no score."""
        contrib = float(contribuicao)
        if contrib >= 15:
            return "muito_alto"
        if contrib >= 10:
            return "alto"
        if contrib >= 5:
            return "medio"
        if contrib >= 2:
            return "baixo"
        return "minimo"

    def _get_recomendacoes_fator(self, nome: str) -> list[str]:
        """Retorna recomendacoes para um fator especifico."""
        return self.RECOMENDACOES_PADRAO.get(
            nome,
            [
                "Analisar situacao especifica do funcionario",
                "Conversar com gestor direto",
                "Verificar historico recente",
            ],
        )

    def _calcular_prioridade_acao(self, fator: RiskFactor) -> int:
        """Calcula prioridade de acao (1=maxima, 5=minima)."""
        contrib = float(fator.contribuicao_score)

        if contrib >= 15:
            return 1
        if contrib >= 10:
            return 2
        if contrib >= 5:
            return 3
        if fator.threshold_violado:
            return 4
        return 5

    def _estimar_impacto_acao(self, fator: RiskFactor) -> float:
        """Estima impacto potencial de acao corretiva."""
        # Fatores comportamentais tem maior impacto de acao
        multiplicador_categoria = {
            CategoriaFator.COMPORTAMENTAL: 1.2,
            CategoriaFator.ENGAJAMENTO: 1.3,
            CategoriaFator.OPERACIONAL: 1.0,
            CategoriaFator.CONTEXTUAL: 0.8,
        }

        mult = multiplicador_categoria.get(fator.categoria, 1.0)
        return float(fator.contribuicao_score) * mult

    # =========================================================================
    # Change Detection
    # =========================================================================

    async def detectar_mudancas(
        self,
        funcionario_id: UUID,
        condominium_id: UUID,
    ) -> dict[str, Any] | None:
        """
        Detecta mudancas significativas no risco do funcionario.

        Args:
            funcionario_id: ID do funcionario
            condominium_id: ID do condominio

        Returns:
            Dict com detalhes das mudancas ou None
        """
        # Buscar historico
        historico = await self.repository.get_predictions_by_funcionario(funcionario_id, limit=5)

        if len(historico) < 2:
            return None

        atual = historico[0]
        anterior = historico[1]

        score_atual = float(atual.score_risco)
        score_anterior = float(anterior.score_risco)
        variacao = score_atual - score_anterior

        mudancas = {
            "funcionario_id": str(funcionario_id),
            "score_atual": score_atual,
            "score_anterior": score_anterior,
            "variacao": round(variacao, 2),
            "nivel_atual": atual.nivel.value,
            "nivel_anterior": anterior.nivel.value,
            "nivel_mudou": atual.nivel != anterior.nivel,
            "tendencia": self._classificar_tendencia(variacao),
            "fatores_novos": [],
            "fatores_agravados": [],
            "fatores_melhorados": [],
        }

        # Comparar fatores
        fatores_anterior = {f.nome: f for f in anterior.fatores}
        fatores_atual = {f.nome: f for f in atual.fatores}

        for nome, fator in fatores_atual.items():
            fator_ant = fatores_anterior.get(nome)

            if not fator_ant:
                mudancas["fatores_novos"].append(nome)
            else:
                contrib_atual = float(fator.contribuicao_score)
                contrib_ant = float(fator_ant.contribuicao_score)
                diff = contrib_atual - contrib_ant

                if diff >= 3:  # Aumento significativo
                    mudancas["fatores_agravados"].append(
                        {
                            "nome": nome,
                            "variacao": round(diff, 2),
                            "atual": contrib_atual,
                            "anterior": contrib_ant,
                        }
                    )
                elif diff <= -3:  # Melhoria significativa
                    mudancas["fatores_melhorados"].append(
                        {
                            "nome": nome,
                            "variacao": round(diff, 2),
                            "atual": contrib_atual,
                            "anterior": contrib_ant,
                        }
                    )

        return mudancas

    def _classificar_tendencia(self, variacao: float) -> str:
        """Classifica a tendencia baseada na variacao."""
        if variacao >= 15:
            return "alta_acelerada"
        if variacao >= 5:
            return "alta"
        if variacao >= 2:
            return "leve_alta"
        if variacao <= -15:
            return "queda_acelerada"
        if variacao <= -5:
            return "queda"
        if variacao <= -2:
            return "leve_queda"
        return "estavel"

    # =========================================================================
    # Dashboard Data
    # =========================================================================

    async def get_dashboard_data(
        self,
        condominium_id: UUID,
        setor_id: UUID | None = None,
    ) -> DashboardResponse:
        """
        Retorna dados consolidados para o dashboard.

        Args:
            condominium_id: ID do condominio
            setor_id: Filtrar por setor (opcional)

        Returns:
            DashboardResponse com todos os dados
        """
        agora = datetime.utcnow()
        inicio_mes = agora - timedelta(days=30)

        # Metricas basicas
        total_predicoes = await self.repository.count_active_predictions(condominium_id)
        score_medio = await self.repository.get_average_score(condominium_id)

        # Distribuicao por nivel
        distribuicao_raw = await self.repository.get_distribution_by_nivel(condominium_id)

        total_funcionarios = sum(d["quantidade"] for d in distribuicao_raw)

        distribuicao = [
            DashboardDistribuicaoNivel(
                nivel=d["nivel"],
                quantidade=d["quantidade"],
                percentual=Decimal(
                    str(round(d["quantidade"] / total_funcionarios * 100, 2) if total_funcionarios > 0 else 0)
                ),
            )
            for d in distribuicao_raw
        ]

        # Alertas
        alertas_pendentes = len(await self.repository.get_pending_alerts(condominium_id, limit=1000))
        alertas_mes = await self.repository.count_alerts_by_period(condominium_id, inicio_mes)

        # Top fatores
        fatores_agregados = await self.repository.get_aggregated_factors(condominium_id)
        fatores_frequentes = [
            DashboardFatorFrequente(
                nome=f["nome"],
                categoria=f["categoria"],
                ocorrencias=f["total_ocorrencias"],
                contribuicao_media=Decimal(str(f["contribuicao_media"])),
            )
            for f in fatores_agregados[:10]
        ]

        # Tendencia
        tendencia_raw = await self.repository.get_trend_data(condominium_id, dias=30)
        tendencia = [
            DashboardTendencia(
                data=t["data"],
                score_medio=Decimal(str(t["score_medio"])),
                total_criticos=t["total_criticos"],
                total_altos=t["total_altos"],
            )
            for t in tendencia_raw
        ]

        # Variacao mensal
        variacao_score = None
        if len(tendencia_raw) >= 2:
            score_inicio = tendencia_raw[0]["score_medio"]
            score_fim = tendencia_raw[-1]["score_medio"]
            variacao_score = Decimal(str(round(score_fim - score_inicio, 2)))

        # Funcionarios com risco crescente/decrescente
        crescente, decrescente = await self.repository.get_score_variation(condominium_id, dias=30)

        return DashboardResponse(
            total_funcionarios=total_funcionarios,
            total_predicoes_ativas=total_predicoes,
            score_medio_geral=score_medio,
            distribuicao_niveis=distribuicao,
            alertas_pendentes=alertas_pendentes,
            alertas_ultimo_mes=alertas_mes,
            fatores_mais_frequentes=fatores_frequentes,
            tendencia_30_dias=tendencia,
            variacao_score_medio_mensal=variacao_score,
            funcionarios_risco_crescente=crescente,
            funcionarios_risco_decrescente=decrescente,
            data_atualizacao=agora,
        )

    # =========================================================================
    # History Analysis
    # =========================================================================

    async def get_historico_funcionario(
        self,
        funcionario_id: UUID,
        limite: int = 30,
    ) -> HistoricoResponse:
        """
        Retorna historico completo de predicoes do funcionario.

        Args:
            funcionario_id: ID do funcionario
            limite: Maximo de predicoes a retornar

        Returns:
            HistoricoResponse com analise temporal
        """
        predicoes = await self.repository.get_predictions_by_funcionario(funcionario_id, limit=limite)

        if not predicoes:
            return HistoricoResponse(
                funcionario_id=funcionario_id,
                total_predicoes=0,
                predicao_atual=None,
                historico=[],
            )

        predicoes[0]
        scores = [float(p.score_risco) for p in predicoes]

        # Calcular estatisticas
        score_minimo = min(scores)
        score_maximo = max(scores)
        score_medio = sum(scores) / len(scores)

        # Calcular tendencia
        tendencia = self._calcular_tendencia_historico(predicoes)

        # Montar historico
        historico_items = []
        for i, pred in enumerate(predicoes):
            variacao = None
            if i < len(predicoes) - 1:
                variacao = Decimal(str(float(pred.score_risco) - float(predicoes[i + 1].score_risco)))

            # Contar alertas
            alertas = len(pred.alertas) if hasattr(pred, "alertas") else 0

            # Principais fatores
            principais = [
                RiskFactorSummary(
                    nome=f.nome,
                    categoria=f.categoria,
                    contribuicao_score=f.contribuicao_score,
                    threshold_violado=f.threshold_violado,
                    descricao=f.descricao,
                )
                for f in sorted(pred.fatores, key=lambda x: x.contribuicao_score, reverse=True)[:3]
            ]

            historico_items.append(
                HistoricoItemResponse(
                    predicao_id=pred.id,
                    data_calculo=pred.data_calculo,
                    score_risco=pred.score_risco,
                    nivel=pred.nivel,
                    variacao_anterior=variacao,
                    alertas_gerados=alertas,
                    principais_fatores=principais,
                )
            )

        return HistoricoResponse(
            funcionario_id=funcionario_id,
            total_predicoes=len(predicoes),
            predicao_atual=None,  # Preenchido pelo controller
            score_minimo=Decimal(str(round(score_minimo, 2))),
            score_maximo=Decimal(str(round(score_maximo, 2))),
            score_medio=Decimal(str(round(score_medio, 2))),
            tendencia=tendencia,
            historico=historico_items,
        )

    def _calcular_tendencia_historico(
        self,
        predicoes: list[TurnoverPrediction],
    ) -> str:
        """Calcula tendencia baseada no historico."""
        if len(predicoes) < 3:
            return "insuficiente"

        # Pegar ultimas 5 predicoes
        recentes = predicoes[:5]
        scores = [float(p.score_risco) for p in recentes]

        # Calcular tendencia linear simples
        n = len(scores)
        soma_x = sum(range(n))
        soma_y = sum(scores)
        soma_xy = sum(i * s for i, s in enumerate(scores))
        soma_x2 = sum(i**2 for i in range(n))

        denominador = n * soma_x2 - soma_x**2
        if denominador == 0:
            return "estavel"

        inclinacao = (n * soma_xy - soma_x * soma_y) / denominador

        # Scores mais recentes tem indice menor, entao inclinacao negativa
        # significa aumento (risco crescente)
        if inclinacao < -3:
            return "crescente"
        if inclinacao > 3:
            return "decrescente"
        return "estavel"

    # =========================================================================
    # Aggregated Factors
    # =========================================================================

    async def get_fatores_agregados(
        self,
        condominium_id: UUID,
        categoria: CategoriaFator | None = None,
    ) -> list[FatorAgregadoResponse]:
        """
        Retorna estatisticas agregadas dos fatores de risco.

        Args:
            condominium_id: ID do condominio
            categoria: Filtrar por categoria

        Returns:
            Lista de fatores com estatisticas
        """
        fatores_raw = await self.repository.get_aggregated_factors(condominium_id, categoria)

        resultado = []
        for f in fatores_raw:
            recomendacoes = self.RECOMENDACOES_PADRAO.get(f["nome"], ["Analisar situacao especifica"])

            resultado.append(
                FatorAgregadoResponse(
                    nome=f["nome"],
                    categoria=f["categoria"],
                    total_ocorrencias=f["total_ocorrencias"],
                    contribuicao_media=Decimal(str(f["contribuicao_media"])),
                    contribuicao_maxima=Decimal(str(f["contribuicao_maxima"])),
                    percentual_threshold_violado=Decimal(str(f["percentual_threshold_violado"])),
                    funcionarios_afetados=f["funcionarios_afetados"],
                    descricao_padrao=self._formatar_nome_fator(f["nome"]),
                    recomendacoes_comuns=recomendacoes[:3],
                )
            )

        return resultado

    # =========================================================================
    # Alert Management
    # =========================================================================

    async def get_alertas_pendentes(
        self,
        condominium_id: UUID,
        limite: int = 50,
    ) -> list[RiskAlert]:
        """Retorna alertas pendentes de visualizacao."""
        return await self.repository.get_pending_alerts(condominium_id, limite)

    async def marcar_alerta_visualizado(
        self,
        alert_id: UUID,
        usuario_id: UUID,
    ) -> RiskAlert | None:
        """Marca alerta como visualizado."""
        return await self.repository.mark_alert_visualizado(alert_id, usuario_id)

    async def registrar_acao_alerta(
        self,
        alert_id: UUID,
        acao: str,
        usuario_id: UUID,
    ) -> RiskAlert | None:
        """Registra acao tomada em alerta."""
        return await self.repository.register_alert_action(alert_id, acao, usuario_id)

    # =========================================================================
    # Audit
    # =========================================================================

    async def registrar_acesso_auditoria(
        self,
        usuario_id: UUID,
        condominium_id: UUID,
        acao: str,
        recurso: str,
        recurso_id: UUID | None = None,
        funcionario_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Registra acesso para auditoria."""
        await self.repository.create_audit_log(
            usuario_id=usuario_id,
            condominium_id=condominium_id,
            acao=acao,
            recurso=recurso,
            recurso_id=recurso_id,
            funcionario_id=funcionario_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
