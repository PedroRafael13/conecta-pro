"""Skills IA do Departamento Pessoal."""

from modules.people_management.hr.skills.benefits_skill import BenefitsSkill
from modules.people_management.hr.skills.compliance_skill import ComplianceSkill
from modules.people_management.hr.skills.documenter_skill import DocumenterSkill
from modules.people_management.hr.skills.payroll_skill import PayrollSkill

__all__ = [
    "PayrollSkill",
    "ComplianceSkill",
    "DocumenterSkill",
    "BenefitsSkill",
]
