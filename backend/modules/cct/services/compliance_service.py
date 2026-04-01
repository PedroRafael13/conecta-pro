"""
Servico de Compliance — CCT 2026.

Verificacao geral de conformidade: salarios, beneficios, jornadas.
"""

import logging
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.cct.models.cct_metadata import CCT_METADATA
from modules.cct.models.cct_tables import CCTComplianceCheck
from modules.cct.validators.salary_validator import SalaryValidator
from modules.cct.validators.stability_validator import StabilityValidator

logger = logging.getLogger(__name__)


class ComplianceService:
    """Servico de compliance CCT 2026."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def verificar_compliance_salarios(self, periodo: str) -> dict:
        """Verifica compliance salarial de todos os colaboradores.

        Busca colaboradores no banco e valida contra pisos CCT.

        Args:
            periodo: Periodo de referencia (YYYY-MM).

        Returns:
            Resultado da verificacao.
        """
        # Buscar colaboradores ativos
        try:
            from modules.operacional.models.employee import Employee

            query = select(Employee).where(Employee.status == "ativo")
            result = await self.db.execute(query)
            employees = list(result.scalars().all())
        except ImportError:
            employees = []
            logger.warning("Modelo Employee nao disponivel — verificacao sem dados reais")

        validator = SalaryValidator()
        itens = []
        conformes = 0
        nao_conformes = 0

        for emp in employees:
            cargo = getattr(emp, "cargo", None)
            salario = getattr(emp, "salario_base", None)

            if not cargo or not salario:
                continue

            resultado = validator.validar_salario(cargo, float(salario))

            if resultado["conforme"]:
                conformes += 1
            else:
                nao_conformes += 1

            itens.append(
                {
                    "employee_id": str(emp.id),
                    "employee_nome": getattr(emp, "nome", None),
                    "cargo": cargo,
                    "categoria": "salario",
                    "conforme": resultado["conforme"],
                    "detalhes": resultado.get("alerta") or "Conforme",
                }
            )

        total = conformes + nao_conformes
        percentual = round((conformes / total * 100) if total > 0 else 100, 2)

        alertas = []
        if nao_conformes > 0:
            alertas.append(f"{nao_conformes} colaborador(es) com salario abaixo do piso CCT")

        return {
            "tipo_verificacao": "salarios",
            "periodo_referencia": periodo,
            "total_funcionarios": total,
            "conformes": conformes,
            "nao_conformes": nao_conformes,
            "percentual_conformidade": percentual,
            "itens": itens,
            "alertas": alertas,
        }

    async def gerar_resumo_compliance(self, periodo: str, empresa_id: str | None = None) -> dict:
        """Gera resumo geral de compliance CCT.

        Args:
            periodo: Periodo de referencia (YYYY-MM).
            empresa_id: ID da empresa (opcional).

        Returns:
            Resumo de compliance.
        """
        salarios = await self.verificar_compliance_salarios(periodo)

        percentual_geral = salarios["percentual_conformidade"]
        status = "conforme"
        if percentual_geral < 100:
            status = "nao_conforme" if percentual_geral < 80 else "parcialmente_conforme"

        recomendacoes = []
        if salarios["nao_conformes"] > 0:
            recomendacoes.append(f"Reajustar {salarios['nao_conformes']} salario(s) para piso CCT")

        return {
            "empresa_id": empresa_id,
            "periodo": periodo,
            "cct_vigente": CCT_METADATA.nome,
            "registro_mte": CCT_METADATA.registro_mte,
            "salarios_conformes": salarios["conformes"],
            "salarios_total": salarios["total_funcionarios"],
            "beneficios_conformes": 0,
            "beneficios_total": 0,
            "jornadas_conformes": 0,
            "jornadas_total": 0,
            "percentual_geral": percentual_geral,
            "status": status,
            "recomendacoes": recomendacoes,
        }

    async def registrar_verificacao(
        self,
        tipo: str,
        periodo: str,
        resultado: dict,
        empresa_id: str | None = None,
        executado_por: str | None = None,
    ) -> CCTComplianceCheck:
        """Persiste resultado de verificacao de compliance.

        Args:
            tipo: Tipo de verificacao.
            periodo: Periodo de referencia.
            resultado: Resultado da verificacao.
            empresa_id: ID da empresa.
            executado_por: Usuario executor.

        Returns:
            Registro persistido.
        """
        check = CCTComplianceCheck(
            id=str(uuid4()),
            empresa_id=empresa_id,
            tipo_verificacao=tipo,
            periodo_referencia=periodo,
            total_funcionarios=resultado.get("total_funcionarios", 0),
            conformes=resultado.get("conformes", 0),
            nao_conformes=resultado.get("nao_conformes", 0),
            percentual_conformidade=resultado.get("percentual_conformidade", 0),
            detalhes=resultado,
            executado_por=executado_por,
        )
        self.db.add(check)
        await self.db.flush()
        await self.db.refresh(check)
        logger.info("Verificacao compliance CCT registrada: tipo=%s periodo=%s", tipo, periodo)
        return check

    def verificar_estabilidade(
        self,
        employee_id: str,
        data_admissao: str,
        data_nascimento: str | None = None,
        acidente_trabalho: bool = False,
        data_alta_inss: str | None = None,
        gestante: bool = False,
        data_parto: str | None = None,
    ) -> dict:
        """Verifica estabilidade de um colaborador."""
        return StabilityValidator.verificar_estabilidade(
            employee_id=employee_id,
            data_admissao=data_admissao,
            data_nascimento=data_nascimento,
            acidente_trabalho=acidente_trabalho,
            data_alta_inss=data_alta_inss,
            gestante=gestante,
            data_parto=data_parto,
        )
