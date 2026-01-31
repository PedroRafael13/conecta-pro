/**
 * Service Layer - Roteirização (CAMPO)
 * Otimização de rotas e distribuição de equipes
 */

import * as RoteirizacaoAPI from '@/api/campo/generated/roteirização/roteirização';
import type {
  OtimizarRotaRequest,
  ReotimizarRotaRequest,
  AnalisarRotasEquipeApiV1CampoRoteirizacaoAnaliseEquipeGetParams,
  SugerirRedistribuicaoApiV1CampoRoteirizacaoAnaliseRedistribuicaoGetParams,
  GetRotaTecnicoApiV1CampoRoteirizacaoTecnicoTecnicoIdGetParams,
  GetResumoDiaApiV1CampoRoteirizacaoResumoDiaTecnicoIdGetParams,
  CalcularDistanciaApiV1CampoRoteirizacaoCalcularDistanciaPostParams,
} from '@/api/campo/generated/models';

export class RoteirizacaoService {
  /**
   * Otimiza rotas para equipes
   */
  async otimizar(data: OtimizarRotaRequest) {
    return RoteirizacaoAPI.otimizarRotaApiV1CampoRoteirizacaoOtimizarPost(data);
  }

  /**
   * Reotimiza rotas existentes
   */
  async reotimizar(data: ReotimizarRotaRequest) {
    return RoteirizacaoAPI.reotimizarRotaApiV1CampoRoteirizacaoReotimizarPost(data);
  }

  /**
   * Calcula distância entre pontos
   */
  async calcularDistancia(params: CalcularDistanciaApiV1CampoRoteirizacaoCalcularDistanciaPostParams) {
    return RoteirizacaoAPI.calcularDistanciaApiV1CampoRoteirizacaoCalcularDistanciaPost(params);
  }

  /**
   * Análise de carga de trabalho por equipe
   */
  async analisarEquipe(params: AnalisarRotasEquipeApiV1CampoRoteirizacaoAnaliseEquipeGetParams) {
    return RoteirizacaoAPI.analisarRotasEquipeApiV1CampoRoteirizacaoAnaliseEquipeGet(params);
  }

  /**
   * Análise de redistribuição de tarefas
   */
  async analisarRedistribuicao(params: SugerirRedistribuicaoApiV1CampoRoteirizacaoAnaliseRedistribuicaoGetParams) {
    return RoteirizacaoAPI.sugerirRedistribuicaoApiV1CampoRoteirizacaoAnaliseRedistribuicaoGet(params);
  }

  /**
   * Redistribui tarefas entre equipes
   */
  async redistribuir(data: unknown) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint redistribuir não disponível na API gerada');
  }

  /**
   * Visualizar mapa de rotas
   */
  async visualizarMapa(params: {
    data?: string;
    equipe_id?: string;
    tecnico_id?: string;
  }) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint visualizarMapa não disponível na API gerada');
  }

  /**
   * Relatório de eficiência de rotas
   */
  async relatorioEficiencia(params?: {
    data_inicio?: string;
    data_fim?: string;
    formato?: 'pdf' | 'excel';
  }) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint relatorioEficiencia não disponível na API gerada');
  }

  /**
   * Obtém rota do técnico
   */
  async getRotaTecnico(tecnicoId: string, params: GetRotaTecnicoApiV1CampoRoteirizacaoTecnicoTecnicoIdGetParams) {
    return RoteirizacaoAPI.getRotaTecnicoApiV1CampoRoteirizacaoTecnicoTecnicoIdGet(
      tecnicoId,
      params
    );
  }

  /**
   * Lista tipos de otimização disponíveis
   */
  async listarTiposOtimizacao() {
    return RoteirizacaoAPI.listarTiposOtimizacaoApiV1CampoRoteirizacaoTiposOtimizacaoGet();
  }

  /**
   * Obtém resumo do dia do técnico
   */
  async getResumoDia(tecnicoId: string, params: GetResumoDiaApiV1CampoRoteirizacaoResumoDiaTecnicoIdGetParams) {
    return RoteirizacaoAPI.getResumoDiaApiV1CampoRoteirizacaoResumoDiaTecnicoIdGet(
      tecnicoId,
      params
    );
  }
}

export const roteirizacaoService = new RoteirizacaoService();
