"""
Conector Domínio Sistemas (Contabilidade TOTVS)

Chave API configurada. Testa conectividade e usa fallback
para exportação de arquivos quando a API não está disponível.

Configuração: DOMINIO_API_KEY, DOMINIO_API_URL, DOMINIO_CNPJ, DOMINIO_ENABLED
"""

from .connector import check_connectivity, exportar_lancamentos, get_status

__all__ = ["check_connectivity", "exportar_lancamentos", "get_status"]
