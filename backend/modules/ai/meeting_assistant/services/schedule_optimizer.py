"""
Schedule Optimizer Service - Sprint 49.

Serviço de otimização de agendamento de reuniões.
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional, Tuple
import uuid

from modules.ai.meeting_assistant.models import Meeting, MeetingParticipant, MeetingStatusEnum
from modules.ai.meeting_assistant.schemas import TimeSlot, ScheduleSuggestionRequest


class ScheduleOptimizer:
    """Serviço de otimização de agendamento."""

    def __init__(self):
        self.business_hours_start = time(8, 0)
        self.business_hours_end = time(18, 0)
        self.lunch_start = time(12, 0)
        self.lunch_end = time(13, 0)
        self.min_break_minutes = 15  # Intervalo mínimo entre reuniões
        self.preferred_times = {
            "morning": (time(9, 0), time(11, 0)),
            "afternoon": (time(14, 0), time(17, 0))
        }

    def find_optimal_slots(
        self,
        request: ScheduleSuggestionRequest,
        existing_meetings: List[Meeting]
    ) -> List[TimeSlot]:
        """
        Encontra slots ótimos para agendamento.

        Args:
            request: Request com parâmetros de busca
            existing_meetings: Reuniões existentes dos participantes

        Returns:
            Lista de TimeSlots ordenados por score
        """
        # Define período de busca
        start_date = request.preferred_start_date or datetime.utcnow()
        end_date = request.preferred_end_date or (start_date + timedelta(days=14))

        # Gera slots candidatos
        candidate_slots = self._generate_candidate_slots(
            start_date=start_date,
            end_date=end_date,
            duration_minutes=request.duration_minutes,
            preferred_times=request.preferred_times,
            avoid_times=request.avoid_times
        )

        # Avalia cada slot
        scored_slots = []
        for slot in candidate_slots:
            score, conflicts = self._evaluate_slot(
                slot=slot,
                existing_meetings=existing_meetings,
                participant_ids=request.participant_ids,
                meeting_type=request.meeting_type,
                priority=request.priority
            )

            if score > 0:  # Slot viável
                scored_slots.append(TimeSlot(
                    start=slot[0],
                    end=slot[1],
                    score=score,
                    reason=self._get_score_reason(score),
                    conflicts=conflicts
                ))

        # Ordena por score e retorna top N
        scored_slots.sort(key=lambda x: x.score, reverse=True)
        return scored_slots[:request.max_suggestions]

    def _generate_candidate_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int,
        preferred_times: List[str] = None,
        avoid_times: List[str] = None
    ) -> List[Tuple[datetime, datetime]]:
        """Gera slots candidatos."""
        slots = []
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        while current_date <= end_date:
            # Pula fins de semana
            if current_date.weekday() < 5:
                # Gera slots em intervalos de 30 minutos
                slot_time = datetime.combine(current_date.date(), self.business_hours_start)

                while slot_time.time() < self.business_hours_end:
                    slot_end = slot_time + timedelta(minutes=duration_minutes)

                    # Verifica se não passa do horário comercial
                    if slot_end.time() <= self.business_hours_end:
                        # Verifica se não é horário de almoço
                        if not self._is_lunch_time(slot_time, slot_end):
                            # Verifica horários a evitar
                            if not self._should_avoid(slot_time, slot_end, avoid_times):
                                slots.append((slot_time, slot_end))

                    slot_time += timedelta(minutes=30)

            current_date += timedelta(days=1)

        return slots

    def _evaluate_slot(
        self,
        slot: Tuple[datetime, datetime],
        existing_meetings: List[Meeting],
        participant_ids: List[uuid.UUID],
        meeting_type: str,
        priority: int
    ) -> Tuple[float, List[str]]:
        """
        Avalia um slot e retorna score e conflitos.

        Returns:
            Tuple[score, conflicts]
        """
        score = 100.0
        conflicts = []
        slot_start, slot_end = slot

        # Verifica conflitos com reuniões existentes
        for meeting in existing_meetings:
            if self._has_overlap(slot_start, slot_end, meeting.scheduled_start, meeting.scheduled_end):
                # Verifica se algum participante está nesta reunião
                meeting_participant_ids = {p.user_id for p in meeting.participants}
                conflicting_participants = set(participant_ids) & meeting_participant_ids

                if conflicting_participants:
                    if meeting.status in [MeetingStatusEnum.CONFIRMED, MeetingStatusEnum.IN_PROGRESS]:
                        score -= 50  # Conflito grave
                        conflicts.append(f"Conflito com '{meeting.title}'")
                    elif meeting.status == MeetingStatusEnum.SCHEDULED:
                        score -= 25  # Conflito moderado
                        conflicts.append(f"Possível conflito com '{meeting.title}'")

        # Bonus para horários preferenciais
        if self._is_preferred_time(slot_start.time()):
            score += 10

        # Bonus para início da manhã ou tarde
        if slot_start.time() in [time(9, 0), time(14, 0)]:
            score += 5

        # Penalidade para horários muito cedo ou tarde
        if slot_start.time() < time(9, 0) or slot_end.time() > time(17, 0):
            score -= 10

        # Bonus por prioridade
        if priority > 70:
            score += 5

        # Penalidade para sexta-feira à tarde
        if slot_start.weekday() == 4 and slot_start.time() >= time(15, 0):
            score -= 15

        # Normaliza score
        score = max(0, min(100, score))

        return score, conflicts

    def _has_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Verifica se dois períodos se sobrepõem."""
        # Adiciona buffer de intervalo mínimo
        buffer = timedelta(minutes=self.min_break_minutes)
        return start1 < (end2 + buffer) and end1 > (start2 - buffer)

    def _is_lunch_time(self, start: datetime, end: datetime) -> bool:
        """Verifica se o período inclui horário de almoço."""
        return (start.time() < self.lunch_end and end.time() > self.lunch_start)

    def _is_preferred_time(self, t: time) -> bool:
        """Verifica se é horário preferencial."""
        for period_name, (start, end) in self.preferred_times.items():
            if start <= t <= end:
                return True
        return False

    def _should_avoid(
        self,
        start: datetime,
        end: datetime,
        avoid_times: List[str] = None
    ) -> bool:
        """Verifica se deve evitar este horário."""
        if not avoid_times:
            return False

        for avoid in avoid_times:
            if "-" in avoid:
                avoid_start_str, avoid_end_str = avoid.split("-")
                avoid_start = datetime.strptime(avoid_start_str.strip(), "%H:%M").time()
                avoid_end = datetime.strptime(avoid_end_str.strip(), "%H:%M").time()

                if start.time() < avoid_end and end.time() > avoid_start:
                    return True

        return False

    def _get_score_reason(self, score: float) -> str:
        """Gera explicação para o score."""
        if score >= 90:
            return "Excelente horário - sem conflitos"
        elif score >= 75:
            return "Bom horário - poucos conflitos"
        elif score >= 50:
            return "Horário aceitável - alguns conflitos"
        else:
            return "Horário com muitos conflitos"

    def suggest_reschedule(
        self,
        meeting: Meeting,
        existing_meetings: List[Meeting],
        reason: str = None
    ) -> List[TimeSlot]:
        """
        Sugere horários alternativos para reagendamento.

        Args:
            meeting: Reunião a ser reagendada
            existing_meetings: Outras reuniões dos participantes
            reason: Motivo do reagendamento

        Returns:
            Lista de slots sugeridos
        """
        participant_ids = [p.user_id for p in meeting.participants]

        request = ScheduleSuggestionRequest(
            participant_ids=participant_ids,
            duration_minutes=meeting.duration_minutes,
            preferred_start_date=datetime.utcnow(),
            meeting_type=meeting.meeting_type,
            priority=meeting.priority,
            max_suggestions=5
        )

        # Remove a própria reunião da lista de existentes
        other_meetings = [m for m in existing_meetings if m.id != meeting.id]

        return self.find_optimal_slots(request, other_meetings)

    def check_availability(
        self,
        participant_ids: List[uuid.UUID],
        start: datetime,
        end: datetime,
        existing_meetings: List[Meeting]
    ) -> Dict[str, Any]:
        """
        Verifica disponibilidade para um horário específico.

        Returns:
            Dict com disponibilidade e conflitos
        """
        available = True
        conflicts = []
        partial_conflicts = []

        for meeting in existing_meetings:
            if self._has_overlap(start, end, meeting.scheduled_start, meeting.scheduled_end):
                meeting_participant_ids = {p.user_id for p in meeting.participants}
                conflicting = set(participant_ids) & meeting_participant_ids

                if conflicting:
                    if meeting.status in [MeetingStatusEnum.CONFIRMED, MeetingStatusEnum.IN_PROGRESS]:
                        available = False
                        conflicts.append({
                            "meeting_id": str(meeting.id),
                            "title": meeting.title,
                            "start": meeting.scheduled_start.isoformat(),
                            "end": meeting.scheduled_end.isoformat(),
                            "participants_affected": [str(p) for p in conflicting]
                        })
                    else:
                        partial_conflicts.append({
                            "meeting_id": str(meeting.id),
                            "title": meeting.title,
                            "status": meeting.status.value
                        })

        return {
            "available": available,
            "conflicts": conflicts,
            "partial_conflicts": partial_conflicts,
            "recommendation": "Horário disponível" if available else "Existem conflitos"
        }
