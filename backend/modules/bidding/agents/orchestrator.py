"""
Orchestrator - Pipeline de agentes para licitacoes
=====================================================
Coordena a execucao sequencial dos agentes:
SCOUT -> ANALYST -> ASSESSOR -> PRICER -> COMPILER
"""

import logging
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from modules.bidding.agents.analyst_agent import AnalystAgent
from modules.bidding.agents.assessor_agent import AssessorAgent, CompanyProfile
from modules.bidding.agents.base_agent import AgentConfig, ExecutionResult, ExecutionStatus
from modules.bidding.agents.compiler_agent import CompilerAgent, CompilerInput
from modules.bidding.agents.pricer_agent import PricerAgent
from modules.bidding.agents.scout_agent import ScoutAgent, ScoutSearchParams
from modules.bidding.agents.sentinel_agent import SentinelAgent

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# DTOs
# ──────────────────────────────────────────────


class PipelineStep(StrEnum):
    """Etapas do pipeline."""

    SCOUT = "scout"
    ANALYST = "analyst"
    ASSESSOR = "assessor"
    PRICER = "pricer"
    COMPILER = "compiler"
    SENTINEL = "sentinel"


class StepResult(BaseModel):
    """Resultado de uma etapa do pipeline."""

    step: PipelineStep
    status: str  # success, failed, skipped
    duration_ms: float = 0.0
    data: dict | list | None = None
    error: str | None = None


class PipelineResult(BaseModel):
    """Resultado consolidado do pipeline."""

    # Controle
    pipeline_id: str = ""
    steps_executados: list[StepResult] = Field(default_factory=list)
    status_geral: str = "pending"  # pending, running, completed, failed, partial

    # Resultado resumido
    total_oportunidades: int = 0
    oportunidade_selecionada: dict | None = None
    analise: dict | None = None
    avaliacao: dict | None = None
    precificacao: dict | None = None
    documentos: dict | None = None
    sentinela: dict | None = None

    # Recomendacao final
    recomendacao_final: str | None = None
    score_final: float | None = None

    # Metadados
    inicio: datetime | None = None
    fim: datetime | None = None
    duracao_total_ms: float = 0.0
    erros: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────


class PipelineOrchestrator:
    """
    Orquestrador do pipeline de licitacoes.

    Executa a cadeia completa ou parcial de agentes:
    1. SCOUT - Busca oportunidades
    2. ANALYST - Analisa edital selecionado
    3. ASSESSOR - Avalia Go/No-Go
    4. PRICER - Calcula preco da proposta
    5. COMPILER - Gera documentos

    Cada etapa alimenta a proxima com seus resultados.
    O pipeline pode ser executado parcialmente (ex: so ANALYST + ASSESSOR).
    """

    def __init__(
        self,
        company_profile: CompanyProfile | None = None,
        agent_config: AgentConfig | None = None,
    ):
        self.company = company_profile or CompanyProfile()
        self.config = agent_config or AgentConfig()
        self.logger = logging.getLogger("bidding.orchestrator")

        # Instanciar agentes
        self.scout = ScoutAgent(self.config)
        self.analyst = AnalystAgent(self.config)
        self.assessor = AssessorAgent(self.config, self.company)
        self.pricer = PricerAgent(self.config)
        self.compiler = CompilerAgent(self.config)
        self.sentinel = SentinelAgent(self.config)

    async def run_full_pipeline(
        self,
        search_params: ScoutSearchParams | None = None,
        oportunidade_index: int = 0,
        gerar_documentos: bool = True,
        verificar_certidoes: bool = True,
    ) -> PipelineResult:
        """
        Executa o pipeline completo: SCOUT -> ANALYST -> ASSESSOR -> PRICER -> COMPILER.

        Args:
            search_params: Parametros de busca para o SCOUT.
            oportunidade_index: Indice da oportunidade a selecionar (0 = mais relevante).
            gerar_documentos: Se True, executa o COMPILER.
            verificar_certidoes: Se True, executa o SENTINEL.

        Returns:
            PipelineResult consolidado.
        """
        import uuid

        pipeline = PipelineResult(
            pipeline_id=str(uuid.uuid4())[:8],
            inicio=datetime.utcnow(),
            status_geral="running",
        )

        steps_to_run = [PipelineStep.SCOUT, PipelineStep.ANALYST, PipelineStep.ASSESSOR, PipelineStep.PRICER]
        if gerar_documentos:
            steps_to_run.append(PipelineStep.COMPILER)
        if verificar_certidoes:
            steps_to_run.append(PipelineStep.SENTINEL)

        # ── STEP 1: SCOUT ──
        scout_result = await self.scout.run(search_params=search_params)
        step = self._build_step_result(PipelineStep.SCOUT, scout_result)
        pipeline.steps_executados.append(step)

        if not scout_result.success or not scout_result.data:
            pipeline.status_geral = "failed"
            pipeline.erros.append(f"SCOUT falhou: {scout_result.error or 'sem resultados'}")
            pipeline.fim = datetime.utcnow()
            pipeline.duracao_total_ms = self._calc_duracao(pipeline)
            return pipeline

        oportunidades = scout_result.data
        pipeline.total_oportunidades = len(oportunidades)

        # Selecionar oportunidade
        idx = min(oportunidade_index, len(oportunidades) - 1)
        oportunidade = oportunidades[idx]
        pipeline.oportunidade_selecionada = oportunidade

        self.logger.info(
            f"Pipeline [{pipeline.pipeline_id}]: SCOUT encontrou {len(oportunidades)} oportunidades, "
            f"selecionada #{idx}: {oportunidade.get('objeto', '')[:60]}..."
        )

        # ── STEP 2: ANALYST ──
        # Para o ANALYST, precisamos do texto do edital.
        # Em um cenario real, baixariamos o edital do PNCP.
        # Aqui usamos o objeto como texto para demonstracao.
        edital_text = oportunidade.get("objeto", "")
        if oportunidade.get("objeto_resumido"):
            edital_text += f"\n\nResumo: {oportunidade['objeto_resumido']}"

        analyst_result = await self.analyst.run(
            edital_text=edital_text,
            numero_edital=oportunidade.get("numero_compra", ""),
            orgao=oportunidade.get("orgao_nome", ""),
            uf=oportunidade.get("orgao_uf", "AM"),
        )
        step = self._build_step_result(PipelineStep.ANALYST, analyst_result)
        pipeline.steps_executados.append(step)

        if not analyst_result.success:
            pipeline.status_geral = "partial"
            pipeline.erros.append(f"ANALYST falhou: {analyst_result.error}")
            pipeline.fim = datetime.utcnow()
            pipeline.duracao_total_ms = self._calc_duracao(pipeline)
            return pipeline

        pipeline.analise = analyst_result.data

        # ── STEP 3: ASSESSOR ──
        assessor_result = await self.assessor.run(analysis=analyst_result.data)
        step = self._build_step_result(PipelineStep.ASSESSOR, assessor_result)
        pipeline.steps_executados.append(step)

        if assessor_result.success and assessor_result.data:
            pipeline.avaliacao = assessor_result.data
            pipeline.recomendacao_final = assessor_result.data.get("recomendacao")
            pipeline.score_final = assessor_result.data.get("score")

            # Se NO_GO, nao continuar com PRICER/COMPILER
            if assessor_result.data.get("recomendacao") == "NO_GO":
                self.logger.info(
                    f"Pipeline [{pipeline.pipeline_id}]: ASSESSOR recomendou NO_GO - pulando PRICER e COMPILER"
                )
                pipeline.steps_executados.append(
                    StepResult(
                        step=PipelineStep.PRICER,
                        status="skipped",
                    )
                )
                if gerar_documentos:
                    pipeline.steps_executados.append(
                        StepResult(
                            step=PipelineStep.COMPILER,
                            status="skipped",
                        )
                    )
                # Pular para SENTINEL se configurado
                if verificar_certidoes:
                    await self._run_sentinel(pipeline)
                pipeline.status_geral = "completed"
                pipeline.fim = datetime.utcnow()
                pipeline.duracao_total_ms = self._calc_duracao(pipeline)
                return pipeline
        else:
            pipeline.erros.append(f"ASSESSOR falhou: {assessor_result.error}")

        # ── STEP 4: PRICER ──
        pricer_result = await self.pricer.run(analysis=analyst_result.data)
        step = self._build_step_result(PipelineStep.PRICER, pricer_result)
        pipeline.steps_executados.append(step)

        if pricer_result.success:
            pipeline.precificacao = pricer_result.data
        else:
            pipeline.erros.append(f"PRICER falhou: {pricer_result.error}")

        # ── STEP 5: COMPILER ──
        if gerar_documentos and pricer_result.success:
            compiler_input = CompilerInput(
                numero_edital=oportunidade.get("numero_compra", ""),
                orgao=oportunidade.get("orgao_nome", ""),
                orgao_cnpj=oportunidade.get("orgao_cnpj", ""),
                objeto=oportunidade.get("objeto", ""),
                modalidade=oportunidade.get("modalidade", ""),
            )

            compiler_result = await self.compiler.run(
                compiler_input=compiler_input,
                pricing_data=pricer_result.data,
                analysis=analyst_result.data,
            )
            step = self._build_step_result(PipelineStep.COMPILER, compiler_result)
            pipeline.steps_executados.append(step)

            if compiler_result.success:
                pipeline.documentos = compiler_result.data
            else:
                pipeline.erros.append(f"COMPILER falhou: {compiler_result.error}")
        elif gerar_documentos:
            pipeline.steps_executados.append(
                StepResult(
                    step=PipelineStep.COMPILER,
                    status="skipped",
                    error="PRICER falhou - sem dados para gerar documentos",
                )
            )

        # ── STEP 6: SENTINEL ──
        if verificar_certidoes:
            await self._run_sentinel(pipeline)

        # Resultado final
        falhas = [s for s in pipeline.steps_executados if s.status == "failed"]
        if falhas:
            pipeline.status_geral = (
                "partial" if any(s.status == "success" for s in pipeline.steps_executados) else "failed"
            )
        else:
            pipeline.status_geral = "completed"

        pipeline.fim = datetime.utcnow()
        pipeline.duracao_total_ms = self._calc_duracao(pipeline)

        self.logger.info(
            f"Pipeline [{pipeline.pipeline_id}]: {pipeline.status_geral} em "
            f"{pipeline.duracao_total_ms:.0f}ms | "
            f"{len(pipeline.steps_executados)} etapas | "
            f"{len(pipeline.erros)} erros"
        )

        return pipeline

    async def run_analysis_only(
        self,
        edital_text: str,
        numero_edital: str = "",
        orgao: str = "",
        uf: str = "AM",
    ) -> PipelineResult:
        """
        Executa apenas ANALYST + ASSESSOR.

        Util para avaliar um edital especifico ja conhecido.
        """
        import uuid

        pipeline = PipelineResult(
            pipeline_id=str(uuid.uuid4())[:8],
            inicio=datetime.utcnow(),
            status_geral="running",
        )

        # ANALYST
        analyst_result = await self.analyst.run(
            edital_text=edital_text,
            numero_edital=numero_edital,
            orgao=orgao,
            uf=uf,
        )
        pipeline.steps_executados.append(self._build_step_result(PipelineStep.ANALYST, analyst_result))

        if not analyst_result.success:
            pipeline.status_geral = "failed"
            pipeline.erros.append(f"ANALYST falhou: {analyst_result.error}")
            pipeline.fim = datetime.utcnow()
            pipeline.duracao_total_ms = self._calc_duracao(pipeline)
            return pipeline

        pipeline.analise = analyst_result.data

        # ASSESSOR
        assessor_result = await self.assessor.run(analysis=analyst_result.data)
        pipeline.steps_executados.append(self._build_step_result(PipelineStep.ASSESSOR, assessor_result))

        if assessor_result.success:
            pipeline.avaliacao = assessor_result.data
            pipeline.recomendacao_final = assessor_result.data.get("recomendacao")
            pipeline.score_final = assessor_result.data.get("score")

        pipeline.status_geral = "completed"
        pipeline.fim = datetime.utcnow()
        pipeline.duracao_total_ms = self._calc_duracao(pipeline)
        return pipeline

    async def run_pricing_only(
        self,
        analysis: dict | None = None,
        pricing_input: dict | None = None,
    ) -> PipelineResult:
        """
        Executa apenas PRICER (+ COMPILER opcionalmente).

        Util para recalcular precos de uma analise existente.
        """
        import uuid

        pipeline = PipelineResult(
            pipeline_id=str(uuid.uuid4())[:8],
            inicio=datetime.utcnow(),
            status_geral="running",
        )

        pricer_result = await self.pricer.run(
            pricing_input=pricing_input,
            analysis=analysis,
        )
        pipeline.steps_executados.append(self._build_step_result(PipelineStep.PRICER, pricer_result))

        if pricer_result.success:
            pipeline.precificacao = pricer_result.data
            pipeline.status_geral = "completed"
        else:
            pipeline.status_geral = "failed"
            pipeline.erros.append(f"PRICER falhou: {pricer_result.error}")

        pipeline.fim = datetime.utcnow()
        pipeline.duracao_total_ms = self._calc_duracao(pipeline)
        return pipeline

    async def run_sentinel_check(
        self,
        documentos: list[dict] | None = None,
        cnpj: str = "35.710.481/0001-03",
    ) -> PipelineResult:
        """
        Executa apenas SENTINEL para verificacao de certidoes.
        """
        import uuid

        pipeline = PipelineResult(
            pipeline_id=str(uuid.uuid4())[:8],
            inicio=datetime.utcnow(),
            status_geral="running",
        )

        await self._run_sentinel(pipeline, documentos=documentos, cnpj=cnpj)

        pipeline.status_geral = "completed"
        pipeline.fim = datetime.utcnow()
        pipeline.duracao_total_ms = self._calc_duracao(pipeline)
        return pipeline

    # ──────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────

    async def _run_sentinel(
        self,
        pipeline: PipelineResult,
        documentos: list[dict] | None = None,
        cnpj: str = "35.710.481/0001-03",
    ) -> None:
        """Executa o SENTINEL e adiciona ao pipeline."""
        sentinel_result = await self.sentinel.run(
            documentos=documentos,
            cnpj=cnpj,
        )
        pipeline.steps_executados.append(self._build_step_result(PipelineStep.SENTINEL, sentinel_result))
        if sentinel_result.success:
            pipeline.sentinela = sentinel_result.data
        else:
            pipeline.erros.append(f"SENTINEL falhou: {sentinel_result.error}")

    def _build_step_result(self, step: PipelineStep, result: ExecutionResult) -> StepResult:
        """Converte ExecutionResult em StepResult."""
        status_map = {
            ExecutionStatus.SUCCESS: "success",
            ExecutionStatus.FAILED: "failed",
            ExecutionStatus.CANCELLED: "skipped",
        }
        return StepResult(
            step=step,
            status=status_map.get(result.status, "failed"),
            duration_ms=result.duration_ms,
            data=result.data if isinstance(result.data, (dict, list)) else None,
            error=result.error,
        )

    def _calc_duracao(self, pipeline: PipelineResult) -> float:
        """Calcula duracao total do pipeline."""
        if pipeline.inicio and pipeline.fim:
            return (pipeline.fim - pipeline.inicio).total_seconds() * 1000
        return sum(s.duration_ms for s in pipeline.steps_executados)

    def get_agents_info(self) -> list[dict]:
        """Retorna informacoes de todos os agentes."""
        return [
            self.scout.info(),
            self.analyst.info(),
            self.assessor.info(),
            self.pricer.info(),
            self.compiler.info(),
            {"name": "warrior", "description": "Robo de disputa para pregao eletronico", "status": "planned"},
            self.sentinel.info(),
        ]
