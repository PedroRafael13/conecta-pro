"""Repository de KPI Financeiro."""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from modules.financial.bi_dashboard.models.kpi_definition import (
    AlertLevel,
    FinancialKPI,
    KPICategory,
    KPIFrequency,
    KPIStatus,
)
from modules.financial.bi_dashboard.schemas.kpi_schemas import (
    KPICreate,
    KPIFilters,
    KPISummary,
    KPIUpdate,
)


class KPIRepository:
    """Repository para operacoes de KPI."""

    def __init__(self, db: Session):
        """Inicializa repository."""
        self.db = db

    def create(
        self,
        condominio_id: UUID,
        data: KPICreate,
        created_by: UUID = None,
    ) -> FinancialKPI:
        """Cria novo KPI."""
        kpi = FinancialKPI(
            condominio_id=condominio_id,
            codigo=data.codigo,
            nome=data.nome,
            nome_curto=data.nome_curto,
            descricao=data.descricao,
            categoria=data.categoria,
            frequencia=data.frequencia,
            formula=data.formula,
            formula_descricao=data.formula_descricao,
            variaveis=data.variaveis,
            data_sources=data.data_sources,
            meta_valor=data.meta.valor,
            meta_minimo=data.meta.minimo,
            meta_maximo=data.meta.maximo,
            threshold_warning_min=data.thresholds.warning_min,
            threshold_warning_max=data.thresholds.warning_max,
            threshold_critical_min=data.thresholds.critical_min,
            threshold_critical_max=data.thresholds.critical_max,
            alert_enabled=data.alert_enabled,
            unidade=data.formatting.unidade,
            formato=data.formatting.formato,
            casas_decimais=data.formatting.casas_decimais,
            is_percentage=data.formatting.is_percentage,
            is_inverted=data.formatting.is_inverted,
            icon=data.icon,
            color=data.color,
            show_in_summary=data.show_in_summary,
            order=data.order,
            benchmark_valor=data.benchmark_valor,
            benchmark_fonte=data.benchmark_fonte,
            historico_dias=data.historico_dias,
            tags=data.tags,
            created_by=created_by,
        )
        self.db.add(kpi)
        self.db.commit()
        self.db.refresh(kpi)
        return kpi

    def get_by_id(
        self,
        kpi_id: UUID,
        condominio_id: UUID = None,
    ) -> FinancialKPI | None:
        """Busca KPI por ID."""
        query = self.db.query(FinancialKPI).filter(FinancialKPI.id == kpi_id)
        if condominio_id:
            query = query.filter(FinancialKPI.condominio_id == condominio_id)
        return query.first()

    def get_by_codigo(
        self,
        codigo: str,
        condominio_id: UUID = None,
    ) -> FinancialKPI | None:
        """Busca KPI por codigo."""
        query = self.db.query(FinancialKPI).filter(FinancialKPI.codigo == codigo)
        if condominio_id:
            query = query.filter(FinancialKPI.condominio_id == condominio_id)
        return query.first()

    def list_all(
        self,
        condominio_id: UUID,
        filters: KPIFilters = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FinancialKPI], int]:
        """Lista KPIs com filtros."""
        query = self.db.query(FinancialKPI).filter(FinancialKPI.condominio_id == condominio_id)

        if filters:
            if filters.categoria:
                query = query.filter(FinancialKPI.categoria == filters.categoria)
            if filters.status:
                query = query.filter(FinancialKPI.status == filters.status)
            if filters.frequencia:
                query = query.filter(FinancialKPI.frequencia == filters.frequencia)
            if filters.alert_level:
                query = query.filter(FinancialKPI.alert_level == filters.alert_level)
            if filters.show_in_summary is not None:
                query = query.filter(FinancialKPI.show_in_summary == filters.show_in_summary)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        FinancialKPI.nome.ilike(search_term),
                        FinancialKPI.codigo.ilike(search_term),
                        FinancialKPI.descricao.ilike(search_term),
                    )
                )

        total = query.count()
        items = query.order_by(FinancialKPI.order).offset(skip).limit(limit).all()
        return items, total

    def update(
        self,
        kpi: FinancialKPI,
        data: KPIUpdate,
        updated_by: UUID = None,
    ) -> FinancialKPI:
        """Atualiza KPI."""
        update_data = data.model_dump(exclude_unset=True)

        # Processa meta separadamente
        if "meta" in update_data and update_data["meta"]:
            meta = update_data.pop("meta")
            if "valor" in meta:
                kpi.meta_valor = meta["valor"]
            if "minimo" in meta:
                kpi.meta_minimo = meta["minimo"]
            if "maximo" in meta:
                kpi.meta_maximo = meta["maximo"]

        # Processa thresholds separadamente
        if "thresholds" in update_data and update_data["thresholds"]:
            th = update_data.pop("thresholds")
            if "warning_min" in th:
                kpi.threshold_warning_min = th["warning_min"]
            if "warning_max" in th:
                kpi.threshold_warning_max = th["warning_max"]
            if "critical_min" in th:
                kpi.threshold_critical_min = th["critical_min"]
            if "critical_max" in th:
                kpi.threshold_critical_max = th["critical_max"]

        # Processa formatting separadamente
        if "formatting" in update_data and update_data["formatting"]:
            fmt = update_data.pop("formatting")
            for field, value in fmt.items():
                if hasattr(kpi, field):
                    setattr(kpi, field, value)

        # Atualiza campos restantes
        for field, value in update_data.items():
            if hasattr(kpi, field):
                setattr(kpi, field, value)

        kpi.updated_by = updated_by
        self.db.commit()
        self.db.refresh(kpi)
        return kpi

    def delete(self, kpi: FinancialKPI) -> bool:
        """Deleta KPI."""
        self.db.delete(kpi)
        self.db.commit()
        return True

    def update_value(
        self,
        kpi: FinancialKPI,
        new_value: Decimal,
        save_history: bool = True,
    ) -> FinancialKPI:
        """Atualiza valor do KPI."""
        kpi.update_value(new_value)
        if save_history:
            kpi.add_to_history(new_value)
        self.db.commit()
        self.db.refresh(kpi)
        return kpi

    def get_summary(self, condominio_id: UUID) -> list[FinancialKPI]:
        """Lista KPIs para resumo."""
        return (
            self.db.query(FinancialKPI)
            .filter(
                FinancialKPI.condominio_id == condominio_id,
                FinancialKPI.status == KPIStatus.ACTIVE,
                FinancialKPI.show_in_summary,
            )
            .order_by(FinancialKPI.order)
            .all()
        )

    def get_by_category(
        self,
        condominio_id: UUID,
        categoria: KPICategory,
    ) -> list[FinancialKPI]:
        """Lista KPIs por categoria."""
        return (
            self.db.query(FinancialKPI)
            .filter(
                FinancialKPI.condominio_id == condominio_id,
                FinancialKPI.categoria == categoria,
                FinancialKPI.status == KPIStatus.ACTIVE,
            )
            .order_by(FinancialKPI.order)
            .all()
        )

    def get_alerts(
        self,
        condominio_id: UUID,
        min_level: AlertLevel = AlertLevel.WARNING,
    ) -> list[FinancialKPI]:
        """Lista KPIs em alerta."""
        levels = [AlertLevel.WARNING, AlertLevel.CRITICAL]
        if min_level == AlertLevel.CRITICAL:
            levels = [AlertLevel.CRITICAL]

        return (
            self.db.query(FinancialKPI)
            .filter(
                FinancialKPI.condominio_id == condominio_id,
                FinancialKPI.status == KPIStatus.ACTIVE,
                FinancialKPI.alert_enabled,
                FinancialKPI.alert_level.in_(levels),
            )
            .all()
        )

    def get_needing_calculation(
        self,
        condominio_id: UUID,
    ) -> list[FinancialKPI]:
        """Lista KPIs que precisam recalculo."""
        now = datetime.utcnow()
        kpis = []

        for kpi in (
            self.db.query(FinancialKPI)
            .filter(
                FinancialKPI.condominio_id == condominio_id,
                FinancialKPI.status == KPIStatus.ACTIVE,
            )
            .all()
        ):
            if not kpi.ultimo_calculo_at:
                kpis.append(kpi)
                continue

            # Verifica frequencia
            if kpi.frequencia == KPIFrequency.REAL_TIME:
                if (now - kpi.ultimo_calculo_at).total_seconds() > 60:
                    kpis.append(kpi)
            elif kpi.frequencia == KPIFrequency.HOURLY:
                if (now - kpi.ultimo_calculo_at).total_seconds() > 3600:
                    kpis.append(kpi)
            elif kpi.frequencia == KPIFrequency.DAILY:
                if (now - kpi.ultimo_calculo_at).days >= 1:
                    kpis.append(kpi)

        return kpis

    def get_stats(self, condominio_id: UUID) -> KPISummary:
        """Retorna estatisticas de KPIs."""
        base_query = self.db.query(FinancialKPI).filter(FinancialKPI.condominio_id == condominio_id)

        total = base_query.count()
        active = base_query.filter(FinancialKPI.status == KPIStatus.ACTIVE).count()
        on_target = base_query.filter(
            FinancialKPI.status == KPIStatus.ACTIVE,
            FinancialKPI.meta_atingida,
        ).count()
        warning = base_query.filter(FinancialKPI.alert_level == AlertLevel.WARNING).count()
        critical = base_query.filter(FinancialKPI.alert_level == AlertLevel.CRITICAL).count()

        by_category = {}
        for cat in KPICategory:
            count = base_query.filter(FinancialKPI.categoria == cat).count()
            if count > 0:
                by_category[cat.value] = count

        # Top performers (maior progresso para meta)
        top_performers = []
        for kpi in base_query.filter(
            FinancialKPI.status == KPIStatus.ACTIVE,
            FinancialKPI.meta_valor.isnot(None),
        ).all():
            if kpi.progress_to_target > 0:
                top_performers.append(
                    {
                        "id": str(kpi.id),
                        "codigo": kpi.codigo,
                        "nome": kpi.nome,
                        "progress": float(kpi.progress_to_target),
                    }
                )
        top_performers.sort(key=lambda x: x["progress"], reverse=True)

        # Needs attention (em alerta)
        needs_attention = []
        for kpi in base_query.filter(FinancialKPI.alert_level.in_([AlertLevel.WARNING, AlertLevel.CRITICAL])).all():
            needs_attention.append(
                {
                    "id": str(kpi.id),
                    "codigo": kpi.codigo,
                    "nome": kpi.nome,
                    "alert_level": kpi.alert_level.value,
                    "alert_message": kpi.alert_message,
                }
            )

        return KPISummary(
            total=total,
            active=active,
            on_target=on_target,
            warning=warning,
            critical=critical,
            by_category=by_category,
            top_performers=top_performers[:5],
            needs_attention=needs_attention,
        )

    def get_history(
        self,
        kpi: FinancialKPI,
        days: int = 30,
    ) -> list[dict]:
        """Retorna historico de valores."""
        if not kpi.historico_valores:
            return []

        cutoff = datetime.utcnow() - timedelta(days=days)
        history = []
        for entry in kpi.historico_valores:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date >= cutoff:
                history.append(entry)

        return history
