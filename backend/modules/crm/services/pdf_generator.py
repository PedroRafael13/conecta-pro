"""
Gerador de PDF para Propostas Comerciais.

Gera documentos PDF profissionais para propostas comerciais
usando templates HTML e conversao via WeasyPrint ou ReportLab.
"""

import base64
import os
import tempfile
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from core.logging import logger


@dataclass
class CompanyInfo:
    """Informacoes da empresa emissora."""

    name: str
    cnpj: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
    website: str
    logo_path: Optional[str] = None


@dataclass
class ClientInfo:
    """Informacoes do cliente."""

    name: str
    document: str  # CNPJ ou CPF
    contact_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


@dataclass
class ProposalItem:
    """Item da proposta para PDF."""

    description: str
    quantity: int
    unit: str
    unit_price: Decimal
    discount_percent: Decimal
    total: Decimal
    details: Optional[str] = None


@dataclass
class ProposalData:
    """Dados completos da proposta para geracao de PDF."""

    number: str
    version: int
    issue_date: date
    valid_until: date
    company: CompanyInfo
    client: ClientInfo
    items: list[ProposalItem]
    subtotal: Decimal
    discount_value: Decimal
    taxes: Decimal
    total: Decimal
    cct_value: Optional[Decimal] = None
    margin_percent: Optional[Decimal] = None
    introduction: Optional[str] = None
    terms: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    salesperson_name: Optional[str] = None
    salesperson_email: Optional[str] = None


class PDFGenerator:
    """
    Gerador de PDF para propostas comerciais.

    Suporta:
    - Templates HTML customizaveis
    - Logotipo da empresa
    - Cabecalho e rodape personalizados
    - Tabela de itens com totais
    - Termos e condicoes
    - Assinatura digital (espaco reservado)
    """

    # Diretorio de templates
    TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

    # Diretorio de saida (temporario seguro)
    OUTPUT_DIR = Path(tempfile.gettempdir()) / "proposals"

    # CSS padrao para o PDF
    DEFAULT_CSS = """
        @page {
            size: A4;
            margin: 2cm;
            @top-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 9pt;
                color: #666;
            }
            @bottom-center {
                content: "Documento gerado em " string(generation-date);
                font-size: 8pt;
                color: #999;
            }
        }

        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }

        .logo {
            max-width: 180px;
            max-height: 80px;
        }

        .company-info {
            text-align: right;
            font-size: 9pt;
            color: #666;
        }

        .proposal-title {
            font-size: 24pt;
            color: #1e40af;
            margin: 20px 0;
            text-align: center;
        }

        .proposal-number {
            font-size: 12pt;
            color: #666;
            text-align: center;
            margin-bottom: 30px;
        }

        .section {
            margin: 20px 0;
        }

        .section-title {
            font-size: 14pt;
            color: #1e40af;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }

        .client-info {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .info-row {
            display: flex;
            margin-bottom: 5px;
        }

        .info-label {
            font-weight: bold;
            width: 120px;
            color: #666;
        }

        table.items {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        table.items th {
            background: #1e40af;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: normal;
        }

        table.items td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }

        table.items tr:nth-child(even) {
            background: #f8fafc;
        }

        table.items .number {
            text-align: right;
        }

        .totals {
            margin-top: 20px;
            float: right;
            width: 300px;
        }

        .totals-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }

        .totals-row.grand-total {
            font-size: 14pt;
            font-weight: bold;
            color: #1e40af;
            border-top: 2px solid #1e40af;
            border-bottom: none;
            padding-top: 15px;
        }

        .terms {
            clear: both;
            margin-top: 40px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 8px;
            font-size: 10pt;
        }

        .validity {
            text-align: center;
            margin: 30px 0;
            padding: 15px;
            background: #fef3c7;
            border-radius: 8px;
            color: #92400e;
        }

        .signature-area {
            margin-top: 50px;
            display: flex;
            justify-content: space-around;
        }

        .signature-box {
            text-align: center;
            width: 250px;
        }

        .signature-line {
            border-top: 1px solid #333;
            margin-top: 60px;
            padding-top: 10px;
        }

        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 9pt;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 15px;
        }
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> None:
        """
        Inicializa o gerador de PDF.

        Args:
            template_dir: Diretorio de templates (opcional)
            output_dir: Diretorio de saida (opcional)
        """
        self.template_dir = template_dir or self.TEMPLATE_DIR
        self.output_dir = output_dir or self.OUTPUT_DIR

        # Criar diretorio de saida se nao existir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, data: ProposalData) -> str:
        """
        Gera PDF da proposta.

        Args:
            data: Dados da proposta

        Returns:
            Caminho do arquivo PDF gerado
        """
        # Gerar HTML
        html_content = self._render_html(data)

        # Gerar nome do arquivo
        filename = f"proposta_{data.number.replace('-', '_')}_v{data.version}.pdf"
        output_path = self.output_dir / filename

        # Converter para PDF
        self._html_to_pdf(html_content, output_path)

        logger.info(
            "PDF gerado com sucesso",
            extra={
                "proposal_number": data.number,
                "output_path": str(output_path),
            },
        )

        return str(output_path)

    def generate_preview(self, data: ProposalData) -> str:
        """
        Gera HTML preview da proposta (sem PDF).

        Args:
            data: Dados da proposta

        Returns:
            HTML da proposta
        """
        return self._render_html(data)

    def _render_html(self, data: ProposalData) -> str:
        """Renderiza template HTML com dados da proposta."""
        # Formatar valores monetarios
        subtotal_fmt = self._format_currency(data.subtotal)
        discount_fmt = self._format_currency(data.discount_value)
        taxes_fmt = self._format_currency(data.taxes)
        total_fmt = self._format_currency(data.total)

        # Gerar linhas de itens
        items_html = self._render_items(data.items)

        # Logo em base64 (se existir)
        logo_html = self._render_logo(data.company.logo_path)

        # Renderizar HTML completo
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Proposta {data.number}</title>
            <style>
                {self.DEFAULT_CSS}
            </style>
        </head>
        <body>
            <!-- Cabecalho -->
            <div class="header">
                <div class="logo-area">
                    {logo_html}
                </div>
                <div class="company-info">
                    <strong>{data.company.name}</strong><br>
                    CNPJ: {data.company.cnpj}<br>
                    {data.company.address}<br>
                    {data.company.city} - {data.company.state}, {data.company.zip_code}<br>
                    Tel: {data.company.phone}<br>
                    {data.company.email}
                </div>
            </div>

            <!-- Titulo -->
            <h1 class="proposal-title">PROPOSTA COMERCIAL</h1>
            <p class="proposal-number">
                Número: <strong>{data.number}</strong> |
                Versão: {data.version} |
                Emissão: {data.issue_date.strftime('%d/%m/%Y')}
            </p>

            <!-- Dados do Cliente -->
            <div class="section">
                <h2 class="section-title">Cliente</h2>
                <div class="client-info">
                    <div class="info-row">
                        <span class="info-label">Empresa:</span>
                        <span>{data.client.name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">CNPJ/CPF:</span>
                        <span>{data.client.document}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Contato:</span>
                        <span>{data.client.contact_name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">E-mail:</span>
                        <span>{data.client.email}</span>
                    </div>
                    {self._render_optional_row('Telefone:', data.client.phone)}
                    {self._render_optional_row('Endereço:', data.client.address)}
                </div>
            </div>

            <!-- Introducao -->
            {self._render_introduction(data.introduction)}

            <!-- Itens -->
            <div class="section">
                <h2 class="section-title">Itens da Proposta</h2>
                <table class="items">
                    <thead>
                        <tr>
                            <th style="width: 40%">Descrição</th>
                            <th style="width: 10%">Qtd</th>
                            <th style="width: 10%">Unid</th>
                            <th style="width: 15%" class="number">Valor Unit.</th>
                            <th style="width: 10%" class="number">Desc.</th>
                            <th style="width: 15%" class="number">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <!-- Totais -->
                <div class="totals">
                    <div class="totals-row">
                        <span>Subtotal:</span>
                        <span>{subtotal_fmt}</span>
                    </div>
                    {self._render_discount_row(data.discount_value, discount_fmt)}
                    {self._render_taxes_row(data.taxes, taxes_fmt)}
                    {self._render_cct_row(data.cct_value)}
                    <div class="totals-row grand-total">
                        <span>TOTAL:</span>
                        <span>{total_fmt}</span>
                    </div>
                </div>
            </div>

            <!-- Validade -->
            <div class="validity">
                <strong>Validade da Proposta:</strong>
                {data.valid_until.strftime('%d/%m/%Y')}
                ({self._days_until(data.valid_until)} dias)
            </div>

            <!-- Condicoes de Pagamento -->
            {self._render_payment_terms(data.payment_terms)}

            <!-- Termos e Condicoes -->
            {self._render_terms(data.terms)}

            <!-- Observacoes -->
            {self._render_notes(data.notes)}

            <!-- Area de Assinatura -->
            <div class="signature-area">
                <div class="signature-box">
                    <div class="signature-line">
                        {data.company.name}<br>
                        <small>{data.salesperson_name or 'Responsável'}</small>
                    </div>
                </div>
                <div class="signature-box">
                    <div class="signature-line">
                        {data.client.name}<br>
                        <small>{data.client.contact_name}</small>
                    </div>
                </div>
            </div>

            <!-- Rodape -->
            <div class="footer">
                Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br>
                {data.company.website}
            </div>
        </body>
        </html>
        """

        return html

    def _render_items(self, items: list[ProposalItem]) -> str:
        """Renderiza linhas de itens da tabela."""
        rows = []
        for item in items:
            unit_price_fmt = self._format_currency(item.unit_price)
            total_fmt = self._format_currency(item.total)
            discount_fmt = f"{item.discount_percent}%" if item.discount_percent > 0 else "-"

            details_html = ""
            if item.details:
                details_html = f'<br><small style="color:#666">{item.details}</small>'

            row = f"""
            <tr>
                <td>{item.description}{details_html}</td>
                <td class="number">{item.quantity}</td>
                <td>{item.unit}</td>
                <td class="number">{unit_price_fmt}</td>
                <td class="number">{discount_fmt}</td>
                <td class="number">{total_fmt}</td>
            </tr>
            """
            rows.append(row)

        return "\n".join(rows)

    def _render_logo(self, logo_path: Optional[str]) -> str:
        """Renderiza logo em base64 ou placeholder."""
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
                ext = Path(logo_path).suffix.lower().replace(".", "")
                mime = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                return f'<img src="data:{mime};base64,{encoded}" class="logo" alt="Logo">'

        return '<div class="logo" style="font-size:20pt;color:#1e40af;">LOGO</div>'

    def _render_optional_row(self, label: str, value: Optional[str]) -> str:
        """Renderiza linha opcional se valor existir."""
        if not value:
            return ""
        return f"""
        <div class="info-row">
            <span class="info-label">{label}</span>
            <span>{value}</span>
        </div>
        """

    def _render_introduction(self, introduction: Optional[str]) -> str:
        """Renderiza secao de introducao."""
        if not introduction:
            return ""
        return f"""
        <div class="section">
            <h2 class="section-title">Apresentação</h2>
            <p>{introduction}</p>
        </div>
        """

    def _render_discount_row(self, value: Decimal, formatted: str) -> str:
        """Renderiza linha de desconto se existir."""
        if value <= 0:
            return ""
        return f"""
        <div class="totals-row">
            <span>Desconto:</span>
            <span style="color:#dc2626">-{formatted}</span>
        </div>
        """

    def _render_taxes_row(self, value: Decimal, formatted: str) -> str:
        """Renderiza linha de impostos se existir."""
        if value <= 0:
            return ""
        return f"""
        <div class="totals-row">
            <span>Impostos:</span>
            <span>{formatted}</span>
        </div>
        """

    def _render_cct_row(self, value: Optional[Decimal]) -> str:
        """Renderiza linha de CCT se existir."""
        if not value or value <= 0:
            return ""
        formatted = self._format_currency(value)
        return f"""
        <div class="totals-row">
            <span>Encargos (CCT):</span>
            <span>{formatted}</span>
        </div>
        """

    def _render_payment_terms(self, terms: Optional[str]) -> str:
        """Renderiza condicoes de pagamento."""
        if not terms:
            return ""
        return f"""
        <div class="section">
            <h2 class="section-title">Condições de Pagamento</h2>
            <p>{terms}</p>
        </div>
        """

    def _render_terms(self, terms: Optional[str]) -> str:
        """Renderiza termos e condicoes."""
        if not terms:
            return ""
        return f"""
        <div class="section terms">
            <h2 class="section-title">Termos e Condições</h2>
            <p>{terms}</p>
        </div>
        """

    def _render_notes(self, notes: Optional[str]) -> str:
        """Renderiza observacoes."""
        if not notes:
            return ""
        return f"""
        <div class="section">
            <h2 class="section-title">Observações</h2>
            <p>{notes}</p>
        </div>
        """

    def _format_currency(self, value: Decimal) -> str:
        """Formata valor monetario."""
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"

    def _days_until(self, target_date: date) -> int:
        """Calcula dias ate data alvo."""
        delta = target_date - date.today()
        return max(0, delta.days)

    def _html_to_pdf(self, html: str, output_path: Path) -> None:
        """
        Converte HTML para PDF.

        Tenta usar WeasyPrint primeiro, depois ReportLab como fallback.
        """
        try:
            # Tentar WeasyPrint (requer instalacao: pip install weasyprint)
            from weasyprint import HTML  # pylint: disable=import-outside-toplevel

            HTML(string=html).write_pdf(str(output_path))
            logger.debug("PDF gerado com WeasyPrint")

        except ImportError:
            # Fallback: salvar HTML e logar aviso
            html_path = output_path.with_suffix(".html")
            with open(html_path, "w", encoding="utf-8") as html_file:
                html_file.write(html)

            logger.warning(
                "WeasyPrint nao instalado. HTML salvo em vez de PDF.",
                extra={"html_path": str(html_path)},
            )

            # Criar arquivo PDF vazio com mensagem
            self._create_placeholder_pdf(output_path, html_path)

    def _create_placeholder_pdf(self, pdf_path: Path, html_path: Path) -> None:
        """Cria PDF placeholder indicando que WeasyPrint nao esta instalado."""
        try:
            from reportlab.lib.pagesizes import A4  # pylint: disable=import-outside-toplevel
            from reportlab.pdfgen import canvas  # pylint: disable=import-outside-toplevel

            canv = canvas.Canvas(str(pdf_path), pagesize=A4)
            canv.drawString(100, 750, "PDF Preview nao disponivel")
            canv.drawString(100, 730, f"Visualize o HTML em: {html_path}")
            canv.drawString(100, 710, "Instale weasyprint para PDF completo:")
            canv.drawString(100, 690, "pip install weasyprint")
            canv.save()

        except ImportError:
            # Nem ReportLab disponivel - criar arquivo texto
            with open(pdf_path, "w", encoding="utf-8") as placeholder:
                placeholder.write(f"PDF nao gerado. Veja HTML em: {html_path}\n")
                placeholder.write("Instale: pip install weasyprint\n")


# Instancia global
pdf_generator = PDFGenerator()
