// Field Service Module - Conecta PRO
// Exporta todos os componentes, hooks e tipos do módulo

// Dashboard principal
export { FieldServiceDashboard } from './FieldServiceDashboard';

// Types
export * from './types';

// Hooks
export { useFieldService } from './hooks';
export { useServiceOrders, useServiceOrder } from './orders/hooks';
export { useTechnicians, useTechnician, useRoutes, useRoute } from './technicians/hooks';

// Componentes de Ordens
export {
  ServiceOrderCard,
  type ServiceOrderCardProps,
  OrderTimeline,
  OrderTimelineCompact,
  type OrderTimelineProps,
} from './orders/components';

// Componentes de Técnicos
export {
  TechnicianCard,
  type TechnicianCardProps,
  TechnicianMap,
  type TechnicianMapProps,
  RouteOptimizer,
  type RouteOptimizerProps,
} from './technicians/components';
