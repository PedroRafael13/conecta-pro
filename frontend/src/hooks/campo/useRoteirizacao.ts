/**
 * React Query Hooks - Roteirização (CAMPO)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roteirizacaoService } from '@/services/campo';
import type {
  OtimizarRotaRequest,
  ReotimizarRotaRequest,
  CalcularDistanciaApiV1CampoRoteirizacaoCalcularDistanciaPostParams,
  AnalisarRotasEquipeApiV1CampoRoteirizacaoAnaliseEquipeGetParams,
  SugerirRedistribuicaoApiV1CampoRoteirizacaoAnaliseRedistribuicaoGetParams,
} from '@/api/campo/generated/models';

const QUERY_KEYS = {
  all: ['campo', 'roteirizacao'] as const,
  analiseEquipe: (params?: AnalisarRotasEquipeApiV1CampoRoteirizacaoAnaliseEquipeGetParams) => [...QUERY_KEYS.all, 'analise-equipe', params] as const,
  analiseRedistribuicao: (params?: SugerirRedistribuicaoApiV1CampoRoteirizacaoAnaliseRedistribuicaoGetParams) =>
    [...QUERY_KEYS.all, 'analise-redistribuicao', params] as const,
  mapa: (params: { data?: string; equipe_id?: string; tecnico_id?: string }) => [...QUERY_KEYS.all, 'mapa', params] as const,
};

export const useOtimizarRotas = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: OtimizarRotaRequest) => roteirizacaoService.otimizar(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.all }),
  });
};

export const useReotimizarRotas = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ReotimizarRotaRequest) => roteirizacaoService.reotimizar(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.all }),
  });
};

export const useCalcularDistancia = () => {
  return useMutation({
    mutationFn: (params: CalcularDistanciaApiV1CampoRoteirizacaoCalcularDistanciaPostParams) =>
      roteirizacaoService.calcularDistancia(params),
  });
};

export const useAnaliseEquipe = (params: AnalisarRotasEquipeApiV1CampoRoteirizacaoAnaliseEquipeGetParams) => {
  return useQuery({
    queryKey: QUERY_KEYS.analiseEquipe(params),
    queryFn: () => roteirizacaoService.analisarEquipe(params),
    enabled: !!params.data,
  });
};

export const useAnaliseRedistribuicao = (params: SugerirRedistribuicaoApiV1CampoRoteirizacaoAnaliseRedistribuicaoGetParams) => {
  return useQuery({
    queryKey: QUERY_KEYS.analiseRedistribuicao(params),
    queryFn: () => roteirizacaoService.analisarRedistribuicao(params),
    enabled: !!params.data,
  });
};

export const useRedistribuir = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: unknown) => roteirizacaoService.redistribuir(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.all }),
  });
};

export const useMapaRotas = (params: { data?: string; equipe_id?: string; tecnico_id?: string }) => {
  return useQuery({
    queryKey: QUERY_KEYS.mapa(params),
    queryFn: () => roteirizacaoService.visualizarMapa(params),
    enabled: !!params.data || !!params.equipe_id || !!params.tecnico_id,
  });
};
