/**
 * Service Layer - Receita Federal
 *
 * Endpoints: Validação CPF/CNPJ, Consultas Cadastrais
 */

import api from '@/lib/api';
import type {
  CadastroContribuinteResponse,
  StandardResponse,
} from '@/types/generated/government';

// Tipos locais para a camada de serviço
export interface ValidacaoDocumentoParams {
  documento: string;
  tipo?: 'CPF' | 'CNPJ';
}

export interface ConsultaCPFParams {
  cpf: string;
  data_nascimento?: string;
}

export interface ConsultaCNPJParams {
  cnpj: string;
  incluir_quadro_societario?: boolean;
}

/**
 * Valida CPF ou CNPJ (dígitos verificadores)
 */
export async function validarDocumento(
  params: ValidacaoDocumentoParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/receita/validar-documento',
    {
      documento: params.documento,
      tipo: params.tipo,
    }
  );
  return data;
}

/**
 * Consulta situação cadastral de CPF na Receita Federal
 */
export async function consultarCPF(
  params: ConsultaCPFParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/receita/consultar-cpf',
    {
      cpf: params.cpf,
      data_nascimento: params.data_nascimento,
    }
  );
  return data;
}

/**
 * Consulta situação cadastral de CNPJ na Receita Federal
 */
export async function consultarCNPJ(
  params: ConsultaCNPJParams
): Promise<CadastroContribuinteResponse> {
  const { data } = await api.post<CadastroContribuinteResponse>(
    '/api/v1/government/receita/consultar-cnpj',
    {
      cnpj: params.cnpj,
      incluir_quadro_societario: params.incluir_quadro_societario,
    }
  );
  return data;
}

/**
 * Valida inscrição estadual
 */
export async function validarInscricaoEstadual(params: {
  inscricao_estadual: string;
  uf: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/receita/validar-ie',
    params
  );
  return data;
}

const receitaFederalService = {
  validarDocumento,
  consultarCPF,
  consultarCNPJ,
  validarInscricaoEstadual,
};

export default receitaFederalService;
