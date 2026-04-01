"""Repository de Relatorio Agendado Financeiro."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from modules.financial.bi_dashboard.models.scheduled_report import (
    ReportFormat,
    ReportFrequency,
    ReportStatus,
    ReportType,
    ScheduledReport,
)
from modules.financial.bi_dashboard.schemas.report_schemas import (
    ReportCreate,
    ReportFilters,
    ReportStats,
    ReportUpdate,
)


class ReportRepository:
    """Repository para operacoes de Relatorio Agendado."""

    def __init__(self, db: Session):
        """Inicializa repository."""
        self.db = db

    def create(
        self,
        condominio_id: UUID,
        data: ReportCreate,
        created_by: UUID = None,
    ) -> ScheduledReport:
        """Cria novo relatorio agendado."""
        report = ScheduledReport(
            condominio_id=condominio_id,
            codigo=data.codigo,
            nome=data.nome,
            descricao=data.descricao,
            tipo=data.tipo,
            formato=data.formato,
            frequencia=data.schedule.frequencia,
            hora_execucao=data.schedule.hora_execucao,
            dia_semana=data.schedule.dia_semana,
            dia_mes=data.schedule.dia_mes,
            timezone=data.schedule.timezone,
            periodo_tipo=data.period.periodo_tipo,
            periodo_dias=data.period.periodo_dias,
            data_inicio=data.period.data_inicio,
            data_fim=data.period.data_fim,
            valido_de=data.valido_de,
            valido_ate=data.valido_ate,
            metodo_entrega=data.delivery.metodo,
            destinatarios_email=data.delivery.destinatarios_email,
            webhook_url=data.delivery.webhook_url,
            storage_path=data.delivery.storage_path,
            notificar_sucesso=data.delivery.notificar_sucesso,
            notificar_erro=data.delivery.notificar_erro,
            notificar_email=data.delivery.notificar_email,
            template_id=data.template.template_id,
            logo_url=data.template.logo_url,
            header_text=data.template.header_text,
            footer_text=data.template.footer_text,
            show_charts=data.template.show_charts,
            show_summary=data.template.show_summary,
            paper_size=data.template.paper_size,
            orientation=data.template.orientation,
            filtros=data.filtros,
            ordenacao=data.ordenacao,
            agrupamento=data.agrupamento,
            custom_query=data.custom_query,
            tags=data.tags,
            created_by=created_by,
        )

        # Calcula proxima execucao
        report.proxima_execucao_at = report.calculate_next_execution()

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_id(
        self,
        report_id: UUID,
        condominio_id: UUID = None,
    ) -> ScheduledReport | None:
        """Busca relatorio por ID."""
        query = self.db.query(ScheduledReport).filter(ScheduledReport.id == report_id)
        if condominio_id:
            query = query.filter(ScheduledReport.condominio_id == condominio_id)
        return query.first()

    def get_by_codigo(
        self,
        codigo: str,
        condominio_id: UUID,
    ) -> ScheduledReport | None:
        """Busca relatorio por codigo."""
        return (
            self.db.query(ScheduledReport)
            .filter(
                ScheduledReport.codigo == codigo,
                ScheduledReport.condominio_id == condominio_id,
            )
            .first()
        )

    def list_all(
        self,
        condominio_id: UUID,
        filters: ReportFilters = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ScheduledReport], int]:
        """Lista relatorios com filtros."""
        query = self.db.query(ScheduledReport).filter(ScheduledReport.condominio_id == condominio_id)

        if filters:
            if filters.tipo:
                query = query.filter(ScheduledReport.tipo == filters.tipo)
            if filters.formato:
                query = query.filter(ScheduledReport.formato == filters.formato)
            if filters.status:
                query = query.filter(ScheduledReport.status == filters.status)
            if filters.frequencia:
                query = query.filter(ScheduledReport.frequencia == filters.frequencia)
            if filters.metodo_entrega:
                query = query.filter(ScheduledReport.metodo_entrega == filters.metodo_entrega)
            if filters.is_due:
                now = datetime.utcnow()
                query = query.filter(
                    ScheduledReport.status == ReportStatus.ACTIVE,
                    or_(
                        ScheduledReport.proxima_execucao_at.is_(None),
                        ScheduledReport.proxima_execucao_at <= now,
                    ),
                )
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        ScheduledReport.nome.ilike(search_term),
                        ScheduledReport.codigo.ilike(search_term),
                    )
                )
            if filters.created_after:
                query = query.filter(ScheduledReport.created_at >= filters.created_after)
            if filters.created_before:
                query = query.filter(ScheduledReport.created_at <= filters.created_before)

        total = query.count()
        items = query.order_by(ScheduledReport.proxima_execucao_at).offset(skip).limit(limit).all()
        return items, total

    def update(
        self,
        report: ScheduledReport,
        data: ReportUpdate,
        updated_by: UUID = None,
    ) -> ScheduledReport:
        """Atualiza relatorio."""
        update_data = data.model_dump(exclude_unset=True)

        # Processa schedule separadamente
        if "schedule" in update_data and update_data["schedule"]:
            sched = update_data.pop("schedule")
            for field, value in sched.items():
                if hasattr(report, field):
                    setattr(report, field, value)

        # Processa period separadamente
        if "period" in update_data and update_data["period"]:
            period = update_data.pop("period")
            for field, value in period.items():
                if hasattr(report, field):
                    setattr(report, field, value)

        # Processa delivery separadamente
        if "delivery" in update_data and update_data["delivery"]:
            delivery = update_data.pop("delivery")
            if "metodo" in delivery:
                report.metodo_entrega = delivery["metodo"]
            for field, value in delivery.items():
                if field != "metodo" and hasattr(report, field):
                    setattr(report, field, value)

        # Processa template separadamente
        if "template" in update_data and update_data["template"]:
            template = update_data.pop("template")
            for field, value in template.items():
                if hasattr(report, field):
                    setattr(report, field, value)

        # Atualiza campos restantes
        for field, value in update_data.items():
            if hasattr(report, field):
                setattr(report, field, value)

        report.updated_by = updated_by

        # Recalcula proxima execucao se necessario
        if report.status == ReportStatus.ACTIVE:
            report.proxima_execucao_at = report.calculate_next_execution()

        self.db.commit()
        self.db.refresh(report)
        return report

    def delete(self, report: ScheduledReport) -> bool:
        """Deleta relatorio."""
        self.db.delete(report)
        self.db.commit()
        return True

    def get_due_reports(
        self,
        condominio_id: UUID = None,
    ) -> list[ScheduledReport]:
        """Lista relatorios prontos para execucao."""
        now = datetime.utcnow()
        query = self.db.query(ScheduledReport).filter(
            ScheduledReport.status == ReportStatus.ACTIVE,
            or_(
                ScheduledReport.proxima_execucao_at.is_(None),
                ScheduledReport.proxima_execucao_at <= now,
            ),
        )
        if condominio_id:
            query = query.filter(ScheduledReport.condominio_id == condominio_id)
        return query.all()

    def mark_executed(
        self,
        report: ScheduledReport,
        success: bool,
        error: str = None,
        file_url: str = None,
        file_size: int = None,
        file_hash: str = None,
    ) -> ScheduledReport:
        """Marca relatorio como executado."""
        report.mark_executed(success, error)

        if success and file_url:
            report.ultimo_arquivo_url = file_url
            report.ultimo_arquivo_tamanho = file_size
            report.ultimo_arquivo_hash = file_hash

        self.db.commit()
        self.db.refresh(report)
        return report

    def pause(self, report: ScheduledReport) -> ScheduledReport:
        """Pausa agendamento."""
        report.pause()
        self.db.commit()
        self.db.refresh(report)
        return report

    def resume(self, report: ScheduledReport) -> ScheduledReport:
        """Retoma agendamento."""
        report.resume()
        self.db.commit()
        self.db.refresh(report)
        return report

    def cancel(self, report: ScheduledReport) -> ScheduledReport:
        """Cancela agendamento."""
        report.cancel()
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_stats(self, condominio_id: UUID) -> ReportStats:
        """Retorna estatisticas de relatorios."""
        base_query = self.db.query(ScheduledReport).filter(ScheduledReport.condominio_id == condominio_id)

        total = base_query.count()
        active = base_query.filter(ScheduledReport.status == ReportStatus.ACTIVE).count()
        paused = base_query.filter(ScheduledReport.status == ReportStatus.PAUSED).count()
        expired = base_query.filter(ScheduledReport.status == ReportStatus.EXPIRED).count()

        now = datetime.utcnow()
        due_today = base_query.filter(
            ScheduledReport.status == ReportStatus.ACTIVE,
            ScheduledReport.proxima_execucao_at <= now,
        ).count()

        total_executions = base_query.with_entities(func.sum(ScheduledReport.total_execucoes)).scalar() or 0
        total_errors = base_query.with_entities(func.sum(ScheduledReport.total_erros)).scalar() or 0

        success_rate = Decimal("100")
        if total_executions > 0:
            success_rate = Decimal(str(((total_executions - total_errors) / total_executions) * 100))

        by_type = {}
        for tipo in ReportType:
            count = base_query.filter(ScheduledReport.tipo == tipo).count()
            if count > 0:
                by_type[tipo.value] = count

        by_format = {}
        for fmt in ReportFormat:
            count = base_query.filter(ScheduledReport.formato == fmt).count()
            if count > 0:
                by_format[fmt.value] = count

        by_frequency = {}
        for freq in ReportFrequency:
            count = base_query.filter(ScheduledReport.frequencia == freq).count()
            if count > 0:
                by_frequency[freq.value] = count

        return ReportStats(
            total=total,
            active=active,
            paused=paused,
            expired=expired,
            due_today=due_today,
            total_executions=int(total_executions),
            total_errors=int(total_errors),
            success_rate=success_rate,
            by_type=by_type,
            by_format=by_format,
            by_frequency=by_frequency,
        )

    def get_by_type(
        self,
        condominio_id: UUID,
        tipo: ReportType,
    ) -> list[ScheduledReport]:
        """Lista relatorios por tipo."""
        return (
            self.db.query(ScheduledReport)
            .filter(
                ScheduledReport.condominio_id == condominio_id,
                ScheduledReport.tipo == tipo,
                ScheduledReport.status == ReportStatus.ACTIVE,
            )
            .all()
        )

    def get_expiring_soon(
        self,
        condominio_id: UUID,
        days: int = 7,
    ) -> list[ScheduledReport]:
        """Lista relatorios expirando em breve."""
        cutoff = date.today() + timedelta(days=days)
        return (
            self.db.query(ScheduledReport)
            .filter(
                ScheduledReport.condominio_id == condominio_id,
                ScheduledReport.status == ReportStatus.ACTIVE,
                ScheduledReport.valido_ate.isnot(None),
                ScheduledReport.valido_ate <= cutoff,
            )
            .all()
        )
