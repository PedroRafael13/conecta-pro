"""Service: renderiza contrato de trabalho com Jinja2 e persiste em disco."""

from datetime import date, datetime
from pathlib import Path

from jinja2 import StrictUndefined, Template
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_TEMPLATE_CANDIDATES = [
    Path("/app/templates/contrato_trabalho.html"),
    Path("/app/templates/templates/contrato_trabalho.html"),
]
_UPLOAD_DIR = Path("/app/uploads/contratos_gerados")


class ContratoGerado(BaseModel):
    template_slug: str
    employee_id: str
    employee_name: str
    file_path: str
    file_url: str
    generated_at: datetime
    formato: str


class ContractGeneratorService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def gerar_contrato_trabalho_html(self, employee_id: str) -> ContratoGerado:
        emp = await self._get_employee(employee_id)
        if not emp:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        html_template = await self._get_template()

        sal = float(emp["salario_base"] or 0)
        sal_fmt = f"R$ {sal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        adm = emp["data_admissao"]
        start_date_str = adm.strftime("%d/%m/%Y") if adm else ""

        context = {
            "employee_name": emp["nome"] or "",
            "cpf": emp["cpf"] or "",
            "role": emp["cargo"] or "",
            "start_date": start_date_str,
            "base_salary": sal_fmt,
            "contract_date": date.today().strftime("%d/%m/%Y"),
        }

        rendered = Template(html_template, undefined=StrictUndefined).render(context)

        output_dir = _UPLOAD_DIR / employee_id
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contrato_trabalho_{ts}.html"
        file_path = output_dir / filename
        file_path.write_text(rendered, encoding="utf-8")

        file_url = f"/api/v1/people-management/hr/contracts/employee/{employee_id}/download/{filename}"

        return ContratoGerado(
            template_slug="contrato_trabalho",
            employee_id=employee_id,
            employee_name=emp["nome"] or "",
            file_path=str(file_path),
            file_url=file_url,
            generated_at=datetime.now(),
            formato="html",
        )

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
