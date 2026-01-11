"""
Service para integrações com eSocial.
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, "/opt/conecta-pro")

from government_integrations import (
    get_esocial_transmitter,
    ESocialEnvironment,
)

logger = logging.getLogger(__name__)


class ESocialService:
    """Service para operações com eSocial."""

    # Eventos suportados
    EVENTOS_SUPORTADOS: List[Dict[str, str]] = [
        {
            "codigo": "S-2200",
            "nome": "Cadastramento Inicial do Vinculo e Admissao",
            "descricao": "Evento de admissao de funcionario",
        },
        {
            "codigo": "S-2205",
            "nome": "Alteracao de Dados Cadastrais",
            "descricao": "Alteracao de dados do funcionario",
        },
        {
            "codigo": "S-2206",
            "nome": "Alteracao de Contrato de Trabalho",
            "descricao": "Alteracao de condicoes contratuais",
        },
        {
            "codigo": "S-2210",
            "nome": "Comunicacao de Acidente de Trabalho",
            "descricao": "CAT - Comunicacao de Acidente",
        },
        {
            "codigo": "S-2220",
            "nome": "Monitoramento da Saude do Trabalhador",
            "descricao": "ASO - Atestado de Saude Ocupacional",
        },
        {
            "codigo": "S-2230",
            "nome": "Afastamento Temporario",
            "descricao": "Afastamentos (ferias, licencas, etc)",
        },
        {
            "codigo": "S-2240",
            "nome": "Condicoes Ambientais do Trabalho",
            "descricao": "Fatores de risco e EPIs",
        },
        {
            "codigo": "S-2299",
            "nome": "Desligamento",
            "descricao": "Evento de demissao/desligamento",
        },
    ]

    @staticmethod
    def enviar_evento(
        tipo_evento: str,
        funcionario_id: str,
        dados: Dict[str, Any],
        ambiente: str = "homologacao",
    ) -> Dict[str, Any]:
        """
        Envia evento para o eSocial.

        Args:
            tipo_evento: Tipo do evento eSocial.
            funcionario_id: ID do funcionário.
            dados: Dados específicos do evento.
            ambiente: Ambiente (producao ou homologacao).

        Returns:
            Dict com protocolo de transmissão.

        Raises:
            ValueError: Se dados inválidos.
        """
        esocial = get_esocial_transmitter()
        ambiente_enum = ESocialEnvironment(ambiente.upper())

        resultado = esocial.transmit_event(
            event_type=tipo_evento,
            funcionario_id=funcionario_id,
            dados=dados,
            ambiente=ambiente_enum,
        )

        logger.info(
            "Evento eSocial enviado: tipo=%s, funcionario=%s",
            tipo_evento,
            funcionario_id,
        )

        return {
            "protocolo": resultado.get("protocolo"),
            "tipo_evento": tipo_evento,
            "funcionario_id": funcionario_id,
            "ambiente": ambiente,
            "status": "enviado",
            "data_transmissao": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def consultar_status(protocolo: str) -> Dict[str, Any]:
        """
        Consulta status de evento eSocial.

        Args:
            protocolo: Protocolo de transmissão.

        Returns:
            Dict com status do evento.

        Raises:
            ValueError: Se protocolo não encontrado.
        """
        esocial = get_esocial_transmitter()
        status_info = esocial.get_event_status(protocolo)

        return {
            "protocolo": protocolo,
            "status": status_info.get("status"),
            "recibo": status_info.get("recibo"),
            "erros": status_info.get("erros"),
            "data_processamento": status_info.get("data_processamento"),
        }

    @classmethod
    def listar_eventos_suportados(cls) -> Dict[str, Any]:
        """
        Lista eventos eSocial suportados.

        Returns:
            Dict com lista de eventos.
        """
        return {
            "eventos": cls.EVENTOS_SUPORTADOS,
            "ambiente_producao": "Requer certificado digital A1/A3",
            "ambiente_homologacao": "Disponivel para testes",
        }
