/**
 * Service Layer - Gov.br e e-CAC
 *
 * Endpoints: Autenticação Gov.br, Consultas e-CAC
 */

import api from '@/lib/api';
import type { StandardResponse } from '@/types/generated/government';

// Tipos locais para a camada de serviço
export interface AutenticacaoGovBrParams {
  redirect_uri: string;
  state?: string;
  scope?: string[];
}

export interface CallbackGovBrParams {
  code: string;
  state: string;
}

export interface ConsultaDebitosParams {
  tipo?: 'federal' | 'previdenciaria' | 'fgts';
  situacao?: 'em_aberto' | 'parcelado' | 'quitado';
}

export interface EmissaoCertidaoParams {
  tipo_certidao:
    | 'negativa_debitos'
    | 'positiva_efeitos_negativa'
    | 'regularidade_fgts';
}

/**
 * Gera URL de autorização Gov.br
 */
export async function gerarUrlAutorizacao(
  params: AutenticacaoGovBrParams
): Promise<{ url: string }> {
  const { data } = await api.post<{ url: string }>(
    '/api/v1/government/govbr/autorizar',
    {
      redirect_uri: params.redirect_uri,
      state: params.state,
      scope: params.scope,
    }
  );
  return data;
}

/**
 * Processa callback de autenticação Gov.br
 */
export async function processarCallback(
  params: CallbackGovBrParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/govbr/callback',
    params
  );
  return data;
}

/**
 * Gera URL de logout Gov.br
 */
export async function gerarUrlLogout(params: {
  post_logout_redirect_uri: string;
}): Promise<{ url: string }> {
  const { data } = await api.post<{ url: string }>(
    '/api/v1/government/govbr/logout',
    {
      post_logout_redirect_uri: params.post_logout_redirect_uri,
    }
  );
  return data;
}

/**
 * Obtém dados do usuário autenticado via Gov.br
 */
export async function obterDadosUsuario(): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/govbr/usuario'
  );
  return data;
}

/**
 * Consulta débitos no e-CAC
 */
export async function consultarDebitos(
  params?: ConsultaDebitosParams
): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/ecac/debitos',
    { params }
  );
  return data;
}

/**
 * Consulta declarações entregues no e-CAC
 */
export async function consultarDeclaracoes(params?: {
  exercicio?: number;
  tipo?: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/ecac/declaracoes',
    { params }
  );
  return data;
}

/**
 * Consulta parcelamentos no e-CAC
 */
export async function consultarParcelamentos(params?: {
  situacao?: 'ativo' | 'quitado' | 'cancelado';
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/ecac/parcelamentos',
    { params }
  );
  return data;
}

/**
 * Consulta processos no e-CAC
 */
export async function consultarProcessos(params?: {
  tipo?: string;
  situacao?: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/ecac/processos',
    { params }
  );
  return data;
}

/**
 * Consulta situação fiscal no e-CAC
 */
export async function consultarSituacaoFiscal(params?: {
  cpf_cnpj?: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/ecac/situacao-fiscal',
    { params }
  );
  return data;
}

/**
 * Emite certidão de regularidade fiscal
 */
export async function emitirCertidao(
  params: EmissaoCertidaoParams
): Promise<Blob> {
  const { data } = await api.post('/api/v1/government/ecac/emitir-certidao', {
    tipo_certidao: params.tipo_certidao,
  }, {
    responseType: 'blob',
  });
  return data;
}

/**
 * Valida certidão de regularidade fiscal
 */
export async function validarCertidao(params: {
  codigo_validacao: string;
  cpf_cnpj: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/ecac/validar-certidao',
    params
  );
  return data;
}

/**
 * Consulta malha fiscal (IRPF)
 */
export async function consultarMalhaFiscal(params: {
  cpf: string;
  exercicio: number;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/ecac/malha-fiscal',
    { params }
  );
  return data;
}

/**
 * Consulta restituição IRPF
 */
export async function consultarRestituicao(params: {
  cpf: string;
  exercicio: number;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/ecac/restituicao',
    { params }
  );
  return data;
}

const govbrEcacService = {
  gerarUrlAutorizacao,
  processarCallback,
  gerarUrlLogout,
  obterDadosUsuario,
  consultarDebitos,
  consultarDeclaracoes,
  consultarParcelamentos,
  consultarProcessos,
  consultarSituacaoFiscal,
  emitirCertidao,
  validarCertidao,
  consultarMalhaFiscal,
  consultarRestituicao,
};

export default govbrEcacService;
