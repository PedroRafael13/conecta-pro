"""
Repository para Perfil Operacional.

Camada de acesso a dados para perfis operacionais e matches.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any

from sqlalchemy import select, func, and_, or_, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.retention.profile.models.profile_models import (
    OperationalProfile,
    ProfileQuestion,
    PostMatch,
    QUESTIONARIO_PERFIL,
)
from modules.retention.profile.schemas.profile_schemas import (
    SubmitRespostasRequest,
    ProfileFilter,
    MatchFilter,
    ProfileQuestionCreate,
    ProfileQuestionUpdate,
    CalculateMatchRequest,
)

logger = logging.getLogger(__name__)


class ProfileRepository:
    """Repository para operacoes de Perfil Operacional."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    # ============================================================
    # CRUD de OperationalProfile
    # ============================================================

    async def create_profile(
        self,
        funcionario_id: str,
        scores: Dict[str, int],
        respostas: Dict[str, int],
        tempo_resposta: Optional[int] = None,
        condominium_id: Optional[str] = None,
    ) -> OperationalProfile:
        """
        Cria um novo perfil operacional.

        Args:
            funcionario_id: UUID do funcionario
            scores: Scores calculados por dimensao
            respostas: Respostas brutas do questionario
            tempo_resposta: Tempo total em segundos
            condominium_id: UUID do condominio

        Returns:
            Perfil criado
        """
        # Identifica perfil predominante
        perfil_predominante = max(scores, key=scores.get)

        profile = OperationalProfile(
            funcionario_id=funcionario_id,
            vigilancia=scores.get("vigilancia", 0),
            comunicacao=scores.get("comunicacao", 0),
            resiliencia=scores.get("resiliencia", 0),
            lideranca=scores.get("lideranca", 0),
            perfil_predominante=perfil_predominante,
            respostas=respostas,
            tempo_resposta_segundos=tempo_resposta,
            em_andamento=False,
            condominium_id=condominium_id,
        )

        self.session.add(profile)
        await self.session.flush()

        logger.info(
            f"Perfil operacional criado para funcionario {funcionario_id}",
            extra={
                "profile_id": profile.id,
                "perfil_predominante": perfil_predominante,
            },
        )

        return profile

    async def get_profile_by_id(self, profile_id: str) -> Optional[OperationalProfile]:
        """Busca perfil por ID."""
        result = await self.session.execute(
            select(OperationalProfile).where(OperationalProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_profile(
        self, funcionario_id: str, apenas_valido: bool = True
    ) -> Optional[OperationalProfile]:
        """
        Busca o perfil mais recente do funcionario.

        Args:
            funcionario_id: UUID do funcionario
            apenas_valido: Se deve retornar apenas perfis validos

        Returns:
            Perfil mais recente ou None
        """
        query = (
            select(OperationalProfile)
            .where(
                and_(
                    OperationalProfile.funcionario_id == funcionario_id,
                    OperationalProfile.em_andamento.is_(False),
                )
            )
            .order_by(desc(OperationalProfile.data_avaliacao))
        )

        if apenas_valido:
            query = query.where(OperationalProfile.is_valid.is_(True))

        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none()

    async def get_profile_history(
        self,
        funcionario_id: str,
        limit: int = 10,
        apenas_validos: bool = True,
    ) -> List[OperationalProfile]:
        """
        Busca historico de perfis do funcionario.

        Args:
            funcionario_id: UUID do funcionario
            limit: Limite de resultados
            apenas_validos: Se deve filtrar apenas validos

        Returns:
            Lista de perfis ordenados por data
        """
        query = (
            select(OperationalProfile)
            .where(
                and_(
                    OperationalProfile.funcionario_id == funcionario_id,
                    OperationalProfile.em_andamento.is_(False),
                )
            )
            .order_by(desc(OperationalProfile.data_avaliacao))
            .limit(limit)
        )

        if apenas_validos:
            query = query.where(OperationalProfile.is_valid.is_(True))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_profiles(
        self,
        filters: Optional[ProfileFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[OperationalProfile], int]:
        """
        Lista perfis com filtros e paginacao.

        Args:
            filters: Filtros opcionais
            skip: Offset
            limit: Limite
            order_by: Campo para ordenacao
            order_desc: Ordem descendente

        Returns:
            Tuple (lista de perfis, total)
        """
        query = select(OperationalProfile).where(
            OperationalProfile.em_andamento.is_(False)
        )

        if filters:
            if filters.funcionario_id:
                query = query.where(
                    OperationalProfile.funcionario_id == filters.funcionario_id
                )
            if filters.perfil_predominante:
                query = query.where(
                    OperationalProfile.perfil_predominante == filters.perfil_predominante.value
                )
            if filters.score_minimo is not None:
                # Filtra por score medio minimo
                score_medio = (
                    OperationalProfile.vigilancia
                    + OperationalProfile.comunicacao
                    + OperationalProfile.resiliencia
                    + OperationalProfile.lideranca
                ) / 4
                query = query.where(score_medio >= filters.score_minimo)
            if filters.score_maximo is not None:
                score_medio = (
                    OperationalProfile.vigilancia
                    + OperationalProfile.comunicacao
                    + OperationalProfile.resiliencia
                    + OperationalProfile.lideranca
                ) / 4
                query = query.where(score_medio <= filters.score_maximo)
            if filters.data_inicio:
                query = query.where(
                    OperationalProfile.data_avaliacao >= filters.data_inicio
                )
            if filters.data_fim:
                query = query.where(
                    OperationalProfile.data_avaliacao <= filters.data_fim
                )
            if filters.condominium_id:
                query = query.where(
                    OperationalProfile.condominium_id == filters.condominium_id
                )
            if filters.apenas_validos:
                query = query.where(OperationalProfile.is_valid.is_(True))

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenacao
        order_column = getattr(OperationalProfile, order_by, OperationalProfile.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # Paginacao
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        profiles = list(result.scalars().all())

        return profiles, total

    async def invalidate_profile(
        self, profile_id: str, reason: str
    ) -> Optional[OperationalProfile]:
        """Invalida um perfil."""
        profile = await self.get_profile_by_id(profile_id)
        if profile:
            profile.is_valid = False
            profile.invalidation_reason = reason
            await self.session.flush()
            logger.warning(f"Perfil {profile_id} invalidado: {reason}")
        return profile

    # ============================================================
    # Salvamento de Progresso
    # ============================================================

    async def save_progress(
        self,
        funcionario_id: str,
        respostas_parciais: Dict[str, int],
        ultima_pergunta: int,
        condominium_id: Optional[str] = None,
    ) -> OperationalProfile:
        """
        Salva progresso do questionario.

        Args:
            funcionario_id: UUID do funcionario
            respostas_parciais: Respostas ate o momento
            ultima_pergunta: Numero da ultima pergunta respondida
            condominium_id: UUID do condominio

        Returns:
            Perfil em andamento
        """
        # Busca perfil em andamento
        result = await self.session.execute(
            select(OperationalProfile).where(
                and_(
                    OperationalProfile.funcionario_id == funcionario_id,
                    OperationalProfile.em_andamento.is_(True),
                )
            )
        )
        profile = result.scalar_one_or_none()

        if profile:
            # Atualiza progresso existente
            profile.progresso_respostas = respostas_parciais
            profile.ultima_pergunta_respondida = ultima_pergunta
        else:
            # Cria novo perfil em andamento
            profile = OperationalProfile(
                funcionario_id=funcionario_id,
                vigilancia=0,
                comunicacao=0,
                resiliencia=0,
                lideranca=0,
                perfil_predominante="vigilancia",
                respostas={},
                em_andamento=True,
                progresso_respostas=respostas_parciais,
                ultima_pergunta_respondida=ultima_pergunta,
                condominium_id=condominium_id,
            )
            self.session.add(profile)

        await self.session.flush()
        return profile

    async def get_progress(self, funcionario_id: str) -> Optional[OperationalProfile]:
        """Busca progresso salvo do funcionario."""
        result = await self.session.execute(
            select(OperationalProfile).where(
                and_(
                    OperationalProfile.funcionario_id == funcionario_id,
                    OperationalProfile.em_andamento.is_(True),
                )
            )
        )
        return result.scalar_one_or_none()

    async def delete_progress(self, funcionario_id: str) -> bool:
        """Remove progresso salvo."""
        result = await self.session.execute(
            select(OperationalProfile).where(
                and_(
                    OperationalProfile.funcionario_id == funcionario_id,
                    OperationalProfile.em_andamento.is_(True),
                )
            )
        )
        profile = result.scalar_one_or_none()
        if profile:
            await self.session.delete(profile)
            await self.session.flush()
            return True
        return False

    # ============================================================
    # CRUD de ProfileQuestion
    # ============================================================

    async def get_questions(
        self,
        versao: str = "1.0.0",
        condominium_id: Optional[str] = None,
        apenas_ativas: bool = True,
    ) -> List[ProfileQuestion]:
        """
        Busca perguntas do questionario.

        Args:
            versao: Versao do questionario
            condominium_id: Filtrar por condominio (null = global)
            apenas_ativas: Filtrar apenas ativas

        Returns:
            Lista de perguntas ordenadas
        """
        query = (
            select(ProfileQuestion)
            .where(ProfileQuestion.versao == versao)
            .order_by(ProfileQuestion.ordem)
        )

        if apenas_ativas:
            query = query.where(ProfileQuestion.ativo.is_(True))

        if condominium_id:
            query = query.where(
                or_(
                    ProfileQuestion.condominium_id == condominium_id,
                    ProfileQuestion.condominium_id.is_(None),
                )
            )
        else:
            query = query.where(ProfileQuestion.condominium_id.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_question(self, data: ProfileQuestionCreate) -> ProfileQuestion:
        """Cria uma nova pergunta."""
        question = ProfileQuestion(
            codigo=data.codigo,
            texto=data.texto,
            dimensao=data.dimensao.value,
            ordem=data.ordem,
            peso=data.peso,
            versao=data.versao,
            condominium_id=data.condominium_id,
        )
        self.session.add(question)
        await self.session.flush()
        return question

    async def update_question(
        self, question_id: str, data: ProfileQuestionUpdate
    ) -> Optional[ProfileQuestion]:
        """Atualiza uma pergunta."""
        result = await self.session.execute(
            select(ProfileQuestion).where(ProfileQuestion.id == question_id)
        )
        question = result.scalar_one_or_none()

        if question:
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(question, field, value)
            await self.session.flush()

        return question

    async def seed_default_questions(self) -> int:
        """
        Popula perguntas padrao do questionario.

        Returns:
            Numero de perguntas criadas
        """
        count = 0
        for q in QUESTIONARIO_PERFIL:
            # Verifica se ja existe
            result = await self.session.execute(
                select(ProfileQuestion).where(ProfileQuestion.codigo == q["id"])
            )
            if not result.scalar_one_or_none():
                question = ProfileQuestion(
                    codigo=q["id"],
                    texto=q["texto"],
                    dimensao=q["dimensao"],
                    ordem=q["ordem"],
                )
                self.session.add(question)
                count += 1

        if count > 0:
            await self.session.flush()
            logger.info(f"Criadas {count} perguntas padrao do questionario")

        return count

    # ============================================================
    # CRUD de PostMatch
    # ============================================================

    async def create_match(
        self,
        funcionario_id: str,
        posto_id: str,
        posto_tipo: str,
        score_match: float,
        profile_id: Optional[str] = None,
        fatores_positivos: Optional[List[str]] = None,
        fatores_negativos: Optional[List[str]] = None,
        scores_detalhados: Optional[Dict[str, Any]] = None,
        condominium_id: Optional[str] = None,
    ) -> PostMatch:
        """
        Cria ou atualiza match entre funcionario e posto.

        Args:
            funcionario_id: UUID do funcionario
            posto_id: UUID do posto
            posto_tipo: Tipo do posto
            score_match: Score calculado
            profile_id: ID do perfil usado no calculo
            fatores_positivos: Pontos fortes
            fatores_negativos: Pontos a desenvolver
            scores_detalhados: Detalhamento por dimensao
            condominium_id: UUID do condominio

        Returns:
            Match criado/atualizado
        """
        # Verifica se ja existe match
        result = await self.session.execute(
            select(PostMatch).where(
                and_(
                    PostMatch.funcionario_id == funcionario_id,
                    PostMatch.posto_id == posto_id,
                )
            )
        )
        match = result.scalar_one_or_none()

        # Determina nivel e recomendacao
        if score_match >= 85:
            nivel = "excelente"
            recomendado = True
        elif score_match >= 70:
            nivel = "alto"
            recomendado = True
        elif score_match >= 50:
            nivel = "medio"
            recomendado = False
        else:
            nivel = "baixo"
            recomendado = False

        if match:
            # Atualiza existente
            match.score_match = score_match
            match.posto_tipo = posto_tipo
            match.profile_id = profile_id
            match.fatores_positivos = fatores_positivos or []
            match.fatores_negativos = fatores_negativos or []
            match.scores_detalhados = scores_detalhados
            match.nivel_match = nivel
            match.recomendado = recomendado
            match.calculado_em = datetime.utcnow()
        else:
            # Cria novo
            match = PostMatch(
                funcionario_id=funcionario_id,
                posto_id=posto_id,
                posto_tipo=posto_tipo,
                profile_id=profile_id,
                score_match=score_match,
                fatores_positivos=fatores_positivos or [],
                fatores_negativos=fatores_negativos or [],
                scores_detalhados=scores_detalhados,
                nivel_match=nivel,
                recomendado=recomendado,
                condominium_id=condominium_id,
            )
            self.session.add(match)

        await self.session.flush()
        return match

    async def get_match(
        self, funcionario_id: str, posto_id: str
    ) -> Optional[PostMatch]:
        """Busca match especifico."""
        result = await self.session.execute(
            select(PostMatch)
            .options(selectinload(PostMatch.profile))
            .where(
                and_(
                    PostMatch.funcionario_id == funcionario_id,
                    PostMatch.posto_id == posto_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_matches_by_funcionario(
        self,
        funcionario_id: str,
        limit: int = 10,
        apenas_recomendados: bool = False,
    ) -> List[PostMatch]:
        """
        Busca melhores matches para um funcionario.

        Args:
            funcionario_id: UUID do funcionario
            limit: Limite de resultados
            apenas_recomendados: Filtrar apenas recomendados

        Returns:
            Lista de matches ordenados por score
        """
        query = (
            select(PostMatch)
            .options(selectinload(PostMatch.profile))
            .where(PostMatch.funcionario_id == funcionario_id)
            .order_by(desc(PostMatch.score_match))
            .limit(limit)
        )

        if apenas_recomendados:
            query = query.where(PostMatch.recomendado.is_(True))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_matches_by_posto(
        self,
        posto_id: str,
        limit: int = 10,
        apenas_recomendados: bool = False,
    ) -> List[PostMatch]:
        """
        Busca melhores funcionarios para um posto.

        Args:
            posto_id: UUID do posto
            limit: Limite de resultados
            apenas_recomendados: Filtrar apenas recomendados

        Returns:
            Lista de matches ordenados por score
        """
        query = (
            select(PostMatch)
            .options(selectinload(PostMatch.profile))
            .where(PostMatch.posto_id == posto_id)
            .order_by(desc(PostMatch.score_match))
            .limit(limit)
        )

        if apenas_recomendados:
            query = query.where(PostMatch.recomendado.is_(True))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_matches(
        self,
        filters: Optional[MatchFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "score_match",
        order_desc: bool = True,
    ) -> Tuple[List[PostMatch], int]:
        """
        Lista matches com filtros e paginacao.

        Args:
            filters: Filtros opcionais
            skip: Offset
            limit: Limite
            order_by: Campo para ordenacao
            order_desc: Ordem descendente

        Returns:
            Tuple (lista de matches, total)
        """
        query = select(PostMatch).options(selectinload(PostMatch.profile))

        if filters:
            if filters.funcionario_id:
                query = query.where(PostMatch.funcionario_id == filters.funcionario_id)
            if filters.posto_id:
                query = query.where(PostMatch.posto_id == filters.posto_id)
            if filters.posto_tipo:
                query = query.where(PostMatch.posto_tipo == filters.posto_tipo.value)
            if filters.score_minimo is not None:
                query = query.where(PostMatch.score_match >= filters.score_minimo)
            if filters.apenas_recomendados:
                query = query.where(PostMatch.recomendado.is_(True))
            if filters.nivel_match:
                query = query.where(PostMatch.nivel_match == filters.nivel_match.value)
            if filters.condominium_id:
                query = query.where(PostMatch.condominium_id == filters.condominium_id)

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenacao
        order_column = getattr(PostMatch, order_by, PostMatch.score_match)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # Paginacao
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        matches = list(result.scalars().all())

        return matches, total

    async def delete_matches_by_funcionario(self, funcionario_id: str) -> int:
        """Remove todos os matches de um funcionario."""
        result = await self.session.execute(
            select(PostMatch).where(PostMatch.funcionario_id == funcionario_id)
        )
        matches = result.scalars().all()
        count = len(matches)
        for match in matches:
            await self.session.delete(match)
        await self.session.flush()
        return count

    # ============================================================
    # Estatisticas e Dashboard
    # ============================================================

    async def get_stats(self, condominium_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcula estatisticas gerais.

        Args:
            condominium_id: Filtrar por condominio

        Returns:
            Dict com estatisticas
        """
        query = select(OperationalProfile).where(
            and_(
                OperationalProfile.em_andamento.is_(False),
                OperationalProfile.is_valid.is_(True),
            )
        )

        if condominium_id:
            query = query.where(OperationalProfile.condominium_id == condominium_id)

        result = await self.session.execute(query)
        profiles = list(result.scalars().all())

        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        stats = {
            "total_avaliacoes": len(profiles),
            "avaliacoes_mes": 0,
            "avaliacoes_semana": 0,
            "media_vigilancia": 0.0,
            "media_comunicacao": 0.0,
            "media_resiliencia": 0.0,
            "media_lideranca": 0.0,
            "media_geral": 0.0,
            "distribuicao_perfis": {},
            "desvio_vigilancia": 0.0,
            "desvio_comunicacao": 0.0,
            "desvio_resiliencia": 0.0,
            "desvio_lideranca": 0.0,
        }

        if not profiles:
            return stats

        # Calcula medias e contagens
        vigilancias = []
        comunicacoes = []
        resiliencias = []
        liderancas = []

        for profile in profiles:
            vigilancias.append(profile.vigilancia)
            comunicacoes.append(profile.comunicacao)
            resiliencias.append(profile.resiliencia)
            liderancas.append(profile.lideranca)

            # Contagem por perfil predominante
            key = profile.perfil_predominante
            stats["distribuicao_perfis"][key] = stats["distribuicao_perfis"].get(key, 0) + 1

            # Contagem temporal
            if profile.data_avaliacao.replace(tzinfo=None) >= month_ago:
                stats["avaliacoes_mes"] += 1
            if profile.data_avaliacao.replace(tzinfo=None) >= week_ago:
                stats["avaliacoes_semana"] += 1

        # Medias
        stats["media_vigilancia"] = sum(vigilancias) / len(vigilancias)
        stats["media_comunicacao"] = sum(comunicacoes) / len(comunicacoes)
        stats["media_resiliencia"] = sum(resiliencias) / len(resiliencias)
        stats["media_lideranca"] = sum(liderancas) / len(liderancas)
        stats["media_geral"] = (
            stats["media_vigilancia"]
            + stats["media_comunicacao"]
            + stats["media_resiliencia"]
            + stats["media_lideranca"]
        ) / 4

        # Desvios padrao
        def calc_std(values: List[int], media: float) -> float:
            if len(values) < 2:
                return 0.0
            variance = sum((x - media) ** 2 for x in values) / len(values)
            return variance ** 0.5

        stats["desvio_vigilancia"] = calc_std(vigilancias, stats["media_vigilancia"])
        stats["desvio_comunicacao"] = calc_std(comunicacoes, stats["media_comunicacao"])
        stats["desvio_resiliencia"] = calc_std(resiliencias, stats["media_resiliencia"])
        stats["desvio_lideranca"] = calc_std(liderancas, stats["media_lideranca"])

        return stats

    async def get_funcionarios_sem_perfil(
        self,
        funcionario_ids: List[str],
        condominium_id: Optional[str] = None,
    ) -> List[str]:
        """
        Identifica funcionarios sem perfil avaliado.

        Args:
            funcionario_ids: Lista de IDs de funcionarios
            condominium_id: Filtrar por condominio

        Returns:
            Lista de IDs sem perfil
        """
        query = select(OperationalProfile.funcionario_id).where(
            and_(
                OperationalProfile.funcionario_id.in_(funcionario_ids),
                OperationalProfile.em_andamento.is_(False),
                OperationalProfile.is_valid.is_(True),
            )
        )

        if condominium_id:
            query = query.where(OperationalProfile.condominium_id == condominium_id)

        result = await self.session.execute(query.distinct())
        com_perfil = set(r for r in result.scalars().all())

        return [fid for fid in funcionario_ids if fid not in com_perfil]

    async def get_evolucao_mensal(
        self,
        meses: int = 12,
        condominium_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retorna evolucao mensal de avaliacoes.

        Args:
            meses: Numero de meses retroativos
            condominium_id: Filtrar por condominio

        Returns:
            Lista com dados mensais
        """
        data_inicio = datetime.utcnow() - timedelta(days=meses * 30)

        query = (
            select(
                func.date_trunc("month", OperationalProfile.data_avaliacao).label("mes"),
                func.count(OperationalProfile.id).label("total"),
                func.avg(
                    (
                        OperationalProfile.vigilancia
                        + OperationalProfile.comunicacao
                        + OperationalProfile.resiliencia
                        + OperationalProfile.lideranca
                    )
                    / 4
                ).label("media"),
            )
            .where(
                and_(
                    OperationalProfile.data_avaliacao >= data_inicio,
                    OperationalProfile.em_andamento.is_(False),
                    OperationalProfile.is_valid.is_(True),
                )
            )
            .group_by(func.date_trunc("month", OperationalProfile.data_avaliacao))
            .order_by(func.date_trunc("month", OperationalProfile.data_avaliacao))
        )

        if condominium_id:
            query = query.where(OperationalProfile.condominium_id == condominium_id)

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "mes": row.mes.isoformat() if row.mes else None,
                "total": row.total,
                "media": round(float(row.media or 0), 2),
            }
            for row in rows
        ]
