"""Controller para skills jurídicas da Conecta Mais."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/juridico", tags=["Jurídico - Skills"])

# ---------------------------------------------------------------------------
# Catálogo estático de skills jurídicas
# ---------------------------------------------------------------------------

_SKILLS: list[dict] = [
    {
        "id": "089",
        "codigo": "089",
        "nome": "Contrato de Prestação de Serviços",
        "descricao": "Modelos de contrato B2B para Kit Mensal, Portaria Remota e Manutenção CFTV",
        "categoria": "contrato",
        "tipos_contrato": ["kit_mensal", "portaria_remota", "manutencao_cftv"],
        "arquivo": "089-contrato-prestacao-servicos-conecta.md",
        "versao": "2026-01",
        "ativo": True,
    },
    {
        "id": "090",
        "codigo": "090",
        "nome": "Política de Privacidade LGPD",
        "descricao": "Política de privacidade e proteção de dados adaptada para CFTV e biometria",
        "categoria": "lgpd",
        "tipos_contrato": [],
        "arquivo": "090-092-lgpd-conecta-pro.md",
        "versao": "2026-01",
        "ativo": True,
    },
    {
        "id": "092",
        "codigo": "092",
        "nome": "Checklist LGPD Operacional",
        "descricao": "Checklist de compliance LGPD para implantação de sistemas de segurança eletrônica",
        "categoria": "lgpd",
        "tipos_contrato": [],
        "arquivo": "090-092-lgpd-conecta-pro.md",
        "versao": "2026-01",
        "ativo": True,
    },
    {
        "id": "095",
        "codigo": "095",
        "nome": "Acordos de Confidencialidade (NDA)",
        "descricao": "3 modelos de NDA: fornecedor TI, parceiro contencioso e prestador de condomínio",
        "categoria": "nda",
        "tipos_contrato": ["nda_fornecedor_ti", "nda_contencioso", "nda_prestador_condominio"],
        "arquivo": "095-nda-conecta-mais.md",
        "versao": "2026-01",
        "ativo": True,
    },
    {
        "id": "253",
        "codigo": "253",
        "nome": "OS Rápida (Chamado Corretivo Urgente)",
        "descricao": "Template de Ordem de Serviço para chamados corretivos com SLA ≤ 4h",
        "categoria": "ordem_servico",
        "tipos_contrato": ["os_rapida"],
        "arquivo": "253-305-318-contratos-operacionais-conecta.md",
        "versao": "2026-01",
        "ativo": True,
    },
    {
        "id": "305",
        "codigo": "305",
        "nome": "Contrato de Serviço Padrão",
        "descricao": "Contrato para instalações pontuais e serviços avulsos (até 16 câmeras)",
        "categoria": "contrato",
        "tipos_contrato": ["servico_avulso", "instalacao_pontual"],
        "arquivo": "253-305-318-contratos-operacionais-conecta.md",
        "versao": "2026-01",
        "ativo": True,
    },
    {
        "id": "318",
        "codigo": "318",
        "nome": "Contrato Operacional Completo",
        "descricao": "Contrato completo com cronograma, milestones, aceite e DPA para projetos de grande porte",
        "categoria": "contrato",
        "tipos_contrato": ["projeto_grande_porte", "portaria_remota_completa"],
        "arquivo": "253-305-318-contratos-operacionais-conecta.md",
        "versao": "2026-01",
        "ativo": True,
    },
]

_SKILLS_BY_ID: dict[str, dict] = {s["id"]: s for s in _SKILLS}

_TIPOS_CONTRATO: list[dict] = [
    {"tipo": "kit_mensal", "nome": "Kit Mensal (Monitoramento)", "skill_id": "089", "vigencia_min_meses": 12},
    {"tipo": "portaria_remota", "nome": "Portaria Remota", "skill_id": "089", "vigencia_min_meses": 24},
    {"tipo": "manutencao_cftv", "nome": "Manutenção CFTV", "skill_id": "089", "vigencia_min_meses": 12},
    {"tipo": "nda_fornecedor_ti", "nome": "NDA Fornecedor de TI", "skill_id": "095", "vigencia_min_meses": 60},
    {"tipo": "nda_contencioso", "nome": "NDA Parceiro de Contencioso", "skill_id": "095", "vigencia_min_meses": 60},
    {
        "tipo": "nda_prestador_condominio",
        "nome": "NDA Prestador de Condomínio",
        "skill_id": "095",
        "vigencia_min_meses": 3,
    },
    {"tipo": "os_rapida", "nome": "OS Rápida (Corretiva Urgente)", "skill_id": "253", "vigencia_min_meses": 0},
    {
        "tipo": "servico_avulso",
        "nome": "Serviço Avulso / Instalação Pontual",
        "skill_id": "305",
        "vigencia_min_meses": 0,
    },
    {"tipo": "instalacao_pontual", "nome": "Instalação Pontual", "skill_id": "305", "vigencia_min_meses": 0},
    {
        "tipo": "projeto_grande_porte",
        "nome": "Projeto Grande Porte (>16 câmeras)",
        "skill_id": "318",
        "vigencia_min_meses": 0,
    },
    {
        "tipo": "portaria_remota_completa",
        "nome": "Portaria Remota Completa",
        "skill_id": "318",
        "vigencia_min_meses": 24,
    },
]

# Caminho base das skills no filesystem
_SKILLS_BASE_PATH = Path("/opt/conecta-pro/skills/financeiro/juridico")


# ---------------------------------------------------------------------------
# Schemas de resposta
# ---------------------------------------------------------------------------


class SkillResponse(BaseModel):
    id: str
    codigo: str
    nome: str
    descricao: str
    categoria: str
    tipos_contrato: list[str]
    arquivo: str
    versao: str
    ativo: bool


class SkillDetailResponse(SkillResponse):
    conteudo: str | None = None


class TipoContratoResponse(BaseModel):
    tipo: str
    nome: str
    skill_id: str
    vigencia_min_meses: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/skills",
    response_model=list[SkillResponse],
    summary="Listar skills jurídicas",
)
async def list_skills(
    categoria: str | None = None,
    ativo: bool = True,
) -> list[SkillResponse]:
    """Retorna todas as skills jurídicas cadastradas, com filtro opcional por categoria."""
    result = [s for s in _SKILLS if s["ativo"] == ativo]
    if categoria:
        result = [s for s in result if s["categoria"] == categoria]
    return [SkillResponse(**s) for s in result]


@router.get(
    "/skills/contratos/tipos",
    response_model=list[TipoContratoResponse],
    summary="Listar tipos de contrato disponíveis",
)
async def list_tipos_contrato() -> list[TipoContratoResponse]:
    """Retorna os 7 tipos de contrato/instrumento jurídico disponíveis na Conecta Mais."""
    return [TipoContratoResponse(**t) for t in _TIPOS_CONTRATO]


@router.get(
    "/skills/{skill_id}",
    response_model=SkillDetailResponse,
    summary="Buscar skill jurídica por ID",
)
async def get_skill(skill_id: str, incluir_conteudo: bool = False) -> SkillDetailResponse:
    """Retorna detalhes de uma skill jurídica. Com `incluir_conteudo=true` retorna o markdown completo."""
    skill = _SKILLS_BY_ID.get(skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_id}' não encontrada. Skills disponíveis: {list(_SKILLS_BY_ID.keys())}",
        )

    conteudo = None
    if incluir_conteudo:
        skill_path = _SKILLS_BASE_PATH / skill["arquivo"]
        try:
            conteudo = skill_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"Arquivo de skill não encontrado: {skill_path}")
            conteudo = None

    return SkillDetailResponse(**skill, conteudo=conteudo)
