"""
Módulo de Busca Global — Conecta PRO.

Expõe endpoint GET /search que busca em:
  - Colaboradores (nome, CPF, matrícula)
  - Postos (nome, código, cliente)
  - Escalas (código, período)
  - Ocorrências (descrição, responsável)
  - Rondas de inspeção

Registrado via modules/monitoring/__init__.py para não alterar
main_production.py (ZONA PROIBIDA).
"""

from .controller import router

__all__ = ["router"]
