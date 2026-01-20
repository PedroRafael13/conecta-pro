"""
Extrator Base para Serviços Governamentais.

Classe base com funcionalidades comuns a todos os extratores.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, AsyncIterator
from dataclasses import dataclass, field
from uuid import UUID
import asyncio
import logging
import aiohttp
import ssl

from ..core.credentials import ProvedorCredenciais, TipoCredencial
from ..core.etl import NormalizadorDados, ValidadorXSD, DeduplicadorDocumentos
from ..core.errors import ClassificadorErros, RetryConfig
from ..core.contingency import ComutadorEndpoints

logger = logging.getLogger(__name__)


@dataclass
class DocumentoExtraido:
    """Documento extraído de serviço governamental."""
    id: str  # Identificador único (chave_acesso, id_evento, etc.)
    tipo: str  # nfe, cte, evento_esocial, etc.
    dados: Dict[str, Any]
    xml_original: Optional[str] = None
    data_documento: Optional[datetime] = None
    processado: bool = False
    erro: Optional[str] = None


@dataclass
class ResultadoExtracao:
    """Resultado de extração de um serviço."""
    servico: str
    status: str = "em_andamento"
    inicio: datetime = field(default_factory=datetime.utcnow)
    fim: Optional[datetime] = None
    documentos_processados: int = 0
    documentos_novos: int = 0
    documentos_atualizados: int = 0
    documentos_erro: int = 0
    erros: List[str] = field(default_factory=list)
    detalhes: Dict[str, Any] = field(default_factory=dict)
    documentos: List[DocumentoExtraido] = field(default_factory=list)


class ExtratorBase(ABC):
    """
    Classe base para extratores de dados governamentais.

    Fornece:
    - Gerenciamento de sessão HTTP com certificado
    - Retry automático com backoff
    - Normalização de dados
    - Validação de XML
    - Deduplicação
    """

    # Configurações padrão
    TIMEOUT = 30
    MAX_RETRIES = 3
    BATCH_SIZE = 100

    def __init__(
        self,
        credentials: ProvedorCredenciais,
        comutador: Optional[ComutadorEndpoints] = None,
    ):
        self.credentials = credentials
        self.comutador = comutador or ComutadorEndpoints()
        self.normalizador = NormalizadorDados()
        self.validador = ValidadorXSD()
        self.classificador = ClassificadorErros()
        self._session: Optional[aiohttp.ClientSession] = None
        self._ssl_context: Optional[ssl.SSLContext] = None

    @property
    @abstractmethod
    def tipo_servico(self) -> str:
        """Tipo do serviço (sefaz_nfe, esocial, etc.)"""
        pass

    @property
    @abstractmethod
    def tipo_credencial(self) -> TipoCredencial:
        """Tipo de credencial necessária."""
        pass

    @abstractmethod
    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cnpjs: Optional[List[str]] = None,
        ufs: Optional[List[str]] = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """
        Executa extração de dados.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial do período
            data_fim: Data final do período
            cnpjs: Lista de CNPJs a consultar
            ufs: Lista de UFs a consultar
            incremental: Se True, extrai apenas novos/alterados

        Returns:
            ResultadoExtracao com documentos e estatísticas
        """
        pass

    async def _get_session(
        self,
        tenant_id: UUID,
        with_cert: bool = True
    ) -> aiohttp.ClientSession:
        """
        Obtém sessão HTTP configurada.

        Args:
            tenant_id: ID do tenant
            with_cert: Se deve incluir certificado

        Returns:
            Sessão aiohttp configurada
        """
        if self._session is None or self._session.closed:
            connector = None

            if with_cert:
                # Obter certificado do tenant
                ssl_context = await self._criar_ssl_context(tenant_id)
                connector = aiohttp.TCPConnector(ssl=ssl_context)

            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
            )

        return self._session

    async def _criar_ssl_context(self, tenant_id: UUID) -> ssl.SSLContext:
        """Cria contexto SSL com certificado do tenant."""
        # Tentar usar FileCredentialProvider primeiro (modo simplificado)
        try:
            from ..core.credentials.file_credential_provider import get_file_credential_provider

            file_provider = get_file_credential_provider()
            return file_provider.get_ssl_context()

        except Exception as e:
            logger.debug(f"FileCredentialProvider não disponível: {e}")

        # Fallback: usar Vault/GerenciadorCertificados
        try:
            from ..core.credentials import GerenciadorCertificados, TipoCertificado

            cert_manager = GerenciadorCertificados(self.credentials.vault)

            # Mapear tipo de credencial para tipo de certificado
            tipo_cert = TipoCertificado.E_CNPJ

            ssl_ctx = await cert_manager.criar_contexto_ssl(tenant_id, tipo_cert)

            if ssl_ctx is not None:
                return ssl_ctx

        except Exception as e:
            logger.debug(f"Vault não disponível: {e}")

        # Último fallback: contexto sem certificado cliente
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        return ssl_ctx

    async def _fazer_requisicao(
        self,
        tenant_id: UUID,
        url: str,
        method: str = "POST",
        data: Optional[str] = None,
        headers: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Faz requisição HTTP com retry.

        Args:
            tenant_id: ID do tenant
            url: URL do serviço
            method: Método HTTP
            data: Dados da requisição
            headers: Headers adicionais

        Returns:
            Resposta como string ou None se falhar
        """
        default_headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
        }
        if headers:
            default_headers.update(headers)

        # Validar URL
        if not url:
            logger.error("URL vazia - não é possível fazer requisição")
            return None

        logger.debug(f"Requisição {method} para: {url}")

        session = await self._get_session(tenant_id)

        for tentativa in range(self.MAX_RETRIES):
            try:
                async with session.request(
                    method,
                    url,
                    data=data,
                    headers=default_headers,
                ) as response:
                    if response.status == 200:
                        logger.debug(f"Resposta 200 OK de {url}")
                        return await response.text()

                    logger.warning(
                        f"Resposta não-200: {response.status} - {url}"
                    )

                    # Classificar erro
                    erro = await response.text()
                    classificacao = self.classificador.classificar_erro_http(
                        response.status, erro
                    )

                    if not classificacao.get("retry", False):
                        raise Exception(f"Erro não recuperável: {erro[:200]}")

            except aiohttp.ClientError as e:
                logger.error(
                    f"Erro de conexão (tentativa {tentativa + 1}/{self.MAX_RETRIES}): "
                    f"{type(e).__name__}: {e} - URL: {url}"
                )

                if tentativa < self.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** tentativa)  # Backoff exponencial
                else:
                    raise

        return None

    async def _processar_documento(
        self,
        doc: DocumentoExtraido,
        validar_xsd: bool = True,
        normalizar: bool = True,
    ) -> DocumentoExtraido:
        """
        Processa um documento extraído.

        Args:
            doc: Documento a processar
            validar_xsd: Se deve validar XML contra XSD
            normalizar: Se deve normalizar campos

        Returns:
            Documento processado
        """
        try:
            # Validar XML
            if validar_xsd and doc.xml_original:
                valido, erros = self.validador.validar(doc.xml_original, doc.tipo)
                if not valido:
                    doc.erro = f"XML inválido: {'; '.join(erros)}"
                    return doc

            # Normalizar dados
            if normalizar:
                doc.dados = self._normalizar_dados(doc.dados, doc.tipo)

            doc.processado = True

        except Exception as e:
            doc.erro = str(e)
            logger.error(f"Erro ao processar documento {doc.id}: {e}")

        return doc

    def _normalizar_dados(
        self,
        dados: Dict[str, Any],
        tipo: str
    ) -> Dict[str, Any]:
        """Normaliza dados do documento."""
        # CPF/CNPJ
        for campo in ["cpf", "cnpj", "emit_cnpj", "dest_cnpj"]:
            if campo in dados and dados[campo]:
                if len(str(dados[campo]).replace(".", "").replace("-", "").replace("/", "")) == 11:
                    dados[campo] = self.normalizador.normalizar_cpf(dados[campo])
                else:
                    dados[campo] = self.normalizador.normalizar_cnpj(dados[campo])

        # Datas
        for campo in ["data_emissao", "dhEmi", "data_envio", "data_processamento"]:
            if campo in dados and dados[campo]:
                dados[campo] = self.normalizador.normalizar_data(dados[campo])

        # Valores
        for campo in ["valor_total", "vNF", "vProd", "valor"]:
            if campo in dados and dados[campo]:
                dados[campo] = self.normalizador.normalizar_valor(dados[campo])

        return dados

    async def close(self):
        """Fecha recursos."""
        if self._session and not self._session.closed:
            await self._session.close()

    def __del__(self):
        """Destrutor."""
        if self._session and not self._session.closed:
            asyncio.create_task(self._session.close())
