"""Seeder de alocações funcionário → condomínio — FASE 3.5 GEDEON

Grafia oficial da planilha VT/VR (03/2026).
Idempotente: pula alocação se (employee_id, condominio_id, ativo=True) já existe.
"""

import os
import sys
import uuid
from datetime import date

sys.path.insert(0, "/app")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DATA_INICIO = date(2026, 1, 1)

ALOCACOES = [
    # IDEAL FLORES — 11
    {"nome": "ANTONIO CARLOS CASTRO GAMA", "condominio": "ideal_flores", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "ANTONIO DINIZ ASSIS DOS SANTOS", "condominio": "ideal_flores", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "ANTONIO WALCICLEY PEREIRA DA SILVA", "condominio": "ideal_flores", "funcao": "LÍDER DE PORTARIA"},
    {"nome": "CELIANE GARCIA DE SOUSA", "condominio": "ideal_flores", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "DANIEL VIDAL LARROQUE", "condominio": "ideal_flores", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "EDILENE SALES SOUSA", "condominio": "ideal_flores", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "FERNANDA VINHOTE MACIEL", "condominio": "ideal_flores", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "GEILSON RODRIGUES", "condominio": "ideal_flores", "funcao": "JARDINEIRO"},
    {"nome": "JONHATA DINIZ BENAION", "condominio": "ideal_flores", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "LIVIA CARISE PEREIRA CONSENTINE", "condominio": "ideal_flores", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "MARTA DA SILVA PINHEIRO", "condominio": "ideal_flores", "funcao": "AGENTE DE PORTARIA"},
    # VILLA PÁSSAROS — 6
    {"nome": "ADEMIR SALUSTIANO DE SOUZA FILHO", "condominio": "villa_passaros", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "EDWARD JOSE ATENCIO DOMINGUEZ", "condominio": "villa_passaros", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "FERNANDO SOUZA SIMPLICIO JUNIOR", "condominio": "villa_passaros", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "KALEL SILVA DE JESUS", "condominio": "villa_passaros", "funcao": "ARTÍFICE"},
    {"nome": "MARCELINO AURISMAR DA SILVA", "condominio": "villa_passaros", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "OSCAR SOARES COSTA FILHO", "condominio": "villa_passaros", "funcao": "SERVIÇOS GERAIS"},
    # MICHELANGELO — 1
    {"nome": "ANTONIO CARLOS VIEIRA", "condominio": "michelangelo", "funcao": "ARTÍFICE"},
    # MIRANTE — 10
    {"nome": "AILTON CESAR VASCONCELOS", "condominio": "mirante", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "EDIWILSON CORREA MARQUES", "condominio": "mirante", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "EDUARDO OLIVEIRA DE SOUZA", "condominio": "mirante", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "MAIARA MUNIZ DE SANTOS", "condominio": "mirante", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "MALAQUIAS PEREIRA FERREIRA", "condominio": "mirante", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "RAILSON ASSUNÇÃO LIMA", "condominio": "mirante", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "TELMA MARIA LAGES MEIRA", "condominio": "mirante", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "THAIS FERREIRA MATOS", "condominio": "mirante", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "VANDERLICE SANTOS DA SILVA", "condominio": "mirante", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "ERIKA CRISTINA MAQUINE PEREIRA", "condominio": "mirante", "funcao": "LÍDER DE PORTARIA"},
    # PRIME ARENA — 7
    {"nome": "ARYELTON BRAGA FIGUEIRA", "condominio": "prime_arena", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "CARLOS EDUARDO DA SILVA FACANHA", "condominio": "prime_arena", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "FRANCISCO RAMON FARIAS DE SOUZA", "condominio": "prime_arena", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "GRACIENE PEREIRA DE CASTRO", "condominio": "prime_arena", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "MAURICIO ALVES CHAGAS", "condominio": "prime_arena", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "RAIMUNDO JOSE BATISTA DA SILVA", "condominio": "prime_arena", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "RILEM FERREIRA DE SOUZA", "condominio": "prime_arena", "funcao": "AGENTE DE PORTARIA"},
    # VILLA DEI FIORI — 6
    {"nome": "CINTIA BEZERRA OLIVEIRA", "condominio": "villa_dei_fiori", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "GERNANES BINDA APARICIO", "condominio": "villa_dei_fiori", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "JAQUELINE CARLOS DOS SANTOS", "condominio": "villa_dei_fiori", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "KEYSON DA SILVA PINTO", "condominio": "villa_dei_fiori", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "LORINALDO OLIVEIRA DA SILVA", "condominio": "villa_dei_fiori", "funcao": "SERVIÇOS GERAIS"},
    {"nome": "RUAN RODRIGUES FIGUEIREDO", "condominio": "villa_dei_fiori", "funcao": "AGENTE DE PORTARIA"},
    # LARANJEIRAS — 6
    {"nome": "ADAILSON SERRA ALVES", "condominio": "laranjeiras", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "ANDREA GONÇALVES DOS SANTOS", "condominio": "laranjeiras", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "ANILSON JOSE SEIXAS NEVES", "condominio": "laranjeiras", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "BIANCA HELLEM DA SILVA MEIRA", "condominio": "laranjeiras", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "EIDY CULIER DE CASTRO", "condominio": "laranjeiras", "funcao": "AGENTE DE PORTARIA"},
    {"nome": "ELEN XAVIER NUNES", "condominio": "laranjeiras", "funcao": "AGENTE DE PORTARIA"},
    # ESCRITÓRIO — 2
    {"nome": "ELIZIEL GONZAGA", "condominio": "escritorio", "funcao": "ADMINISTRATIVO"},
    {"nome": "SEBASTIAO LIMA DE FREITAS", "condominio": "escritorio", "funcao": "ADMINISTRATIVO"},
]


def seed(db_url: str | None = None) -> None:
    url = db_url or os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    engine = create_engine(url)
    nao_encontrados = []
    criados = 0
    ja_existem = 0

    with Session(engine) as session:
        for a in ALOCACOES:
            # Find employee by partial name match
            emp = session.execute(
                text("SELECT id FROM employees WHERE nome ILIKE :pattern LIMIT 1"),
                {"pattern": f"%{a['nome']}%"},
            ).first()
            if not emp:
                nao_encontrados.append(a["nome"])
                continue

            cond = session.execute(
                text("SELECT id FROM condominios WHERE nome_normalizado = :slug"),
                {"slug": a["condominio"]},
            ).first()
            if not cond:
                print(f"❌ Condomínio não encontrado: {a['condominio']}")
                continue

            exists = session.execute(
                text(
                    "SELECT id FROM employee_alocacoes "
                    "WHERE employee_id = :eid AND condominio_id = :cid AND ativo = true"
                ),
                {"eid": str(emp[0]), "cid": str(cond[0])},
            ).first()
            if exists:
                ja_existem += 1
                continue

            session.execute(
                text(
                    "INSERT INTO employee_alocacoes "
                    "(id, employee_id, condominio_id, funcao, data_inicio, ativo, created_at) "
                    "VALUES (:id, :eid, :cid, :funcao, :dt, true, NOW())"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "eid": str(emp[0]),
                    "cid": str(cond[0]),
                    "funcao": a["funcao"],
                    "dt": DATA_INICIO,
                },
            )
            criados += 1
            print(f"✅ {a['nome']} → {a['condominio']}")

        session.commit()

        total = session.execute(text("SELECT COUNT(*) FROM employee_alocacoes")).scalar()
        print(f"\n📊 Resumo: {criados} criados, {ja_existem} já existentes, {len(nao_encontrados)} não encontrados")
        print(f"📊 Total alocações no DB: {total}")

        if nao_encontrados:
            print(f"\n⚠️  Funcionários não encontrados ({len(nao_encontrados)}):")
            for n in nao_encontrados:
                print(f"  - {n}")


if __name__ == "__main__":
    seed()
