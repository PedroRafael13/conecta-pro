/**
 * React Query Hooks - Consent Management
 * Hooks para gestão de consentimentos LGPD
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ConsentService } from '@/services/security-lgpd';
import type { ConsentRequest } from '@/services/security-lgpd';

/**
 * Hook para registrar novo consentimento
 */
export function useRegisterConsent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ConsentRequest) =>
      ConsentService.registerConsent(request),
    onSuccess: (_, variables) => {
      // Invalida cache de consentimentos do titular
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'consents', variables.titular_id],
      });
    },
  });
}

/**
 * Hook para consultar consentimentos de um titular
 */
export function useConsents(titularId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['lgpd', 'consents', titularId],
    queryFn: () => ConsentService.getConsents(titularId),
    enabled: enabled && !!titularId,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para revogar consentimento
 */
export function useRevokeConsent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ consentId, reason }: { consentId: string; reason: string }) =>
      ConsentService.revokeConsent(consentId, reason),
    onSuccess: () => {
      // Invalida todos os consents (não sabemos o titular_id aqui)
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'consents'],
      });
    },
  });
}

/**
 * Hook para listar finalidades de consentimento
 */
export function usePurposes() {
  return useQuery({
    queryKey: ['lgpd', 'consent', 'purposes'],
    queryFn: () => ConsentService.listPurposes(),
    staleTime: 30 * 60 * 1000, // 30 minutos (dados estáticos)
  });
}

/**
 * Hook para listar bases legais LGPD
 */
export function useLegalBases() {
  return useQuery({
    queryKey: ['lgpd', 'consent', 'legal-bases'],
    queryFn: () => ConsentService.listLegalBases(),
    staleTime: 30 * 60 * 1000, // 30 minutos (dados estáticos)
  });
}

/**
 * Hook para verificar consentimentos ativos
 */
export function useActiveConsents(titularId: string) {
  return useQuery({
    queryKey: ['lgpd', 'consents', 'active', titularId],
    queryFn: async () => {
      const response = await ConsentService.getConsents(titularId);
      const consentsData = (response.data as Record<string, unknown> | undefined)?.consents;
      const consents = Array.isArray(consentsData) ? consentsData : [];
      return consents.filter((consent: any) =>
        ConsentService.isConsentActive(consent)
      );
    },
    enabled: !!titularId,
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
}

/**
 * Hook para verificar consentimentos expirados/expirando
 */
export function useExpiringConsents(titularId: string, daysThreshold: number = 30) {
  return useQuery({
    queryKey: ['lgpd', 'consents', 'expiring', titularId, daysThreshold],
    queryFn: async () => {
      const response = await ConsentService.getConsents(titularId);
      const consentsData = (response.data as Record<string, unknown> | undefined)?.consents;
      const consents = Array.isArray(consentsData) ? consentsData : [];

      return consents.filter((consent: any) => {
        if (!consent.expires_at) return false;
        const daysRemaining = ConsentService.getDaysUntilExpiration(
          consent.expires_at
        );
        return daysRemaining > 0 && daysRemaining <= daysThreshold;
      });
    },
    enabled: !!titularId,
    staleTime: 5 * 60 * 1000,
  });
}
