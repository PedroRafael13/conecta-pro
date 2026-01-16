"""
NFS-e Padrão Nacional - Preparação para Migração.

O Padrão Nacional de NFS-e está substituindo gradualmente os padrões municipais
(como ABRASF usado em Manaus). A migração está prevista para 2026.

Portal: https://www.gov.br/nfse
Documentação: https://www.gov.br/nfse/pt-br/acesso-a-informacao/manuais

Características do Padrão Nacional:
- Ambiente único de dados (AUD)
- Webservice REST/JSON (não mais SOAP/XML)
- Autenticação via certificado digital e Gov.br
- Número único nacional da NFS-e
- Integração com eSocial e DCTFWeb
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


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
