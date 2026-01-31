/**
 * React Query Hook - useGlobalSearch
 *
 * Hook para busca global no sistema com React Query
 * - Busca unificada em múltiplas entidades
 * - Cache automático de resultados
 * - Debounce recomendado para evitar queries excessivas
 *
 * @example
 * ```tsx
 * function SearchComponent() {
 *   const [query, setQuery] = useState('');
 *   const { data, isLoading } = useGlobalSearch(
 *     { q: query },
 *     { enabled: query.length >= 2 }
 *   );
 *
 *   return (
 *     <div>
 *       <input
 *         value={query}
 *         onChange={(e) => setQuery(e.target.value)}
 *         placeholder="Buscar..."
 *       />
 *       {isLoading && <Spinner />}
 *       {data?.results.map((result) => (
 *         <SearchResultCard key={result.id} result={result} />
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */

import { useQuery, type UseQueryOptions } from '@tanstack/react-query';
import { searchService, type GlobalSearchOptions } from '@/services/search/searchService';
import type { SearchResponse } from '@/types/generated/search/models';

export const searchKeys = {
  all: ['search'] as const,
  global: (params: GlobalSearchOptions) => [...searchKeys.all, 'global', params] as const,
};

/**
 * Hook para busca global no sistema
 *
 * @param options - Parâmetros de busca (q: query, limit: opcional)
 * @param queryOptions - Opções do React Query (enabled, staleTime, etc)
 * @returns Query com resultados da busca
 *
 * Recomendações:
 * - Use `enabled: query.length >= 2` para evitar queries vazias
 * - Combine com debounce para melhor UX
 * - staleTime padrão: 30 segundos
 */
export function useGlobalSearch(
  options: GlobalSearchOptions,
  queryOptions?: Omit<
    UseQueryOptions<SearchResponse, Error>,
    'queryKey' | 'queryFn'
  >
) {
  return useQuery({
    queryKey: searchKeys.global(options),
    queryFn: () => searchService.globalSearch(options),
    staleTime: 30000, // 30 segundos
    enabled: options.q.length >= 1, // mínimo 1 caractere
    ...queryOptions,
  });
}
