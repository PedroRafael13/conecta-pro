/**
 * Service Layer - Estoque CAMPO
 * Integração com estoque para requisição e baixa de materiais
 */

import * as EstoqueAPI from '@/api/campo/generated/estoque/estoque';
import type {
  CriarRequisicaoRequest,
  AprovarRequisicaoRequest,
  RegistrarBaixaRequest,
  AlertasEstoqueBaixoApiV1CampoEstoqueAlertasGetParams,
  VerificarDisponibilidadeApiV1CampoEstoqueDisponibilidadeProdutoIdGetParams,
  RelatorioConsumoPeriodoApiV1CampoEstoqueRelatorioPeriodoGetParams,
} from '@/api/campo/generated/models';

export class EstoqueService {
  /**
   * Lista alertas de estoque
   */
  async listarAlertas(params?: AlertasEstoqueBaixoApiV1CampoEstoqueAlertasGetParams) {
    return EstoqueAPI.alertasEstoqueBaixoApiV1CampoEstoqueAlertasGet(params);
  }

  /**
   * Cria requisição de material
   */
  async criarRequisicao(data: CriarRequisicaoRequest) {
    return EstoqueAPI.criarRequisicaoApiV1CampoEstoqueRequisicaoPost(data);
  }

  /**
   * Busca requisição por ID
   */
  async buscarRequisicao(requisicaoId: string) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint buscarRequisicao não disponível na API gerada');
  }

  /**
   * Lista requisições
   */
  async listarRequisicoes(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    tecnico_id?: string;
  }) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint listarRequisicoes não disponível na API gerada');
  }

  /**
   * Aprova requisição
   */
  async aprovarRequisicao(requisicaoId: string, data: AprovarRequisicaoRequest) {
    return EstoqueAPI.aprovarRequisicaoApiV1CampoEstoqueRequisicaoRequisicaoIdAprovarPost(
      requisicaoId,
      data
    );
  }

  /**
   * Rejeita requisição
   */
  async rejeitarRequisicao(requisicaoId: string, motivo: string) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint rejeitarRequisicao não disponível na API gerada');
  }

  /**
   * Registra baixa de material na OS
   */
  async baixarMaterial(ordemServicoId: string, data: RegistrarBaixaRequest) {
    return EstoqueAPI.registrarBaixaApiV1CampoEstoqueBaixaOrdemServicoIdPost(
      ordemServicoId,
      data
    );
  }

  /**
   * Baixa automática de materiais
   */
  async baixaAutomatica(ordemServicoId: string) {
    return EstoqueAPI.baixaAutomaticaApiV1CampoEstoqueBaixaAutomaticaOrdemServicoIdPost(
      ordemServicoId
    );
  }

  /**
   * Lista materiais disponíveis
   */
  async listarMateriais(params?: {
    skip?: number;
    limit?: number;
    categoria?: string;
    search?: string;
  }) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint listarMateriais não disponível na API gerada');
  }

  /**
   * Busca material por ID
   */
  async buscarMaterial(materialId: string) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint buscarMaterial não disponível na API gerada');
  }

  /**
   * Verifica disponibilidade de materiais
   */
  async verificarDisponibilidade(produtoId: string, params: VerificarDisponibilidadeApiV1CampoEstoqueDisponibilidadeProdutoIdGetParams) {
    return EstoqueAPI.verificarDisponibilidadeApiV1CampoEstoqueDisponibilidadeProdutoIdGet(
      produtoId,
      params
    );
  }

  /**
   * Relatório de consumo por OS
   */
  async relatorioConsumoPorOS(ordemServicoId: string) {
    return EstoqueAPI.relatorioConsumoOsApiV1CampoEstoqueRelatorioOsOrdemServicoIdGet(
      ordemServicoId
    );
  }

  /**
   * Relatório de consumo por período
   */
  async relatorioConsumoPorPeriodo(params: RelatorioConsumoPeriodoApiV1CampoEstoqueRelatorioPeriodoGetParams) {
    return EstoqueAPI.relatorioConsumoPeriodoApiV1CampoEstoqueRelatorioPeriodoGet(params);
  }
}

export const estoqueService = new EstoqueService();
