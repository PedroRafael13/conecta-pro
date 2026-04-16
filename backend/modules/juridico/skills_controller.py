"""
Controller para skills jurídicas adaptadas — Conecta Mais
Serve os templates e prompts das skills 089, 090, 092, 095, 253, 305, 318
"""

import re
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/juridico", tags=["Jurídico"])

SKILLS_DIR = Path("/tmp/skills/juridico")  # nosec B108


def _parse_frontmatter(text: str) -> dict:
    """Extrai campos name e description do frontmatter YAML simples."""
    meta: dict = {}
    for line in text.splitlines():
        m = re.match(r"^(name|description):\s*(.+)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
    return meta


def parse_skill(filepath: Path) -> dict:
    """Extrai metadata e conteúdo de um arquivo .md de skill."""
    content = filepath.read_text(encoding="utf-8")
    # Extrair frontmatter YAML (---...---)
    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if fm_match:
        meta = _parse_frontmatter(fm_match.group(1))
        body = fm_match.group(2)
    else:
        meta = {}
        body = content
    return {
        "id": filepath.stem,
        "name": meta.get("name", filepath.stem),
        "description": meta.get("description", ""),
        "content": body,
        "filename": filepath.name,
    }


@router.get("/skills")
async def list_skills():
    """Lista todas as skills jurídicas disponíveis."""
    if not SKILLS_DIR.exists():
        return []
    skills = []
    for f in sorted(SKILLS_DIR.glob("*.md")):
        try:
            skills.append(parse_skill(f))
        except Exception as e:
            skills.append({"id": f.stem, "error": str(e)})
    return skills


@router.get("/skills/{skill_id}")
async def get_skill(skill_id: str):
    """Retorna uma skill jurídica específica com o prompt completo."""
    for f in SKILLS_DIR.glob("*.md"):
        if skill_id in f.stem:
            return parse_skill(f)
    return {"error": f"Skill '{skill_id}' não encontrada"}


@router.get("/skills/contratos/tipos")
async def get_contract_types():
    """Lista os tipos de contrato disponíveis para a UI."""
    return [
        {
            "id": "kit_mensal",
            "label": "Kit Mensal — Mão de Obra Presencial",
            "skill": "089-contrato-prestacao-servicos-conecta",
            "modelo": "A",
            "descricao": "Portaria + facilities com agentes CLT",
        },
        {
            "id": "portaria_remota",
            "label": "Portaria Remota",
            "skill": "089-contrato-prestacao-servicos-conecta",
            "modelo": "B",
            "descricao": "Monitoramento remoto 24h",
        },
        {
            "id": "manutencao_cftv",
            "label": "Manutenção CFTV",
            "skill": "089-contrato-prestacao-servicos-conecta",
            "modelo": "C",
            "descricao": "Manutenção preventiva e corretiva",
        },
        {
            "id": "nda_fornecedor",
            "label": "NDA — Fornecedor TI",
            "skill": "095-nda-conecta-mais",
            "modelo": "1",
            "descricao": "Para acesso ao Conecta PRO",
        },
        {
            "id": "nda_licitacao",
            "label": "NDA — Parceiro Licitação",
            "skill": "095-nda-conecta-mais",
            "modelo": "2",
            "descricao": "Para consórcios em editais",
        },
        {
            "id": "lgpd_politica",
            "label": "Política de Privacidade LGPD",
            "skill": "090-092-lgpd-conecta-pro",
            "modelo": "politica",
            "descricao": "Conformidade LGPD do Conecta PRO",
        },
        {
            "id": "lgpd_checklist",
            "label": "Checklist LGPD",
            "skill": "090-092-lgpd-conecta-pro",
            "modelo": "checklist",
            "descricao": "Auditoria de conformidade",
        },
    ]
