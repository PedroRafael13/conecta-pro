"""
Skill Loader — Conecta PRO Financial Agents
Carrega skills do disco e as injeta nos system prompts dos agentes.
Cache LRU para evitar I/O repetido.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Primary path (host mount), fallback to /tmp for container environments
_PRIMARY_PATH = Path("/opt/conecta-pro/skills/financeiro")
_FALLBACK_PATH = Path("/tmp/skills/financeiro")  # nosec B108
SKILLS_BASE_PATH = _PRIMARY_PATH if _PRIMARY_PATH.exists() else _FALLBACK_PATH


class SkillLoader:
    """Carrega e cacheia skills financeiras do disco."""

    _cache: dict[str, str] = {}

    @classmethod
    def load(cls, skill_name: str) -> str:
        """Carrega uma skill pelo nome (sem extensão .md)."""
        if skill_name in cls._cache:
            return cls._cache[skill_name]

        matches = list(cls._get_base_path().glob(f"*{skill_name}*.md"))
        if not matches:
            logger.warning(f"Skill não encontrada: {skill_name}")
            return ""

        try:
            content = matches[0].read_text(encoding="utf-8")
            cls._cache[skill_name] = content
            logger.info(f"Skill carregada: {skill_name} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Erro ao carregar skill {skill_name}: {e}")
            return ""

    @classmethod
    def load_multiple(cls, skill_names: list) -> str:
        """Carrega e concatena múltiplas skills."""
        parts = []
        for name in skill_names:
            content = cls.load(name)
            if content:
                parts.append(f"\n\n{'=' * 60}\n{content}")
        return "\n".join(parts)

    @classmethod
    def _get_base_path(cls) -> Path:
        """Retorna o path base resolvido em tempo de execução."""
        return _PRIMARY_PATH if _PRIMARY_PATH.exists() else _FALLBACK_PATH

    @classmethod
    def list_available(cls) -> list:
        """Lista todas as skills disponíveis."""
        base = cls._get_base_path()
        if not base.exists():
            return []
        return [f.stem for f in sorted(base.glob("*.md")) if not f.name.startswith("INDEX")]

    @classmethod
    def clear_cache(cls):
        """Limpa o cache (hot-reload em dev)."""
        cls._cache.clear()
