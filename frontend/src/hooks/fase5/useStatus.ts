/**
 * Status Hooks - Monitoramento de Status e Health da Fase 5
 *
 * Re-exports dos hooks Orval do módulo fase5 - System Status
 */

import {
  useStatusFase5ApiV1Fase5StatusGet,
  useHealthFase5ApiV1Fase5HealthGet,
} from '@/types/generated/fase5/fase-5-grand-finale/fase-5-grand-finale';

// Read
export const useFase5Status = useStatusFase5ApiV1Fase5StatusGet;
export const useFase5Health = useHealthFase5ApiV1Fase5HealthGet;
