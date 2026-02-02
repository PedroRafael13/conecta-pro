/**
 * Service Layer - Roteirização (CAMPO)
 * Otimização de rotas e distribuição de equipes
 */

import * as RoteirizacaoAPI from '@/api/campo/generated/campo-roteirizacao/campo-roteirizacao';
import type {
  OtimizarRotaRequest,
  ReotimizarRotaRequest,
  AnalisarRotasEquipeApiV1CampoRotasAnaliseEquipeGetParams,
  SugerirRedistribuicaoApiV1CampoRotasAnaliseRedistribuicaoGetParams,
  GetRotaTecnicoApiV1CampoRotasTecnicoTecnicoIdGetParams,
  GetResumoDiaApiV1CampoRotasResumoDiaTecnicoIdGetParams,
  CalcularDistanciaApiV1CampoRotasCalcularDistanciaPostParams,
} from '@/api/campo/generated/models';

export class RoteirizacaoService {
  /**
   * Otimiza rotas para equipes
   */
  async otimizar(data: OtimizarRotaRequest) {
    return RoteirizacaoAPI.otimizarRotaApiV1CampoRotasOtimizarPost(data);
  }

  /**
   * Reotimiza rotas existentes
   */
  async reotimizar(data: ReotimizarRotaRequest) {
    return RoteirizacaoAPI.reotimizarRotaApiV1CampoRotasReotimizarPost(data);
  }

  /**
   * Calcula distância entre pontos
   */
  async calcularDistancia(params: CalcularDistanciaApiV1CampoRotasCalcularDistanciaPostParams) {
    return RoteirizacaoAPI.calcularDistanciaApiV1CampoRotasCalcularDistanciaPost(params);
  }

  /**
   * Análise de carga de trabalho por equipe
   */
  async analisarEquipe(params: AnalisarRotasEquipeApiV1CampoRotasAnaliseEquipeGetParams) {
    return RoteirizacaoAPI.analisarRotasEquipeApiV1CampoRotasAnaliseEquipeGet(params);
  }

  /**
   * Análise de redistribuição de tarefas
   */
  async analisarRedistribuicao(params: SugerirRedistribuicaoApiV1CampoRotasAnaliseRedistribuicaoGetParams) {
    return RoteirizacaoAPI.sugerirRedistribuicaoApiV1CampoRotasAnaliseRedistribuicaoGet(params);
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
  async getRotaTecnico(tecnicoId: string, params: GetRotaTecnicoApiV1CampoRotasTecnicoTecnicoIdGetParams) {
    return RoteirizacaoAPI.getRotaTecnicoApiV1CampoRotasTecnicoTecnicoIdGet(
      tecnicoId,
      params
    );
  }

  /**
   * Lista tipos de otimização disponíveis
   */
  async listarTiposOtimizacao() {
    return RoteirizacaoAPI.listarTiposOtimizacaoApiV1CampoRotasTiposOtimizacaoGet();
  }

  /**
   * Obtém resumo do dia do técnico
   */
  async getResumoDia(tecnicoId: string, params: GetResumoDiaApiV1CampoRotasResumoDiaTecnicoIdGetParams) {
    return RoteirizacaoAPI.getResumoDiaApiV1CampoRotasResumoDiaTecnicoIdGet(
      tecnicoId,
      params
    );
  }
}

export const roteirizacaoService = new RoteirizacaoService();
