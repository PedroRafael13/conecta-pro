"""
Intelligent Operations Service - FASE 3 ONDA 2
==============================================

Otimização inteligente de operações com IA:
- Escalas automáticas otimizadas
- Distribuição inteligente de recursos
- Predição de demanda operacional
- Automação de processos operacionais

ROI Target: R$ 150K
Sprint: FASE 3 - Excelência Operacional
"""

from datetime import datetime, timedelta, time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import json
import statistics

class OptimizationType(str, Enum):
    """Tipos de otimização operacional."""
    SCALE_OPTIMIZATION = "scale_optimization"
    RESOURCE_ALLOCATION = "resource_allocation"
    DEMAND_PREDICTION = "demand_prediction"
    PROCESS_AUTOMATION = "process_automation"
    EFFICIENCY_BOOST = "efficiency_boost"

class ShiftType(str, Enum):
    """Tipos de turno."""
    MORNING = "morning"      # 06:00-14:00
    AFTERNOON = "afternoon"  # 14:00-22:00
    NIGHT = "night"          # 22:00-06:00
    FULL_DAY = "full_day"    # 08:00-18:00
    FLEXIBLE = "flexible"     # Horário flexível

class SkillLevel(str, Enum):
    """Níveis de habilidade."""
    TRAINEE = "trainee"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    SPECIALIST = "specialist"

class OptimizationStatus(str, Enum):
    """Status da otimização."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    APPLIED = "applied"
    FAILED = "failed"

@dataclass
class Employee:
    """Funcionário com skills e disponibilidade."""
    id: str
    name: str
    skills: List[str]
    skill_level: SkillLevel
    availability: Dict[str, List[str]]  # {"monday": ["morning", "afternoon"]}
    preferred_shifts: List[ShiftType]
    overtime_capacity: float  # 0.0-1.0
    performance_score: float  # 0.0-1.0
    cost_per_hour: float

@dataclass
class WorkStation:
    """Posto de trabalho/estação."""
    id: str
    name: str
    location: str
    required_skills: List[str]
    required_skill_level: SkillLevel
    capacity: int  # Quantas pessoas podem trabalhar simultaneamente
    priority: int  # 1-10 (10 = crítico)
    equipment_available: bool
    operational_hours: Dict[str, Tuple[time, time]]  # {"monday": (time(8,0), time(18,0))}

@dataclass
class DemandForecast:
    """Previsão de demanda operacional."""
    date: datetime
    shift: ShiftType
    workstation: str
    predicted_demand: int  # Número de pessoas necessárias
    confidence: float  # 0.0-1.0
    factors: List[str]  # Fatores que influenciam a demanda
    historical_pattern: List[float]  # Padrão histórico

@dataclass
class ScheduleAssignment:
    """Alocação de escala."""
    employee_id: str
    workstation_id: str
    date: datetime
    shift: ShiftType
    start_time: time
    end_time: time
    break_times: List[Tuple[time, time]]
    overtime: bool
    estimated_productivity: float

@dataclass
class OptimizedSchedule:
    """Escala otimizada completa."""
    id: str
    period_start: datetime
    period_end: datetime
    assignments: List[ScheduleAssignment]
    optimization_metrics: Dict[str, float]
    cost_analysis: Dict[str, float]
    efficiency_score: float
    coverage_score: float
    created_at: datetime
    status: OptimizationStatus

@dataclass
class OperationalInsight:
    """Insight operacional."""
    type: str
    description: str
    impact: str  # "high", "medium", "low"
    recommendation: str
    estimated_savings: float
    implementation_effort: str
    confidence: float

class IntelligentOperationsService:
    """Serviço de Operações Inteligentes com IA."""
    
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.workstations: Dict[str, WorkStation] = {}
        self.optimized_schedules: Dict[str, OptimizedSchedule] = {}
        
        # Configurações de otimização
        self.optimization_weights = {
            "cost": 0.3,
            "efficiency": 0.4,
            "employee_satisfaction": 0.2,
            "coverage": 0.1
        }
        
        # Inicializa dados de exemplo
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Inicializa dados de exemplo para demonstração."""
        # Funcionários de exemplo
        self.employees = {
            "EMP001": Employee(
                id="EMP001",
                name="Ana Silva",
                skills=["limpeza", "atendimento", "supervisao"],
                skill_level=SkillLevel.SENIOR,
                availability={
                    "monday": ["morning", "afternoon"],
                    "tuesday": ["morning", "afternoon"],
                    "wednesday": ["morning"],
                    "thursday": ["morning", "afternoon"],
                    "friday": ["morning", "afternoon"]
                },
                preferred_shifts=[ShiftType.MORNING],
                overtime_capacity=0.8,
                performance_score=0.92,
                cost_per_hour=25.0
            ),
            "EMP002": Employee(
                id="EMP002",
                name="Carlos Santos",
                skills=["manutencao", "eletrica", "supervisao"],
                skill_level=SkillLevel.SPECIALIST,
                availability={
                    "monday": ["morning", "afternoon", "night"],
                    "tuesday": ["morning", "afternoon"],
                    "wednesday": ["morning", "afternoon", "night"],
                    "thursday": ["morning", "afternoon"],
                    "friday": ["morning", "afternoon"]
                },
                preferred_shifts=[ShiftType.AFTERNOON, ShiftType.MORNING],
                overtime_capacity=0.6,
                performance_score=0.95,
                cost_per_hour=35.0
            ),
            "EMP003": Employee(
                id="EMP003",
                name="Maria Oliveira",
                skills=["limpeza", "organizacao"],
                skill_level=SkillLevel.PLENO,
                availability={
                    "monday": ["morning", "afternoon"],
                    "tuesday": ["morning", "afternoon"],
                    "wednesday": ["morning", "afternoon"],
                    "thursday": ["morning", "afternoon"],
                    "friday": ["morning"]
                },
                preferred_shifts=[ShiftType.MORNING, ShiftType.AFTERNOON],
                overtime_capacity=0.4,
                performance_score=0.87,
                cost_per_hour=22.0
            )
        }
        
        # Postos de trabalho de exemplo
        self.workstations = {
            "WS001": WorkStation(
                id="WS001",
                name="Recepção Principal",
                location="Térreo - Bloco A",
                required_skills=["atendimento"],
                required_skill_level=SkillLevel.PLENO,
                capacity=2,
                priority=9,
                equipment_available=True,
                operational_hours={
                    "monday": (time(8, 0), time(18, 0)),
                    "tuesday": (time(8, 0), time(18, 0)),
                    "wednesday": (time(8, 0), time(18, 0)),
                    "thursday": (time(8, 0), time(18, 0)),
                    "friday": (time(8, 0), time(18, 0))
                }
            ),
            "WS002": WorkStation(
                id="WS002",
                name="Manutenção Técnica",
                location="Subsolo - Área Técnica",
                required_skills=["manutencao"],
                required_skill_level=SkillLevel.SENIOR,
                capacity=1,
                priority=8,
                equipment_available=True,
                operational_hours={
                    "monday": (time(7, 0), time(19, 0)),
                    "tuesday": (time(7, 0), time(19, 0)),
                    "wednesday": (time(7, 0), time(19, 0)),
                    "thursday": (time(7, 0), time(19, 0)),
                    "friday": (time(7, 0), time(17, 0))
                }
            ),
            "WS003": WorkStation(
                id="WS003",
                name="Limpeza Geral",
                location="Múltiplas áreas",
                required_skills=["limpeza"],
                required_skill_level=SkillLevel.JUNIOR,
                capacity=3,
                priority=6,
                equipment_available=True,
                operational_hours={
                    "monday": (time(6, 0), time(22, 0)),
                    "tuesday": (time(6, 0), time(22, 0)),
                    "wednesday": (time(6, 0), time(22, 0)),
                    "thursday": (time(6, 0), time(22, 0)),
                    "friday": (time(6, 0), time(22, 0))
                }
            )
        }
    
    async def optimize_schedule(self, 
                               start_date: datetime, 
                               end_date: datetime,
                               optimization_type: OptimizationType = OptimizationType.SCALE_OPTIMIZATION) -> OptimizedSchedule:
        """
        Otimiza escala para período específico usando IA.
        
        Args:
            start_date: Data início do período
            end_date: Data fim do período  
            optimization_type: Tipo de otimização
            
        Returns:
            Escala otimizada com IA
        """
        schedule_id = f"OPT_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        # Gera previsão de demanda
        demand_forecasts = await self._generate_demand_forecasts(start_date, end_date)
        
        # Executa algoritmo de otimização
        assignments = await self._run_optimization_algorithm(demand_forecasts, start_date, end_date)
        
        # Calcula métricas de otimização
        metrics = await self._calculate_optimization_metrics(assignments)
        
        # Análise de custo
        cost_analysis = await self._analyze_costs(assignments)
        
        # Calcula scores
        efficiency_score = await self._calculate_efficiency_score(assignments)
        coverage_score = await self._calculate_coverage_score(assignments, demand_forecasts)
        
        optimized_schedule = OptimizedSchedule(
            id=schedule_id,
            period_start=start_date,
            period_end=end_date,
            assignments=assignments,
            optimization_metrics=metrics,
            cost_analysis=cost_analysis,
            efficiency_score=efficiency_score,
            coverage_score=coverage_score,
            created_at=datetime.now(),
            status=OptimizationStatus.COMPLETED
        )
        
        # Armazena escala otimizada
        self.optimized_schedules[schedule_id] = optimized_schedule
        
        return optimized_schedule
    
    async def _generate_demand_forecasts(self, start_date: datetime, end_date: datetime) -> List[DemandForecast]:
        """Gera previsões de demanda usando algoritmos de ML."""
        forecasts = []
        
        current_date = start_date
        while current_date <= end_date:
            # Para cada estação de trabalho
            for ws_id, workstation in self.workstations.items():
                # Previsão para turnos diferentes
                for shift in ShiftType:
                    if shift != ShiftType.FLEXIBLE:  # Pula flexible por simplicidade
                        # Algoritmo simples de predição (em produção seria ML real)
                        base_demand = workstation.capacity
                        
                        # Ajustes por dia da semana
                        weekday = current_date.weekday()
                        day_factor = 1.0
                        if weekday == 0:  # Segunda
                            day_factor = 1.2
                        elif weekday == 4:  # Sexta  
                            day_factor = 0.9
                        elif weekday >= 5:  # Fim de semana
                            day_factor = 0.6
                        
                        # Ajustes por turno
                        shift_factor = 1.0
                        if shift == ShiftType.MORNING:
                            shift_factor = 1.1
                        elif shift == ShiftType.NIGHT:
                            shift_factor = 0.7
                        
                        # Ajustes por prioridade da estação
                        priority_factor = workstation.priority / 10
                        
                        predicted_demand = int(base_demand * day_factor * shift_factor * priority_factor)
                        
                        forecasts.append(DemandForecast(
                            date=current_date,
                            shift=shift,
                            workstation=ws_id,
                            predicted_demand=max(1, predicted_demand),
                            confidence=0.85,
                            factors=[f"weekday_{weekday}", f"shift_{shift.value}", f"priority_{workstation.priority}"],
                            historical_pattern=[base_demand * 0.9, base_demand, base_demand * 1.1]
                        ))
            
            current_date += timedelta(days=1)
        
        return forecasts
    
    async def _run_optimization_algorithm(self, 
                                         forecasts: List[DemandForecast], 
                                         start_date: datetime, 
                                         end_date: datetime) -> List[ScheduleAssignment]:
        """Executa algoritmo de otimização de escala (simulação ML)."""
        assignments = []
        
        # Agrupa previsões por data e turno
        forecast_dict = {}
        for forecast in forecasts:
            key = (forecast.date, forecast.shift)
            if key not in forecast_dict:
                forecast_dict[key] = []
            forecast_dict[key].append(forecast)
        
        # Para cada dia e turno, otimiza alocações
        for (date, shift), day_forecasts in forecast_dict.items():
            # Funcionários disponíveis neste turno
            available_employees = self._get_available_employees(date, shift)
            
            # Algoritmo greedy para alocação ótima
            for forecast in sorted(day_forecasts, key=lambda x: x.workstation, reverse=True):
                workstation = self.workstations[forecast.workstation]
                needed_people = forecast.predicted_demand
                
                # Seleciona melhores funcionários para esta estação
                suitable_employees = [
                    emp for emp in available_employees
                    if self._is_employee_suitable(emp, workstation)
                ]
                
                # Ordena por score de adequação
                suitable_employees.sort(
                    key=lambda emp: self._calculate_suitability_score(emp, workstation, shift),
                    reverse=True
                )
                
                # Aloca funcionários
                allocated = 0
                for emp in suitable_employees[:needed_people]:
                    if allocated >= workstation.capacity:
                        break
                    
                    start_time, end_time = self._get_shift_times(shift, workstation)
                    
                    assignment = ScheduleAssignment(
                        employee_id=emp.id,
                        workstation_id=forecast.workstation,
                        date=date,
                        shift=shift,
                        start_time=start_time,
                        end_time=end_time,
                        break_times=[(time(12, 0), time(13, 0))],  # Almoço padrão
                        overtime=False,
                        estimated_productivity=emp.performance_score * 0.95  # Pequena redução por fadiga
                    )
                    
                    assignments.append(assignment)
                    allocated += 1
                    
                    # Remove funcionário da lista de disponíveis
                    available_employees.remove(emp)
        
        return assignments
    
    def _get_available_employees(self, date: datetime, shift: ShiftType) -> List[Employee]:
        """Retorna funcionários disponíveis para data/turno específico."""
        weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekday = weekday_names[date.weekday()]
        
        available = []
        for emp in self.employees.values():
            if weekday in emp.availability:
                shift_map = {
                    ShiftType.MORNING: "morning",
                    ShiftType.AFTERNOON: "afternoon", 
                    ShiftType.NIGHT: "night",
                    ShiftType.FULL_DAY: "morning"  # Full day precisa estar disponível de manhã
                }
                
                required_availability = shift_map.get(shift)
                if required_availability in emp.availability[weekday]:
                    available.append(emp)
        
        return available
    
    def _is_employee_suitable(self, employee: Employee, workstation: WorkStation) -> bool:
        """Verifica se funcionário é adequado para estação."""
        # Verifica se tem skills necessárias
        has_required_skills = any(skill in employee.skills for skill in workstation.required_skills)
        
        # Verifica nível de skill
        skill_levels = [SkillLevel.TRAINEE, SkillLevel.JUNIOR, SkillLevel.PLENO, SkillLevel.SENIOR, SkillLevel.SPECIALIST]
        emp_level_idx = skill_levels.index(employee.skill_level)
        required_level_idx = skill_levels.index(workstation.required_skill_level)
        
        has_sufficient_level = emp_level_idx >= required_level_idx
        
        return has_required_skills and has_sufficient_level
    
    def _calculate_suitability_score(self, employee: Employee, workstation: WorkStation, shift: ShiftType) -> float:
        """Calcula score de adequação funcionário-estação."""
        score = 0.0
        
        # Score por skills (40%)
        matching_skills = len(set(employee.skills) & set(workstation.required_skills))
        total_required_skills = len(workstation.required_skills)
        skill_score = matching_skills / total_required_skills if total_required_skills > 0 else 0
        score += skill_score * 0.4
        
        # Score por performance (30%)
        score += employee.performance_score * 0.3
        
        # Score por preferência de turno (20%)
        shift_preference_score = 1.0 if shift in employee.preferred_shifts else 0.5
        score += shift_preference_score * 0.2
        
        # Score por custo (10% - inverso, menor custo = melhor score)
        max_cost = max(emp.cost_per_hour for emp in self.employees.values())
        cost_score = (max_cost - employee.cost_per_hour) / max_cost
        score += cost_score * 0.1
        
        return score
    
    def _get_shift_times(self, shift: ShiftType, workstation: WorkStation) -> Tuple[time, time]:
        """Retorna horários de início e fim do turno."""
        shift_times = {
            ShiftType.MORNING: (time(6, 0), time(14, 0)),
            ShiftType.AFTERNOON: (time(14, 0), time(22, 0)),
            ShiftType.NIGHT: (time(22, 0), time(6, 0)),
            ShiftType.FULL_DAY: (time(8, 0), time(18, 0))
        }
        
        return shift_times.get(shift, (time(8, 0), time(17, 0)))
    
    async def _calculate_optimization_metrics(self, assignments: List[ScheduleAssignment]) -> Dict[str, float]:
        """Calcula métricas de otimização."""
        if not assignments:
            return {}
        
        # Utilização de funcionários
        total_employees = len(self.employees)
        used_employees = len(set(a.employee_id for a in assignments))
        employee_utilization = used_employees / total_employees
        
        # Utilização de estações
        total_workstations = len(self.workstations)
        used_workstations = len(set(a.workstation_id for a in assignments))
        workstation_utilization = used_workstations / total_workstations
        
        # Produtividade média
        avg_productivity = statistics.mean(a.estimated_productivity for a in assignments)
        
        # Distribuição de turnos
        shift_distribution = {}
        for assignment in assignments:
            shift = assignment.shift.value
            shift_distribution[shift] = shift_distribution.get(shift, 0) + 1
        
        # Score de balanceamento
        total_assignments = len(assignments)
        shift_balance_score = 1.0 - (max(shift_distribution.values()) - min(shift_distribution.values())) / total_assignments
        
        return {
            "employee_utilization": employee_utilization,
            "workstation_utilization": workstation_utilization,
            "avg_productivity": avg_productivity,
            "shift_balance_score": shift_balance_score,
            "total_assignments": total_assignments,
            "unique_employees": used_employees,
            "unique_workstations": used_workstations
        }
    
    async def _analyze_costs(self, assignments: List[ScheduleAssignment]) -> Dict[str, float]:
        """Analisa custos da escala otimizada."""
        total_cost = 0.0
        regular_hours_cost = 0.0
        overtime_cost = 0.0
        
        for assignment in assignments:
            employee = self.employees[assignment.employee_id]
            
            # Calcula horas trabalhadas
            start_datetime = datetime.combine(assignment.date, assignment.start_time)
            end_datetime = datetime.combine(assignment.date, assignment.end_time)
            
            # Ajusta para turno noturno que cruza meia-noite
            if assignment.shift == ShiftType.NIGHT and end_datetime <= start_datetime:
                end_datetime += timedelta(days=1)
            
            hours_worked = (end_datetime - start_datetime).total_seconds() / 3600
            
            # Desconta pausas
            break_hours = sum((datetime.combine(assignment.date, end) - datetime.combine(assignment.date, start)).total_seconds() / 3600 
                            for start, end in assignment.break_times)
            net_hours = hours_worked - break_hours
            
            # Calcula custo
            if assignment.overtime:
                overtime_cost += net_hours * employee.cost_per_hour * 1.5  # 50% adicional
            else:
                regular_hours_cost += net_hours * employee.cost_per_hour
            
            total_cost += net_hours * employee.cost_per_hour * (1.5 if assignment.overtime else 1.0)
        
        return {
            "total_cost": total_cost,
            "regular_hours_cost": regular_hours_cost,
            "overtime_cost": overtime_cost,
            "avg_cost_per_hour": total_cost / sum((datetime.combine(a.date, a.end_time) - datetime.combine(a.date, a.start_time)).total_seconds() / 3600 for a in assignments) if assignments else 0,
            "cost_efficiency_score": 1.0 - (overtime_cost / total_cost) if total_cost > 0 else 0
        }
    
    async def _calculate_efficiency_score(self, assignments: List[ScheduleAssignment]) -> float:
        """Calcula score de eficiência da escala."""
        if not assignments:
            return 0.0
        
        # Média ponderada de produtividade
        total_productivity = sum(a.estimated_productivity for a in assignments)
        avg_productivity = total_productivity / len(assignments)
        
        # Penalty por assignments com baixa adequação
        low_productivity_penalty = sum(1 for a in assignments if a.estimated_productivity < 0.7) / len(assignments)
        
        # Bonus por high performers
        high_productivity_bonus = sum(1 for a in assignments if a.estimated_productivity > 0.9) / len(assignments)
        
        efficiency = avg_productivity + high_productivity_bonus * 0.1 - low_productivity_penalty * 0.2
        
        return max(0.0, min(1.0, efficiency))
    
    async def _calculate_coverage_score(self, assignments: List[ScheduleAssignment], forecasts: List[DemandForecast]) -> float:
        """Calcula score de cobertura da demanda."""
        if not forecasts:
            return 1.0
        
        coverage_scores = []
        
        # Agrupa assignments por estação, data e turno
        assignment_dict = {}
        for assignment in assignments:
            key = (assignment.workstation_id, assignment.date, assignment.shift)
            assignment_dict[key] = assignment_dict.get(key, 0) + 1
        
        # Compara com demanda prevista
        for forecast in forecasts:
            key = (forecast.workstation, forecast.date, forecast.shift)
            assigned_people = assignment_dict.get(key, 0)
            
            if forecast.predicted_demand > 0:
                coverage = min(assigned_people / forecast.predicted_demand, 1.0)
                coverage_scores.append(coverage)
        
        return statistics.mean(coverage_scores) if coverage_scores else 0.0
    
    async def generate_operational_insights(self, schedule: OptimizedSchedule) -> List[OperationalInsight]:
        """Gera insights operacionais com IA."""
        insights = []
        
        # Análise de eficiência
        if schedule.efficiency_score < 0.8:
            insights.append(OperationalInsight(
                type="efficiency_warning",
                description="Eficiência da escala abaixo do ideal",
                impact="medium",
                recommendation="Revisar alocação de funcionários para maximizar skills matching",
                estimated_savings=schedule.cost_analysis["total_cost"] * 0.1,
                implementation_effort="low",
                confidence=0.85
            ))
        
        # Análise de custos
        if schedule.cost_analysis["overtime_cost"] > schedule.cost_analysis["total_cost"] * 0.2:
            insights.append(OperationalInsight(
                type="cost_optimization",
                description="Alto uso de horas extras detectado",
                impact="high",
                recommendation="Contratar funcionários adicionais ou redistribuir carga",
                estimated_savings=schedule.cost_analysis["overtime_cost"] * 0.5,
                implementation_effort="medium",
                confidence=0.92
            ))
        
        # Análise de cobertura
        if schedule.coverage_score < 0.9:
            insights.append(OperationalInsight(
                type="coverage_gap",
                description="Cobertura de demanda insuficiente em alguns períodos",
                impact="high",
                recommendation="Identificar gargalos e realocar recursos críticos",
                estimated_savings=0.0,  # Evita perda de receita
                implementation_effort="low",
                confidence=0.88
            ))
        
        # Análise de balanceamento
        shift_assignments = {}
        for assignment in schedule.assignments:
            shift = assignment.shift.value
            shift_assignments[shift] = shift_assignments.get(shift, 0) + 1
        
        if len(shift_assignments) > 1:
            min_shift = min(shift_assignments.values())
            max_shift = max(shift_assignments.values())
            if max_shift > min_shift * 2:
                insights.append(OperationalInsight(
                    type="workload_imbalance",
                    description="Distribuição desigual entre turnos detectada",
                    impact="medium",
                    recommendation="Rebalancear distribuição para melhorar satisfação dos funcionários",
                    estimated_savings=0.0,
                    implementation_effort="medium",
                    confidence=0.76
                ))
        
        return insights
    
    async def get_optimization_summary(self, schedule_id: str) -> Dict[str, Any]:
        """Retorna resumo da otimização."""
        if schedule_id not in self.optimized_schedules:
            raise ValueError(f"Escala {schedule_id} não encontrada")
        
        schedule = self.optimized_schedules[schedule_id]
        insights = await self.generate_operational_insights(schedule)
        
        return {
            "schedule_id": schedule_id,
            "period": {
                "start": schedule.period_start.isoformat(),
                "end": schedule.period_end.isoformat()
            },
            "performance": {
                "efficiency_score": schedule.efficiency_score,
                "coverage_score": schedule.coverage_score,
                "status": schedule.status.value
            },
            "metrics": schedule.optimization_metrics,
            "costs": schedule.cost_analysis,
            "insights": [asdict(insight) for insight in insights],
            "recommendations_count": len(insights),
            "estimated_total_savings": sum(insight.estimated_savings for insight in insights)
        }

# Instância singleton do serviço
intelligent_operations_service = IntelligentOperationsService()
