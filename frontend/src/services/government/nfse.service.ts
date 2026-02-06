/**
 * Service Layer - NFS-e
 *
 * Endpoints: Emissão, Consulta e Cancelamento de NFS-e
 * Suporta: NFS-e Padrão Nacional e NFS-e Manaus
 */

import api from '@/lib/api';
import type { StandardResponse } from '@/types/generated/government';

// Tipos locais para a camada de serviço
export interface EmissaoNFSeParams {
  tomador: {
    cpf_cnpj: string;
    razao_social: string;
    email?: string;
  };
  servico: {
    codigo: string;
    descricao: string;
    valor: number;
    aliquota_iss?: number;
  };
  rps?: {
    numero: number;
    serie: string;
  };
}

export interface CancelamentoNFSeParams {
  numero_nota: string;
  codigo_cancelamento: string;
  motivo: string;
}

export interface ConsultaNFSeParams {
  numero_nota?: string;
  numero_rps?: string;
  serie_rps?: string;
  data_emissao_inicial?: string;
  data_emissao_final?: string;
}

/**
 * Emite NFS-e Padrão Nacional
 */
export async function emitirNFSeNacional(
  params: EmissaoNFSeParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/nfse-nacional/emitir',
    {
      tomador: params.tomador,
      servico: params.servico,
      rps: params.rps,
    }
  );
  return data;
}

/**
 * Emite NFS-e Manaus
 */
export async function emitirNFSeManaus(
  params: EmissaoNFSeParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/nfse-manaus/emitir',
    {
      tomador: params.tomador,
      servico: params.servico,
      rps: params.rps,
    }
  );
  return data;
}

/**
 * Cancela NFS-e Padrão Nacional
 */
export async function cancelarNFSeNacional(
  params: CancelamentoNFSeParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/nfse-nacional/cancelar',
    {
      numero_nota: params.numero_nota,
      codigo_cancelamento: params.codigo_cancelamento,
      motivo: params.motivo,
    }
  );
  return data;
}

/**
 * Cancela NFS-e Manaus
 */
export async function cancelarNFSeManaus(
  params: CancelamentoNFSeParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/nfse-manaus/cancelar',
    {
      numero_nota: params.numero_nota,
      codigo_cancelamento: params.codigo_cancelamento,
      motivo: params.motivo,
    }
  );
  return data;
}

/**
 * Consulta NFS-e por RPS (Manaus)
 */
export async function consultarNFSePorRPS(params: {
  numero_rps: string;
  serie_rps: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    `/api/v1/government/nfse-manaus/consultar-rps/${params.numero_rps}`,
    { params: { serie: params.serie_rps } }
  );
  return data;
}

/**
 * Consulta lote de NFS-e
 */
export async function consultarLoteNFSe(params: {
  numero_lote: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    `/api/v1/government/nfse-nacional/consultar-lote/${params.numero_lote}`
  );
  return data;
}

/**
 * Lista NFS-e emitidas com filtros
 */
export async function listarNFSe(
  params: ConsultaNFSeParams
): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/nfse-nacional/listar',
    { params }
  );
  return data;
}

const nfseService = {
  emitirNFSeNacional,
  emitirNFSeManaus,
  cancelarNFSeNacional,
  cancelarNFSeManaus,
  consultarNFSePorRPS,
  consultarLoteNFSe,
  listarNFSe,
};

export default nfseService;
