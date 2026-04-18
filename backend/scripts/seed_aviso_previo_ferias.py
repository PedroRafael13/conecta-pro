"""Seeder: popula contract_templates com o template HTML de aviso prévio de férias."""

import sys

sys.path.insert(0, "/app")

import uuid
from pathlib import Path

from sqlalchemy import text

_TEMPLATE_CANDIDATES = [
    Path("/app/templates/aviso_previo_ferias.html"),
    Path("/app/templates/templates/aviso_previo_ferias.html"),
]

_SERVICE_TYPE = "ferias"

_VARIABLES = [
    "employee_name",
    "role",
    "admission_date",
    "period_start",
    "period_end",
    "vacation_start",
    "vacation_end",
    "vacation_days",
    "return_date",
    "notice_date",
]


def _load_template() -> str:
    for p in _TEMPLATE_CANDIDATES:
        if p.exists():
            return p.read_text(encoding="utf-8")
    raise FileNotFoundError("aviso_previo_ferias.html não encontrado em nenhum candidato")


def seed(db_url: str | None = None) -> None:
    import os

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    url = db_url or os.environ.get("DATABASE_URL", "").replace("+asyncpg", "")
    engine = create_engine(url)

    html_content = _load_template()
    variables_json = str(_VARIABLES).replace("'", '"')

    with Session(engine) as session:
        exists = session.execute(
            text("SELECT id FROM contract_templates WHERE service_type = :st AND is_active = true LIMIT 1"),
            {"st": _SERVICE_TYPE},
        ).first()

        if exists:
            print(f"⚠️  Template '{_SERVICE_TYPE}' já existe (id={exists[0]})")
            return

        session.execute(
            text("""
                INSERT INTO contract_templates
                    (id, name, service_type, content_template, variables, is_active, created_at, updated_at)
                VALUES (
                    :id, :name, :service_type,
                    :content_template,
                    CAST(:variables AS jsonb),
                    true, NOW(), NOW()
                )
            """),
            {
                "id": str(uuid.uuid4()),
                "name": "Aviso Prévio de Férias — CLT",
                "service_type": _SERVICE_TYPE,
                "content_template": html_content,
                "variables": variables_json,
            },
        )
        session.commit()
        print(f"✅ Template '{_SERVICE_TYPE}' inserido ({len(html_content)} chars, {len(_VARIABLES)} variáveis)")


if __name__ == "__main__":
    seed()
