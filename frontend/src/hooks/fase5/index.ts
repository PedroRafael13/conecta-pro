/**
 * Fase 5 Hooks - Grand Finale
 *
 * API completa para Fase 5 - Grand Finale
 * Cobertura: 11 hooks React Query
 *
 * Funcionalidades:
 * - CCT Compliance: Validação de cargos, salários e propostas comerciais (SINDCOND 2026)
 * - Email Intelligence: Análise e classificação de emails com IA
 * - Quality Framework: Validação de qualidade do sistema (target 99+/100)
 * - System Status: Monitoramento de status e health
 *
 * Total: 11 endpoints organizados em:
 * - 6 endpoints CCT Compliance
 * - 2 endpoints Email Intelligence
 * - 1 endpoint Quality Framework
 * - 2 endpoints System Status
 */

// CCT Compliance
export * from './useCCT';

// Email Intelligence
export * from './useEmailIntelligence';

// Quality Framework
export * from './useQuality';

// System Status
export * from './useStatus';
