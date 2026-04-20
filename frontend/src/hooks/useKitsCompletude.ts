'use client';

import { useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import type { CompletudeKit } from '@/types/kit-completude';
import { FIXTURE_KITS_04_2026 } from '@/fixtures/kits-completude';

// Enquanto T2 não sobe endpoints: true. Mudar para false após deploy T2 + E2E.
const USE_FIXTURE = true;

const API_BASE = '/api/v1/gedeon/kits';

async function fetchLote(mesRef: string): Promise<CompletudeKit[]> {
  if (USE_FIXTURE) {
    return FIXTURE_KITS_04_2026;
  }
  return customInstance<CompletudeKit[]>({
    url: `${API_BASE}/lote`,
    method: 'GET',
    params: { mes_ref: mesRef },
  });
}

async function fetchCompletude(
  condominioId: string,
  mesRef: string,
): Promise<CompletudeKit> {
  if (USE_FIXTURE) {
    const found = FIXTURE_KITS_04_2026.find((k) => k.condominio_id === condominioId);
    if (!found) throw new Error(`Condomínio ${condominioId} não encontrado na fixture`);
    return found;
  }
  return customInstance<CompletudeKit>({
    url: `${API_BASE}/completude/${condominioId}`,
    method: 'GET',
    params: { mes_ref: mesRef },
  });
}

export function useKitsLote(mesRef: string) {
  return useQuery({
    queryKey: ['kits', 'lote', mesRef],
    queryFn: () => fetchLote(mesRef),
    staleTime: 60_000,
  });
}

export function useKitCompletude(condominioId: string | null, mesRef: string) {
  return useQuery({
    queryKey: ['kits', 'completude', condominioId, mesRef],
    queryFn: () => fetchCompletude(condominioId!, mesRef),
    enabled: !!condominioId,
    staleTime: 60_000,
  });
}
