"""Criar tabelas do modulo de medidas administrativas/disciplinares.

Revision ID: sprint57_disciplinary
Revises:
Create Date: 2026-01-22

Tabelas criadas:
- digital_signatures (assinaturas digitais)
- disciplinary_templates (templates de documentos)
- disciplinary_actions (medidas disciplinares)
"""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

# revision identifiers
revision = "sprint57_disciplinary"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas do modulo disciplinary."""

    # === DIGITAL SIGNATURES ===
    op.create_table(
        "digital_signatures",
        # Identificacao
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("tenant_id", UUID(as_uuid=False), nullable=False, index=True),
        # Signatario
        sa.Column("signer_id", UUID(as_uuid=False), nullable=False, index=True),
        sa.Column("signer_type", sa.String(20), nullable=False, index=True),
        sa.Column("signer_name", sa.String(255), nullable=False),
        sa.Column("signer_cpf", sa.String(14), nullable=True),
        sa.Column("signer_email", sa.String(255), nullable=True),
        # Documento
        sa.Column("document_type", sa.String(50), nullable=False, index=True),
        sa.Column("document_id", UUID(as_uuid=False), nullable=False, index=True),
        # Dados da Assinatura
        sa.Column("signature_data", sa.Text(), nullable=False),
        sa.Column("signature_hash", sa.String(64), nullable=False),
        # Rastreabilidade
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        # Geolocalizacao
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("geolocation_accuracy", sa.Float(), nullable=True),
        sa.Column("geolocation_timestamp", sa.DateTime(), nullable=True),
        # Validacao
        sa.Column("is_valid", sa.Boolean(), default=True, nullable=False),
        sa.Column("validated_at", sa.DateTime(), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(), nullable=True),
        sa.Column("invalidation_reason", sa.String(500), nullable=True),
        # Metadados
        sa.Column("device_fingerprint", sa.String(255), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        # Controle
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Indices para digital_signatures
    op.create_index("ix_digital_signatures_document", "digital_signatures", ["document_type", "document_id"])

    # === DISCIPLINARY TEMPLATES ===
    op.create_table(
        "disciplinary_templates",
        # Identificacao
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("tenant_id", UUID(as_uuid=False), nullable=False, index=True),
        # Dados do Template
        sa.Column("action_type", sa.String(30), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        # Configuracoes
        sa.Column("is_default", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False, index=True),
        # Controle
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=False), nullable=True),
    )

    # === DISCIPLINARY ACTIONS ===
    op.create_table(
        "disciplinary_actions",
        # Identificacao
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("code", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("tenant_id", UUID(as_uuid=False), nullable=False, index=True),
        # Tipo e Status
        sa.Column("action_type", sa.String(30), nullable=False, index=True),
        sa.Column("status", sa.String(30), default="rascunho", nullable=False, index=True),
        # Dados do Funcionario (Snapshot)
        sa.Column("employee_id", UUID(as_uuid=False), nullable=False, index=True),
        sa.Column("employee_name", sa.String(255), nullable=False),
        sa.Column("employee_cpf", sa.String(14), nullable=False),
        sa.Column("employee_position", sa.String(100), nullable=True),
        sa.Column("employee_admission_date", sa.Date(), nullable=True),
        # Local
        sa.Column("post_id", UUID(as_uuid=False), nullable=True, index=True),
        sa.Column("client_id", UUID(as_uuid=False), nullable=True, index=True),
        # Motivo
        sa.Column("reason_category", sa.String(30), nullable=False, index=True),
        sa.Column("reason_description", sa.Text(), nullable=False),
        sa.Column("occurrence_id", UUID(as_uuid=False), nullable=True),
        # Datas
        sa.Column("incident_date", sa.Date(), nullable=False),
        sa.Column("application_date", sa.Date(), nullable=True),
        # Suspensao (se aplicavel)
        sa.Column("suspension_start_date", sa.Date(), nullable=True),
        sa.Column("suspension_end_date", sa.Date(), nullable=True),
        sa.Column("suspension_days", sa.Integer(), nullable=True),
        # Documento
        sa.Column("document_text", sa.Text(), nullable=True),
        sa.Column(
            "document_template_id", UUID(as_uuid=False), sa.ForeignKey("disciplinary_templates.id"), nullable=True
        ),
        sa.Column("document_hash", sa.String(64), nullable=True),
        # Testemunhas
        sa.Column("witness_1_name", sa.String(255), nullable=True),
        sa.Column("witness_1_cpf", sa.String(14), nullable=True),
        sa.Column("witness_2_name", sa.String(255), nullable=True),
        sa.Column("witness_2_cpf", sa.String(14), nullable=True),
        # Aprovacao
        sa.Column("requires_approval", sa.Boolean(), default=True, nullable=False),
        sa.Column("approved_by_id", UUID(as_uuid=False), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("approval_notes", sa.String(500), nullable=True),
        sa.Column("rejected_by_id", UUID(as_uuid=False), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.String(500), nullable=True),
        # Assinaturas do Funcionario
        sa.Column("employee_signature_id", UUID(as_uuid=False), sa.ForeignKey("digital_signatures.id"), nullable=True),
        sa.Column("employee_signed_at", sa.DateTime(), nullable=True),
        sa.Column("employee_refused_sign", sa.Boolean(), default=False, nullable=False),
        sa.Column("refusal_witness_1_name", sa.String(255), nullable=True),
        sa.Column("refusal_witness_1_cpf", sa.String(14), nullable=True),
        sa.Column("refusal_witness_2_name", sa.String(255), nullable=True),
        sa.Column("refusal_witness_2_cpf", sa.String(14), nullable=True),
        # Outras Assinaturas
        sa.Column(
            "supervisor_signature_id", UUID(as_uuid=False), sa.ForeignKey("digital_signatures.id"), nullable=True
        ),
        sa.Column("supervisor_signed_at", sa.DateTime(), nullable=True),
        sa.Column("hr_signature_id", UUID(as_uuid=False), sa.ForeignKey("digital_signatures.id"), nullable=True),
        sa.Column("hr_signed_at", sa.DateTime(), nullable=True),
        # Ciencia
        sa.Column("employee_acknowledged", sa.Boolean(), default=False, nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        # Historico (Snapshot)
        sa.Column("previous_warnings_count", sa.Integer(), default=0, nullable=False),
        sa.Column("previous_suspensions_count", sa.Integer(), default=0, nullable=False),
        # IA e Metadados
        sa.Column("ai_recommendation", JSONB(), nullable=True),
        sa.Column("extra_data", JSONB(), nullable=True, default=dict),
        # Controle
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=False), nullable=True),
    )

    # Indices compostos para disciplinary_actions
    op.create_index("ix_disciplinary_actions_tenant_status", "disciplinary_actions", ["tenant_id", "status"])
    op.create_index("ix_disciplinary_actions_tenant_employee", "disciplinary_actions", ["tenant_id", "employee_id"])
    op.create_index("ix_disciplinary_actions_tenant_date", "disciplinary_actions", ["tenant_id", "incident_date"])

    # Inserir templates padrao
    _insert_default_templates()


def downgrade() -> None:
    """Remove tabelas do modulo disciplinary."""
    op.drop_index("ix_disciplinary_actions_tenant_date", table_name="disciplinary_actions")
    op.drop_index("ix_disciplinary_actions_tenant_employee", table_name="disciplinary_actions")
    op.drop_index("ix_disciplinary_actions_tenant_status", table_name="disciplinary_actions")
    op.drop_table("disciplinary_actions")
    op.drop_table("disciplinary_templates")
    op.drop_index("ix_digital_signatures_document", table_name="digital_signatures")
    op.drop_table("digital_signatures")


def _insert_default_templates():
    """Insere templates padrao para cada tipo de medida."""
    import uuid

    from sqlalchemy import text

    default_tenant_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    templates = [
        {
            "id": str(uuid.uuid4()),
            "tenant_id": default_tenant_id,
            "action_type": "advertencia_verbal",
            "name": "Advertência Verbal - Padrão",
            "description": "Template padrão para advertências verbais",
            "content": """ADVERTÊNCIA VERBAL

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, vem por meio deste documento registrar ADVERTÊNCIA VERBAL ao(a) funcionário(a):

FUNCIONÁRIO: {{employee_name}}
CPF: {{employee_cpf}}
CARGO: {{employee_position}}
DATA DE ADMISSÃO: {{employee_admission_date}}

MOTIVO DA ADVERTÊNCIA:
{{reason_description}}

DATA DO INCIDENTE: {{incident_date}}

O(A) funcionário(a) acima identificado(a) está sendo advertido(a) verbalmente em razão do fato descrito acima, ficando ciente de que a reincidência poderá acarretar em penalidades mais severas, conforme legislação trabalhista vigente.

Esta advertência verbal fica registrada para fins de histórico disciplinar.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
{{employee_name}}
Funcionário(a)
""",
            "is_default": True,
            "is_active": True,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": default_tenant_id,
            "action_type": "advertencia_escrita",
            "name": "Advertência Escrita - Padrão",
            "description": "Template padrão para advertências escritas",
            "content": """ADVERTÊNCIA ESCRITA

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, vem por meio deste documento aplicar ADVERTÊNCIA ESCRITA ao(a) funcionário(a) abaixo identificado(a):

DADOS DO FUNCIONÁRIO:
Nome: {{employee_name}}
CPF: {{employee_cpf}}
Cargo: {{employee_position}}
Data de Admissão: {{employee_admission_date}}
Local de Trabalho: {{post_name}}

HISTÓRICO DISCIPLINAR:
Advertências anteriores: {{previous_warnings}}
Suspensões anteriores: {{previous_suspensions}}

DESCRIÇÃO DA OCORRÊNCIA:
Data do Incidente: {{incident_date}}
Categoria: {{reason_category_display}}

{{reason_description}}

FUNDAMENTAÇÃO LEGAL:
Esta advertência está fundamentada no Art. 482 da CLT e no regulamento interno da empresa, servindo como registro formal de conduta inadequada.

CIÊNCIA:
O(A) funcionário(a) declara estar ciente de que:
1. A reincidência poderá resultar em suspensão disciplinar;
2. Novas infrações poderão ensejar rescisão por justa causa;
3. Esta advertência ficará arquivada em seu prontuário.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
{{employee_name}}
Funcionário(a)

TESTEMUNHAS (em caso de recusa de assinatura):

1. _________________________________
   Nome: {{witness_1_name}}
   CPF: {{witness_1_cpf}}

2. _________________________________
   Nome: {{witness_2_name}}
   CPF: {{witness_2_cpf}}
""",
            "is_default": True,
            "is_active": True,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": default_tenant_id,
            "action_type": "suspensao",
            "name": "Suspensão Disciplinar - Padrão",
            "description": "Template padrão para suspensões disciplinares",
            "content": """TERMO DE SUSPENSÃO DISCIPLINAR

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, vem por meio deste documento aplicar SUSPENSÃO DISCIPLINAR ao(a) funcionário(a) abaixo identificado(a):

DADOS DO FUNCIONÁRIO:
Nome: {{employee_name}}
CPF: {{employee_cpf}}
Cargo: {{employee_position}}
Data de Admissão: {{employee_admission_date}}
Local de Trabalho: {{post_name}}

HISTÓRICO DISCIPLINAR:
Advertências anteriores: {{previous_warnings}}
Suspensões anteriores: {{previous_suspensions}}

PERÍODO DA SUSPENSÃO:
Data de Início: {{suspension_start_date}}
Data de Término: {{suspension_end_date}}
Total de Dias: {{suspension_days}} dias

DESCRIÇÃO DA OCORRÊNCIA:
Data do Incidente: {{incident_date}}
Categoria: {{reason_category_display}}

{{reason_description}}

FUNDAMENTAÇÃO LEGAL:
Esta suspensão disciplinar está fundamentada no Art. 474 da CLT, limitada ao máximo de 30 dias consecutivos, e decorre das seguintes justificativas:
- Reincidência em condutas inadequadas apesar de advertências anteriores;
- Gravidade da falta cometida que justifica medida mais severa.

CONSEQUÊNCIAS:
1. Durante o período de suspensão, o contrato de trabalho fica suspenso;
2. Não haverá remuneração correspondente aos dias de suspensão;
3. O período de suspensão não será computado para férias e 13º salário;
4. O(A) funcionário(a) deverá retornar ao trabalho no primeiro dia útil após o término da suspensão.

CIÊNCIA:
O(A) funcionário(a) declara estar ciente de que nova infração poderá resultar em demissão por justa causa.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
Departamento de Recursos Humanos

_________________________________
{{employee_name}}
Funcionário(a)

TESTEMUNHAS (em caso de recusa de assinatura):

1. _________________________________
   Nome: {{witness_1_name}}
   CPF: {{witness_1_cpf}}

2. _________________________________
   Nome: {{witness_2_name}}
   CPF: {{witness_2_cpf}}
""",
            "is_default": True,
            "is_active": True,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": default_tenant_id,
            "action_type": "demissao_justa_causa",
            "name": "Demissão por Justa Causa - Padrão",
            "description": "Template padrão para demissões por justa causa",
            "content": """TERMO DE RESCISÃO DO CONTRATO DE TRABALHO POR JUSTA CAUSA

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, comunica a RESCISÃO DO CONTRATO DE TRABALHO POR JUSTA CAUSA do(a) funcionário(a) abaixo identificado(a):

DADOS DO FUNCIONÁRIO:
Nome: {{employee_name}}
CPF: {{employee_cpf}}
Cargo: {{employee_position}}
Data de Admissão: {{employee_admission_date}}
Data da Rescisão: {{application_date}}
Local de Trabalho: {{post_name}}

HISTÓRICO DISCIPLINAR:
Advertências anteriores: {{previous_warnings}}
Suspensões anteriores: {{previous_suspensions}}

DESCRIÇÃO DA FALTA GRAVE:
Data do Incidente: {{incident_date}}
Categoria: {{reason_category_display}}

{{reason_description}}

FUNDAMENTAÇÃO LEGAL:
A presente rescisão por justa causa está fundamentada no Art. 482 da Consolidação das Leis do Trabalho (CLT).

VERBAS RESCISÓRIAS:
Conforme Art. 477 da CLT, o(a) funcionário(a) terá direito apenas às seguintes verbas:
- Saldo de salário
- Férias vencidas + 1/3 (se houver)

NÃO terá direito a:
- Aviso prévio
- Férias proporcionais + 1/3
- 13º salário proporcional
- Multa de 40% do FGTS
- Seguro-desemprego

CIÊNCIA:
O(A) funcionário(a) declara ciência da presente rescisão e de seus motivos, reservando-se o direito de questioná-la perante a Justiça do Trabalho.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
Departamento de Recursos Humanos

_________________________________
{{employee_name}}
Funcionário(a)

TESTEMUNHAS:

1. _________________________________
   Nome: {{witness_1_name}}
   CPF: {{witness_1_cpf}}

2. _________________________________
   Nome: {{witness_2_name}}
   CPF: {{witness_2_cpf}}
""",
            "is_default": True,
            "is_active": True,
        },
    ]

    conn = op.get_bind()

    for template in templates:
        conn.execute(
            text("""
                INSERT INTO disciplinary_templates
                (id, tenant_id, action_type, name, description, content, is_default, is_active, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :action_type, :name, :description, :content, :is_default, :is_active, NOW(), NOW())
                ON CONFLICT DO NOTHING
            """),
            template,
        )
