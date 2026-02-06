/**
 * Módulo HR - API Client
 * Exporta todos os hooks e tipos do módulo de Recursos Humanos
 * 
 * Cobertura: 236 endpoints, 1490 tipos, 152 hooks React Query
 * Submódulos: 11 (Analytics, Portal, Mobile, Payroll, REP, TimeTracking)
 */

// Analytics
export * from './generated/hr-analytics-dashboards/hr-analytics-dashboards';
export * from './generated/hr-analytics-kpis/hr-analytics-kpis';
export * from './generated/hr-analytics-reports/hr-analytics-reports';

// Mobile
export * from './generated/hr-mobile-check-ins/hr-mobile-check-ins';
export * from './generated/hr-mobile-devices/hr-mobile-devices';
export * from './generated/hr-mobile-geofencing/hr-mobile-geofencing';
export * from './generated/hr-mobile-offline-sync/hr-mobile-offline-sync';

// Payroll
export * from './generated/hr-payroll-integration/hr-payroll-integration';

// Portal
export * from './generated/hr-portal-employee-portal/hr-portal-employee-portal';

// REP Integration
export * from './generated/hr-rep-integration/hr-rep-integration';

// Time Tracking
export * from './generated/hr-time-tracking/hr-time-tracking';

// Models (tipos)
export * from './generated/models';
