"""
Extratores da Receita Federal do Brasil.

Inclui:
- RFB: Consultas cadastrais (CNPJ, CPF)
- DCTFWeb: Declaração de Débitos e Créditos
- EFD-Reinf: Escrituração de Retenções
- e-CAC: Centro Virtual de Atendimento
- Simples Nacional: PGDAS-D, DEFIS, DAS
"""

from .rfb_extractor import ExtratorRFB
from .dctfweb_extractor import ExtratorDCTFWeb
from .efd_reinf_extractor import ExtratorEFDReinf
from .ecac_extractor import ExtratorECAC
from .simples_nacional_extractor import ExtratorSimplesNacional

__all__ = [
    "ExtratorRFB",
    "ExtratorDCTFWeb",
    "ExtratorEFDReinf",
    "ExtratorECAC",
    "ExtratorSimplesNacional",
]
