"""
Classificador de Erros para Integrações Governamentais.

Categoriza erros e determina ações apropriadas.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class CategoriaErro(Enum):
    """Categorias de erro para tratamento diferenciado."""
    AUTENTICACAO = "autenticacao"      # Token/certificado inválido
    CERTIFICADO = "certificado"        # Certificado vencido/inválido
    TIMEOUT = "timeout"                # Serviço não respondeu
    INDISPONIVEL = "indisponivel"      # Serviço fora do ar
    SCHEMA = "schema"                  # XML/dados inválidos
    NEGOCIO = "negocio"                # Regra de negócio violada
    REDE = "rede"                      # Erro de conexão
    RATE_LIMIT = "rate_limit"          # Limite de requisições excedido
    DESCONHECIDO = "desconhecido"      # Outros


@dataclass
class ErroIntegracao:
    """Estrutura padronizada de erro."""
    categoria: CategoriaErro
    codigo: str
    mensagem: str
    servico: str
    tentativas: int = 0
    pode_retentar: bool = True
    acao_recomendada: Optional[str] = None
    dados_adicionais: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "categoria": self.categoria.value,
            "codigo": self.codigo,
            "mensagem": self.mensagem,
            "servico": self.servico,
            "tentativas": self.tentativas,
            "pode_retentar": self.pode_retentar,
            "acao_recomendada": self.acao_recomendada,
            "dados_adicionais": self.dados_adicionais,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }


class ClassificadorErros:
    """Classifica erros e determina ação apropriada."""

    # Padrões de erro por categoria
    PADROES_ERRO: Dict[CategoriaErro, List[str]] = {
        CategoriaErro.AUTENTICACAO: [
            "token expired", "invalid_token", "unauthorized",
            "401", "403", "token inválido", "sessão expirada",
            "authentication failed", "invalid credentials",
            "access denied", "not authenticated",
        ],
        CategoriaErro.CERTIFICADO: [
            "certificate", "ssl", "x509", "certificado vencido",
            "bad certificate", "certificate expired", "cert_error",
            "ssl_error", "handshake", "pkcs", "pfx",
        ],
        CategoriaErro.TIMEOUT: [
            "timeout", "timed out", "tempo limite", "deadline exceeded",
            "request timeout", "connection timeout", "read timeout",
        ],
        CategoriaErro.INDISPONIVEL: [
            "503", "502", "504", "service unavailable",
            "connection refused", "host unreachable", "server error",
            "temporarily unavailable", "maintenance",
        ],
        CategoriaErro.SCHEMA: [
            "xml", "xsd", "schema", "validation", "parse error",
            "malformed", "invalid format", "invalid xml",
            "namespace", "element not found",
        ],
        CategoriaErro.NEGOCIO: [
            "rejeição", "rejeitado", "não autorizado",
            "duplicado", "já existe", "não encontrado",
            "regra de negócio", "business rule", "invalid data",
        ],
        CategoriaErro.RATE_LIMIT: [
            "429", "rate limit", "too many requests",
            "quota exceeded", "throttling", "limit exceeded",
        ],
        CategoriaErro.REDE: [
            "connection error", "network", "dns",
            "host not found", "socket", "connection reset",
        ],
    }

    # Ações recomendadas por categoria
    ACOES_RECOMENDADAS: Dict[CategoriaErro, str] = {
        CategoriaErro.AUTENTICACAO: "Renovar token automaticamente",
        CategoriaErro.CERTIFICADO: "CRÍTICO: Suspender serviço e alertar admin",
        CategoriaErro.TIMEOUT: "Aplicar retry com backoff exponencial",
        CategoriaErro.INDISPONIVEL: "Tentar endpoint de contingência",
        CategoriaErro.SCHEMA: "Marcar para reprocessamento manual",
        CategoriaErro.NEGOCIO: "Registrar e notificar usuário",
        CategoriaErro.RATE_LIMIT: "Aguardar cooldown e retentar",
        CategoriaErro.REDE: "Verificar conectividade e retentar",
        CategoriaErro.DESCONHECIDO: "Registrar para análise",
    }

    # Categorias que permitem retry automático
    CATEGORIAS_RETENTAVEIS = {
        CategoriaErro.TIMEOUT,
        CategoriaErro.INDISPONIVEL,
        CategoriaErro.REDE,
        CategoriaErro.RATE_LIMIT,
    }

    @classmethod
    def classificar(
        cls,
        erro: Exception,
        servico: str,
        tentativas: int = 0,
        correlation_id: Optional[str] = None
    ) -> ErroIntegracao:
        """
        Classifica erro e retorna estrutura padronizada.

        Args:
            erro: Exceção capturada
            servico: Nome do serviço onde ocorreu o erro
            tentativas: Número de tentativas já realizadas
            correlation_id: ID de correlação para rastreamento

        Returns:
            ErroIntegracao com classificação e recomendações
        """
        erro_str = str(erro).lower()
        erro_tipo = type(erro).__name__

        # Identificar categoria
        categoria = CategoriaErro.DESCONHECIDO
        for cat, padroes in cls.PADROES_ERRO.items():
            if any(p in erro_str for p in padroes):
                categoria = cat
                break

        # Verificar código HTTP se disponível
        http_code = cls._extrair_codigo_http(erro_str)
        if http_code:
            categoria = cls._classificar_por_http(http_code, categoria)

        # Determinar se pode retentar
        pode_retentar = categoria in cls.CATEGORIAS_RETENTAVEIS

        # Extrair dados adicionais
        dados_adicionais = cls._extrair_dados_adicionais(erro, erro_str)

        return ErroIntegracao(
            categoria=categoria,
            codigo=erro_tipo,
            mensagem=str(erro)[:500],
            servico=servico,
            tentativas=tentativas,
            pode_retentar=pode_retentar,
            acao_recomendada=cls.ACOES_RECOMENDADAS.get(categoria),
            dados_adicionais=dados_adicionais,
            correlation_id=correlation_id,
        )

    @classmethod
    def _extrair_codigo_http(cls, erro_str: str) -> Optional[int]:
        """Extrai código HTTP da mensagem de erro."""
        # Padrões comuns: "HTTP 500", "status 404", "code: 503"
        patterns = [
            r'http[s]?\s*(\d{3})',
            r'status[:\s]+(\d{3})',
            r'code[:\s]+(\d{3})',
            r'\b([45]\d{2})\b',
        ]
        for pattern in patterns:
            match = re.search(pattern, erro_str, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    @classmethod
    def _classificar_por_http(
        cls,
        http_code: int,
        categoria_atual: CategoriaErro
    ) -> CategoriaErro:
        """Classifica ou refina categoria baseado em código HTTP."""
        if http_code == 401:
            return CategoriaErro.AUTENTICACAO
        elif http_code == 403:
            return CategoriaErro.AUTENTICACAO
        elif http_code == 404:
            return CategoriaErro.NEGOCIO
        elif http_code == 429:
            return CategoriaErro.RATE_LIMIT
        elif http_code in (502, 503, 504):
            return CategoriaErro.INDISPONIVEL
        elif 400 <= http_code < 500:
            return CategoriaErro.NEGOCIO
        elif http_code >= 500:
            return CategoriaErro.INDISPONIVEL
        return categoria_atual

    @classmethod
    def _extrair_dados_adicionais(
        cls,
        erro: Exception,
        erro_str: str
    ) -> Optional[Dict[str, Any]]:
        """Extrai dados adicionais do erro para diagnóstico."""
        dados = {}

        # Código HTTP
        http_code = cls._extrair_codigo_http(erro_str)
        if http_code:
            dados["http_code"] = http_code

        # Código SEFAZ/eSocial
        codigo_sefaz = re.search(r'cstat[:\s]*(\d+)', erro_str, re.IGNORECASE)
        if codigo_sefaz:
            dados["codigo_sefaz"] = codigo_sefaz.group(1)

        # Mensagem original do serviço
        xmotivo = re.search(r'xmotivo[:\s]*([^<\n]+)', erro_str, re.IGNORECASE)
        if xmotivo:
            dados["mensagem_servico"] = xmotivo.group(1).strip()

        # Atributos específicos da exceção
        if hasattr(erro, 'response'):
            dados["response_type"] = type(erro.response).__name__
        if hasattr(erro, 'request'):
            dados["request_type"] = type(erro.request).__name__

        return dados if dados else None

    @classmethod
    def deve_alertar_admin(cls, erro: ErroIntegracao) -> bool:
        """Determina se o erro deve gerar alerta para admin."""
        categorias_criticas = {
            CategoriaErro.CERTIFICADO,
        }

        # Alertar se categoria crítica
        if erro.categoria in categorias_criticas:
            return True

        # Alertar se muitas tentativas falharam
        if erro.tentativas >= 5:
            return True

        return False

    @classmethod
    def deve_usar_contingencia(cls, erro: ErroIntegracao) -> bool:
        """Determina se deve tentar endpoint de contingência."""
        return erro.categoria in {
            CategoriaErro.INDISPONIVEL,
            CategoriaErro.TIMEOUT,
        }

    def classificar_erro_http(
        self,
        status_code: int,
        response_body: str
    ) -> Dict[str, Any]:
        """
        Classifica erro HTTP e determina se deve fazer retry.

        Args:
            status_code: Código HTTP da resposta
            response_body: Corpo da resposta

        Returns:
            Dict com classificação e flag de retry
        """
        categoria = self._classificar_por_http(status_code, CategoriaErro.DESCONHECIDO)

        # Determinar se pode retentar
        retry = categoria in self.CATEGORIAS_RETENTAVEIS

        # Códigos específicos que não devem retentar
        if status_code in (400, 401, 403, 404, 422):
            retry = False

        # 500 pode ser temporário em alguns casos
        if status_code == 500:
            # Verificar se é erro de validação (não retentar)
            if "soap:sender" in response_body.lower():
                retry = False
            # Verificar se é erro temporário
            elif "temporary" in response_body.lower():
                retry = True
            else:
                retry = False

        return {
            "categoria": categoria.value,
            "status_code": status_code,
            "retry": retry,
            "acao": self.ACOES_RECOMENDADAS.get(categoria, "Registrar para análise"),
        }
