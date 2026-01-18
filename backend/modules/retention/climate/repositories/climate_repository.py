"""
Repository para operacoes de banco de dados com Pesquisa de Clima.

Implementa padrao Repository com operacoes CRUD async usando SQLAlchemy 2.0.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.retention.climate.models.climate_models import (
    AlertSeverity,
    ClimateAlert,
    ClimateResponse,
    ClimateScore,
    ClimateSurvey,
    EntityType,
)
from modules.retention.climate.schemas.climate_schemas import (
    ClimateFilter,
    SurveyCreate,
    SurveyUpdate,
)


class ClimateSurveyRepository:
    """Repository para operacoes CRUD de ClimateSurvey."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o repository.

        Args:
            db: Sessao async do banco de dados
        """
        self.db = db

    async def create(self, data: SurveyCreate, created_by: Optional[str] = None) -> ClimateSurvey:
        """
        Cria uma nova pesquisa de clima.

        Args:
            data: Dados da pesquisa
            created_by: ID do usuario criador

        Returns:
            ClimateSurvey criada
        """
        # Converter perguntas para formato dict
        perguntas_dict = [q.model_dump() for q in data.perguntas] if data.perguntas else []

        survey = ClimateSurvey(
            id=str(uuid4()),
            nome=data.nome,
            descricao=data.descricao,
            perguntas=perguntas_dict,
            frequencia=data.frequencia.value,
            ativo=True,
            data_inicio=data.data_inicio or datetime.now(),
            data_fim=data.data_fim,
            empresa_id=data.empresa_id,
            created_by=created_by,
        )

        self.db.add(survey)
        await self.db.commit()
        await self.db.refresh(survey)

        logger.info(f"ClimateSurvey criada: {survey.id} - {survey.nome}")
        return survey

    async def get_by_id(self, survey_id: str) -> Optional[ClimateSurvey]:
        """
        Busca pesquisa por ID.

        Args:
            survey_id: ID da pesquisa

        Returns:
            ClimateSurvey ou None
        """
        result = await self.db.execute(
            select(ClimateSurvey).where(ClimateSurvey.id == survey_id)
        )
        return result.scalar_one_or_none()

    async def get_active(self, empresa_id: Optional[str] = None) -> Optional[ClimateSurvey]:
        """
        Busca pesquisa ativa.

        Args:
            empresa_id: Filtrar por empresa

        Returns:
            ClimateSurvey ativa ou None
        """
        now = datetime.now()
        query = select(ClimateSurvey).where(
            ClimateSurvey.ativo.is_(True),
            or_(ClimateSurvey.data_fim.is_(None), ClimateSurvey.data_fim > now),
        )

        if empresa_id:
            query = query.where(
                or_(
                    ClimateSurvey.empresa_id == empresa_id,
                    ClimateSurvey.empresa_id.is_(None),
                )
            )

        query = query.order_by(ClimateSurvey.created_at.desc())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        empresa_id: Optional[str] = None,
        ativo: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ClimateSurvey], int]:
        """
        Lista pesquisas com filtros e paginacao.

        Args:
            empresa_id: Filtrar por empresa
            ativo: Filtrar por status
            page: Pagina atual
            page_size: Itens por pagina

        Returns:
            Tupla (pesquisas, total)
        """
        query = select(ClimateSurvey)
        count_query = select(func.count(ClimateSurvey.id))

        if empresa_id:
            query = query.where(
                or_(
                    ClimateSurvey.empresa_id == empresa_id,
                    ClimateSurvey.empresa_id.is_(None),
                )
            )
            count_query = count_query.where(
                or_(
                    ClimateSurvey.empresa_id == empresa_id,
                    ClimateSurvey.empresa_id.is_(None),
                )
            )

        if ativo is not None:
            query = query.where(ClimateSurvey.ativo == ativo)
            count_query = count_query.where(ClimateSurvey.ativo == ativo)

        # Total
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginacao
        query = query.order_by(ClimateSurvey.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        surveys = list(result.scalars().all())

        return surveys, total

    async def update(self, survey_id: str, data: SurveyUpdate) -> Optional[ClimateSurvey]:
        """
        Atualiza uma pesquisa.

        Args:
            survey_id: ID da pesquisa
            data: Dados para atualizacao

        Returns:
            ClimateSurvey atualizada ou None
        """
        survey = await self.get_by_id(survey_id)
        if not survey:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "perguntas" and value:
                value = [q.model_dump() if hasattr(q, "model_dump") else q for q in value]
            if field == "frequencia" and value:
                value = value.value if hasattr(value, "value") else value
            setattr(survey, field, value)

        survey.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(survey)

        logger.info(f"ClimateSurvey atualizada: {survey.id}")
        return survey

    async def delete(self, survey_id: str) -> bool:
        """
        Desativa uma pesquisa (soft delete).

        Args:
            survey_id: ID da pesquisa

        Returns:
            True se desativada
        """
        survey = await self.get_by_id(survey_id)
        if not survey:
            return False

        survey.ativo = False
        survey.updated_at = datetime.now()

        await self.db.commit()

        logger.info(f"ClimateSurvey desativada: {survey.id}")
        return True

    async def update_stats(
        self,
        survey_id: str,
        total_respostas: int,
        score_medio: float,
    ) -> None:
        """
        Atualiza estatisticas da pesquisa.

        Args:
            survey_id: ID da pesquisa
            total_respostas: Total de respostas
            score_medio: Score medio
        """
        survey = await self.get_by_id(survey_id)
        if survey:
            survey.total_respostas = total_respostas
            survey.score_medio = score_medio
            survey.updated_at = datetime.now()
            await self.db.commit()


class ClimateResponseRepository:
    """Repository para operacoes CRUD de ClimateResponse."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o repository.

        Args:
            db: Sessao async do banco de dados
        """
        self.db = db

    async def create(
        self,
        survey_id: str,
        funcionario_hash: str,
        respostas: Dict[str, int],
        score_calculado: float,
        scores_por_dimensao: Dict[str, float],
        tempo_resposta_segundos: int,
        posto_id: Optional[str] = None,
        equipe_id: Optional[str] = None,
        empresa_id: Optional[str] = None,
        cliente_id: Optional[str] = None,
        comentarios: Optional[Dict[str, str]] = None,
        ip_hash: Optional[str] = None,
        user_agent_hash: Optional[str] = None,
    ) -> ClimateResponse:
        """
        Cria uma nova resposta de pesquisa.

        Args:
            survey_id: ID da pesquisa
            funcionario_hash: Hash do funcionario (anonimizado)
            respostas: Respostas {pergunta_id: valor}
            score_calculado: Score calculado
            scores_por_dimensao: Scores por dimensao
            tempo_resposta_segundos: Tempo de resposta
            posto_id: ID do posto
            equipe_id: ID da equipe
            empresa_id: ID da empresa
            cliente_id: ID do cliente
            comentarios: Comentarios opcionais
            ip_hash: Hash do IP
            user_agent_hash: Hash do User-Agent

        Returns:
            ClimateResponse criada
        """
        now = datetime.now()
        periodo = now.strftime("%Y-%m")

        response = ClimateResponse(
            id=str(uuid4()),
            survey_id=survey_id,
            funcionario_hash=funcionario_hash,
            posto_id=posto_id,
            equipe_id=equipe_id,
            empresa_id=empresa_id,
            cliente_id=cliente_id,
            periodo=periodo,
            data_resposta=now,
            respostas=respostas,
            comentarios=comentarios,
            score_calculado=score_calculado,
            scores_por_dimensao=scores_por_dimensao,
            tempo_resposta_segundos=tempo_resposta_segundos,
            is_complete=True,
            ip_hash=ip_hash,
            user_agent_hash=user_agent_hash,
        )

        self.db.add(response)
        await self.db.commit()
        await self.db.refresh(response)

        logger.debug(f"ClimateResponse criada: {response.id}")
        return response

    async def get_by_id(self, response_id: str) -> Optional[ClimateResponse]:
        """
        Busca resposta por ID.

        Args:
            response_id: ID da resposta

        Returns:
            ClimateResponse ou None
        """
        result = await self.db.execute(
            select(ClimateResponse).where(ClimateResponse.id == response_id)
        )
        return result.scalar_one_or_none()

    async def check_already_responded(
        self,
        survey_id: str,
        funcionario_hash: str,
        periodo: str,
    ) -> bool:
        """
        Verifica se funcionario ja respondeu no periodo.

        Args:
            survey_id: ID da pesquisa
            funcionario_hash: Hash do funcionario
            periodo: Periodo YYYY-MM

        Returns:
            True se ja respondeu
        """
        result = await self.db.execute(
            select(func.count(ClimateResponse.id)).where(
                ClimateResponse.survey_id == survey_id,
                ClimateResponse.funcionario_hash == funcionario_hash,
                ClimateResponse.periodo == periodo,
            )
        )
        count = result.scalar() or 0
        return count > 0

    async def get_responses_by_periodo(
        self,
        survey_id: str,
        periodo_inicio: str,
        periodo_fim: str,
    ) -> List[ClimateResponse]:
        """
        Busca respostas por periodo.

        Args:
            survey_id: ID da pesquisa
            periodo_inicio: Periodo inicial YYYY-MM
            periodo_fim: Periodo final YYYY-MM

        Returns:
            Lista de respostas
        """
        result = await self.db.execute(
            select(ClimateResponse)
            .where(
                ClimateResponse.survey_id == survey_id,
                ClimateResponse.periodo >= periodo_inicio,
                ClimateResponse.periodo <= periodo_fim,
            )
            .order_by(ClimateResponse.data_resposta)
        )
        return list(result.scalars().all())

    async def get_responses_by_entidade(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
    ) -> List[ClimateResponse]:
        """
        Busca respostas por entidade e periodo.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo YYYY-MM

        Returns:
            Lista de respostas
        """
        query = select(ClimateResponse).where(ClimateResponse.periodo == periodo)

        if entidade_tipo == EntityType.POSTO:
            query = query.where(ClimateResponse.posto_id == entidade_id)
        elif entidade_tipo == EntityType.EQUIPE:
            query = query.where(ClimateResponse.equipe_id == entidade_id)
        elif entidade_tipo == EntityType.EMPRESA:
            query = query.where(ClimateResponse.empresa_id == entidade_id)
        elif entidade_tipo == EntityType.CLIENTE:
            query = query.where(ClimateResponse.cliente_id == entidade_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_periodo(
        self,
        periodo: str,
        empresa_id: Optional[str] = None,
    ) -> int:
        """
        Conta respostas por periodo.

        Args:
            periodo: Periodo YYYY-MM
            empresa_id: Filtrar por empresa

        Returns:
            Total de respostas
        """
        query = select(func.count(ClimateResponse.id)).where(
            ClimateResponse.periodo == periodo
        )

        if empresa_id:
            query = query.where(ClimateResponse.empresa_id == empresa_id)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_score_medio_periodo(
        self,
        periodo: str,
        empresa_id: Optional[str] = None,
    ) -> float:
        """
        Calcula score medio do periodo.

        Args:
            periodo: Periodo YYYY-MM
            empresa_id: Filtrar por empresa

        Returns:
            Score medio
        """
        query = select(func.avg(ClimateResponse.score_calculado)).where(
            ClimateResponse.periodo == periodo
        )

        if empresa_id:
            query = query.where(ClimateResponse.empresa_id == empresa_id)

        result = await self.db.execute(query)
        avg = result.scalar()
        return round(float(avg), 2) if avg else 0.0

    async def list_by_filters(
        self,
        filters: ClimateFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ClimateResponse], int]:
        """
        Lista respostas com filtros.

        Args:
            filters: Filtros de busca
            page: Pagina atual
            page_size: Itens por pagina

        Returns:
            Tupla (respostas, total)
        """
        query = select(ClimateResponse)
        count_query = select(func.count(ClimateResponse.id))

        # Aplicar filtros
        if filters.empresa_id:
            query = query.where(ClimateResponse.empresa_id == filters.empresa_id)
            count_query = count_query.where(ClimateResponse.empresa_id == filters.empresa_id)

        if filters.posto_id:
            query = query.where(ClimateResponse.posto_id == filters.posto_id)
            count_query = count_query.where(ClimateResponse.posto_id == filters.posto_id)

        if filters.equipe_id:
            query = query.where(ClimateResponse.equipe_id == filters.equipe_id)
            count_query = count_query.where(ClimateResponse.equipe_id == filters.equipe_id)

        if filters.periodo_inicio:
            query = query.where(ClimateResponse.periodo >= filters.periodo_inicio)
            count_query = count_query.where(ClimateResponse.periodo >= filters.periodo_inicio)

        if filters.periodo_fim:
            query = query.where(ClimateResponse.periodo <= filters.periodo_fim)
            count_query = count_query.where(ClimateResponse.periodo <= filters.periodo_fim)

        if filters.score_min is not None:
            query = query.where(ClimateResponse.score_calculado >= filters.score_min)
            count_query = count_query.where(ClimateResponse.score_calculado >= filters.score_min)

        if filters.score_max is not None:
            query = query.where(ClimateResponse.score_calculado <= filters.score_max)
            count_query = count_query.where(ClimateResponse.score_calculado <= filters.score_max)

        # Total
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginacao
        query = query.order_by(ClimateResponse.data_resposta.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        responses = list(result.scalars().all())

        return responses, total


class ClimateScoreRepository:
    """Repository para operacoes CRUD de ClimateScore."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o repository.

        Args:
            db: Sessao async do banco de dados
        """
        self.db = db

    async def create_or_update(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
        score: float,
        scores_dimensao: Dict[str, float],
        total_respostas: int,
        taxa_participacao: float = 0.0,
        tendencia: float = 0.0,
        fatores_positivos: Optional[List[str]] = None,
        fatores_negativos: Optional[List[str]] = None,
        enps_score: float = 0.0,
        enps_promotores: int = 0,
        enps_neutros: int = 0,
        enps_detratores: int = 0,
        entidade_nome: Optional[str] = None,
        empresa_id: Optional[str] = None,
        alertas: Optional[List[Dict[str, Any]]] = None,
    ) -> ClimateScore:
        """
        Cria ou atualiza um score de clima.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo YYYY-MM
            score: Score geral
            scores_dimensao: Scores por dimensao
            total_respostas: Total de respostas
            taxa_participacao: Taxa de participacao
            tendencia: Variacao vs periodo anterior
            fatores_positivos: Pontos positivos
            fatores_negativos: Pontos negativos
            enps_score: Score eNPS
            enps_promotores: Quantidade de promotores
            enps_neutros: Quantidade de neutros
            enps_detratores: Quantidade de detratores
            entidade_nome: Nome da entidade
            empresa_id: ID da empresa
            alertas: Lista de alertas

        Returns:
            ClimateScore criado ou atualizado
        """
        # Verificar se ja existe
        existing = await self.get_by_entidade_periodo(
            entidade_tipo, entidade_id, periodo
        )

        if existing:
            # Atualizar
            existing.score = score
            existing.scores_dimensao = scores_dimensao
            existing.total_respostas = total_respostas
            existing.taxa_participacao = taxa_participacao
            existing.tendencia = tendencia
            existing.fatores_positivos = fatores_positivos or []
            existing.fatores_negativos = fatores_negativos or []
            existing.enps_score = enps_score
            existing.enps_promotores = enps_promotores
            existing.enps_neutros = enps_neutros
            existing.enps_detratores = enps_detratores
            existing.alertas = alertas or []
            existing.calculado_em = datetime.now()
            existing.updated_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(existing)

            logger.debug(f"ClimateScore atualizado: {existing.id}")
            return existing

        # Criar novo
        climate_score = ClimateScore(
            id=str(uuid4()),
            entidade_tipo=entidade_tipo.value,
            entidade_id=entidade_id,
            entidade_nome=entidade_nome,
            empresa_id=empresa_id,
            periodo=periodo,
            score=score,
            scores_dimensao=scores_dimensao,
            tendencia=tendencia,
            total_respostas=total_respostas,
            taxa_participacao=taxa_participacao,
            fatores_positivos=fatores_positivos or [],
            fatores_negativos=fatores_negativos or [],
            enps_score=enps_score,
            enps_promotores=enps_promotores,
            enps_neutros=enps_neutros,
            enps_detratores=enps_detratores,
            alertas=alertas or [],
            calculado_em=datetime.now(),
        )

        self.db.add(climate_score)
        await self.db.commit()
        await self.db.refresh(climate_score)

        logger.debug(f"ClimateScore criado: {climate_score.id}")
        return climate_score

    async def get_by_id(self, score_id: str) -> Optional[ClimateScore]:
        """
        Busca score por ID.

        Args:
            score_id: ID do score

        Returns:
            ClimateScore ou None
        """
        result = await self.db.execute(
            select(ClimateScore).where(ClimateScore.id == score_id)
        )
        return result.scalar_one_or_none()

    async def get_by_entidade_periodo(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
    ) -> Optional[ClimateScore]:
        """
        Busca score por entidade e periodo.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo YYYY-MM

        Returns:
            ClimateScore ou None
        """
        result = await self.db.execute(
            select(ClimateScore).where(
                ClimateScore.entidade_tipo == entidade_tipo.value,
                ClimateScore.entidade_id == entidade_id,
                ClimateScore.periodo == periodo,
            )
        )
        return result.scalar_one_or_none()

    async def get_scores_by_entidade(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodos: int = 6,
    ) -> List[ClimateScore]:
        """
        Busca historico de scores de uma entidade.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodos: Quantidade de periodos

        Returns:
            Lista de scores ordenados por periodo
        """
        result = await self.db.execute(
            select(ClimateScore)
            .where(
                ClimateScore.entidade_tipo == entidade_tipo.value,
                ClimateScore.entidade_id == entidade_id,
            )
            .order_by(ClimateScore.periodo.desc())
            .limit(periodos)
        )
        scores = list(result.scalars().all())
        return sorted(scores, key=lambda x: x.periodo)

    async def get_scores_by_periodo(
        self,
        periodo: str,
        entidade_tipo: Optional[EntityType] = None,
        empresa_id: Optional[str] = None,
    ) -> List[ClimateScore]:
        """
        Busca scores de um periodo.

        Args:
            periodo: Periodo YYYY-MM
            entidade_tipo: Filtrar por tipo
            empresa_id: Filtrar por empresa

        Returns:
            Lista de scores
        """
        query = select(ClimateScore).where(ClimateScore.periodo == periodo)

        if entidade_tipo:
            query = query.where(ClimateScore.entidade_tipo == entidade_tipo.value)

        if empresa_id:
            query = query.where(ClimateScore.empresa_id == empresa_id)

        query = query.order_by(ClimateScore.score.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_top_scores(
        self,
        periodo: str,
        entidade_tipo: EntityType,
        limit: int = 5,
        empresa_id: Optional[str] = None,
    ) -> List[ClimateScore]:
        """
        Busca melhores scores do periodo.

        Args:
            periodo: Periodo YYYY-MM
            entidade_tipo: Tipo da entidade
            limit: Quantidade de resultados
            empresa_id: Filtrar por empresa

        Returns:
            Lista de melhores scores
        """
        query = select(ClimateScore).where(
            ClimateScore.periodo == periodo,
            ClimateScore.entidade_tipo == entidade_tipo.value,
        )

        if empresa_id:
            query = query.where(ClimateScore.empresa_id == empresa_id)

        query = query.order_by(ClimateScore.score.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_bottom_scores(
        self,
        periodo: str,
        entidade_tipo: EntityType,
        limit: int = 5,
        empresa_id: Optional[str] = None,
    ) -> List[ClimateScore]:
        """
        Busca piores scores do periodo.

        Args:
            periodo: Periodo YYYY-MM
            entidade_tipo: Tipo da entidade
            limit: Quantidade de resultados
            empresa_id: Filtrar por empresa

        Returns:
            Lista de piores scores
        """
        query = select(ClimateScore).where(
            ClimateScore.periodo == periodo,
            ClimateScore.entidade_tipo == entidade_tipo.value,
            ClimateScore.total_respostas > 0,  # Apenas com respostas
        )

        if empresa_id:
            query = query.where(ClimateScore.empresa_id == empresa_id)

        query = query.order_by(ClimateScore.score.asc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def calcular_score_agregado(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
    ) -> Dict[str, Any]:
        """
        Calcula score agregado de uma entidade.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo YYYY-MM

        Returns:
            Dicionario com score e estatisticas
        """
        # Buscar respostas
        response_repo = ClimateResponseRepository(self.db)
        respostas = await response_repo.get_responses_by_entidade(
            entidade_tipo, entidade_id, periodo
        )

        if not respostas:
            return {
                "score": 0.0,
                "total_respostas": 0,
                "scores_dimensao": {},
            }

        # Calcular media
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

        return {
            "score": round(score_medio, 2),
            "total_respostas": len(respostas),
            "scores_dimensao": scores_dimensao,
        }


class ClimateAlertRepository:
    """Repository para operacoes CRUD de ClimateAlert."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o repository.

        Args:
            db: Sessao async do banco de dados
        """
        self.db = db

    async def create(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
        tipo_alerta: str,
        mensagem: str,
        severidade: AlertSeverity = AlertSeverity.MEDIA,
        score_atual: float = 0.0,
        score_anterior: Optional[float] = None,
        variacao: float = 0.0,
        dimensao: Optional[str] = None,
        entidade_nome: Optional[str] = None,
        empresa_id: Optional[str] = None,
    ) -> ClimateAlert:
        """
        Cria um novo alerta de clima.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo
            tipo_alerta: Tipo do alerta
            mensagem: Mensagem do alerta
            severidade: Severidade
            score_atual: Score atual
            score_anterior: Score anterior
            variacao: Variacao
            dimensao: Dimensao afetada
            entidade_nome: Nome da entidade
            empresa_id: ID da empresa

        Returns:
            ClimateAlert criado
        """
        alert = ClimateAlert(
            id=str(uuid4()),
            empresa_id=empresa_id,
            entidade_tipo=entidade_tipo.value,
            entidade_id=entidade_id,
            entidade_nome=entidade_nome,
            periodo=periodo,
            tipo_alerta=tipo_alerta,
            dimensao=dimensao,
            severidade=severidade.value,
            mensagem=mensagem,
            score_atual=score_atual,
            score_anterior=score_anterior,
            variacao=variacao,
            resolvido=False,
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.warning(f"ClimateAlert criado: {alert.tipo_alerta} - {alert.mensagem}")
        return alert

    async def get_by_id(self, alert_id: str) -> Optional[ClimateAlert]:
        """
        Busca alerta por ID.

        Args:
            alert_id: ID do alerta

        Returns:
            ClimateAlert ou None
        """
        result = await self.db.execute(
            select(ClimateAlert).where(ClimateAlert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        empresa_id: Optional[str] = None,
        severidade: Optional[AlertSeverity] = None,
        limit: int = 50,
    ) -> List[ClimateAlert]:
        """
        Lista alertas ativos.

        Args:
            empresa_id: Filtrar por empresa
            severidade: Filtrar por severidade
            limit: Limite de resultados

        Returns:
            Lista de alertas ativos
        """
        query = select(ClimateAlert).where(ClimateAlert.resolvido.is_(False))

        if empresa_id:
            query = query.where(ClimateAlert.empresa_id == empresa_id)

        if severidade:
            query = query.where(ClimateAlert.severidade == severidade.value)

        query = query.order_by(
            ClimateAlert.severidade.desc(),
            ClimateAlert.created_at.desc(),
        ).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_severidade(
        self,
        empresa_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Conta alertas ativos por severidade.

        Args:
            empresa_id: Filtrar por empresa

        Returns:
            Contagem por severidade
        """
        counts = {s.value: 0 for s in AlertSeverity}

        for severidade in AlertSeverity:
            query = select(func.count(ClimateAlert.id)).where(
                ClimateAlert.resolvido.is_(False),
                ClimateAlert.severidade == severidade.value,
            )

            if empresa_id:
                query = query.where(ClimateAlert.empresa_id == empresa_id)

            result = await self.db.execute(query)
            counts[severidade.value] = result.scalar() or 0

        return counts

    async def resolve(
        self,
        alert_id: str,
        resolvido_por: str,
        notas_resolucao: Optional[str] = None,
    ) -> Optional[ClimateAlert]:
        """
        Resolve um alerta.

        Args:
            alert_id: ID do alerta
            resolvido_por: ID do usuario
            notas_resolucao: Notas da resolucao

        Returns:
            ClimateAlert resolvido ou None
        """
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None

        alert.resolvido = True
        alert.resolvido_em = datetime.now()
        alert.resolvido_por = resolvido_por
        alert.notas_resolucao = notas_resolucao

        await self.db.commit()
        await self.db.refresh(alert)

        logger.info(f"ClimateAlert resolvido: {alert.id}")
        return alert

    async def check_existing_alert(
        self,
        entidade_tipo: EntityType,
        entidade_id: str,
        periodo: str,
        tipo_alerta: str,
    ) -> bool:
        """
        Verifica se ja existe alerta similar ativo.

        Args:
            entidade_tipo: Tipo da entidade
            entidade_id: ID da entidade
            periodo: Periodo
            tipo_alerta: Tipo do alerta

        Returns:
            True se ja existe
        """
        result = await self.db.execute(
            select(func.count(ClimateAlert.id)).where(
                ClimateAlert.entidade_tipo == entidade_tipo.value,
                ClimateAlert.entidade_id == entidade_id,
                ClimateAlert.periodo == periodo,
                ClimateAlert.tipo_alerta == tipo_alerta,
                ClimateAlert.resolvido.is_(False),
            )
        )
        count = result.scalar() or 0
        return count > 0
