/**
 * Service Layer - SEFAZ
 *
 * Endpoints: NF-e, NFC-e, CT-e, MDF-e
 */

import api from '@/lib/api';
import type {
  CriarCTeRequest,
  CriarMDFeRequest,
  EncerrarMDFeRequest,
  IncluirCondutorRequest,
  ConsultaNFeResponse,
  DFeResponse,
  StandardResponse,
} from '@/types/generated/government';

export interface EmissaoNFeParams {
  destinatario: {
    cpf_cnpj: string;
    nome: string;
    endereco: Record<string, any>;
  };
  produtos: Array<{
    codigo: string;
    descricao: string;
    quantidade: number;
    valor_unitario: number;
    ncm: string;
  }>;
  impostos: {
    icms?: number;
    ipi?: number;
    pis?: number;
    cofins?: number;
  };
}

export interface ConsultaNFeParams {
  chave_acesso: string;
}

export interface CancelamentoNFeParams {
  chave_acesso: string;
  justificativa: string;
  protocolo: string;
}

/**
 * Emite NF-e
 */
export async function emitirNFe(
  params: EmissaoNFeParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/nfe/emitir',
    params
  );
  return data;
}

/**
 * Consulta NF-e por chave de acesso
 */
export async function consultarNFe(
  params: ConsultaNFeParams
): Promise<ConsultaNFeResponse> {
  const { data } = await api.get<ConsultaNFeResponse>(
    `/api/v1/government/sefaz/nfe/${params.chave_acesso}`
  );
  return data;
}

/**
 * Cancela NF-e
 */
export async function cancelarNFe(
  params: CancelamentoNFeParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/nfe/cancelar',
    params
  );
  return data;
}

/**
 * Emite Carta de Correção para NF-e
 */
export async function emitirCartaCorrecao(params: {
  chave_acesso: string;
  correcao: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/nfe/carta-correcao',
    params
  );
  return data;
}

/**
 * Inutiliza numeração de NF-e
 */
export async function inutilizarNumeracao(params: {
  serie: string;
  numero_inicial: number;
  numero_final: number;
  justificativa: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/nfe/inutilizar',
    params
  );
  return data;
}

/**
 * Emite CT-e (Conhecimento de Transporte Eletrônico)
 */
export async function emitirCTe(
  params: CriarCTeRequest
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/cte/emitir',
    params
  );
  return data;
}

/**
 * Cancela CT-e
 */
export async function cancelarCTe(params: {
  chave_acesso: string;
  justificativa: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/cte/cancelar',
    params
  );
  return data;
}

/**
 * Emite MDF-e (Manifesto Eletrônico de Documentos Fiscais)
 */
export async function emitirMDFe(
  params: CriarMDFeRequest
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/mdfe/emitir',
    params
  );
  return data;
}

/**
 * Encerra MDF-e
 */
export async function encerrarMDFe(
  params: EncerrarMDFeRequest
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/mdfe/encerrar',
    params
  );
  return data;
}

/**
 * Inclui condutor em MDF-e
 */
export async function incluirCondutor(
  params: IncluirCondutorRequest
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sefaz/mdfe/incluir-condutor',
    params
  );
  return data;
}

/**
 * Consulta status do serviço SEFAZ
 */
export async function consultarStatusServico(params?: {
  uf?: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/sefaz/status',
    { params }
  );
  return data;
}

/**
 * Consulta documentos fiscais destinados (DFe)
 */
export async function consultarDFeDestinadas(params?: {
  data_inicial?: string;
  data_final?: string;
  nsu?: number;
}): Promise<DFeResponse> {
  const { data } = await api.get<DFeResponse>(
    '/api/v1/government/sefaz-am/dfe',
    { params }
  );
  return data;
}

/**
 * Gera DANFE (Documento Auxiliar NF-e)
 */
export async function gerarDANFE(params: {
  chave_acesso: string;
  formato?: 'pdf' | 'xml';
}): Promise<Blob> {
  const { data } = await api.get(
    `/api/v1/government/sefaz/nfe/${params.chave_acesso}/danfe`,
    {
      params: { formato: params.formato },
      responseType: 'blob',
    }
  );
  return data;
}

/**
 * Gera DANFE NFC-e
 */
export async function gerarDANFENFCe(params: {
  chave_acesso: string;
}): Promise<Blob> {
  const { data } = await api.get(
    `/api/v1/government/nfce/danfe/${params.chave_acesso}`,
    { responseType: 'blob' }
  );
  return data;
}

const sefazService = {
  emitirNFe,
  consultarNFe,
  cancelarNFe,
  emitirCartaCorrecao,
  inutilizarNumeracao,
  emitirCTe,
  cancelarCTe,
  emitirMDFe,
  encerrarMDFe,
  incluirCondutor,
  consultarStatusServico,
  consultarDFeDestinadas,
  gerarDANFE,
  gerarDANFENFCe,
};

export default sefazService;
