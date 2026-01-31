/**
 * Financial Services - DEPRECIADO
 *
 * Este módulo foi migrado para hooks Orval.
 * Use os hooks em @/hooks/financial ao invés destes services.
 *
 * @deprecated Use '@/hooks/financial' ao invés deste módulo
 */

// Re-export dos hooks para compatibilidade temporária
export * from '@/hooks/financial';

// Log de aviso em desenvolvimento
if (process.env.NODE_ENV === 'development') {
  console.warn(
    'DEPRECATION WARNING: @/services/financial está depreciado. ' +
    'Use @/hooks/financial ao invés.'
  );
}
