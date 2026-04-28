"""
Cliente para CNDT — Certidao Negativa de Debitos Trabalhistas
==============================================================
Consulta de CNDT no portal do Tribunal Superior do Trabalho (TST).

A CNDT e exigida para participacao em licitacoes publicas
(Lei 12.440/2011, que alterou a CLT e a Lei 8.666/93).
Validade: 180 dias a partir da emissao.

D5.3 — Investigacao (28/04/2026): portal vivo, formulario em 2 etapas JSF.
Etapa 2 exige captcha de imagem customizado do TST (campos `resposta` +
`tokenDesafio` — `tokenDesafio` e populado via JavaScript, impossivel sem
browser headless). ROTA-FALLBACK adotada.
Backlog D5.6: Playwright para navegar fluxo JSF + captcha de imagem.
"""

import logging
import re
from datetime import datetime
from typing import Any

from modules.integrations.brasilapi.client import BrasilAPIClient
from modules.integrations.brasilapi.exceptions import (
    BrasilAPINotFoundError,
    BrasilAPIUnavailableError,
)

logger = logging.getLogger(__name__)


class CNDTTrabalhistaClient:
    """
    Cliente HTTP para consulta de CNDT no portal do TST.

    A Certidao Negativa de Debitos Trabalhistas (CNDT) e emitida
    pelo Tribunal Superior do Trabalho e comprova a inexistencia
    de debitos trabalhistas no Banco Nacional de Devedores Trabalhistas.
    """

    # URL do servico de consulta CNDT
    BASE_URL = "https://www.tst.jus.br"
    CONSULTA_URL = "https://cndt-certidao.tst.jus.br/inicio.faces"

    # Tipos de certidao trabalhista
    TIPO_CNDT = "CNDT"  # Certidao Negativa
    TIPO_CPDT_EN = "CPDT-EN"  # Certidao Positiva com Efeito de Negativa
    TIPO_CPDT = "CPDT"  # Certidao Positiva

    VALIDADE_DIAS = 180

    def _format_cnpj(self, cnpj: str) -> str:
        """Remove formatacao do CNPJ, mantendo apenas digitos."""
        return re.sub(r"\D", "", cnpj)

    async def _fallback_brasilapi(self, cnpj_limpo: str) -> dict[str, Any]:
        """
        Fallback via BrasilAPI quando portal TST indisponivel ou exige captcha.

        Principio §42.4: situacao_cadastral RFB e INDEPENDENTE de regularidade
        trabalhista no BNDT. regular=None e o unico retorno honesto nesse cenario.
        """
        try:
            cnpj_data, _ = await BrasilAPIClient().get_cnpj(cnpj_limpo)
            situacao_cadastral = (cnpj_data.descricao_situacao_cadastral or "").upper()
            cnpj_ativo = situacao_cadastral == "ATIVA"
            logger.warning(
                "CNDT TST indisponivel para %s (captcha imagem requer browser). Apenas RFB cadastral disponivel: %s",
                cnpj_limpo,
                situacao_cadastral,
            )
            return {
                "cnpj": cnpj_limpo,
                "tipo_certidao": "CNDT",
                "situacao": "indeterminado_portal_indisponivel",
                "regular": None,
                "cnpj_ativo_rfb": cnpj_ativo,
                "fonte": "BrasilAPI (fallback)",
                "nota": (
                    "Portal TST exige captcha de imagem nao solucionavel "
                    "programaticamente. Status CNDT NÃO confirmado via fonte "
                    "oficial. Apenas situacao cadastral RFB conhecida "
                    f"({'ativa' if cnpj_ativo else 'inativa'}). "
                    "Consultar manualmente em cndt-certidao.tst.jus.br."
                ),
                "consultado_em": datetime.utcnow().isoformat(),
            }
        except (BrasilAPINotFoundError, BrasilAPIUnavailableError) as e:
            logger.error("CNDT BrasilAPI fallback falhou para %s: %s", cnpj_limpo, e)
            return {
                "cnpj": cnpj_limpo,
                "tipo_certidao": None,
                "situacao": "erro_consulta",
                "regular": None,
                "fonte": "TST + BrasilAPI ambos indisponiveis",
                "mensagem": str(e),
                "consultado_em": datetime.utcnow().isoformat(),
            }

    async def consultar_cndt(self, cnpj: str) -> dict[str, Any]:
        """
        Consulta CNDT (Certidao de Debitos Trabalhistas) de um CNPJ.

        D5.3 ROTA-FALLBACK: portal TST usa captcha de imagem customizado
        (campos resposta + tokenDesafio) que requer JavaScript para popular
        tokenDesafio — impossivel sem Playwright. Fallback BrasilAPI segue
        principio §42.4 (regular=None quando fonte oficial indisponivel).
        """
        cnpj_limpo = self._format_cnpj(cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError(f"CNPJ invalido: {cnpj}. Deve conter 14 digitos.")

        logger.info("Consultando CNDT para CNPJ %s", cnpj_limpo)
        return await self._fallback_brasilapi(cnpj_limpo)

    async def verificar_regularidade(self, cnpj: str) -> dict[str, Any]:
        """
        Verifica regularidade trabalhista de um CNPJ.

        Interface consistente com CNDFederalClient e CRFFGTSClient.
        Tratamento tripartite: regular True/False/None -> apto_licitar bool/None.
        """
        resultado = await self.consultar_cndt(cnpj)
        regular = resultado.get("regular")
        return {
            "cnpj": resultado["cnpj"],
            "regular": regular,
            "tipo_certidao": resultado.get("tipo_certidao"),
            "situacao": resultado.get("situacao"),
            "data_validade": resultado.get("data_validade"),
            "apto_licitar": bool(regular) if regular is not None else None,
            "observacao": (
                "Empresa regular perante a Justica do Trabalho (BNDT)"
                if regular is True
                else "Empresa com debitos trabalhistas — verificar BNDT no TST"
                if regular is False
                else "Status CNDT indeterminado — portal TST exige captcha, "
                "consultar manualmente em cndt-certidao.tst.jus.br"
            ),
        }

    async def verificar_debitos(self, cnpj: str) -> dict[str, Any]:
        """
        Verifica existencia de debitos trabalhistas de um CNPJ.

        Mantido para compatibilidade com callers existentes.
        Delega para verificar_regularidade (tripartite §42.4).
        """
        resultado = await self.consultar_cndt(cnpj)
        regular = resultado.get("regular")
        possui_debitos = resultado.get("tipo_certidao") == self.TIPO_CPDT
        return {
            "cnpj": resultado["cnpj"],
            "possui_debitos": possui_debitos,
            "regular": regular,
            "tipo_certidao": resultado.get("tipo_certidao"),
            "situacao": resultado.get("situacao"),
            "data_validade": resultado.get("data_validade"),
            "apto_licitar": bool(regular) if regular is not None else None,
            "observacao": (
                "Empresa sem debitos trabalhistas no BNDT"
                if regular is True
                else "Empresa consta no BNDT — verificar debitos trabalhistas pendentes"
                if regular is False
                else "Status CNDT indeterminado — consultar manualmente em cndt-certidao.tst.jus.br"
            ),
            "base_legal": "Lei 12.440/2011 (Art. 29, V da Lei 8.666/93)",
        }
