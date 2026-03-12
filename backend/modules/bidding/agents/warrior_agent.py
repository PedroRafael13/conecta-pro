"""
WARRIOR Agent - Robo de disputa para pregao eletronico
========================================================
Automacao de lances em portais de pregao eletronico.
Status: DEVELOPMENT - simulacao funcional de disputa implementada.
Integracao com portais reais pendente (requer Playwright + certificado digital).
"""

import logging
import random
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from modules.bidding.agents.base_agent import AgentConfig, AgentStatus, BaseAgent

logger = logging.getLogger(__name__)

# Semente para reprodutibilidade em testes (pode ser None para aleatorio real)
_RANDOM_SEED: int | None = None


def _get_rng(seed: int | None = None) -> random.Random:
    """Retorna um gerador de numeros aleatorios."""
    return random.Random(seed if seed is not None else _RANDOM_SEED)  # noqa: S311


# ──────────────────────────────────────────────
# DTOs
# ──────────────────────────────────────────────


class PortalType(StrEnum):
    """Portais de pregao eletronico suportados."""

    COMPRASNET = "comprasnet"
    COMPRAS_GOV = "compras_gov"
    BLL = "bll"
    LICITANET = "licitanet"
    BOLSA_LICITACOES = "bolsa_licitacoes"
    BANPARA = "banpara"
    AMAZON_COMPRAS = "amazon_compras"  # Portal de compras do Estado do Amazonas


class WarriorStatus(StrEnum):
    """Status do warrior durante disputa."""

    IDLE = "idle"
    CONNECTED = "connected"
    MONITORING = "monitoring"
    BIDDING = "bidding"
    WON = "won"
    LOST = "lost"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class BidStrategy(StrEnum):
    """Estrategia de lances."""

    AGRESSIVO = "agressivo"  # Cobrir com margem minima
    MODERADO = "moderado"  # Cobrir com margem confortavel
    CONSERVADOR = "conservador"  # Cobrir apenas se dentro do preco-teto
    SNIPER = "sniper"  # Esperar ultimos segundos para dar lance


class ResultadoDisputa(StrEnum):
    """Resultado final da disputa."""

    VENCEDOR = "vencedor"
    SEGUNDO_LUGAR = "segundo_lugar"
    DESCLASSIFICADO = "desclassificado"
    DESISTIU = "desistiu"


class LanceRegistrado(BaseModel):
    """Lance registrado durante disputa."""

    numero_lance: int
    valor: Decimal
    momento: datetime
    tipo: str  # nosso, concorrente
    posicao: int | None = None  # Classificacao apos o lance
    coberto_por: Decimal | None = None  # Valor que cobriu nosso lance


class LanceRodada(BaseModel):
    """Lance de uma rodada especifica (para retorno da simulacao)."""

    rodada: int
    valor: Decimal
    posicao: int
    delta: Decimal  # Diferenca em relacao ao lance anterior


class ConcorrenteLanceRodada(BaseModel):
    """Lance de um concorrente em uma rodada."""

    concorrente_id: str
    rodada: int
    valor: Decimal
    posicao: int


class RodadaCompleta(BaseModel):
    """Historico completo de uma rodada."""

    rodada: int
    lances: list[dict[str, Any]] = Field(default_factory=list)
    menor_valor: Decimal
    lider: str  # "warrior" ou "concorrente_N"
    warrior_posicao: int
    warrior_valor: Decimal | None = None
    warrior_acao: str  # "lance", "passo", "aguardando"


class EstrategiaConfig(BaseModel):
    """Configuracao validada de estrategia."""

    estrategia: BidStrategy = BidStrategy.MODERADO
    valor_referencia: Decimal
    piso_minimo: Decimal
    num_rodadas: int = Field(default=10, ge=1, le=100)
    concorrentes: int = Field(default=3, ge=1, le=10)
    margem_seguranca: Decimal = Decimal("0.05")  # 5%

    @field_validator("valor_referencia")
    @classmethod
    def validar_valor_referencia(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("valor_referencia deve ser maior que zero")
        return v

    @field_validator("piso_minimo")
    @classmethod
    def validar_piso_minimo(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("piso_minimo nao pode ser negativo")
        return v


class WarriorConfig(BaseModel):
    """Configuracao do WARRIOR para uma disputa."""

    # Portal
    portal: PortalType = PortalType.COMPRAS_GOV

    # Credenciais (em producao, virao do vault/env)
    portal_usuario: str = ""
    portal_senha: str = ""
    certificado_digital_path: str | None = None

    # Edital
    numero_pregao: str = ""
    numero_item: int = 1

    # Estrategia
    estrategia: BidStrategy = BidStrategy.MODERADO

    # Limites
    preco_teto: Decimal = Decimal("0")  # Maximo que podemos ofertar
    preco_minimo: Decimal = Decimal("0")  # Nosso custo + margem minima
    decremento_padrao: Decimal = Decimal("0.01")  # Valor padrao de decremento
    decremento_percentual: Decimal = Decimal("0.5")  # % de decremento sobre lance atual

    # Tempos
    intervalo_lances_segundos: int = 5
    timeout_disputa_minutos: int = 180
    sniper_ultimos_segundos: int = 10  # Para estrategia sniper

    # Automacao
    max_lances: int = 50  # Limite de lances automaticos
    auto_negociacao: bool = False  # Aceitar negociacao automaticamente


class SimulacaoResponse(BaseModel):
    """Resultado completo da simulacao de pregao."""

    # Lances do warrior
    lances_realizados: list[LanceRodada] = Field(default_factory=list)

    # Lances dos concorrentes por rodada
    concorrentes_lances: list[ConcorrenteLanceRodada] = Field(default_factory=list)

    # Resultado
    resultado: ResultadoDisputa
    valor_final: Decimal | None = None
    posicao_final: int
    economia_percentual: Decimal | None = None

    # Historico completo
    historico_completo: list[RodadaCompleta] = Field(default_factory=list)

    # Metadados
    estrategia_utilizada: str = ""
    valor_referencia: Decimal = Decimal("0")
    piso_minimo: Decimal = Decimal("0")
    total_rodadas: int = 0
    total_concorrentes: int = 0
    log_eventos: list[str] = Field(default_factory=list)

    # Dashboard-ready data
    dashboard: dict[str, Any] = Field(default_factory=dict)


class WarriorResponse(BaseModel):
    """Resultado da participacao em pregao."""

    # Status
    status: WarriorStatus = WarriorStatus.IDLE

    # Resultado
    vencedor: bool = False
    posicao_final: int | None = None
    melhor_lance: Decimal | None = None
    lance_vencedor: Decimal | None = None

    # Historico
    lances: list[LanceRegistrado] = Field(default_factory=list)
    total_lances_nossos: int = 0
    total_lances_concorrentes: int = 0

    # Economias
    diferenca_para_teto: Decimal | None = None  # preco_teto - lance_vencedor
    economia_percentual: Decimal | None = None

    # Logs
    log_eventos: list[str] = Field(default_factory=list)

    # Metadados
    inicio_disputa: datetime | None = None
    fim_disputa: datetime | None = None
    duracao_minutos: float | None = None
    portal: str = ""

    # Simulacao detalhada (quando executado em modo simulacao)
    simulacao: SimulacaoResponse | None = None


# ──────────────────────────────────────────────
# Perfis de concorrentes simulados
# ──────────────────────────────────────────────


class _PerfilConcorrente:
    """Perfil de comportamento de um concorrente simulado."""

    def __init__(
        self,
        nome: str,
        agressividade: float,
        piso_fator: float,
        desistencia_prob: float,
        rng: random.Random,
    ):
        self.nome = nome
        self.agressividade = agressividade  # Fator de decremento (0.01 a 0.05)
        self.piso_fator = piso_fator  # Fator do piso em relacao ao referencia (0.5 a 0.9)
        self.desistencia_prob = desistencia_prob  # Probabilidade de desistir por rodada
        self.rng = rng
        self.ativo = True
        self.ultimo_lance: Decimal | None = None

    def fazer_lance(self, menor_valor_atual: Decimal, valor_referencia: Decimal) -> Decimal | None:
        """Calcula o proximo lance do concorrente."""
        if not self.ativo:
            return None

        # Chance de desistir
        if self.rng.random() < self.desistencia_prob:
            self.ativo = False
            return None

        # Calcular piso deste concorrente
        piso = (valor_referencia * Decimal(str(self.piso_fator))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Calcular decremento aleatorio baseado na agressividade
        variacao = self.rng.uniform(0.5, 1.5)
        decremento_pct = Decimal(str(self.agressividade * variacao))
        decremento = (menor_valor_atual * decremento_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        decremento = max(decremento, Decimal("0.01"))

        novo_lance = menor_valor_atual - decremento

        if novo_lance < piso:
            # Tenta dar lance no piso
            if piso < menor_valor_atual:
                novo_lance = piso
            else:
                self.ativo = False
                return None

        novo_lance = novo_lance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.ultimo_lance = novo_lance
        return novo_lance


def _criar_concorrentes(n: int, rng: random.Random) -> list[_PerfilConcorrente]:
    """Cria N concorrentes com perfis variados."""
    perfis = []
    templates = [
        ("Agressivo", 0.03, 0.55, 0.02),
        ("Moderado", 0.018, 0.65, 0.05),
        ("Conservador", 0.008, 0.78, 0.10),
        ("Barganha", 0.025, 0.60, 0.03),
        ("Cauteloso", 0.010, 0.75, 0.08),
        ("Rapido", 0.035, 0.50, 0.04),
        ("Resistente", 0.012, 0.70, 0.01),
        ("Irregular", 0.022, 0.62, 0.06),
        ("Novato", 0.015, 0.72, 0.12),
        ("Veterano", 0.020, 0.58, 0.02),
    ]
    for i in range(n):
        t = templates[i % len(templates)]
        # Adicionar variacao leve para cada instancia
        agr = t[1] * rng.uniform(0.8, 1.2)
        piso = t[2] * rng.uniform(0.9, 1.1)
        piso = min(piso, 0.95)
        des = t[3] * rng.uniform(0.5, 1.5)
        perfis.append(
            _PerfilConcorrente(
                nome=f"Concorrente_{i + 1}_{t[0]}",
                agressividade=agr,
                piso_fator=piso,
                desistencia_prob=des,
                rng=rng,
            )
        )
    return perfis


# ──────────────────────────────────────────────
# WARRIOR Agent
# ──────────────────────────────────────────────


class WarriorAgent(BaseAgent):
    """
    Agente WARRIOR - Robo de disputa para pregao eletronico.

    Responsabilidades:
    - Conectar ao portal de pregao eletronico
    - Monitorar lances da disputa
    - Calcular e enviar lances automaticos conforme estrategia
    - Registrar historico completo da disputa

    Status: DEVELOPMENT
    - Simulacao funcional de pregao eletronico com multiplos concorrentes
    - 4 estrategias de lance: agressivo, moderado, conservador, sniper
    - Analise de concorrencia e calculo de lance minimo
    - Integracao com portais reais requer automacao web (Playwright/Selenium)
    - Em producao, necessita certificado digital A1 e credenciais do portal
    """

    AGENT_NAME = "warrior"
    AGENT_DESCRIPTION = "Robo de disputa para pregao eletronico"
    AGENT_STATUS = AgentStatus.DEVELOPMENT

    def __init__(self, config: AgentConfig | None = None):
        super().__init__(config or AgentConfig(timeout_seconds=600.0))
        self._status = WarriorStatus.IDLE
        self._lances: list[LanceRegistrado] = []
        self._lance_counter = 0
        self._estrategia_config: EstrategiaConfig | None = None

    # ──────────────────────────────────────────
    # Metodo principal
    # ──────────────────────────────────────────

    async def execute(
        self,
        warrior_config: WarriorConfig | dict | None = None,
        *,
        valor_referencia: float | Decimal | None = None,
        estrategia: str | BidStrategy | None = None,
        piso_minimo: float | Decimal | None = None,
        num_rodadas: int = 10,
        concorrentes: int = 3,
        seed: int | None = None,
        **kwargs,
    ) -> dict:
        """
        Executa simulacao de pregao eletronico.

        Aceita tanto WarriorConfig (legado) quanto parametros diretos de simulacao.
        Em modo DEVELOPMENT, executa simulacao completa com concorrentes virtuais.

        Args:
            warrior_config: Configuracao legada (WarriorConfig).
            valor_referencia: Valor de referencia do edital.
            estrategia: Estrategia de lances ("agressivo", "moderado", "conservador", "sniper").
            piso_minimo: Piso minimo - nunca dar lance abaixo deste valor.
            num_rodadas: Numero de rodadas a simular (default 10).
            concorrentes: Numero de concorrentes simulados (default 3).
            seed: Semente para reproducibilidade (opcional).

        Returns:
            WarriorResponse como dict, incluindo SimulacaoResponse.
        """
        # Resolver configuracao: parametros diretos tem precedencia
        if valor_referencia is not None:
            vr = Decimal(str(valor_referencia))
            pm = Decimal(str(piso_minimo)) if piso_minimo is not None else vr * Decimal("0.70")
            est = BidStrategy(estrategia) if estrategia else BidStrategy.MODERADO

            estrategia_cfg = self.configurar_estrategia(
                estrategia=est,
                valor_referencia=vr,
                piso_minimo=pm,
                num_rodadas=num_rodadas,
                concorrentes=concorrentes,
            )
        elif warrior_config is not None:
            if isinstance(warrior_config, dict):
                warrior_config = WarriorConfig(**warrior_config)
            # Converter WarriorConfig legado para EstrategiaConfig
            vr = warrior_config.preco_teto if warrior_config.preco_teto > 0 else Decimal("100000")
            pm = warrior_config.preco_minimo if warrior_config.preco_minimo > 0 else vr * Decimal("0.70")
            estrategia_cfg = EstrategiaConfig(
                estrategia=warrior_config.estrategia,
                valor_referencia=vr,
                piso_minimo=pm,
                num_rodadas=num_rodadas,
                concorrentes=concorrentes,
            )
        else:
            raise ValueError(
                "Fornecer valor_referencia + estrategia + piso_minimo, ou warrior_config com preco_teto > 0."
            )

        self.logger.info(
            f"WARRIOR: Simulacao (status={self.AGENT_STATUS.value}). "
            f"Ref: R$ {float(estrategia_cfg.valor_referencia):,.2f}, "
            f"Estrategia: {estrategia_cfg.estrategia.value}, "
            f"Piso: R$ {float(estrategia_cfg.piso_minimo):,.2f}, "
            f"Rodadas: {estrategia_cfg.num_rodadas}, "
            f"Concorrentes: {estrategia_cfg.concorrentes}"
        )

        # Executar simulacao
        simulacao = self._executar_simulacao(estrategia_cfg, seed=seed)

        # Construir WarriorResponse
        response = self._build_warrior_response(simulacao, estrategia_cfg)

        return response.model_dump(mode="json")

    # ──────────────────────────────────────────
    # Configuracao de estrategia
    # ──────────────────────────────────────────

    def configurar_estrategia(
        self,
        estrategia: str | BidStrategy = BidStrategy.MODERADO,
        valor_referencia: Decimal | float = Decimal("0"),
        piso_minimo: Decimal | float = Decimal("0"),
        num_rodadas: int = 10,
        concorrentes: int = 3,
        margem_seguranca: float = 0.05,
    ) -> EstrategiaConfig:
        """
        Valida e armazena configuracao de estrategia.

        Args:
            estrategia: Tipo de estrategia.
            valor_referencia: Valor de referencia do edital.
            piso_minimo: Piso minimo (nunca dar lance abaixo).
            num_rodadas: Numero de rodadas.
            concorrentes: Numero de concorrentes.
            margem_seguranca: Margem de seguranca (fator, ex: 0.05 = 5%).

        Returns:
            EstrategiaConfig validada.

        Raises:
            ValueError: Se parametros invalidos.
        """
        if isinstance(estrategia, str):
            estrategia = BidStrategy(estrategia)

        vr = Decimal(str(valor_referencia))
        pm = Decimal(str(piso_minimo))

        if pm >= vr:
            raise ValueError(
                f"piso_minimo (R$ {float(pm):,.2f}) deve ser menor que valor_referencia (R$ {float(vr):,.2f})"
            )

        cfg = EstrategiaConfig(
            estrategia=estrategia,
            valor_referencia=vr,
            piso_minimo=pm,
            num_rodadas=num_rodadas,
            concorrentes=concorrentes,
            margem_seguranca=Decimal(str(margem_seguranca)),
        )
        self._estrategia_config = cfg
        self.logger.info(
            f"Estrategia configurada: {cfg.estrategia.value}, ref={cfg.valor_referencia}, piso={cfg.piso_minimo}"
        )
        return cfg

    # ──────────────────────────────────────────
    # Calculo de lance minimo
    # ──────────────────────────────────────────

    def calcular_lance_minimo(
        self,
        valor_referencia: Decimal | float,
        margem_seguranca: float = 0.05,
    ) -> dict[str, Any]:
        """
        Calcula o piso de lance com base no valor de referencia e margem de seguranca.

        Considera custos tipicos de servico de vigilancia:
        - Mao de obra: ~65% do valor
        - Encargos sociais: ~30% da mao de obra
        - Custos administrativos: ~10%
        - Lucro minimo: margem_seguranca

        Args:
            valor_referencia: Valor de referencia do edital.
            margem_seguranca: Margem de seguranca sobre o custo (ex: 0.05 = 5%).

        Returns:
            Dict com piso calculado e breakdown de custos.
        """
        vr = Decimal(str(valor_referencia))
        ms = Decimal(str(margem_seguranca))

        # Estimativa de custos (baseado em vigilancia patrimonial)
        mao_de_obra = vr * Decimal("0.65")
        encargos = mao_de_obra * Decimal("0.30")
        custos_admin = vr * Decimal("0.10")
        custo_total = mao_de_obra + encargos + custos_admin

        # Piso = custo_total * (1 + margem)
        piso = (custo_total * (Decimal("1") + ms)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Percentual do piso em relacao ao referencia
        piso_pct = ((piso / vr) * Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        return {
            "valor_referencia": float(vr),
            "margem_seguranca": float(ms),
            "custos": {
                "mao_de_obra": float(mao_de_obra.quantize(Decimal("0.01"))),
                "encargos_sociais": float(encargos.quantize(Decimal("0.01"))),
                "custos_administrativos": float(custos_admin.quantize(Decimal("0.01"))),
                "custo_total": float(custo_total.quantize(Decimal("0.01"))),
            },
            "piso_minimo": float(piso),
            "piso_percentual_referencia": float(piso_pct),
            "margem_maxima_desconto": float(((vr - piso) / vr * Decimal("100")).quantize(Decimal("0.1"))),
        }

    # ──────────────────────────────────────────
    # Analise de concorrencia
    # ──────────────────────────────────────────

    def analisar_concorrencia(
        self,
        historico_lances: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Analisa padroes de comportamento dos concorrentes com base no historico de lances.

        Identifica:
        - Velocidade de decremento de cada concorrente
        - Agressividade (media de decremento percentual)
        - Ponto provavel de desistencia
        - Concorrentes mais perigosos

        Args:
            historico_lances: Lista de dicts com {concorrente_id, rodada, valor}.

        Returns:
            Analise detalhada de cada concorrente e recomendacoes.
        """
        if not historico_lances:
            return {
                "total_concorrentes": 0,
                "analise_individual": [],
                "recomendacao": "Sem dados suficientes para analise.",
            }

        # Agrupar por concorrente
        por_concorrente: dict[str, list[dict]] = {}
        for lance in historico_lances:
            cid = lance.get("concorrente_id", "desconhecido")
            if cid not in por_concorrente:
                por_concorrente[cid] = []
            por_concorrente[cid].append(lance)

        analises = []
        for cid, lances in por_concorrente.items():
            lances_sorted = sorted(lances, key=lambda x: x.get("rodada", 0))
            valores = [Decimal(str(lance.get("valor", 0))) for lance in lances_sorted]

            if len(valores) < 2:
                analises.append(
                    {
                        "concorrente_id": cid,
                        "total_lances": len(valores),
                        "agressividade": "indeterminada",
                        "valor_inicial": float(valores[0]) if valores else 0,
                        "valor_final": float(valores[-1]) if valores else 0,
                    }
                )
                continue

            # Calcular decrementos percentuais entre rodadas
            decrementos_pct = []
            for i in range(1, len(valores)):
                if valores[i - 1] > 0:
                    dec = float((valores[i - 1] - valores[i]) / valores[i - 1] * 100)
                    decrementos_pct.append(dec)

            media_dec = sum(decrementos_pct) / len(decrementos_pct) if decrementos_pct else 0
            max_dec = max(decrementos_pct) if decrementos_pct else 0
            min_dec = min(decrementos_pct) if decrementos_pct else 0

            # Classificar agressividade
            if media_dec > 3.0:
                agressividade = "muito_agressivo"
            elif media_dec > 2.0:
                agressividade = "agressivo"
            elif media_dec > 1.0:
                agressividade = "moderado"
            else:
                agressividade = "conservador"

            # Estimar piso provavel (ultimo lance - uma margem)
            piso_estimado = float(valores[-1] * Decimal("0.95"))

            # Tendencia: esta desacelerando?
            if len(decrementos_pct) >= 3:
                primeira_metade = decrementos_pct[: len(decrementos_pct) // 2]
                segunda_metade = decrementos_pct[len(decrementos_pct) // 2 :]
                media_1 = sum(primeira_metade) / len(primeira_metade)
                media_2 = sum(segunda_metade) / len(segunda_metade)
                if media_2 < media_1 * 0.7:
                    tendencia = "desacelerando"
                elif media_2 > media_1 * 1.3:
                    tendencia = "acelerando"
                else:
                    tendencia = "estavel"
            else:
                tendencia = "dados_insuficientes"

            analises.append(
                {
                    "concorrente_id": cid,
                    "total_lances": len(valores),
                    "valor_inicial": float(valores[0]),
                    "valor_final": float(valores[-1]),
                    "reducao_total_pct": float(((valores[0] - valores[-1]) / valores[0] * 100).quantize(Decimal("0.1")))
                    if valores[0] > 0
                    else 0,
                    "agressividade": agressividade,
                    "media_decremento_pct": round(media_dec, 2),
                    "max_decremento_pct": round(max_dec, 2),
                    "min_decremento_pct": round(min_dec, 2),
                    "tendencia": tendencia,
                    "piso_estimado": round(piso_estimado, 2),
                }
            )

        # Ordenar por agressividade (mais perigoso primeiro)
        ordem_agr = {"muito_agressivo": 0, "agressivo": 1, "moderado": 2, "conservador": 3, "indeterminada": 4}
        analises.sort(key=lambda x: ordem_agr.get(x["agressividade"], 5))

        # Recomendacao
        mais_perigoso = analises[0] if analises else None
        if mais_perigoso and mais_perigoso["agressividade"] in ("muito_agressivo", "agressivo"):
            recomendacao = (
                f"Concorrente {mais_perigoso['concorrente_id']} e o mais agressivo "
                f"(media {mais_perigoso.get('media_decremento_pct', 0):.1f}%/rodada). "
                f"Considerar estrategia 'sniper' para evitar guerra de precos."
            )
        else:
            recomendacao = (
                "Concorrencia moderada. Estrategia 'moderado' ou 'agressivo' deve ser suficiente para vencer."
            )

        return {
            "total_concorrentes": len(por_concorrente),
            "analise_individual": analises,
            "recomendacao": recomendacao,
        }

    # ──────────────────────────────────────────
    # Motor de simulacao
    # ──────────────────────────────────────────

    def _executar_simulacao(
        self,
        cfg: EstrategiaConfig,
        seed: int | None = None,
    ) -> SimulacaoResponse:
        """
        Motor de simulacao de pregao eletronico.

        Simula um pregao completo com N concorrentes e aplica a estrategia
        configurada para o warrior, retornando resultado detalhado.
        """
        rng = _get_rng(seed)
        vr = cfg.valor_referencia
        piso = cfg.piso_minimo
        est = cfg.estrategia

        log: list[str] = [
            f"[SIMULACAO] Pregao eletronico - {cfg.num_rodadas} rodadas",
            f"[SIMULACAO] Valor referencia: R$ {float(vr):,.2f}",
            f"[SIMULACAO] Piso minimo: R$ {float(piso):,.2f}",
            f"[SIMULACAO] Estrategia: {est.value}",
            f"[SIMULACAO] Concorrentes: {cfg.concorrentes}",
        ]

        # Criar concorrentes
        concorrentes = _criar_concorrentes(cfg.concorrentes, rng)

        # Estado
        lances_warrior: list[LanceRodada] = []
        lances_concorrentes: list[ConcorrenteLanceRodada] = []
        historico: list[RodadaCompleta] = []

        # Valor inicial do warrior depende da estrategia
        warrior_valor: Decimal | None = None
        warrior_ultimo_lance: Decimal | None = None
        menor_global = vr  # Inicia no valor de referencia
        warrior_desistiu = False

        # Lance inicial de cada participante (rodada 0: proposta inicial)
        # Warrior faz proposta inicial
        proposta_warrior = self._proposta_inicial(vr, est)
        if proposta_warrior < piso:
            proposta_warrior = piso

        # Concorrentes fazem propostas iniciais (em torno do valor de referencia)
        propostas_iniciais: dict[str, Decimal] = {"warrior": proposta_warrior}
        for c in concorrentes:
            fator = Decimal(str(rng.uniform(0.92, 1.02)))
            prop = (vr * fator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            propostas_iniciais[c.nome] = prop
            c.ultimo_lance = prop

        # Ordenar por menor proposta
        ranking_inicial = sorted(propostas_iniciais.items(), key=lambda x: x[1])
        menor_global = ranking_inicial[0][1]
        warrior_valor = proposta_warrior
        warrior_ultimo_lance = proposta_warrior

        # Registrar rodada 0 (propostas)
        rodada_0_lances = [
            {"participante": nome, "valor": float(val), "tipo": "proposta"} for nome, val in ranking_inicial
        ]
        pos_warrior_0 = next(i + 1 for i, (nome, _) in enumerate(ranking_inicial) if nome == "warrior")
        historico.append(
            RodadaCompleta(
                rodada=0,
                lances=rodada_0_lances,
                menor_valor=menor_global,
                lider=ranking_inicial[0][0],
                warrior_posicao=pos_warrior_0,
                warrior_valor=warrior_valor,
                warrior_acao="proposta",
            )
        )
        lances_warrior.append(
            LanceRodada(
                rodada=0,
                valor=proposta_warrior,
                posicao=pos_warrior_0,
                delta=vr - proposta_warrior,
            )
        )
        for nome, val in propostas_iniciais.items():
            if nome != "warrior":
                lances_concorrentes.append(
                    ConcorrenteLanceRodada(
                        concorrente_id=nome,
                        rodada=0,
                        valor=val,
                        posicao=next(i + 1 for i, (n, _) in enumerate(ranking_inicial) if n == nome),
                    )
                )

        log.append(
            f"[R0] Propostas iniciais. Warrior: R$ {float(proposta_warrior):,.2f} (pos {pos_warrior_0}). "
            f"Menor: R$ {float(menor_global):,.2f} ({ranking_inicial[0][0]})"
        )

        # Rodadas de disputa
        for rodada in range(1, cfg.num_rodadas + 1):
            lances_rodada: list[dict[str, Any]] = []
            algum_lance = False

            # Concorrentes fazem lances
            for c in concorrentes:
                lance_c = c.fazer_lance(menor_global, vr)
                if lance_c is not None and lance_c < menor_global:
                    lances_rodada.append(
                        {
                            "participante": c.nome,
                            "valor": float(lance_c),
                            "tipo": "lance",
                        }
                    )
                    lances_concorrentes.append(
                        ConcorrenteLanceRodada(
                            concorrente_id=c.nome,
                            rodada=rodada,
                            valor=lance_c,
                            posicao=0,  # Sera atualizado
                        )
                    )
                    if lance_c < menor_global:
                        menor_global = lance_c
                    algum_lance = True
                elif lance_c is None and not c.ativo:
                    log.append(f"[R{rodada}] {c.nome} desistiu da disputa")

            # Warrior faz lance
            warrior_acao = "passo"
            lance_w = self._calcular_lance_simulacao(
                menor_global, vr, piso, est, rodada, cfg.num_rodadas, warrior_ultimo_lance, rng
            )

            if lance_w is not None and lance_w < menor_global:
                warrior_valor = lance_w
                warrior_ultimo_lance = lance_w
                lances_rodada.append(
                    {
                        "participante": "warrior",
                        "valor": float(lance_w),
                        "tipo": "lance",
                    }
                )
                if lance_w < menor_global:
                    menor_global = lance_w
                algum_lance = True
                warrior_acao = "lance"
            elif lance_w is None and menor_global <= piso:
                warrior_acao = "piso_atingido"
                if not warrior_desistiu:
                    log.append(f"[R{rodada}] Warrior: piso minimo atingido, sem mais lances")
                    warrior_desistiu = True
            elif est == BidStrategy.SNIPER and rodada < cfg.num_rodadas - 2:
                warrior_acao = "aguardando"  # Sniper espera

            # Calcular ranking da rodada
            todos_lances_atuais: dict[str, Decimal] = {}
            if warrior_valor is not None:
                todos_lances_atuais["warrior"] = warrior_valor
            for c in concorrentes:
                if c.ultimo_lance is not None:
                    todos_lances_atuais[c.nome] = c.ultimo_lance

            ranking = sorted(todos_lances_atuais.items(), key=lambda x: x[1])
            pos_warrior = next(
                (i + 1 for i, (nome, _) in enumerate(ranking) if nome == "warrior"),
                len(ranking) + 1,
            )

            # Atualizar posicoes nos lances_concorrentes desta rodada
            for lc in lances_concorrentes:
                if lc.rodada == rodada:
                    lc.posicao = next(
                        (i + 1 for i, (n, _) in enumerate(ranking) if n == lc.concorrente_id),
                        0,
                    )

            if warrior_acao == "lance":
                lances_warrior.append(
                    LanceRodada(
                        rodada=rodada,
                        valor=warrior_valor,  # type: ignore
                        posicao=pos_warrior,
                        delta=(warrior_ultimo_lance or vr) - warrior_valor  # type: ignore
                        if warrior_valor
                        else Decimal("0"),
                    )
                )

            historico.append(
                RodadaCompleta(
                    rodada=rodada,
                    lances=lances_rodada,
                    menor_valor=menor_global,
                    lider=ranking[0][0] if ranking else "nenhum",
                    warrior_posicao=pos_warrior,
                    warrior_valor=warrior_valor,
                    warrior_acao=warrior_acao,
                )
            )

            # Log resumido
            concorrentes_ativos = sum(1 for c in concorrentes if c.ativo)
            log.append(
                f"[R{rodada}] Menor: R$ {float(menor_global):,.2f} | "
                f"Warrior pos {pos_warrior} (R$ {float(warrior_valor) if warrior_valor else 0:,.2f}) | "
                f"Acao: {warrior_acao} | "
                f"Conc. ativos: {concorrentes_ativos}"
            )

            # Condicoes de parada
            if concorrentes_ativos == 0:
                log.append(f"[R{rodada}] Todos os concorrentes desistiram")
                break
            if not algum_lance:
                log.append(f"[R{rodada}] Nenhum lance nesta rodada - disputa encerrada")
                break

        # Determinar resultado
        ranking_final = sorted(
            todos_lances_atuais.items(),
            key=lambda x: x[1],
        )
        pos_final = next(
            (i + 1 for i, (n, _) in enumerate(ranking_final) if n == "warrior"),
            len(ranking_final) + 1,
        )

        if pos_final == 1:
            resultado = ResultadoDisputa.VENCEDOR
        elif pos_final == 2:
            resultado = ResultadoDisputa.SEGUNDO_LUGAR
        elif warrior_desistiu:
            resultado = ResultadoDisputa.DESISTIU
        else:
            resultado = ResultadoDisputa.DESCLASSIFICADO

        # Economia
        economia_pct = None
        if warrior_valor and vr > 0:
            economia_pct = ((vr - warrior_valor) / vr * Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        log.append(
            f"[FIM] Resultado: {resultado.value} | Posicao: {pos_final} | "
            f"Valor final: R$ {float(warrior_valor) if warrior_valor else 0:,.2f} | "
            f"Economia: {economia_pct}%"
        )

        # Dashboard-ready data
        dashboard = self._build_dashboard_data(
            lances_warrior=lances_warrior,
            lances_concorrentes=lances_concorrentes,
            historico=historico,
            vr=vr,
            resultado=resultado,
            pos_final=pos_final,
            warrior_valor=warrior_valor,
            economia_pct=economia_pct,
            cfg=cfg,
        )

        return SimulacaoResponse(
            lances_realizados=lances_warrior,
            concorrentes_lances=lances_concorrentes,
            resultado=resultado,
            valor_final=warrior_valor,
            posicao_final=pos_final,
            economia_percentual=economia_pct,
            historico_completo=historico,
            estrategia_utilizada=est.value,
            valor_referencia=vr,
            piso_minimo=piso,
            total_rodadas=len(historico) - 1,  # Exclui rodada 0
            total_concorrentes=cfg.concorrentes,
            log_eventos=log,
            dashboard=dashboard,
        )

    def _proposta_inicial(self, vr: Decimal, estrategia: BidStrategy) -> Decimal:
        """Calcula proposta inicial baseada na estrategia."""
        d = Decimal
        if estrategia == BidStrategy.AGRESSIVO:
            fator = d("0.95")  # 5% abaixo
        elif estrategia == BidStrategy.MODERADO:
            fator = d("1.00")  # No valor de referencia
        elif estrategia == BidStrategy.CONSERVADOR:
            fator = d("1.02")  # 2% acima
        elif estrategia == BidStrategy.SNIPER:
            fator = d("0.98")  # 2% abaixo (discreto)
        else:
            fator = d("1.00")

        return (vr * fator).quantize(d("0.01"), rounding=ROUND_HALF_UP)

    def _calcular_lance_simulacao(
        self,
        menor_atual: Decimal,
        valor_ref: Decimal,
        piso: Decimal,
        estrategia: BidStrategy,
        rodada: int,
        total_rodadas: int,
        ultimo_lance: Decimal | None,
        rng: random.Random,
    ) -> Decimal | None:
        """
        Calcula o proximo lance do warrior na simulacao.

        Aplica logica diferenciada por estrategia.
        """
        d = Decimal

        # Nunca abaixo do piso
        if menor_atual <= piso:
            return None

        if estrategia == BidStrategy.AGRESSIVO:
            # Decremento de 2-3% por rodada
            pct = d(str(rng.uniform(0.02, 0.03)))
            decremento = (menor_atual * pct).quantize(d("0.01"), rounding=ROUND_HALF_UP)
            lance = menor_atual - max(decremento, d("0.01"))

        elif estrategia == BidStrategy.MODERADO:
            # Decremento de 1-2% por rodada
            pct = d(str(rng.uniform(0.01, 0.02)))
            decremento = (menor_atual * pct).quantize(d("0.01"), rounding=ROUND_HALF_UP)
            lance = menor_atual - max(decremento, d("0.01"))

        elif estrategia == BidStrategy.CONSERVADOR:
            # Decremento de 0.5-1% por rodada, com margem de seguranca
            pct = d(str(rng.uniform(0.005, 0.01)))
            decremento = (menor_atual * pct).quantize(d("0.01"), rounding=ROUND_HALF_UP)
            lance = menor_atual - max(decremento, d("0.01"))
            # Conservador nao vai abaixo de 5% acima do piso
            margem = piso * d("1.05")
            if lance < margem:
                return None

        elif estrategia == BidStrategy.SNIPER:
            # Espera ate as ultimas rodadas, depois ataca agressivamente
            rodadas_restantes = total_rodadas - rodada
            if rodadas_restantes > 2:
                # Aguarda - nao faz lance
                return None
            # Nas ultimas 2 rodadas: lance agressivo
            pct = d(str(rng.uniform(0.02, 0.04)))
            decremento = (menor_atual * pct).quantize(d("0.01"), rounding=ROUND_HALF_UP)
            lance = menor_atual - max(decremento, d("0.01"))

        else:
            lance = menor_atual - d("0.01")

        lance = lance.quantize(d("0.01"), rounding=ROUND_HALF_UP)

        # Respeitar piso
        if lance < piso:
            # Tenta dar lance no piso se ainda for menor que o atual
            if piso < menor_atual:
                lance = piso
            else:
                return None

        # Se o lance nao eh menor que o menor atual, nao adianta
        if lance >= menor_atual:
            return None

        return lance

    def _build_dashboard_data(
        self,
        lances_warrior: list[LanceRodada],
        lances_concorrentes: list[ConcorrenteLanceRodada],
        historico: list[RodadaCompleta],
        vr: Decimal,
        resultado: ResultadoDisputa,
        pos_final: int,
        warrior_valor: Decimal | None,
        economia_pct: Decimal | None,
        cfg: EstrategiaConfig,
    ) -> dict[str, Any]:
        """Constroi dados estruturados para exibicao em dashboard frontend."""
        # Series temporais para graficos
        serie_warrior = [{"rodada": lance.rodada, "valor": float(lance.valor)} for lance in lances_warrior]

        # Agrupar concorrentes por ID para series
        conc_series: dict[str, list[dict]] = {}
        for lc in lances_concorrentes:
            if lc.concorrente_id not in conc_series:
                conc_series[lc.concorrente_id] = []
            conc_series[lc.concorrente_id].append(
                {
                    "rodada": lc.rodada,
                    "valor": float(lc.valor),
                }
            )

        # Menor valor por rodada (para area chart)
        menor_por_rodada = [{"rodada": r.rodada, "valor": float(r.menor_valor)} for r in historico]

        # Posicao do warrior por rodada
        posicao_por_rodada = [
            {"rodada": r.rodada, "posicao": r.warrior_posicao, "acao": r.warrior_acao} for r in historico
        ]

        # Resumo de status
        status_color = {
            ResultadoDisputa.VENCEDOR: "green",
            ResultadoDisputa.SEGUNDO_LUGAR: "yellow",
            ResultadoDisputa.DESCLASSIFICADO: "red",
            ResultadoDisputa.DESISTIU: "orange",
        }

        return {
            "resumo": {
                "resultado": resultado.value,
                "resultado_cor": status_color.get(resultado, "gray"),
                "posicao_final": pos_final,
                "valor_referencia": float(vr),
                "valor_final": float(warrior_valor) if warrior_valor else None,
                "economia_percentual": float(economia_pct) if economia_pct else 0,
                "estrategia": cfg.estrategia.value,
                "total_rodadas": len(historico) - 1,
                "total_lances_warrior": len(lances_warrior),
                "total_concorrentes": cfg.concorrentes,
            },
            "series": {
                "warrior": serie_warrior,
                "concorrentes": conc_series,
                "menor_valor": menor_por_rodada,
                "posicao_warrior": posicao_por_rodada,
            },
            "limites": {
                "valor_referencia": float(vr),
                "piso_minimo": float(cfg.piso_minimo),
            },
        }

    def _build_warrior_response(
        self,
        simulacao: SimulacaoResponse,
        cfg: EstrategiaConfig,
    ) -> WarriorResponse:
        """Converte SimulacaoResponse em WarriorResponse (compatibilidade)."""
        # Converter lances para formato legado
        lances_legado: list[LanceRegistrado] = []
        lance_num = 0

        for rodada_data in simulacao.historico_completo:
            for lance_info in rodada_data.lances:
                lance_num += 1
                lances_legado.append(
                    LanceRegistrado(
                        numero_lance=lance_num,
                        valor=Decimal(str(lance_info["valor"])),
                        momento=datetime.utcnow(),
                        tipo="nosso" if lance_info["participante"] == "warrior" else "concorrente",
                        posicao=rodada_data.warrior_posicao if lance_info["participante"] == "warrior" else None,
                    )
                )

        eh_vencedor = simulacao.resultado == ResultadoDisputa.VENCEDOR
        status = WarriorStatus.WON if eh_vencedor else WarriorStatus.LOST

        diferenca_teto = None
        if eh_vencedor and simulacao.valor_final:
            diferenca_teto = cfg.valor_referencia - simulacao.valor_final

        nossos = sum(1 for lance in lances_legado if lance.tipo == "nosso")
        concorrentes_total = sum(1 for lance in lances_legado if lance.tipo == "concorrente")

        return WarriorResponse(
            status=status,
            vencedor=eh_vencedor,
            posicao_final=simulacao.posicao_final,
            melhor_lance=simulacao.valor_final,
            lance_vencedor=simulacao.valor_final if eh_vencedor else None,
            lances=lances_legado,
            total_lances_nossos=nossos,
            total_lances_concorrentes=concorrentes_total,
            diferenca_para_teto=diferenca_teto,
            economia_percentual=simulacao.economia_percentual,
            log_eventos=simulacao.log_eventos,
            inicio_disputa=datetime.utcnow(),
            fim_disputa=datetime.utcnow(),
            duracao_minutos=0.0,
            portal="simulacao",
            simulacao=simulacao,
        )

    # ──────────────────────────────────────────
    # Stubs para integracao futura com portais
    # ──────────────────────────────────────────

    async def _conectar_portal(self, config: WarriorConfig) -> bool:
        """
        [STUB] Conecta ao portal de pregao eletronico.

        Implementacao futura com Playwright/Selenium:
        - ComprasNet/Compras.gov.br: login com certificado digital A1
        - BLL: login com usuario/senha + 2FA
        - LicitaNet: login com certificado
        - Amazon Compras (AM): login com certificado

        Returns:
            True se conectado com sucesso.
        """
        raise NotImplementedError(
            "Integracao com portais reais nao implementada. Use modo simulacao (status=DEVELOPMENT)."
        )

    async def _monitorar_disputa(self, config: WarriorConfig) -> None:
        """
        [STUB] Monitora lances em tempo real no portal.

        Implementacao futura:
        - WebSocket ou polling do portal
        - Captura de lances de concorrentes
        - Deteccao de fase da disputa (aberta, random close, negociacao)
        """
        raise NotImplementedError("Monitoramento de portal nao implementado.")

    async def _enviar_lance_portal(self, valor: Decimal, config: WarriorConfig) -> bool:
        """
        [STUB] Envia lance no portal real.

        Implementacao futura:
        - Preencher campo de valor no portal
        - Confirmar envio
        - Verificar aceitacao do lance
        - Capturar posicao apos lance

        Returns:
            True se lance aceito pelo portal.
        """
        raise NotImplementedError("Envio de lance em portal nao implementado.")

    async def _desconectar_portal(self) -> None:
        """[STUB] Desconecta do portal."""
        raise NotImplementedError("Desconexao de portal nao implementada.")
