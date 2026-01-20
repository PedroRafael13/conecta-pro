"""
Verificador de Disponibilidade de Endpoints.

Testa periodicamente endpoints para detectar indisponibilidade e recuperação.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import ssl
import logging

import aiohttp

from .uf_matrix import (
    MatrizContingencia,
    MATRIZ_CONTINGENCIA_NFE,
    ENDPOINTS_CENTRALIZADOS,
)
from .endpoint_switcher import ComutadorEndpoints, StatusEndpoint

logger = logging.getLogger(__name__)


@dataclass
class ResultadoVerificacao:
    """Resultado de verificação de endpoint."""
    uf: str
    tipo_documento: str
    endpoint: str
    disponivel: bool
    tempo_resposta_ms: float
    http_status: Optional[int] = None
    erro: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class VerificadorDisponibilidade:
    """Verifica disponibilidade de endpoints governamentais."""

    # Timeout para verificação (segundos)
    TIMEOUT = 10

    # Serviço para teste (StatusServico é o mais leve)
    SERVICO_TESTE = {
        "nfe": "NfeStatusServico4",
        "cte": "CteStatusServico",
        "mdfe": "MDFeStatusServico",
    }

    def __init__(self, comutador: Optional[ComutadorEndpoints] = None):
        self.comutador = comutador or ComutadorEndpoints()
        self._ssl_context = self._criar_ssl_context()

    def _criar_ssl_context(self) -> ssl.SSLContext:
        """Cria contexto SSL permissivo para testes."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    async def verificar_endpoint(
        self,
        uf: str,
        tipo_documento: str,
        usar_principal: bool = True
    ) -> ResultadoVerificacao:
        """
        Verifica disponibilidade de um endpoint.

        Args:
            uf: Sigla da UF
            tipo_documento: Tipo (nfe, cte, mdfe)
            usar_principal: Se True, testa principal; senão, contingência

        Returns:
            ResultadoVerificacao
        """
        # Obter configuração
        if tipo_documento.lower() == "nfe":
            config = MatrizContingencia.obter_config_nfe(uf)
        elif tipo_documento.lower() == "cte":
            config = MatrizContingencia.obter_config_cte(uf)
        elif tipo_documento.lower() == "mdfe":
            config = MatrizContingencia.obter_config_mdfe(uf)
        else:
            return ResultadoVerificacao(
                uf=uf,
                tipo_documento=tipo_documento,
                endpoint="",
                disponivel=False,
                tempo_resposta_ms=0,
                erro=f"Tipo não suportado: {tipo_documento}",
            )

        # Selecionar endpoint
        if usar_principal:
            url_base = config.principal.url
        elif config.contingencia:
            url_base = config.contingencia.url
        else:
            return ResultadoVerificacao(
                uf=uf,
                tipo_documento=tipo_documento,
                endpoint="",
                disponivel=False,
                tempo_resposta_ms=0,
                erro="Contingência não configurada",
            )

        # Resolver URL
        servico = self.SERVICO_TESTE.get(tipo_documento.lower(), "NfeStatusServico4")
        url = MatrizContingencia.resolver_url(url_base, servico)

        # Fazer verificação
        return await self._testar_url(uf, tipo_documento, url)

    async def _testar_url(
        self,
        uf: str,
        tipo_documento: str,
        url: str
    ) -> ResultadoVerificacao:
        """Testa uma URL específica."""
        inicio = datetime.utcnow()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
                    ssl=self._ssl_context,
                ) as response:
                    tempo_ms = (datetime.utcnow() - inicio).total_seconds() * 1000

                    # 200, 403, 405, 500 indicam servidor online
                    # (403/405 = requer certificado, 500 = erro mas online)
                    disponivel = response.status < 502

                    return ResultadoVerificacao(
                        uf=uf,
                        tipo_documento=tipo_documento,
                        endpoint=url,
                        disponivel=disponivel,
                        tempo_resposta_ms=tempo_ms,
                        http_status=response.status,
                    )

        except aiohttp.ClientSSLError as e:
            tempo_ms = (datetime.utcnow() - inicio).total_seconds() * 1000
            # Erro SSL geralmente significa servidor online mas requer cert
            return ResultadoVerificacao(
                uf=uf,
                tipo_documento=tipo_documento,
                endpoint=url,
                disponivel=True,  # Servidor respondeu
                tempo_resposta_ms=tempo_ms,
                erro="Requer certificado",
            )

        except asyncio.TimeoutError:
            tempo_ms = (datetime.utcnow() - inicio).total_seconds() * 1000
            return ResultadoVerificacao(
                uf=uf,
                tipo_documento=tipo_documento,
                endpoint=url,
                disponivel=False,
                tempo_resposta_ms=tempo_ms,
                erro="Timeout",
            )

        except Exception as e:
            tempo_ms = (datetime.utcnow() - inicio).total_seconds() * 1000
            return ResultadoVerificacao(
                uf=uf,
                tipo_documento=tipo_documento,
                endpoint=url,
                disponivel=False,
                tempo_resposta_ms=tempo_ms,
                erro=str(e)[:100],
            )

    async def verificar_todas_ufs(
        self,
        tipo_documento: str = "nfe",
        concorrencia: int = 10
    ) -> List[ResultadoVerificacao]:
        """
        Verifica todas as UFs para um tipo de documento.

        Args:
            tipo_documento: Tipo (nfe, cte, mdfe)
            concorrencia: Máximo de verificações simultâneas

        Returns:
            Lista de ResultadoVerificacao
        """
        # Obter lista de UFs
        if tipo_documento.lower() == "nfe":
            ufs = list(MATRIZ_CONTINGENCIA_NFE.keys())
        else:
            ufs = list(MATRIZ_CONTINGENCIA_NFE.keys())  # Mesmo conjunto

        # Criar semáforo para limitar concorrência
        semaphore = asyncio.Semaphore(concorrencia)

        async def verificar_com_limite(uf: str):
            async with semaphore:
                return await self.verificar_endpoint(uf, tipo_documento)

        # Executar verificações
        tarefas = [verificar_com_limite(uf) for uf in ufs]
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)

        # Processar resultados
        verificacoes = []
        for i, resultado in enumerate(resultados):
            if isinstance(resultado, Exception):
                verificacoes.append(ResultadoVerificacao(
                    uf=ufs[i],
                    tipo_documento=tipo_documento,
                    endpoint="",
                    disponivel=False,
                    tempo_resposta_ms=0,
                    erro=str(resultado),
                ))
            else:
                verificacoes.append(resultado)

        return verificacoes

    async def verificar_endpoints_centralizados(self) -> Dict[str, List[ResultadoVerificacao]]:
        """Verifica todos os endpoints centralizados."""
        resultados = {}

        for nome, endpoints in ENDPOINTS_CENTRALIZADOS.items():
            resultados[nome] = []

            for servico, url in endpoints.items():
                resultado = await self._testar_url("CENTRAL", servico, url)
                resultado.uf = nome  # Usar nome do endpoint centralizado
                resultados[nome].append(resultado)

        return resultados

    async def executar_verificacao_periodica(
        self,
        intervalo_segundos: int = 60,
        callback: Optional[callable] = None
    ):
        """
        Executa verificação periódica de endpoints.

        Args:
            intervalo_segundos: Intervalo entre verificações
            callback: Função chamada com resultados de cada verificação
        """
        logger.info(
            f"Iniciando verificação periódica (intervalo: {intervalo_segundos}s)"
        )

        while True:
            try:
                # Verificar NF-e
                resultados_nfe = await self.verificar_todas_ufs("nfe", concorrencia=5)

                # Processar resultados
                for resultado in resultados_nfe:
                    if resultado.disponivel:
                        await self.comutador.registrar_sucesso(
                            resultado.uf,
                            resultado.tipo_documento,
                            resultado.tempo_resposta_ms,
                        )
                    else:
                        await self.comutador.registrar_falha(
                            resultado.uf,
                            resultado.tipo_documento,
                            resultado.erro or "Indisponível",
                        )

                # Callback
                if callback:
                    await callback(resultados_nfe)

                # Estatísticas
                disponiveis = sum(1 for r in resultados_nfe if r.disponivel)
                logger.info(
                    f"Verificação concluída: {disponiveis}/{len(resultados_nfe)} "
                    f"endpoints disponíveis"
                )

            except Exception as e:
                logger.error(f"Erro na verificação periódica: {e}")

            await asyncio.sleep(intervalo_segundos)

    def gerar_relatorio(
        self,
        resultados: List[ResultadoVerificacao]
    ) -> Dict[str, Any]:
        """
        Gera relatório de verificação.

        Args:
            resultados: Lista de resultados de verificação

        Returns:
            Relatório com estatísticas
        """
        total = len(resultados)
        disponiveis = [r for r in resultados if r.disponivel]
        indisponiveis = [r for r in resultados if not r.disponivel]

        tempos = [r.tempo_resposta_ms for r in disponiveis if r.tempo_resposta_ms > 0]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "resumo": {
                "total": total,
                "disponiveis": len(disponiveis),
                "indisponiveis": len(indisponiveis),
                "taxa_disponibilidade": len(disponiveis) / total * 100 if total > 0 else 0,
            },
            "tempos": {
                "medio_ms": tempo_medio,
                "min_ms": min(tempos) if tempos else 0,
                "max_ms": max(tempos) if tempos else 0,
            },
            "indisponiveis": [
                {
                    "uf": r.uf,
                    "endpoint": r.endpoint,
                    "erro": r.erro,
                }
                for r in indisponiveis
            ],
            "degradados": [
                {
                    "uf": r.uf,
                    "tempo_ms": r.tempo_resposta_ms,
                }
                for r in disponiveis
                if r.tempo_resposta_ms > 5000
            ],
        }
