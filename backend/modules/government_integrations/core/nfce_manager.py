"""
Module: NFCEManager
Description: Sistema de emissao de NFC-e (Nota Fiscal de Consumidor Eletronica)
             Modelo 65 - Vendas ao consumidor final
Author: Conecta PRO
Date: 2026-01-17
"""

import hashlib
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Optional, Any
from urllib.parse import quote
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging

from .sefaz_manager import (
    NotaFiscal, DocumentType, DocumentStatus, OperationType,
    Emitente, Destinatario, Produto, Pagamento, PaymentType,
    ContingencyType, NFEXMLBuilder, UF_CONFIGS
)

logger = logging.getLogger(__name__)


# URLs base do QR Code NFC-e por UF
NFCE_QRCODE_URL = {
    # Homologação
    "AM_HOM": "https://homnfce.sefaz.am.gov.br/nfce/consultarNFCe.jsp",
    "SP_HOM": "https://homologacao.nfce.fazenda.sp.gov.br/NFCeConsultaPublica/Paginas/ConsultaQRCode.aspx",
    "MG_HOM": "https://hinternet.fazenda.mg.gov.br/nfce/qrcode",
    "RS_HOM": "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx",
    "PR_HOM": "http://www.fazenda.pr.gov.br/nfce/qrcode",
    "BA_HOM": "http://hnfe.sefaz.ba.gov.br/servicos/nfce/modulos/geral/NFCEC_consulta_chave_acesso.aspx",
    "GO_HOM": "http://homolog.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe",
    "MT_HOM": "https://homologacao.sefaz.mt.gov.br/nfce/consultanfce",
    "MS_HOM": "http://www.dfe.ms.gov.br/nfce/qrcode",
    "PE_HOM": "http://nfcehomolog.sefaz.pe.gov.br/nfce/consulta",
    "RJ_HOM": "http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode",
    "CE_HOM": "http://nfceh.sefaz.ce.gov.br/pages/ShowNFCe.html",

    # Produção
    "AM_PROD": "https://sistemas.sefaz.am.gov.br/nfceweb/consultarNFCe.jsp",
    "SP_PROD": "https://www.nfce.fazenda.sp.gov.br/NFCeConsultaPublica/Paginas/ConsultaQRCode.aspx",
    "MG_PROD": "https://portalsped.fazenda.mg.gov.br/portalnfce/sistema/qrcode.xhtml",
    "RS_PROD": "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx",
    "PR_PROD": "http://www.fazenda.pr.gov.br/nfce/qrcode",
    "BA_PROD": "http://nfe.sefaz.ba.gov.br/servicos/nfce/modulos/geral/NFCEC_consulta_chave_acesso.aspx",
    "GO_PROD": "http://www.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe",
    "MT_PROD": "https://www.sefaz.mt.gov.br/nfce/consultanfce",
    "MS_PROD": "http://www.dfe.ms.gov.br/nfce/qrcode",
    "PE_PROD": "http://nfce.sefaz.pe.gov.br/nfce/consulta",
    "RJ_PROD": "http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode",
    "CE_PROD": "http://nfce.sefaz.ce.gov.br/pages/ShowNFCe.html",
}

# URLs de consulta pela chave
NFCE_URL_CHAVE = {
    "AM_HOM": "https://homnfce.sefaz.am.gov.br/nfce/consultarNFCe.jsp",
    "AM_PROD": "https://sistemas.sefaz.am.gov.br/nfceweb/consultarNFCe.jsp",
    "SP_HOM": "https://homologacao.nfce.fazenda.sp.gov.br/NFCeConsultaPublica",
    "SP_PROD": "https://www.nfce.fazenda.sp.gov.br/NFCeConsultaPublica",
}

# Endpoints NFC-e por UF
NFCE_ENDPOINTS = {
    "AM_HOM": {
        "NfceAutorizacao": "https://homnfce.sefaz.am.gov.br/nfce-services/services/NfeAutorizacao4",
        "NfceRetAutorizacao": "https://homnfce.sefaz.am.gov.br/nfce-services/services/NfeRetAutorizacao4",
        "NfceConsultaProtocolo": "https://homnfce.sefaz.am.gov.br/nfce-services/services/NfeConsulta4",
        "NfceInutilizacao": "https://homnfce.sefaz.am.gov.br/nfce-services/services/NfeInutilizacao4",
        "NfceStatusServico": "https://homnfce.sefaz.am.gov.br/nfce-services/services/NfeStatusServico4",
        "NfceRecepcaoEvento": "https://homnfce.sefaz.am.gov.br/nfce-services/services/RecepcaoEvento4",
    },
    "AM_PROD": {
        "NfceAutorizacao": "https://nfce.sefaz.am.gov.br/nfce-services/services/NfeAutorizacao4",
        "NfceRetAutorizacao": "https://nfce.sefaz.am.gov.br/nfce-services/services/NfeRetAutorizacao4",
        "NfceConsultaProtocolo": "https://nfce.sefaz.am.gov.br/nfce-services/services/NfeConsulta4",
        "NfceInutilizacao": "https://nfce.sefaz.am.gov.br/nfce-services/services/NfeInutilizacao4",
        "NfceStatusServico": "https://nfce.sefaz.am.gov.br/nfce-services/services/NfeStatusServico4",
        "NfceRecepcaoEvento": "https://nfce.sefaz.am.gov.br/nfce-services/services/RecepcaoEvento4",
    },
    # Adicionar outros estados conforme necessário
}


class NFCEQRCodeGenerator:
    """Gerador de QR Code para NFC-e."""

    def __init__(self, uf: str, ambiente: str = "2", csc_id: str = "", csc_token: str = ""):
        """
        Inicializa o gerador de QR Code.

        Args:
            uf: UF do emitente
            ambiente: 1=Produção, 2=Homologação
            csc_id: ID do CSC (Código de Segurança do Contribuinte)
            csc_token: Token do CSC
        """
        self.uf = uf
        self.ambiente = ambiente
        self.csc_id = csc_id
        self.csc_token = csc_token

        env_suffix = "PROD" if ambiente == "1" else "HOM"
        self.qrcode_url = NFCE_QRCODE_URL.get(f"{uf}_{env_suffix}", "")
        self.url_chave = NFCE_URL_CHAVE.get(f"{uf}_{env_suffix}", "")

    def generate_qrcode_url(
        self,
        chave_acesso: str,
        dh_emi: str,
        valor_total: Decimal,
        valor_icms: Decimal,
        dig_val: str,
        cpf_cnpj_dest: Optional[str] = None
    ) -> str:
        """
        Gera a URL do QR Code da NFC-e.

        Formato:
        URL?p=chNFe|nVersao|tpAmb|cDest|dhEmi|vNF|vICMS|digVal|cIdToken|cHashQRCode

        Args:
            chave_acesso: Chave de acesso da NFC-e (44 dígitos)
            dh_emi: Data/hora de emissão (formato ISO com timezone)
            valor_total: Valor total da NFC-e
            valor_icms: Valor do ICMS
            dig_val: Digest Value da assinatura
            cpf_cnpj_dest: CPF/CNPJ do destinatário (opcional)

        Returns:
            URL completa do QR Code
        """
        n_versao = "2"  # Versão do QR Code

        # Formatar valores
        v_nf = f"{valor_total:.2f}"
        v_icms = f"{valor_icms:.2f}"

        # Destino (CPF se houver)
        c_dest = ""
        if cpf_cnpj_dest:
            c_dest = re.sub(r'[^\d]', '', cpf_cnpj_dest)

        # dhEmi em hexadecimal (sem timezone para QR)
        # Formato: AAAA-MM-DDTHH:MM:SS-03:00 -> hex
        dh_emi_hex = dh_emi.encode('utf-8').hex().upper()

        # Montar string para hash
        # chNFe|nVersao|tpAmb|cDest|dhEmi|vNF|vICMS|digVal|cIdToken
        params = f"{chave_acesso}|{n_versao}|{self.ambiente}|{c_dest}|{dh_emi_hex}|{v_nf}|{v_icms}|{dig_val}|{self.csc_id}"

        # Gerar hash SHA1 com CSC
        hash_input = params + self.csc_token
        c_hash_qrcode = hashlib.sha1(hash_input.encode('utf-8')).hexdigest().upper()

        # URL final
        qrcode_data = f"{params}|{c_hash_qrcode}"
        qrcode_url = f"{self.qrcode_url}?p={quote(qrcode_data)}"

        return qrcode_url

    def get_url_chave(self) -> str:
        """Retorna a URL de consulta pela chave."""
        return self.url_chave


class NFCEXMLBuilder(NFEXMLBuilder):
    """Builder de XML específico para NFC-e."""

    def __init__(self, csc_id: str = "", csc_token: str = ""):
        """
        Inicializa o builder de NFC-e.

        Args:
            csc_id: ID do CSC
            csc_token: Token do CSC
        """
        super().__init__()
        self.csc_id = csc_id
        self.csc_token = csc_token

    def build_nfce(self, nf: NotaFiscal, ambiente: str = "2") -> str:
        """
        Constroi XML da NFC-e.

        Args:
            nf: NotaFiscal com dados
            ambiente: 1=Produção, 2=Homologação

        Returns:
            XML da NFC-e
        """
        # Garantir que é NFC-e
        nf.tipo = DocumentType.NFCE

        # Gera chave de acesso se não existir
        if not nf.chave_acesso:
            nf.generate_chave_acesso()

        root = ET.Element("NFe", xmlns=self.NAMESPACE)
        inf = ET.SubElement(root, "infNFe", Id=f"NFe{nf.chave_acesso}", versao=self.VERSION)

        # ide - Identificação (específico NFC-e)
        ide = ET.SubElement(inf, "ide")
        uf_config = UF_CONFIGS.get(nf.emitente.endereco.uf)
        ET.SubElement(ide, "cUF").text = uf_config.code if uf_config else "13"
        ET.SubElement(ide, "cNF").text = nf.chave_acesso[35:43]
        ET.SubElement(ide, "natOp").text = nf.natureza_operacao or "VENDA"
        ET.SubElement(ide, "mod").text = "65"  # Modelo NFC-e
        ET.SubElement(ide, "serie").text = str(nf.serie)
        ET.SubElement(ide, "nNF").text = str(nf.numero)

        # Timezone
        uf_timezone_offset = {
            "AC": -5, "AM": -4, "AP": -3, "PA": -3,
            "RO": -4, "RR": -4, "TO": -3, "MT": -4,
        }.get(nf.emitente.endereco.uf, -3)
        uf_timezone_str = f"{uf_timezone_offset:+03d}:00"

        data_emissao = nf.data_emissao
        if data_emissao.tzinfo is None:
            data_emissao = data_emissao + timedelta(hours=uf_timezone_offset)
        else:
            uf_tz = timezone(timedelta(hours=uf_timezone_offset))
            data_emissao = data_emissao.astimezone(uf_tz)

        dh_emi = data_emissao.strftime(f"%Y-%m-%dT%H:%M:%S{uf_timezone_str}")
        ET.SubElement(ide, "dhEmi").text = dh_emi
        ET.SubElement(ide, "tpNF").text = "1"  # Saída
        ET.SubElement(ide, "idDest").text = "1"  # Operação interna
        ET.SubElement(ide, "cMunFG").text = nf.emitente.endereco.codigo_municipio
        ET.SubElement(ide, "tpImp").text = "4"  # DANFE NFC-e
        ET.SubElement(ide, "tpEmis").text = nf.contingency_type.value if nf.contingency_type else "1"
        ET.SubElement(ide, "cDV").text = nf.chave_acesso[-1]
        ET.SubElement(ide, "tpAmb").text = ambiente
        ET.SubElement(ide, "finNFe").text = "1"  # Normal
        ET.SubElement(ide, "indFinal").text = "1"  # Consumidor final (obrigatório NFC-e)
        ET.SubElement(ide, "indPres").text = "1"  # Presencial (obrigatório NFC-e)
        ET.SubElement(ide, "procEmi").text = "0"
        ET.SubElement(ide, "verProc").text = "CONECTA_PRO_1.0"

        # emit - Emitente
        emit = ET.SubElement(inf, "emit")
        ET.SubElement(emit, "CNPJ").text = re.sub(r'[^\d]', '', nf.emitente.cnpj)
        ET.SubElement(emit, "xNome").text = nf.emitente.razao_social
        if nf.emitente.nome_fantasia:
            ET.SubElement(emit, "xFant").text = nf.emitente.nome_fantasia
        self._add_endereco(emit, "enderEmit", nf.emitente.endereco)
        ET.SubElement(emit, "IE").text = nf.emitente.inscricao_estadual
        ET.SubElement(emit, "CRT").text = nf.emitente.regime_tributario

        # dest - Destinatário (opcional na NFC-e)
        if nf.destinatario and nf.destinatario.cpf_cnpj:
            dest = ET.SubElement(inf, "dest")
            doc = re.sub(r'[^\d]', '', nf.destinatario.cpf_cnpj)
            if len(doc) == 11:
                ET.SubElement(dest, "CPF").text = doc
            else:
                ET.SubElement(dest, "CNPJ").text = doc

            # Nome opcional, mas se identificado usar nome de homologação
            if ambiente == "2":
                ET.SubElement(dest, "xNome").text = "NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"
            elif nf.destinatario.nome:
                ET.SubElement(dest, "xNome").text = nf.destinatario.nome

            ET.SubElement(dest, "indIEDest").text = "9"  # Não contribuinte

        # det - Produtos
        for i, produto in enumerate(nf.produtos, 1):
            det = ET.SubElement(inf, "det", nItem=str(i))
            prod = ET.SubElement(det, "prod")
            ET.SubElement(prod, "cProd").text = produto.codigo
            ET.SubElement(prod, "cEAN").text = produto.ean or "SEM GTIN"

            # Descrição em homologação
            if ambiente == "2":
                ET.SubElement(prod, "xProd").text = "NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"
            else:
                ET.SubElement(prod, "xProd").text = produto.descricao

            ET.SubElement(prod, "NCM").text = produto.ncm
            if produto.cest:
                ET.SubElement(prod, "CEST").text = produto.cest
            ET.SubElement(prod, "CFOP").text = produto.cfop or "5102"
            ET.SubElement(prod, "uCom").text = produto.unidade
            ET.SubElement(prod, "qCom").text = f"{produto.quantidade:.4f}"
            ET.SubElement(prod, "vUnCom").text = f"{produto.valor_unitario:.10f}"
            ET.SubElement(prod, "vProd").text = f"{produto.valor_total:.2f}"
            ET.SubElement(prod, "cEANTrib").text = produto.ean or "SEM GTIN"
            ET.SubElement(prod, "uTrib").text = produto.unidade
            ET.SubElement(prod, "qTrib").text = f"{produto.quantidade:.4f}"
            ET.SubElement(prod, "vUnTrib").text = f"{produto.valor_unitario:.10f}"
            ET.SubElement(prod, "indTot").text = "1"

            # Impostos
            imposto = ET.SubElement(det, "imposto")

            # ICMS
            self._add_icms_nfce(imposto, produto, nf.emitente.regime_tributario)

            # PIS
            self._add_pis(imposto, produto)

            # COFINS
            self._add_cofins(imposto, produto)

        # total
        total = ET.SubElement(inf, "total")
        icms_tot = ET.SubElement(total, "ICMSTot")
        is_simples = nf.emitente.regime_tributario in ["1", "2"]
        ET.SubElement(icms_tot, "vBC").text = "0.00" if is_simples else f"{nf.valor_total_produtos:.2f}"
        ET.SubElement(icms_tot, "vICMS").text = "0.00" if is_simples else f"{nf.valor_icms:.2f}"
        ET.SubElement(icms_tot, "vICMSDeson").text = "0.00"
        ET.SubElement(icms_tot, "vFCP").text = "0.00"
        ET.SubElement(icms_tot, "vBCST").text = "0.00"
        ET.SubElement(icms_tot, "vST").text = "0.00"
        ET.SubElement(icms_tot, "vFCPST").text = "0.00"
        ET.SubElement(icms_tot, "vFCPSTRet").text = "0.00"
        ET.SubElement(icms_tot, "vProd").text = f"{nf.valor_total_produtos:.2f}"
        ET.SubElement(icms_tot, "vFrete").text = "0.00"
        ET.SubElement(icms_tot, "vSeg").text = "0.00"
        ET.SubElement(icms_tot, "vDesc").text = f"{nf.valor_desconto:.2f}"
        ET.SubElement(icms_tot, "vII").text = "0.00"
        ET.SubElement(icms_tot, "vIPI").text = "0.00"
        ET.SubElement(icms_tot, "vIPIDevol").text = "0.00"
        ET.SubElement(icms_tot, "vPIS").text = "0.00"
        ET.SubElement(icms_tot, "vCOFINS").text = "0.00"
        ET.SubElement(icms_tot, "vOutro").text = "0.00"
        ET.SubElement(icms_tot, "vNF").text = f"{nf.valor_total:.2f}"

        # transp - Transporte (sem frete para NFC-e)
        transp = ET.SubElement(inf, "transp")
        ET.SubElement(transp, "modFrete").text = "9"  # Sem frete

        # pag - Pagamentos
        pag = ET.SubElement(inf, "pag")
        for pagamento in nf.pagamentos:
            det_pag = ET.SubElement(pag, "detPag")
            ET.SubElement(det_pag, "tPag").text = pagamento.tipo.value
            ET.SubElement(det_pag, "vPag").text = f"{pagamento.valor:.2f}"

            # Dados do cartão se for crédito/débito
            if pagamento.tipo in [PaymentType.CARTAO_CREDITO, PaymentType.CARTAO_DEBITO]:
                card = ET.SubElement(det_pag, "card")
                ET.SubElement(card, "tpIntegra").text = "2"  # Não integrado

        # Troco se houver
        if nf.valor_troco and nf.valor_troco > 0:
            ET.SubElement(pag, "vTroco").text = f"{nf.valor_troco:.2f}"

        # infRespTec - Responsável Técnico
        inf_resp = ET.SubElement(inf, "infRespTec")
        ET.SubElement(inf_resp, "CNPJ").text = re.sub(r'[^\d]', '', nf.emitente.cnpj)
        ET.SubElement(inf_resp, "xContato").text = "Suporte Tecnico"
        ET.SubElement(inf_resp, "email").text = "suporte@conectapro.com.br"
        ET.SubElement(inf_resp, "fone").text = "92999999999"

        # Gerar XML sem infNFeSupl (será adicionado após assinatura)
        return self._prettify(root)

    def add_inf_nfe_supl(self, xml_assinado: str, qrcode_url: str, url_chave: str) -> str:
        """
        Adiciona o grupo infNFeSupl ao XML assinado.

        Este grupo deve ser adicionado APÓS a assinatura, pois não faz
        parte do conteúdo assinado.

        Args:
            xml_assinado: XML da NFC-e já assinado
            qrcode_url: URL do QR Code
            url_chave: URL de consulta pela chave

        Returns:
            XML com infNFeSupl
        """
        # Parse XML
        root = ET.fromstring(xml_assinado.encode('utf-8'))

        # Encontrar NFe
        ns = {"nfe": self.NAMESPACE}
        nfe = root if root.tag.endswith("NFe") else root.find(".//nfe:NFe", ns)
        if nfe is None:
            nfe = root.find(".//NFe")

        if nfe is None:
            raise ValueError("Elemento NFe não encontrado")

        # Criar infNFeSupl
        inf_supl = ET.Element("infNFeSupl")

        # QR Code com CDATA
        qr_code = ET.SubElement(inf_supl, "qrCode")
        qr_code.text = qrcode_url

        # URL consulta chave
        url_chave_elem = ET.SubElement(inf_supl, "urlChave")
        url_chave_elem.text = url_chave

        # Inserir após Signature (ou no final do NFe)
        signature = nfe.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
        if signature is not None:
            # Inserir após assinatura
            parent = nfe
            idx = list(parent).index(signature)
            parent.insert(idx + 1, inf_supl)
        else:
            nfe.append(inf_supl)

        return ET.tostring(root, encoding='unicode')

    def _add_icms_nfce(self, parent: ET.Element, produto: Produto, regime_tributario: str) -> None:
        """Adiciona ICMS específico para NFC-e."""
        icms = ET.SubElement(parent, "ICMS")
        cst = produto.cst_icms or "102"

        # Simples Nacional
        if regime_tributario in ["1", "2"]:
            if cst in ["101", "102", "103", "201", "202", "203", "300", "400", "500", "900"]:
                icms_elem = ET.SubElement(icms, f"ICMSSN{cst}")
                ET.SubElement(icms_elem, "orig").text = produto.origem or "0"
                ET.SubElement(icms_elem, "CSOSN").text = cst
            else:
                # Fallback para ICMSSN102
                icms_elem = ET.SubElement(icms, "ICMSSN102")
                ET.SubElement(icms_elem, "orig").text = produto.origem or "0"
                ET.SubElement(icms_elem, "CSOSN").text = "102"
        else:
            # Regime Normal
            icms_elem = ET.SubElement(icms, f"ICMS{cst}")
            ET.SubElement(icms_elem, "orig").text = produto.origem or "0"
            ET.SubElement(icms_elem, "CST").text = cst

            if cst in ["00", "10", "20", "70"]:
                ET.SubElement(icms_elem, "modBC").text = "3"
                ET.SubElement(icms_elem, "vBC").text = f"{produto.valor_total:.2f}"
                ET.SubElement(icms_elem, "pICMS").text = f"{produto.aliquota_icms:.2f}"
                ET.SubElement(icms_elem, "vICMS").text = f"{produto.valor_icms:.2f}"


class NFCETransmitter:
    """Transmissor de NFC-e para SEFAZ."""

    def __init__(
        self,
        uf: str,
        ambiente: str = "2",
        csc_id: str = "",
        csc_token: str = ""
    ):
        """
        Inicializa o transmissor de NFC-e.

        Args:
            uf: UF do emitente
            ambiente: 1=Produção, 2=Homologação
            csc_id: ID do CSC
            csc_token: Token do CSC
        """
        self.uf = uf
        self.ambiente = ambiente
        self.csc_id = csc_id
        self.csc_token = csc_token

        env_suffix = "PROD" if ambiente == "1" else "HOM"
        self.endpoints = NFCE_ENDPOINTS.get(f"{uf}_{env_suffix}", {})

        self.qrcode_generator = NFCEQRCodeGenerator(uf, ambiente, csc_id, csc_token)
        self.xml_builder = NFCEXMLBuilder(csc_id, csc_token)

        logger.info(f"NFCETransmitter inicializado: UF={uf}, Ambiente={'Produção' if ambiente == '1' else 'Homologação'}")

    def get_endpoint(self, service: str) -> str:
        """Retorna endpoint do serviço."""
        return self.endpoints.get(service, "")

    def generate_qrcode(
        self,
        chave_acesso: str,
        dh_emi: str,
        valor_total: Decimal,
        valor_icms: Decimal,
        dig_val: str,
        cpf_cnpj_dest: Optional[str] = None
    ) -> str:
        """Gera URL do QR Code."""
        return self.qrcode_generator.generate_qrcode_url(
            chave_acesso, dh_emi, valor_total, valor_icms, dig_val, cpf_cnpj_dest
        )


logger.info("Módulo NFCEManager carregado")
