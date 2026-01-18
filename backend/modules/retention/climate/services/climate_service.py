"""
ClimateService - Servico para Pesquisa de Clima Operacional.

Implementa logica de negocio para:
- Gestao de pesquisas de clima
- Calculo de scores normalizados (0-100)
- Agregacao por entidade (posto, equipe, empresa)
- Deteccao de quedas e alertas
- Dashboards e tendencias
"""

import hashlib
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.retention.climate.models.climate_models import (
    AlertSeverity,
    ClimateDimension,
    EntityType,
    QuestionType,
)
from modules.retention.climate.repositories.climate_repository import (
    ClimateAlertRepository,
    ClimateResponseRepository,
    ClimateScoreRepository,
    ClimateSurveyRepository,
)
from modules.retention.climate.schemas.climate_schemas import (
    CalculationResult,
    ClimateAnalytics,
    ClimateByEquipe,
    ClimateByEmpresa,
    ClimateByPosto,
    ClimateDashboard,
    ClimateTrend,
    DimensionAnalysis,
    EntityScore,
    QuestionSchema,
    ResponseConfirmation,
    ResponseCreate,
    ScoreByDimension,
    SurveyCreate,
    TrendPoint,
)


# =============================================================================
# Perguntas Padrao do Sistema
# =============================================================================

PERGUNTAS_CLIMA_PADRAO: List[QuestionSchema] = [
    QuestionSchema(
        id="sat_posto",
        texto="Estou satisfeito com o posto onde trabalho",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.SATISFACAO,
        ordem=1,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="rel_supervisor",
        texto="Tenho um bom relacionamento com meu supervisor",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.LIDERANCA,
        ordem=2,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="suporte_supervisor",
        texto="Meu supervisor me apoia quando preciso",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.LIDERANCA,
        ordem=3,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="carga_trabalho",
        texto="Minha carga de trabalho e adequada",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.OPERACIONAL,
        ordem=4,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="equipamentos",
        texto="Tenho os equipamentos necessarios para trabalhar bem",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.OPERACIONAL,
        ordem=5,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="crescimento",
        texto="Vejo oportunidades de crescimento na empresa",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.CARREIRA,
        ordem=6,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="treinamento",
        texto="Recebo treinamentos adequados para minha funcao",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.CARREIRA,
        ordem=7,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="comunicacao",
        texto="A comunicacao da empresa e clara e eficiente",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.COMUNICACAO,
        ordem=8,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="reconhecimento",
        texto="Me sinto reconhecido pelo meu trabalho",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.RECONHECIMENTO,
        ordem=9,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="ambiente",
        texto="O ambiente de trabalho e seguro e agradavel",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.AMBIENTE,
        ordem=10,
        obrigatoria=True,
    ),
    QuestionSchema(
        id="enps",
        texto="Recomendaria esta empresa para um amigo trabalhar",
        tipo=QuestionType.ESCALA,
        dimensao=ClimateDimension.ENPS,
        ordem=11,
        obrigatoria=True,
        permite_comentario=True,
    ),
]

# Mapeamento de perguntas para dimensoes
PERGUNTAS_POR_DIMENSAO: Dict[str, List[str]] = {
    ClimateDimension.SATISFACAO.value: ["sat_posto"],
    ClimateDimension.LIDERANCA.value: ["rel_supervisor", "suporte_supervisor"],
    ClimateDimension.OPERACIONAL.value: ["carga_trabalho", "equipamentos"],
    ClimateDimension.CARREIRA.value: ["crescimento", "treinamento"],
    ClimateDimension.COMUNICACAO.value: ["comunicacao"],
    ClimateDimension.RECONHECIMENTO.value: ["reconhecimento"],
    ClimateDimension.AMBIENTE.value: ["ambiente"],
    ClimateDimension.ENPS.value: ["enps"],
}

# Salt para hash de funcionarios (em producao, usar variavel de ambiente)
HASH_SALT = "conecta_pro_climate_2025_salt"


class ClimateService:
    """
    Servico de Pesquisa de Clima Operacional.

    Gerencia todo o ciclo de vida das pesquisas de clima,
    desde a criacao ate a analise de resultados.
    """

    # Thresholds para classificacao
    SCORE_EXCELENTE = 80
    SCORE_BOM = 65
    SCORE_REGULAR = 50
    SCORE_ATENCAO = 35

    # Threshold para alertas
    QUEDA_ALERTA_PERCENTUAL = 20
    SCORE_CRITICO = 35

    # Tempo minimo para resposta valida (segundos)
    TEMPO_MINIMO_RESPOSTA = 30

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o servico.

        Args:
            db: Sessao async do banco de dados
        """
        self.db = db
        self.survey_repo = ClimateSurveyRepository(db)
        self.response_repo = ClimateResponseRepository(db)
        self.score_repo = ClimateScoreRepository(db)
        self.alert_repo = ClimateAlertRepository(db)

    # =========================================================================
    # Gestao de Pesquisas
    # =========================================================================

    async def criar_pesquisa(
        self,
        data: SurveyCreate,
        created_by: Optional[str] = None,
    ) -> Any:
        """
        Cria uma nova pesquisa de clima.

        Args:
            data: Dados da pesquisa
            created_by: ID do usuario criador

        Returns:
            ClimateSurvey criada
        """
        # Usar perguntas padrao se solicitado
        if data.usar_perguntas_padrao or not data.perguntas:
            data.perguntas = PERGUNTAS_CLIMA_PADRAO

        survey = await self.survey_repo.create(data, created_by)
        logger.info(f"Pesquisa de clima criada: {survey.nome}")

        return survey

    async def get_pesquisa_ativa(
        self,
        empresa_id: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Busca pesquisa ativa para uma empresa.

        Args:
            empresa_id: ID da empresa

        Returns:
            Pesquisa ativa ou None
        """
        return await self.survey_repo.get_active(empresa_id)

    async def get_perguntas_padrao(self) -> List[QuestionSchema]:
        """
        Retorna lista de perguntas padrao.

        Returns:
            Lista de perguntas
        """
        return PERGUNTAS_CLIMA_PADRAO

    # =========================================================================
    # Respostas
    # =========================================================================

    def _hash_funcionario(self, funcionario_id: str) -> str:
        """
        Gera hash anonimo do funcionario.

        Args:
            funcionario_id: ID do funcionario

        Returns:
            Hash SHA-256 do ID
        """
        data = f"{HASH_SALT}:{funcionario_id}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _hash_ip(self, ip: str) -> str:
        """
        Gera hash do IP.

        Args:
            ip: Endereco IP

        Returns:
            Hash SHA-256 do IP
        """
        data = f"{HASH_SALT}:ip:{ip}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _calcular_score_resposta(
        self,
        respostas: Dict[str, int],
        perguntas: List[Dict[str, Any]],
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calcula score normalizado (0-100) das respostas.

        A escala e 1-4, sem opcao neutra:
        1 = Discordo totalmente (0%)
        2 = Discordo parcialmente (33%)
        3 = Concordo parcialmente (66%)
        4 = Concordo totalmente (100%)

        Args:
            respostas: Dicionario {pergunta_id: valor 1-4}
            perguntas: Lista de perguntas da pesquisa

        Returns:
            Tupla (score_geral, scores_por_dimensao)
        """
        # Criar mapa de pergunta para dimensao
        pergunta_dimensao: Dict[str, str] = {}
        for pergunta in perguntas:
            if isinstance(pergunta, dict):
                pergunta_dimensao[pergunta.get("id", "")] = pergunta.get(
                    "dimensao", ClimateDimension.SATISFACAO.value
                )

        # Agrupar respostas por dimensao
        dimensoes_valores: Dict[str, List[float]] = {}
        todos_valores: List[float] = []

        for pergunta_id, valor in respostas.items():
            # Normalizar para 0-100
            # 1 -> 0, 2 -> 33.33, 3 -> 66.67, 4 -> 100
            score_normalizado = ((valor - 1) / 3) * 100

            todos_valores.append(score_normalizado)

            dimensao = pergunta_dimensao.get(pergunta_id, ClimateDimension.SATISFACAO.value)
            if dimensao not in dimensoes_valores:
                dimensoes_valores[dimensao] = []
            dimensoes_valores[dimensao].append(score_normalizado)

        # Calcular score geral
        score_geral = sum(todos_valores) / len(todos_valores) if todos_valores else 0.0

        # Calcular score por dimensao
        scores_dimensao = {
            dim: round(sum(vals) / len(vals), 2)
            for dim, vals in dimensoes_valores.items()
        }

        return round(score_geral, 2), scores_dimensao

    async def responder_pesquisa(
        self,
        data: ResponseCreate,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ResponseConfirmation:
        """
        Registra resposta de pesquisa (anonimizada).

        Args:
            data: Dados da resposta
            ip: IP do respondente (sera hasheado)
            user_agent: User-Agent (sera hasheado)

        Returns:
            Confirmacao com score calculado

        Raises:
            ValueError: Se ja respondeu ou dados invalidos
        """
        # Validar tempo minimo
        if data.tempo_resposta_segundos < self.TEMPO_MINIMO_RESPOSTA:
            logger.warning(
                f"Resposta muito rapida: {data.tempo_resposta_segundos}s < {self.TEMPO_MINIMO_RESPOSTA}s"
            )
            # Permite, mas marca como suspeita

        # Gerar hash do funcionario
        funcionario_hash = self._hash_funcionario(data.funcionario_id)

        # Verificar periodo atual
        periodo = datetime.now().strftime("%Y-%m")

        # Verificar se ja respondeu
        ja_respondeu = await self.response_repo.check_already_responded(
            data.survey_id, funcionario_hash, periodo
        )
        if ja_respondeu:
            raise ValueError("Funcionario ja respondeu esta pesquisa no periodo atual")

        # Buscar pesquisa para obter perguntas
        survey = await self.survey_repo.get_by_id(data.survey_id)
        if not survey:
            raise ValueError("Pesquisa nao encontrada")

        if not survey.is_active:
            raise ValueError("Pesquisa nao esta ativa")

        # Calcular scores
        score_geral, scores_dimensao = self._calcular_score_resposta(
            data.respostas, survey.perguntas
        )

        # Hashes de seguranca
        ip_hash = self._hash_ip(ip) if ip else None
        ua_hash = (
            hashlib.sha256(f"{HASH_SALT}:ua:{user_agent}".encode()).hexdigest()
            if user_agent
            else None
        )

        # Criar resposta
        await self.response_repo.create(
            survey_id=data.survey_id,
            funcionario_hash=funcionario_hash,
            respostas=data.respostas,
            score_calculado=score_geral,
            scores_por_dimensao=scores_dimensao,
            tempo_resposta_segundos=data.tempo_resposta_segundos,
            posto_id=data.posto_id,
            equipe_id=data.equipe_id,
            empresa_id=data.empresa_id,
            cliente_id=data.cliente_id,
            comentarios=data.comentarios,
            ip_hash=ip_hash,
            user_agent_hash=ua_hash,
        )

        logger.info(f"Resposta de clima registrada: score={score_geral}")

        return ResponseConfirmation(
            success=True,
            message="Resposta registrada com sucesso. Obrigado pela participacao!",
            score=score_geral,
            classificacao=self._classificar_score(score_geral),
        )

    def _classificar_score(self, score: float) -> str:
        """
        Classifica score em categoria.

        Args:
            score: Score 0-100

        Returns:
            Classificacao (excelente, bom, regular, atencao, critico)
        """
        if score >= self.SCORE_EXCELENTE:
            return "excelente"
        if score >= self.SCORE_BOM:
            return "bom"
        if score >= self.SCORE_REGULAR:
            return "regular"
        if score >= self.SCORE_ATENCAO:
            return "atencao"
        return "critico"

    # =========================================================================
    # Calculo de Scores
    # =========================================================================

    async def calcular_scores_periodo(
        self,
        periodo: str,
        empresa_id: Optional[str] = None,
        recalcular: bool = False,
    ) -> CalculationResult:
        """
        Calcula scores agregados para um periodo.

        Job que agrega scores por posto, equipe e empresa.

        Args:
            periodo: Periodo YYYY-MM
            empresa_id: Filtrar por empresa
            recalcular: Forcar recalculo

        Returns:
            Resultado do calculo
        """
        import time

        inicio = time.time()
        scores_calculados = 0
        alertas_gerados = 0
        erros: List[str] = []

        try:
            # Buscar todas as respostas do periodo
            respostas, _ = await self.response_repo.list_by_filters(
                filters=type(
                    "Filters",
                    (),
                    {
                        "empresa_id": empresa_id,
                        "periodo_inicio": periodo,
                        "periodo_fim": periodo,
                        "posto_id": None,
                        "equipe_id": None,
                        "cliente_id": None,
                        "score_min": None,
                        "score_max": None,
                        "dimensao": None,
                        "apenas_alertas": False,
                    },
                )(),
                page=1,
                page_size=10000,
            )

            if not respostas:
                logger.warning(f"Nenhuma resposta encontrada para periodo {periodo}")
                return CalculationResult(
                    periodo=periodo,
                    scores_calculados=0,
                    alertas_gerados=0,
                    tempo_processamento_ms=int((time.time() - inicio) * 1000),
                    sucesso=True,
                    erros=["Nenhuma resposta encontrada para o periodo"],
                )

            # Agrupar por entidade
            postos: Dict[str, List] = {}
            equipes: Dict[str, List] = {}
            empresas: Dict[str, List] = {}

            for resposta in respostas:
                if resposta.posto_id:
                    if resposta.posto_id not in postos:
                        postos[resposta.posto_id] = []
                    postos[resposta.posto_id].append(resposta)

                if resposta.equipe_id:
                    if resposta.equipe_id not in equipes:
                        equipes[resposta.equipe_id] = []
                    equipes[resposta.equipe_id].append(resposta)

                if resposta.empresa_id:
                    if resposta.empresa_id not in empresas:
                        empresas[resposta.empresa_id] = []
                    empresas[resposta.empresa_id].append(resposta)

            # Calcular scores por posto
            for posto_id, respostas_posto in postos.items():
                try:
                    alertas = await self._calcular_e_salvar_score(
                        EntityType.POSTO,
                        posto_id,
                        periodo,
                        respostas_posto,
                        empresa_id=respostas_posto[0].empresa_id if respostas_posto else None,
                    )
                    scores_calculados += 1
                    alertas_gerados += len(alertas)
                except Exception as e:
                    erros.append(f"Erro ao calcular score do posto {posto_id}: {str(e)}")
                    logger.error(f"Erro ao calcular score do posto {posto_id}: {e}")

            # Calcular scores por equipe
            for equipe_id, respostas_equipe in equipes.items():
                try:
                    alertas = await self._calcular_e_salvar_score(
                        EntityType.EQUIPE,
                        equipe_id,
                        periodo,
                        respostas_equipe,
                        empresa_id=respostas_equipe[0].empresa_id if respostas_equipe else None,
                    )
                    scores_calculados += 1
                    alertas_gerados += len(alertas)
                except Exception as e:
                    erros.append(f"Erro ao calcular score da equipe {equipe_id}: {str(e)}")
                    logger.error(f"Erro ao calcular score da equipe {equipe_id}: {e}")

            # Calcular scores por empresa
            for empresa_id_calc, respostas_empresa in empresas.items():
                try:
                    alertas = await self._calcular_e_salvar_score(
                        EntityType.EMPRESA,
                        empresa_id_calc,
                        periodo,
                        respostas_empresa,
                        empresa_id=empresa_id_calc,
                    )
                    scores_calculados += 1
                    alertas_gerados += len(alertas)
                except Exception as e:
                    erros.append(f"Erro ao calcular score da empresa {empresa_id_calc}: {str(e)}")
                    logger.error(f"Erro ao calcular score da empresa {empresa_id_calc}: {e}")

            tempo_ms = int((time.time() - inicio) * 1000)
            logger.info(
                f"Calculo de scores concluido: {scores_calculados} scores, "
                f"{alertas_gerados} alertas em {tempo_ms}ms"
            )

            return CalculationResult(
                periodo=periodo,
                scores_calculados=scores_calculados,
                alertas_gerados=alertas_gerados,
                tempo_processamento_ms=tempo_ms,
                sucesso=True,
                erros=erros,
            )

        except Exception as e:
            logger.error(f"Erro ao calcular scores do periodo {periodo}: {e}")
            return CalculationResult(
                periodo=periodo,
                scores_calculados=scores_calculados,
                alertas_gerados=alertas_gerados,
                tempo_processamento_ms=int((time.time() - inicio) * 1000),
                sucesso=False,
                erros=[str(e)],
            )

    async def _calcular_e_salvar_score(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
        respostas: List,
        empresa_id: Optional[str] = None,
    ) -> List:
        """
        Calcula e salva score de uma entidade.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo YYYY-MM
            respostas: Lista de respostas
            empresa_id: ID da empresa

        Returns:
            Lista de alertas gerados
        """
        alertas = []

        if not respostas:
            return alertas

        # Calcular score medio
        scores = [r.score_calculado for r in respostas]
        score_medio = sum(scores) / len(scores)

        # Agregar scores por dimensao
        dimensoes: Dict[str, List[float]] = {}
        for resposta in respostas:
            for dim, score in resposta.scores_por_dimensao.items():
                if dim not in dimensoes:
                    dimensoes[dim] = []
                dimensoes[dim].append(score)

        scores_dimensao = {
            dim: round(sum(vals) / len(vals), 2) for dim, vals in dimensoes.items()
        }

        # Calcular eNPS
        enps_score, enps_promotores, enps_neutros, enps_detratores = self._calcular_enps(
            respostas
        )

        # Buscar score anterior para tendencia
        periodo_anterior = self._get_periodo_anterior(periodo)
        score_anterior = await self.score_repo.get_by_entidade_periodo(
            entidade_tipo, entidade_id, periodo_anterior
        )

        tendencia = 0.0
        if score_anterior and score_anterior.score > 0:
            tendencia = ((score_medio - score_anterior.score) / score_anterior.score) * 100

        # Identificar fatores positivos e negativos
        fatores_positivos, fatores_negativos = self._identificar_fatores(scores_dimensao)

        # Verificar alertas
        alertas_lista = await self._verificar_alertas(
            entidade_tipo,
            entidade_id,
            periodo,
            score_medio,
            score_anterior.score if score_anterior else None,
            tendencia,
            scores_dimensao,
            empresa_id,
        )

        # Salvar score
        await self.score_repo.create_or_update(
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            periodo=periodo,
            score=round(score_medio, 2),
            scores_dimensao=scores_dimensao,
            total_respostas=len(respostas),
            tendencia=round(tendencia, 2),
            fatores_positivos=fatores_positivos,
            fatores_negativos=fatores_negativos,
            enps_score=enps_score,
            enps_promotores=enps_promotores,
            enps_neutros=enps_neutros,
            enps_detratores=enps_detratores,
            empresa_id=empresa_id,
            alertas=alertas_lista,
        )

        return alertas

    def _calcular_enps(
        self,
        respostas: List,
    ) -> Tuple[float, int, int, int]:
        """
        Calcula eNPS (Employee Net Promoter Score).

        Na escala 1-4:
        - 4 = Promotor
        - 3 = Neutro
        - 1-2 = Detrator

        eNPS = % Promotores - % Detratores

        Args:
            respostas: Lista de respostas

        Returns:
            Tupla (enps_score, promotores, neutros, detratores)
        """
        promotores = 0
        neutros = 0
        detratores = 0

        for resposta in respostas:
            # Pegar resposta da pergunta eNPS
            valor_enps = resposta.respostas.get("enps", 0)

            if valor_enps == 4:
                promotores += 1
            elif valor_enps == 3:
                neutros += 1
            else:
                detratores += 1

        total = promotores + neutros + detratores
        if total == 0:
            return 0.0, 0, 0, 0

        pct_promotores = (promotores / total) * 100
        pct_detratores = (detratores / total) * 100
        enps = pct_promotores - pct_detratores

        return round(enps, 2), promotores, neutros, detratores

    def _get_periodo_anterior(self, periodo: str) -> str:
        """
        Retorna periodo anterior.

        Args:
            periodo: Periodo YYYY-MM

        Returns:
            Periodo anterior YYYY-MM
        """
        ano, mes = map(int, periodo.split("-"))
        if mes == 1:
            return f"{ano - 1}-12"
        return f"{ano}-{mes - 1:02d}"

    def _identificar_fatores(
        self,
        scores_dimensao: Dict[str, float],
    ) -> Tuple[List[str], List[str]]:
        """
        Identifica fatores positivos e negativos.

        Args:
            scores_dimensao: Scores por dimensao

        Returns:
            Tupla (fatores_positivos, fatores_negativos)
        """
        positivos = []
        negativos = []

        dimensao_labels = {
            ClimateDimension.SATISFACAO.value: "Satisfacao com o posto",
            ClimateDimension.LIDERANCA.value: "Relacionamento com lideranca",
            ClimateDimension.OPERACIONAL.value: "Condicoes operacionais",
            ClimateDimension.CARREIRA.value: "Oportunidades de carreira",
            ClimateDimension.COMUNICACAO.value: "Comunicacao",
            ClimateDimension.RECONHECIMENTO.value: "Reconhecimento",
            ClimateDimension.AMBIENTE.value: "Ambiente de trabalho",
            ClimateDimension.ENPS.value: "Recomendacao (eNPS)",
        }

        for dim, score in sorted(scores_dimensao.items(), key=lambda x: x[1], reverse=True):
            label = dimensao_labels.get(dim, dim)
            if score >= self.SCORE_BOM:
                positivos.append(f"{label}: {score:.0f}")
            elif score < self.SCORE_REGULAR:
                negativos.append(f"{label}: {score:.0f}")

        return positivos[:3], negativos[:3]

    async def _verificar_alertas(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
        score_atual: float,
        score_anterior: Optional[float],
        tendencia: float,
        scores_dimensao: Dict[str, float],
        empresa_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Verifica e cria alertas de clima.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo
            score_atual: Score atual
            score_anterior: Score anterior
            tendencia: Variacao percentual
            scores_dimensao: Scores por dimensao
            empresa_id: ID da empresa

        Returns:
            Lista de alertas criados
        """
        alertas = []

        # Alerta de queda significativa
        if tendencia < -self.QUEDA_ALERTA_PERCENTUAL:
            alerta_existe = await self.alert_repo.check_existing_alert(
                entidade_tipo, entidade_id, periodo, "queda_score"
            )
            if not alerta_existe:
                severidade = (
                    AlertSeverity.CRITICA
                    if tendencia < -40
                    else AlertSeverity.ALTA
                    if tendencia < -30
                    else AlertSeverity.MEDIA
                )
                alerta = await self.alert_repo.create(
                    entidade_tipo=entidade_tipo,
                    entidade_id=entidade_id,
                    periodo=periodo,
                    tipo_alerta="queda_score",
                    mensagem=f"Queda de {abs(tendencia):.1f}% no score de clima",
                    severidade=severidade,
                    score_atual=score_atual,
                    score_anterior=score_anterior,
                    variacao=tendencia,
                    empresa_id=empresa_id,
                )
                alertas.append(
                    {"tipo": "queda_score", "severidade": severidade.value, "id": alerta.id}
                )

        # Alerta de score critico
        if score_atual < self.SCORE_CRITICO:
            alerta_existe = await self.alert_repo.check_existing_alert(
                entidade_tipo, entidade_id, periodo, "score_critico"
            )
            if not alerta_existe:
                alerta = await self.alert_repo.create(
                    entidade_tipo=entidade_tipo,
                    entidade_id=entidade_id,
                    periodo=periodo,
                    tipo_alerta="score_critico",
                    mensagem=f"Score de clima critico: {score_atual:.1f}",
                    severidade=AlertSeverity.CRITICA,
                    score_atual=score_atual,
                    empresa_id=empresa_id,
                )
                alertas.append(
                    {"tipo": "score_critico", "severidade": "critica", "id": alerta.id}
                )

        # Alerta de dimensao critica
        for dim, score in scores_dimensao.items():
            if score < self.SCORE_CRITICO:
                alerta_existe = await self.alert_repo.check_existing_alert(
                    entidade_tipo, entidade_id, periodo, f"dimensao_critica_{dim}"
                )
                if not alerta_existe:
                    alerta = await self.alert_repo.create(
                        entidade_tipo=entidade_tipo,
                        entidade_id=entidade_id,
                        periodo=periodo,
                        tipo_alerta=f"dimensao_critica",
                        dimensao=dim,
                        mensagem=f"Dimensao {dim} com score critico: {score:.1f}",
                        severidade=AlertSeverity.ALTA,
                        score_atual=score,
                        empresa_id=empresa_id,
                    )
                    alertas.append(
                        {"tipo": "dimensao_critica", "dimensao": dim, "id": alerta.id}
                    )

        return alertas

    # =========================================================================
    # Dashboard e Tendencias
    # =========================================================================

    async def get_dashboard(
        self,
        empresa_id: Optional[str] = None,
    ) -> ClimateDashboard:
        """
        Retorna dashboard geral de clima.

        Args:
            empresa_id: Filtrar por empresa

        Returns:
            Dashboard com visao geral
        """
        periodo_atual = datetime.now().strftime("%Y-%m")
        periodo_anterior = self._get_periodo_anterior(periodo_atual)

        # Score geral atual
        score_atual = await self.response_repo.get_score_medio_periodo(
            periodo_atual, empresa_id
        )
        score_anterior = await self.response_repo.get_score_medio_periodo(
            periodo_anterior, empresa_id
        )

        variacao = 0.0
        if score_anterior > 0:
            variacao = ((score_atual - score_anterior) / score_anterior) * 100

        # Total de respostas
        total_respostas = await self.response_repo.count_by_periodo(
            periodo_atual, empresa_id
        )

        # Buscar scores por dimensao
        respostas, _ = await self.response_repo.list_by_filters(
            filters=type(
                "Filters",
                (),
                {
                    "empresa_id": empresa_id,
                    "periodo_inicio": periodo_atual,
                    "periodo_fim": periodo_atual,
                    "posto_id": None,
                    "equipe_id": None,
                    "cliente_id": None,
                    "score_min": None,
                    "score_max": None,
                    "dimensao": None,
                    "apenas_alertas": False,
                },
            )(),
            page=1,
            page_size=10000,
        )

        # Agregar por dimensao
        dimensoes: Dict[str, List[float]] = {}
        for resposta in respostas:
            for dim, score in resposta.scores_por_dimensao.items():
                if dim not in dimensoes:
                    dimensoes[dim] = []
                dimensoes[dim].append(score)

        scores_dimensao_list = []
        for dim, valores in dimensoes.items():
            score_dim = sum(valores) / len(valores) if valores else 0
            scores_dimensao_list.append(
                ScoreByDimension(
                    dimensao=ClimateDimension(dim),
                    score=round(score_dim, 2),
                    total_respostas=len(valores),
                    tendencia=0.0,  # TODO: calcular tendencia por dimensao
                    classificacao=self._classificar_score(score_dim),
                )
            )

        # Top e Bottom postos
        top_postos = await self.score_repo.get_top_scores(
            periodo_atual, EntityType.POSTO, 5, empresa_id
        )
        bottom_postos = await self.score_repo.get_bottom_scores(
            periodo_atual, EntityType.POSTO, 5, empresa_id
        )

        # Top e Bottom equipes
        top_equipes = await self.score_repo.get_top_scores(
            periodo_atual, EntityType.EQUIPE, 5, empresa_id
        )
        bottom_equipes = await self.score_repo.get_bottom_scores(
            periodo_atual, EntityType.EQUIPE, 5, empresa_id
        )

        # Converter para EntityScore
        def to_entity_score(score) -> EntityScore:
            return EntityScore(
                entidade_id=score.entidade_id,
                entidade_nome=score.entidade_nome or score.entidade_id[:8],
                score=score.score,
                total_respostas=score.total_respostas,
                tendencia=score.tendencia,
                classificacao=self._classificar_score(score.score),
            )

        # Alertas ativos
        alertas_counts = await self.alert_repo.count_by_severidade(empresa_id)
        total_alertas = sum(alertas_counts.values())

        # Tendencia 6 meses
        tendencia_6_meses = await self._get_tendencia_periodos(
            empresa_id=empresa_id, periodos=6
        )

        # Calcular eNPS geral
        enps_score = 0.0
        if respostas:
            _, promotores, neutros, detratores = self._calcular_enps(respostas)
            total = promotores + neutros + detratores
            if total > 0:
                enps_score = ((promotores - detratores) / total) * 100

        return ClimateDashboard(
            periodo_atual=periodo_atual,
            score_geral=round(score_atual, 2),
            score_anterior=round(score_anterior, 2),
            variacao=round(variacao, 2),
            classificacao=self._classificar_score(score_atual),
            total_respostas=total_respostas,
            taxa_participacao=0.0,  # TODO: calcular baseado em total de funcionarios
            enps_score=round(enps_score, 2),
            scores_por_dimensao=sorted(
                scores_dimensao_list, key=lambda x: x.score, reverse=True
            ),
            top_postos=[to_entity_score(s) for s in top_postos],
            bottom_postos=[to_entity_score(s) for s in bottom_postos],
            top_equipes=[to_entity_score(s) for s in top_equipes],
            bottom_equipes=[to_entity_score(s) for s in bottom_equipes],
            alertas_ativos=total_alertas,
            tendencia_6_meses=tendencia_6_meses,
            ultima_atualizacao=datetime.now(),
        )

    async def _get_tendencia_periodos(
        self,
        empresa_id: Optional[str] = None,
        periodos: int = 6,
    ) -> List[TrendPoint]:
        """
        Retorna tendencia dos ultimos periodos.

        Args:
            empresa_id: Filtrar por empresa
            periodos: Quantidade de periodos

        Returns:
            Lista de pontos de tendencia
        """
        from dateutil.relativedelta import relativedelta

        tendencia = []
        data_atual = datetime.now()

        for i in range(periodos - 1, -1, -1):
            data = data_atual - relativedelta(months=i)
            periodo = data.strftime("%Y-%m")

            score = await self.response_repo.get_score_medio_periodo(periodo, empresa_id)
            total = await self.response_repo.count_by_periodo(periodo, empresa_id)

            variacao = 0.0
            if len(tendencia) > 0 and tendencia[-1].score > 0:
                variacao = ((score - tendencia[-1].score) / tendencia[-1].score) * 100

            tendencia.append(
                TrendPoint(
                    periodo=periodo,
                    score=round(score, 2),
                    total_respostas=total,
                    variacao=round(variacao, 2),
                )
            )

        return tendencia

    async def get_tendencias(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodos: int = 6,
    ) -> ClimateTrend:
        """
        Retorna tendencia historica de uma entidade.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodos: Quantidade de periodos

        Returns:
            ClimateTrend com evolucao historica
        """
        scores = await self.score_repo.get_scores_by_entidade(
            entidade_tipo, entidade_id, periodos
        )

        if not scores:
            return ClimateTrend(
                entidade_tipo=entidade_tipo,
                entidade_id=entidade_id,
                entidade_nome=None,
                periodos=[],
                score_atual=0.0,
                score_medio=0.0,
                melhor_periodo=None,
                pior_periodo=None,
                tendencia_geral="sem_dados",
                variacao_total=0.0,
            )

        pontos = []
        for i, score in enumerate(scores):
            variacao = 0.0
            if i > 0 and scores[i - 1].score > 0:
                variacao = ((score.score - scores[i - 1].score) / scores[i - 1].score) * 100

            pontos.append(
                TrendPoint(
                    periodo=score.periodo,
                    score=score.score,
                    total_respostas=score.total_respostas,
                    variacao=round(variacao, 2),
                )
            )

        # Estatisticas
        todos_scores = [s.score for s in scores]
        score_atual = scores[-1].score if scores else 0.0
        score_medio = sum(todos_scores) / len(todos_scores) if todos_scores else 0.0

        # Melhor e pior periodo
        melhor_idx = todos_scores.index(max(todos_scores)) if todos_scores else 0
        pior_idx = todos_scores.index(min(todos_scores)) if todos_scores else 0

        # Tendencia geral
        variacao_total = 0.0
        if len(scores) >= 2 and scores[0].score > 0:
            variacao_total = ((scores[-1].score - scores[0].score) / scores[0].score) * 100

        if variacao_total > 5:
            tendencia_geral = "alta"
        elif variacao_total < -5:
            tendencia_geral = "queda"
        else:
            tendencia_geral = "estavel"

        return ClimateTrend(
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            entidade_nome=scores[-1].entidade_nome if scores else None,
            periodos=pontos,
            score_atual=round(score_atual, 2),
            score_medio=round(score_medio, 2),
            melhor_periodo=scores[melhor_idx].periodo if scores else None,
            pior_periodo=scores[pior_idx].periodo if scores else None,
            tendencia_geral=tendencia_geral,
            variacao_total=round(variacao_total, 2),
        )

    # =========================================================================
    # Resultados por Entidade
    # =========================================================================

    async def get_results_by_posto(
        self,
        posto_id: str,
        periodo: Optional[str] = None,
    ) -> Optional[ClimateByPosto]:
        """
        Retorna resultados de clima de um posto.

        Args:
            posto_id: ID do posto
            periodo: Periodo (default: atual)

        Returns:
            ClimateByPosto ou None
        """
        periodo = periodo or datetime.now().strftime("%Y-%m")
        periodo_anterior = self._get_periodo_anterior(periodo)

        score = await self.score_repo.get_by_entidade_periodo(
            EntityType.POSTO, posto_id, periodo
        )

        if not score:
            return None

        score_ant = await self.score_repo.get_by_entidade_periodo(
            EntityType.POSTO, posto_id, periodo_anterior
        )

        variacao = 0.0
        if score_ant and score_ant.score > 0:
            variacao = ((score.score - score_ant.score) / score_ant.score) * 100

        return ClimateByPosto(
            posto_id=posto_id,
            posto_nome=score.entidade_nome or posto_id[:8],
            cliente_nome=None,  # TODO: buscar nome do cliente
            periodo=periodo,
            score=score.score,
            score_anterior=score_ant.score if score_ant else 0.0,
            variacao=round(variacao, 2),
            classificacao=self._classificar_score(score.score),
            total_respostas=score.total_respostas,
            total_funcionarios=0,  # TODO: buscar total de funcionarios
            taxa_participacao=score.taxa_participacao,
            scores_dimensao=score.scores_dimensao,
            enps_score=score.enps_score,
            fatores_positivos=score.fatores_positivos,
            fatores_negativos=score.fatores_negativos,
            alertas=score.alertas,
        )

    async def get_results_by_equipe(
        self,
        equipe_id: str,
        periodo: Optional[str] = None,
    ) -> Optional[ClimateByEquipe]:
        """
        Retorna resultados de clima de uma equipe.

        Args:
            equipe_id: ID da equipe
            periodo: Periodo (default: atual)

        Returns:
            ClimateByEquipe ou None
        """
        periodo = periodo or datetime.now().strftime("%Y-%m")
        periodo_anterior = self._get_periodo_anterior(periodo)

        score = await self.score_repo.get_by_entidade_periodo(
            EntityType.EQUIPE, equipe_id, periodo
        )

        if not score:
            return None

        score_ant = await self.score_repo.get_by_entidade_periodo(
            EntityType.EQUIPE, equipe_id, periodo_anterior
        )

        variacao = 0.0
        if score_ant and score_ant.score > 0:
            variacao = ((score.score - score_ant.score) / score_ant.score) * 100

        return ClimateByEquipe(
            equipe_id=equipe_id,
            equipe_nome=score.entidade_nome or equipe_id[:8],
            supervisor_nome=None,  # TODO: buscar nome do supervisor
            periodo=periodo,
            score=score.score,
            score_anterior=score_ant.score if score_ant else 0.0,
            variacao=round(variacao, 2),
            classificacao=self._classificar_score(score.score),
            total_respostas=score.total_respostas,
            total_funcionarios=0,  # TODO: buscar total
            taxa_participacao=score.taxa_participacao,
            scores_dimensao=score.scores_dimensao,
            enps_score=score.enps_score,
            postos_vinculados=0,  # TODO: contar postos
        )

    async def get_results_empresa(
        self,
        empresa_id: str,
        periodo: Optional[str] = None,
    ) -> Optional[ClimateByEmpresa]:
        """
        Retorna resultados de clima da empresa.

        Args:
            empresa_id: ID da empresa
            periodo: Periodo (default: atual)

        Returns:
            ClimateByEmpresa ou None
        """
        periodo = periodo or datetime.now().strftime("%Y-%m")
        periodo_anterior = self._get_periodo_anterior(periodo)

        score = await self.score_repo.get_by_entidade_periodo(
            EntityType.EMPRESA, empresa_id, periodo
        )

        if not score:
            # Tentar calcular em tempo real
            score_valor = await self.response_repo.get_score_medio_periodo(
                periodo, empresa_id
            )
            total = await self.response_repo.count_by_periodo(periodo, empresa_id)

            if total == 0:
                return None

            return ClimateByEmpresa(
                empresa_id=empresa_id,
                empresa_nome="Empresa",
                periodo=periodo,
                score=round(score_valor, 2),
                score_anterior=0.0,
                variacao=0.0,
                classificacao=self._classificar_score(score_valor),
                total_respostas=total,
                total_funcionarios=0,
                taxa_participacao=0.0,
                scores_dimensao={},
                enps_score=0.0,
                total_postos=0,
                total_equipes=0,
                postos_criticos=0,
                equipes_criticas=0,
            )

        score_ant = await self.score_repo.get_by_entidade_periodo(
            EntityType.EMPRESA, empresa_id, periodo_anterior
        )

        variacao = 0.0
        if score_ant and score_ant.score > 0:
            variacao = ((score.score - score_ant.score) / score_ant.score) * 100

        # Contar postos e equipes criticos
        postos_criticos = len(
            await self.score_repo.get_bottom_scores(
                periodo, EntityType.POSTO, 100, empresa_id
            )
        )
        equipes_criticas = len(
            await self.score_repo.get_bottom_scores(
                periodo, EntityType.EQUIPE, 100, empresa_id
            )
        )

        return ClimateByEmpresa(
            empresa_id=empresa_id,
            empresa_nome=score.entidade_nome or "Empresa",
            periodo=periodo,
            score=score.score,
            score_anterior=score_ant.score if score_ant else 0.0,
            variacao=round(variacao, 2),
            classificacao=self._classificar_score(score.score),
            total_respostas=score.total_respostas,
            total_funcionarios=0,  # TODO
            taxa_participacao=score.taxa_participacao,
            scores_dimensao=score.scores_dimensao,
            enps_score=score.enps_score,
            total_postos=0,  # TODO
            total_equipes=0,  # TODO
            postos_criticos=postos_criticos,
            equipes_criticas=equipes_criticas,
        )

    # =========================================================================
    # Alertas
    # =========================================================================

    async def verificar_quedas(
        self,
        empresa_id: Optional[str] = None,
    ) -> List[Any]:
        """
        Detecta quedas significativas (>20%) para alertar.

        Args:
            empresa_id: Filtrar por empresa

        Returns:
            Lista de alertas gerados
        """
        periodo_atual = datetime.now().strftime("%Y-%m")

        # Buscar scores atuais
        scores = await self.score_repo.get_scores_by_periodo(
            periodo_atual, empresa_id=empresa_id
        )

        alertas_gerados = []

        for score in scores:
            if score.tendencia < -self.QUEDA_ALERTA_PERCENTUAL:
                # Verificar se alerta ja existe
                existe = await self.alert_repo.check_existing_alert(
                    EntityType(score.entidade_tipo),
                    score.entidade_id,
                    periodo_atual,
                    "queda_score",
                )

                if not existe:
                    alerta = await self.alert_repo.create(
                        entidade_tipo=EntityType(score.entidade_tipo),
                        entidade_id=score.entidade_id,
                        periodo=periodo_atual,
                        tipo_alerta="queda_score",
                        mensagem=f"Queda de {abs(score.tendencia):.1f}% no score",
                        severidade=(
                            AlertSeverity.CRITICA
                            if score.tendencia < -40
                            else AlertSeverity.ALTA
                        ),
                        score_atual=score.score,
                        variacao=score.tendencia,
                        entidade_nome=score.entidade_nome,
                        empresa_id=score.empresa_id,
                    )
                    alertas_gerados.append(alerta)

        logger.info(f"Verificacao de quedas: {len(alertas_gerados)} alertas gerados")
        return alertas_gerados


# Singleton para uso em dependencias
def get_climate_service(db: AsyncSession) -> ClimateService:
    """
    Factory function para obter instancia do servico.

    Args:
        db: Sessao do banco de dados

    Returns:
        Instancia do ClimateService
    """
    return ClimateService(db)
