"""Seeder: popula contract_templates com o template HTML de contrato de trabalho."""

import sys

sys.path.insert(0, "/app")

import uuid
from pathlib import Path

from sqlalchemy import text

_TEMPLATE_CANDIDATES = [
    Path("/app/templates/contrato_trabalho.html"),
    Path("/app/templates/templates/contrato_trabalho.html"),
]


def seed() -> None:
    from core.database.session import SyncSessionLocal

    html_path = next((p for p in _TEMPLATE_CANDIDATES if p.exists()), None)
    if not html_path:
        print("❌ Template HTML não encontrado em nenhum caminho esperado.")
        sys.exit(1)
    html = html_path.read_text(encoding="utf-8")

    with SyncSessionLocal() as db:
        exists = db.execute(text("SELECT id FROM contract_templates WHERE service_type = 'admissao' LIMIT 1")).first()

        if exists:
            print(f"⚠️  Template já existe (id={exists[0]}), pulando.")
            return

        db.execute(
            text("""
                INSERT INTO contract_templates
                    (id, name, description, service_type, content_template,
                     variables, version, approved_by_legal, is_active, created_at)
                VALUES
                    (:id, :name, :description, :service_type, :content_template,
                     CAST(:variables AS jsonb), :version, :approved_by_legal, :is_active, now())
            """),
            {
                "id": str(uuid.uuid4()),
                "name": "Contrato de Trabalho CLT",
                "description": "Contrato CLT padrão Conecta Mais — gerado via template HTML",
                "service_type": "admissao",
                "content_template": html,
                "variables": '{"required": ["employee_name", "cpf", "role", "start_date", "base_salary", "contract_date"]}',
                "version": 1,
                "approved_by_legal": False,
                "is_active": True,
            },
        )
        db.commit()
        print("✅ Template 'Contrato de Trabalho CLT' inserido com sucesso.")


if __name__ == "__main__":
    seed()
