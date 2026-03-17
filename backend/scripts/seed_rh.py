"""Seed data para módulo RH — 13 tabelas."""

import asyncio
import json
import os
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Employee IDs by role (from real DB)
PORTARIA = [
    "2430761d-172e-44b8-a817-edfea166e321",
    "430bc8bc-da1a-4667-b6fc-578774e5d2cf",
    "2e814e1c-d022-4bb4-8e39-62fab36cd4ac",
    "0d7887cc-d824-44ff-86be-201c7ab70dc6",
    "13a02a88-abdc-48e0-b128-d1005ba57a04",
    "58e002c7-7df8-42a8-aef9-0607d41a306c",
    "82a1d1d6-401d-487a-928f-42ed29756bca",
    "e32ea647-7470-43b0-a560-abd3eb6ff412",
    "f5fe3ccb-8529-4525-9241-5f031d3b9204",
    "4f4d6166-1327-40e7-89e8-29e0736fbcfe",
    "ebfc72fe-7081-47b8-bce6-88b81cdcb09a",
    "706edbc3-e0b9-438a-98e7-c2bf7c40db42",
    "7ccefd89-b89d-463a-a0ba-ffa6475159fb",
    "e38fc9dc-dd7c-44f7-af7b-952ec4c7ccb2",
    "0adfb14d-4b12-4ac0-9d5a-0570ed4531f5",
    "b2f5ac0e-fb97-43ce-b7fe-78466284ea1b",
    "eb84be29-7760-4d64-9688-dd5433172283",
    "b2b39603-19a1-4050-b062-98e500198012",
    "89f89f2c-b0dd-430a-ae84-e4d35981a498",
    "500922e3-4866-454a-8f06-d5685e8e25c1",
    "41587c09-1b42-469f-9c65-4419c870d07c",
    "109edac0-17a1-4cd4-8bf8-8b7062d905d0",
    "7e5e4c49-a1d2-4bbf-8699-9e2fa22063aa",
    "2938d6a4-ca53-4406-ad1d-1309fa555fe6",
    "795abf6c-0a41-4b26-9094-87142591e01d",
    "62897018-8de6-4c8d-85da-dfb0acb8a105",
    "4714fbc7-608b-443d-9669-7b1d54897b92",
    "4fb9bcb3-8ca9-42b7-903e-6c2e0ee7d12e",
    "e0f63eca-6ace-4169-880e-9c021872329a",
    "13a74a88-beef-4b40-af78-66e15a8f9dff",
    "2b4f0614-f3c4-4acd-bdce-cf16d27c3fc2",
    "c58e8b76-916e-4959-b1dc-7327e110a516",
    "a7d7cb41-0223-466c-8c2b-5353c9fa1511",
    "7d6280ad-2471-43e1-9d0c-5a8f576e79b1",
]
SERVICOS = [
    "0754e0aa-0be4-4253-9816-003c0149c1cd",
    "4392a2d4-ea9b-4692-a1f9-289460aab766",
    "9e9e1678-9988-490c-b59b-b2786bb67e1c",
    "0d7f8148-337c-4c66-9000-c9589a23c88a",
    "9e32646c-8bb3-431e-bde8-03f4dc05f9f6",
    "783a8170-e951-4406-856e-6b0cc659d8c3",
    "5e9fa756-5e32-4772-861b-4bb8bff00ffe",
    "29c7e69f-8fb5-4fc7-a124-cfd06c799fe0",
    "176f110f-237c-44c6-bad3-e5ba7e495b3a",
    "a85f315b-4029-4eb1-9584-7a22ed3a7c78",
    "a7d18664-0f10-41b6-adf9-8e824794bc4a",
    "5bfbd45c-0a80-4be4-9776-e8651471f5dc",
]
ARTIFICES = [
    "ab54e4fc-627f-44cd-ae92-c43b459a90ec",
    "7f10bafe-6a44-4c7b-ab37-f344a08caa2f",
    "12423164-f7d8-4db3-bf36-cffebda5948e",
]
LIDERES = [
    "29dae28f-e688-4df0-8879-2704d8351d87",
    "6bf7804a-4976-44d2-aa3e-5bf1f25c3530",
    "4f6d1b27-d05b-4315-aa86-f245d70e52bb",
]
ADMIN_USER = "81d35a73-90a3-4198-afa0-a2e1a2b01d07"


def uid() -> str:
    return str(uuid.uuid4())


async def main() -> None:
    raw_url = os.environ.get("DATABASE_URL", "")
    url = raw_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        # ===== 1. TRAINING_COURSES (8) =====
        courses: list[str] = []
        course_data = [
            ("Tecnicas de Portaria e Controle de Acesso", "mandatory_security", 16.0, True, 12),
            ("Ronda e Seguranca Patrimonial", "mandatory_security", 8.0, True, 12),
            ("NR-1 Gerenciamento de Riscos Ocupacionais", "mandatory_safety", 4.0, True, 24),
            ("Atendimento ao Cliente e Conduta Profissional", "behavioral", 8.0, False, None),
            ("Primeiros Socorros e Emergencias", "mandatory_safety", 12.0, True, 12),
            ("Limpeza e Conservacao de Ambientes", "technical", 6.0, False, None),
            ("Uso de EPI e Seguranca no Trabalho", "mandatory_safety", 4.0, True, 12),
            ("CCT 2026 Direitos e Deveres do Trabalhador", "compliance", 4.0, False, None),
        ]
        for name, cat, hours, mandatory, validity in course_data:
            cid = uid()
            courses.append(cid)
            await conn.execute(
                text("""INSERT INTO training_courses
                    (id, name, category, duration_hours, is_mandatory, validity_months)
                    VALUES (:id, :name, :cat, :hours, :mandatory, :validity)"""),
                {"id": cid, "name": name, "cat": cat, "hours": hours, "mandatory": mandatory, "validity": validity},
            )
        print(f"training_courses: {len(courses)} inseridos")

        # ===== 2. TRAININGS (5) =====
        trainings: list[str] = []
        training_data = [
            (
                courses[0],
                "Portaria e Controle de Acesso - Turma Mar/2026",
                datetime(2026, 3, 3, 8, 0, tzinfo=UTC),
                datetime(2026, 3, 4, 17, 0, tzinfo=UTC),
                "completed",
                "Sala de treinamento Conecta Mais",
                "Carlos Eduardo Lima",
            ),
            (
                courses[4],
                "Primeiros Socorros - Turma Mar/2026",
                datetime(2026, 3, 10, 8, 0, tzinfo=UTC),
                datetime(2026, 3, 11, 17, 0, tzinfo=UTC),
                "completed",
                "Auditorio SEST SENAT Manaus",
                "Dra. Patricia Souza",
            ),
            (
                courses[1],
                "Ronda Patrimonial - Turma Abr/2026",
                datetime(2026, 4, 7, 8, 0, tzinfo=UTC),
                datetime(2026, 4, 7, 17, 0, tzinfo=UTC),
                "scheduled",
                "Sala de treinamento Conecta Mais",
                "Sgt. Ricardo Fonseca",
            ),
            (
                courses[2],
                "NR-1 Riscos Ocupacionais - Turma Abr/2026",
                datetime(2026, 4, 14, 8, 0, tzinfo=UTC),
                datetime(2026, 4, 14, 17, 0, tzinfo=UTC),
                "scheduled",
                "Online via Google Meet",
                "Eng. Marcos Viana",
            ),
            (
                courses[6],
                "Uso de EPI - Turma Abr/2026",
                datetime(2026, 4, 21, 8, 0, tzinfo=UTC),
                datetime(2026, 4, 21, 17, 0, tzinfo=UTC),
                "scheduled",
                "Sala de treinamento Conecta Mais",
                "Tec. Amanda Reis",
            ),
        ]
        for cid, title, start, end, status, loc, instr in training_data:
            tid = uid()
            trainings.append(tid)
            await conn.execute(
                text("""INSERT INTO trainings
                    (id, course_id, title, start_date, end_date, status, location, instructor_name, max_participants, created_by_id)
                    VALUES (:id, :cid, :title, :start, :end, :status, :loc, :instr, 20, :admin)"""),
                {
                    "id": tid,
                    "cid": cid,
                    "title": title,
                    "start": start,
                    "end": end,
                    "status": status,
                    "loc": loc,
                    "instr": instr,
                    "admin": ADMIN_USER,
                },
            )
        print(f"trainings: {len(trainings)} inseridos")

        # ===== 3. TRAINING_ENROLLMENTS (20) =====
        enrollments: list[tuple[str, str, str]] = []
        # Turma 1 completed: 10 porteiros
        for i, emp_id in enumerate(PORTARIA[:10]):
            eid = uid()
            enrollments.append((eid, emp_id, courses[0]))
            await conn.execute(
                text("""INSERT INTO training_enrollments
                    (id, training_id, employee_id, status, confirmed_at, attended_at, score)
                    VALUES (:id, :tid, :eid, 'attended', :conf, :att, :score)"""),
                {
                    "id": eid,
                    "tid": trainings[0],
                    "eid": emp_id,
                    "conf": datetime(2026, 3, 2, 12, 0, tzinfo=UTC),
                    "att": datetime(2026, 3, 4, 17, 0, tzinfo=UTC),
                    "score": 7.0 + (i % 4),
                },
            )
        # Turma 2 completed: 7 porteiros + 3 servicos
        for i, emp_id in enumerate(PORTARIA[10:17] + SERVICOS[:3]):
            eid = uid()
            enrollments.append((eid, emp_id, courses[4]))
            await conn.execute(
                text("""INSERT INTO training_enrollments
                    (id, training_id, employee_id, status, confirmed_at, attended_at, score)
                    VALUES (:id, :tid, :eid, 'attended', :conf, :att, :score)"""),
                {
                    "id": eid,
                    "tid": trainings[1],
                    "eid": emp_id,
                    "conf": datetime(2026, 3, 9, 12, 0, tzinfo=UTC),
                    "att": datetime(2026, 3, 11, 17, 0, tzinfo=UTC),
                    "score": 7.5 + (i % 3),
                },
            )
        print(f"training_enrollments: {len(enrollments)} inseridos")

        # ===== 4. TRAINING_CERTIFICATES (20) =====
        for i, (enroll_id, emp_id, course_id) in enumerate(enrollments):
            cert_num = f"CERT-2026-{i + 1:04d}"
            exp = datetime(2027, 3, 4, 0, 0, tzinfo=UTC) if i < 10 else datetime(2027, 3, 11, 0, 0, tzinfo=UTC)
            await conn.execute(
                text("""INSERT INTO training_certificates
                    (id, enrollment_id, employee_id, course_id, certificate_number, expires_at, status)
                    VALUES (:id, :eid, :empid, :cid, :num, :exp, 'valid')"""),
                {"id": uid(), "eid": enroll_id, "empid": emp_id, "cid": course_id, "num": cert_num, "exp": exp},
            )
        print(f"training_certificates: {len(enrollments)} inseridos")

        # ===== 5. PERFORMANCE_REVIEWS (15) =====
        review_count = 0
        for i, emp_id in enumerate(PORTARIA[:15]):
            reviewer = LIDERES[i % len(LIDERES)]
            scores = {
                "punctuality": round(6.5 + (i % 4) * 0.8, 1),
                "quality": round(7.0 + (i % 3) * 0.7, 1),
                "initiative": round(5.5 + (i % 5) * 0.9, 1),
                "teamwork": round(7.5 + (i % 3) * 0.5, 1),
                "leadership": round(5.0 + (i % 4) * 1.0, 1),
            }
            overall = round(sum(scores.values()) / len(scores), 1)
            strengths_list = [
                "Pontualidade exemplar",
                "Boa relacao com colegas",
                "Proativo nas rondas",
                "Conhecimento tecnico solido",
                "Comprometido com horarios",
            ]
            improvements_list = [
                "Comunicacao escrita",
                "Uso de tecnologia",
                "Lideranca de equipe",
                "Gestao de conflitos",
                "Documentacao de ocorrencias",
            ]
            await conn.execute(
                text("""INSERT INTO performance_reviews
                    (id, employee_id, reviewer_id, review_period_start, review_period_end,
                     type, status, overall_score, scores_breakdown, strengths, improvements, completed_at)
                    VALUES (:id, :eid, :rid, :pstart, :pend, 'annual', 'completed',
                            :overall, :scores, :strengths, :improvements, :completed)"""),
                {
                    "id": uid(),
                    "eid": emp_id,
                    "rid": reviewer,
                    "pstart": date(2025, 7, 1),
                    "pend": date(2025, 12, 31),
                    "overall": overall,
                    "scores": json.dumps(scores),
                    "strengths": strengths_list[i % 5],
                    "improvements": improvements_list[i % 5],
                    "completed": datetime(2026, 1, 15, 10, 0, tzinfo=UTC),
                },
            )
            review_count += 1
        print(f"performance_reviews: {review_count} inseridos")

        # ===== 6. CAREER_PLANS (11) =====
        career_count = 0
        for i, emp_id in enumerate(PORTARIA[:8]):
            mentor = LIDERES[i % len(LIDERES)]
            milestones = [
                {"title": "Completar curso de Lideranca", "status": "pending", "due": "2026-06-30"},
                {"title": "Avaliacoes consecutivas acima de 8.0", "status": "pending", "due": "2026-09-30"},
                {"title": "Estagiar como Lider substituto", "status": "pending", "due": "2026-12-31"},
            ]
            await conn.execute(
                text("""INSERT INTO career_plans
                    (id, employee_id, current_position, target_position,
                     current_level, target_level, estimated_timeline_months,
                     status, milestones, mentor_id)
                    VALUES (:id, :eid, 'Agente de Portaria', 'Lider de Portaria',
                            'junior', 'coordinator', 18, 'active', :milestones, :mentor)"""),
                {"id": uid(), "eid": emp_id, "milestones": json.dumps(milestones), "mentor": mentor},
            )
            career_count += 1
        for emp_id in ARTIFICES:
            milestones = [
                {"title": "Certificacao NR-10 Eletrica", "status": "pending", "due": "2026-06-30"},
                {"title": "Curso Hidraulica Predial", "status": "pending", "due": "2026-09-30"},
            ]
            await conn.execute(
                text("""INSERT INTO career_plans
                    (id, employee_id, current_position, target_position,
                     current_level, target_level, estimated_timeline_months,
                     status, milestones)
                    VALUES (:id, :eid, 'Artifice', 'Artifice Especializado',
                            'pleno', 'senior', 12, 'active', :milestones)"""),
                {"id": uid(), "eid": emp_id, "milestones": json.dumps(milestones)},
            )
            career_count += 1
        print(f"career_plans: {career_count} inseridos")

        # ===== 7. JOB_POSITIONS (5) =====
        positions: list[str] = []
        pos_data = [
            ("Agente de Portaria Diurno", "Vaga para portaria diurna 12x36 em condominio residencial", "full_time", 3),
            ("Agente de Portaria Noturno", "Vaga para portaria noturna 12x36 em condominio comercial", "full_time", 2),
            ("Agente de Servicos Gerais", "Vaga para limpeza e conservacao de areas comuns", "full_time", 2),
            ("Artifice de Manutencao", "Vaga para manutencao predial eletrica e hidraulica", "full_time", 1),
            (
                "Lider de Portaria",
                "Vaga para lideranca de equipe de porteiros em condominio de grande porte",
                "full_time",
                1,
            ),
        ]
        for title, desc, ptype, vac in pos_data:
            pid = uid()
            positions.append(pid)
            await conn.execute(
                text("""INSERT INTO job_positions
                    (id, title, description, position_type, vacancies, status,
                     city, state, salary_min, salary_max, deadline, published_at, responsible_id)
                    VALUES (:id, :title, :desc, :ptype, :vac, 'aberta',
                            'Manaus', 'AM', 1518.0, 2200.0, :deadline, :pub, :resp)"""),
                {
                    "id": pid,
                    "title": title,
                    "desc": desc,
                    "ptype": ptype,
                    "vac": vac,
                    "deadline": date(2026, 4, 30),
                    "pub": datetime(2026, 3, 10, 8, 0),
                    "resp": ADMIN_USER,
                },
            )
        print(f"job_positions: {len(positions)} inseridos")

        # ===== 8. CANDIDATES (10) =====
        candidates: list[str] = []
        cand_data = [
            (
                "MARCOS OLIVEIRA SILVA",
                "marcos.oliveira@email.com",
                "92991001001",
                "12345678901",
                "Agente de Portaria",
                "imediata",
            ),
            (
                "PATRICIA SANTOS LIMA",
                "patricia.lima@email.com",
                "92991002002",
                "23456789012",
                "Agente de Portaria",
                "imediata",
            ),
            (
                "RODRIGO ALMEIDA COSTA",
                "rodrigo.costa@email.com",
                "92991003003",
                "34567890123",
                "Agente de Portaria",
                "15 dias",
            ),
            (
                "FERNANDA RIBEIRO SOUZA",
                "fernanda.souza@email.com",
                "92991004004",
                "45678901234",
                "Agente de Servicos Gerais",
                "imediata",
            ),
            (
                "LUCAS PEREIRA NASCIMENTO",
                "lucas.nascimento@email.com",
                "92991005005",
                "56789012345",
                "Agente de Portaria",
                "imediata",
            ),
            (
                "AMANDA COSTA FERREIRA",
                "amanda.ferreira@email.com",
                "92991006006",
                "67890123456",
                "Agente de Servicos Gerais",
                "30 dias",
            ),
            (
                "JOSE CARLOS MARTINS",
                "jose.martins@email.com",
                "92991007007",
                "78901234567",
                "Artifice de Manutencao",
                "imediata",
            ),
            (
                "MARIA EDUARDA GONCALVES",
                "maria.goncalves@email.com",
                "92991008008",
                "89012345678",
                "Agente de Portaria",
                "imediata",
            ),
            (
                "THIAGO SANTOS ARAUJO",
                "thiago.araujo@email.com",
                "92991009009",
                "90123456789",
                "Lider de Portaria",
                "15 dias",
            ),
            (
                "CAMILA RODRIGUES PINTO",
                "camila.pinto@email.com",
                "92991010010",
                "01234567890",
                "Agente de Portaria",
                "imediata",
            ),
        ]
        for name, email, phone, cpf, pos, avail in cand_data:
            cid = uid()
            candidates.append(cid)
            await conn.execute(
                text("""INSERT INTO candidates
                    (id, name, email, phone, cpf, current_position, availability,
                     city, state, status, source)
                    VALUES (:id, :name, :email, :phone, :cpf, :pos, :avail,
                            'Manaus', 'AM', 'ativo', 'indicacao')"""),
                {"id": cid, "name": name, "email": email, "phone": phone, "cpf": cpf, "pos": pos, "avail": avail},
            )
        print(f"candidates: {len(candidates)} inseridos")

        # ===== 9. CANDIDATE_EDUCATIONS (10) =====
        edu_data = [
            ("Ensino Medio Completo", None, "E.E. Getulio Vargas"),
            ("Ensino Medio Completo", None, "E.E. Santos Dumont"),
            ("Curso Tecnico em Seguranca", "Seguranca Patrimonial", "SENAC Manaus"),
            ("Ensino Medio Completo", None, "SESI Manaus"),
            ("Ensino Superior Incompleto", "Administracao", "UEA"),
            ("Ensino Medio Completo", None, "E.E. Pedro II"),
            ("Curso Tecnico em Eletrica", "Eletrotecnica", "IFAM"),
            ("Ensino Medio Completo", None, "E.E. Amazonense"),
            ("Ensino Superior", "Gestao de Seguranca", "UNINORTE"),
            ("Ensino Medio Completo", None, "E.E. Nilton Lins"),
        ]
        for i, (degree, field, inst) in enumerate(edu_data):
            await conn.execute(
                text("""INSERT INTO candidate_educations
                    (id, candidate_id, institution, degree, field_of_study, start_date, end_date)
                    VALUES (:id, :cid, :inst, :degree, :field, :start, :end)"""),
                {
                    "id": uid(),
                    "cid": candidates[i],
                    "inst": inst,
                    "degree": degree,
                    "field": field,
                    "start": date(2015, 2, 1),
                    "end": date(2017, 12, 15),
                },
            )
        print(f"candidate_educations: {len(edu_data)} inseridos")

        # ===== 10. CANDIDATE_EXPERIENCES (10) =====
        exp_data = [
            ("Vigilante", "Prosegur Manaus", date(2022, 1, 1), date(2025, 12, 31), False),
            ("Porteira", "Condominio Parque das Aguas", date(2023, 6, 1), date(2025, 11, 30), False),
            ("Porteiro", "Solar dos Rios", date(2021, 3, 1), None, True),
            ("Auxiliar de Limpeza", "Limpa Mais Servicos", date(2024, 1, 1), date(2025, 10, 31), False),
            ("Porteiro", "Edif. Comercial Center Plaza", date(2022, 8, 1), date(2025, 9, 30), False),
            ("Servicos Gerais", "Hospital Samel", date(2023, 1, 1), date(2025, 12, 31), False),
            ("Eletricista Predial", "MRV Engenharia", date(2020, 6, 1), date(2025, 8, 31), False),
            ("Recepcionista", "Hotel Tropical Manaus", date(2024, 3, 1), date(2025, 12, 31), False),
            ("Sup. Portaria", "G4S Seguranca", date(2019, 1, 1), date(2025, 7, 31), False),
            ("Porteira", "Cond. Villa Lobos", date(2023, 9, 1), None, True),
        ]
        for i, (pos, company, start, end, current) in enumerate(exp_data):
            await conn.execute(
                text("""INSERT INTO candidate_experiences
                    (id, candidate_id, company, position, start_date, end_date, is_current)
                    VALUES (:id, :cid, :comp, :pos, :start, :end, :current)"""),
                {
                    "id": uid(),
                    "cid": candidates[i],
                    "comp": company,
                    "pos": pos,
                    "start": start,
                    "end": end,
                    "current": current,
                },
            )
        print(f"candidate_experiences: {len(exp_data)} inseridos")

        # ===== 11. CANDIDATE_SKILLS (15) =====
        skill_data = [
            (0, "Controle de Acesso", "seguranca", "intermediario", 3),
            (0, "Comunicacao via Radio", "seguranca", "avancado", 4),
            (1, "Atendimento ao Publico", "comportamental", "avancado", 5),
            (2, "CFTV Monitoramento", "tecnico", "intermediario", 2),
            (3, "Limpeza Profissional", "tecnico", "avancado", 3),
            (4, "Portaria Eletronica", "tecnico", "basico", 1),
            (5, "Conservacao Predial", "tecnico", "intermediario", 2),
            (6, "Eletrica Predial", "tecnico", "avancado", 5),
            (6, "Hidraulica", "tecnico", "intermediario", 3),
            (7, "Recepcao", "comportamental", "avancado", 4),
            (8, "Gestao de Equipes", "lideranca", "avancado", 6),
            (8, "Elaboracao de Escalas", "lideranca", "intermediario", 4),
            (9, "Controle de Acesso", "seguranca", "intermediario", 2),
            (3, "Manuseio de Produtos Quimicos", "tecnico", "intermediario", 2),
            (4, "Primeiros Socorros", "seguranca", "basico", 1),
        ]
        for cidx, skill_name, cat, level, years in skill_data:
            await conn.execute(
                text("""INSERT INTO candidate_skills
                    (id, candidate_id, name, category, level, years_of_experience)
                    VALUES (:id, :cid, :name, :cat, :level, :years)"""),
                {"id": uid(), "cid": candidates[cidx], "name": skill_name, "cat": cat, "level": level, "years": years},
            )
        print(f"candidate_skills: {len(skill_data)} inseridos")

        # ===== 12. APPLICATIONS (8) =====
        apps: list[str] = []
        app_data = [
            (0, 0, "triagem", 8.5),
            (1, 0, "entrevista", 7.8),
            (2, 1, "nova", 6.5),
            (3, 2, "triagem", 7.2),
            (4, 0, "entrevista", 8.0),
            (5, 2, "nova", 6.8),
            (6, 3, "triagem", 8.2),
            (8, 4, "entrevista", 9.0),
        ]
        for cidx, pidx, status, score in app_data:
            aid = uid()
            apps.append(aid)
            await conn.execute(
                text("""INSERT INTO applications
                    (id, job_position_id, candidate_id, status, ai_match_score, assigned_to_id)
                    VALUES (:id, :jid, :cid, :status, :score, :resp)"""),
                {
                    "id": aid,
                    "jid": positions[pidx],
                    "cid": candidates[cidx],
                    "status": status,
                    "score": score,
                    "resp": ADMIN_USER,
                },
            )
        print(f"applications: {len(apps)} inseridos")

        # ===== 13. INTERVIEWS (4) =====
        int_data = [
            (1, "individual", "presencial", datetime(2026, 3, 18, 10, 0), "agendada", "Sala de reunioes Conecta Mais"),
            (4, "individual", "presencial", datetime(2026, 3, 18, 14, 0), "agendada", "Sala de reunioes Conecta Mais"),
            (7, "painel", "presencial", datetime(2026, 3, 19, 9, 0), "agendada", "Sala de reunioes Conecta Mais"),
            (1, "tecnica", "online", datetime(2026, 3, 20, 10, 0), "agendada", None),
        ]
        for aidx, itype, fmt, sched, status, loc in int_data:
            await conn.execute(
                text("""INSERT INTO interviews
                    (id, application_id, interview_type, format, scheduled_at, status, location, duration_minutes)
                    VALUES (:id, :aid, :itype, :fmt, :sched, :status, :loc, 45)"""),
                {
                    "id": uid(),
                    "aid": apps[aidx],
                    "itype": itype,
                    "fmt": fmt,
                    "sched": sched,
                    "status": status,
                    "loc": loc,
                },
            )
        print(f"interviews: {len(int_data)} inseridos")

    print("\n=== SEED COMPLETO ===")

    # Verificação
    async with engine.connect() as conn:
        print("\n=== CONTAGEM FINAL ===")
        for table in [
            "training_courses",
            "trainings",
            "training_enrollments",
            "training_certificates",
            "performance_reviews",
            "career_plans",
            "job_positions",
            "candidates",
            "candidate_educations",
            "candidate_experiences",
            "candidate_skills",
            "applications",
            "interviews",
        ]:
            r = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            print(f"  {table}: {r.scalar()} registros")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
