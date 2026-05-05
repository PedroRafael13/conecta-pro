#!/usr/bin/env python3
"""
Gera relatório PDF de divergências Domínio Sistemas vs Conecta PRO.

Compara rubricas, cálculos e totais entre os dois sistemas
para os meses 12/2025, 01/2026 e 02/2026.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path("/opt/conecta-pro/folhas-validacao/relatorio-divergencias.pdf")

# =========================================================================
# DADOS — Domínio Sistemas (referência) vs Conecta PRO (calculado)
# =========================================================================

# Valores Domínio extraídos das folhas de pagamento validadas
DOMINIO = {
    "12/2025": {
        "funcionarios": 44,
        "salario_base_total": 73480.00,
        "inss_total": 5605.08,
        "irrf_total": 0.00,
        "fgts_total": 5878.40,
        "vt_provento": 6160.00,
        "vr_provento": 13200.00,
        "vt_desconto": 2640.00,
        "vr_desconto": 1320.00,
        "he50_total": 4230.50,
        "adn_total": 3186.40,
        "intra_total": 890.20,
        "liquido_total": 88291.62,
    },
    "01/2026": {
        "funcionarios": 48,
        "salario_base_total": 80280.00,
        "inss_total": 6127.02,
        "irrf_total": 0.00,
        "fgts_total": 6422.40,
        "vt_provento": 6720.00,
        "vr_provento": 14400.00,
        "vt_desconto": 2880.00,
        "vr_desconto": 1440.00,
        "he50_total": 3890.75,
        "adn_total": 3456.80,
        "intra_total": 712.00,
        "liquido_total": 96041.53,
    },
    "02/2026": {
        "funcionarios": 52,
        "salario_base_total": 87410.15,
        "inss_total": 6682.89,
        "irrf_total": 0.00,
        "fgts_total": 6992.81,
        "vt_provento": 7280.00,
        "vr_provento": 15600.00,
        "vt_desconto": 3120.00,
        "vr_desconto": 1560.00,
        "he50_total": 0.00,
        "adn_total": 0.00,
        "intra_total": 0.00,
        "liquido_total": 104929.26,
    },
}

# Valores Conecta PRO (calculados pelo sistema)
CONECTA = {
    "12/2025": {
        "funcionarios": 44,
        "salario_base_total": 73480.00,
        "inss_total": 5605.08,
        "irrf_total": 0.00,
        "fgts_total": None,  # Não calculado
        "vt_provento": None,
        "vr_provento": None,
        "vt_desconto": None,
        "vr_desconto": None,
        "he50_total": None,
        "adn_total": None,
        "intra_total": None,
        "liquido_total": None,
    },
    "01/2026": {
        "funcionarios": 48,
        "salario_base_total": 80280.00,
        "inss_total": 6127.02,
        "irrf_total": 0.00,
        "fgts_total": None,
        "vt_provento": None,
        "vr_provento": None,
        "vt_desconto": None,
        "vr_desconto": None,
        "he50_total": None,
        "adn_total": None,
        "intra_total": None,
        "liquido_total": None,
    },
    "02/2026": {
        "funcionarios": 52,
        "salario_base_total": 87410.15,
        "inss_total": 6682.89,
        "irrf_total": 0.00,
        "fgts_total": None,
        "vt_provento": None,
        "vr_provento": None,
        "vt_desconto": None,
        "vr_desconto": None,
        "he50_total": None,
        "adn_total": None,
        "intra_total": None,
        "liquido_total": None,
    },
}

# Status das rubricas
RUBRICAS_STATUS = [
    ("0001", "Salário Base", "Implementada", "Cálculo idêntico ao Domínio"),
    ("0010", "Hora Extra 50%", "Pendente", "Rubrica cadastrada, sem lançamentos"),
    ("0011", "Hora Extra 100%", "Pendente", "Rubrica cadastrada, sem lançamentos"),
    ("0020", "Adicional Noturno", "Pendente", "Rubrica cadastrada, sem lançamentos"),
    ("0021", "Hora Noturna Reduzida", "Pendente", "Depende de controle de ponto"),
    ("0030", "Intrajornada Não Concedida", "Pendente", "Rubrica cadastrada, sem lançamentos"),
    ("0040", "Adicional Ronda 15%", "Pendente", "Específico de postos com ronda"),
    ("0050", "Adicional Insalubridade", "Pendente", "Depende de laudo técnico PPRA"),
    ("0051", "Adicional Periculosidade 30%", "Pendente", "Aplicável a vigilantes armados"),
    ("0060", "Vale Refeição", "Pendente", "Valor VR definido na CCT: R$ 300,00/mês"),
    ("0061", "Vale Transporte", "Pendente", "Desconto: 6% do salário base"),
    ("0070", "13º Salário 1ª Parcela", "Pendente", "Cálculo em novembro"),
    ("0071", "13º Salário 2ª Parcela", "Pendente", "Cálculo em dezembro"),
    ("0080", "Férias", "Parcial", "Períodos aquisitivos cadastrados, cálculo pendente"),
    ("0090", "DSR sobre HE", "Pendente", "Depende de horas extras lançadas"),
    ("1001", "INSS Segurado", "Implementada", "Cálculo progressivo 2026 (4 faixas)"),
    ("1002", "IRRF", "Implementada", "Cálculo progressivo 2026 (5 faixas)"),
    ("1010", "Desconto VT (6%)", "Pendente", "Rubrica cadastrada"),
    ("1011", "Desconto VR", "Pendente", "Rubrica cadastrada"),
    ("1020", "Plano Odontológico", "Pendente", "Depende de contrato com operadora"),
    ("1021", "Seguro de Vida", "Pendente", "Obrigatório CCT — valor pendente"),
    ("1030", "Taxa Negocial", "Pendente", "SINDECOMPRESTS — 1 dia de salário/ano"),
    ("FGTS", "FGTS Patronal (8%)", "Pendente", "Cálculo simples, integração eSocial S-1200"),
    ("GPS", "GPS/DARF INSS", "Pendente", "Guia de recolhimento — integração gov"),
]


def fmt(val):
    if val is None:
        return "—"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Estilos customizados
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=16, spaceAfter=4 * mm, textColor=colors.HexColor("#1a365d"),
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle", parent=styles["Heading2"],
        fontSize=12, spaceBefore=6 * mm, spaceAfter=3 * mm,
        textColor=colors.HexColor("#2d3748"),
    )
    body_style = ParagraphStyle(
        "CustomBody", parent=styles["Normal"],
        fontSize=9, leading=12, spaceAfter=2 * mm,
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"],
        fontSize=7.5, leading=10, textColor=colors.HexColor("#4a5568"),
    )
    right_style = ParagraphStyle(
        "Right", parent=body_style, alignment=TA_RIGHT,
    )

    # =====================================================================
    # CAPA
    # =====================================================================
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("RELATÓRIO DE DIVERGÊNCIAS", title_style))
    story.append(Paragraph("Domínio Sistemas × Conecta PRO", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#3182ce")))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        f"<b>Empresa:</b> CONECTAMAIS ELETRONICA LTDA (CNPJ: 35.710.481/0001-03)<br/>"
        f"<b>Período:</b> Dezembro/2025, Janeiro/2026, Fevereiro/2026<br/>"
        f"<b>Data de geração:</b> {date.today().strftime('%d/%m/%Y')}<br/>"
        f"<b>Gerado por:</b> Conecta PRO — Multi-Agent System<br/>"
        f"<b>CCT:</b> SINDECOMPRESTS 2026",
        body_style,
    ))

    story.append(Spacer(1, 8 * mm))

    # =====================================================================
    # 1. COMPARATIVO MENSAL
    # =====================================================================
    story.append(Paragraph("1. COMPARATIVO MENSAL — Totais da Folha", subtitle_style))

    header = ["Rubrica", "12/2025\nDomínio", "12/2025\nConecta", "01/2026\nDomínio", "01/2026\nConecta", "02/2026\nDomínio", "02/2026\nConecta"]
    rows = [header]

    comparisons = [
        ("Funcionários", "funcionarios", False),
        ("Salário Base", "salario_base_total", True),
        ("INSS Segurado", "inss_total", True),
        ("IRRF", "irrf_total", True),
        ("FGTS Patronal", "fgts_total", True),
        ("VT (provento)", "vt_provento", True),
        ("VR (provento)", "vr_provento", True),
        ("VT (desconto)", "vt_desconto", True),
        ("HE 50%", "he50_total", True),
        ("Adic. Noturno", "adn_total", True),
        ("Intrajornada", "intra_total", True),
        ("Líquido Total", "liquido_total", True),
    ]

    for label, key, is_money in comparisons:
        row = [Paragraph(f"<b>{label}</b>", small_style)]
        for month in ["12/2025", "01/2026", "02/2026"]:
            dom_val = DOMINIO[month].get(key)
            con_val = CONECTA[month].get(key)
            if is_money:
                row.append(Paragraph(fmt(dom_val), small_style))
                row.append(Paragraph(fmt(con_val), small_style))
            else:
                row.append(Paragraph(str(dom_val or "—"), small_style))
                row.append(Paragraph(str(con_val or "—"), small_style))
        rows.append(row)

    col_widths = [3.2 * cm] + [2.5 * cm] * 6
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        # Highlight matches in green, mismatches in red
    ]))
    story.append(table)
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "<i>Nota: Células com '—' indicam valores não calculados pelo Conecta PRO.</i>",
        small_style,
    ))

    # =====================================================================
    # 2. DIVERGÊNCIAS IDENTIFICADAS
    # =====================================================================
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("2. DIVERGÊNCIAS IDENTIFICADAS", subtitle_style))

    divergencias = [
        ["#", "Rubrica", "Tipo", "Severidade", "Descrição"],
        ["1", "Hora Extra 50%", "Ausência", "Alta",
         "Domínio lança HE com base no ponto. Conecta PRO não tem integração com REP ainda."],
        ["2", "Adicional Noturno", "Ausência", "Alta",
         "Domínio calcula ADN automático (20% CLT). Conecta PRO depende de lançamento manual."],
        ["3", "Intrajornada", "Ausência", "Média",
         "Domínio calcula intrajornada não concedida. Conecta PRO sem controle."],
        ["4", "VT/VR Proventos", "Ausência", "Média",
         "Domínio lança VT/VR como provento e desconto separados. Conecta PRO pendente."],
        ["5", "FGTS Patronal", "Ausência", "Alta",
         "8% sobre remuneração. Conecta PRO não calcula — necessário para eSocial S-1200."],
        ["6", "DSR sobre HE", "Ausência", "Média",
         "Repouso semanal remunerado sobre horas extras. Depende de HE lançada."],
        ["7", "Adic. Periculosidade", "Ausência", "Alta",
         "30% sobre salário base para vigilantes armados. CCT SINDECOMPRESTS obrigatório."],
        ["8", "Taxa Negocial", "Ausência", "Baixa",
         "1 dia de salário/ano em março. Desconto único."],
        ["9", "Seguro de Vida", "Ausência", "Média",
         "Obrigatório pela CCT. Valor depende de cotação com seguradora."],
    ]

    col_widths_div = [0.8 * cm, 3.5 * cm, 2 * cm, 1.8 * cm, 10 * cm]
    div_rows = [[Paragraph(str(c), small_style) for c in row] for row in divergencias]
    table_div = Table(div_rows, colWidths=col_widths_div, repeatRows=1)
    sev_colors = {"Alta": colors.HexColor("#fc8181"), "Média": colors.HexColor("#fbd38d"), "Baixa": colors.HexColor("#9ae6b4")}
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    # Color severity cells
    for i, row in enumerate(divergencias[1:], start=1):
        sev = row[3]
        if sev in sev_colors:
            style_cmds.append(("BACKGROUND", (3, i), (3, i), sev_colors[sev]))
    table_div.setStyle(TableStyle(style_cmds))
    story.append(table_div)

    # =====================================================================
    # 3. STATUS DAS RUBRICAS
    # =====================================================================
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("3. STATUS DAS RUBRICAS — Conecta PRO", subtitle_style))

    rub_header = ["Código", "Descrição", "Status", "Observação"]
    rub_rows = [[Paragraph(str(c), small_style) for c in rub_header]]
    status_colors = {
        "Implementada": colors.HexColor("#c6f6d5"),
        "Parcial": colors.HexColor("#fefcbf"),
        "Pendente": colors.HexColor("#fed7d7"),
    }
    for code, desc, status, obs in RUBRICAS_STATUS:
        rub_rows.append([
            Paragraph(code, small_style),
            Paragraph(desc, small_style),
            Paragraph(f"<b>{status}</b>", small_style),
            Paragraph(obs, small_style),
        ])

    col_widths_rub = [1.5 * cm, 4.5 * cm, 2.2 * cm, 10 * cm]
    table_rub = Table(rub_rows, colWidths=col_widths_rub, repeatRows=1)
    rub_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    for i, (_, _, status, _) in enumerate(RUBRICAS_STATUS, start=1):
        if status in status_colors:
            rub_style.append(("BACKGROUND", (2, i), (2, i), status_colors[status]))
    table_rub.setStyle(TableStyle(rub_style))
    story.append(table_rub)

    # Contagem
    impl = sum(1 for _, _, s, _ in RUBRICAS_STATUS if s == "Implementada")
    parc = sum(1 for _, _, s, _ in RUBRICAS_STATUS if s == "Parcial")
    pend = sum(1 for _, _, s, _ in RUBRICAS_STATUS if s == "Pendente")
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f"<b>Resumo:</b> {impl} implementadas, {parc} parcial, {pend} pendentes "
        f"({impl}/{len(RUBRICAS_STATUS)} = {impl/len(RUBRICAS_STATUS)*100:.0f}% de cobertura)",
        body_style,
    ))

    # =====================================================================
    # 4. RECOMENDAÇÕES
    # =====================================================================
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("4. RECOMENDAÇÕES PARA IGUALAR AO DOMÍNIO", subtitle_style))

    recs = [
        ("<b>PRIORIDADE 1 — Integração REP (Registrador Eletrônico de Ponto)</b><br/>"
         "Sem REP integrado, não é possível calcular HE, ADN, intrajornada e DSR. "
         "O Domínio recebe marcações do REP e calcula automaticamente. "
         "Recomendação: integrar com o REP via módulo hr/rep_integration já existente."),

        ("<b>PRIORIDADE 2 — FGTS Patronal + Guias</b><br/>"
         "Cálculo de 8% sobre remuneração bruta é trivial mas necessário para: "
         "eSocial S-1200, GFIP/SEFIP, e conciliação com a CAIXA. "
         "Implementar no mesmo serviço de folha."),

        ("<b>PRIORIDADE 3 — Adicional de Periculosidade</b><br/>"
         "CCT SINDECOMPRESTS exige 30% para vigilantes armados. "
         "Conecta PRO tem o campo na tabela CCT (adicional_periculosidade) mas "
         "não inclui no cálculo da folha. Adicionar como rubrica automática."),

        ("<b>PRIORIDADE 4 — VT/VR como Rubricas de Folha</b><br/>"
         "O Domínio lança VT (provento + desconto 6%) e VR (provento + desconto fixo) "
         "na folha. O Conecta PRO tem as rubricas cadastradas mas sem lançamento automático. "
         "Valores CCT: VR R$ 300,00/mês, VT calculado por itinerário."),

        ("<b>PRIORIDADE 5 — Validação Cruzada Mensal</b><br/>"
         "Após implementar as rubricas faltantes, rodar validação automática comparando "
         "totais do Conecta PRO com as PDFs do Domínio para os meses de referência. "
         "Meta: divergência < R$ 1,00 por rubrica."),
    ]
    for rec in recs:
        story.append(Paragraph(rec, body_style))
        story.append(Spacer(1, 2 * mm))

    # =====================================================================
    # RODAPÉ
    # =====================================================================
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#a0aec0")))
    story.append(Paragraph(
        f"Conecta PRO — Relatório gerado automaticamente em {date.today().strftime('%d/%m/%Y')} | "
        f"CONECTAMAIS ELETRONICA LTDA | CNPJ 35.710.481/0001-03",
        ParagraphStyle("Footer", parent=small_style, alignment=TA_CENTER, textColor=colors.HexColor("#a0aec0")),
    ))

    doc.build(story)
    print(f"PDF gerado: {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build_pdf()
