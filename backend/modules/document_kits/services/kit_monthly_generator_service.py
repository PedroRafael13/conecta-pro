"""
Serviço de Geração Automática de Kits Mensais.

Este serviço gera automaticamente kits documentais mensais para todos os funcionários
de um condomínio, usando a integração com o módulo operacional.

Autor: Jordan Santos de Jesus LTDA
Data: 23/01/2026
"""

import logging
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.document_kits.models.document_kit import (
    DocumentKit,
    DocumentKitAssignment,
    EntityType,
    KitStatus,
    KitType,
)
from modules.document_kits.schemas.kit_schemas import DocumentKitAssignmentCreate
from modules.document_kits.services.kit_operational_service import KitOperationalService
from modules.document_kits.services.kit_service import DocumentKitService

logger = logging.getLogger(__name__)


class KitMonthlyGeneratorService:
    """
    Serviço de geração automática de kits mensais.

    Responsável por:
    - Gerar kits mensais para todos os funcionários de um condomínio
    - Criar/reutilizar templates de kits
    - Atribuir kits automaticamente
    - Fornecer relatórios de geração
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.operational_service = KitOperationalService(db)
        self.kit_service = DocumentKitService(db)

    async def get_or_create_monthly_kit_template(
        self,
        condominio_id: UUID,
        month: int,
        year: int,
        created_by: UUID,
    ) -> DocumentKit:
        """
        Busca ou cria um template de kit mensal padrão.

        Args:
            condominio_id: UUID do condomínio
            month: Mês (1-12)
            year: Ano
            created_by: UUID do usuário que está criando

        Returns:
            DocumentKit template
        """
        # Buscar template existente
        result = await self.db.execute(
            select(DocumentKit)
            .where(
                DocumentKit.condominio_id == condominio_id,
                DocumentKit.is_template.is_(True),
                DocumentKit.tipo == KitType.MENSAL,
                DocumentKit.status == KitStatus.ATIVO,
            )
            .limit(1)
        )
        template = result.scalar_one_or_none()

        if template:
            logger.info(f"Template mensal encontrado: {template.nome}")
            return template

        # Criar novo template
        codigo = f"KIT-MENSAL-{condominio_id}-{uuid4().hex[:6].upper()}"
        nome = f"Kit Mensal de Documentos - {month:02d}/{year}"

        template_data = {
            "id": uuid4(),
            "condominio_id": condominio_id,
            "codigo": codigo,
            "nome": nome,
            "descricao": (
                "Kit mensal contendo holerite, vale transporte, vale alimentação, "
                "folha de ponto e demais documentos obrigatórios."
            ),
            "tipo": KitType.MENSAL,
            "categoria": "Trabalhista",
            "is_template": True,
            "status": KitStatus.ATIVO,
            "obrigatorio": True,
            "prazo_dias": 30,
            "tags": ["mensal", "trabalhista", "obrigatório"],
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        template = DocumentKit(**template_data)
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        logger.info(f"Novo template mensal criado: {template.nome}")
        return template

    async def generate_monthly_kits(
        self,
        condominio_id: str,
        month: int,
        year: int,
        created_by_id: str,
        prazo_dias: int | None = 30,
    ) -> dict:
        """
        Gera kits mensais para TODOS os funcionários de um condomínio.

        Esta é a função PRINCIPAL de geração automática.

        Args:
            condominio_id: UUID do condomínio
            month: Mês (1-12)
            year: Ano
            created_by_id: UUID do usuário que solicitou a geração
            prazo_dias: Prazo em dias para entrega (default: 30)

        Returns:
            Dict com resumo da geração:
            {
                "success": bool,
                "condominium_id": str,
                "period": "01/2026",
                "template_kit_id": str,
                "employees_found": int,
                "assignments_created": int,
                "assignments_skipped": int,
                "assignments_failed": int,
                "details": [...]
            }

        Example:
            >>> result = await generator.generate_monthly_kits(
            ...     condominio_id="uuid",
            ...     month=1,
            ...     year=2026,
            ...     created_by_id="user-uuid"
            ... )
            >>> print(f"{result['assignments_created']} kits criados")
        """
        try:
            cond_uuid = UUID(condominio_id)
            created_by_uuid = UUID(created_by_id)

            logger.info(f"Iniciando geração de kits mensais: condomínio={condominio_id}, período={month:02d}/{year}")

            # 1. Buscar funcionários do condomínio no período
            employees_data = await self.operational_service.get_employees_by_month(
                condominium_id=condominio_id,
                month=month,
                year=year,
                include_inactive=False,
            )

            if not employees_data:
                logger.warning(f"Nenhum funcionário encontrado para {condominio_id} em {month:02d}/{year}")
                return {
                    "success": True,
                    "condominium_id": condominio_id,
                    "period": f"{month:02d}/{year}",
                    "template_kit_id": None,
                    "employees_found": 0,
                    "assignments_created": 0,
                    "assignments_skipped": 0,
                    "assignments_failed": 0,
                    "details": [],
                    "message": "Nenhum funcionário encontrado no período",
                }

            # 2. Obter/criar template de kit mensal
            template_kit = await self.get_or_create_monthly_kit_template(
                condominio_id=cond_uuid,
                month=month,
                year=year,
                created_by=created_by_uuid,
            )

            # 3. Calcular data limite
            first_day = date(year, month, 1)
            data_limite = first_day + timedelta(days=prazo_dias)

            # 4. Criar atribuições para cada funcionário
            assignments_created = 0
            assignments_skipped = 0
            assignments_failed = 0
            details = []

            for emp_data in employees_data:
                employee = emp_data.employee
                allocation = emp_data.allocation
                post = emp_data.post

                try:
                    # Verificar se já existe atribuição para este funcionário neste mês
                    existing = await self.db.execute(
                        select(DocumentKitAssignment)
                        .where(
                            DocumentKitAssignment.kit_id == template_kit.id,
                            DocumentKitAssignment.entity_type == EntityType.FUNCIONARIO,
                            DocumentKitAssignment.entity_id == employee.id,
                            DocumentKitAssignment.condominio_id == cond_uuid,
                        )
                        .limit(1)
                    )
                    if existing.scalar_one_or_none():
                        logger.debug(f"Atribuição já existe para {employee.nome}")
                        assignments_skipped += 1
                        details.append(
                            {
                                "employee_id": str(employee.id),
                                "employee_name": employee.nome,
                                "status": "skipped",
                                "reason": "Atribuição já existe",
                            }
                        )
                        continue

                    # Criar atribuição
                    assignment_data = DocumentKitAssignmentCreate(
                        kit_id=template_kit.id,
                        condominio_id=cond_uuid,
                        entity_type=EntityType.FUNCIONARIO,
                        entity_id=employee.id,
                        entity_nome=employee.nome,
                        data_limite=data_limite,
                        responsavel_id=None,  # Será atribuído depois
                        observacoes=f"Kit mensal {month:02d}/{year} - Posto: {post.name} - Cargo: {allocation.role}",
                    )

                    assignment = self.kit_service.assign_kit(assignment_data, created_by_uuid)

                    assignments_created += 1
                    details.append(
                        {
                            "employee_id": str(employee.id),
                            "employee_name": employee.nome,
                            "assignment_id": str(assignment.id),
                            "post_name": post.name,
                            "role": allocation.role,
                            "status": "created",
                        }
                    )

                    logger.info(f"Kit atribuído para {employee.nome} (assignment_id={assignment.id})")

                except Exception as e:
                    logger.error(f"Erro ao criar atribuição para {employee.nome}: {e}")
                    assignments_failed += 1
                    details.append(
                        {
                            "employee_id": str(employee.id),
                            "employee_name": employee.nome,
                            "status": "failed",
                            "error": str(e),
                        }
                    )

            # 5. Retornar resumo
            result = {
                "success": True,
                "condominium_id": condominio_id,
                "period": f"{month:02d}/{year}",
                "template_kit_id": str(template_kit.id),
                "template_kit_name": template_kit.nome,
                "employees_found": len(employees_data),
                "assignments_created": assignments_created,
                "assignments_skipped": assignments_skipped,
                "assignments_failed": assignments_failed,
                "data_limite": data_limite.isoformat(),
                "details": details,
                "message": (
                    f"Geração concluída: {assignments_created} kits criados, "
                    f"{assignments_skipped} já existentes, {assignments_failed} falhas"
                ),
            }

            logger.info(
                f"Geração finalizada: {assignments_created} criados, "
                f"{assignments_skipped} skipped, {assignments_failed} falhas"
            )

            return result

        except Exception as e:
            logger.error(f"Erro na geração de kits mensais: {e}")
            return {
                "success": False,
                "condominium_id": condominio_id,
                "period": f"{month:02d}/{year}",
                "error": str(e),
                "message": f"Erro ao gerar kits: {str(e)}",
            }

    async def generate_kits_for_all_condominiums(
        self,
        month: int,
        year: int,
        created_by_id: str,
    ) -> dict:
        """
        Gera kits mensais para TODOS os condomínios que possuem funcionários.

        Função para execução em batch/scheduler.

        Args:
            month: Mês (1-12)
            year: Ano
            created_by_id: UUID do usuário/sistema que solicitou

        Returns:
            Dict com resumo geral da geração para todos os condomínios
        """
        logger.info(f"Iniciando geração em LOTE para período {month:02d}/{year}")

        # Buscar todos os condomínios com funcionários
        condominiums = await self.operational_service.get_condominiums_with_employees()

        if not condominiums:
            return {
                "success": True,
                "period": f"{month:02d}/{year}",
                "condominiums_processed": 0,
                "total_assignments_created": 0,
                "message": "Nenhum condomínio com funcionários encontrado",
            }

        results = []
        total_created = 0
        total_skipped = 0
        total_failed = 0

        for cond in condominiums:
            cond_id = cond["condominium_id"]
            cond_name = cond["condominium_name"]

            logger.info(f"Processando condomínio: {cond_name} ({cond_id})")

            result = await self.generate_monthly_kits(
                condominio_id=cond_id,
                month=month,
                year=year,
                created_by_id=created_by_id,
            )

            results.append(result)
            total_created += result.get("assignments_created", 0)
            total_skipped += result.get("assignments_skipped", 0)
            total_failed += result.get("assignments_failed", 0)

        summary = {
            "success": True,
            "period": f"{month:02d}/{year}",
            "condominiums_processed": len(results),
            "total_employees_found": sum(r.get("employees_found", 0) for r in results),
            "total_assignments_created": total_created,
            "total_assignments_skipped": total_skipped,
            "total_assignments_failed": total_failed,
            "condominiums_details": results,
            "message": (
                f"Geração em lote concluída: {len(results)} condomínios processados, "
                f"{total_created} kits criados, {total_skipped} já existentes, {total_failed} falhas"
            ),
        }

        logger.info(f"Geração em LOTE finalizada: {len(results)} condomínios, {total_created} kits criados")

        return summary
