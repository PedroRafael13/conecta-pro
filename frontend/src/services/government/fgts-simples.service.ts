/**
 * Service Layer - FGTS e Simples Nacional
 *
 * Endpoints: FGTS Digital, DCTFWeb, Simples Nacional
 */

import api from '@/lib/api';
import type { StandardResponse } from '@/types/generated/government';

// Tipos locais para a camada de serviço
export interface CalculoFGTSParams {
  mes_referencia: string;
  ano_referencia: number;
  colaboradores: Array<{
    cpf: string;
    nome: string;
    salario: number;
    data_admissao: string;
  }>;
}

export interface CalculoINSSParams {
  mes_referencia: string;
  ano_referencia: number;
  colaboradores: Array<{
    cpf: string;
    remuneracao: number;
  }>;
}

export interface EmissaoDPSParams {
  mes_competencia: string;
  ano_competencia: number;
  colaboradores: Array<{
    cpf: string;
    valor_fgts: number;
    valor_contribuicao_social: number;
  }>;
}

/**
 * Calcula valores de FGTS
 */
export async function calcularFGTS(
  params: CalculoFGTSParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/fgts/calcular',
    {
      mes_referencia: params.mes_referencia,
      ano_referencia: params.ano_referencia,
      colaboradores: params.colaboradores,
    }
  );
  return data;
}

/**
 * Calcula valores de INSS
 */
export async function calcularINSS(
  params: CalculoINSSParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/fgts/calcular-inss',
    {
      mes_referencia: params.mes_referencia,
      ano_referencia: params.ano_referencia,
      colaboradores: params.colaboradores,
    }
  );
  return data;
}

/**
 * Emite DPS (Declaração Previdenciária e Social)
 */
export async function emitirDPS(
  params: EmissaoDPSParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/fgts/emitir-dps',
    {
      mes_competencia: params.mes_competencia,
      ano_competencia: params.ano_competencia,
      colaboradores: params.colaboradores,
    }
  );
  return data;
}

/**
 * Consulta extrato FGTS de colaborador
 */
export async function consultarExtrato(params: {
  cpf: string;
  periodo_inicial: string;
  periodo_final: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/fgts/consultar-extrato',
    {
      cpf: params.cpf,
      periodo_inicial: params.periodo_inicial,
      periodo_final: params.periodo_final,
    }
  );
  return data;
}

/**
 * Gera guia mensal FGTS
 */
export async function gerarGuiaMensal(params: {
  mes_referencia: string;
  ano_referencia: number;
}): Promise<Blob> {
  const { data } = await api.post(
    '/api/v1/government/fgts/gerar-guia',
    {
      mes_referencia: params.mes_referencia,
      ano_referencia: params.ano_referencia,
    },
    { responseType: 'blob' }
  );
  return data;
}

/**
 * Calcula apuração do Simples Nacional
 */
export async function calcularApuracaoSimples(params: {
  mes_referencia: string;
  ano_referencia: number;
  receita_bruta: number;
  anexo: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/simples/calcular-apuracao',
    {
      mes_referencia: params.mes_referencia,
      ano_referencia: params.ano_referencia,
      receita_bruta: params.receita_bruta,
      anexo: params.anexo,
    }
  );
  return data;
}

/**
 * Calcula PGDAS-D (Programa Gerador do DAS)
 */
export async function calcularPGDASD(params: {
  mes_referencia: string;
  ano_referencia: number;
  receitas: Array<{
    tipo: string;
    valor: number;
  }>;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/simples/calcular-pgdas',
    {
      mes_referencia: params.mes_referencia,
      ano_referencia: params.ano_referencia,
      receitas: params.receitas,
    }
  );
  return data;
}

/**
 * Gera DAS (Documento de Arrecadação do Simples Nacional)
 */
export async function gerarDAS(params: {
  mes_referencia: string;
  ano_referencia: number;
}): Promise<Blob> {
  const { data } = await api.post('/api/v1/government/simples/gerar-das', {
    mes_referencia: params.mes_referencia,
    ano_referencia: params.ano_referencia,
  }, {
    responseType: 'blob',
  });
  return data;
}

/**
 * Gera DARFs (Documento de Arrecadação de Receitas Federais)
 */
export async function gerarDARFs(params: {
  mes_referencia: string;
  ano_referencia: number;
  impostos: Array<{
    codigo_receita: string;
    valor: number;
  }>;
}): Promise<Blob> {
  const { data } = await api.post('/api/v1/government/simples/gerar-darfs', {
    mes_referencia: params.mes_referencia,
    ano_referencia: params.ano_referencia,
    impostos: params.impostos,
  }, {
    responseType: 'blob',
  });
  return data;
}

/**
 * Calcula Fator R (para definição do anexo Simples Nacional)
 */
export async function calcularFatorR(params: {
  receita_bruta: number;
  folha_salarios: number;
  periodo_meses: number;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/simples/calcular-fator-r',
    {
      receita_bruta: params.receita_bruta,
      folha_salarios: params.folha_salarios,
      periodo_meses: params.periodo_meses,
    }
  );
  return data;
}

/**
 * Consulta débitos FGTS
 */
export async function consultarDebitosFGTS(params: {
  cnpj: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/fgts/debitos',
    { params }
  );
  return data;
}

/**
 * Consulta situação no Simples Nacional
 */
export async function consultarSituacaoSimples(params: {
  cnpj: string;
}): Promise<StandardResponse> {
  const { data } = await api.get<StandardResponse>(
    '/api/v1/government/simples/situacao',
    { params }
  );
  return data;
}

const fgtsSimplesService = {
  calcularFGTS,
  calcularINSS,
  emitirDPS,
  consultarExtrato,
  gerarGuiaMensal,
  calcularApuracaoSimples,
  calcularPGDASD,
  gerarDAS,
  gerarDARFs,
  calcularFatorR,
  consultarDebitosFGTS,
  consultarSituacaoSimples,
};

export default fgtsSimplesService;
