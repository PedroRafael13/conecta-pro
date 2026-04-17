"""
GEDEON Fase 3 — Onvio Document Parser
Classifica documentos por nome de arquivo e extrai metadados.
"""

import re
from dataclasses import dataclass


@dataclass
class DocumentoClassificado:
    onvio_id: str
    folder_id: str
    nome: str
    categoria: str
    mes_ref: str | None  # "03.2026"
    funcionario: str | None  # nome do funcionário, se aplicável
    data_onvio: str | None


def extrair_mes_ref(nome: str) -> str | None:
    """Extrai referência de mês do nome: '03.2026', '03/2026', '032026'"""
    patterns = [
        r"(\d{2})[.\-/](\d{4})",  # 03.2026 ou 03/2026
        r"(\d{2})(\d{4})",  # 032026
    ]
    for pat in patterns:
        m = re.search(pat, nome)
        if m:
            mes, ano = m.group(1), m.group(2)
            if 1 <= int(mes) <= 12 and 2020 <= int(ano) <= 2030:
                return f"{mes}.{ano}"
    return None


def classificar_documento(item: dict) -> DocumentoClassificado:
    nome = item.get("name", "")
    nome_upper = nome.upper()
    folder_id = item.get("parentId", item.get("containerId", ""))

    # Classificação por conteúdo do nome
    if "DCTFWEB" in nome_upper:
        if "DECLARACAO" in nome_upper or "DECLARAÇÃO" in nome_upper:
            cat = "dctfweb_declaracao"
        elif "RECIBO" in nome_upper:
            cat = "dctfweb_recibo"
        elif "EXTRATO" in nome_upper:
            cat = "dctfweb_extrato"
        elif "RESUMODEBITOS" in nome_upper.replace(" ", ""):
            cat = "dctfweb_debitos"
        elif "RESUMOCREDITOS" in nome_upper.replace(" ", ""):
            cat = "dctfweb_creditos"
        elif "SITUACAO" in nome_upper or "SITUAÇÃO" in nome_upper:
            cat = "dctfweb_situacao"
        else:
            cat = "dctfweb_outros"
    elif "GFD FGTS" in nome_upper or "GFD-FGTS" in nome_upper:
        if "CONSIGNADO" in nome_upper:
            cat = "fgts_consignado"
        elif "RELATORIO" in nome_upper or "RELATÓRIO" in nome_upper:
            cat = "fgts_relatorio"
        else:
            cat = "fgts_guia"
    elif "INSS" in nome_upper:
        cat = "inss_guia"
    elif "CONTRACHEQUE" in nome_upper or "HOLERITE" in nome_upper:
        cat = "contracheque"
    elif "FOLHA" in nome_upper and ("PAGAMENTO" in nome_upper or "PAG" in nome_upper):
        cat = "folha_pagamento"
    elif "RESCISAO" in nome_upper or "RESCISÃO" in nome_upper:
        cat = "rescisao"
    elif "ADMISSAO" in nome_upper or "ADMISSÃO" in nome_upper:
        cat = "admissao"
    elif "FERIAS" in nome_upper or "FÉRIAS" in nome_upper:
        cat = "ferias"
    elif "13" in nome_upper and "SALARIO" in nome_upper:
        cat = "decimo_terceiro"
    elif "AVISO" in nome_upper and "PREVIO" in nome_upper:
        cat = "ferias"
    elif "ASO" in nome_upper:
        cat = "aso"
    elif "ATESTADO" in nome_upper:
        cat = "atestado"
    elif "ALTERACAO" in nome_upper or "ALTERAÇÃO" in nome_upper:
        cat = "empresa_docs"
    else:
        cat = "outros"

    return DocumentoClassificado(
        onvio_id=item.get("id", ""),
        folder_id=folder_id,
        nome=nome,
        categoria=cat,
        mes_ref=extrair_mes_ref(nome),
        funcionario=None,  # extraído pelo context da pasta pai
        data_onvio=item.get("createdDate"),
    )
