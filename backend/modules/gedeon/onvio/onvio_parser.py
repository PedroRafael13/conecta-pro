"""GEDEON Fase 3 — Onvio Document Parser

Classifica documentos Onvio por nome/pasta → categoria + mes_ref.
"""

import re
from dataclasses import dataclass


@dataclass
class DocumentoClassificado:
    categoria: str
    mes_ref: str | None  # formato AAAA-MM ou None


# Meses PT-BR → número
_MESES_PT = {
    "janeiro": "01",
    "fevereiro": "02",
    "março": "03",
    "marco": "03",
    "abril": "04",
    "maio": "05",
    "junho": "06",
    "julho": "07",
    "agosto": "08",
    "setembro": "09",
    "outubro": "10",
    "novembro": "11",
    "dezembro": "12",
}

# Abrev meses 3 letras
_MESES_ABREV = {
    "jan": "01",
    "fev": "02",
    "mar": "03",
    "abr": "04",
    "mai": "05",
    "jun": "06",
    "jul": "07",
    "ago": "08",
    "set": "09",
    "out": "10",
    "nov": "11",
    "dez": "12",
}

# Mapa pasta → categoria padrão
_PASTA_CATEGORIA = {
    "Encargos da Folha": "encargos_folha",
    "Folha de Pagamento": "folha_pagamento",
    "Rescisão": "rescisao",
    "Admissão": "admissao",
    "Recibo de Férias": "ferias",
    "Aviso Prévio de Férias": "aviso_ferias",
    "13º Salário": "decimo_terceiro",
    "Fiscal": "fiscal",
    "Registro de Empresas": "registro_empresa",
}

# Palavras-chave no nome do arquivo → categoria refinada
_NOME_CATEGORIA = [
    (r"fgts.*consign", "fgts_consignado"),
    (r"fgts.*relat", "fgts_relatorio"),
    (r"guia.*fgts|fgts.*guia|grf\b", "fgts_guia"),
    (r"guia.*inss|inss.*guia|gps\b|das\b", "inss_guia"),
    (r"darf", "darf"),
    (r"simples.*nacional|pgmei", "simples_nacional"),
    (r"folha.*pagamento|holerite|contracheque", "folha_pagamento"),
    (r"rescis[aã]o", "rescisao"),
    (r"admiss[aã]o", "admissao"),
    (r"f[eé]rias", "ferias"),
    (r"aviso.*pr[eé]vio", "aviso_ferias"),
    (r"13.*sal[aá]rio|decimo.*terceiro", "decimo_terceiro"),
    (r"encargo", "encargos_folha"),
    (r"fiscal|nfs.?e|nota.*fiscal", "fiscal"),
]


def _extrair_mes_ref(texto: str) -> str | None:
    """Tenta extrair AAAA-MM do nome do arquivo ou pasta."""
    # Padrão: MM/AAAA ou AAAA-MM ou AAAA_MM
    m = re.search(r"(\d{4})[-_](\d{2})", texto)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    m = re.search(r"(\d{2})[/\-](\d{4})", texto)
    if m:
        return f"{m.group(2)}-{m.group(1)}"

    # Padrão: "março 2026", "Março/2026", "MAR2026"
    texto_lower = texto.lower()
    for nome, num in _MESES_PT.items():
        if nome in texto_lower:
            ano = re.search(r"\d{4}", texto)
            if ano:
                return f"{ano.group()}-{num}"

    for abrev, num in _MESES_ABREV.items():
        pat = re.search(rf"\b{abrev}(\d{{4}}|\s*\d{{4}})", texto_lower)
        if pat:
            ano = re.search(r"\d{4}", pat.group())
            if ano:
                return f"{ano.group()}-{num}"

    return None


def classificar_documento(item: dict) -> DocumentoClassificado:
    """
    Classifica um documento Onvio.

    Args:
        item: dict com campos 'name', '_pasta', 'parentId', 'createdDate'

    Returns:
        DocumentoClassificado(categoria, mes_ref)
    """
    nome = item.get("name", "")
    pasta = item.get("_pasta", "")
    nome_lower = nome.lower()

    # Categoria: primeiro pelo nome, depois pela pasta
    categoria = _PASTA_CATEGORIA.get(pasta, "outros")
    for pattern, cat in _NOME_CATEGORIA:
        if re.search(pattern, nome_lower):
            categoria = cat
            break

    # mes_ref: do nome do arquivo
    mes_ref = _extrair_mes_ref(nome) or _extrair_mes_ref(pasta)

    # Fallback: data de criação do documento
    if not mes_ref:
        data_str = item.get("createdDate", item.get("created_date", ""))
        if data_str and len(data_str) >= 7:
            mes_ref = data_str[:7]  # AAAA-MM

    return DocumentoClassificado(categoria=categoria, mes_ref=mes_ref)
