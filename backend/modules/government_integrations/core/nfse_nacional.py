"""
Module: NFSeNacional
Description: Integração com o Sistema Nacional NFS-e (Padrão Nacional)
             Obrigatório para todos municípios a partir de 01/01/2026
             Lei Complementar 214/2025
Author: Conecta PRO
Date: 2026-01-17

Portal: https://www.nfse.gov.br
Documentação: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica
Swagger: https://www.nfse.gov.br/swagger/contribuintesissqn/

Características:
- API REST (não mais SOAP)
- Autenticação mTLS com certificado ICP-Brasil
- XML assinado, compactado (GZip) e codificado (Base64)
- Respostas em JSON
- Número único nacional da NFS-e
"""

import base64
import gzip
import json
import hashlib
import ssl
import re
import logging
import tempfile
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4
import xml.etree.ElementTree as ET
from xml.dom import minidom

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)


# Endpoints do Sistema Nacional NFS-e
NFSE_NACIONAL_ENDPOINTS = {
    "producao": {
        "base_url": "https://www.nfse.gov.br",
        "api_url": "https://www.nfse.gov.br/api",
        "portal": "https://www.nfse.gov.br/EmissorNacional",
        "swagger": "https://www.nfse.gov.br/swagger/contribuintesissqn/",
    },
    "homologacao": {
        "base_url": "https://www.producaorestrita.nfse.gov.br",
        "api_url": "https://www.producaorestrita.nfse.gov.br/api",
        "portal": "https://www.producaorestrita.nfse.gov.br/EmissorNacional",
        "swagger": "https://www.producaorestrita.nfse.gov.br/swagger/",
    }
}


class AmbienteNacional(str, Enum):
    """Ambientes do Padrão Nacional."""
    PRODUCAO = "producao"
    HOMOLOGACAO = "homologacao"


class TipoTributacao(str, Enum):
    """Tipos de tributação no Padrão Nacional."""
    TRIBUTACAO_MUNICIPIO = "1"
    TRIBUTACAO_FORA_MUNICIPIO = "2"
    ISENCAO = "3"
    IMUNE = "4"
    EXIGIBILIDADE_SUSPENSA_JUDICIAL = "5"
    EXIGIBILIDADE_SUSPENSA_ADM = "6"
    EXPORTACAO_SERVICO = "7"


class RegimeEspecial(str, Enum):
    """Regimes especiais de tributação."""
    SEM_REGIME = "0"
    MICROEMPRESA = "1"
    ESTIMATIVA = "2"
    SOCIEDADE_PROFISSIONAIS = "3"
    COOPERATIVA = "4"
    MEI = "5"
    ME_EPP_SIMPLES = "6"


@dataclass
class PrestadorNacional:
    """Dados do prestador no Padrão Nacional."""
    cnpj: str
    inscricao_municipal: str
    codigo_municipio: str  # Código IBGE
    razao_social: str
    nome_fantasia: Optional[str] = None
    regime_especial: RegimeEspecial = RegimeEspecial.ME_EPP_SIMPLES
    optante_simples: bool = True


@dataclass
class TomadorNacional:
    """Dados do tomador no Padrão Nacional."""
    cpf_cnpj: str
    razao_social: str
    endereco: Dict[str, str] = field(default_factory=dict)
    email: Optional[str] = None
    telefone: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    tipo_documento: str = "CNPJ"  # CPF ou CNPJ


@dataclass
class ServicoNacional:
    """Dados do serviço no Padrão Nacional."""
    codigo_tributacao_nacional: str  # Código do item da NBS ou LC 116
    descricao: str
    valor_servico: Decimal
    valor_deducao: Decimal = Decimal("0")
    valor_desconto_incondicionado: Decimal = Decimal("0")
    valor_desconto_condicionado: Decimal = Decimal("0")
    codigo_cnae: Optional[str] = None
    aliquota_iss: Decimal = Decimal("0.05")
    iss_retido: bool = False


@dataclass
class DPSNacional:
    """
    Declaração de Prestação de Serviços (DPS).

    No Padrão Nacional, o RPS foi substituído pela DPS.
    """
    # Identificação
    id_dps: Optional[str] = None
    numero: Optional[str] = None

    # Prestador
    prestador: Optional[PrestadorNacional] = None

    # Tomador
    tomador: Optional[TomadorNacional] = None

    # Serviço
    servico: Optional[ServicoNacional] = None

    # Datas
    data_competencia: datetime = field(default_factory=datetime.now)

    # Tributação
    tipo_tributacao: TipoTributacao = TipoTributacao.TRIBUTACAO_MUNICIPIO

    # Valores calculados
    valor_liquido: Optional[Decimal] = None
    valor_iss: Optional[Decimal] = None

    def calcular_valores(self):
        """Calcula valores derivados."""
        if self.servico:
            base_calculo = (
                self.servico.valor_servico -
                self.servico.valor_deducao -
                self.servico.valor_desconto_incondicionado
            )
            self.valor_iss = base_calculo * self.servico.aliquota_iss

            self.valor_liquido = (
                self.servico.valor_servico -
                self.servico.valor_deducao -
                self.servico.valor_desconto_incondicionado -
                (self.valor_iss if self.servico.iss_retido else Decimal("0"))
            )


class NFSeNacionalManager:
    """
    Gerenciador de NFS-e Padrão Nacional (Preparação).

    IMPORTANTE: Esta classe está em preparação para a migração.
    O Padrão Nacional ainda não está disponível em Manaus.

    Quando a migração for realizada, este manager substituirá
    o NFSeManausManager para novas emissões.

    URLs previstas:
    - Produção: https://nfse.fazenda.gov.br/api/
    - Homologação: https://nfse-homolog.fazenda.gov.br/api/
    """

    # URLs previstas (sujeitas a alteração)
    URL_PRODUCAO = "https://nfse.fazenda.gov.br/api/v1"
    URL_HOMOLOGACAO = "https://nfse-homolog.fazenda.gov.br/api/v1"

    # Endpoints previstos
    ENDPOINTS = {
        "emitir_dps": "/dps",
        "consultar_dps": "/dps/{id}",
        "consultar_nfse": "/nfse/{numero}",
        "cancelar_nfse": "/nfse/{numero}/cancelamento",
        "substituir_nfse": "/nfse/{numero}/substituicao",
        "eventos": "/nfse/{numero}/eventos",
    }

    def __init__(
        self,
        ambiente: AmbienteNacional = AmbienteNacional.HOMOLOGACAO,
        cnpj: str = "",
        certificado_path: Optional[str] = None,
        certificado_senha: Optional[str] = None,
    ):
        """
        Inicializa o manager.

        Args:
            ambiente: Ambiente (produção ou homologação)
            cnpj: CNPJ do prestador
            certificado_path: Caminho para certificado A1
            certificado_senha: Senha do certificado
        """
        self.ambiente = ambiente
        self.cnpj = cnpj
        self.certificado_path = certificado_path
        self.certificado_senha = certificado_senha

        self.url_base = (
            self.URL_PRODUCAO if ambiente == AmbienteNacional.PRODUCAO
            else self.URL_HOMOLOGACAO
        )

        logger.info(
            f"NFSe Nacional Manager inicializado (PREPARAÇÃO) - "
            f"Ambiente: {ambiente.value}"
        )

    def emitir_dps(self, dps: DPSNacional) -> Dict[str, Any]:
        """
        Emite DPS (Declaração de Prestação de Serviços).

        NOTA: Método em preparação. Retorna estrutura simulada.

        Args:
            dps: Dados da DPS

        Returns:
            Dict com resultado da emissão
        """
        dps.calcular_valores()

        # Estrutura JSON prevista para o Padrão Nacional
        payload = {
            "infDPS": {
                "tpAmb": 1 if self.ambiente == AmbienteNacional.PRODUCAO else 2,
                "dhEmi": dps.data_competencia.isoformat(),
                "verAplic": "ConectaPRO-1.0",
                "serie": "DPS",
                "nDPS": dps.numero,
                "dCompet": dps.data_competencia.strftime("%Y-%m"),
                "prest": {
                    "CNPJ": self.cnpj,
                    "IM": dps.prestador.inscricao_municipal if dps.prestador else "",
                },
                "toma": {
                    "CNPJ" if len(dps.tomador.cpf_cnpj) == 14 else "CPF": dps.tomador.cpf_cnpj,
                    "xNome": dps.tomador.razao_social,
                } if dps.tomador else None,
                "serv": {
                    "cServ": {
                        "cTribNac": dps.servico.codigo_tributacao_nacional,
                        "CNAE": dps.servico.codigo_cnae,
                    },
                    "xDescServ": dps.servico.descricao,
                    "vServ": str(dps.servico.valor_servico),
                    "vDescIncworking": str(dps.servico.valor_desconto_incondicionado),
                } if dps.servico else None,
                "valores": {
                    "vServPrest": {
                        "vServ": str(dps.servico.valor_servico) if dps.servico else "0",
                        "vDescIncond": str(dps.servico.valor_desconto_incondicionado) if dps.servico else "0",
                    },
                    "trib": {
                        "tribMun": {
                            "tribISSQN": 1,  # ISS devido ao município
                            "pAliq": str(dps.servico.aliquota_iss * 100) if dps.servico else "5",
                            "tpRetISSQN": 1 if dps.servico and dps.servico.iss_retido else 2,
                        }
                    }
                }
            }
        }

        logger.warning(
            "NFSe Padrão Nacional: Emissão simulada (migração não disponível ainda)"
        )

        return {
            "status": "preparacao",
            "mensagem": "Padrão Nacional ainda não disponível em Manaus. "
                       "Use NFSeManausManager para emissões atuais.",
            "payload_previsto": payload,
            "previsao_migracao": "2026",
        }

    def consultar_status_migracao(self) -> Dict[str, Any]:
        """
        Consulta status da migração para o Padrão Nacional.

        Returns:
            Dict com informações sobre a migração
        """
        return {
            "municipio": "Manaus",
            "codigo_ibge": "1302603",
            "padrao_atual": "ABRASF 2.04",
            "provedor_atual": "Abaco/GIF",
            "migracao_prevista": "2026",
            "status": "aguardando",
            "notas": [
                "O Padrão Nacional está sendo implementado gradualmente",
                "Manaus ainda utiliza o padrão ABRASF via Abaco/GIF",
                "A migração trará benefícios como número único nacional",
                "Recomenda-se acompanhar comunicados da SEMEF Manaus",
            ],
            "links_uteis": {
                "portal_nacional": "https://www.gov.br/nfse",
                "documentacao": "https://www.gov.br/nfse/pt-br/acesso-a-informacao/manuais",
                "semef_manaus": "https://semef.manaus.am.gov.br",
            }
        }

    def comparar_padroes(self) -> Dict[str, Any]:
        """
        Compara características entre padrão atual e Padrão Nacional.

        Returns:
            Dict com comparação entre padrões
        """
        return {
            "abrasf_204": {
                "nome": "ABRASF 2.04 (Atual em Manaus)",
                "protocolo": "SOAP/XML",
                "autenticacao": "Certificado Digital A1/A3",
                "documento": "RPS (Recibo Provisório de Serviço)",
                "numeracao": "Municipal (cada município)",
                "cancelamento": "Até 90 dias",
                "vantagens": [
                    "Sistema estável e consolidado",
                    "Integração conhecida",
                ],
                "desvantagens": [
                    "Sem padronização nacional",
                    "Cada município tem suas regras",
                    "Dificuldade em operações intermunicipais",
                ],
            },
            "padrao_nacional": {
                "nome": "Padrão Nacional NFS-e",
                "protocolo": "REST/JSON",
                "autenticacao": "Certificado Digital + Gov.br",
                "documento": "DPS (Declaração de Prestação de Serviços)",
                "numeracao": "Nacional (único em todo Brasil)",
                "cancelamento": "Seguirá regras nacionais",
                "vantagens": [
                    "Número único nacional",
                    "Integração com eSocial/DCTFWeb",
                    "API moderna (REST/JSON)",
                    "Ambiente único de dados",
                    "Simplificação de obrigações",
                ],
                "desvantagens": [
                    "Período de transição",
                    "Necessidade de adaptação de sistemas",
                ],
            },
            "recomendacao": (
                "Mantenha o sistema atual funcionando com NFSeManausManager. "
                "Quando a migração for anunciada, ative NFSeNacionalManager "
                "e migre gradualmente as emissões."
            ),
        }


# Mapeamento de códigos de serviço ABRASF para NBS (Nomenclatura Brasileira de Serviços)
# Este mapeamento será necessário na migração
MAPEAMENTO_SERVICOS_VIGILANCIA = {
    # Código ABRASF -> Código NBS + descrição
    "11.02": {
        "nbs": "1.1701.10.00",
        "descricao": "Serviços de vigilância e segurança privada",
    },
    "11.03": {
        "nbs": "1.1701.20.00",
        "descricao": "Serviços de escolta armada",
    },
    "11.04": {
        "nbs": "1.1702.10.00",
        "descricao": "Serviços de armazenamento e guarda de bens",
    },
    "11.05": {
        "nbs": "1.1701.30.00",
        "descricao": "Serviços de transporte de valores",
    },
}


@dataclass
class NFSeNacionalResult:
    """Resultado de operação com NFS-e Nacional."""
    sucesso: bool
    mensagem: str
    codigo: Optional[str] = None
    chave_acesso: Optional[str] = None
    numero_nfse: Optional[int] = None
    codigo_verificacao: Optional[str] = None
    link_nfse: Optional[str] = None
    xml_nfse: Optional[str] = None
    pdf_danfse: Optional[bytes] = None
    dados_retorno: Optional[Dict[str, Any]] = None
    tempo_resposta: float = 0.0


class NFSeNacionalClient:
    """
    Cliente para integração com o Sistema Nacional NFS-e.

    Utiliza API REST com autenticação mTLS (certificado digital).

    Endpoints:
    - Produção: https://www.nfse.gov.br/api
    - Homologação: https://www.producaorestrita.nfse.gov.br/api

    Rotas principais:
    - POST /dps - Enviar DPS (gera NFS-e)
    - GET /dps/{id} - Consultar DPS
    - GET /nfse/{chaveAcesso} - Consultar NFS-e
    - GET /danfse/{chaveAcesso} - Baixar DANFSE (PDF)
    - POST /nfse/{chaveAcesso}/eventos - Registrar eventos (cancelamento, etc)
    """

    def __init__(
        self,
        ambiente: str = "2",
        cert_path: Optional[str] = None,
        cert_password: Optional[str] = None,
    ):
        """
        Inicializa o cliente NFS-e Nacional.

        Args:
            ambiente: 1=Produção, 2=Homologação
            cert_path: Caminho do certificado PFX/P12
            cert_password: Senha do certificado
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx é necessário para NFSeNacionalClient. Instale com: pip install httpx")

        self.ambiente = ambiente
        env_key = "producao" if ambiente == "1" else "homologacao"
        self.endpoints = NFSE_NACIONAL_ENDPOINTS[env_key]
        self.api_url = self.endpoints["api_url"]

        self.cert_path = cert_path
        self.cert_password = cert_password

        self._client: Optional[httpx.AsyncClient] = None
        self._cert_pem_path: Optional[str] = None
        self._key_pem_path: Optional[str] = None

        logger.info(f"NFSeNacionalClient inicializado: Ambiente={'Produção' if ambiente == '1' else 'Homologação'}")

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtém cliente HTTP com certificado mTLS."""
        if self._client is None:
            ssl_context = ssl.create_default_context()

            if self.cert_path:
                from .certificate_manager import CertificateManager
                cert_manager = CertificateManager(
                    pfx_path=self.cert_path,
                    password=self.cert_password
                )
                cert_manager.load()

                # Exportar para arquivos temporários PEM
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as cert_file:
                    cert_file.write(cert_manager.get_certificate_pem())
                    self._cert_pem_path = cert_file.name

                with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as key_file:
                    key_file.write(cert_manager.get_private_key_pem())
                    self._key_pem_path = key_file.name

                ssl_context.load_cert_chain(self._cert_pem_path, self._key_pem_path)

            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                verify=ssl_context,
                timeout=60.0,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

        return self._client

    async def close(self):
        """Fecha o cliente HTTP e limpa arquivos temporários."""
        if self._client:
            await self._client.aclose()
            self._client = None

        # Limpar arquivos temporários
        import os
        if self._cert_pem_path and os.path.exists(self._cert_pem_path):
            os.unlink(self._cert_pem_path)
        if self._key_pem_path and os.path.exists(self._key_pem_path):
            os.unlink(self._key_pem_path)

    def _compress_and_encode_xml(self, xml: str) -> str:
        """Compacta (GZip) e codifica (Base64) o XML."""
        xml_bytes = xml.encode('utf-8')
        compressed = gzip.compress(xml_bytes)
        return base64.b64encode(compressed).decode('ascii')

    def _decode_and_decompress_xml(self, encoded: str) -> str:
        """Decodifica (Base64) e descompacta (GZip) o XML."""
        compressed = base64.b64decode(encoded)
        xml_bytes = gzip.decompress(compressed)
        return xml_bytes.decode('utf-8')

    async def enviar_dps(self, dps: DPSNacional) -> NFSeNacionalResult:
        """
        Envia um DPS para gerar NFS-e.

        Args:
            dps: Declaração de Prestação de Serviços

        Returns:
            Resultado da operação
        """
        import time
        start_time = time.time()

        try:
            client = await self._get_client()

            # Montar payload JSON (formato da API Nacional)
            dps.calcular_valores()

            payload = {
                "infDPS": {
                    "tpAmb": int(self.ambiente),
                    "dhEmi": datetime.now(timezone.utc).isoformat(),
                    "verAplic": "CONECTA_PRO_1.0",
                    "dCompet": dps.data_competencia.strftime("%Y-%m"),
                    "prest": dps.prestador.to_dict() if hasattr(dps.prestador, 'to_dict') else {
                        "CNPJ": re.sub(r'[^\d]', '', dps.prestador.cnpj),
                        "IM": dps.prestador.inscricao_municipal,
                    },
                    "serv": {
                        "cServ": dps.servico.codigo_tributacao_nacional,
                        "xDescServ": dps.servico.descricao,
                    },
                    "valores": {
                        "vServPrest": float(dps.servico.valor_servico),
                        "vISS": float(dps.valor_iss or 0),
                    }
                }
            }

            if dps.tomador:
                payload["infDPS"]["toma"] = {
                    "CPF" if len(re.sub(r'[^\d]', '', dps.tomador.cpf_cnpj)) == 11 else "CNPJ": re.sub(r'[^\d]', '', dps.tomador.cpf_cnpj),
                    "xNome": dps.tomador.razao_social,
                }

            response = await client.post("/dps", json=payload)
            tempo_resposta = time.time() - start_time

            if response.status_code in [200, 201]:
                data = response.json()
                return NFSeNacionalResult(
                    sucesso=True,
                    mensagem="DPS enviado com sucesso",
                    chave_acesso=data.get("chaveAcesso"),
                    numero_nfse=data.get("numero"),
                    codigo_verificacao=data.get("codigoVerificacao"),
                    link_nfse=data.get("link"),
                    dados_retorno=data,
                    tempo_resposta=tempo_resposta
                )
            else:
                data = response.json() if "application/json" in response.headers.get("content-type", "") else {}
                return NFSeNacionalResult(
                    sucesso=False,
                    mensagem=data.get("message", f"Erro HTTP {response.status_code}"),
                    codigo=str(response.status_code),
                    dados_retorno=data,
                    tempo_resposta=tempo_resposta
                )

        except Exception as e:
            logger.error(f"Erro ao enviar DPS: {e}")
            return NFSeNacionalResult(
                sucesso=False,
                mensagem=str(e),
                tempo_resposta=time.time() - start_time
            )

    async def consultar_nfse(self, chave_acesso: str) -> NFSeNacionalResult:
        """Consulta uma NFS-e pela chave de acesso."""
        import time
        start_time = time.time()

        try:
            client = await self._get_client()
            response = await client.get(f"/nfse/{chave_acesso}")
            tempo_resposta = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                xml_nfse = None
                if "xmlNFSe" in data:
                    xml_nfse = self._decode_and_decompress_xml(data["xmlNFSe"])

                return NFSeNacionalResult(
                    sucesso=True,
                    mensagem="NFS-e encontrada",
                    chave_acesso=chave_acesso,
                    numero_nfse=data.get("numero"),
                    xml_nfse=xml_nfse,
                    dados_retorno=data,
                    tempo_resposta=tempo_resposta
                )
            else:
                return NFSeNacionalResult(
                    sucesso=False,
                    mensagem=f"Erro HTTP {response.status_code}",
                    codigo=str(response.status_code),
                    tempo_resposta=tempo_resposta
                )

        except Exception as e:
            logger.error(f"Erro ao consultar NFS-e: {e}")
            return NFSeNacionalResult(
                sucesso=False,
                mensagem=str(e),
                tempo_resposta=time.time() - start_time
            )

    async def baixar_danfse(self, chave_acesso: str) -> NFSeNacionalResult:
        """Baixa o DANFSE (PDF) de uma NFS-e."""
        import time
        start_time = time.time()

        try:
            client = await self._get_client()
            response = await client.get(f"/danfse/{chave_acesso}")
            tempo_resposta = time.time() - start_time

            if response.status_code == 200:
                return NFSeNacionalResult(
                    sucesso=True,
                    mensagem="DANFSE baixado",
                    chave_acesso=chave_acesso,
                    pdf_danfse=response.content,
                    tempo_resposta=tempo_resposta
                )
            else:
                return NFSeNacionalResult(
                    sucesso=False,
                    mensagem=f"Erro HTTP {response.status_code}",
                    tempo_resposta=tempo_resposta
                )

        except Exception as e:
            return NFSeNacionalResult(sucesso=False, mensagem=str(e), tempo_resposta=time.time() - start_time)

    async def cancelar_nfse(self, chave_acesso: str, codigo: str, motivo: str) -> NFSeNacionalResult:
        """Registra evento de cancelamento de NFS-e."""
        import time
        start_time = time.time()

        try:
            client = await self._get_client()
            payload = {"tipoEvento": "cancelamento", "codigoCancelamento": codigo, "motivo": motivo}
            response = await client.post(f"/nfse/{chave_acesso}/eventos", json=payload)
            tempo_resposta = time.time() - start_time

            if response.status_code in [200, 201]:
                return NFSeNacionalResult(
                    sucesso=True,
                    mensagem="NFS-e cancelada",
                    chave_acesso=chave_acesso,
                    dados_retorno=response.json(),
                    tempo_resposta=tempo_resposta
                )
            else:
                return NFSeNacionalResult(
                    sucesso=False,
                    mensagem=f"Erro HTTP {response.status_code}",
                    tempo_resposta=tempo_resposta
                )

        except Exception as e:
            return NFSeNacionalResult(sucesso=False, mensagem=str(e), tempo_resposta=time.time() - start_time)


logger.info("Módulo NFSeNacional carregado")
