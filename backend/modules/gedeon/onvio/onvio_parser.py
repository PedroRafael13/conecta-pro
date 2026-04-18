"""GEDEON Fase 3 — Onvio Document Parser (v2 — refit CIC 2026-04-18)

Refatoração crítica baseada em dados reais de 436 documentos do CIC:
  BUG 1 FIX: mes_ref extraído do NOME do arquivo, nunca do createdDate.
  BUG 2 FIX: 26 categorias cobrindo 95%+ dos documentos (antes: 77% em "outros").

Categorias suportadas:
  DCTFWEB: declaracao, recibo, resumo_debitos, resumo_creditos, extrato, situacao, debitos, creditos
  FGTS: guia, relatorio, consignado, consignado_relatorio, crf
  INSS: guia
  FOLHA: folha_pagamento, recibo_folha, contracheque
  13º: decimo_terceiro, recibo_decimo_terceiro
  PESSOAL: rescisao, admissao, ferias, aviso_previo, contrato_trabalho, ficha_registro, declaracao_vt
  FISCAL: das_simples_nacional, parcelamento_simples, divida_ativa_simples, dar_sefaz, guia_issqn
  OUTROS: autodeclaracao, aso, atestado, certidao, alvara, empresa_docs, documento_digitalizado
"""

import re
from dataclasses import dataclass


@dataclass
class DocumentoClassificado:
    """Mantida para compatibilidade com consumidores legados."""

    categoria: str
    mes_ref: str | None  # formato MM.YYYY, ou só YYYY, ou None


def extract_mes_ref(nome: str) -> str | None:
    """
    Extrai mes_ref do nome do arquivo.

    REGRA 1: Formato explícito MM.YYYY, MM-YYYY ou MM/YYYY (preferido).
    REGRA 2: _MMYYYY_ entre underscores (ex: DCTFWEB _032026_).
    REGRA 3: Só ano YYYY (fallback para docs anuais como "13º SALARIO 2025").
    IGNORA: sequências dentro de CNPJs (14 dígitos contíguos).

    Retorna "MM.YYYY", "YYYY", ou None.
    """
    # Remove CNPJs para evitar falso-positivo (14 dígitos contíguos)
    nome_clean = re.sub(r"\d{14}", "_CNPJ_", nome)

    # Regra 1: MM.YYYY / MM-YYYY / MM/YYYY
    m = re.search(r"(?<!\d)(\d{2})[.\-/](\d{4})(?!\d)", nome_clean)
    if m and 1 <= int(m.group(1)) <= 12 and 2020 <= int(m.group(2)) <= 2030:
        return f"{m.group(1)}.{m.group(2)}"

    # Regra 2: _MMYYYY_ (ex: _032026_ em nomes DCTFWEB)
    m = re.search(r"_(\d{2})(\d{4})_", nome_clean)
    if m and 1 <= int(m.group(1)) <= 12 and 2020 <= int(m.group(2)) <= 2030:
        return f"{m.group(1)}.{m.group(2)}"

    # Regra 3: apenas YYYY — docs anuais (13º salário, DAS, PARC)
    m = re.search(r"(?<!\d)(\d{4})(?!\d)", nome_clean)
    if m and 2020 <= int(m.group(1)) <= 2030:
        return m.group(1)

    return None


def classificar_documento(nome: str, created_date: str | None = None) -> dict:
    """
    Classifica documento em 26+ categorias pelo nome do arquivo.

    Args:
        nome: Nome do arquivo (ex: "DCTFWEB Debitos_35710481000103_032026_40_.pdf")
        created_date: Data de criação no Onvio (IGNORADA para mes_ref — apenas informativo)

    Returns:
        {
            "categoria": str,
            "mes_ref": str | None,   # MM.YYYY ou YYYY — extraído do NOME, nunca do created_date
            "confianca": float,      # 0.0 a 1.0
        }
    """
    u = nome.upper()
    u_ns = u.replace(" ", "")  # sem espaços (para RESUMODEBITOS, etc.)
    u_nc = u.replace("Ç", "C").replace("Ã", "A").replace("Á", "A").replace("É", "E").replace("Ê", "E")

    mes_ref = extract_mes_ref(nome)

    # ── Regras ordenadas: MAIS ESPECÍFICO PRIMEIRO ──────────────────────────
    rules = [
        # DCTFWEB — 8 subcategorias (mais específico antes do genérico)
        ("DCTFWEB" in u and "DECLARACAO" in u_nc, "dctfweb_declaracao"),
        ("DCTFWEB" in u and "RECIBO" in u, "dctfweb_recibo"),
        ("DCTFWEB" in u and "RESUMODEBITOS" in u_ns, "dctfweb_resumo_debitos"),
        ("DCTFWEB" in u and "RESUMOCREDITOS" in u_ns, "dctfweb_resumo_creditos"),
        ("DCTFWEB" in u and "EXTRATO" in u, "dctfweb_extrato"),
        ("DCTFWEB" in u and "SITUACAO" in u_nc.replace(" ", ""), "dctfweb_situacao"),
        ("DCTFWEB" in u and "DEBITO" in u, "dctfweb_debitos"),
        ("DCTFWEB" in u and "CREDITO" in u, "dctfweb_creditos"),
        ("DCTFWEB" in u, "dctfweb_outros"),
        # FGTS — ordem: mais específico primeiro
        ("GFD FGTS" in u and "CONSIGNADO" in u and "RELATORIO" in u_nc, "fgts_consignado_relatorio"),
        ("GFD FGTS" in u and "CONSIGNADO" in u, "fgts_consignado"),
        ("GFD FGTS" in u and "RELATORIO" in u_nc, "fgts_relatorio"),
        ("GFD FGTS" in u, "fgts_guia"),
        ("FGTS" in u and "CRF" in u, "fgts_crf"),
        # INSS
        ("INSS" in u and "GUIAPAGAMENTO" in u_ns, "inss_guia"),
        ("INSS" in u and "GUIA" in u, "inss_guia"),
        # SIMPLES NACIONAL / DAS / DAR — ordem importa
        ("DAS" in u and "SIMPLES" in u, "das_simples_nacional"),
        ("PARC" in u and "SIMPLES NACIONAL" in u, "parcelamento_simples"),
        ("DIVIDA ATIVA" in u and "SIMPLES" in u, "divida_ativa_simples"),
        ("DAR" in u and ("SEFAZ" in u or "PARCELAMENTO" in u), "dar_sefaz"),
        ("ISSQN" in u or "ISS" in u, "guia_issqn"),
        # FOLHA — "RECIBO FOLHA" ANTES de "FOLHA" simples
        ("RECIBO FOLHA" in u, "recibo_folha"),
        (
            "FOLHA" in u and ("PAGAMENTO" in u or "PAG" in u or bool(re.search(r"\d{2}\.\d{4}", nome))),
            "folha_pagamento",
        ),
        ("CONTRACHEQUE" in u or "HOLERITE" in u, "contracheque"),
        # 13º — "RECIBO 13" ANTES de "13" simples
        ("RECIBO" in u and ("13º" in nome or ("13" in u and "SALARIO" in u_nc)), "recibo_decimo_terceiro"),
        ("13º" in nome or ("13" in u and "SALARIO" in u_nc), "decimo_terceiro"),
        # Rescisão / Admissão / Férias / Aviso
        ("RESCISAO" in u_nc or "RESCISÃO" in u, "rescisao"),
        ("ADMISSAO" in u_nc or "ADMISSÃO" in u, "admissao"),
        ("AVISO" in u and ("PREVIO" in u_nc or "PRÉVIO" in u), "aviso_previo"),
        ("FERIAS" in u_nc or "FÉRIAS" in u, "ferias"),
        # Cadastrais / RH
        (
            "CONTRATO DE EXPERIENCIA" in u_nc or "CONTRATO DE EXPERIÊNCIA" in u or "CONTRATO DE TRABALHO" in u,
            "contrato_trabalho",
        ),
        ("FICHA" in u and "REGISTRO" in u, "ficha_registro"),
        (
            "DECLARACAO" in u_nc and ("VALE TRANSPORTE" in u or "VT" in u),
            "declaracao_vt",
        ),
        ("AUTODECLARACAO" in u_nc, "autodeclaracao"),
        ("ASO" in u, "aso"),
        ("ATESTADO" in u, "atestado"),
        # Empresa / Fiscal
        (
            "ALTERACAO" in u_nc or "ALTERAÇÃO" in u or "CONTRATO SOCIAL" in u,
            "empresa_docs",
        ),
        ("ALVARA" in u_nc or "ALVARÁ" in u, "alvara"),
        ("CND" in u or "CERTIDAO" in u_nc or "CERTIDÃO" in u, "certidao"),
        # Genéricos por último
        ("CAMSCANNER" in u, "documento_digitalizado"),
        ("PORTAL" in u and "EMPREGADOR" in u, "portal_empregador"),
    ]

    for condition, categoria in rules:
        if condition:
            return {
                "categoria": categoria,
                "mes_ref": mes_ref,
                "confianca": 0.95,
            }

    return {
        "categoria": "outros",
        "mes_ref": mes_ref,
        "confianca": 0.30,
    }


def classificar_item_onvio(item: dict) -> DocumentoClassificado:
    """
    Wrapper para compatibilidade com onvio_sync_service legado.
    Aceita o dict bruto do Onvio (com chave 'name').
    Retorna DocumentoClassificado para acesso por atributo (.categoria, .mes_ref).
    """
    nome = item.get("name", "")
    created_date = item.get("createdDate") or item.get("created_date")
    resultado = classificar_documento(nome, created_date)
    return DocumentoClassificado(
        categoria=resultado["categoria"],
        mes_ref=resultado["mes_ref"],
    )


# ── Testes inline ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    casos = [
        # (nome, categoria_esperada, mes_ref_esperado)
        ("Folha 03.2026_Prime Arena (1).pdf", "folha_pagamento", "03.2026"),
        ("Recibo Folha 03.2026_Conecta Mais - Geral (4).pdf", "recibo_folha", "03.2026"),
        ("GFD FGTS 03.2026_Conecta Mais.pdf", "fgts_guia", "03.2026"),
        ("RELATORIO GFD FGTS 03.2026_Conecta Mais.pdf", "fgts_relatorio", "03.2026"),
        ("GFD FGTS - CONSIGNADO 03.2026.pdf", "fgts_consignado", "03.2026"),
        ("RELATORIO GFD FGTS - CONSIGNADO 03.2026.pdf", "fgts_consignado_relatorio", "03.2026"),
        ("INSS 03.2026 - GuiaPagamento_Conecta Mais.pdf", "inss_guia", "03.2026"),
        ("DCTFWEB Debitos_35710481000103_032026_40_.pdf", "dctfweb_debitos", "03.2026"),
        ("DCTFWEB ResumoDebitos_35710481000103_032026_40_.pdf", "dctfweb_resumo_debitos", "03.2026"),
        ("DCTFWEB DeclaracaoCompleta_35710481000103_032026_40_.pdf", "dctfweb_declaracao", "03.2026"),
        ("DCTFWEB Recibo_35710481000103_032026_40_0000050000467380773.pdf", "dctfweb_recibo", "03.2026"),
        ("PARC 26_145 DIVIDA ATIVA 1 SIMPLES NACIONAL JORDAN 2026 02.pdf", "parcelamento_simples", "2026"),
        ("DAS 9_60 SIMPLES NACIONAL 2026 01.pdf", "das_simples_nacional", "2026"),
        ("DAR 25_25 PARCELAMENTO SEFAZ 12 2025.pdf", "dar_sefaz", "2025"),
        ("Contrato de Experiência_Daniel Larroque.pdf", "contrato_trabalho", None),
        ("Ficha Registro de Empregado_Daniel Larroque.pdf", "ficha_registro", None),
        ("13º SALARIO 2025_Villa dos Passaros (1).pdf", "decimo_terceiro", "2025"),
        ("Recibo 13º SALARIO 2025_Villa dos Passaros (1).pdf", "recibo_decimo_terceiro", "2025"),
        ("AUTODECLARAÇÃO ÉTNICO-RACIAL.pdf", "autodeclaracao", None),
        ("CamScanner 30-03-2026 14.44.pdf", "documento_digitalizado", "03.2026"),
    ]

    erros = 0
    for nome, cat_esp, mes_esp in casos:
        r = classificar_documento(nome)
        ok_cat = r["categoria"] == cat_esp
        ok_mes = r["mes_ref"] == mes_esp
        status = "✅" if (ok_cat and ok_mes) else "❌"
        if not (ok_cat and ok_mes):
            erros += 1
            print(f"{status} {nome}")
            print(f"   Esperado: cat={cat_esp}, mes={mes_esp}")
            print(f"   Obtido:   cat={r['categoria']}, mes={r['mes_ref']}")
        else:
            print(f"{status} {nome}")

    print(f"\n{'✅ TODOS OS 20 CASOS PASSARAM' if erros == 0 else f'❌ {erros}/20 FALHARAM'}")
    assert erros == 0, "Testes falharam — não commitar"
