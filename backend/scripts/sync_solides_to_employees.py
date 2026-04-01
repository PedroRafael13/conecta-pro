"""
Script de propagacao Solides/Tangerino -> tabela employees.

Busca dados da API Tangerino e atualiza campos pessoais
(data_nascimento, sexo, PIS, data_admissao) na tabela employees
sem tocar em cargo e salario (que ja existem).

Uso:
  docker exec conecta-pro-backend python3 scripts/sync_solides_to_employees.py
"""

import os
import sys
from datetime import datetime

import httpx
from sqlalchemy import create_engine, text


def main():
    token = os.environ.get("SOLIDES_API_TOKEN")
    if not token:
        print("ERRO: SOLIDES_API_TOKEN nao configurado")
        sys.exit(1)

    headers = {"Authorization": f"Basic {token}"}

    # Buscar funcionarios do Tangerino
    print("Buscando funcionarios do Tangerino...")
    all_employees = []
    page = 0
    while True:
        resp = httpx.get(
            f"https://employer.tangerino.com.br/employee/find-all?size=100&page={page}",
            headers=headers,
        )
        data = resp.json()
        items = data.get("content", data) if isinstance(data, dict) else data
        if not items:
            break
        all_employees.extend(items)
        if isinstance(data, dict) and data.get("last", True):
            break
        page += 1

    print(f"Tangerino: {len(all_employees)} funcionarios")

    # Conectar ao banco
    db_url = os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    engine = create_engine(db_url)
    updated = 0
    skipped = 0

    with engine.connect() as conn:
        for emp in all_employees:
            cpf = (emp.get("cpf") or "").replace(".", "").replace("-", "").strip()
            if not cpf:
                skipped += 1
                continue

            birth = None
            bd = emp.get("birthDate")
            if bd:
                try:
                    birth = datetime.fromtimestamp(bd / 1000).date()
                except Exception:
                    pass

            adm = None
            ad = emp.get("admissionDate")
            if ad:
                try:
                    adm = datetime.fromtimestamp(ad / 1000).date()
                except Exception:
                    pass

            gender = emp.get("gender", "")
            sexo = None
            if "FEM" in gender.upper():
                sexo = "F"
            elif "MASC" in gender.upper():
                sexo = "M"

            pis = (emp.get("pis", "") or "")[:20]
            sid = str(emp.get("id", ""))

            sets = []
            params = {"cpf": cpf}
            if birth:
                sets.append("data_nascimento = :b")
                params["b"] = birth
            if sexo:
                sets.append("sexo = :s")
                params["s"] = sexo
            if pis:
                sets.append("pis = :p")
                params["p"] = pis
            if adm:
                sets.append("data_admissao = :a")
                params["a"] = adm
            if sid:
                sets.append("solides_id = :sid")
                params["sid"] = sid

            if sets:
                sql = f"UPDATE employees SET {', '.join(sets)} WHERE cpf = :cpf AND status = 'ativo'"
                r = conn.execute(text(sql), params)
                if r.rowcount > 0:
                    updated += 1
                else:
                    skipped += 1

        conn.commit()

    print(f"Resultado: {updated} atualizados, {skipped} sem match")
    print("(cargos e salarios mantidos intactos)")


if __name__ == "__main__":
    main()
