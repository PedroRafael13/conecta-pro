/**
 * Service Layer - Search
 *
 * Gerencia busca global no sistema Conecta PRO
 * - Busca unificada em múltiplas entidades
 * - Colaboradores, Postos, Escalas, Ocorrências, Rondas
 * - Resultados ordenados por relevância
 *
 * Performance: até 20 resultados em <200ms
 */

import { api } from '@/lib/api';
import type {
  SearchResponse,
  GlobalSearchApiV1SearchGetParams,
} from '@/types/generated/search/models';

const BASE_URL = '/api/v1/search';

export interface GlobalSearchOptions {
  /** Query de busca (mínimo 1 caractere) */
  q: string;
  /** Limite de resultados (1-100, padrão: 20) */
  limit?: number;
}

export const searchService = {
  /**
   * Busca global no sistema
   *
   * Busca em:
   * - Colaboradores (nome, CPF, matrícula)
   * - Postos (nome, código)
   * - Escalas (período, código)
   * - Ocorrências (descrição, responsável)
   * - Rondas (código, inspetor)
   *
   * @param options - Parâmetros de busca
   * @returns Resultados da busca com tempo de execução
   *
   * @example
   * ```ts
   * const results = await searchService.globalSearch({
   *   q: 'João Silva',
   *   limit: 10
   * });
   * console.log(`Encontrados ${results.total} resultados em ${results.took_ms}ms`);
   * ```
   */
  async globalSearch(options: GlobalSearchOptions): Promise<SearchResponse> {
    const params: GlobalSearchApiV1SearchGetParams = {
      q: options.q,
      limit: options.limit,
    };

    const response = await api.get<SearchResponse>(BASE_URL, { params });
    return response.data;
  },
};
