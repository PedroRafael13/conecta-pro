"""Service: renderiza contrato de trabalho em HTML para um funcionário."""

import re
from datetime import date
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_TEMPLATE_CANDIDATES = [
    Path("/app/templates/contrato_trabalho.html"),
    Path("/app/templates/templates/contrato_trabalho.html"),
]


class ContractGeneratorService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def gerar_contrato_trabalho_html(self, employee_id: str) -> dict:
        emp = await self._get_employee(employee_id)
        if not emp:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        html = await self._get_template()

        sal = float(emp["salario_base"] or 0)
        sal_fmt = f"R$ {sal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        adm = emp["data_admissao"]
        start_date_str = adm.strftime("%d/%m/%Y") if adm else ""

        variables = {
            "employee_name": emp["nome"] or "",
            "cpf": emp["cpf"] or "",
            "role": emp["cargo"] or "",
            "start_date": start_date_str,
            "base_salary": sal_fmt,
            "contract_date": date.today().strftime("%d/%m/%Y"),
        }

        rendered = self._render(html, variables)
        nome_slug = re.sub(r"[^\w]", "_", (emp["nome"] or "funcionario").lower())[:40]

        return {
            "html_content": rendered,
            "filename": f"contrato_trabalho_{nome_slug}.html",
            "employee_name": emp["nome"],
        }

    async def _get_employee(self, employee_id: str) -> dict | None:
        r = await self.db.execute(
            text("""
                SELECT nome, cpf, cargo, data_admissao, salario_base
                FROM employees
                WHERE id = CAST(:eid AS uuid)
                  AND is_active = true
                LIMIT 1
            """),
            {"eid": employee_id},
        )
        row = r.mappings().first()
        return dict(row) if row else None

    async def _get_template(self) -> str:
        r = await self.db.execute(
            text("""
                SELECT content_template
                FROM contract_templates
                WHERE service_type = 'admissao'
                  AND is_active = true
                ORDER BY created_at ASC
                LIMIT 1
            """)
        )
        row = r.first()
        if row and row[0]:
            return row[0]
        for p in _TEMPLATE_CANDIDATES:
            if p.exists():
                return p.read_text(encoding="utf-8")
        raise FileNotFoundError("Template contrato_trabalho.html não encontrado")

    @staticmethod
    def _render(html: str, variables: dict) -> str:
        for key, value in variables.items():
            html = re.sub(r"\{\{\s*" + re.escape(key) + r"\s*\}\}", value, html)
        return html
