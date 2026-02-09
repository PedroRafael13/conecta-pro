"""
Repository PCMSO - Acesso a Dados de Exames Medicos
====================================================

Camada de acesso a dados para entidades do PCMSO.
"""

from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.health_occupational.models.pcmso import (
    ASO,
    ComplementaryExam,
    ExamStatus,
    MedicalExam,
)


class PCMSORepository:
    """Repository para entidades do PCMSO."""

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================================
    # Medical Exam Repository
    # ==========================================================================

    def create_exam(self, exam: MedicalExam) -> MedicalExam:
        """Cria novo exame."""
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_exam_by_id(self, exam_id: UUID) -> MedicalExam | None:
        """Busca exame por ID."""
        return self.db.query(MedicalExam).filter(MedicalExam.id == exam_id).first()

    def get_exams_by_funcionario(
        self,
        funcionario_id: UUID,
        status: str | None = None,
        tipo: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MedicalExam]:
        """Lista exames de um funcionario."""
        query = self.db.query(MedicalExam).filter(MedicalExam.funcionario_id == funcionario_id)

        if status:
            query = query.filter(MedicalExam.status == status)
        if tipo:
            query = query.filter(MedicalExam.tipo_exame == tipo)

        return query.order_by(MedicalExam.data_agendamento.desc()).offset(offset).limit(limit).all()

    def count_exams_by_funcionario(
        self,
        funcionario_id: UUID,
        status: str | None = None,
        tipo: str | None = None,
    ) -> int:
        """Conta exames de um funcionario."""
        query = self.db.query(MedicalExam).filter(MedicalExam.funcionario_id == funcionario_id)

        if status:
            query = query.filter(MedicalExam.status == status)
        if tipo:
            query = query.filter(MedicalExam.tipo_exame == tipo)

        return query.count()

    def get_pending_exams(self, days_ahead: int = 30) -> list[MedicalExam]:
        """Lista exames pendentes."""
        limit_date = date.today() + timedelta(days=days_ahead)

        return (
            self.db.query(MedicalExam)
            .filter(
                MedicalExam.status.in_([ExamStatus.AGENDADO.value, ExamStatus.CONFIRMADO.value]),
                MedicalExam.data_agendamento <= limit_date,
            )
            .order_by(MedicalExam.data_agendamento)
            .all()
        )

    def update_exam(self, exam: MedicalExam) -> MedicalExam:
        """Atualiza exame."""
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def delete_exam(self, exam_id: UUID) -> bool:
        """Remove exame (soft delete nao implementado)."""
        exam = self.get_exam_by_id(exam_id)
        if exam:
            self.db.delete(exam)
            self.db.commit()
            return True
        return False

    # ==========================================================================
    # ASO Repository
    # ==========================================================================

    def create_aso(self, aso: ASO) -> ASO:
        """Cria novo ASO."""
        self.db.add(aso)
        self.db.commit()
        self.db.refresh(aso)
        return aso

    def get_aso_by_id(self, aso_id: UUID) -> ASO | None:
        """Busca ASO por ID."""
        return self.db.query(ASO).filter(ASO.id == aso_id).first()

    def get_aso_by_exam(self, exam_id: UUID) -> ASO | None:
        """Busca ASO pelo exame."""
        return self.db.query(ASO).filter(ASO.exame_id == exam_id).first()

    def get_aso_by_numero(self, numero: str) -> ASO | None:
        """Busca ASO pelo numero."""
        return self.db.query(ASO).filter(ASO.numero_aso == numero).first()

    def get_expiring_asos(self, days: int = 30) -> list[ASO]:
        """Lista ASOs a vencer."""
        limit_date = date.today() + timedelta(days=days)

        return (
            self.db.query(ASO)
            .filter(
                ASO.ativo,
                not ASO.cancelado,
                ASO.data_vencimento <= limit_date,
                ASO.data_vencimento >= date.today(),
            )
            .order_by(ASO.data_vencimento)
            .all()
        )

    def get_expired_asos(self) -> list[ASO]:
        """Lista ASOs vencidos."""
        return (
            self.db.query(ASO)
            .filter(
                ASO.ativo,
                not ASO.cancelado,
                ASO.data_vencimento < date.today(),
            )
            .order_by(ASO.data_vencimento)
            .all()
        )

    def update_aso(self, aso: ASO) -> ASO:
        """Atualiza ASO."""
        self.db.commit()
        self.db.refresh(aso)
        return aso

    def count_asos_by_year(self, year: int) -> int:
        """Conta ASOs emitidos no ano."""
        return (
            self.db.query(ASO)
            .filter(
                ASO.data_emissao >= datetime(year, 1, 1),
                ASO.data_emissao < datetime(year + 1, 1, 1),
            )
            .count()
        )

    # ==========================================================================
    # Complementary Exam Repository
    # ==========================================================================

    def create_complementary_exam(self, exam: ComplementaryExam) -> ComplementaryExam:
        """Cria exame complementar."""
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def get_complementary_exams(self, exam_principal_id: UUID) -> list[ComplementaryExam]:
        """Lista exames complementares de um exame principal."""
        return self.db.query(ComplementaryExam).filter(ComplementaryExam.exame_principal_id == exam_principal_id).all()

    def update_complementary_exam(self, exam: ComplementaryExam) -> ComplementaryExam:
        """Atualiza exame complementar."""
        self.db.commit()
        self.db.refresh(exam)
        return exam

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def get_exam_statistics(self, start_date: date, end_date: date) -> dict[str, Any]:
        """Retorna estatisticas de exames em um periodo."""
        total = (
            self.db.query(MedicalExam)
            .filter(
                MedicalExam.data_agendamento >= start_date,
                MedicalExam.data_agendamento <= end_date,
            )
            .count()
        )

        by_type = {}
        for tipo in ["admissional", "periodico", "demissional", "retorno_trabalho", "mudanca_funcao"]:
            by_type[tipo] = (
                self.db.query(MedicalExam)
                .filter(
                    MedicalExam.data_agendamento >= start_date,
                    MedicalExam.data_agendamento <= end_date,
                    MedicalExam.tipo_exame == tipo,
                )
                .count()
            )

        by_status = {}
        for status in ["agendado", "confirmado", "realizado", "cancelado"]:
            by_status[status] = (
                self.db.query(MedicalExam)
                .filter(
                    MedicalExam.data_agendamento >= start_date,
                    MedicalExam.data_agendamento <= end_date,
                    MedicalExam.status == status,
                )
                .count()
            )

        return {
            "total": total,
            "by_type": by_type,
            "by_status": by_status,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }
