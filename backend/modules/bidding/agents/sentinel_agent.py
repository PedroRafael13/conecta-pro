"""
SENTINEL Agent - Monitoramento de certidoes e documentos
==========================================================
Monitora validade de certidoes, documentos e certificados
necessarios para participacao em licitacoes.

Inclui verificacao online (httpx) com fallback offline,
cache Redis (6h) e retry com exponential backoff.
"""

import asyncio
import logging
import re
from datetime import date, datetime, timedelta
from enum import StrEnum

import httpx
from pydantic import BaseModel, Field

from modules.bidding.agents.base_agent import AgentConfig, AgentStatus, BaseAgent

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Constantes de verificacao online
# ──────────────────────────────────────────────

ONLINE_CACHE_TTL = 6 * 60 * 60  # 6 horas em segundos
ONLINE_CACHE_PREFIX = "sentinel:certidao"
ONLINE_REQUEST_TIMEOUT = 30.0
ONLINE_MAX_RETRIES = 3
ONLINE_BACKOFF_BASE = 2.0  # segundos — backoff exponencial: 2, 4, 8

# Headers realistas para evitar bloqueio por User-Agent
_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}


# ──────────────────────────────────────────────
# DTOs
# ──────────────────────────────────────────────


class TipoDocumentoMonitorado(StrEnum):
    """Tipos de documentos monitorados pelo SENTINEL."""

    CND_FEDERAL = "cnd_federal"  # Certidao Negativa Debitos Federais (RFB/PGFN)
    CND_ESTADUAL = "cnd_estadual"  # Certidao Negativa Debitos Estaduais
    CND_MUNICIPAL = "cnd_municipal"  # Certidao Negativa Debitos Municipais (ISS)
    CRF_FGTS = "crf_fgts"  # Certificado Regularidade FGTS (Caixa)
    CNDT_TRABALHISTA = "cndt_trabalhista"  # Certidao Negativa Debitos Trabalhistas (TST)
    SICAF = "sicaf"  # Sistema Cadastramento Unificado Fornecedores
    AUTORIZACAO_PF = "autorizacao_pf"  # Autorizacao Policia Federal (vigilancia)
    ALVARA_FUNCIONAMENTO = "alvara_funcionamento"
    CERTIFICADO_DIGITAL = "certificado_digital"  # e-CNPJ / A1
    ISO_9001 = "iso_9001"
    ISO_14001 = "iso_14001"
    SEGURO_RESPONSABILIDADE = "seguro_responsabilidade"
    REGISTRO_CREA = "registro_crea"
    BALANCO_PATRIMONIAL = "balanco_patrimonial"


class StatusDocumento(StrEnum):
    """Status de um documento monitorado."""

    VALIDO = "valido"
    VENCENDO = "vencendo"  # Proximo do vencimento (dentro do alerta)
    VENCIDO = "vencido"
    NAO_POSSUI = "nao_possui"
    RENOVANDO = "renovando"  # Em processo de renovacao
    ERRO_CONSULTA = "erro_consulta"


class NivelAlerta(StrEnum):
    """Nivel de alerta para documentos."""

    OK = "ok"
    ATENCAO = "atencao"  # Vence em 30-60 dias
    URGENTE = "urgente"  # Vence em 15-30 dias
    CRITICO = "critico"  # Vence em < 15 dias ou ja vencido


class CertificateOnlineResult(BaseModel):
    """Resultado de uma verificacao online de certidao."""

    tipo: TipoDocumentoMonitorado
    cnpj: str
    verificado_online: bool = False
    is_valid: bool | None = None
    expiry_date: date | None = None
    emission_date: date | None = None
    codigo_controle: str | None = None
    url_consultada: str | None = None
    erro: str | None = None
    fonte: str = "offline"  # "online", "cache", "offline"
    raw_snippet: str | None = None  # trecho da resposta para debug


class DocumentoMonitorado(BaseModel):
    """Documento individual monitorado."""

    tipo: TipoDocumentoMonitorado
    nome_exibicao: str
    cnpj_empresa: str = "35.710.481/0001-03"

    # Validade
    data_emissao: date | None = None
    data_validade: date | None = None
    validade_padrao_dias: int = 180  # Validade default se nao informada

    # Status
    status: StatusDocumento = StatusDocumento.NAO_POSSUI
    nivel_alerta: NivelAlerta = NivelAlerta.OK
    dias_para_vencimento: int | None = None

    # Consulta
    url_consulta: str | None = None  # URL para emissao/consulta online
    ultima_consulta: datetime | None = None
    proximo_check: datetime | None = None
    erro_consulta: str | None = None

    # Verificacao online
    verificado_online: bool = False
    fonte_verificacao: str | None = None  # "online", "cache", "offline"

    # Arquivo
    arquivo_path: str | None = None
    arquivo_hash: str | None = None

    # Observacoes
    observacoes: str | None = None


class SentinelResponse(BaseModel):
    """Resultado do monitoramento de documentos."""

    # Resumo
    total_documentos: int = 0
    validos: int = 0
    vencendo: int = 0
    vencidos: int = 0
    nao_possui: int = 0

    # Alertas
    alertas_criticos: list[str] = Field(default_factory=list)
    alertas_urgentes: list[str] = Field(default_factory=list)
    alertas_atencao: list[str] = Field(default_factory=list)

    # Documentos detalhados
    documentos: list[DocumentoMonitorado] = Field(default_factory=list)

    # Aptidao para licitar
    apto_licitar: bool = False
    motivo_inaptidao: list[str] = Field(default_factory=list)

    # Verificacao online
    verificacoes_online: list[CertificateOnlineResult] = Field(default_factory=list)

    # Metadados
    verificado_em: datetime | None = None
    proxima_verificacao: datetime | None = None


# ──────────────────────────────────────────────
# Registro de documentos padrao
# ──────────────────────────────────────────────

DOCUMENTOS_PADRAO: list[dict] = [
    {
        "tipo": TipoDocumentoMonitorado.CND_FEDERAL,
        "nome_exibicao": "CND Federal (RFB/PGFN)",
        "validade_padrao_dias": 180,
        "url_consulta": "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CND_ESTADUAL,
        "nome_exibicao": "CND Estadual (SEFAZ-AM)",
        "validade_padrao_dias": 90,
        "url_consulta": "https://online.sefaz.am.gov.br/certidao",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CND_MUNICIPAL,
        "nome_exibicao": "CND Municipal (ISS Manaus)",
        "validade_padrao_dias": 90,
        "url_consulta": "https://semef.manaus.am.gov.br",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CRF_FGTS,
        "nome_exibicao": "CRF FGTS (Caixa)",
        "validade_padrao_dias": 30,
        "url_consulta": "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CNDT_TRABALHISTA,
        "nome_exibicao": "CNDT Trabalhista (TST)",
        "validade_padrao_dias": 180,
        "url_consulta": "https://www.tst.jus.br/certidao1",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.SICAF,
        "nome_exibicao": "Cadastro SICAF",
        "validade_padrao_dias": 365,
        "url_consulta": "https://www.gov.br/compras/pt-br/acesso-ao-sicaf",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.AUTORIZACAO_PF,
        "nome_exibicao": "Autorizacao Policia Federal (Vigilancia)",
        "validade_padrao_dias": 365,
        "url_consulta": "https://www.gov.br/pf/pt-br/assuntos/seguranca-privada",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.ALVARA_FUNCIONAMENTO,
        "nome_exibicao": "Alvara de Funcionamento",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CERTIFICADO_DIGITAL,
        "nome_exibicao": "Certificado Digital e-CNPJ (A1)",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.SEGURO_RESPONSABILIDADE,
        "nome_exibicao": "Seguro de Responsabilidade Civil",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": False,
    },
    {
        "tipo": TipoDocumentoMonitorado.BALANCO_PATRIMONIAL,
        "nome_exibicao": "Balanco Patrimonial (ultimo exercicio)",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": True,
    },
]


# ──────────────────────────────────────────────
# Helpers: parse de respostas HTML dos portais
# ──────────────────────────────────────────────

_DATE_PATTERNS = [
    # dd/mm/yyyy
    re.compile(r"(\d{2})/(\d{2})/(\d{4})"),
    # yyyy-mm-dd
    re.compile(r"(\d{4})-(\d{2})-(\d{2})"),
]


def _extract_date_from_text(text: str, keyword: str | None = None) -> date | None:
    """
    Tenta extrair uma data de um trecho de texto HTML/plain.
    Se ``keyword`` for fornecido, procura a data mais proxima apos a keyword.
    """
    search_text = text
    if keyword:
        idx = text.lower().find(keyword.lower())
        if idx >= 0:
            search_text = text[idx : idx + 200]

    # Tenta dd/mm/yyyy primeiro (padrao BR)
    m = _DATE_PATTERNS[0].search(search_text)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass

    # Tenta yyyy-mm-dd
    m = _DATE_PATTERNS[1].search(search_text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    return None


def _cnpj_digits(cnpj: str) -> str:
    """Retorna apenas os 14 digitos do CNPJ."""
    return re.sub(r"\D", "", cnpj)


# ──────────────────────────────────────────────
# SENTINEL Agent
# ──────────────────────────────────────────────


class SentinelAgent(BaseAgent):
    """
    Agente SENTINEL - Monitoramento de certidoes e documentos.

    Responsabilidades:
    - Verificar validade de todas as certidoes obrigatorias
    - Alertar sobre documentos vencendo/vencidos
    - Classificar nivel de alerta (OK, atencao, urgente, critico)
    - Determinar aptidao para licitar
    - Agendar verificacoes periodicas
    - Verificacao online de certidoes nos portais dos orgaos emissores
      com cache Redis (6h), retry com backoff e fallback offline
    """

    AGENT_NAME = "sentinel"
    AGENT_DESCRIPTION = "Monitora validade de certidoes e documentos para licitacoes"
    AGENT_STATUS = AgentStatus.DEVELOPMENT

    # Limiares de alerta (dias)
    ALERTA_ATENCAO_DIAS = 60
    ALERTA_URGENTE_DIAS = 30
    ALERTA_CRITICO_DIAS = 15

    # Tipos que possuem verificacao online implementada
    _TIPOS_VERIFICAVEIS_ONLINE = {
        TipoDocumentoMonitorado.CND_FEDERAL,
        TipoDocumentoMonitorado.CNDT_TRABALHISTA,
        TipoDocumentoMonitorado.CRF_FGTS,
        TipoDocumentoMonitorado.CND_ESTADUAL,
        TipoDocumentoMonitorado.CND_MUNICIPAL,
    }

    def __init__(
        self,
        config: AgentConfig | None = None,
        documentos_cadastrados: list[DocumentoMonitorado] | None = None,
    ):
        super().__init__(config)
        self._documentos = documentos_cadastrados or []

    # ──────────────────────────────────────────
    # Metodo principal
    # ──────────────────────────────────────────

    async def execute(
        self,
        documentos: list[dict] | None = None,
        cnpj: str = "35.710.481/0001-03",
        verificar_online: bool = False,
        **kwargs,
    ) -> dict:
        """
        Verifica status de todos os documentos monitorados.

        Args:
            documentos: Lista de documentos com datas de validade (override).
                        Cada dict: {"tipo": str, "data_emissao": str, "data_validade": str}
            cnpj: CNPJ da empresa.
            verificar_online: Se True, consulta APIs dos orgaos emissores online
                              com cache Redis e fallback para tracking offline.

        Returns:
            SentinelResponse como dict.
        """
        hoje = date.today()
        docs_monitorados: list[DocumentoMonitorado] = []

        # Usar documentos passados ou defaults
        if documentos:
            docs_monitorados = self._parse_documentos_input(documentos, cnpj)
        elif self._documentos:
            docs_monitorados = self._documentos
        else:
            docs_monitorados = self._criar_documentos_padrao(cnpj)

        # Atualizar status de cada documento (offline)
        for doc in docs_monitorados:
            self._atualizar_status(doc, hoje)

        # Verificacao online com fallback
        online_results: list[CertificateOnlineResult] = []
        if verificar_online:
            online_results = await self.verificar_online(cnpj)
            self._aplicar_resultados_online(docs_monitorados, online_results, hoje)

        # Construir resposta
        response = self._construir_resposta(docs_monitorados, hoje, online_results)

        self.logger.info(
            f"SENTINEL: {response.total_documentos} docs verificados | "
            f"Validos: {response.validos} | Vencendo: {response.vencendo} | "
            f"Vencidos: {response.vencidos} | Apto: {response.apto_licitar}"
            + (f" | Online: {len(online_results)} verificacoes" if online_results else "")
        )

        return response.model_dump(mode="json")

    # ──────────────────────────────────────────
    # Verificacao online — orquestrador
    # ──────────────────────────────────────────

    async def verificar_online(self, cnpj: str) -> list[CertificateOnlineResult]:
        """
        Executa verificacao online de todas as certidoes verificaveis.

        Para cada tipo com verificador implementado, tenta:
        1. Buscar resultado em cache Redis (TTL 6h)
        2. Se cache miss, faz chamada HTTP com retry + exponential backoff
        3. Se falhar, retorna resultado com fonte="offline" (fallback)

        Args:
            cnpj: CNPJ da empresa (com ou sem formatacao).

        Returns:
            Lista de CertificateOnlineResult, um por tipo verificavel.
        """
        cnpj_limpo = _cnpj_digits(cnpj)
        results: list[CertificateOnlineResult] = []

        # Mapa tipo -> metodo verificador
        verificadores = {
            TipoDocumentoMonitorado.CND_FEDERAL: self._verificar_cnd_federal,
            TipoDocumentoMonitorado.CNDT_TRABALHISTA: self._verificar_cndt_trabalhista,
            TipoDocumentoMonitorado.CRF_FGTS: self._verificar_crf_fgts,
            TipoDocumentoMonitorado.CND_ESTADUAL: self._verificar_cnd_estadual_sefaz_am,
            TipoDocumentoMonitorado.CND_MUNICIPAL: self._verificar_cnd_municipal_iss_manaus,
        }

        # Executar todas as verificacoes em paralelo
        tasks = []
        tipos_ordem = []
        for tipo, verificador in verificadores.items():
            tipos_ordem.append(tipo)
            tasks.append(self._verificar_com_cache_e_retry(tipo, cnpj_limpo, verificador))

        resultados = await asyncio.gather(*tasks, return_exceptions=True)

        for tipo, resultado in zip(tipos_ordem, resultados, strict=False):
            if isinstance(resultado, Exception):
                self.logger.error(f"[SENTINEL] Excecao inesperada ao verificar {tipo.value}: {resultado}")
                results.append(
                    CertificateOnlineResult(
                        tipo=tipo,
                        cnpj=cnpj_limpo,
                        verificado_online=False,
                        erro=str(resultado),
                        fonte="offline",
                    )
                )
            else:
                results.append(resultado)

        return results

    # ──────────────────────────────────────────
    # Cache + retry wrapper
    # ──────────────────────────────────────────

    async def _verificar_com_cache_e_retry(
        self,
        tipo: TipoDocumentoMonitorado,
        cnpj: str,
        verificador,
    ) -> CertificateOnlineResult:
        """
        Wrapper que adiciona cache Redis e retry com backoff a um verificador.

        Fluxo:
        1. Tenta ler do cache Redis
        2. Se miss, chama verificador com ate ONLINE_MAX_RETRIES tentativas
        3. Se sucesso, salva no cache
        4. Se falha total, retorna resultado offline (fallback)
        """
        cache_key = f"{ONLINE_CACHE_PREFIX}:{tipo.value}:{cnpj}"

        # 1. Tentar cache
        cached = await self._cache_get(cache_key)
        if cached is not None:
            self.logger.info(f"[SENTINEL] Cache HIT para {tipo.value} (CNPJ {cnpj[:6]}...)")
            try:
                result = CertificateOnlineResult(**cached)
                result.fonte = "cache"
                return result
            except Exception:
                self.logger.warning(f"[SENTINEL] Cache corrompido para {cache_key}, ignorando")

        # 2. Tentativas com backoff exponencial
        last_error: str | None = None
        for attempt in range(1, ONLINE_MAX_RETRIES + 1):
            try:
                self.logger.info(
                    f"[SENTINEL] Verificacao online {tipo.value} — tentativa {attempt}/{ONLINE_MAX_RETRIES}"
                )
                result = await verificador(cnpj)
                result.fonte = "online"
                result.verificado_online = True

                # Salvar no cache
                await self._cache_set(cache_key, result.model_dump(mode="json"), ONLINE_CACHE_TTL)
                self.logger.info(
                    f"[SENTINEL] Verificacao online {tipo.value} OK — cache salvo (TTL {ONLINE_CACHE_TTL}s)"
                )
                return result

            except (httpx.HTTPError, httpx.TimeoutException, ConnectionError, OSError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                self.logger.warning(f"[SENTINEL] Falha {tipo.value} tentativa {attempt}: {last_error}")
                if attempt < ONLINE_MAX_RETRIES:
                    delay = ONLINE_BACKOFF_BASE**attempt
                    await asyncio.sleep(delay)

            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                self.logger.error(f"[SENTINEL] Erro inesperado {tipo.value}: {last_error}")
                break  # Nao faz retry para erros nao-HTTP

        # 3. Fallback offline
        self.logger.warning(
            f"[SENTINEL] Verificacao online {tipo.value} falhou apos {ONLINE_MAX_RETRIES} tentativas. "
            f"Fallback para tracking offline. Ultimo erro: {last_error}"
        )
        return CertificateOnlineResult(
            tipo=tipo,
            cnpj=cnpj,
            verificado_online=False,
            erro=last_error,
            fonte="offline",
        )

    # ──────────────────────────────────────────
    # Cache helpers (isolados para facilitar mock)
    # ──────────────────────────────────────────

    async def _cache_get(self, key: str):
        """Busca valor no cache Redis. Retorna None se indisponivel."""
        try:
            from core.cache.redis import cache_get

            return await cache_get(key)
        except Exception as exc:
            self.logger.debug(f"[SENTINEL] Redis indisponivel para GET {key}: {exc}")
            return None

    async def _cache_set(self, key: str, value, ttl: int):
        """Salva valor no cache Redis. Silencia erros."""
        try:
            from core.cache.redis import cache_set

            await cache_set(key, value, ttl)
        except Exception as exc:
            self.logger.debug(f"[SENTINEL] Redis indisponivel para SET {key}: {exc}")

    # ──────────────────────────────────────────
    # Verificadores individuais por tipo
    # ──────────────────────────────────────────

    async def _verificar_cnd_federal(self, cnpj: str) -> CertificateOnlineResult:
        """
        Verifica CND Federal (Receita Federal + PGFN).

        URL: https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir
        Envia POST com CNPJ e analisa resposta HTML para status de validade.
        """
        url = "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir"
        result = CertificateOnlineResult(
            tipo=TipoDocumentoMonitorado.CND_FEDERAL,
            cnpj=cnpj,
            url_consultada=url,
        )

        async with httpx.AsyncClient(
            timeout=ONLINE_REQUEST_TIMEOUT,
            headers=_DEFAULT_HEADERS,
            follow_redirects=True,
            verify=True,
        ) as client:
            # Primeiro GET para obter cookies/viewstate
            resp_get = await client.get(url)
            resp_get.raise_for_status()

            # Extrair __VIEWSTATE e __EVENTVALIDATION se presentes (ASP.NET)
            form_data = {"NI": cnpj}
            viewstate = self._extract_aspnet_field(resp_get.text, "__VIEWSTATE")
            if viewstate:
                form_data["__VIEWSTATE"] = viewstate
            event_val = self._extract_aspnet_field(resp_get.text, "__EVENTVALIDATION")
            if event_val:
                form_data["__EVENTVALIDATION"] = event_val
            viewstate_gen = self._extract_aspnet_field(resp_get.text, "__VIEWSTATEGENERATOR")
            if viewstate_gen:
                form_data["__VIEWSTATEGENERATOR"] = viewstate_gen

            # POST com CNPJ
            resp_post = await client.post(url, data=form_data)
            resp_post.raise_for_status()

            body = resp_post.text
            result.raw_snippet = body[:500]

            # Parse: procurar indicadores de certidao valida/negativa
            body_lower = body.lower()

            if "certidão negativa" in body_lower or "certidao negativa" in body_lower:
                result.is_valid = True
            elif "certidão positiva com efeitos de negativa" in body_lower:
                result.is_valid = True  # CPEN tambem eh valida para licitar
            elif "certidão positiva" in body_lower or "certidao positiva" in body_lower:
                result.is_valid = False
            elif "situação regular" in body_lower or "regularidade fiscal" in body_lower:
                result.is_valid = True
            elif "pendências" in body_lower or "debitos" in body_lower:
                result.is_valid = False

            # Extrair datas
            result.emission_date = _extract_date_from_text(body, "emiss")
            result.expiry_date = _extract_date_from_text(body, "valid")

            # Codigo de controle
            ctrl_match = re.search(r"(?:código|codigo)\s*(?:de\s*)?controle[:\s]*([A-Z0-9\.\-]+)", body, re.IGNORECASE)
            if ctrl_match:
                result.codigo_controle = ctrl_match.group(1).strip()

        return result

    async def _verificar_cndt_trabalhista(self, cnpj: str) -> CertificateOnlineResult:
        """
        Verifica CNDT Trabalhista (TST).

        URL: https://www.tst.jus.br/certidao1/servlet/ControleAcesso
        Envia POST com CNPJ e analisa resposta para status.
        """
        url = "https://www.tst.jus.br/certidao1/servlet/ControleAcesso"
        result = CertificateOnlineResult(
            tipo=TipoDocumentoMonitorado.CNDT_TRABALHISTA,
            cnpj=cnpj,
            url_consultada=url,
        )

        async with httpx.AsyncClient(
            timeout=ONLINE_REQUEST_TIMEOUT,
            headers=_DEFAULT_HEADERS,
            follow_redirects=True,
            verify=True,
        ) as client:
            form_data = {
                "tipoCertidao": "2",  # PJ
                "numeroDocumento": cnpj,
            }

            resp = await client.post(url, data=form_data)
            resp.raise_for_status()

            body = resp.text
            result.raw_snippet = body[:500]
            body_lower = body.lower()

            # CNDT = Certidao Negativa de Debitos Trabalhistas
            if "certidão negativa" in body_lower or "certidao negativa" in body_lower or "nada consta" in body_lower:
                result.is_valid = True
            elif (
                "certidão positiva" in body_lower
                or "certidao positiva" in body_lower
                or "existência de débitos" in body_lower
                or "debitos trabalhistas" in body_lower
            ):
                result.is_valid = False

            result.emission_date = _extract_date_from_text(body, "emiss")
            result.expiry_date = _extract_date_from_text(body, "valid")

            # Codigo de controle do TST
            ctrl_match = re.search(r"certidão\s+n[°º]?\s*[:\s]*(\d+)", body, re.IGNORECASE)
            if ctrl_match:
                result.codigo_controle = ctrl_match.group(1).strip()

        return result

    async def _verificar_crf_fgts(self, cnpj: str) -> CertificateOnlineResult:
        """
        Verifica CRF FGTS (Caixa Economica Federal).

        URL: https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf
        Portal JSF — envia POST com CNPJ.
        """
        url = "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"
        result = CertificateOnlineResult(
            tipo=TipoDocumentoMonitorado.CRF_FGTS,
            cnpj=cnpj,
            url_consultada=url,
        )

        async with httpx.AsyncClient(
            timeout=ONLINE_REQUEST_TIMEOUT,
            headers=_DEFAULT_HEADERS,
            follow_redirects=True,
            verify=True,
        ) as client:
            # GET inicial para obter javax.faces.ViewState
            resp_get = await client.get(url)
            resp_get.raise_for_status()

            # Extrair ViewState (JSF)
            viewstate = self._extract_jsf_viewstate(resp_get.text)

            form_data = {
                "consultaEmpregadorForm": "consultaEmpregadorForm",
                "consultaEmpregadorForm:cnpj": cnpj,
                "consultaEmpregadorForm:consultar": "Consultar",
                "javax.faces.ViewState": viewstate or "",
            }

            resp_post = await client.post(url, data=form_data)
            resp_post.raise_for_status()

            body = resp_post.text
            result.raw_snippet = body[:500]
            body_lower = body.lower()

            if (
                "certificado de regularidade" in body_lower
                or "situação regular" in body_lower
                or "regular perante o fgts" in body_lower
            ):
                result.is_valid = True
            elif "não regular" in body_lower or "irregular" in body_lower:
                result.is_valid = False
            elif "não foi possível" in body_lower:
                result.is_valid = None  # Indeterminado
                result.erro = "Portal retornou resposta indeterminada"

            result.emission_date = _extract_date_from_text(body, "emiss")
            result.expiry_date = _extract_date_from_text(body, "valid")

        return result

    async def _verificar_cnd_estadual_sefaz_am(self, cnpj: str) -> CertificateOnlineResult:
        """
        Verifica CND Estadual (SEFAZ-AM — Secretaria da Fazenda do Amazonas).

        URL: https://online.sefaz.am.gov.br/
        Especifico para o estado do Amazonas.
        """
        url = "https://online.sefaz.am.gov.br/certidao"
        result = CertificateOnlineResult(
            tipo=TipoDocumentoMonitorado.CND_ESTADUAL,
            cnpj=cnpj,
            url_consultada=url,
        )

        async with httpx.AsyncClient(
            timeout=ONLINE_REQUEST_TIMEOUT,
            headers=_DEFAULT_HEADERS,
            follow_redirects=True,
            verify=True,
        ) as client:
            # Tentar GET na pagina de certidao
            resp_get = await client.get(url)
            resp_get.raise_for_status()

            # Extrair campos de formulario
            form_data = {"cnpj": cnpj, "tipoPessoa": "J"}

            # Tentar extrair campos ASP.NET ou similares
            viewstate = self._extract_aspnet_field(resp_get.text, "__VIEWSTATE")
            if viewstate:
                form_data["__VIEWSTATE"] = viewstate

            resp_post = await client.post(url, data=form_data)
            resp_post.raise_for_status()

            body = resp_post.text
            result.raw_snippet = body[:500]
            body_lower = body.lower()

            if (
                "certidão negativa" in body_lower
                or "nada consta" in body_lower
                or "regularidade fiscal" in body_lower
                and "atestamos" in body_lower
            ):
                result.is_valid = True
            elif "débitos" in body_lower or "pendências" in body_lower or "certidão positiva" in body_lower:
                result.is_valid = False

            result.emission_date = _extract_date_from_text(body, "emiss")
            result.expiry_date = _extract_date_from_text(body, "valid")

        return result

    async def _verificar_cnd_municipal_iss_manaus(self, cnpj: str) -> CertificateOnlineResult:
        """
        Verifica CND Municipal / ISS (Prefeitura de Manaus).

        URL: https://nfs-e.manaus.am.gov.br/
        Portal NFS-e de Manaus.
        """
        url = "https://nfs-e.manaus.am.gov.br/"
        result = CertificateOnlineResult(
            tipo=TipoDocumentoMonitorado.CND_MUNICIPAL,
            cnpj=cnpj,
            url_consultada=url,
        )

        async with httpx.AsyncClient(
            timeout=ONLINE_REQUEST_TIMEOUT,
            headers=_DEFAULT_HEADERS,
            follow_redirects=True,
            verify=True,
        ) as client:
            # GET pagina principal para descobrir URL de certidao
            resp_get = await client.get(url)
            resp_get.raise_for_status()

            # Tentar acessar endpoint de certidao (varia conforme portal)
            certidao_url = url.rstrip("/") + "/certidao"
            try:
                resp_cert = await client.get(certidao_url)
                resp_cert.raise_for_status()
                form_target = certidao_url
            except httpx.HTTPStatusError:
                # Tentar URL alternativa
                form_target = url

            form_data = {
                "cnpj": cnpj,
                "inscricaoMunicipal": "45177801",  # Inscricao Municipal Conecta
                "tipoPessoa": "J",
            }

            resp_post = await client.post(form_target, data=form_data)
            resp_post.raise_for_status()

            body = resp_post.text
            result.raw_snippet = body[:500]
            body_lower = body.lower()

            if "certidão negativa" in body_lower or "nada consta" in body_lower or "regularidade fiscal" in body_lower:
                result.is_valid = True
            elif "débitos" in body_lower or "irregularidade" in body_lower or "certidão positiva" in body_lower:
                result.is_valid = False

            result.emission_date = _extract_date_from_text(body, "emiss")
            result.expiry_date = _extract_date_from_text(body, "valid")

        return result

    # ──────────────────────────────────────────
    # Helpers de parse HTML
    # ──────────────────────────────────────────

    @staticmethod
    def _extract_aspnet_field(html: str, field_name: str) -> str | None:
        """Extrai campo hidden de formulario ASP.NET (__VIEWSTATE, etc)."""
        pattern = re.compile(
            rf'<input[^>]*name="{re.escape(field_name)}"[^>]*value="([^"]*)"',
            re.IGNORECASE,
        )
        m = pattern.search(html)
        if m:
            return m.group(1)
        # Tentar com aspas simples
        pattern2 = re.compile(
            rf"<input[^>]*name='{re.escape(field_name)}'[^>]*value='([^']*)'",
            re.IGNORECASE,
        )
        m2 = pattern2.search(html)
        return m2.group(1) if m2 else None

    @staticmethod
    def _extract_jsf_viewstate(html: str) -> str | None:
        """Extrai javax.faces.ViewState de formulario JSF."""
        pattern = re.compile(
            r'<input[^>]*name="javax\.faces\.ViewState"[^>]*value="([^"]*)"',
            re.IGNORECASE,
        )
        m = pattern.search(html)
        return m.group(1) if m else None

    # ──────────────────────────────────────────
    # Aplicar resultados online nos documentos
    # ──────────────────────────────────────────

    def _aplicar_resultados_online(
        self,
        documentos: list[DocumentoMonitorado],
        online_results: list[CertificateOnlineResult],
        hoje: date,
    ) -> None:
        """
        Aplica resultados da verificacao online nos DocumentoMonitorado.

        Se a verificacao online retornou dados validos (is_valid != None),
        atualiza o documento correspondente. Caso contrario, mantem o status
        offline (fallback).
        """
        results_map = {r.tipo: r for r in online_results}

        for doc in documentos:
            online = results_map.get(doc.tipo)
            if online is None:
                continue

            doc.fonte_verificacao = online.fonte

            if online.is_valid is None:
                # Verificacao indeterminada — manter status offline
                doc.erro_consulta = online.erro
                continue

            doc.verificado_online = True
            doc.ultima_consulta = datetime.utcnow()

            # Atualizar datas se obtidas online
            if online.emission_date:
                doc.data_emissao = online.emission_date
            if online.expiry_date:
                doc.data_validade = online.expiry_date

            # Atualizar status baseado na verificacao online
            if online.is_valid:
                if doc.data_validade and doc.data_validade >= hoje:
                    # Recalcular com nova validade
                    self._atualizar_status(doc, hoje)
                else:
                    # Valida online mas sem data de validade — considerar valida
                    doc.status = StatusDocumento.VALIDO
                    doc.nivel_alerta = NivelAlerta.OK
                    # Se nao tem validade, estimar com padrao
                    if not doc.data_validade and doc.data_emissao:
                        doc.data_validade = doc.data_emissao + timedelta(days=doc.validade_padrao_dias)
                        self._atualizar_status(doc, hoje)
                    elif not doc.data_validade:
                        # Sem data nenhuma mas confirmado valido online
                        doc.data_emissao = hoje
                        doc.data_validade = hoje + timedelta(days=doc.validade_padrao_dias)
                        self._atualizar_status(doc, hoje)
            else:
                # Certidao invalida/positiva online
                doc.status = StatusDocumento.VENCIDO
                doc.nivel_alerta = NivelAlerta.CRITICO
                doc.dias_para_vencimento = 0
                doc.observacoes = (doc.observacoes or "") + " [Verificacao online: certidao POSITIVA/invalida]"

    # ──────────────────────────────────────────
    # Metodos originais (offline)
    # ──────────────────────────────────────────

    def _parse_documentos_input(self, documentos: list[dict], cnpj: str) -> list[DocumentoMonitorado]:
        """Converte input de documentos para DocumentoMonitorado."""
        resultado = []

        # Mapa de info padrao por tipo
        info_padrao = {d["tipo"].value: d for d in DOCUMENTOS_PADRAO}

        for doc_input in documentos:
            tipo_str = doc_input.get("tipo", "")
            try:
                tipo = TipoDocumentoMonitorado(tipo_str)
            except ValueError:
                self.logger.warning(f"Tipo de documento desconhecido: {tipo_str}")
                continue

            padrao = info_padrao.get(tipo_str, {})

            data_emissao = None
            data_validade = None

            if doc_input.get("data_emissao"):
                data_emissao = date.fromisoformat(doc_input["data_emissao"])
            if doc_input.get("data_validade"):
                data_validade = date.fromisoformat(doc_input["data_validade"])

            doc = DocumentoMonitorado(
                tipo=tipo,
                nome_exibicao=padrao.get("nome_exibicao", tipo_str),
                cnpj_empresa=cnpj,
                data_emissao=data_emissao,
                data_validade=data_validade,
                validade_padrao_dias=padrao.get("validade_padrao_dias", 180),
                url_consulta=padrao.get("url_consulta"),
                arquivo_path=doc_input.get("arquivo_path"),
            )
            resultado.append(doc)

        return resultado

    def _criar_documentos_padrao(self, cnpj: str) -> list[DocumentoMonitorado]:
        """Cria lista de documentos padrao sem datas (status: nao_possui)."""
        resultado = []
        for padrao in DOCUMENTOS_PADRAO:
            doc = DocumentoMonitorado(
                tipo=padrao["tipo"],
                nome_exibicao=padrao["nome_exibicao"],
                cnpj_empresa=cnpj,
                validade_padrao_dias=padrao["validade_padrao_dias"],
                url_consulta=padrao.get("url_consulta"),
                status=StatusDocumento.NAO_POSSUI,
            )
            resultado.append(doc)
        return resultado

    def _atualizar_status(self, doc: DocumentoMonitorado, hoje: date) -> None:
        """Atualiza status e nivel de alerta de um documento."""
        if doc.data_validade is None:
            if doc.data_emissao is not None:
                # Calcular validade estimada
                doc.data_validade = doc.data_emissao + timedelta(days=doc.validade_padrao_dias)
            else:
                doc.status = StatusDocumento.NAO_POSSUI
                doc.nivel_alerta = NivelAlerta.CRITICO
                doc.dias_para_vencimento = None
                return

        dias_restantes = (doc.data_validade - hoje).days
        doc.dias_para_vencimento = dias_restantes
        doc.ultima_consulta = datetime.utcnow()

        if dias_restantes < 0:
            doc.status = StatusDocumento.VENCIDO
            doc.nivel_alerta = NivelAlerta.CRITICO
        elif dias_restantes <= self.ALERTA_CRITICO_DIAS:
            doc.status = StatusDocumento.VENCENDO
            doc.nivel_alerta = NivelAlerta.CRITICO
        elif dias_restantes <= self.ALERTA_URGENTE_DIAS:
            doc.status = StatusDocumento.VENCENDO
            doc.nivel_alerta = NivelAlerta.URGENTE
        elif dias_restantes <= self.ALERTA_ATENCAO_DIAS:
            doc.status = StatusDocumento.VENCENDO
            doc.nivel_alerta = NivelAlerta.ATENCAO
        else:
            doc.status = StatusDocumento.VALIDO
            doc.nivel_alerta = NivelAlerta.OK

        # Proximo check: documentos criticos verificar diariamente,
        # urgentes a cada 3 dias, atencao semanalmente, ok mensalmente
        intervalo = {
            NivelAlerta.CRITICO: 1,
            NivelAlerta.URGENTE: 3,
            NivelAlerta.ATENCAO: 7,
            NivelAlerta.OK: 30,
        }[doc.nivel_alerta]
        doc.proximo_check = datetime.utcnow() + timedelta(days=intervalo)

    def _construir_resposta(
        self,
        documentos: list[DocumentoMonitorado],
        hoje: date,
        online_results: list[CertificateOnlineResult] | None = None,
    ) -> SentinelResponse:
        """Constroi resposta consolidada."""
        validos = sum(1 for d in documentos if d.status == StatusDocumento.VALIDO)
        vencendo = sum(1 for d in documentos if d.status == StatusDocumento.VENCENDO)
        vencidos = sum(1 for d in documentos if d.status == StatusDocumento.VENCIDO)
        nao_possui = sum(1 for d in documentos if d.status == StatusDocumento.NAO_POSSUI)

        alertas_criticos = []
        alertas_urgentes = []
        alertas_atencao = []

        # Mapa de obrigatoriedade
        obrigatorio_map = {d["tipo"].value: d.get("obrigatorio_licitar", True) for d in DOCUMENTOS_PADRAO}

        motivos_inaptidao = []

        for doc in documentos:
            obrigatorio = obrigatorio_map.get(doc.tipo.value, True)

            if doc.nivel_alerta == NivelAlerta.CRITICO:
                msg = f"{doc.nome_exibicao}: "
                if doc.status == StatusDocumento.VENCIDO:
                    msg += f"VENCIDO ha {abs(doc.dias_para_vencimento or 0)} dias"
                elif doc.status == StatusDocumento.VENCENDO:
                    msg += f"vence em {doc.dias_para_vencimento} dias"
                elif doc.status == StatusDocumento.NAO_POSSUI:
                    msg += "NAO CADASTRADO"
                alertas_criticos.append(msg)
                if obrigatorio:
                    motivos_inaptidao.append(msg)

            elif doc.nivel_alerta == NivelAlerta.URGENTE:
                alertas_urgentes.append(f"{doc.nome_exibicao}: vence em {doc.dias_para_vencimento} dias")
                if obrigatorio and doc.status == StatusDocumento.VENCENDO:
                    # Urgente mas ainda valido
                    pass

            elif doc.nivel_alerta == NivelAlerta.ATENCAO:
                alertas_atencao.append(f"{doc.nome_exibicao}: vence em {doc.dias_para_vencimento} dias")

        # Apto para licitar = sem alertas criticos em documentos obrigatorios
        apto = len(motivos_inaptidao) == 0

        # Proxima verificacao = menor proximo_check entre documentos
        proxima = None
        for doc in documentos:
            if doc.proximo_check:
                if proxima is None or doc.proximo_check < proxima:
                    proxima = doc.proximo_check

        return SentinelResponse(
            total_documentos=len(documentos),
            validos=validos,
            vencendo=vencendo,
            vencidos=vencidos,
            nao_possui=nao_possui,
            alertas_criticos=alertas_criticos,
            alertas_urgentes=alertas_urgentes,
            alertas_atencao=alertas_atencao,
            documentos=documentos,
            apto_licitar=apto,
            motivo_inaptidao=motivos_inaptidao,
            verificacoes_online=online_results or [],
            verificado_em=datetime.utcnow(),
            proxima_verificacao=proxima,
        )
