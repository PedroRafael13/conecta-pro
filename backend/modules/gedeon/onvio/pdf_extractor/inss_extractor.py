"""
INSSExtractor — Extrai dados estruturados de DARFs INSS (GPS/DARF Receitas Federais).
Herda de BaseExtractor (T1_B2).

Estrutura do DARF INSS (validada empiricamente em 4 PDFs reais, 2025-12 a 2026-04):
  - Header: "Documento de Arrecadação\nde Receitas Federais"
  - Competência: nome do mês em PT-BR + ano (ex: "Março/2026")
  - Vencimento: "Pagar até: DD/MM/YYYY" (seção PIX)
  - Valor: "Valor: X.XXX,XX" (seção PIX) ou "Valor Total do Documento\nXXX,XX"
  - Barcode: 4 grupos de 11 dígitos + 1 check digit cada (48 dígitos totais)
  - CNPJ emissor: 35.710.481/0001-03 (Conecta Mais)
"""

from __future__ import annotations

import re
from pathlib import Path

from .base import BaseExtractor, ExtractionResult

_MESES_PT: dict[str, str] = {
    "janeiro": "01",
    "fevereiro": "02",
    "março": "03",
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


class INSSExtractor(BaseExtractor):
    TIPO = "inss_guia"

    # Marker exclusivo de DARF de Receitas Federais (≠ DAS "do Simples Nacional")
    RE_TIPO_DOC = re.compile(
        r"Documento de Arrecada[çc][ãa]o\s+de Receitas Federais",
        re.IGNORECASE,
    )

    # Valor da seção PIX (mais limpo) — fallback: linha após "Valor Total do Documento"
    RE_VALOR_PIX = re.compile(r"\bValor:\s*([\d\.]+,\d{2})", re.IGNORECASE)
    RE_VALOR_TOTAL = re.compile(r"Valor Total do Documento\s*\n\s*([\d\.]+,\d{2})", re.IGNORECASE | re.MULTILINE)

    # Vencimento da seção PIX: "Pagar até: DD/MM/YYYY"
    RE_VENCIMENTO = re.compile(r"Pagar at[eé]:\s*(\d{1,2}/\d{1,2}/\d{4})", re.IGNORECASE)

    # Competência: linha após cabeçalho "Período de Apuração …"
    RE_COMPETENCIA = re.compile(
        r"Per[íi]odo de Apura[çc][ãa]o[^\n]*\n\s*(\w+/\d{4})",
        re.IGNORECASE,
    )

    # Barcode DARF: 4 grupos de 11 dígitos separados por 1 check digit
    # Exemplo: "85830000169 2 93550385261 9 10071626103 7 42526096301 2" → 48 dígitos
    RE_BARCODE = re.compile(r"(\d{11}\s+\d\s+\d{11}\s+\d\s+\d{11}\s+\d\s+\d{11}\s+\d)")

    # CNPJ Conecta Mais
    RE_CNPJ = re.compile(r"35[\.\s]*710[\.\s]*481[/\s]*0001[-\s]*03")

    def extract(self, pdf_path: Path) -> ExtractionResult:
        result = ExtractionResult(tipo=self.TIPO)
        try:
            texto = self._read_pdf_text(pdf_path)
            if not texto:
                result.erro = "PDF vazio ou não legível"
                result.confianca = 0.0
                return result

            result.detalhes["texto_len"] = len(texto)

            # Verificar marcador DARF de Receitas Federais (discrimina vs DAS)
            is_darf = bool(self.RE_TIPO_DOC.search(texto))
            result.detalhes["is_darf"] = is_darf

            # Valor: preferir seção PIX, depois "Valor Total do Documento"
            m = self.RE_VALOR_PIX.search(texto)
            if not m:
                m = self.RE_VALOR_TOTAL.search(texto)
            if m:
                result.valor = self._safe_decimal(m.group(1))
                result.detalhes["valor_raw"] = m.group(1)

            # Vencimento
            m = self.RE_VENCIMENTO.search(texto)
            if m:
                result.vencimento = self._safe_date(m.group(1))
                result.detalhes["vencimento_raw"] = m.group(1)

            # Competência (nome PT-BR → MM/YYYY)
            m = self.RE_COMPETENCIA.search(texto)
            if m:
                result.competencia = self._parse_competencia_ptbr(m.group(1))
                result.detalhes["competencia_raw"] = m.group(1)

            # Código de barras DARF (48 dígitos: 4×11 + 4 check digits)
            m = self.RE_BARCODE.search(texto)
            if m:
                result.codigo_barras = re.sub(r"\s+", "", m.group(1))
                result.detalhes["barcode_len"] = len(result.codigo_barras)

            # Validação cruzada: CNPJ Conecta Mais
            tem_cnpj = bool(self.RE_CNPJ.search(texto))
            result.detalhes["cnpj_validado"] = tem_cnpj

            # Score de confiança
            score = 0.0
            if is_darf:
                score += 0.20
            if result.valor and result.valor > 0:
                score += 0.30
            if result.vencimento:
                score += 0.20
            if result.competencia:
                score += 0.15
            if result.codigo_barras:
                score += 0.10
            if tem_cnpj:
                score += 0.05

            # Documentos sem marcador DARF (DAS, GRF, etc.) nunca atingem 0.70
            # mesmo que tenham campos similares preenchidos
            result.confianca = round(min(score, 0.65) if not is_darf else score, 2)
            result.metodo_extracao = "regex_v1"

        except Exception as e:
            result.erro = str(e)[:200]
            result.confianca = 0.0

        return result

    def _parse_competencia_ptbr(self, texto: str) -> str | None:
        m = re.match(r"(\w+)/(\d{4})", texto.strip(), re.IGNORECASE)
        if not m:
            return None
        mes_num = _MESES_PT.get(m.group(1).lower())
        return f"{mes_num}/{m.group(2)}" if mes_num else None


# TESTES INLINE
if __name__ == "__main__":
    from pathlib import Path

    pdfs = sorted(Path("/app/uploads/onvio/inss_guia").rglob("*.pdf"))
    print(f"\n=== INSSExtractor TESTE REAL ({len(pdfs)} PDFs no diretório) ===\n")

    extractor = INSSExtractor()
    resultados = []
    sucessos = 0
    baixa_confianca = 0
    falhas = 0

    for pdf in pdfs:
        r = extractor.extract(pdf)
        resultados.append(r)
        d = r.to_dict()
        is_darf = r.detalhes.get("is_darf", False)
        print(f"\n📄 {pdf.name}")
        print(f"   is_darf:       {is_darf}")
        print(f"   valor:         {d['valor']}")
        print(f"   vencimento:    {d['vencimento']}")
        print(f"   competência:   {d['competencia']}")
        print(f"   código barras: {(d['codigo_barras'] or '')[:20] + '...' if d['codigo_barras'] else None}")
        print(f"   confiança:     {d['confianca']}")
        if d["erro"]:
            print(f"   ❌ erro:       {d['erro']}")
        if is_darf:
            if d["confianca"] >= 0.90:
                print("   ✅ salvaria no DB")
                sucessos += 1
            elif d["confianca"] >= 0.70:
                print("   ⚠️  revisao_manual")
                baixa_confianca += 1
            else:
                print("   ❌ não salvaria (DARF mas confiança baixa)")
                falhas += 1

    # Meta calculada apenas sobre PDFs que são DARFs reais
    darf_results = [(pdf, r) for pdf, r in zip(pdfs, resultados, strict=False) if r.detalhes.get("is_darf")]
    darf_ok = sum(1 for _, r in darf_results if r.confianca >= 0.70)

    print("\n=== RESUMO ===")
    print(f"Total no diretório:    {len(pdfs)}")
    print(f"DARFs INSS reais:      {len(darf_results)}")
    print(f"Sucessos (>=0.90):     {sucessos}")
    print(f"Revisão (0.70-0.89):   {baixa_confianca}")
    print(f"Falhas DARF (<0.70):   {falhas}")

    meta = darf_ok / len(darf_results) if darf_results else 0
    print(f"\nTaxa utilizável (DARFs): {meta:.0%} (meta: >=80%)")
    assert meta >= 0.8, f"Menos de 80% dos DARFs INSS foram parseados com confiança >=0.70 ({meta:.0%})"
    print("\n✅ INSSExtractor APROVADO")
