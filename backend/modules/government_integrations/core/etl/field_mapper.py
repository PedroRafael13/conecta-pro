"""
Mapeador de Campos para documentos fiscais.

Define mapeamentos de XML/JSON para modelos internos.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import logging

from .normalizer import NormalizadorDados

logger = logging.getLogger(__name__)


# =============================================================================
# MAPEAMENTOS DE CAMPOS
# =============================================================================

# NF-e / NFC-e (modelo 55/65)
MAPEAMENTO_NFE: Dict[str, str] = {
    # Identificação
    "ide/cUF": "uf_codigo",
    "ide/cNF": "codigo_numerico",
    "ide/natOp": "natureza_operacao",
    "ide/mod": "modelo",
    "ide/serie": "serie",
    "ide/nNF": "numero",
    "ide/dhEmi": "data_emissao",
    "ide/dhSaiEnt": "data_saida_entrada",
    "ide/tpNF": "tipo",  # 0=Entrada, 1=Saída
    "ide/idDest": "destino_operacao",
    "ide/cMunFG": "municipio_fato_gerador",
    "ide/tpImp": "formato_impressao",
    "ide/tpEmis": "tipo_emissao",
    "ide/finNFe": "finalidade",
    "ide/indFinal": "consumidor_final",
    "ide/indPres": "presenca_comprador",

    # Emitente
    "emit/CNPJ": "emitente_cnpj",
    "emit/CPF": "emitente_cpf",
    "emit/xNome": "emitente_razao_social",
    "emit/xFant": "emitente_fantasia",
    "emit/IE": "emitente_ie",
    "emit/IEST": "emitente_ie_st",
    "emit/CRT": "emitente_crt",
    "emit/enderEmit/xLgr": "emitente_logradouro",
    "emit/enderEmit/nro": "emitente_numero",
    "emit/enderEmit/xBairro": "emitente_bairro",
    "emit/enderEmit/cMun": "emitente_municipio_codigo",
    "emit/enderEmit/xMun": "emitente_municipio",
    "emit/enderEmit/UF": "emitente_uf",
    "emit/enderEmit/CEP": "emitente_cep",

    # Destinatário
    "dest/CNPJ": "destinatario_cnpj",
    "dest/CPF": "destinatario_cpf",
    "dest/idEstrangeiro": "destinatario_id_estrangeiro",
    "dest/xNome": "destinatario_nome",
    "dest/indIEDest": "destinatario_indicador_ie",
    "dest/IE": "destinatario_ie",
    "dest/email": "destinatario_email",
    "dest/enderDest/xLgr": "destinatario_logradouro",
    "dest/enderDest/nro": "destinatario_numero",
    "dest/enderDest/xBairro": "destinatario_bairro",
    "dest/enderDest/cMun": "destinatario_municipio_codigo",
    "dest/enderDest/xMun": "destinatario_municipio",
    "dest/enderDest/UF": "destinatario_uf",
    "dest/enderDest/CEP": "destinatario_cep",

    # Totais
    "total/ICMSTot/vBC": "base_calculo_icms",
    "total/ICMSTot/vICMS": "valor_icms",
    "total/ICMSTot/vICMSDeson": "valor_icms_desonerado",
    "total/ICMSTot/vFCPUFDest": "valor_fcp_uf_dest",
    "total/ICMSTot/vICMSUFDest": "valor_icms_uf_dest",
    "total/ICMSTot/vICMSUFRemet": "valor_icms_uf_remet",
    "total/ICMSTot/vFCP": "valor_fcp",
    "total/ICMSTot/vBCST": "base_calculo_st",
    "total/ICMSTot/vST": "valor_st",
    "total/ICMSTot/vFCPST": "valor_fcp_st",
    "total/ICMSTot/vFCPSTRet": "valor_fcp_st_ret",
    "total/ICMSTot/vProd": "valor_produtos",
    "total/ICMSTot/vFrete": "valor_frete",
    "total/ICMSTot/vSeg": "valor_seguro",
    "total/ICMSTot/vDesc": "valor_desconto",
    "total/ICMSTot/vII": "valor_ii",
    "total/ICMSTot/vIPI": "valor_ipi",
    "total/ICMSTot/vIPIDevol": "valor_ipi_devolvido",
    "total/ICMSTot/vPIS": "valor_pis",
    "total/ICMSTot/vCOFINS": "valor_cofins",
    "total/ICMSTot/vOutro": "valor_outros",
    "total/ICMSTot/vNF": "valor_total",
    "total/ICMSTot/vTotTrib": "valor_total_tributos",

    # Protocolo
    "protNFe/infProt/tpAmb": "ambiente",
    "protNFe/infProt/verAplic": "versao_aplicativo",
    "protNFe/infProt/chNFe": "chave_acesso",
    "protNFe/infProt/dhRecbto": "data_autorizacao",
    "protNFe/infProt/nProt": "protocolo",
    "protNFe/infProt/digVal": "digest_value",
    "protNFe/infProt/cStat": "codigo_status",
    "protNFe/infProt/xMotivo": "motivo_status",
}

# CT-e (modelo 57)
MAPEAMENTO_CTE: Dict[str, str] = {
    # Identificação
    "ide/cUF": "uf_codigo",
    "ide/cCT": "codigo_numerico",
    "ide/CFOP": "cfop",
    "ide/natOp": "natureza_operacao",
    "ide/mod": "modelo",
    "ide/serie": "serie",
    "ide/nCT": "numero",
    "ide/dhEmi": "data_emissao",
    "ide/tpImp": "formato_impressao",
    "ide/tpEmis": "tipo_emissao",
    "ide/tpCTe": "tipo_cte",
    "ide/tpServ": "tipo_servico",
    "ide/cMunEnv": "municipio_envio",
    "ide/cMunIni": "municipio_inicio",
    "ide/cMunFim": "municipio_fim",

    # Emitente
    "emit/CNPJ": "emitente_cnpj",
    "emit/IE": "emitente_ie",
    "emit/xNome": "emitente_razao_social",
    "emit/xFant": "emitente_fantasia",

    # Remetente
    "rem/CNPJ": "remetente_cnpj",
    "rem/CPF": "remetente_cpf",
    "rem/xNome": "remetente_nome",

    # Destinatário
    "dest/CNPJ": "destinatario_cnpj",
    "dest/CPF": "destinatario_cpf",
    "dest/xNome": "destinatario_nome",

    # Valores
    "vPrest/vTPrest": "valor_total_prestacao",
    "vPrest/vRec": "valor_receber",

    # Protocolo
    "protCTe/infProt/chCTe": "chave_acesso",
    "protCTe/infProt/dhRecbto": "data_autorizacao",
    "protCTe/infProt/nProt": "protocolo",
    "protCTe/infProt/cStat": "codigo_status",
}

# NFS-e (padrão ABRASF)
MAPEAMENTO_NFSE: Dict[str, str] = {
    # Identificação
    "InfNfse/Numero": "numero",
    "InfNfse/CodigoVerificacao": "codigo_verificacao",
    "InfNfse/DataEmissao": "data_emissao",
    "InfNfse/NaturezaOperacao": "natureza_operacao",
    "InfNfse/OptanteSimplesNacional": "optante_simples",
    "InfNfse/IncentivadorCultural": "incentivador_cultural",

    # Prestador
    "InfNfse/PrestadorServico/IdentificacaoPrestador/Cnpj": "prestador_cnpj",
    "InfNfse/PrestadorServico/IdentificacaoPrestador/InscricaoMunicipal": "prestador_im",
    "InfNfse/PrestadorServico/RazaoSocial": "prestador_razao_social",
    "InfNfse/PrestadorServico/NomeFantasia": "prestador_fantasia",

    # Tomador
    "InfNfse/TomadorServico/IdentificacaoTomador/CpfCnpj/Cnpj": "tomador_cnpj",
    "InfNfse/TomadorServico/IdentificacaoTomador/CpfCnpj/Cpf": "tomador_cpf",
    "InfNfse/TomadorServico/RazaoSocial": "tomador_razao_social",

    # Serviço
    "InfNfse/Servico/ItemListaServico": "codigo_servico",
    "InfNfse/Servico/CodigoCnae": "cnae",
    "InfNfse/Servico/Discriminacao": "discriminacao",
    "InfNfse/Servico/CodigoMunicipio": "municipio_prestacao",

    # Valores
    "InfNfse/Servico/Valores/ValorServicos": "valor_servicos",
    "InfNfse/Servico/Valores/ValorDeducoes": "valor_deducoes",
    "InfNfse/Servico/Valores/ValorPis": "valor_pis",
    "InfNfse/Servico/Valores/ValorCofins": "valor_cofins",
    "InfNfse/Servico/Valores/ValorInss": "valor_inss",
    "InfNfse/Servico/Valores/ValorIr": "valor_ir",
    "InfNfse/Servico/Valores/ValorCsll": "valor_csll",
    "InfNfse/Servico/Valores/IssRetido": "iss_retido",
    "InfNfse/Servico/Valores/ValorIss": "valor_iss",
    "InfNfse/Servico/Valores/BaseCalculo": "base_calculo",
    "InfNfse/Servico/Valores/Aliquota": "aliquota_iss",
    "InfNfse/Servico/Valores/ValorLiquidoNfse": "valor_liquido",
}

# eSocial
MAPEAMENTO_ESOCIAL: Dict[str, str] = {
    # Identificação do evento
    "ideEvento/tpAmb": "ambiente",
    "ideEvento/procEmi": "processo_emissao",
    "ideEvento/verProc": "versao_processo",

    # Empregador
    "ideEmpregador/tpInsc": "tipo_inscricao",
    "ideEmpregador/nrInsc": "numero_inscricao",

    # Trabalhador (quando aplicável)
    "ideTrabalhador/cpfTrab": "trabalhador_cpf",
    "ideTrabalhador/nisTrab": "trabalhador_nis",

    # Recibo
    "recibo/nrRecibo": "numero_recibo",
    "recibo/dhRecepcao": "data_recepcao",
    "recibo/versaoAppRecepcao": "versao_recepcao",
    "recibo/protocoloEnvioLote": "protocolo_lote",
}

# FGTS Digital
MAPEAMENTO_FGTS: Dict[str, str] = {
    # Trabalhador
    "trabalhador/cpf": "trabalhador_cpf",
    "trabalhador/pis": "trabalhador_pis",
    "trabalhador/nome": "trabalhador_nome",
    "trabalhador/dataNascimento": "trabalhador_nascimento",
    "trabalhador/dataAdmissao": "trabalhador_admissao",

    # Competência
    "competencia/anoMes": "competencia",

    # Remuneração
    "remuneracao/valor": "remuneracao_bruta",
    "remuneracao/categoria": "categoria_trabalhador",

    # FGTS
    "fgts/baseCalculo": "base_calculo_fgts",
    "fgts/aliquota": "aliquota_fgts",
    "fgts/valorDeposito": "valor_fgts",
    "fgts/valorMulta": "valor_multa",

    # Guia
    "guia/numero": "numero_guia",
    "guia/codigoBarras": "codigo_barras",
    "guia/linhaDigitavel": "linha_digitavel",
    "guia/dataVencimento": "data_vencimento",
    "guia/valorTotal": "valor_guia",
}


# =============================================================================
# MAPEADOR DE CAMPOS
# =============================================================================

@dataclass
class ConfigMapeamento:
    """Configuração de mapeamento."""
    mapeamento: Dict[str, str]
    campos_obrigatorios: List[str] = field(default_factory=list)
    normalizadores: Dict[str, Callable] = field(default_factory=dict)


class MapeadorCampos:
    """
    Mapeia campos de XML/JSON para modelo interno.
    """

    # Normalizadores padrão por tipo de campo
    NORMALIZADORES_PADRAO: Dict[str, Callable] = {
        "cnpj": NormalizadorDados.normalizar_cnpj,
        "cpf": NormalizadorDados.normalizar_cpf,
        "ie": NormalizadorDados.normalizar_ie,
        "data": NormalizadorDados.normalizar_data,
        "valor": NormalizadorDados.normalizar_valor,
        "chave": NormalizadorDados.normalizar_chave_acesso,
        "cep": NormalizadorDados.normalizar_cep,
        "codigo_municipio": NormalizadorDados.normalizar_codigo_municipio,
        "ncm": NormalizadorDados.normalizar_ncm,
    }

    # Padrões de campos para auto-detecção de normalizador
    PADROES_CAMPOS = {
        r"_cnpj$|^cnpj$": "cnpj",
        r"_cpf$|^cpf$": "cpf",
        r"_ie$|^ie$": "ie",
        r"data_|_data$|^data$": "data",
        r"valor_|_valor$|^valor$|^base_|_base$": "valor",
        r"chave_acesso": "chave",
        r"_cep$|^cep$": "cep",
        r"municipio_codigo|codigo_municipio": "codigo_municipio",
        r"^ncm$": "ncm",
    }

    def __init__(
        self,
        tipo_documento: str,
        mapeamento_custom: Optional[Dict[str, str]] = None
    ):
        """
        Inicializa mapeador.

        Args:
            tipo_documento: Tipo do documento (nfe, cte, nfse, esocial, fgts)
            mapeamento_custom: Mapeamento customizado (opcional)
        """
        self.tipo_documento = tipo_documento

        # Selecionar mapeamento
        mapeamentos = {
            "nfe": MAPEAMENTO_NFE,
            "nfce": MAPEAMENTO_NFE,
            "cte": MAPEAMENTO_CTE,
            "nfse": MAPEAMENTO_NFSE,
            "esocial": MAPEAMENTO_ESOCIAL,
            "fgts": MAPEAMENTO_FGTS,
        }

        base = mapeamentos.get(tipo_documento.lower(), {})
        self.mapeamento = {**base, **(mapeamento_custom or {})}

    def mapear_xml(
        self,
        xml_content: bytes,
        namespaces: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Mapeia XML para dicionário usando mapeamento definido.

        Args:
            xml_content: Conteúdo XML em bytes
            namespaces: Namespaces XML (opcional)

        Returns:
            Dicionário com campos mapeados e normalizados
        """
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML: {e}")
            raise ValueError(f"XML inválido: {e}")

        resultado = {}

        for xpath, campo_destino in self.mapeamento.items():
            # Tentar encontrar elemento
            elemento = root.find(f".//{xpath}", namespaces)

            if elemento is not None and elemento.text:
                valor = elemento.text.strip()

                # Aplicar normalizador
                valor_normalizado = self._normalizar_campo(campo_destino, valor)
                resultado[campo_destino] = valor_normalizado

        return resultado

    def mapear_dict(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dicionário para modelo interno.

        Args:
            dados: Dicionário com dados originais

        Returns:
            Dicionário com campos mapeados e normalizados
        """
        resultado = {}

        for caminho, campo_destino in self.mapeamento.items():
            # Navegar pelo caminho (suporta "a/b/c")
            partes = caminho.split("/")
            valor = dados

            for parte in partes:
                if isinstance(valor, dict):
                    valor = valor.get(parte)
                else:
                    valor = None
                    break

            if valor is not None:
                valor_normalizado = self._normalizar_campo(campo_destino, valor)
                resultado[campo_destino] = valor_normalizado

        return resultado

    def _normalizar_campo(self, nome_campo: str, valor: Any) -> Any:
        """
        Aplica normalizador apropriado ao campo.
        """
        import re

        # Detectar tipo de normalizador pelo nome do campo
        for padrao, tipo in self.PADROES_CAMPOS.items():
            if re.search(padrao, nome_campo, re.IGNORECASE):
                normalizador = self.NORMALIZADORES_PADRAO.get(tipo)
                if normalizador:
                    try:
                        return normalizador(valor)
                    except Exception as e:
                        logger.warning(
                            f"Erro ao normalizar {nome_campo}: {e}"
                        )
                        return valor

        return valor

    @classmethod
    def extrair_itens_nfe(
        cls,
        xml_content: bytes,
        namespaces: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extrai itens de uma NF-e.

        Args:
            xml_content: Conteúdo XML
            namespaces: Namespaces

        Returns:
            Lista de itens com campos normalizados
        """
        root = ET.fromstring(xml_content)
        itens = []

        for det in root.findall(".//det", namespaces):
            item = {
                "numero_item": det.get("nItem"),
            }

            # Produto
            prod = det.find("prod", namespaces)
            if prod is not None:
                item.update({
                    "codigo": prod.findtext("cProd", namespaces=namespaces),
                    "ean": prod.findtext("cEAN", namespaces=namespaces),
                    "descricao": prod.findtext("xProd", namespaces=namespaces),
                    "ncm": NormalizadorDados.normalizar_ncm(
                        prod.findtext("NCM", namespaces=namespaces)
                    ),
                    "cfop": prod.findtext("CFOP", namespaces=namespaces),
                    "unidade": prod.findtext("uCom", namespaces=namespaces),
                    "quantidade": NormalizadorDados.normalizar_valor(
                        prod.findtext("qCom", namespaces=namespaces), 4
                    ),
                    "valor_unitario": NormalizadorDados.normalizar_valor(
                        prod.findtext("vUnCom", namespaces=namespaces), 4
                    ),
                    "valor_total": NormalizadorDados.normalizar_valor(
                        prod.findtext("vProd", namespaces=namespaces)
                    ),
                })

            # Impostos
            imposto = det.find("imposto", namespaces)
            if imposto is not None:
                icms = imposto.find(".//ICMS", namespaces)
                if icms is not None:
                    # Pegar primeiro elemento filho (ICMS00, ICMS10, etc)
                    icms_det = list(icms)[0] if list(icms) else None
                    if icms_det is not None:
                        item["cst_icms"] = icms_det.findtext("CST", namespaces=namespaces)
                        item["base_icms"] = NormalizadorDados.normalizar_valor(
                            icms_det.findtext("vBC", namespaces=namespaces)
                        )
                        item["aliquota_icms"] = NormalizadorDados.normalizar_valor(
                            icms_det.findtext("pICMS", namespaces=namespaces)
                        )
                        item["valor_icms"] = NormalizadorDados.normalizar_valor(
                            icms_det.findtext("vICMS", namespaces=namespaces)
                        )

            itens.append(item)

        return itens
