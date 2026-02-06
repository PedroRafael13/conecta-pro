/**
 * Hooks - Integrations Module
 * React Query hooks para módulo de Integrações
 */

// Core Integrations
export * from './useAPIEndpoints';
export * from './useAPIKeys';
export * from './useWebhooks';
export * from './useIntegrationLogs';
export * from './useSyncQueue';
export * from './useIntegrationDashboard';

// Connectors
export * from './useConnectors';
export * from './useIntegrationAccounts';
export * from './useSyncRuns';
export * from './useSolides';

// Banking, WhatsApp, Email
// Nota: Hooks serão adicionados quando endpoints REST estiverem disponíveis
