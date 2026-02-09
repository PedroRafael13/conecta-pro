"""
Servico de Predicao de Turnover.

Implementa a logica de calculo de risco de turnover usando
algoritmo heuristico baseado em features comportamentais,
de engajamento, operacionais e contextuais.

Importante: Score NUNCA visivel para o funcionario.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.retention.turnover.models.turnover_models import (
    CategoriaFator,
    NivelRisco,
    RiskAlert,
    TipoAlerta,
    TurnoverPrediction,
)
from modules.retention.turnover.repositories.turnover_repository import (
    TurnoverRepository,
)
from modules.retention.turnover.schemas.turnover_schemas import (
    AlertCreate,
    PredictionCreate,
    RecalcularBatchResponse,
    RecalcularResponse,
    RiskFactorCreate,
)

logger = logging.getLogger(__name__)


@dataclass
class FeatureDefinition:
    """Definicao de uma feature do modelo."""

    nome: str
    categoria: CategoriaFator
    peso: float
    descricao: str
    threshold_alto: float | None = None
    threshold_baixo: float | None = None
    threshold_negativo: float | None = None
    threshold_critico: float | None = None
    inversao: bool = False  # True se maior valor = menor risco
    recomendacao_template: str = ""


# =============================================================================
# Feature Definitions
# =============================================================================

FEATURES_CONFIG: dict[str, FeatureDefinition] = {
    # Comportamentais (peso alto)
    "faltas_ultimo_mes": FeatureDefinition(
        nome="faltas_ultimo_mes",
        categoria=CategoriaFator.COMPORTAMENTAL,
        peso=0.15,
        descricao="Numero de faltas no ultimo mes",
        threshold_alto=2,
        recomendacao_template=(
            "Agendar conversa individual para entender motivos das faltas. Verificar situacao pessoal/familiar."
        ),
    ),
    "atrasos_ultimo_mes": FeatureDefinition(
        nome="atrasos_ultimo_mes",
        categoria=CategoriaFator.COMPORTAMENTAL,
        peso=0.10,
        descricao="Numero de atrasos no ultimo mes",
        threshold_alto=5,
        recomendacao_template=(
            "Avaliar problemas de transporte ou escala. Considerar flexibilizacao de horario se aplicavel."
        ),
    ),
    "ocorrencias_trimestre": FeatureDefinition(
        nome="ocorrencias_trimestre",
        categoria=CategoriaFator.COMPORTAMENTAL,
        peso=0.12,
        descricao="Ocorrencias disciplinares no ultimo trimestre",
        threshold_alto=2,
        recomendacao_template=("Revisar historico de ocorrencias. Aplicar medidas corretivas ou oferecer suporte."),
    ),
    "advertencias_total": FeatureDefinition(
        nome="advertencias_total",
        categoria=CategoriaFator.COMPORTAMENTAL,
        peso=0.15,
        descricao="Total de advertencias no historico",
        threshold_alto=1,
        threshold_critico=3,
        recomendacao_template=("Avaliar gravidade e frequencia das advertencias. Considerar plano de desenvolvimento."),
    ),
    # Engajamento (peso alto)
    "score_clima_atual": FeatureDefinition(
        nome="score_clima_atual",
        categoria=CategoriaFator.ENGAJAMENTO,
        peso=0.18,
        descricao="Score da ultima pesquisa de clima (1-5)",
        threshold_baixo=2.5,
        threshold_critico=2.0,
        inversao=True,  # Maior score = menor risco
        recomendacao_template=(
            "Analisar respostas da pesquisa de clima. Identificar areas de insatisfacao e agir proativamente."
        ),
    ),
    "tendencia_clima": FeatureDefinition(
        nome="tendencia_clima",
        categoria=CategoriaFator.ENGAJAMENTO,
        peso=0.08,
        descricao="Variacao do score de clima vs. medicao anterior",
        threshold_negativo=-0.3,
        inversao=True,  # Tendencia positiva = menor risco
        recomendacao_template=(
            "Investigar causa da queda no engajamento. Conversa individual para entender preocupacoes."
        ),
    ),
    # Operacionais (peso medio)
    "distancia_casa_posto_km": FeatureDefinition(
        nome="distancia_casa_posto_km",
        categoria=CategoriaFator.OPERACIONAL,
        peso=0.05,
        descricao="Distancia em km entre residencia e posto de trabalho",
        threshold_alto=20,
        threshold_critico=40,
        recomendacao_template=(
            "Avaliar possibilidade de realocacao para posto mais proximo. Considerar auxilio transporte adicional."
        ),
    ),
    "horas_extras_media": FeatureDefinition(
        nome="horas_extras_media",
        categoria=CategoriaFator.OPERACIONAL,
        peso=0.05,
        descricao="Media de horas extras mensais",
        threshold_alto=30,
        threshold_critico=50,
        recomendacao_template=(
            "Verificar necessidade de contratacao adicional. Equilibrar carga de trabalho entre equipe."
        ),
    ),
    "tempo_empresa_meses": FeatureDefinition(
        nome="tempo_empresa_meses",
        categoria=CategoriaFator.OPERACIONAL,
        peso=0.07,
        descricao="Tempo de empresa em meses",
        threshold_critico=3,
        inversao=True,  # Mais tempo = menor risco
        recomendacao_template=(
            "Fortalecer onboarding e acompanhamento inicial. Designar mentor para novos colaboradores."
        ),
    ),
    # Contextuais (peso baixo)
    "dias_sem_aumento": FeatureDefinition(
        nome="dias_sem_aumento",
        categoria=CategoriaFator.CONTEXTUAL,
        peso=0.05,
        descricao="Dias desde o ultimo reajuste salarial",
        threshold_alto=365,
        threshold_critico=730,
        recomendacao_template=("Avaliar politica de remuneracao. Considerar ajuste salarial ou beneficios adicionais."),
    ),
}


class TurnoverPredictor:
    """
    Servico de predicao de risco de turnover.

    Calcula o score de risco de turnover para funcionarios
    usando um modelo heuristico baseado em multiplas features.
    """

    MODELO_VERSAO = "heuristic_v1.0"
    THRESHOLD_ALERTA = 70.0  # Score minimo para gerar alerta
    THRESHOLD_AUMENTO_SIGNIFICATIVO = 15.0  # Variacao para alerta

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa o servico.

        Args:
            session: Sessao do banco de dados
        """
        self.session = session
        self.repository = TurnoverRepository(session)
        self._features = FEATURES_CONFIG

    # =========================================================================
    # Main Prediction Methods
    # =========================================================================

    async def calcular_risco(
        self,
        funcionario_id: UUID,
        condominium_id: UUID,
        dados_funcionario: dict[str, Any],
        calculado_por: UUID | None = None,
    ) -> TurnoverPrediction:
        """
        Calcula o risco de turnover para um funcionario.

        Args:
            funcionario_id: ID do funcionario
            condominium_id: ID do condominio
            dados_funcionario: Dados do funcionario para calculo
            calculado_por: Usuario que solicitou (None = sistema)

        Returns:
            TurnoverPrediction com o resultado do calculo
        """
        logger.info(f"Calculando risco para funcionario {funcionario_id}")

        # 1. Buscar predicao anterior para comparacao
        predicao_anterior = await self.repository.get_latest_prediction(funcionario_id)

        # 2. Calcular features e score
        features_calculadas = self._calcular_features(dados_funcionario)
        score, fatores_detalhados = self._calcular_score_heuristico(features_calculadas)
        nivel = TurnoverPrediction.calcular_nivel(score)

        # 3. Marcar predicoes anteriores como recalculadas
        await self.repository.mark_prediction_recalculado(funcionario_id)

        # 4. Criar nova predicao
        prediction_data = PredictionCreate(
            funcionario_id=funcionario_id,
            condominium_id=condominium_id,
            score_risco=Decimal(str(score)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            nivel=nivel,
            modelo_versao=self.MODELO_VERSAO,
            features_usadas=features_calculadas,
            metricas_modelo=self._get_metricas_modelo(),
            valido_ate=datetime.utcnow() + timedelta(days=7),
            calculado_por=calculado_por,
        )

        prediction = await self.repository.create_prediction(prediction_data)

        # 5. Criar fatores de risco
        fatores_to_create = [
            RiskFactorCreate(
                prediction_id=prediction.id,
                nome=f["nome"],
                categoria=f["categoria"],
                peso=Decimal(str(f["peso"])),
                valor_atual=Decimal(str(f["valor_atual"])),
                valor_normalizado=Decimal(str(f["valor_normalizado"])),
                contribuicao_score=Decimal(str(f["contribuicao"])),
                threshold_violado=f["threshold_violado"],
                descricao=f["descricao"],
                recomendacao_acao=f.get("recomendacao"),
                dados_brutos=f.get("dados_brutos"),
            )
            for f in fatores_detalhados
        ]

        fatores = await self.repository.create_risk_factors(fatores_to_create)
        prediction.fatores = fatores

        # 6. Verificar necessidade de alerta
        await self._verificar_e_criar_alerta(
            prediction=prediction,
            predicao_anterior=predicao_anterior,
            condominium_id=condominium_id,
        )

        logger.info(f"Predicao calculada: funcionario={funcionario_id}, score={score:.2f}, nivel={nivel.value}")

        return prediction

    async def calcular_risco_batch(
        self,
        funcionarios_dados: list[dict[str, Any]],
        condominium_id: UUID,
        calculado_por: UUID | None = None,
    ) -> RecalcularBatchResponse:
        """
        Calcula risco em lote para multiplos funcionarios.

        Args:
            funcionarios_dados: Lista com dados de cada funcionario
            condominium_id: ID do condominio
            calculado_por: Usuario que solicitou

        Returns:
            RecalcularBatchResponse com estatisticas
        """
        inicio = datetime.utcnow()
        total_sucesso = 0
        total_erros = 0
        alertas_gerados = 0
        erros: list[dict[str, Any]] = []

        for dados in funcionarios_dados:
            try:
                funcionario_id = dados.get("funcionario_id")
                if not funcionario_id:
                    continue

                prediction = await self.calcular_risco(
                    funcionario_id=UUID(funcionario_id) if isinstance(funcionario_id, str) else funcionario_id,
                    condominium_id=condominium_id,
                    dados_funcionario=dados,
                    calculado_por=calculado_por,
                )

                total_sucesso += 1
                if prediction.is_alerta_necessario:
                    alertas_gerados += 1

            except Exception as e:
                total_erros += 1
                erros.append(
                    {
                        "funcionario_id": str(dados.get("funcionario_id")),
                        "erro": str(e),
                    }
                )
                logger.error(f"Erro ao calcular risco para {dados.get('funcionario_id')}: {e}")

        tempo_execucao = (datetime.utcnow() - inicio).total_seconds()

        logger.info(
            f"Batch concluido: {total_sucesso} sucesso, "
            f"{total_erros} erros, {alertas_gerados} alertas, "
            f"{tempo_execucao:.2f}s"
        )

        return RecalcularBatchResponse(
            total_processados=len(funcionarios_dados),
            total_sucesso=total_sucesso,
            total_erros=total_erros,
            alertas_gerados=alertas_gerados,
            tempo_execucao_segundos=round(tempo_execucao, 2),
            erros=erros,
        )

    async def recalcular_funcionario(
        self,
        funcionario_id: UUID,
        condominium_id: UUID,
        dados_funcionario: dict[str, Any],
        calculado_por: UUID,
    ) -> RecalcularResponse:
        """
        Recalcula risco de um funcionario especifico.

        Args:
            funcionario_id: ID do funcionario
            condominium_id: ID do condominio
            dados_funcionario: Dados atualizados
            calculado_por: Usuario que solicitou

        Returns:
            RecalcularResponse com comparacao
        """
        # Buscar predicao anterior
        predicao_anterior = await self.repository.get_latest_prediction(funcionario_id)

        score_anterior = predicao_anterior.score_risco if predicao_anterior else None
        nivel_anterior = predicao_anterior.nivel if predicao_anterior else None

        # Calcular novo risco
        prediction = await self.calcular_risco(
            funcionario_id=funcionario_id,
            condominium_id=condominium_id,
            dados_funcionario=dados_funcionario,
            calculado_por=calculado_por,
        )

        alerta_gerado = prediction.is_alerta_necessario

        return RecalcularResponse(
            funcionario_id=funcionario_id,
            predicao_id=prediction.id,
            score_anterior=score_anterior,
            score_novo=prediction.score_risco,
            nivel_anterior=nivel_anterior,
            nivel_novo=prediction.nivel,
            alerta_gerado=alerta_gerado,
            data_calculo=prediction.data_calculo,
        )

    # =========================================================================
    # Feature Calculation
    # =========================================================================

    def _calcular_features(
        self,
        dados: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extrai e normaliza features dos dados do funcionario.

        Args:
            dados: Dados brutos do funcionario

        Returns:
            Dict com features normalizadas
        """
        features = {}

        for nome, config in self._features.items():
            valor = dados.get(nome)

            if valor is None:
                # Usar valor neutro se nao disponivel
                valor = self._get_valor_neutro(config)

            features[nome] = {
                "valor_bruto": valor,
                "valor_normalizado": self._normalizar_feature(valor, config),
                "peso": config.peso,
                "categoria": config.categoria.value,
            }

        return features

    def _normalizar_feature(
        self,
        valor: Any,
        config: FeatureDefinition,
    ) -> float:
        """
        Normaliza valor da feature para escala 0-1.

        Valor normalizado representa o nivel de risco:
        - 0 = risco minimo
        - 1 = risco maximo

        Args:
            valor: Valor bruto da feature
            config: Configuracao da feature

        Returns:
            Valor normalizado entre 0 e 1
        """
        if valor is None:
            return 0.5  # Valor neutro

        valor = float(valor)

        # Features com inversao (maior valor = menor risco)
        if config.inversao:
            if config.threshold_baixo is not None:
                # Ex: score_clima (1-5, baixo = 2.5)
                if valor <= config.threshold_critico if config.threshold_critico else 0:
                    return 1.0
                if valor >= 4.0:  # Assumindo escala 1-5
                    return 0.0
                # Normalizar linearmente
                return max(0, min(1, (4.0 - valor) / (4.0 - config.threshold_baixo)))

            if config.threshold_negativo is not None:
                # Ex: tendencia_clima (positivo = bom)
                if valor <= config.threshold_negativo:
                    return 1.0
                if valor >= 0.3:
                    return 0.0
                return max(0, min(1, (0.3 - valor) / 0.6))

            if config.threshold_critico is not None:
                # Ex: tempo_empresa (mais = melhor)
                if valor <= config.threshold_critico:
                    return 1.0
                if valor >= 24:  # 2 anos
                    return 0.0
                return max(0, min(1, 1 - (valor / 24)))

        # Features sem inversao (maior valor = maior risco)
        else:
            if config.threshold_critico is not None and config.threshold_alto:
                if valor >= config.threshold_critico:
                    return 1.0
                if valor <= 0:
                    return 0.0
                # Escalar entre 0 e critico
                return min(1.0, valor / config.threshold_critico)

            if config.threshold_alto is not None:
                if valor >= config.threshold_alto * 2:
                    return 1.0
                if valor <= 0:
                    return 0.0
                # Escalar entre 0 e 2x threshold
                return min(1.0, valor / (config.threshold_alto * 2))

        return 0.5  # Valor neutro se nenhuma regra aplicavel

    def _get_valor_neutro(self, config: FeatureDefinition) -> float:
        """Retorna valor neutro para feature nao disponivel."""
        if config.inversao:
            # Para features invertidas, valor neutro e bom
            if config.threshold_baixo:
                return config.threshold_baixo + 1.0
            return 0.0
        else:
            # Para features normais, valor neutro e 0
            return 0.0

    # =========================================================================
    # Score Calculation
    # =========================================================================

    def _calcular_score_heuristico(
        self,
        features: dict[str, Any],
    ) -> tuple[float, list[dict[str, Any]]]:
        """
        Calcula score final usando modelo heuristico.

        O score final e a soma ponderada das features normalizadas,
        escalada para 0-100.

        Args:
            features: Features calculadas

        Returns:
            Tupla (score 0-100, lista de fatores detalhados)
        """
        score_total = 0.0
        fatores_detalhados = []

        for nome, dados in features.items():
            config = self._features.get(nome)
            if not config:
                continue

            valor_norm = dados["valor_normalizado"]
            peso = config.peso
            contribuicao = valor_norm * peso * 100  # Escalar para 0-100

            # Verificar threshold
            valor_bruto = dados["valor_bruto"]
            threshold_violado = self._verificar_threshold(valor_bruto, config)

            # Aplicar bonus de risco se threshold violado
            if threshold_violado:
                contribuicao *= 1.2  # 20% de penalizacao extra

            score_total += contribuicao

            fatores_detalhados.append(
                {
                    "nome": nome,
                    "categoria": config.categoria,
                    "peso": peso,
                    "valor_atual": valor_bruto,
                    "valor_normalizado": round(valor_norm, 4),
                    "contribuicao": round(contribuicao, 2),
                    "threshold_violado": threshold_violado,
                    "descricao": self._gerar_descricao(config, valor_bruto),
                    "recomendacao": (config.recomendacao_template if threshold_violado else None),
                    "dados_brutos": dados,
                }
            )

        # Normalizar score para garantir range 0-100
        score_final = max(0, min(100, score_total))

        # Ordenar fatores por contribuicao
        fatores_detalhados.sort(key=lambda x: x["contribuicao"], reverse=True)

        return score_final, fatores_detalhados

    def _verificar_threshold(
        self,
        valor: Any,
        config: FeatureDefinition,
    ) -> bool:
        """Verifica se o valor viola algum threshold."""
        if valor is None:
            return False

        valor = float(valor)

        if config.inversao:
            if config.threshold_baixo and valor < config.threshold_baixo:
                return True
            if config.threshold_negativo and valor < config.threshold_negativo:
                return True
            if config.threshold_critico and valor < config.threshold_critico:
                return True
        else:
            if config.threshold_alto and valor >= config.threshold_alto:
                return True
            if config.threshold_critico and valor >= config.threshold_critico:
                return True

        return False

    def _gerar_descricao(
        self,
        config: FeatureDefinition,
        valor: Any,
    ) -> str:
        """Gera descricao legivel do fator."""
        if valor is None:
            return f"{config.descricao}: dado nao disponivel"

        if config.inversao:
            if config.threshold_baixo and float(valor) < config.threshold_baixo:
                return f"{config.descricao}: {valor} (abaixo do ideal de {config.threshold_baixo})"
            if config.threshold_negativo and float(valor) < config.threshold_negativo:
                return f"{config.descricao}: {valor} (tendencia negativa maior que {config.threshold_negativo})"
        else:
            if config.threshold_alto and float(valor) >= config.threshold_alto:
                return f"{config.descricao}: {valor} (acima do limite de {config.threshold_alto})"
            if config.threshold_critico and float(valor) >= config.threshold_critico:
                return f"{config.descricao}: {valor} (nivel critico, limite {config.threshold_critico})"

        return f"{config.descricao}: {valor}"

    def _get_metricas_modelo(self) -> dict[str, Any]:
        """Retorna metricas do modelo heuristico."""
        return {
            "tipo": "heuristico",
            "versao": self.MODELO_VERSAO,
            "total_features": len(self._features),
            "soma_pesos": sum(f.peso for f in self._features.values()),
            "categorias": {
                cat.value: sum(1 for f in self._features.values() if f.categoria == cat) for cat in CategoriaFator
            },
            "nota": ("Modelo baseado em regras heuristicas. Score indica tendencia, nao certeza."),
        }

    # =========================================================================
    # Alert Management
    # =========================================================================

    async def _verificar_e_criar_alerta(
        self,
        prediction: TurnoverPrediction,
        predicao_anterior: TurnoverPrediction | None,
        condominium_id: UUID,
    ) -> UUID | None:
        """
        Verifica se deve criar alerta baseado na predicao.

        Criterios de alerta (threshold conservador >= 70):
        - Novo risco: primeira predicao com score >= 70
        - Aumento risco: score subiu >= 15 pontos
        - Risco critico: score >= 80
        - Mudanca nivel: mudou para alto ou critico

        Args:
            prediction: Nova predicao
            predicao_anterior: Predicao anterior (se existir)
            condominium_id: ID do condominio

        Returns:
            ID do alerta criado (ou None)
        """
        score_atual = float(prediction.score_risco)

        # Score abaixo do threshold - sem alerta
        if score_atual < self.THRESHOLD_ALERTA:
            return None

        score_anterior = float(predicao_anterior.score_risco) if predicao_anterior else None
        nivel_anterior = predicao_anterior.nivel if predicao_anterior else None

        # Determinar tipo de alerta
        tipo_alerta: TipoAlerta | None = None
        titulo = ""
        mensagem = ""

        if prediction.is_critico:
            tipo_alerta = TipoAlerta.RISCO_CRITICO
            titulo = "ALERTA CRITICO: Risco de turnover muito alto"
            mensagem = (
                f"O funcionario apresenta score de risco de {score_atual:.1f}, "
                f"classificado como CRITICO. Acao imediata recomendada."
            )

        elif score_anterior is None:
            tipo_alerta = TipoAlerta.NOVO_RISCO
            titulo = "Novo funcionario em risco de turnover"
            mensagem = (
                f"Primeira analise identificou score de risco de {score_atual:.1f}. "
                f"Nivel: {prediction.nivel.value.upper()}."
            )

        elif score_anterior is not None and (score_atual - score_anterior) >= self.THRESHOLD_AUMENTO_SIGNIFICATIVO:
            tipo_alerta = TipoAlerta.AUMENTO_RISCO
            variacao = score_atual - score_anterior
            titulo = "Aumento significativo no risco de turnover"
            mensagem = (
                f"Score de risco aumentou {variacao:.1f} pontos "
                f"(de {score_anterior:.1f} para {score_atual:.1f}). "
                f"Investigar causas."
            )

        elif (
            nivel_anterior is not None
            and nivel_anterior != prediction.nivel
            and prediction.nivel in [NivelRisco.ALTO, NivelRisco.CRITICO]
        ):
            tipo_alerta = TipoAlerta.MUDANCA_NIVEL
            titulo = f"Funcionario mudou para nivel de risco {prediction.nivel.value}"
            mensagem = (
                f"Nivel de risco alterou de {nivel_anterior.value} "
                f"para {prediction.nivel.value}. "
                f"Score atual: {score_atual:.1f}."
            )

        if not tipo_alerta:
            return None

        # Adicionar principais fatores na mensagem
        principais = prediction.principais_fatores[:3]
        if principais:
            fatores_texto = ", ".join(f.nome.replace("_", " ") for f in principais)
            mensagem += f"\n\nPrincipais fatores de risco: {fatores_texto}."

        # Criar alerta
        alert_data = AlertCreate(
            funcionario_id=prediction.funcionario_id,
            prediction_id=prediction.id,
            condominium_id=condominium_id,
            tipo=tipo_alerta,
            score_atual=prediction.score_risco,
            score_anterior=(predicao_anterior.score_risco if predicao_anterior else None),
            variacao_score=(Decimal(str(score_atual - score_anterior)) if score_anterior else None),
            nivel_atual=prediction.nivel,
            nivel_anterior=nivel_anterior,
            titulo=titulo,
            mensagem=mensagem,
            enviado_para=[],  # Sera preenchido pelo sistema de notificacoes
            prioridade=RiskAlert.calcular_prioridade(tipo_alerta, score_atual),
            expira_em=datetime.utcnow() + timedelta(days=30),
        )

        alert = await self.repository.create_alert(alert_data)
        logger.info(f"Alerta criado: tipo={tipo_alerta.value}, funcionario={prediction.funcionario_id}")

        return alert.id

    # =========================================================================
    # Configuration
    # =========================================================================

    def get_features_config(self) -> list[dict[str, Any]]:
        """Retorna configuracao das features."""
        return [
            {
                "nome": config.nome,
                "categoria": config.categoria.value,
                "peso": config.peso,
                "descricao": config.descricao,
                "threshold_alto": config.threshold_alto,
                "threshold_baixo": config.threshold_baixo,
                "threshold_negativo": config.threshold_negativo,
                "threshold_critico": config.threshold_critico,
                "inversao": config.inversao,
            }
            for config in self._features.values()
        ]

    def get_total_peso(self) -> float:
        """Retorna soma total dos pesos das features."""
        return sum(f.peso for f in self._features.values())
