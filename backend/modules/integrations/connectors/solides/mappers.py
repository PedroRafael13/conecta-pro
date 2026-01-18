"""
Mappers para Sólides - Gestão de Pessoas (RH + DP)
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
    SolidesOcorrencia,
    SolidesOcorrenciaCreate,
    SolidesAbsenteismo,
    SolidesAbsenteismoCreate,
    SolidesPassaporte,
    SolidesUnidade,
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
        "Jovem Aprendiz": "apprentice",
    }
    contract_type = contract_type_map.get(tipo_contrato, "clt")

    # Mapear sexo
    sexo = solides_data.get("sexo")
    gender_map = {"M": "masculino", "F": "feminino", "O": "outro"}
    gender = gender_map.get(sexo) if sexo else None

    # Extrair nome do cargo e departamento
    cargo_nome = None
    if isinstance(solides_data.get("cargo"), dict):
        cargo_nome = solides_data["cargo"].get("nome")
    elif solides_data.get("cargo_nome"):
        cargo_nome = solides_data["cargo_nome"]

    departamento_nome = None
    if isinstance(solides_data.get("departamento"), dict):
        departamento_nome = solides_data["departamento"].get("nome")
    elif solides_data.get("departamento_nome"):
        departamento_nome = solides_data["departamento_nome"]

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
        "position_name": cargo_nome,
        "department_name": departamento_nome,
        "manager_name": solides_data.get("gestor_nome"),
        # Contrato
        "hire_date": _parse_date(solides_data.get("data_admissao")),
        "termination_date": _parse_date(solides_data.get("data_demissao")),
        "contract_type": contract_type,
        "work_regime": solides_data.get("regime_trabalho"),
        "work_schedule": solides_data.get("jornada_trabalho"),
        "salary": solides_data.get("salario"),
        # Dados DP
        "ctps_number": solides_data.get("ctps_numero"),
        "ctps_series": solides_data.get("ctps_serie"),
        "ctps_state": solides_data.get("ctps_uf"),
        "pis_number": solides_data.get("pis"),
        "voter_id": solides_data.get("titulo_eleitor"),
        "military_certificate": solides_data.get("certificado_reservista"),
        # Dependentes
        "dependents": solides_data.get("dependentes"),
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
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "cargo_id": solides_data.get("cargo_id"),
            "departamento_id": solides_data.get("departamento_id"),
            "unidade_id": solides_data.get("unidade_id"),
            "gestor_id": solides_data.get("gestor_id"),
            "dados_adicionais": solides_data.get("dados_adicionais"),
        },
        **defaults,
    }


def employee_to_solides_colaborador(
    employee_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mapeia dados de funcionário interno para criação/atualização no Sólides.

    Args:
        employee_data: Dados do funcionário

    Returns:
        Dict para API Sólides
    """
    # Mapear tipo de contrato
    contract_map = {
        "clt": "CLT",
        "pj": "PJ",
        "intern": "Estagio",
        "temporary": "Temporario",
        "outsourced": "Terceirizado",
        "apprentice": "Jovem Aprendiz",
    }
    tipo_contrato = contract_map.get(
        employee_data.get("contract_type", "clt"),
        "CLT"
    )

    # Mapear sexo
    gender = employee_data.get("gender")
    sexo_map = {"masculino": "M", "feminino": "F", "outro": "O"}
    sexo = sexo_map.get(gender) if gender else None

    # Mapear status
    status = employee_data.get("status", "active")
    situacao_map = {
        "active": "ativo",
        "inactive": "inativo",
        "on_leave": "afastado",
        "terminated": "demitido",
    }
    situacao = situacao_map.get(status, "ativo")

    # Montar endereço
    endereco = None
    if employee_data.get("address_street"):
        endereco = {
            "logradouro": employee_data.get("address_street"),
            "numero": employee_data.get("address_number"),
            "complemento": employee_data.get("address_complement"),
            "bairro": employee_data.get("address_neighborhood"),
            "cidade": employee_data.get("address_city"),
            "estado": employee_data.get("address_state"),
            "cep": employee_data.get("address_zipcode"),
        }

    extra_data = employee_data.get("extra_data", {})

    result = {
        "nome": employee_data.get("name", ""),
        "email": employee_data.get("email"),
        "cpf": employee_data.get("cpf"),
        "rg": employee_data.get("rg"),
        "data_nascimento": _format_date(employee_data.get("birth_date")),
        "sexo": sexo,
        "estado_civil": _reverse_map_marital_status(employee_data.get("marital_status")),
        "telefone": employee_data.get("phone"),
        "celular": employee_data.get("mobile"),
        "endereco": endereco,
        "matricula": employee_data.get("registration_number"),
        "data_admissao": _format_date(employee_data.get("hire_date")),
        "data_demissao": _format_date(employee_data.get("termination_date")),
        "tipo_contrato": tipo_contrato,
        "regime_trabalho": employee_data.get("work_regime"),
        "jornada_trabalho": employee_data.get("work_schedule"),
        "salario": float(employee_data["salary"]) if employee_data.get("salary") else None,
        "situacao": situacao,
        # Dados DP
        "ctps_numero": employee_data.get("ctps_number"),
        "ctps_serie": employee_data.get("ctps_series"),
        "ctps_uf": employee_data.get("ctps_state"),
        "pis": employee_data.get("pis_number"),
        "titulo_eleitor": employee_data.get("voter_id"),
        "certificado_reservista": employee_data.get("military_certificate"),
        # IDs de referência
        "cargo_id": extra_data.get("cargo_id"),
        "departamento_id": extra_data.get("departamento_id"),
        "unidade_id": extra_data.get("unidade_id"),
        "gestor_id": extra_data.get("gestor_id"),
    }

    # Remover campos None
    return {k: v for k, v in result.items() if v is not None}


# ==================== OCORRÊNCIA ====================

def solides_ocorrencia_to_occurrence(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia ocorrência Sólides para Occurrence interno.

    Args:
        solides_data: Dados da ocorrência do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados da ocorrência
    """
    defaults = defaults or {}

    # Mapear tipo de ocorrência
    tipo_solides = solides_data.get("tipo", "outro")
    tipo_map = {
        "advertencia_verbal": "verbal_warning",
        "advertencia_escrita": "written_warning",
        "suspensao": "suspension",
        "elogio": "praise",
        "promocao": "promotion",
        "merito": "merit",
        "feedback": "feedback",
        "anotacao": "note",
        "treinamento": "training",
        "outro": "other",
    }
    occurrence_type = tipo_map.get(tipo_solides, "other")

    return {
        "condominium_id": str(condominio_id),
        "employee_external_id": str(solides_data.get("colaborador_id")),
        "employee_name": solides_data.get("colaborador_nome"),
        "type": occurrence_type,
        "description": solides_data.get("descricao"),
        "date": _parse_date(solides_data.get("data")),
        "effective_date": _parse_date(solides_data.get("data_vigencia")),
        "duration_days": solides_data.get("duracao_dias"),
        "raise_amount": solides_data.get("valor_aumento"),
        "raise_percentage": solides_data.get("percentual_aumento"),
        "new_position_id": solides_data.get("novo_cargo_id"),
        "new_position_name": solides_data.get("novo_cargo_nome"),
        "registered_by_id": solides_data.get("registrado_por_id"),
        "registered_by_name": solides_data.get("registrado_por_nome"),
        "attachments": solides_data.get("anexos"),
        "notes": solides_data.get("observacoes"),
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "dados_adicionais": solides_data.get("dados_adicionais"),
        },
        **defaults,
    }


def occurrence_to_solides_ocorrencia(
    occurrence_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mapeia Occurrence interno para dados da API Sólides.

    Args:
        occurrence_data: Dados da ocorrência

    Returns:
        Dict para API Sólides
    """
    # Mapear tipo reverso
    tipo_map = {
        "verbal_warning": "advertencia_verbal",
        "written_warning": "advertencia_escrita",
        "suspension": "suspensao",
        "praise": "elogio",
        "promotion": "promocao",
        "merit": "merito",
        "feedback": "feedback",
        "note": "anotacao",
        "training": "treinamento",
        "other": "outro",
    }
    tipo = tipo_map.get(occurrence_data.get("type", "other"), "outro")

    result = {
        "colaborador_id": int(occurrence_data.get("employee_external_id", 0)),
        "tipo": tipo,
        "descricao": occurrence_data.get("description"),
        "data": _format_date(occurrence_data.get("date")),
        "data_vigencia": _format_date(occurrence_data.get("effective_date")),
        "duracao_dias": occurrence_data.get("duration_days"),
        "valor_aumento": float(occurrence_data["raise_amount"]) if occurrence_data.get("raise_amount") else None,
        "percentual_aumento": float(occurrence_data["raise_percentage"]) if occurrence_data.get("raise_percentage") else None,
        "novo_cargo_id": occurrence_data.get("new_position_id"),
        "observacoes": occurrence_data.get("notes"),
    }

    return {k: v for k, v in result.items() if v is not None}


# ==================== ABSENTEÍSMO ====================

def solides_absenteismo_to_absence(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia absenteísmo Sólides para Absence interno.

    Args:
        solides_data: Dados do absenteísmo do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados do absenteísmo
    """
    defaults = defaults or {}

    # Mapear tipo de absenteísmo
    tipo_solides = solides_data.get("tipo", "falta")
    tipo_map = {
        "falta": "absence",
        "atraso": "late_arrival",
        "saida_antecipada": "early_departure",
        "atestado_medico": "medical_leave",
        "licenca_maternidade": "maternity_leave",
        "licenca_paternidade": "paternity_leave",
        "licenca_casamento": "wedding_leave",
        "licenca_luto": "bereavement_leave",
        "afastamento_inss": "inss_leave",
        "ferias": "vacation",
        "folga": "day_off",
        "outro": "other",
    }
    absence_type = tipo_map.get(tipo_solides, "absence")

    return {
        "condominium_id": str(condominio_id),
        "employee_external_id": str(solides_data.get("colaborador_id")),
        "employee_name": solides_data.get("colaborador_nome"),
        "type": absence_type,
        "reason": solides_data.get("motivo"),
        "start_date": _parse_date(solides_data.get("data_inicio")),
        "end_date": _parse_date(solides_data.get("data_fim")),
        "hours": solides_data.get("horas"),
        "minutes_late": solides_data.get("minutos_atraso"),
        "justified": solides_data.get("justificado", False),
        "document_url": solides_data.get("documento_anexo"),
        "icd_code": solides_data.get("cid"),
        "payroll_deduction": solides_data.get("desconto_em_folha", True),
        "days_deducted": solides_data.get("dias_descontados"),
        "inss_benefit_number": solides_data.get("numero_beneficio_inss"),
        "inss_start_date": _parse_date(solides_data.get("data_inicio_inss")),
        "inss_end_date": _parse_date(solides_data.get("data_fim_inss")),
        "registered_by_id": solides_data.get("registrado_por_id"),
        "registered_by_name": solides_data.get("registrado_por_nome"),
        "notes": solides_data.get("observacoes"),
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "dados_adicionais": solides_data.get("dados_adicionais"),
        },
        **defaults,
    }


def absence_to_solides_absenteismo(
    absence_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mapeia Absence interno para dados da API Sólides.

    Args:
        absence_data: Dados do absenteísmo

    Returns:
        Dict para API Sólides
    """
    # Mapear tipo reverso
    tipo_map = {
        "absence": "falta",
        "late_arrival": "atraso",
        "early_departure": "saida_antecipada",
        "medical_leave": "atestado_medico",
        "maternity_leave": "licenca_maternidade",
        "paternity_leave": "licenca_paternidade",
        "wedding_leave": "licenca_casamento",
        "bereavement_leave": "licenca_luto",
        "inss_leave": "afastamento_inss",
        "vacation": "ferias",
        "day_off": "folga",
        "other": "outro",
    }
    tipo = tipo_map.get(absence_data.get("type", "absence"), "falta")

    result = {
        "colaborador_id": int(absence_data.get("employee_external_id", 0)),
        "tipo": tipo,
        "motivo": absence_data.get("reason"),
        "data_inicio": _format_date(absence_data.get("start_date")),
        "data_fim": _format_date(absence_data.get("end_date")),
        "horas": float(absence_data["hours"]) if absence_data.get("hours") else None,
        "justificado": absence_data.get("justified", False),
        "documento_anexo": absence_data.get("document_url"),
        "cid": absence_data.get("icd_code"),
        "desconto_em_folha": absence_data.get("payroll_deduction", True),
        "observacoes": absence_data.get("notes"),
    }

    return {k: v for k, v in result.items() if v is not None}


# ==================== PASSAPORTE COMPORTAMENTAL ====================

def solides_passaporte_to_behavioral_profile(
    solides_data: Dict[str, Any],
    condominio_id: UUID,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mapeia passaporte comportamental Sólides para dados internos.

    Args:
        solides_data: Dados do passaporte do Sólides
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados do perfil comportamental
    """
    defaults = defaults or {}

    # Extrair perfil DISC
    perfil_disc = solides_data.get("perfil_disc", {})

    return {
        "condominium_id": str(condominio_id),
        "employee_external_id": str(solides_data.get("colaborador_id")),
        "employee_name": solides_data.get("colaborador_nome"),
        # Perfil DISC
        "disc_profile": perfil_disc,
        "dominant_profile": solides_data.get("perfil_predominante"),
        "secondary_profiles": solides_data.get("perfis_secundarios"),
        "intensity": solides_data.get("intensidade"),
        # Competências
        "competencies": solides_data.get("competencias"),
        "strengths": solides_data.get("pontos_fortes"),
        "development_points": solides_data.get("pontos_desenvolvimento"),
        # Estilo
        "communication_style": solides_data.get("estilo_comunicacao"),
        "leadership_style": solides_data.get("estilo_lideranca"),
        "ideal_environment": solides_data.get("ambiente_ideal"),
        "motivators": solides_data.get("motivadores"),
        "demotivators": solides_data.get("desmotivadores"),
        # Compatibilidade
        "position_compatibility": solides_data.get("compatibilidade_cargo"),
        "team_compatibility": solides_data.get("compatibilidade_equipe"),
        # Relatórios
        "report_url": solides_data.get("relatorio_url"),
        "report_pdf_url": solides_data.get("relatorio_pdf_url"),
        # Metadados
        "assessment_date": _parse_datetime(solides_data.get("data_avaliacao")),
        "instrument_version": solides_data.get("versao_instrumento"),
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
        "extra_data": solides_data.get("dados_adicionais"),
        **defaults,
    }


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
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
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

    result = {
        "nome": candidate_data.get("name", ""),
        "email": candidate_data.get("email"),
        "cpf": candidate_data.get("cpf"),
        "telefone": candidate_data.get("phone"),
        "celular": candidate_data.get("whatsapp"),
        "data_nascimento": _format_date(candidate_data.get("birth_date")),
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

    return {k: v for k, v in result.items() if v is not None}


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
        "parent_external_id": str(solides_data.get("departamento_pai_id")) if solides_data.get("departamento_pai_id") else None,
        "manager_external_id": str(solides_data.get("gestor_id")) if solides_data.get("gestor_id") else None,
        "unit_external_id": str(solides_data.get("unidade_id")) if solides_data.get("unidade_id") else None,
        "is_active": solides_data.get("ativo", True),
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
        "extra_data": {
            "solides_id": solides_data.get("id"),
        },
        **defaults,
    }


def department_to_solides_departamento(
    department_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mapeia Department interno para API Sólides.
    """
    result = {
        "nome": department_data.get("name"),
        "codigo": department_data.get("code"),
        "departamento_pai_id": int(department_data["parent_external_id"]) if department_data.get("parent_external_id") else None,
        "gestor_id": int(department_data["manager_external_id"]) if department_data.get("manager_external_id") else None,
        "unidade_id": int(department_data["unit_external_id"]) if department_data.get("unit_external_id") else None,
        "ativo": department_data.get("is_active", True),
    }

    return {k: v for k, v in result.items() if v is not None}


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
        "department_external_id": str(solides_data.get("departamento_id")) if solides_data.get("departamento_id") else None,
        "cbo_code": solides_data.get("cbo_codigo"),
        "level": solides_data.get("nivel"),
        "salary_range_min": solides_data.get("faixa_salarial_min"),
        "salary_range_max": solides_data.get("faixa_salarial_max"),
        "is_active": solides_data.get("ativo", True),
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "cbo_id": solides_data.get("cbo_id"),
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
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
        "extra_data": {
            "solides_id": solides_data.get("id"),
            "cargo_id": solides_data.get("cargo_id"),
            "departamento_id": solides_data.get("departamento_id"),
            "unidade_id": solides_data.get("unidade_id"),
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
        "solides_id": str(solides_data.get("id")) if solides_data.get("id") else None,
        "sync_source": "solides",
        "last_synced_at": datetime.utcnow(),
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

    if isinstance(date_val, datetime):
        return date_val.date()

    if isinstance(date_val, str):
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]
        for fmt in formats:
            try:
                return datetime.strptime(date_val[:10], fmt[:min(len(fmt), len(date_val[:10])+2)]).date()
            except (ValueError, TypeError):
                continue

    return None


def _format_date(date_val: Any) -> Optional[str]:
    """Formata data para string ISO."""
    if not date_val:
        return None

    if isinstance(date_val, (date, datetime)):
        return date_val.strftime("%Y-%m-%d")

    if isinstance(date_val, str):
        return date_val[:10] if len(date_val) >= 10 else date_val

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


def _reverse_map_marital_status(status: Optional[str]) -> Optional[str]:
    """Mapeia estado civil reverso (interno -> Sólides)."""
    if not status:
        return None

    mapping = {
        "solteiro": "solteiro",
        "casado": "casado",
        "divorciado": "divorciado",
        "viuvo": "viuvo",
        "uniao_estavel": "uniao_estavel",
    }
    return mapping.get(status)


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
        "colaboradores": ["nome", "email", "cpf", "situacao", "cargo_id", "departamento_id", "data_admissao", "data_demissao", "salario"],
        "departamentos": ["nome", "codigo", "ativo", "gestor_id", "departamento_pai_id"],
        "cargos": ["nome", "codigo", "departamento_id", "nivel", "ativo"],
        "unidades": ["nome", "codigo", "ativo"],
        "vagas": ["titulo", "status", "quantidade_vagas", "vagas_preenchidas"],
        "candidatos": ["nome", "email", "cpf", "status"],
        "inscricoes": ["vaga_id", "candidato_id", "status", "etapa", "nota_final"],
        "avaliacoes": ["colaborador_id", "status", "nota_final"],
        "ocorrencias": ["colaborador_id", "tipo", "data", "descricao"],
        "absenteismos": ["colaborador_id", "tipo", "data_inicio", "data_fim", "justificado"],
        "passaportes": ["colaborador_id", "perfil_predominante", "intensidade"],
    }

    fields = hash_fields.get(entity_type, list(data.keys()))

    # Extrair apenas campos relevantes
    hash_data = {k: data.get(k) for k in fields if k in data}

    # Serializar e computar hash
    json_str = json.dumps(hash_data, sort_keys=True, default=str)
    return hashlib.md5(json_str.encode()).hexdigest()


def detect_changes(
    old_data: Dict[str, Any],
    new_data: Dict[str, Any],
    entity_type: str
) -> Dict[str, Dict[str, Any]]:
    """
    Detecta mudanças entre versões de dados.

    Args:
        old_data: Dados antigos
        new_data: Dados novos
        entity_type: Tipo da entidade

    Returns:
        Dict com campos alterados {campo: {old: valor_antigo, new: valor_novo}}
    """
    # Campos a comparar por tipo
    compare_fields = {
        "colaboradores": ["nome", "email", "situacao", "cargo_id", "departamento_id", "salario", "data_demissao"],
        "departamentos": ["nome", "codigo", "ativo", "gestor_id"],
        "cargos": ["nome", "codigo", "ativo"],
        "ocorrencias": ["tipo", "descricao", "data"],
        "absenteismos": ["tipo", "motivo", "data_inicio", "data_fim", "justificado"],
    }

    fields = compare_fields.get(entity_type, list(set(old_data.keys()) | set(new_data.keys())))

    changes = {}
    for field in fields:
        old_value = old_data.get(field)
        new_value = new_data.get(field)

        # Normalizar valores para comparação
        if isinstance(old_value, (date, datetime)):
            old_value = str(old_value)
        if isinstance(new_value, (date, datetime)):
            new_value = str(new_value)

        if old_value != new_value:
            changes[field] = {"old": old_data.get(field), "new": new_data.get(field)}

    return changes
