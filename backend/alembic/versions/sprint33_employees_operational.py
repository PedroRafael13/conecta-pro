"""Tabela employees operacional e tipos de posto

Revision ID: sprint33_employees_operational
Revises: sprint33_solides_data_tables
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

revision = 'sprint33_employees_operational'
down_revision = 'sprint33_solides_data_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # TABELA EMPLOYEES - Funcionários Operacionais
    # ==========================================================================
    op.create_table(
        'employees',
        # Identificação
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('solides_id', sa.String(50), nullable=True),  # Link com Sólides
        sa.Column('matricula', sa.String(50), nullable=True),
        sa.Column('codigo', sa.String(20), nullable=True),  # Código interno
        
        # Dados Pessoais
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('nome_social', sa.String(255), nullable=True),
        sa.Column('cpf', sa.String(14), nullable=True),
        sa.Column('rg', sa.String(20), nullable=True),
        sa.Column('rg_orgao', sa.String(20), nullable=True),
        sa.Column('rg_uf', sa.String(2), nullable=True),
        sa.Column('data_nascimento', sa.Date, nullable=True),
        sa.Column('sexo', sa.String(1), nullable=True),  # M/F
        sa.Column('estado_civil', sa.String(20), nullable=True),
        sa.Column('nacionalidade', sa.String(50), default='Brasileira'),
        sa.Column('naturalidade', sa.String(100), nullable=True),
        sa.Column('nome_mae', sa.String(255), nullable=True),
        sa.Column('nome_pai', sa.String(255), nullable=True),
        
        # Contato
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('celular', sa.String(20), nullable=True),
        sa.Column('contato_emergencia', sa.String(255), nullable=True),
        sa.Column('telefone_emergencia', sa.String(20), nullable=True),
        
        # Endereço
        sa.Column('cep', sa.String(10), nullable=True),
        sa.Column('logradouro', sa.String(255), nullable=True),
        sa.Column('numero', sa.String(20), nullable=True),
        sa.Column('complemento', sa.String(100), nullable=True),
        sa.Column('bairro', sa.String(100), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=True),
        sa.Column('uf', sa.String(2), nullable=True),
        
        # Dados Profissionais
        sa.Column('cargo', sa.String(100), nullable=True),
        sa.Column('cargo_id', UUID(as_uuid=True), nullable=True),
        sa.Column('departamento', sa.String(100), nullable=True),
        sa.Column('departamento_id', UUID(as_uuid=True), nullable=True),
        sa.Column('setor', sa.String(100), nullable=True),
        sa.Column('centro_custo', sa.String(100), nullable=True),
        sa.Column('gestor_id', UUID(as_uuid=True), nullable=True),
        sa.Column('gestor_nome', sa.String(255), nullable=True),
        
        # Vínculo Empregatício
        sa.Column('data_admissao', sa.Date, nullable=True),
        sa.Column('data_demissao', sa.Date, nullable=True),
        sa.Column('tipo_contrato', sa.String(50), default='CLT'),  # CLT, PJ, Temporário, Estagiário
        sa.Column('regime_trabalho', sa.String(50), nullable=True),
        sa.Column('jornada_trabalho', sa.String(100), nullable=True),
        sa.Column('carga_horaria_semanal', sa.Integer, default=44),
        sa.Column('escala_padrao', sa.String(20), nullable=True),  # 12x36, 6x1, 5x2
        
        # Remuneração
        sa.Column('salario_base', sa.Numeric(10, 2), nullable=True),
        sa.Column('tipo_pagamento', sa.String(20), default='mensal'),  # mensal, quinzenal, semanal
        sa.Column('banco', sa.String(100), nullable=True),
        sa.Column('agencia', sa.String(20), nullable=True),
        sa.Column('conta', sa.String(30), nullable=True),
        sa.Column('tipo_conta', sa.String(20), nullable=True),  # corrente, poupanca, salario
        sa.Column('pix', sa.String(100), nullable=True),
        
        # Documentos Trabalhistas
        sa.Column('ctps_numero', sa.String(20), nullable=True),
        sa.Column('ctps_serie', sa.String(10), nullable=True),
        sa.Column('ctps_uf', sa.String(2), nullable=True),
        sa.Column('ctps_data_emissao', sa.Date, nullable=True),
        sa.Column('pis', sa.String(20), nullable=True),
        sa.Column('titulo_eleitor', sa.String(20), nullable=True),
        sa.Column('zona_eleitoral', sa.String(10), nullable=True),
        sa.Column('secao_eleitoral', sa.String(10), nullable=True),
        sa.Column('certificado_reservista', sa.String(20), nullable=True),
        sa.Column('cnh_numero', sa.String(20), nullable=True),
        sa.Column('cnh_categoria', sa.String(5), nullable=True),
        sa.Column('cnh_validade', sa.Date, nullable=True),
        
        # Qualificações (Vigilância)
        sa.Column('curso_vigilante', sa.Boolean, default=False),
        sa.Column('curso_vigilante_validade', sa.Date, nullable=True),
        sa.Column('cnv', sa.String(30), nullable=True),  # Carteira Nacional de Vigilante
        sa.Column('cnv_validade', sa.Date, nullable=True),
        sa.Column('porte_arma', sa.Boolean, default=False),
        sa.Column('porte_arma_numero', sa.String(30), nullable=True),
        sa.Column('porte_arma_validade', sa.Date, nullable=True),
        sa.Column('certificacoes', JSONB, default=[]),  # Lista de certificações
        
        # Alocação Operacional
        sa.Column('posto_atual_id', UUID(as_uuid=True), nullable=True),
        sa.Column('posto_atual_nome', sa.String(255), nullable=True),
        sa.Column('cliente_id', UUID(as_uuid=True), nullable=True),
        sa.Column('cliente_nome', sa.String(255), nullable=True),
        sa.Column('data_inicio_posto', sa.Date, nullable=True),
        sa.Column('turno_padrao', sa.String(20), nullable=True),  # diurno, noturno, misto
        
        # Status
        sa.Column('status', sa.String(20), default='ativo'),  # ativo, inativo, ferias, afastado, demitido
        sa.Column('motivo_inatividade', sa.String(255), nullable=True),
        sa.Column('data_retorno_previsto', sa.Date, nullable=True),
        
        # Perfil Comportamental (Sólides)
        sa.Column('perfil_disc', JSONB, nullable=True),
        sa.Column('perfil_predominante', sa.String(50), nullable=True),
        sa.Column('competencias', JSONB, default=[]),
        
        # Biometria e Identificação
        sa.Column('foto_url', sa.String(500), nullable=True),
        sa.Column('biometria_facial', sa.Boolean, default=False),
        sa.Column('biometria_digital', sa.Boolean, default=False),
        sa.Column('cracha_numero', sa.String(20), nullable=True),
        
        # Dependentes
        sa.Column('dependentes', JSONB, default=[]),
        
        # Observações
        sa.Column('observacoes', sa.Text, nullable=True),
        sa.Column('dados_adicionais', JSONB, default={}),
        
        # Sync
        sa.Column('sync_source', sa.String(20), default='conecta'),  # conecta, solides
        sa.Column('last_synced_at', sa.DateTime, nullable=True),
        
        # Auditoria
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Índices
    op.create_index('ix_employees_cpf', 'employees', ['cpf'])
    op.create_index('ix_employees_matricula', 'employees', ['matricula'])
    op.create_index('ix_employees_solides_id', 'employees', ['solides_id'])
    op.create_index('ix_employees_status', 'employees', ['status'])
    op.create_index('ix_employees_posto_atual', 'employees', ['posto_atual_id'])
    op.create_index('ix_employees_cliente', 'employees', ['cliente_id'])
    op.create_index('ix_employees_cargo', 'employees', ['cargo'])
    op.create_index('ix_employees_nome', 'employees', ['nome'])
    
    # ==========================================================================
    # TABELA POST_TYPES - Tipos de Posto
    # ==========================================================================
    op.create_table(
        'post_types',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('codigo', sa.String(20), nullable=False, unique=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('descricao', sa.Text, nullable=True),
        sa.Column('categoria', sa.String(50), nullable=True),  # vigilancia, portaria, servicos_gerais, administrativo
        sa.Column('requer_curso_vigilante', sa.Boolean, default=False),
        sa.Column('requer_porte_arma', sa.Boolean, default=False),
        sa.Column('requer_cnh', sa.Boolean, default=False),
        sa.Column('cnh_categoria_minima', sa.String(5), nullable=True),
        sa.Column('certificacoes_requeridas', JSONB, default=[]),
        sa.Column('salario_base_sugerido', sa.Numeric(10, 2), nullable=True),
        sa.Column('adicional_noturno_percent', sa.Numeric(5, 2), default=20),
        sa.Column('adicional_periculosidade_percent', sa.Numeric(5, 2), default=30),
        sa.Column('carga_horaria_padrao', sa.Integer, default=44),
        sa.Column('escala_padrao', sa.String(20), default='12x36'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    # ==========================================================================
    # TABELA SCALE_TEMPLATES - Templates de Escala
    # ==========================================================================
    op.create_table(
        'scale_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('codigo', sa.String(20), nullable=False, unique=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('descricao', sa.Text, nullable=True),
        sa.Column('tipo', sa.String(20), nullable=False),  # 12x36, 6x1, 5x2, 4x2, personalizada
        sa.Column('horas_trabalho', sa.Integer, nullable=False),  # Horas por turno
        sa.Column('horas_descanso', sa.Integer, nullable=True),  # Horas de folga (para 12x36, 24x72)
        sa.Column('dias_trabalho', sa.Integer, nullable=True),  # Para escalas tipo 6x1
        sa.Column('dias_folga', sa.Integer, nullable=True),
        sa.Column('horario_inicio_diurno', sa.Time, nullable=True),
        sa.Column('horario_fim_diurno', sa.Time, nullable=True),
        sa.Column('horario_inicio_noturno', sa.Time, nullable=True),
        sa.Column('horario_fim_noturno', sa.Time, nullable=True),
        sa.Column('intervalo_minutos', sa.Integer, default=60),
        sa.Column('considera_dsr', sa.Boolean, default=True),  # Descanso Semanal Remunerado
        sa.Column('adicional_noturno', sa.Boolean, default=True),
        sa.Column('config', JSONB, default={}),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    # ==========================================================================
    # INSERIR TIPOS DE POSTO PADRÃO
    # ==========================================================================
    op.execute("""
        INSERT INTO post_types (id, codigo, nome, descricao, categoria, requer_curso_vigilante, requer_porte_arma, escala_padrao) VALUES
        (gen_random_uuid(), 'PORTARIA', 'Porteiro', 'Controle de acesso e atendimento na portaria', 'portaria', false, false, '12x36'),
        (gen_random_uuid(), 'VIGILANTE', 'Vigilante', 'Vigilância patrimonial desarmada', 'vigilancia', true, false, '12x36'),
        (gen_random_uuid(), 'VIGILANTE_ARM', 'Vigilante Armado', 'Vigilância patrimonial armada', 'vigilancia', true, true, '12x36'),
        (gen_random_uuid(), 'RONDA', 'Rondante', 'Ronda motorizada ou a pé', 'vigilancia', true, false, '12x36'),
        (gen_random_uuid(), 'SUPERVISOR', 'Supervisor', 'Supervisão de equipes e postos', 'vigilancia', true, false, '6x1'),
        (gen_random_uuid(), 'GERENTE', 'Gerente', 'Gestão operacional e administrativa', 'administrativo', false, false, '5x2'),
        (gen_random_uuid(), 'AUX_SERVICOS', 'Auxiliar de Serviços Gerais', 'Limpeza e conservação', 'servicos_gerais', false, false, '6x1'),
        (gen_random_uuid(), 'JARDINEIRO', 'Jardineiro', 'Manutenção de áreas verdes', 'servicos_gerais', false, false, '6x1'),
        (gen_random_uuid(), 'PISCINEIRO', 'Piscineiro', 'Manutenção de piscinas', 'servicos_gerais', false, false, '6x1'),
        (gen_random_uuid(), 'ARTIFICE', 'Artífice', 'Manutenção predial geral', 'servicos_gerais', false, false, '6x1'),
        (gen_random_uuid(), 'AUX_ADMIN', 'Auxiliar Administrativo', 'Apoio administrativo', 'administrativo', false, false, '5x2'),
        (gen_random_uuid(), 'CONTROLADOR', 'Controlador de Acesso', 'Controle de acesso veicular e pedestres', 'portaria', false, false, '12x36'),
        (gen_random_uuid(), 'RECEPCIONISTA', 'Recepcionista', 'Recepção e atendimento', 'administrativo', false, false, '6x1'),
        (gen_random_uuid(), 'ZELADOR', 'Zelador', 'Zeladoria e pequenos reparos', 'servicos_gerais', false, false, '6x1');
    """)
    
    # ==========================================================================
    # INSERIR TEMPLATES DE ESCALA PADRÃO
    # ==========================================================================
    op.execute("""
        INSERT INTO scale_templates (id, codigo, nome, descricao, tipo, horas_trabalho, horas_descanso, dias_trabalho, dias_folga, horario_inicio_diurno, horario_fim_diurno, horario_inicio_noturno, horario_fim_noturno, intervalo_minutos) VALUES
        (gen_random_uuid(), '12X36_DIA', 'Escala 12x36 Diurno', 'Trabalha 12h, folga 36h - Turno diurno', '12x36', 12, 36, NULL, NULL, '07:00', '19:00', NULL, NULL, 60),
        (gen_random_uuid(), '12X36_NOITE', 'Escala 12x36 Noturno', 'Trabalha 12h, folga 36h - Turno noturno', '12x36', 12, 36, NULL, NULL, NULL, NULL, '19:00', '07:00', 60),
        (gen_random_uuid(), '6X1_DIA', 'Escala 6x1 Diurno', 'Trabalha 6 dias, folga 1 - Diurno', '6x1', 8, NULL, 6, 1, '08:00', '17:00', NULL, NULL, 60),
        (gen_random_uuid(), '6X1_TARDE', 'Escala 6x1 Tarde', 'Trabalha 6 dias, folga 1 - Tarde', '6x1', 8, NULL, 6, 1, '14:00', '22:00', NULL, NULL, 60),
        (gen_random_uuid(), '5X2_COMERCIAL', 'Escala 5x2 Comercial', 'Segunda a sexta, horário comercial', '5x2', 8, NULL, 5, 2, '08:00', '18:00', NULL, NULL, 60),
        (gen_random_uuid(), '4X2_12H', 'Escala 4x2', 'Trabalha 4 dias de 12h, folga 2', '4x2', 12, NULL, 4, 2, '07:00', '19:00', NULL, NULL, 60),
        (gen_random_uuid(), '24X72', 'Escala 24x72', 'Trabalha 24h, folga 72h', '24x72', 24, 72, NULL, NULL, '07:00', '07:00', NULL, NULL, 120);
    """)
    
    # ==========================================================================
    # ADICIONAR FK em shifts para employees
    # ==========================================================================
    op.create_foreign_key(
        'fk_shifts_employee',
        'shifts', 'employees',
        ['employee_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_shifts_employee', 'shifts', type_='foreignkey')
    op.drop_table('scale_templates')
    op.drop_table('post_types')
    op.drop_index('ix_employees_nome', 'employees')
    op.drop_index('ix_employees_cargo', 'employees')
    op.drop_index('ix_employees_cliente', 'employees')
    op.drop_index('ix_employees_posto_atual', 'employees')
    op.drop_index('ix_employees_status', 'employees')
    op.drop_index('ix_employees_solides_id', 'employees')
    op.drop_index('ix_employees_matricula', 'employees')
    op.drop_index('ix_employees_cpf', 'employees')
    op.drop_table('employees')
