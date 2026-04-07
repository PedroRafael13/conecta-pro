"""Sub-agentes do GEDEON."""

from modules.gedeon.agents.argos import Argos, argos
from modules.gedeon.agents.atlas import Atlas, atlas
from modules.gedeon.agents.hermes import Hermes, hermes
from modules.gedeon.agents.kronos import Kronos, kronos
from modules.gedeon.agents.sophia import SophiaIndex, sophia
from modules.gedeon.agents.themis import Themis, themis

__all__ = [
    "hermes",
    "Hermes",
    "argos",
    "Argos",
    "atlas",
    "Atlas",
    "kronos",
    "Kronos",
    "themis",
    "Themis",
    "sophia",
    "SophiaIndex",
]
