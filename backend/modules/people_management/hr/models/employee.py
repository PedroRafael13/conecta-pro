"""
Re-exportação do modelo Employee do módulo Operacional.

Este arquivo NÃO duplica o modelo — apenas importa e re-exporta
para que o módulo DP possa referenciar Employee de forma transparente.
"""

from modules.operacional.models.employee import Employee

__all__ = ["Employee"]
