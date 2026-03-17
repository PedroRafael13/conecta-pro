"""Create people_management tables (14 tables).

New tables:
- admission_processes (DP - Workflow de admissão)
- termination_processes (DP - Workflow de rescisão)
- employment_contracts (DP - Contratos de trabalho)
- employee_benefits (DP - Benefícios do colaborador)
- training_courses (RH - Catálogo de cursos)
- trainings (RH - Turmas de treinamento)
- training_enrollments (RH - Matrículas)
- training_certificates (RH - Certificados)
- performance_reviews (RH - Avaliações de desempenho)
- career_plans (RH - Planos de carreira)
- portal_access_logs (Portal - Log de acessos)
- portal_notifications (Portal - Notificações)
- portal_preferences (Portal - Preferências)
- portal_digital_signatures (Portal - Assinaturas digitais)

Revision ID: sprint72_people_management
Revises: sprint71_bidding_ai_agents
Create Date: 2026-03-12

"""

from alembic import op

revision = "sprint72_people_management"
down_revision = "sprint71_bidding_ai_agents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===================================================================
    # ENUMS (IF NOT EXISTS via DO block for PostgreSQL compatibility)
    # ===================================================================
    enums = {
        "trainingcategorycourse": "'mandatory_security', 'mandatory_safety', 'technical', 'behavioral', 'leadership', 'compliance', 'onboarding', 'other'",
        "rh_trainingstatus": "'scheduled', 'in_progress', 'completed', 'cancelled'",
        "enrollmentstatus": "'enrolled', 'confirmed', 'attended', 'absent', 'cancelled'",
        "certificatestatus": "'valid', 'expired', 'revoked'",
        "reviewtype": "'monthly', 'quarterly', 'annual', 'probation'",
        "reviewstatus": "'draft', 'self_evaluation', 'manager_review', 'calibration', 'completed'",
        "careerlevel": "'junior', 'pleno', 'senior', 'specialist', 'coordinator', 'manager', 'director'",
        "careerplanstatus": "'active', 'completed', 'cancelled', 'on_hold'",
        "portal_access_action_enum": "'login', 'logout', 'view_payslip', 'view_schedule', 'sign_document', 'update_data', 'view_warning'",
        "portal_notification_type_enum": "'document_pending', 'schedule_update', 'payslip_available', 'warning_issued', 'general', 'system'",
        "portal_document_type_enum": "'warning', 'suspension', 'payslip', 'contract', 'vacation', 'policy', 'training_certificate', 'other'",
    }
    for enum_name, enum_values in enums.items():
        op.execute(f"""
            DO $$ BEGIN
                CREATE TYPE {enum_name} AS ENUM ({enum_values});
            EXCEPTION WHEN duplicate_object THEN NULL;
            END $$;
        """)

    # ===================================================================
    # TABLE 1: admission_processes (DP)
    # ===================================================================
    op.execute("""
        CREATE TABLE admission_processes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            candidate_id UUID,
            employee_id UUID,
            job_position_id UUID,
            status VARCHAR(30) NOT NULL DEFAULT 'documents_pending',
            expected_start_date DATE,
            actual_start_date DATE,
            salary_proposed NUMERIC(12, 2),
            workplace_id UUID,
            checklist JSONB DEFAULT '{}',
            documents_received JSONB DEFAULT '{}',
            medical_exam_date DATE,
            medical_exam_result VARCHAR(50),
            contract_signed_at TIMESTAMPTZ,
            notes TEXT,
            created_by_id UUID,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_admission_candidate ON admission_processes(candidate_id);
        CREATE INDEX idx_admission_employee ON admission_processes(employee_id);
        CREATE INDEX idx_admission_status ON admission_processes(status);

        COMMENT ON COLUMN admission_processes.candidate_id IS 'FK para candidato (recruitment)';
        COMMENT ON COLUMN admission_processes.employee_id IS 'FK para funcionário criado após conclusão';
        COMMENT ON COLUMN admission_processes.job_position_id IS 'FK para vaga/posto';
        COMMENT ON COLUMN admission_processes.workplace_id IS 'FK para local de trabalho';
    """)

    # ===================================================================
    # TABLE 2: termination_processes (DP)
    # ===================================================================
    op.execute("""
        CREATE TABLE termination_processes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            type VARCHAR(30) NOT NULL,
            reason TEXT,
            notice_period_days INTEGER,
            notice_start_date DATE,
            last_working_day DATE,
            status VARCHAR(30) NOT NULL DEFAULT 'initiated',
            severance_amount NUMERIC(12, 2),
            vacation_balance_amount NUMERIC(12, 2),
            thirteenth_salary_amount NUMERIC(12, 2),
            fgts_amount NUMERIC(12, 2),
            total_amount NUMERIC(12, 2),
            exit_interview_done BOOLEAN NOT NULL DEFAULT FALSE,
            exit_interview_notes TEXT,
            esocial_event_sent BOOLEAN NOT NULL DEFAULT FALSE,
            documents_generated JSONB DEFAULT '{}',
            created_by_id UUID,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_termination_employee ON termination_processes(employee_id);
        CREATE INDEX idx_termination_status ON termination_processes(status);

        COMMENT ON COLUMN termination_processes.employee_id IS 'FK para employees';
        COMMENT ON COLUMN termination_processes.type IS 'Tipo de rescisão';
    """)

    # ===================================================================
    # TABLE 3: employment_contracts (DP)
    # ===================================================================
    op.execute("""
        CREATE TABLE employment_contracts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            type VARCHAR(30) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            work_schedule VARCHAR(30),
            weekly_hours NUMERIC(5, 2),
            base_salary NUMERIC(12, 2) NOT NULL,
            hazard_pay_percent NUMERIC(5, 2) DEFAULT 0,
            unhealthy_pay_percent NUMERIC(5, 2) DEFAULT 0,
            night_shift_percent NUMERIC(5, 2) DEFAULT 0,
            job_title VARCHAR(200),
            department VARCHAR(100),
            cost_center VARCHAR(50),
            workplace_id UUID,
            union_name VARCHAR(200),
            union_code VARCHAR(20),
            is_current BOOLEAN NOT NULL DEFAULT TRUE,
            previous_contract_id UUID,
            notes TEXT,
            document_path VARCHAR(500),
            signed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_contract_employee ON employment_contracts(employee_id);
        CREATE INDEX idx_contract_current ON employment_contracts(is_current);

        COMMENT ON COLUMN employment_contracts.work_schedule IS 'Ex: 12x36, 44h/sem, 6x1';
        COMMENT ON COLUMN employment_contracts.hazard_pay_percent IS 'Periculosidade %';
        COMMENT ON COLUMN employment_contracts.unhealthy_pay_percent IS 'Insalubridade %';
        COMMENT ON COLUMN employment_contracts.night_shift_percent IS 'Adicional noturno %';
        COMMENT ON COLUMN employment_contracts.workplace_id IS 'FK para local de trabalho';
        COMMENT ON COLUMN employment_contracts.previous_contract_id IS 'FK para contrato anterior';
    """)

    # ===================================================================
    # TABLE 4: employee_benefits (DP)
    # ===================================================================
    op.execute("""
        CREATE TABLE employee_benefits (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            type VARCHAR(30) NOT NULL,
            provider VARCHAR(200),
            plan_name VARCHAR(200),
            employee_contribution NUMERIC(10, 2) DEFAULT 0,
            company_contribution NUMERIC(10, 2) DEFAULT 0,
            start_date DATE,
            end_date DATE,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            card_number VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_benefit_employee ON employee_benefits(employee_id);
        CREATE INDEX idx_benefit_type ON employee_benefits(type);
        CREATE INDEX idx_benefit_status ON employee_benefits(status);

        COMMENT ON COLUMN employee_benefits.employee_id IS 'FK para employees';
    """)

    # ===================================================================
    # TABLE 5: training_courses (RH - Catálogo)
    # ===================================================================
    op.execute("""
        CREATE TABLE training_courses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category trainingcategorycourse NOT NULL DEFAULT 'other',
            duration_hours FLOAT NOT NULL DEFAULT 1.0,
            max_participants INTEGER,
            is_mandatory BOOLEAN NOT NULL DEFAULT FALSE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            required_for_workplace_types JSONB DEFAULT '[]',
            validity_months INTEGER,
            syllabus JSONB,
            instructor_name VARCHAR(200),
            instructor_qualification TEXT,
            cost_per_participant FLOAT,
            provider VARCHAR(200),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_training_course_category ON training_courses(category);
        CREATE INDEX idx_training_course_active ON training_courses(is_active);
        CREATE INDEX idx_training_course_mandatory ON training_courses(is_mandatory);

        COMMENT ON COLUMN training_courses.duration_hours IS 'Duracao do curso em horas';
        COMMENT ON COLUMN training_courses.max_participants IS 'Maximo de participantes por turma';
        COMMENT ON COLUMN training_courses.required_for_workplace_types IS 'Tipos de posto que exigem este curso';
        COMMENT ON COLUMN training_courses.validity_months IS 'Meses de validade do certificado (null = sem validade)';
        COMMENT ON COLUMN training_courses.syllabus IS 'Ementa do curso em formato estruturado';
        COMMENT ON COLUMN training_courses.cost_per_participant IS 'Custo por participante em BRL';
        COMMENT ON COLUMN training_courses.provider IS 'Fornecedor ou empresa de treinamento';
    """)

    # ===================================================================
    # TABLE 6: trainings (RH - Turmas)
    # ===================================================================
    op.execute("""
        CREATE TABLE trainings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            course_id UUID NOT NULL REFERENCES training_courses(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            start_date TIMESTAMPTZ NOT NULL,
            end_date TIMESTAMPTZ,
            location VARCHAR(300),
            status rh_trainingstatus NOT NULL DEFAULT 'scheduled',
            instructor_name VARCHAR(200),
            max_participants INTEGER,
            current_participants INTEGER NOT NULL DEFAULT 0,
            workplace_id UUID,
            notes TEXT,
            created_by_id UUID,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_training_course_id ON trainings(course_id);
        CREATE INDEX idx_training_status ON trainings(status);
        CREATE INDEX idx_training_start_date ON trainings(start_date);
        CREATE INDEX idx_training_workplace ON trainings(workplace_id);
    """)

    # ===================================================================
    # TABLE 7: training_enrollments (RH - Matrículas)
    # ===================================================================
    op.execute("""
        CREATE TABLE training_enrollments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            training_id UUID NOT NULL REFERENCES trainings(id) ON DELETE CASCADE,
            employee_id UUID NOT NULL,
            status enrollmentstatus NOT NULL DEFAULT 'enrolled',
            enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            confirmed_at TIMESTAMPTZ,
            attended_at TIMESTAMPTZ,
            score FLOAT,
            feedback TEXT,
            certificate_id UUID,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_enrollment_training_employee UNIQUE (training_id, employee_id)
        );

        CREATE INDEX idx_enrollment_training ON training_enrollments(training_id);
        CREATE INDEX idx_enrollment_employee ON training_enrollments(employee_id);
        CREATE INDEX idx_enrollment_status ON training_enrollments(status);

        COMMENT ON COLUMN training_enrollments.score IS 'Nota obtida no treinamento (0-100)';
    """)

    # ===================================================================
    # TABLE 8: training_certificates (RH - Certificados)
    # ===================================================================
    op.execute("""
        CREATE TABLE training_certificates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            enrollment_id UUID NOT NULL REFERENCES training_enrollments(id) ON DELETE CASCADE,
            employee_id UUID NOT NULL,
            course_id UUID NOT NULL REFERENCES training_courses(id) ON DELETE CASCADE,
            certificate_number VARCHAR(50) NOT NULL,
            issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ,
            status certificatestatus NOT NULL DEFAULT 'valid',
            revoked_at TIMESTAMPTZ,
            revocation_reason TEXT,
            document_path VARCHAR(500),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_certificate_number UNIQUE (certificate_number)
        );

        CREATE INDEX idx_tc_employee ON training_certificates(employee_id);
        CREATE INDEX idx_tc_course ON training_certificates(course_id);
        CREATE INDEX idx_tc_status ON training_certificates(status);
        CREATE INDEX idx_tc_expires ON training_certificates(expires_at);
    """)

    # ===================================================================
    # TABLE 9: performance_reviews (RH - Avaliações)
    # ===================================================================
    op.execute("""
        CREATE TABLE performance_reviews (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            reviewer_id UUID NOT NULL,
            review_period_start DATE NOT NULL,
            review_period_end DATE NOT NULL,
            type reviewtype NOT NULL DEFAULT 'quarterly',
            status reviewstatus NOT NULL DEFAULT 'draft',
            overall_score FLOAT,
            scores_breakdown JSONB DEFAULT '{}',
            strengths TEXT,
            improvements TEXT,
            goals_next_period JSONB DEFAULT '[]',
            employee_comments TEXT,
            reviewer_comments TEXT,
            calibrated_score FLOAT,
            completed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_perf_review_employee ON performance_reviews(employee_id);
        CREATE INDEX idx_perf_review_reviewer ON performance_reviews(reviewer_id);
        CREATE INDEX idx_perf_review_status ON performance_reviews(status);
        CREATE INDEX idx_perf_review_type ON performance_reviews(type);
        CREATE INDEX idx_perf_review_period ON performance_reviews(review_period_start, review_period_end);

        COMMENT ON COLUMN performance_reviews.overall_score IS 'Score geral de 0 a 100';
        COMMENT ON COLUMN performance_reviews.scores_breakdown IS 'Scores por dimensao: punctuality, quality, initiative, teamwork, leadership';
        COMMENT ON COLUMN performance_reviews.strengths IS 'Pontos fortes identificados';
        COMMENT ON COLUMN performance_reviews.improvements IS 'Areas de melhoria';
        COMMENT ON COLUMN performance_reviews.goals_next_period IS 'Metas para o proximo periodo';
        COMMENT ON COLUMN performance_reviews.calibrated_score IS 'Score apos calibracao gerencial';
    """)

    # ===================================================================
    # TABLE 10: career_plans (RH - Planos de Carreira)
    # ===================================================================
    op.execute("""
        CREATE TABLE career_plans (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            current_position VARCHAR(200) NOT NULL,
            target_position VARCHAR(200) NOT NULL,
            current_level careerlevel NOT NULL,
            target_level careerlevel NOT NULL,
            estimated_timeline_months INTEGER NOT NULL DEFAULT 12,
            status careerplanstatus NOT NULL DEFAULT 'active',
            milestones JSONB DEFAULT '[]',
            mentor_id UUID,
            started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_career_plan_employee ON career_plans(employee_id);
        CREATE INDEX idx_career_plan_status ON career_plans(status);
        CREATE INDEX idx_career_plan_mentor ON career_plans(mentor_id);
        CREATE INDEX idx_career_plan_levels ON career_plans(current_level, target_level);

        COMMENT ON COLUMN career_plans.estimated_timeline_months IS 'Tempo estimado em meses para atingir o objetivo';
        COMMENT ON COLUMN career_plans.milestones IS 'Lista de marcos: [{title, description, target_date, completed, completed_at}]';
    """)

    # ===================================================================
    # TABLE 11: portal_access_logs (Portal)
    # ===================================================================
    op.execute("""
        CREATE TABLE portal_access_logs (
            id SERIAL PRIMARY KEY,
            employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            action portal_access_action_enum NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            device_fingerprint VARCHAR(255),
            geolocation JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_portal_access_employee ON portal_access_logs(employee_id);
        CREATE INDEX idx_portal_access_action ON portal_access_logs(action);
        CREATE INDEX idx_portal_access_date ON portal_access_logs(created_at);
    """)

    # ===================================================================
    # TABLE 12: portal_notifications (Portal)
    # ===================================================================
    op.execute("""
        CREATE TABLE portal_notifications (
            id SERIAL PRIMARY KEY,
            employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            notification_type portal_notification_type_enum NOT NULL DEFAULT 'general',
            title VARCHAR(255) NOT NULL,
            message TEXT,
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            read_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_portal_notif_employee ON portal_notifications(employee_id);
        CREATE INDEX idx_portal_notif_read ON portal_notifications(is_read);
        CREATE INDEX idx_portal_notif_date ON portal_notifications(created_at);
    """)

    # ===================================================================
    # TABLE 13: portal_preferences (Portal)
    # ===================================================================
    op.execute("""
        CREATE TABLE portal_preferences (
            id SERIAL PRIMARY KEY,
            employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            language VARCHAR(10) NOT NULL DEFAULT 'pt-BR',
            theme VARCHAR(20) NOT NULL DEFAULT 'light',
            notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
            push_notifications BOOLEAN NOT NULL DEFAULT FALSE,
            extra_settings JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_portal_pref_employee UNIQUE (employee_id)
        );

        CREATE INDEX idx_portal_pref_employee ON portal_preferences(employee_id);
    """)

    # ===================================================================
    # TABLE 14: portal_digital_signatures (Portal)
    # ===================================================================
    op.execute("""
        CREATE TABLE portal_digital_signatures (
            id SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL,
            document_type portal_document_type_enum NOT NULL,
            employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            signature_hash VARCHAR(256) NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            device_fingerprint VARCHAR(255),
            geolocation JSONB,
            signed_at TIMESTAMP NOT NULL DEFAULT NOW(),
            is_valid BOOLEAN NOT NULL DEFAULT TRUE,
            invalidated_at TIMESTAMP,
            invalidation_reason TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_signature_hash UNIQUE (signature_hash)
        );

        CREATE INDEX idx_digsig_document ON portal_digital_signatures(document_id);
        CREATE INDEX idx_digsig_employee ON portal_digital_signatures(employee_id);
        CREATE INDEX idx_digsig_valid ON portal_digital_signatures(is_valid);
    """)

    # ===================================================================
    # TRIGGER: auto-update updated_at on tables that have it
    # ===================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    tables_with_updated_at = [
        "admission_processes",
        "termination_processes",
        "employment_contracts",
        "employee_benefits",
        "training_courses",
        "trainings",
        "training_enrollments",
        "performance_reviews",
        "career_plans",
        "portal_preferences",
    ]
    for table in tables_with_updated_at:
        op.execute(f"""
            CREATE TRIGGER trigger_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop tables in reverse order (respecting FK dependencies)
    tables = [
        "portal_digital_signatures",
        "portal_preferences",
        "portal_notifications",
        "portal_access_logs",
        "career_plans",
        "performance_reviews",
        "training_certificates",
        "training_enrollments",
        "trainings",
        "training_courses",
        "employee_benefits",
        "employment_contracts",
        "termination_processes",
        "admission_processes",
    ]
    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        op.execute(f"DROP TRIGGER IF EXISTS trigger_{table}_updated_at ON {table};")

    # Drop enums
    enums = [
        "portal_document_type_enum",
        "portal_notification_type_enum",
        "portal_access_action_enum",
        "careerplanstatus",
        "careerlevel",
        "reviewstatus",
        "reviewtype",
        "certificatestatus",
        "enrollmentstatus",
        "rh_trainingstatus",
        "trainingcategorycourse",
    ]
    for enum in enums:
        op.execute(f"DROP TYPE IF EXISTS {enum};")

    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
