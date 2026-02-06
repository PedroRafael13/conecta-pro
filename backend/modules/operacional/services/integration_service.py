"""
Serviço de Integração Diaristas-Operacional.

Fornece funcionalidades para:
- Alocar diaristas a postos de trabalho
- Vincular schedules de diaristas a shifts
- Dashboard unificado de ocupação
- Métricas consolidadas
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
import logging

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from modules.operacional.models import (
    Post,
    PostStatus,
    Scale,
    ScaleStatus,
    Shift,
    ShiftStatus,
    Allocation,
    AllocationStatus,
)
from modules.operacional.diaristas.models import (
    Diarist,
    DiaristStatus,
    DiaristAssignment,
    DiaristSchedule,
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """Serviço de integração entre Diaristas e módulo Operacional."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # ALOCAÇÃO DE DIARISTAS A POSTOS
    # =========================================================================

    def alocar_diarista_posto(
        self,
        diarista_id: UUID,
        post_id: UUID,
        data_inicio: date,
        data_fim: Optional[date] = None,
        shift_id: Optional[UUID] = None,
        cliente_id: Optional[UUID] = None,
        contrato_id: Optional[UUID] = None,
        observacoes: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> DiaristAssignment:
        """
        Aloca um diarista a um posto de trabalho.

        Args:
            diarista_id: ID do diarista
            post_id: ID do posto
            data_inicio: Data de início da alocação
            data_fim: Data de fim (opcional, para alocações temporárias)
            shift_id: ID do turno específico (opcional)
            cliente_id: ID do cliente do posto
            contrato_id: ID do contrato associado
            observacoes: Observações adicionais
            created_by: ID do usuário que criou

        Returns:
            DiaristAssignment criado
        """
        # Verificar diarista existe e está ativo
        diarista = self.db.query(Diarist).filter(
            Diarist.id == diarista_id,
            Diarist.is_active == True
        ).first()

        if not diarista:
            raise ValueError(f"Diarista {diarista_id} não encontrado ou inativo")

        if diarista.status not in [DiaristStatus.ACTIVE, DiaristStatus.ON_ASSIGNMENT]:
            raise ValueError(f"Diarista não está disponível. Status: {diarista.status}")

        # Verificar posto existe e está ativo
        post = self.db.query(Post).filter(
            Post.id == post_id,
            Post.status == PostStatus.ACTIVE
        ).first()

        if not post:
            raise ValueError(f"Posto {post_id} não encontrado ou inativo")

        # Verificar se não há conflito de alocação
        conflito = self.db.query(DiaristAssignment).filter(
            DiaristAssignment.diarist_id == diarista_id,
            DiaristAssignment.status == "active",
            or_(
                and_(
                    DiaristAssignment.start_date <= data_inicio,
                    or_(
                        DiaristAssignment.end_date.is_(None),
                        DiaristAssignment.end_date >= data_inicio
                    )
                ),
                and_(
                    DiaristAssignment.start_date <= data_fim,
                    or_(
                        DiaristAssignment.end_date.is_(None),
                        DiaristAssignment.end_date >= data_fim
                    )
                ) if data_fim else False
            )
        ).first()

        if conflito:
            raise ValueError(
                f"Diarista já possui alocação ativa no período: "
                f"Assignment {conflito.id}"
            )

        # Criar assignment
        assignment = DiaristAssignment(
            diarist_id=diarista_id,
            post_id=post_id,
            shift_id=shift_id,
            cliente_id=cliente_id or post.client_id if hasattr(post, 'client_id') else None,
            contrato_id=contrato_id,
            client_name=post.name,
            location=post.address if hasattr(post, 'address') else None,
            start_date=data_inicio,
            end_date=data_fim,
            status="active",
            notes=observacoes,
            created_by=created_by,
        )

        self.db.add(assignment)

        # Atualizar status do diarista
        diarista.status = DiaristStatus.ON_ASSIGNMENT

        self.db.commit()
        self.db.refresh(assignment)

        logger.info(
            f"Diarista {diarista_id} alocado ao posto {post_id} "
            f"de {data_inicio} até {data_fim or 'indefinido'}"
        )

        return assignment

    def desalocar_diarista_posto(
        self,
        assignment_id: UUID,
        motivo: Optional[str] = None,
        updated_by: Optional[UUID] = None,
    ) -> DiaristAssignment:
        """
        Remove alocação de diarista de um posto.

        Args:
            assignment_id: ID da alocação
            motivo: Motivo da desalocação
            updated_by: ID do usuário que atualizou

        Returns:
            DiaristAssignment atualizado
        """
        assignment = self.db.query(DiaristAssignment).filter(
            DiaristAssignment.id == assignment_id
        ).first()

        if not assignment:
            raise ValueError(f"Assignment {assignment_id} não encontrado")

        assignment.status = "completed"
        assignment.end_date = date.today()
        if motivo:
            assignment.notes = (assignment.notes or "") + f"\nDesalocação: {motivo}"

        # Verificar se diarista tem outras alocações ativas
        outras_alocacoes = self.db.query(DiaristAssignment).filter(
            DiaristAssignment.diarist_id == assignment.diarist_id,
            DiaristAssignment.id != assignment_id,
            DiaristAssignment.status == "active"
        ).count()

        if outras_alocacoes == 0:
            # Voltar status do diarista para ativo
            diarista = self.db.query(Diarist).filter(
                Diarist.id == assignment.diarist_id
            ).first()
            if diarista:
                diarista.status = DiaristStatus.ACTIVE

        self.db.commit()
        self.db.refresh(assignment)

        logger.info(f"Assignment {assignment_id} finalizado")

        return assignment

    # =========================================================================
    # DASHBOARD UNIFICADO
    # =========================================================================

    def get_dashboard_unificado(
        self,
        data_referencia: Optional[date] = None,
        cliente_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Retorna dashboard unificado com métricas de operacional e diaristas.

        Args:
            data_referencia: Data de referência (default: hoje)
            cliente_id: Filtrar por cliente específico

        Returns:
            Dict com métricas consolidadas
        """
        data_ref = data_referencia or date.today()

        # Métricas de Postos
        postos_query = self.db.query(Post)
        if cliente_id:
            postos_query = postos_query.filter(Post.client_id == cliente_id)

        total_postos = postos_query.count()
        postos_ativos = postos_query.filter(Post.status == PostStatus.ACTIVE).count()
        postos_inativos = postos_query.filter(Post.status == PostStatus.INACTIVE).count()

        # Métricas de Escalas
        escalas_query = self.db.query(Scale).filter(
            Scale.start_date <= data_ref,
            Scale.end_date >= data_ref
        )

        escalas_ativas = escalas_query.filter(Scale.status == ScaleStatus.ACTIVE).count()
        escalas_em_execucao = escalas_query.filter(Scale.status == ScaleStatus.IN_PROGRESS).count()

        # Métricas de Turnos do dia
        turnos_hoje = self.db.query(Shift).filter(
            func.date(Shift.start_time) == data_ref
        ).count()

        turnos_em_andamento = self.db.query(Shift).filter(
            func.date(Shift.start_time) == data_ref,
            Shift.status == ShiftStatus.IN_PROGRESS
        ).count()

        # Métricas de Alocações (funcionários fixos)
        alocacoes_ativas = self.db.query(Allocation).filter(
            Allocation.status == AllocationStatus.ACTIVE
        ).count()

        # Métricas de Diaristas
        total_diaristas = self.db.query(Diarist).filter(
            Diarist.is_active == True
        ).count()

        diaristas_ativos = self.db.query(Diarist).filter(
            Diarist.is_active == True,
            Diarist.status == DiaristStatus.ACTIVE
        ).count()

        diaristas_em_servico = self.db.query(Diarist).filter(
            Diarist.is_active == True,
            Diarist.status == DiaristStatus.ON_ASSIGNMENT
        ).count()

        diaristas_suspensos = self.db.query(Diarist).filter(
            Diarist.is_active == True,
            Diarist.status == DiaristStatus.SUSPENDED
        ).count()

        # Assignments de diaristas do dia
        assignments_hoje = self.db.query(DiaristAssignment).filter(
            DiaristAssignment.status == "active",
            DiaristAssignment.start_date <= data_ref,
            or_(
                DiaristAssignment.end_date.is_(None),
                DiaristAssignment.end_date >= data_ref
            )
        ).count()

        # Schedules de diaristas do dia
        schedules_hoje = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.date == data_ref
        ).count()

        schedules_confirmados = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.date == data_ref,
            DiaristSchedule.status == "confirmed"
        ).count()

        schedules_checkin = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.date == data_ref,
            DiaristSchedule.actual_check_in.isnot(None)
        ).count()

        # Calcular taxa de ocupação
        capacidade_postos = postos_ativos * 3  # Assumindo 3 turnos por posto
        ocupacao_funcionarios = alocacoes_ativas
        ocupacao_diaristas = assignments_hoje
        ocupacao_total = ocupacao_funcionarios + ocupacao_diaristas
        taxa_ocupacao = (ocupacao_total / capacidade_postos * 100) if capacidade_postos > 0 else 0

        return {
            "data_referencia": data_ref.isoformat(),
            "postos": {
                "total": total_postos,
                "ativos": postos_ativos,
                "inativos": postos_inativos,
            },
            "escalas": {
                "ativas": escalas_ativas,
                "em_execucao": escalas_em_execucao,
            },
            "turnos": {
                "hoje": turnos_hoje,
                "em_andamento": turnos_em_andamento,
            },
            "funcionarios": {
                "alocacoes_ativas": alocacoes_ativas,
            },
            "diaristas": {
                "total": total_diaristas,
                "disponiveis": diaristas_ativos,
                "em_servico": diaristas_em_servico,
                "suspensos": diaristas_suspensos,
                "assignments_hoje": assignments_hoje,
                "schedules_hoje": schedules_hoje,
                "schedules_confirmados": schedules_confirmados,
                "com_checkin": schedules_checkin,
            },
            "ocupacao": {
                "capacidade_estimada": capacidade_postos,
                "funcionarios_alocados": ocupacao_funcionarios,
                "diaristas_alocados": ocupacao_diaristas,
                "total_alocado": ocupacao_total,
                "taxa_ocupacao_percentual": round(taxa_ocupacao, 2),
            },
            "alertas": self._gerar_alertas(data_ref),
        }

    def _gerar_alertas(self, data_referencia: date) -> List[Dict[str, Any]]:
        """Gera alertas automáticos baseados na situação atual."""
        alertas = []

        # Alerta: Postos sem cobertura
        postos_sem_cobertura = self.db.query(Post).filter(
            Post.status == PostStatus.ACTIVE
        ).outerjoin(
            Allocation,
            and_(
                Allocation.post_id == Post.id,
                Allocation.status == AllocationStatus.ACTIVE
            )
        ).filter(
            Allocation.id.is_(None)
        ).count()

        if postos_sem_cobertura > 0:
            alertas.append({
                "tipo": "warning",
                "categoria": "cobertura",
                "mensagem": f"{postos_sem_cobertura} posto(s) sem funcionário fixo alocado",
                "acao_sugerida": "Alocar funcionário ou diarista aos postos descobertos",
            })

        # Alerta: Diaristas com check-in atrasado
        agora = datetime.now()
        if agora.hour >= 8:  # Após 8h
            schedules_atrasados = self.db.query(DiaristSchedule).filter(
                DiaristSchedule.date == data_referencia,
                DiaristSchedule.status == "confirmed",
                DiaristSchedule.actual_check_in.is_(None),
                DiaristSchedule.scheduled_start <= agora.time()
            ).count()

            if schedules_atrasados > 0:
                alertas.append({
                    "tipo": "error",
                    "categoria": "presenca",
                    "mensagem": f"{schedules_atrasados} diarista(s) com check-in atrasado",
                    "acao_sugerida": "Entrar em contato para verificar situação",
                })

        # Alerta: Poucos diaristas disponíveis
        diaristas_disponiveis = self.db.query(Diarist).filter(
            Diarist.is_active == True,
            Diarist.status == DiaristStatus.ACTIVE
        ).count()

        if diaristas_disponiveis < 5:
            alertas.append({
                "tipo": "info",
                "categoria": "disponibilidade",
                "mensagem": f"Apenas {diaristas_disponiveis} diarista(s) disponível(is)",
                "acao_sugerida": "Considerar recrutar mais diaristas",
            })

        return alertas

    # =========================================================================
    # MÉTRICAS E RELATÓRIOS
    # =========================================================================

    def get_metricas_periodo(
        self,
        data_inicio: date,
        data_fim: date,
        cliente_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Retorna métricas consolidadas para um período.

        Args:
            data_inicio: Data inicial do período
            data_fim: Data final do período
            cliente_id: Filtrar por cliente (opcional)

        Returns:
            Dict com métricas do período
        """
        # Total de dias no período
        dias_periodo = (data_fim - data_inicio).days + 1

        # Schedules de diaristas no período
        schedules_query = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.date >= data_inicio,
            DiaristSchedule.date <= data_fim
        )

        total_schedules = schedules_query.count()
        schedules_realizados = schedules_query.filter(
            DiaristSchedule.status == "completed"
        ).count()
        schedules_cancelados = schedules_query.filter(
            DiaristSchedule.status == "cancelled"
        ).count()
        schedules_faltas = schedules_query.filter(
            DiaristSchedule.status == "no_show"
        ).count()

        # Horas trabalhadas
        horas_trabalhadas = self.db.query(
            func.sum(DiaristSchedule.hours_worked)
        ).filter(
            DiaristSchedule.date >= data_inicio,
            DiaristSchedule.date <= data_fim,
            DiaristSchedule.status == "completed"
        ).scalar() or Decimal("0")

        # Taxa de comparecimento
        taxa_comparecimento = (
            schedules_realizados / total_schedules * 100
            if total_schedules > 0 else 0
        )

        # Turnos do período (funcionários fixos)
        turnos_periodo = self.db.query(Shift).filter(
            func.date(Shift.start_time) >= data_inicio,
            func.date(Shift.start_time) <= data_fim
        ).count()

        turnos_concluidos = self.db.query(Shift).filter(
            func.date(Shift.start_time) >= data_inicio,
            func.date(Shift.start_time) <= data_fim,
            Shift.status == ShiftStatus.COMPLETED
        ).count()

        return {
            "periodo": {
                "inicio": data_inicio.isoformat(),
                "fim": data_fim.isoformat(),
                "dias": dias_periodo,
            },
            "diaristas": {
                "total_schedules": total_schedules,
                "realizados": schedules_realizados,
                "cancelados": schedules_cancelados,
                "faltas": schedules_faltas,
                "taxa_comparecimento": round(taxa_comparecimento, 2),
                "horas_trabalhadas": float(horas_trabalhadas),
            },
            "funcionarios": {
                "total_turnos": turnos_periodo,
                "turnos_concluidos": turnos_concluidos,
                "taxa_conclusao": round(
                    turnos_concluidos / turnos_periodo * 100 if turnos_periodo > 0 else 0, 2
                ),
            },
            "consolidado": {
                "total_servicos": total_schedules + turnos_periodo,
                "servicos_concluidos": schedules_realizados + turnos_concluidos,
            },
        }

    def get_ocupacao_postos(
        self,
        data_referencia: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retorna ocupação detalhada de cada posto.

        Args:
            data_referencia: Data de referência (default: hoje)

        Returns:
            Lista com status de ocupação de cada posto
        """
        data_ref = data_referencia or date.today()

        postos = self.db.query(Post).filter(
            Post.status == PostStatus.ACTIVE
        ).all()

        resultado = []

        for posto in postos:
            # Buscar alocações de funcionários fixos
            alocacoes = self.db.query(Allocation).filter(
                Allocation.post_id == posto.id,
                Allocation.status == AllocationStatus.ACTIVE
            ).all()

            # Buscar assignments de diaristas
            assignments = self.db.query(DiaristAssignment).filter(
                DiaristAssignment.post_id == posto.id,
                DiaristAssignment.status == "active",
                DiaristAssignment.start_date <= data_ref,
                or_(
                    DiaristAssignment.end_date.is_(None),
                    DiaristAssignment.end_date >= data_ref
                )
            ).all()

            resultado.append({
                "posto_id": str(posto.id),
                "posto_nome": posto.name,
                "posto_tipo": posto.type.value if hasattr(posto.type, 'value') else str(posto.type),
                "funcionarios_alocados": len(alocacoes),
                "diaristas_alocados": len(assignments),
                "total_alocados": len(alocacoes) + len(assignments),
                "status": "coberto" if (alocacoes or assignments) else "descoberto",
                "detalhes": {
                    "funcionarios": [
                        {"allocation_id": str(a.id), "employee_id": str(a.employee_id)}
                        for a in alocacoes
                    ],
                    "diaristas": [
                        {"assignment_id": str(a.id), "diarist_id": str(a.diarist_id)}
                        for a in assignments
                    ],
                },
            })

        return resultado

    def sugerir_diarista_posto(
        self,
        post_id: UUID,
        data: date,
        habilidades_requeridas: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Sugere diaristas disponíveis para um posto.

        Args:
            post_id: ID do posto
            data: Data desejada
            habilidades_requeridas: Lista de habilidades necessárias

        Returns:
            Lista de diaristas sugeridos ordenados por adequação
        """
        # Buscar diaristas disponíveis
        diaristas_disponiveis = self.db.query(Diarist).filter(
            Diarist.is_active == True,
            Diarist.status == DiaristStatus.ACTIVE
        ).all()

        # Filtrar quem não tem conflito na data
        sugestoes = []

        for diarista in diaristas_disponiveis:
            # Verificar se não tem schedule na data
            conflito = self.db.query(DiaristSchedule).filter(
                DiaristSchedule.diarist_id == diarista.id,
                DiaristSchedule.date == data,
                DiaristSchedule.status.in_(["scheduled", "confirmed"])
            ).first()

            if conflito:
                continue

            # Calcular score de adequação
            score = 100
            motivos = []

            # Verificar habilidades
            if habilidades_requeridas and hasattr(diarista, 'skills'):
                skills_diarista = diarista.skills or []
                matches = len(set(habilidades_requeridas) & set(skills_diarista))
                if matches < len(habilidades_requeridas):
                    score -= (len(habilidades_requeridas) - matches) * 10
                    motivos.append(f"Faltam {len(habilidades_requeridas) - matches} habilidades")

            # Verificar avaliação média
            if hasattr(diarista, 'average_rating') and diarista.average_rating:
                if diarista.average_rating >= 4.5:
                    score += 10
                    motivos.append("Avaliação excelente")
                elif diarista.average_rating < 3.5:
                    score -= 20
                    motivos.append("Avaliação baixa")

            sugestoes.append({
                "diarist_id": str(diarista.id),
                "nome": diarista.full_name,
                "score": score,
                "motivos": motivos,
                "avaliacao": float(diarista.average_rating) if hasattr(diarista, 'average_rating') and diarista.average_rating else None,
                "total_servicos": diarista.total_assignments if hasattr(diarista, 'total_assignments') else 0,
            })

        # Ordenar por score
        sugestoes.sort(key=lambda x: x["score"], reverse=True)

        return sugestoes[:10]  # Top 10


# Singleton para uso global
def get_integration_service(db: Session) -> IntegrationService:
    """Factory function para obter instância do serviço."""
    return IntegrationService(db)
