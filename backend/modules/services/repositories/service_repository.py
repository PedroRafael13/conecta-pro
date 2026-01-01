"""
Service Repository - Data Access Layer
Sprint 31: Gestão de Serviços
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import func, or_, desc
from sqlalchemy.orm import Session

from modules.services.models.service_catalog import (
    ServiceCatalog, ServiceStatus
)
from modules.services.models.service_order import (
    ServiceOrder, OrderStatus
)
from modules.services.models.service_execution import ServiceExecution
from modules.services.models.service_report import ServiceReport
from modules.services.models.sla_config import SLAConfig
from modules.services.schemas.service_schemas import (
    ServiceCatalogCreate, ServiceCatalogUpdate,
    ServiceOrderCreate, ServiceOrderUpdate, ServiceOrderFilter,
    ServiceExecutionCreate, ServiceExecutionUpdate,
    ServiceReportCreate, ServiceReportUpdate,
    SLAConfigCreate, SLAConfigUpdate,
)

logger = logging.getLogger(__name__)


class ServiceRepository:
    """Repository para operações de dados do módulo Services."""

    def __init__(self, db: Session):
        """Inicializa o repository."""
        self.db = db

    # ========================================
    # SERVICE CATALOG
    # ========================================

    def create_service(self, data: ServiceCatalogCreate) -> ServiceCatalog:
        """Cria um novo serviço no catálogo."""
        service = ServiceCatalog(
            id=uuid4(),
            code=self._generate_service_code(),
            **data.model_dump()
        )
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        logger.info(f"Serviço criado: {service.code}")
        return service

    def get_service(self, service_id: UUID) -> Optional[ServiceCatalog]:
        """Busca serviço por ID."""
        return self.db.query(ServiceCatalog).filter(
            ServiceCatalog.id == service_id,
            ServiceCatalog.ativo.is_(True)
        ).first()

    def get_service_by_code(self, code: str) -> Optional[ServiceCatalog]:
        """Busca serviço por código."""
        return self.db.query(ServiceCatalog).filter(
            ServiceCatalog.code == code,
            ServiceCatalog.ativo.is_(True)
        ).first()

    def list_services(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        service_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ServiceCatalog], int]:
        """Lista serviços com filtros."""
        query = self.db.query(ServiceCatalog).filter(
            ServiceCatalog.ativo.is_(True)
        )

        if category:
            query = query.filter(ServiceCatalog.category == category)
        if service_type:
            query = query.filter(ServiceCatalog.service_type == service_type)
        if status:
            query = query.filter(ServiceCatalog.status == status)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    ServiceCatalog.name.ilike(search_filter),
                    ServiceCatalog.code.ilike(search_filter),
                    ServiceCatalog.description.ilike(search_filter)
                )
            )

        total = query.count()
        services = query.order_by(
            desc(ServiceCatalog.created_at)
        ).offset(skip).limit(limit).all()

        return services, total

    def update_service(
        self, service_id: UUID, data: ServiceCatalogUpdate
    ) -> Optional[ServiceCatalog]:
        """Atualiza um serviço."""
        service = self.get_service(service_id)
        if not service:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)

        service.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(service)
        return service

    def delete_service(self, service_id: UUID) -> bool:
        """Exclui logicamente um serviço."""
        service = self.get_service(service_id)
        if not service:
            return False

        service.ativo = False
        service.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_service_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos serviços."""
        total = self.db.query(func.count(ServiceCatalog.id)).filter(
            ServiceCatalog.ativo.is_(True)
        ).scalar() or 0

        active = self.db.query(func.count(ServiceCatalog.id)).filter(
            ServiceCatalog.ativo.is_(True),
            ServiceCatalog.status == ServiceStatus.ATIVO
        ).scalar() or 0

        by_category = dict(
            self.db.query(
                ServiceCatalog.category,
                func.count(ServiceCatalog.id)
            ).filter(
                ServiceCatalog.ativo.is_(True)
            ).group_by(ServiceCatalog.category).all()
        )

        total_revenue = self.db.query(
            func.sum(ServiceCatalog.total_revenue)
        ).filter(ServiceCatalog.ativo.is_(True)).scalar() or Decimal("0")

        return {
            "total_services": total,
            "active_services": active,
            "by_category": {str(k): v for k, v in by_category.items()},
            "total_revenue": total_revenue
        }

    def _generate_service_code(self) -> str:
        """Gera código único para serviço."""
        last = self.db.query(ServiceCatalog).order_by(
            desc(ServiceCatalog.created_at)
        ).first()

        if last and last.code:
            try:
                num = int(last.code.split("-")[1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1

        return f"SRV-{num:05d}"

    # ========================================
    # SERVICE ORDER
    # ========================================

    def create_order(self, data: ServiceOrderCreate) -> ServiceOrder:
        """Cria uma nova ordem de serviço."""
        order = ServiceOrder(
            id=uuid4(),
            order_number=self._generate_order_number(),
            **data.model_dump()
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        logger.info(f"Ordem criada: {order.order_number}")
        return order

    def get_order(self, order_id: UUID) -> Optional[ServiceOrder]:
        """Busca ordem por ID."""
        return self.db.query(ServiceOrder).filter(
            ServiceOrder.id == order_id,
            ServiceOrder.ativo.is_(True)
        ).first()

    def get_order_by_number(self, order_number: str) -> Optional[ServiceOrder]:
        """Busca ordem por número."""
        return self.db.query(ServiceOrder).filter(
            ServiceOrder.order_number == order_number,
            ServiceOrder.ativo.is_(True)
        ).first()

    def list_orders(
        self,
        filters: Optional[ServiceOrderFilter] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> Tuple[List[ServiceOrder], int]:
        """Lista ordens com filtros."""
        query = self.db.query(ServiceOrder).filter(
            ServiceOrder.ativo.is_(True)
        )

        if filters:
            if filters.status:
                query = query.filter(ServiceOrder.status == filters.status)
            if filters.priority:
                query = query.filter(ServiceOrder.priority == filters.priority)
            if filters.client_id:
                query = query.filter(ServiceOrder.client_id == filters.client_id)
            if filters.condominium_id:
                query = query.filter(
                    ServiceOrder.condominium_id == filters.condominium_id
                )
            if filters.service_id:
                query = query.filter(ServiceOrder.service_id == filters.service_id)
            if filters.technician_id:
                query = query.filter(
                    ServiceOrder.assigned_technician_id == filters.technician_id
                )
            if filters.scheduled_date_from:
                query = query.filter(
                    ServiceOrder.scheduled_date >= filters.scheduled_date_from
                )
            if filters.scheduled_date_to:
                query = query.filter(
                    ServiceOrder.scheduled_date <= filters.scheduled_date_to
                )
            if filters.search:
                search_filter = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        ServiceOrder.order_number.ilike(search_filter),
                        ServiceOrder.title.ilike(search_filter)
                    )
                )

        total = query.count()

        order_column = getattr(ServiceOrder, order_by, ServiceOrder.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)

        orders = query.offset(skip).limit(limit).all()
        return orders, total

    def update_order(
        self, order_id: UUID, data: ServiceOrderUpdate
    ) -> Optional[ServiceOrder]:
        """Atualiza uma ordem."""
        order = self.get_order(order_id)
        if not order:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        order.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_stats(
        self,
        client_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Retorna estatísticas das ordens."""
        query = self.db.query(ServiceOrder).filter(
            ServiceOrder.ativo.is_(True)
        )

        if client_id:
            query = query.filter(ServiceOrder.client_id == client_id)
        if date_from:
            query = query.filter(ServiceOrder.created_at >= date_from)
        if date_to:
            query = query.filter(ServiceOrder.created_at <= date_to)

        total = query.count()

        by_status = dict(
            query.with_entities(
                ServiceOrder.status,
                func.count(ServiceOrder.id)
            ).group_by(ServiceOrder.status).all()
        )

        by_priority = dict(
            query.with_entities(
                ServiceOrder.priority,
                func.count(ServiceOrder.id)
            ).group_by(ServiceOrder.priority).all()
        )

        overdue = query.filter(
            ServiceOrder.status.notin_([
                OrderStatus.CONCLUIDA, OrderStatus.CANCELADA
            ]),
            ServiceOrder.sla_resolution_deadline < datetime.utcnow()
        ).count()

        avg_rating = query.filter(
            ServiceOrder.rating.isnot(None)
        ).with_entities(
            func.avg(ServiceOrder.rating)
        ).scalar()

        return {
            "total_orders": total,
            "by_status": {str(k): v for k, v in by_status.items()},
            "by_priority": {str(k): v for k, v in by_priority.items()},
            "overdue_count": overdue,
            "avg_rating": float(avg_rating) if avg_rating else None
        }

    def get_overdue_orders(self) -> List[ServiceOrder]:
        """Retorna ordens atrasadas."""
        return self.db.query(ServiceOrder).filter(
            ServiceOrder.ativo.is_(True),
            ServiceOrder.status.notin_([
                OrderStatus.CONCLUIDA, OrderStatus.CANCELADA
            ]),
            ServiceOrder.sla_resolution_deadline < datetime.utcnow()
        ).all()

    def _generate_order_number(self) -> str:
        """Gera número único para ordem."""
        year = datetime.now().year
        prefix = f"OS-{year}-"

        last = self.db.query(ServiceOrder).filter(
            ServiceOrder.order_number.like(f"{prefix}%")
        ).order_by(desc(ServiceOrder.created_at)).first()

        if last:
            try:
                num = int(last.order_number.split("-")[-1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1

        return f"{prefix}{num:06d}"

    # ========================================
    # SERVICE EXECUTION
    # ========================================

    def create_execution(
        self, data: ServiceExecutionCreate
    ) -> ServiceExecution:
        """Cria uma nova execução."""
        order = self.get_order(data.order_id)
        sequence = 1
        if order:
            existing = self.db.query(ServiceExecution).filter(
                ServiceExecution.order_id == data.order_id
            ).count()
            sequence = existing + 1

        execution = ServiceExecution(
            id=uuid4(),
            execution_number=self._generate_execution_number(data.order_id),
            sequence=sequence,
            **data.model_dump()
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def get_execution(self, execution_id: UUID) -> Optional[ServiceExecution]:
        """Busca execução por ID."""
        return self.db.query(ServiceExecution).filter(
            ServiceExecution.id == execution_id,
            ServiceExecution.ativo.is_(True)
        ).first()

    def list_executions_by_order(
        self, order_id: UUID
    ) -> List[ServiceExecution]:
        """Lista execuções de uma ordem."""
        return self.db.query(ServiceExecution).filter(
            ServiceExecution.order_id == order_id,
            ServiceExecution.ativo.is_(True)
        ).order_by(ServiceExecution.sequence).all()

    def update_execution(
        self, execution_id: UUID, data: ServiceExecutionUpdate
    ) -> Optional[ServiceExecution]:
        """Atualiza uma execução."""
        execution = self.get_execution(execution_id)
        if not execution:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(execution, field, value)

        execution.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def _generate_execution_number(self, order_id: UUID) -> str:
        """Gera número da execução."""
        order = self.get_order(order_id)
        if order:
            count = self.db.query(ServiceExecution).filter(
                ServiceExecution.order_id == order_id
            ).count()
            return f"{order.order_number}-E{count + 1:02d}"
        return f"EXE-{uuid4().hex[:8].upper()}"

    # ========================================
    # SERVICE REPORT
    # ========================================

    def create_report(self, data: ServiceReportCreate) -> ServiceReport:
        """Cria um novo relatório."""
        report = ServiceReport(
            id=uuid4(),
            report_number=self._generate_report_number(),
            **data.model_dump()
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report(self, report_id: UUID) -> Optional[ServiceReport]:
        """Busca relatório por ID."""
        return self.db.query(ServiceReport).filter(
            ServiceReport.id == report_id,
            ServiceReport.ativo.is_(True)
        ).first()

    def list_reports_by_order(self, order_id: UUID) -> List[ServiceReport]:
        """Lista relatórios de uma ordem."""
        return self.db.query(ServiceReport).filter(
            ServiceReport.order_id == order_id,
            ServiceReport.ativo.is_(True)
        ).order_by(desc(ServiceReport.created_at)).all()

    def update_report(
        self, report_id: UUID, data: ServiceReportUpdate
    ) -> Optional[ServiceReport]:
        """Atualiza um relatório."""
        report = self.get_report(report_id)
        if not report:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(report, field, value)

        report.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(report)
        return report

    def _generate_report_number(self) -> str:
        """Gera número do relatório."""
        year = datetime.now().year
        prefix = f"REL-{year}-"

        last = self.db.query(ServiceReport).filter(
            ServiceReport.report_number.like(f"{prefix}%")
        ).order_by(desc(ServiceReport.created_at)).first()

        if last:
            try:
                num = int(last.report_number.split("-")[-1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1

        return f"{prefix}{num:06d}"

    # ========================================
    # SLA CONFIG
    # ========================================

    def create_sla(self, data: SLAConfigCreate) -> SLAConfig:
        """Cria uma nova configuração de SLA."""
        sla = SLAConfig(
            id=uuid4(),
            code=self._generate_sla_code(),
            **data.model_dump()
        )
        self.db.add(sla)
        self.db.commit()
        self.db.refresh(sla)
        return sla

    def get_sla(self, sla_id: UUID) -> Optional[SLAConfig]:
        """Busca SLA por ID."""
        return self.db.query(SLAConfig).filter(
            SLAConfig.id == sla_id,
            SLAConfig.ativo.is_(True)
        ).first()

    def get_sla_for_service(
        self,
        service_id: UUID,
        client_id: Optional[UUID] = None
    ) -> Optional[SLAConfig]:
        """Busca SLA para um serviço/cliente."""
        query = self.db.query(SLAConfig).filter(
            SLAConfig.ativo.is_(True),
            SLAConfig.is_active.is_(True)
        )

        if client_id:
            client_sla = query.filter(
                SLAConfig.service_id == service_id,
                SLAConfig.client_id == client_id
            ).first()
            if client_sla:
                return client_sla

        service_sla = query.filter(
            SLAConfig.service_id == service_id,
            SLAConfig.client_id.is_(None)
        ).first()
        if service_sla:
            return service_sla

        return query.filter(
            SLAConfig.is_default.is_(True)
        ).first()

    def list_slas(
        self,
        service_id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[SLAConfig]:
        """Lista configurações de SLA."""
        query = self.db.query(SLAConfig).filter(
            SLAConfig.ativo.is_(True)
        )

        if service_id:
            query = query.filter(SLAConfig.service_id == service_id)
        if client_id:
            query = query.filter(SLAConfig.client_id == client_id)
        if is_active is not None:
            query = query.filter(SLAConfig.is_active == is_active)

        return query.order_by(desc(SLAConfig.created_at)).all()

    def update_sla(
        self, sla_id: UUID, data: SLAConfigUpdate
    ) -> Optional[SLAConfig]:
        """Atualiza um SLA."""
        sla = self.get_sla(sla_id)
        if not sla:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sla, field, value)

        sla.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(sla)
        return sla

    def _generate_sla_code(self) -> str:
        """Gera código do SLA."""
        last = self.db.query(SLAConfig).order_by(
            desc(SLAConfig.created_at)
        ).first()

        if last and last.code:
            try:
                num = int(last.code.split("-")[1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1

        return f"SLA-{num:04d}"
