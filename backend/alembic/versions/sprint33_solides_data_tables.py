"""Sprint 33: Sólides Data Tables - Tabelas de dados importados

Cria tabelas para armazenar dados históricos importados do Sólides:
- solides_employees: Colaboradores
- solides_departments: Departamentos
- solides_positions: Cargos
- solides_occurrences: Ocorrências
- solides_absences: Absenteísmos/Afastamentos
- solides_workplaces: Locais de trabalho/Unidades
- solides_work_schedules: Escalas de trabalho
- solides_cost_centers: Centros de custo

Revision ID: sprint33_solides_data_tables
Revises: sprint33_solides_integration
Create Date: 2026-01-18 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sprint33_solides_data_tables'
down_revision = 'sprint33_solides_integration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================================
    # 1. SOLIDES_EMPLOYEES
    # ========================================
    op.create_table(
        'solides_employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        # Dados pessoais
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('cpf', sa.String(14), nullable=True),
        sa.Column('rg', sa.String(20), nullable=True),
        sa.Column('data_nascimento', sa.DateTime, nullable=True),
        sa.Column('sexo', sa.String(10), nullable=True),
        sa.Column('estado_civil', sa.String(50), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('celular', sa.String(20), nullable=True),
        # Endereço
        sa.Column('endereco', postgresql.JSONB, nullable=True, server_default='{}'),
        # Dados profissionais
        sa.Column('matricula', sa.String(50), nullable=True),
        sa.Column('cargo_id', sa.String(50), nullable=True),
        sa.Column('cargo_nome', sa.String(255), nullable=True),
        sa.Column('departamento_id', sa.String(50), nullable=True),
        sa.Column('departamento_nome', sa.String(255), nullable=True),
        sa.Column('unidade_id', sa.String(50), nullable=True),
        sa.Column('unidade_nome', sa.String(255), nullable=True),
        sa.Column('gestor_id', sa.String(50), nullable=True),
        sa.Column('gestor_nome', sa.String(255), nullable=True),
        # Contrato
        sa.Column('data_admissao', sa.DateTime, nullable=True),
        sa.Column('data_demissao', sa.DateTime, nullable=True),
        sa.Column('tipo_contrato', sa.String(50), nullable=True),
        sa.Column('regime_trabalho', sa.String(50), nullable=True),
        sa.Column('jornada_trabalho', sa.String(100), nullable=True),
        sa.Column('carga_horaria_semanal', sa.Integer, nullable=True),
        sa.Column('salario', sa.String(50), nullable=True),
        # Dados DP
        sa.Column('ctps_numero', sa.String(50), nullable=True),
        sa.Column('ctps_serie', sa.String(20), nullable=True),
        sa.Column('ctps_uf', sa.String(2), nullable=True),
        sa.Column('pis', sa.String(20), nullable=True),
        sa.Column('titulo_eleitor', sa.String(20), nullable=True),
        sa.Column('certificado_reservista', sa.String(20), nullable=True),
        # Dependentes
        sa.Column('dependentes', postgresql.JSONB, nullable=True, server_default='[]'),
        # Status
        sa.Column('situacao', sa.String(50), nullable=True),
        # Perfil comportamental
        sa.Column('perfil_disc', postgresql.JSONB, nullable=True),
        sa.Column('perfil_profiler', postgresql.JSONB, nullable=True),
        # Foto
        sa.Column('foto_url', sa.String(500), nullable=True),
        # Dados extras
        sa.Column('dados_adicionais', postgresql.JSONB, nullable=True, server_default='{}'),
        # Metadados de sincronização
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('sync_source', sa.String(50), nullable=True, server_default='solides'),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_employee_condominio', 'solides_employees', ['condominio_id'])
    op.create_index('ix_solides_employee_cpf', 'solides_employees', ['cpf'])
    op.create_index('ix_solides_employee_email', 'solides_employees', ['email'])
    op.create_index('ix_solides_employee_matricula', 'solides_employees', ['matricula'])
    op.create_index('ix_solides_employee_situacao', 'solides_employees', ['situacao'])
    op.create_unique_constraint('uq_solides_employee_id', 'solides_employees', ['condominio_id', 'solides_id'])

    # ========================================
    # 2. SOLIDES_DEPARTMENTS
    # ========================================
    op.create_table(
        'solides_departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=True),
        sa.Column('departamento_pai_id', sa.String(50), nullable=True),
        sa.Column('gestor_id', sa.String(50), nullable=True),
        sa.Column('unidade_id', sa.String(50), nullable=True),
        sa.Column('ativo', sa.Boolean, nullable=False, server_default='true'),
        # Metadados
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_department_condominio', 'solides_departments', ['condominio_id'])
    op.create_unique_constraint('uq_solides_department_id', 'solides_departments', ['condominio_id', 'solides_id'])

    # ========================================
    # 3. SOLIDES_POSITIONS
    # ========================================
    op.create_table(
        'solides_positions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=True),
        sa.Column('descricao', sa.Text, nullable=True),
        sa.Column('departamento_id', sa.String(50), nullable=True),
        sa.Column('cbo_id', sa.String(50), nullable=True),
        sa.Column('cbo_codigo', sa.String(20), nullable=True),
        sa.Column('nivel', sa.String(50), nullable=True),
        sa.Column('faixa_salarial_min', sa.String(50), nullable=True),
        sa.Column('faixa_salarial_max', sa.String(50), nullable=True),
        sa.Column('ativo', sa.Boolean, nullable=False, server_default='true'),
        # Metadados
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_position_condominio', 'solides_positions', ['condominio_id'])
    op.create_unique_constraint('uq_solides_position_id', 'solides_positions', ['condominio_id', 'solides_id'])

    # ========================================
    # 4. SOLIDES_OCCURRENCES
    # ========================================
    op.create_table(
        'solides_occurrences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        sa.Column('colaborador_id', sa.String(50), nullable=False),
        sa.Column('colaborador_nome', sa.String(255), nullable=True),
        sa.Column('tipo', sa.String(100), nullable=False),
        sa.Column('descricao', sa.Text, nullable=True),
        sa.Column('data', sa.DateTime, nullable=False),
        sa.Column('data_vigencia', sa.DateTime, nullable=True),
        # Detalhes específicos
        sa.Column('duracao_dias', sa.Integer, nullable=True),
        sa.Column('valor_aumento', sa.String(50), nullable=True),
        sa.Column('percentual_aumento', sa.String(20), nullable=True),
        sa.Column('novo_cargo_id', sa.String(50), nullable=True),
        sa.Column('novo_cargo_nome', sa.String(255), nullable=True),
        # Responsável
        sa.Column('registrado_por_id', sa.String(50), nullable=True),
        sa.Column('registrado_por_nome', sa.String(255), nullable=True),
        # Anexos
        sa.Column('anexos', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('observacoes', sa.Text, nullable=True),
        sa.Column('dados_adicionais', postgresql.JSONB, nullable=True, server_default='{}'),
        # Metadados
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_occurrence_condominio', 'solides_occurrences', ['condominio_id'])
    op.create_index('ix_solides_occurrence_colaborador', 'solides_occurrences', ['colaborador_id'])
    op.create_index('ix_solides_occurrence_tipo', 'solides_occurrences', ['tipo'])
    op.create_index('ix_solides_occurrence_data', 'solides_occurrences', ['data'])
    op.create_unique_constraint('uq_solides_occurrence_id', 'solides_occurrences', ['condominio_id', 'solides_id'])

    # ========================================
    # 5. SOLIDES_ABSENCES
    # ========================================
    op.create_table(
        'solides_absences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        sa.Column('colaborador_id', sa.String(50), nullable=False),
        sa.Column('colaborador_nome', sa.String(255), nullable=True),
        sa.Column('tipo', sa.String(100), nullable=False),
        sa.Column('motivo', sa.Text, nullable=True),
        sa.Column('data_inicio', sa.DateTime, nullable=False),
        sa.Column('data_fim', sa.DateTime, nullable=True),
        sa.Column('horas', sa.String(20), nullable=True),
        sa.Column('minutos_atraso', sa.Integer, nullable=True),
        # Justificativa
        sa.Column('justificado', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('documento_anexo', sa.String(500), nullable=True),
        sa.Column('cid', sa.String(20), nullable=True),
        # Impacto
        sa.Column('desconto_em_folha', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('dias_descontados', sa.Integer, nullable=True),
        # INSS
        sa.Column('numero_beneficio_inss', sa.String(50), nullable=True),
        sa.Column('data_inicio_inss', sa.DateTime, nullable=True),
        sa.Column('data_fim_inss', sa.DateTime, nullable=True),
        # Responsável
        sa.Column('registrado_por_id', sa.String(50), nullable=True),
        sa.Column('registrado_por_nome', sa.String(255), nullable=True),
        sa.Column('observacoes', sa.Text, nullable=True),
        sa.Column('dados_adicionais', postgresql.JSONB, nullable=True, server_default='{}'),
        # Metadados
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_absence_condominio', 'solides_absences', ['condominio_id'])
    op.create_index('ix_solides_absence_colaborador', 'solides_absences', ['colaborador_id'])
    op.create_index('ix_solides_absence_tipo', 'solides_absences', ['tipo'])
    op.create_index('ix_solides_absence_data', 'solides_absences', ['data_inicio'])
    op.create_unique_constraint('uq_solides_absence_id', 'solides_absences', ['condominio_id', 'solides_id'])

    # ========================================
    # 6. SOLIDES_WORKPLACES
    # ========================================
    op.create_table(
        'solides_workplaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=True),
        sa.Column('cnpj', sa.String(20), nullable=True),
        sa.Column('endereco', postgresql.JSONB, nullable=True, server_default='{}'),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('ativo', sa.Boolean, nullable=False, server_default='true'),
        # Metadados
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_workplace_condominio', 'solides_workplaces', ['condominio_id'])
    op.create_unique_constraint('uq_solides_workplace_id', 'solides_workplaces', ['condominio_id', 'solides_id'])

    # ========================================
    # 7. SOLIDES_WORK_SCHEDULES
    # ========================================
    op.create_table(
        'solides_work_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=True),
        sa.Column('tipo', sa.String(50), nullable=True),
        sa.Column('carga_horaria_semanal', sa.Integer, nullable=True),
        sa.Column('horarios', postgresql.JSONB, nullable=True, server_default='{}'),
        sa.Column('ativo', sa.Boolean, nullable=False, server_default='true'),
        # Metadados
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_work_schedule_condominio', 'solides_work_schedules', ['condominio_id'])
    op.create_unique_constraint('uq_solides_work_schedule_id', 'solides_work_schedules', ['condominio_id', 'solides_id'])

    # ========================================
    # 8. SOLIDES_COST_CENTERS
    # ========================================
    op.create_table(
        'solides_cost_centers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solides_id', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=True),
        sa.Column('descricao', sa.Text, nullable=True),
        sa.Column('ativo', sa.Boolean, nullable=False, server_default='true'),
        # Metadados
        sa.Column('data_hash', sa.String(32), nullable=True),
        sa.Column('first_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_synced_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Auditoria
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_solides_cost_center_condominio', 'solides_cost_centers', ['condominio_id'])
    op.create_unique_constraint('uq_solides_cost_center_id', 'solides_cost_centers', ['condominio_id', 'solides_id'])


def downgrade() -> None:
    op.drop_table('solides_cost_centers')
    op.drop_table('solides_work_schedules')
    op.drop_table('solides_workplaces')
    op.drop_table('solides_absences')
    op.drop_table('solides_occurrences')
    op.drop_table('solides_positions')
    op.drop_table('solides_departments')
    op.drop_table('solides_employees')
