# Compatibilidade: este pacote existe para quando o docker cp recursivo
# cria modules/gedeon/gedeon/ (cópia do pacote gedeon dentro de si mesmo).
# Re-exporta o singleton Gedeon da cópia interna (gedeon.py dentro deste dir).
from .gedeon import Gedeon, gedeon  # noqa: F401

__all__ = ["Gedeon", "gedeon"]
