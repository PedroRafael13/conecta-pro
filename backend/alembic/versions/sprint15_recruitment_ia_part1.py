"""Sprint 15 - Recrutamento IA Parte 1

Cria tabelas para:
- JobPosition (vagas)
- Candidate (candidatos)
- Application (candidaturas)
- CandidateEducation (formação)
- CandidateExperience (experiência)
- CandidateSkill (habilidades)

Revision ID: sprint15_recruitment
Revises: sprint14_cpq
Create Date: 2026-01-07

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers, used by Alembic.
revision: str = "sprint15_recruitment"
down_revision: Union[str, None] = "sprint14_cpq"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica migração."""

    # 1. Tabela de Vagas (Job Positions)
    op.create_table(
        "job_positions",
        sa.Column("id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=False), nullable=True),
        # Identificação
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("benefits", sa.Text(), nullable=True),
        # Classificação
        sa.Column("department", sa.String(50), nullable=True),
        sa.Column("position_type", sa.String(30), nullable=False),  # CLT, PJ, etc
        sa.Column("position_level", sa.String(30), nullable=True),  # Junior, Pleno, Senior
        sa.Column("work_model", sa.String(20), nullable=True),  # Presencial, Remoto, Híbrido
        # Localização
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("country", sa.String(50), server_default="Brasil"),
        sa.Column("address", sa.String(300), nullable=True),
        # Remuneração
        sa.Column("salary_min", sa.Numeric(15, 2), nullable=True),
        sa.Column("salary_max", sa.Numeric(15, 2), nullable=True),
        sa.Column("show_salary", sa.Boolean(), server_default="false"),
        sa.Column("additional_benefits", postgresql.JSONB(), nullable=True),
        # Quantidade
        sa.Column("vacancies", sa.Integer(), server_default="1"),
        sa.Column("filled_count", sa.Integer(), server_default="0"),
        # Status e Datas
        sa.Column("status", sa.String(20), nullable=False, server_default="rascunho"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        # Requisitos
        sa.Column("required_skills", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("desired_skills", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("min_experience_years", sa.Integer(), nullable=True),
        sa.Column("education_level", sa.String(50), nullable=True),
        sa.Column("languages", postgresql.JSONB(), nullable=True),
        # Processo seletivo
        sa.Column("selection_steps", postgresql.JSONB(), nullable=True),
        sa.Column("responsible_id", postgresql.UUID(as_uuid=False), nullable=True),
        # Integração
        sa.Column("linkedin_job_id", sa.String(100), nullable=True),
        sa.Column("indeed_job_id", sa.String(100), nullable=True),
        sa.Column("external_url", sa.String(500), nullable=True),
        # Controle
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_positions_tenant_id", "job_positions", ["tenant_id"])
    op.create_index("ix_job_positions_status", "job_positions", ["status"])
    op.create_index("ix_job_positions_department", "job_positions", ["department"])

    # 2. Tabela de Candidatos
    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        # Dados pessoais
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("whatsapp", sa.String(20), nullable=True),
        sa.Column("cpf", sa.String(14), nullable=True),
        sa.Column("rg", sa.String(20), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(30), nullable=True),
        sa.Column("marital_status", sa.String(30), nullable=True),
        # Endereço
        sa.Column("address", sa.String(300), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("zip_code", sa.String(10), nullable=True),
        sa.Column("country", sa.String(50), server_default="Brasil"),
        # Profissional
        sa.Column("headline", sa.String(200), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("current_company", sa.String(200), nullable=True),
        sa.Column("current_position", sa.String(200), nullable=True),
        sa.Column("salary_expectation", sa.Numeric(15, 2), nullable=True),
        sa.Column("availability", sa.String(50), nullable=True),
        # Currículo
        sa.Column("resume_url", sa.String(500), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("resume_parsed", postgresql.JSONB(), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        # Social
        sa.Column("linkedin_url", sa.String(300), nullable=True),
        sa.Column("linkedin_id", sa.String(100), nullable=True),
        sa.Column("github_url", sa.String(300), nullable=True),
        sa.Column("portfolio_url", sa.String(300), nullable=True),
        # Origem e Status
        sa.Column("source", sa.String(30), nullable=True),
        sa.Column("status", sa.String(20), server_default="ativo"),
        # Scoring IA
        sa.Column("ai_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("ai_analysis", postgresql.JSONB(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        # Controle
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidates_tenant_id", "candidates", ["tenant_id"])
    op.create_index("ix_candidates_email", "candidates", ["email"])
    op.create_index("ix_candidates_cpf", "candidates", ["cpf"])
    op.create_index("ix_candidates_status", "candidates", ["status"])

    # 3. Tabela de Candidaturas (Applications)
    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        sa.Column("job_position_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=False), nullable=False),
        # Status e Etapa
        sa.Column("status", sa.String(30), server_default="nova"),
        sa.Column("current_step", sa.String(50), nullable=True),
        sa.Column("step_order", sa.Integer(), server_default="1"),
        # Avaliação
        sa.Column("recruiter_notes", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("ai_match_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("ai_match_details", postgresql.JSONB(), nullable=True),
        # Histórico de etapas
        sa.Column("step_history", postgresql.JSONB(), nullable=True),
        # Carta de apresentação
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column("salary_expectation", sa.Numeric(15, 2), nullable=True),
        sa.Column("availability_date", sa.Date(), nullable=True),
        # Datas importantes
        sa.Column("applied_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("screened_at", sa.DateTime(), nullable=True),
        sa.Column("interviewed_at", sa.DateTime(), nullable=True),
        sa.Column("offered_at", sa.DateTime(), nullable=True),
        sa.Column("hired_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(), nullable=True),
        # Motivo de rejeição/desistência
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("withdrawal_reason", sa.Text(), nullable=True),
        # Responsável
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=False), nullable=True),
        # Controle
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["job_position_id"], ["job_positions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("job_position_id", "candidate_id", name="uq_application_job_candidate"),
    )
    op.create_index("ix_applications_tenant_id", "applications", ["tenant_id"])
    op.create_index("ix_applications_job_position_id", "applications", ["job_position_id"])
    op.create_index("ix_applications_candidate_id", "applications", ["candidate_id"])
    op.create_index("ix_applications_status", "applications", ["status"])

    # 4. Tabela de Formação (Education)
    op.create_table(
        "candidate_educations",
        sa.Column("id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=False), nullable=False),
        # Dados do curso
        sa.Column("institution", sa.String(200), nullable=False),
        sa.Column("degree", sa.String(100), nullable=True),
        sa.Column("field_of_study", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        # Datas
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default="false"),
        # Status
        sa.Column("status", sa.String(30), nullable=True),  # Completo, Em andamento, Trancado
        sa.Column("grade", sa.String(20), nullable=True),
        # Controle
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_candidate_educations_candidate_id", "candidate_educations", ["candidate_id"])

    # 5. Tabela de Experiência
    op.create_table(
        "candidate_experiences",
        sa.Column("id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=False), nullable=False),
        # Dados da experiência
        sa.Column("company", sa.String(200), nullable=False),
        sa.Column("position", sa.String(200), nullable=False),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("achievements", sa.Text(), nullable=True),
        # Datas
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default="false"),
        # Detalhes
        sa.Column("employment_type", sa.String(30), nullable=True),  # CLT, PJ, etc
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("salary", sa.Numeric(15, 2), nullable=True),
        # Controle
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_candidate_experiences_candidate_id", "candidate_experiences", ["candidate_id"])

    # 6. Tabela de Habilidades
    op.create_table(
        "candidate_skills",
        sa.Column("id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=False), nullable=False),
        # Habilidade
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=True),  # Técnica, Comportamental, Idioma
        sa.Column("level", sa.String(30), nullable=True),  # Básico, Intermediário, Avançado
        sa.Column("years_of_experience", sa.Integer(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="false"),
        sa.Column("endorsements_count", sa.Integer(), server_default="0"),
        # Controle
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_candidate_skills_candidate_id", "candidate_skills", ["candidate_id"])
    op.create_index("ix_candidate_skills_name", "candidate_skills", ["name"])

    # 7. Tabela de Entrevistas
    op.create_table(
        "interviews",
        sa.Column("id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        sa.Column("application_id", postgresql.UUID(as_uuid=False), nullable=False),
        # Tipo e formato
        sa.Column("interview_type", sa.String(30), nullable=False),  # Técnica, RH, Gestor, Final
        sa.Column("format", sa.String(20), nullable=False),  # Presencial, Video, Telefone
        # Agendamento
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), server_default="60"),
        sa.Column("location", sa.String(300), nullable=True),
        sa.Column("meeting_url", sa.String(500), nullable=True),
        # Participantes
        sa.Column("interviewer_ids", postgresql.ARRAY(postgresql.UUID()), nullable=True),
        sa.Column("interviewer_notes", postgresql.JSONB(), nullable=True),
        # Status e Resultado
        sa.Column("status", sa.String(20), server_default="agendada"),
        sa.Column("result", sa.String(20), nullable=True),  # Aprovado, Reprovado, Pendente
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        # Datas
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        # Gravação
        sa.Column("recording_url", sa.String(500), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        # Controle
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_interviews_tenant_id", "interviews", ["tenant_id"])
    op.create_index("ix_interviews_application_id", "interviews", ["application_id"])
    op.create_index("ix_interviews_scheduled_at", "interviews", ["scheduled_at"])
    op.create_index("ix_interviews_status", "interviews", ["status"])


def downgrade() -> None:
    """Reverte migração."""
    op.drop_table("interviews")
    op.drop_table("candidate_skills")
    op.drop_table("candidate_experiences")
    op.drop_table("candidate_educations")
    op.drop_table("applications")
    op.drop_table("candidates")
    op.drop_table("job_positions")
