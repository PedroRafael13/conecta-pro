/**
 * React Query Hooks - Estoque CAMPO
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { estoqueService } from '@/services/campo';
import type { EstoqueRequisicao, EstoqueBaixa } from '@/services/campo/types';
import type { AprovarRequisicaoRequest } from '@/api/campo/generated/models';

const QUERY_KEYS = {
  all: ['campo', 'estoque'] as const,
  alertas: () => [...QUERY_KEYS.all, 'alertas'] as const,
  requisicoes: () => [...QUERY_KEYS.all, 'requisicoes'] as const,
  requisicao: (id: string) => [...QUERY_KEYS.requisicoes(), id] as const,
  materiais: () => [...QUERY_KEYS.all, 'materiais'] as const,
  material: (id: string) => [...QUERY_KEYS.materiais(), id] as const,
};

export const useAlertasEstoque = () => {
  return useQuery({
    queryKey: QUERY_KEYS.alertas(),
    queryFn: () => estoqueService.listarAlertas(),
  });
};

export const useCriarRequisicao = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: EstoqueRequisicao) => estoqueService.criarRequisicao(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.requisicoes() }),
  });
};

export const useRequisicao = (requisicaoId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.requisicao(requisicaoId),
    queryFn: () => estoqueService.buscarRequisicao(requisicaoId),
    enabled: !!requisicaoId,
  });
};

export const useRequisicoes = (params?: any) => {
  return useQuery({
    queryKey: [QUERY_KEYS.requisicoes(), params],
    queryFn: () => estoqueService.listarRequisicoes(params),
  });
};

export const useAprovarRequisicao = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ requisicaoId, data }: { requisicaoId: string; data: AprovarRequisicaoRequest }) =>
      estoqueService.aprovarRequisicao(requisicaoId, data),
    onSuccess: (_, { requisicaoId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.requisicao(requisicaoId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.requisicoes() });
    },
  });
};

export const useRejeitarRequisicao = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ requisicaoId, motivo }: { requisicaoId: string; motivo: string }) =>
      estoqueService.rejeitarRequisicao(requisicaoId, motivo),
    onSuccess: (_, { requisicaoId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.requisicao(requisicaoId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.requisicoes() });
    },
  });
};

export const useBaixarMaterial = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ ordemServicoId, data }: { ordemServicoId: string; data: { itens_utilizados: EstoqueBaixa[]; observacoes?: string } }) =>
      estoqueService.baixarMaterial(ordemServicoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.materiais() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.alertas() });
    },
  });
};

export const useBaixaAutomatica = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ordemServicoId: string) => estoqueService.baixaAutomatica(ordemServicoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.materiais() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.alertas() });
    },
  });
};

export const useMateriais = (params?: any) => {
  return useQuery({
    queryKey: [QUERY_KEYS.materiais(), params],
    queryFn: () => estoqueService.listarMateriais(params),
  });
};

export const useMaterial = (materialId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.material(materialId),
    queryFn: () => estoqueService.buscarMaterial(materialId),
    enabled: !!materialId,
  });
};

export const useVerificarDisponibilidade = () => {
  return useMutation({
    mutationFn: ({ produtoId, params }: { produtoId: string; params: { quantidade: number; almoxarifado_id?: string } }) =>
      estoqueService.verificarDisponibilidade(produtoId, params),
  });
};
