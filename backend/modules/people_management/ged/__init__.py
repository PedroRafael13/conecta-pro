"""
GED — Gestão Eletrônica de Documentos (Kits Documentais).

Sub-módulo responsável por:
- Montagem de kits documentais mensais por cliente
- Upload e organização de documentos trabalhistas
- Envio de kits por e-mail, Google Drive ou portal
- Log de acesso e auditoria completa
"""

from fastapi import APIRouter

router = APIRouter(prefix="/ged", tags=["GED - Kits Documentais"])

__all__ = ["router"]
