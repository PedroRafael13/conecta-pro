/**
 * Operacional Hooks - Módulo Operacional Completo
 *
 * Módulo de Gestão Operacional (Postos, Escalas, Funcionários, etc.)
 * Cobertura: 100+ hooks React Query
 *
 * Sub-módulos:
 * - Allocations: Alocações de funcionários em postos
 * - Employees: Gestão de funcionários operacionais
 * - Posts: Gestão de postos de trabalho
 * - Scales: Gestão de escalas de trabalho
 * - Shifts: Gestão de turnos
 * - Occurrences: Ocorrências operacionais
 * - Patrol Rounds: Rondas de inspeção
 * - Disciplinary: Medidas administrativas/disciplinares
 * - Time Bank: Banco de horas
 * - Diarists: Gestão de diaristas
 * - Scale Templates: Templates de escalas
 * - Substitutions: Substituições de funcionários
 * - KPI Trends: Tendências de KPIs
 * - Reports: Relatórios operacionais
 */

// Allocations
export * from './useAllocations';

// Employees
export * from './useEmployees';

// Posts
export * from './usePosts';

// Scales
export * from './useScales';

// Shifts
export * from './useShifts';

// Occurrences
export * from './useOccurrences';

// Patrol Rounds
export * from './usePatrolRounds';

// Disciplinary Actions
export * from './useDisciplinary';

// Time Bank
export * from './useTimeBank';

// Diarists
export * from './useDiarists';

// Scale Templates
export * from './useScaleTemplates';

// Substitutions
export * from './useSubstitutions';

// KPI Trends
export * from './useKPITrends';

// Reports
export * from './useReports';

// WebSocket Operacional
export * from './useOperacionalWebSocket';
