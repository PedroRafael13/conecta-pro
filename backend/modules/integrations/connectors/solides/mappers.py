"""
Mappers para Sólides - Gestão de Pessoas
Sprint 33: Integration Framework

Mapeamento bidirecional entre entidades Sólides e modelos internos Conecta PRO.
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, Optional, List
from uuid import UUID

from modules.integrations.connectors.solides.schemas import (
    SolidesColaborador,
    SolidesColaboradorCreate,
    SolidesDepartamento,
    SolidesCargo,
    SolidesVaga,
    SolidesCandidato,
    SolidesInscricao,
    SolidesAvaliacao,
    SolidesEndereco,
)

logger = logging.getLogger(__name__)


class SolidesMapperError(Exception):
    """Erro no mapeamento de entidades Sólides."""
    pass


# ==================== COLABORADOR → EMPLOYEE DATA ====================

def solides_colaborador_to_employee(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia colaborador Sólides para dados de funcionário interno.

    Args:
        solides_data: Dados do colaborador do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados do funcionário
    """
    defaults = defaults or {}
    endereco = solides_data.get("endereco") or {}

    # Mapear status
    situacao = solides_data.get("situacao", "ativo")
    status_map = {
        "ativo": "active",
        "inativo": "inactive",
        "ferias": "on_leave",
        "afastado": "on_leave",
        "demitido": "terminated",
    }
    status = status_map.get(situacao, "active")

    # Mapear tipo de contrato
    tipo_contrato = solides_data.get("tipo_contrato", "CLT")
    contract_type_map = {
        "CLT": "clt",
        "PJ": "pj",
        "Estagio": "intern",
        "Temporario": "temporary",
        "Terceirizado": "outsourced",
    }
    contract_type = contract_type_map.get(tipo_contrato, "clt")

    # Mapear sexo
    sexo = solides_data.get("sexo")
    gender_map = {"M": "masculino", "F": "feminino", "O": "outro"}
    gender = gender_map.get(sexo) if sexo else None

    return {
        "condominio_id": condominio_id,
        # Identificação
        "name": solides_data.get("nome", ""),
        "email": solides_data.get("email"),
        "cpf": _clean_document(solides_data.get("cpf")),
        "rg": solides_data.get("rg"),
        "birth_date": _parse_date(solides_data.get("data_nascimento")),
        "gender": gender,
        "marital_status": _map_marital_status(solides_data.get("estado_civil")),
        # Contato
        "phone": solides_data.get("telefone"),
        "mobile": solides_data.get("celular"),
        # Endereço
        "address_street": endereco.get("logradouro"),
        "address_number": endereco.get("numero"),
        "address_complement": endereco.get("complemento"),
        "address_neighborhood": endereco.get("bairro"),
        "address_city": endereco.get("cidade"),
        "address_state": endereco.get("estado"),
        "address_zipcode": _clean_cep(endereco.get("cep")),
        # Profissional
        "registration_number": solides_data.get("matricula"),
        "position_name": solides_data.get("cargo", {}).get("nome") if isinstance(solides_data.get("cargo"), dict) else None,
        "department_name": solides_data.get("departamento", {}).get("nome") if isinstance(solides_data.get("departamento"), dict) else None,
        "manager_name": solides_data.get("gestor_nome"),
        # Contrato
        "hire_date": _parse_date(solides_data.get("data_admissao")),
        "termination_date": _parse_date(solides_data.get("data_demissao")),
        "contract_type": contract_type,
        "work_regime": solides_data.get("regime_trabalho"),
        "work_schedule": solides_data.get("jornada_trabalho"),
        "salary": solides_data.get("salario"),
        # Status
        "status": status,
        "is_active": situacao == "ativo",
        # Perfil comportamental
        "behavioral_profile": {
            "disc": solides_data.get("perfil_disc"),
            "profiler": solides_data.get("perfil_profiler"),
        },
        # Metadados
        "photo_url": solides_data.get("foto_url"),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "cargo_id": solides_data.get("cargo_id"),
            "departamento_id": solides_data.get("departamento_id"),
            "gestor_id": solides_data.get("gestor_id"),
            "dados_adicionais": solides_data.get("dados_adicionais"),
        },
        **defaults,
    }


def employee_to_solides_colaborador(
    employee_data: Dict[str, Any]
) -> SolidesColaboradorCreate:
    """
    Mapeia dados de funcionário interno para criação no Sólides.

    Args:
        employee_data: Dados do funcionário

    Returns:
        SolidesColaboradorCreate schema
    """
    # Mapear tipo de contrato
    contract_map = {
        "clt": "CLT",
        "pj": "PJ",
        "intern": "Estagio",
        "temporary": "Temporario",
        "outsourced": "Terceirizado",
    }
    tipo_contrato = contract_map.get(
        employee_data.get("contract_type", "clt"),
        "CLT"
    )

    return SolidesColaboradorCreate(
        nome=employee_data.get("name", ""),
        email=employee_data.get("email", ""),
        cpf=employee_data.get("cpf"),
        data_nascimento=employee_data.get("birth_date"),
        telefone=employee_data.get("phone"),
        celular=employee_data.get("mobile"),
        cargo_id=employee_data.get("extra_data", {}).get("cargo_id"),
        departamento_id=employee_data.get("extra_data", {}).get("departamento_id"),
        data_admissao=employee_data.get("hire_date"),
        tipo_contrato=tipo_contrato,
    )


# ==================== CANDIDATO → CANDIDATE ====================

def solides_candidato_to_candidate(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia candidato Sólides para Candidate do Conecta PRO.

    Args:
        solides_data: Dados do candidato do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados para criar/atualizar Candidate
    """
    defaults = defaults or {}
    endereco = solides_data.get("endereco") or {}

    # Mapear status
    status_solides = solides_data.get("status", "novo")
    status_map = {
        "novo": "ativo",
        "em_analise": "ativo",
        "aprovado": "ativo",
        "reprovado": "arquivado",
        "contratado": "contratado",
    }
    status = status_map.get(status_solides, "ativo")

    # Mapear fonte
    fonte = solides_data.get("fonte", "site")
    source_map = {
        "linkedin": "linkedin",
        "indeed": "site",
        "indicacao": "indicacao",
        "site": "site",
        "banco_talentos": "banco_talentos",
    }
    source = source_map.get(fonte, "outro")

    # Mapear sexo
    sexo = solides_data.get("sexo")
    gender_map = {"M": "masculino", "F": "feminino", "O": "nao_binario"}
    gender = gender_map.get(sexo) if sexo else None

    return {
        "condominium_id": str(condominio_id),
        # Dados pessoais
        "name": solides_data.get("nome", ""),
        "email": solides_data.get("email"),
        "phone": solides_data.get("telefone"),
        "whatsapp": solides_data.get("celular"),
        "cpf": _clean_document(solides_data.get("cpf")),
        "birth_date": _parse_date(solides_data.get("data_nascimento")),
        "gender": gender,
        "marital_status": _map_marital_status(solides_data.get("estado_civil")),
        # Endereço
        "address": endereco.get("logradouro"),
        "neighborhood": endereco.get("bairro"),
        "city": endereco.get("cidade"),
        "state": endereco.get("estado"),
        "zip_code": _clean_cep(endereco.get("cep")),
        # Profissional
        "headline": solides_data.get("cargo_pretendido"),
        "salary_expectation": solides_data.get("pretensao_salarial"),
        "linkedin_url": solides_data.get("linkedin_url"),
        "portfolio_url": solides_data.get("portfolio_url"),
        "resume_file_path": solides_data.get("curriculo_url"),
        # Disponibilidade
        "available_immediately": solides_data.get("disponibilidade") == "imediata",
        # Status e origem
        "status": status,
        "source": source,
        "source_detail": fonte,
        # Tags e notas
        "tags": solides_data.get("tags", []),
        "internal_notes": solides_data.get("notas"),
        # Formação e experiência (JSON)
        "languages": solides_data.get("idiomas", []),
        # Metadados
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "perfil_disc": solides_data.get("perfil_disc"),
            "perfil_profiler": solides_data.get("perfil_profiler"),
            "formacao": solides_data.get("formacao"),
            "experiencias": solides_data.get("experiencias"),
            "habilidades": solides_data.get("habilidades"),
        },
        **defaults,
    }


def candidate_to_solides_candidato(
    candidate_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mapeia Candidate interno para dados do Sólides.

    Args:
        candidate_data: Dados do Candidate

    Returns:
        Dict para criação no Sólides
    """
    # Mapear sexo
    gender = candidate_data.get("gender")
    sexo_map = {"masculino": "M", "feminino": "F", "nao_binario": "O"}
    sexo = sexo_map.get(gender) if gender else None

    # Mapear estado civil
    marital = candidate_data.get("marital_status")
    estado_civil_map = {
        "solteiro": "solteiro",
        "casado": "casado",
        "divorciado": "divorciado",
        "viuvo": "viuvo",
        "uniao_estavel": "uniao_estavel",
    }
    estado_civil = estado_civil_map.get(marital) if marital else None

    endereco = None
    if candidate_data.get("address"):
        endereco = {
            "logradouro": candidate_data.get("address"),
            "bairro": candidate_data.get("neighborhood"),
            "cidade": candidate_data.get("city"),
            "estado": candidate_data.get("state"),
            "cep": candidate_data.get("zip_code"),
        }

    return {
        "nome": candidate_data.get("name", ""),
        "email": candidate_data.get("email"),
        "cpf": candidate_data.get("cpf"),
        "telefone": candidate_data.get("phone"),
        "celular": candidate_data.get("whatsapp"),
        "data_nascimento": str(candidate_data["birth_date"]) if candidate_data.get("birth_date") else None,
        "sexo": sexo,
        "estado_civil": estado_civil,
        "endereco": endereco,
        "cargo_pretendido": candidate_data.get("headline"),
        "pretensao_salarial": float(candidate_data["salary_expectation"]) if candidate_data.get("salary_expectation") else None,
        "curriculo_url": candidate_data.get("resume_file_path"),
        "linkedin_url": candidate_data.get("linkedin_url"),
        "portfolio_url": candidate_data.get("portfolio_url"),
        "tags": candidate_data.get("tags", []),
        "notas": candidate_data.get("internal_notes"),
        "idiomas": candidate_data.get("languages", []),
    }


# ==================== DEPARTAMENTO ====================

def solides_departamento_to_department(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia departamento Sólides para estrutura interna.

    Args:
        solides_data: Dados do departamento do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados do departamento
    """
    defaults = defaults or {}

    return {
        "condominio_id": condominio_id,
        "name": solides_data.get("nome", ""),
        "code": solides_data.get("codigo"),
        "parent_id": solides_data.get("departamento_pai_id"),
        "manager_id": solides_data.get("gestor_id"),
        "is_active": solides_data.get("ativo", True),
        "extra_data": {
            "solides_id": solides_data.get("id"),
        },
        **defaults,
    }


# ==================== CARGO/POSIÇÃO ====================

def solides_cargo_to_position(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia cargo Sólides para estrutura interna.

    Args:
        solides_data: Dados do cargo do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados do cargo
    """
    defaults = defaults or {}

    return {
        "condominio_id": condominio_id,
        "name": solides_data.get("nome", ""),
        "code": solides_data.get("codigo"),
        "description": solides_data.get("descricao"),
        "department_id": solides_data.get("departamento_id"),
        "level": solides_data.get("nivel"),
        "salary_range_min": solides_data.get("faixa_salarial_min"),
        "salary_range_max": solides_data.get("faixa_salarial_max"),
        "is_active": solides_data.get("ativo", True),
        "extra_data": {
            "solides_id": solides_data.get("id"),
        },
        **defaults,
    }


# ==================== VAGA → JOB POSITION ====================

def solides_vaga_to_job_position(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia vaga Sólides para JobPosition interno.

    Args:
        solides_data: Dados da vaga do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados da vaga
    """
    defaults = defaults or {}

    # Mapear status
    status_solides = solides_data.get("status", "aberta")
    status_map = {
        "aberta": "open",
        "em_andamento": "in_progress",
        "congelada": "paused",
        "encerrada": "closed",
    }
    status = status_map.get(status_solides, "open")

    return {
        "condominium_id": str(condominio_id),
        "title": solides_data.get("titulo", ""),
        "code": solides_data.get("codigo"),
        "description": solides_data.get("descricao"),
        "requirements": solides_data.get("requisitos"),
        "benefits": solides_data.get("beneficios"),
        "location": solides_data.get("local_trabalho"),
        "work_model": solides_data.get("regime_trabalho"),
        "salary_min": solides_data.get("salario_min"),
        "salary_max": solides_data.get("salario_max"),
        "hide_salary": solides_data.get("esconder_salario", True),
        "status": status,
        "positions_count": solides_data.get("quantidade_vagas", 1),
        "positions_filled": solides_data.get("vagas_preenchidas", 0),
        "opening_date": _parse_date(solides_data.get("data_abertura")),
        "closing_date": _parse_date(solides_data.get("data_encerramento")),
        "recruiter_id": solides_data.get("recrutador_id"),
        "manager_id": solides_data.get("gestor_id"),
        "apply_url": solides_data.get("url_inscricao"),
        "tags": solides_data.get("tags", []),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "cargo_id": solides_data.get("cargo_id"),
            "departamento_id": solides_data.get("departamento_id"),
        },
        **defaults,
    }


# ==================== INSCRIÇÃO → APPLICATION ====================

def solides_inscricao_to_application(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia inscrição Sólides para Application interno.

    Args:
        solides_data: Dados da inscrição do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados da inscrição
    """
    defaults = defaults or {}

    # Mapear status
    status_solides = solides_data.get("status", "em_andamento")
    status_map = {
        "em_andamento": "in_progress",
        "aprovado": "approved",
        "reprovado": "rejected",
        "desistencia": "withdrawn",
    }
    status = status_map.get(status_solides, "in_progress")

    # Mapear etapa
    etapa_solides = solides_data.get("etapa", "triagem")
    stage_map = {
        "triagem": "screening",
        "entrevista_rh": "hr_interview",
        "entrevista_tecnica": "technical_interview",
        "proposta": "offer",
    }
    stage = stage_map.get(etapa_solides, "screening")

    return {
        "condominium_id": str(condominio_id),
        "job_position_external_id": str(solides_data.get("vaga_id")),
        "candidate_external_id": str(solides_data.get("candidato_id")),
        "status": status,
        "stage": stage,
        "screening_score": solides_data.get("nota_triagem"),
        "interview_score": solides_data.get("nota_entrevista"),
        "technical_score": solides_data.get("nota_tecnica"),
        "final_score": solides_data.get("nota_final"),
        "feedback": solides_data.get("feedback"),
        "applied_at": _parse_datetime(solides_data.get("data_inscricao")),
        "last_stage_at": _parse_datetime(solides_data.get("data_ultima_etapa")),
        "concluded_at": _parse_datetime(solides_data.get("data_conclusao")),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "historico_etapas": solides_data.get("historico_etapas"),
        },
        **defaults,
    }


# ==================== HELPERS ====================

def _clean_document(doc: Optional[str]) -> Optional[str]:
    """Remove formatação de CPF/CNPJ."""
    if not doc:
        return None
    return doc.replace(".", "").replace("-", "").replace("/", "").strip()


def _clean_cep(cep: Optional[str]) -> Optional[str]:
    """Remove formatação de CEP."""
    if not cep:
        return None
    return cep.replace("-", "").replace(".", "").strip()


def _parse_date(date_val: Any) -> Optional[date]:
    """Parse de data."""
    if not date_val:
        return None

    if isinstance(date_val, date):
        return date_val

    if isinstance(date_val, str):
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(date_val[:10], fmt[:len(date_val[:10])+2]).date()
            except (ValueError, TypeError):
                continue

    return None


def _parse_datetime(dt_val: Any) -> Optional[datetime]:
    """Parse de datetime."""
    if not dt_val:
        return None

    if isinstance(dt_val, datetime):
        return dt_val

    if isinstance(dt_val, str):
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(dt_val[:26], fmt)
            except (ValueError, TypeError):
                continue

    return None


def _map_marital_status(status: Optional[str]) -> Optional[str]:
    """Mapeia estado civil."""
    if not status:
        return None

    status_lower = status.lower()
    mapping = {
        "solteiro": "solteiro",
        "casado": "casado",
        "divorciado": "divorciado",
        "viuvo": "viuvo",
        "viúvo": "viuvo",
        "uniao_estavel": "uniao_estavel",
        "união estável": "uniao_estavel",
        "separado": "divorciado",
    }
    return mapping.get(status_lower)


# ==================== DATA HASH ====================

def compute_solides_entity_hash(entity_type: str, data: Dict[str, Any]) -> str:
    """
    Computa hash de dados da entidade para detectar mudanças.

    Args:
        entity_type: Tipo da entidade
        data: Dados da entidade

    Returns:
        Hash MD5 dos dados relevantes
    """
    import hashlib
    import json

    # Campos relevantes por tipo de entidade
    hash_fields = {
        "colaboradores": ["nome", "email", "cpf", "situacao", "cargo_id", "departamento_id", "data_admissao"],
        "departamentos": ["nome", "codigo", "ativo", "gestor_id"],
        "cargos": ["nome", "codigo", "departamento_id", "nivel"],
        "vagas": ["titulo", "status", "quantidade_vagas", "vagas_preenchidas"],
        "candidatos": ["nome", "email", "cpf", "status"],
        "inscricoes": ["vaga_id", "candidato_id", "status", "etapa", "nota_final"],
        "avaliacoes": ["colaborador_id", "status", "nota_final"],
    }

    fields = hash_fields.get(entity_type, list(data.keys()))

    # Extrair apenas campos relevantes
    hash_data = {k: data.get(k) for k in fields if k in data}

    # Serializar e computar hash
    json_str = json.dumps(hash_data, sort_keys=True, default=str)
    return hashlib.md5(json_str.encode()).hexdigest()
