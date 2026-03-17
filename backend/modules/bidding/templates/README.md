# Bidding Templates

Templates used by the COMPILER agent (`modules.bidding.agents.compiler`) for automated document generation in bidding processes.

## Template Files

| File | Purpose |
|------|---------|
| `proposta_comercial.json` | Commercial proposal structure with company data, pricing, and declarations |
| `planilha_custos.json` | Cost breakdown worksheet (IN 05/2017 format) with salary, benefits, and BDI modules |
| `declaracao_me_epp.json` | ME/EPP (micro/small business) eligibility declaration |
| `declaracao_menor.json` | Declaration of no underage labor (Lei 9.854/99, Art. 7 CF) |
| `carta_proposta.json` | Proposal cover letter with pricing summary and validity |

## Usage

The COMPILER agent loads these templates at runtime to generate PDF/DOCX documents via `reportlab` and `python-docx`. Each template defines sections, fields, and formatting parameters.
