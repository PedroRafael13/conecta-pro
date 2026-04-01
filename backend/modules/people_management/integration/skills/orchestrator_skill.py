"""Skill IA: Orchestrator — Orquestração de todos os módulos de Gestão de Pessoas."""

import logging
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class OrchestratorSkill:
    """Skill IA para orquestração completa dos módulos DP + RH + Ops."""

    SKILL_NAME = "people_orchestrator"
    DESCRIPTION = "Orquestração e coordenação entre DP, RH e Operações"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def full_employee_overview(self, employee_id: str) -> dict:
        """Visão 360 do funcionário cruzando todos os módulos."""
        overview = {"employee_id": employee_id, "modules": {}}

        try:
            from modules.people_management.hr.services.payroll_service import PayrollService

            svc = PayrollService(self.db)
            today = date.today()
            payroll = await svc.calculate_employee_payroll(employee_id, today.month, today.year)
            overview["modules"]["payroll"] = {
                "salario_base": payroll["salario_base"],
                "salario_liquido": payroll["salario_liquido"],
                "status": "ok",
            }
        except Exception as e:
            overview["modules"]["payroll"] = {"status": "error", "error": str(e)}

        try:
            from modules.people_management.hr.services.vacation_service import VacationService

            svc = VacationService(self.db)
            vacation = await svc.calculate_vacation_balance(employee_id)
            overview["modules"]["vacation"] = {
                "dias_saldo": vacation["dias_saldo"],
                "status": "ok",
            }
        except Exception as e:
            overview["modules"]["vacation"] = {"status": "error", "error": str(e)}

        try:
            from modules.people_management.human_resources.skills.evaluator_skill import EvaluatorSkill

            evaluator = EvaluatorSkill(self.db)
            perf = await evaluator.employee_performance_history(employee_id)
            overview["modules"]["performance"] = {
                "total_reviews": perf["total_reviews"],
                "average_score": perf["average_score"],
                "trend": perf["trend"],
                "status": "ok",
            }
        except Exception as e:
            overview["modules"]["performance"] = {"status": "error", "error": str(e)}

        try:
            from modules.people_management.hr.skills.compliance_skill import ComplianceSkill

            compliance = ComplianceSkill(self.db)
            check = await compliance.check_employee_compliance(employee_id)
            overview["modules"]["compliance"] = {
                "score": check["compliance_score"],
                "issues": len(check["issues"]),
                "status": "ok",
            }
        except Exception as e:
            overview["modules"]["compliance"] = {"status": "error", "error": str(e)}

        overview["generated_at"] = datetime.utcnow().isoformat()
        return overview

    async def company_health_dashboard(self) -> dict:
        """Dashboard executivo de saúde da empresa — todos os módulos."""
        dashboard = {"sections": {}}

        try:
            from modules.people_management.hr.skills.compliance_skill import ComplianceSkill

            compliance = ComplianceSkill(self.db)
            bulk = await compliance.bulk_compliance_check()
            dashboard["sections"]["compliance"] = {
                "rate": bulk["compliance_rate"],
                "total_issues": bulk["total_issues"],
            }
        except Exception as e:
            dashboard["sections"]["compliance"] = {"error": str(e)}

        try:
            from modules.people_management.operations.skills.planner_skill import PlannerSkill

            planner = PlannerSkill(self.db)
            coverage = await planner.coverage_analysis()
            dashboard["sections"]["operations"] = {
                "coverage_rate": coverage["coverage_rate"],
                "utilization_rate": coverage["utilization_rate"],
            }
        except Exception as e:
            dashboard["sections"]["operations"] = {"error": str(e)}

        try:
            from modules.people_management.common.skills.notifier_skill import NotifierSkill

            notifier = NotifierSkill(self.db)
            alerts_data = await notifier.check_pending_alerts()
            dashboard["sections"]["alerts"] = {"total": alerts_data["total_alerts"]}
        except Exception as e:
            dashboard["sections"]["alerts"] = {"error": str(e)}

        dashboard["generated_at"] = datetime.utcnow().isoformat()
        return dashboard
