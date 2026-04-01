"""
Extratores da Receita Federal do Brasil.

Inclui:
- RFB: Consultas cadastrais (CNPJ, CPF)
- DCTFWeb: Declaração de Débitos e Créditos
- EFD-Reinf: Escrituração de Retenções
- e-CAC: Centro Virtual de Atendimento
- Simples Nacional: PGDAS-D, DEFIS, DAS
"""

from .dctfweb_extractor import ExtratorDCTFWeb
from .ecac_extractor import ExtratorECAC
from .efd_reinf_extractor import ExtratorEFDReinf
from .rfb_extractor import ExtratorRFB
from .simples_nacional_extractor import ExtratorSimplesNacional

__all__ = [
    "ExtratorRFB",
    "ExtratorDCTFWeb",
    "ExtratorEFDReinf",
    "ExtratorECAC",
    "ExtratorSimplesNacional",
]
