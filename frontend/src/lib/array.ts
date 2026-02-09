/**
 * Funções utilitárias para manipulação de arrays
 */

/**
 * Agrupa elementos de um array por uma chave específica
 */
export const groupBy = <T>(
  array: T[],
  keyGetter: (item: T) => string | number
): Record<string | number, T[]> => {
  if (!array || !Array.isArray(array)) {
    return {};
  }

  return array.reduce((acc, item) => {
    const key = keyGetter(item);
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(item);
    return acc;
  }, {} as Record<string | number, T[]>);
};

/**
 * Ordena um array por uma propriedade específica
 * @param array - Array a ser ordenado
 * @param key - Propriedade para ordenação
 * @param order - 'asc' (padrão) ou 'desc'
 */
export const sortBy = <T>(
  array: T[],
  key: keyof T,
  order: 'asc' | 'desc' = 'asc'
): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  const sorted = [...array].sort((a, b) => {
    const valueA = a[key];
    const valueB = b[key];

    // Trata valores nulos/undefined
    if (valueA === null || valueA === undefined) return 1;
    if (valueB === null || valueB === undefined) return -1;

    // Comparação de strings (case insensitive)
    if (typeof valueA === 'string' && typeof valueB === 'string') {
      return valueA.localeCompare(valueB, 'pt-BR', { sensitivity: 'base' });
    }

    // Comparação de datas
    if (valueA instanceof Date && valueB instanceof Date) {
      return valueA.getTime() - valueB.getTime();
    }

    // Comparação numérica padrão
    if (valueA < valueB) return -1;
    if (valueA > valueB) return 1;
    return 0;
  });

  return order === 'desc' ? sorted.reverse() : sorted;
};

/**
 * Ordena por múltiplas propriedades
 */
export const sortByMultiple = <T>(
  array: T[],
  keys: Array<{ key: keyof T; order?: 'asc' | 'desc' }>
): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  return [...array].sort((a, b) => {
    for (const { key, order = 'asc' } of keys) {
      const valueA = a[key];
      const valueB = b[key];

      // Trata valores nulos/undefined
      if (valueA === null || valueA === undefined) {
        if (valueB !== null && valueB !== undefined) {
          return order === 'asc' ? 1 : -1;
        }
        continue;
      }
      if (valueB === null || valueB === undefined) {
        return order === 'asc' ? -1 : 1;
      }

      let comparison = 0;

      // Comparação de strings
      if (typeof valueA === 'string' && typeof valueB === 'string') {
        comparison = valueA.localeCompare(valueB, 'pt-BR', { sensitivity: 'base' });
      }
      // Comparação de datas
      else if (valueA instanceof Date && valueB instanceof Date) {
        comparison = valueA.getTime() - valueB.getTime();
      }
      // Comparação numérica
      else {
        if (valueA < valueB) comparison = -1;
        if (valueA > valueB) comparison = 1;
      }

      if (comparison !== 0) {
        return order === 'desc' ? -comparison : comparison;
      }
    }

    return 0;
  });
};

/**
 * Remove valores duplicados de um array
 * Para objetos, usa uma chave para comparar ou compara por referência
 */
export const unique = <T>(
  array: T[],
  keyGetter?: (item: T) => string | number
): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  if (keyGetter) {
    const seen = new Set<string | number>();
    return array.filter((item) => {
      const key = keyGetter(item);
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });
  }

  return [...new Set(array)];
};

/**
 * Divide um array em chunks de tamanho especificado
 */
export const chunk = <T>(array: T[], size: number): T[][] => {
  if (!array || !Array.isArray(array) || size <= 0) {
    return [];
  }

  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }

  return chunks;
};

/**
 * Divide um array em duas partes com base em uma condição
 * Retorna [arrayQueAtendeCondicao, arrayQueNaoAtendeCondicao]
 */
export const partition = <T>(
  array: T[],
  predicate: (item: T) => boolean
): [T[], T[]] => {
  if (!array || !Array.isArray(array)) {
    return [[], []];
  }

  const pass: T[] = [];
  const fail: T[] = [];

  for (const item of array) {
    if (predicate(item)) {
      pass.push(item);
    } else {
      fail.push(item);
    }
  }

  return [pass, fail];
};

/**
 * Retorna a interseção de dois arrays (elementos presentes em ambos)
 */
export const intersection = <T>(array1: T[], array2: T[]): T[] => {
  if (!array1 || !array2 || !Array.isArray(array1) || !Array.isArray(array2)) {
    return [];
  }

  const set2 = new Set(array2);
  return array1.filter((item) => set2.has(item));
};

/**
 * Retorna a diferença entre dois arrays (elementos em array1 que não estão em array2)
 */
export const difference = <T>(array1: T[], array2: T[]): T[] => {
  if (!array1 || !Array.isArray(array1)) {
    return [];
  }

  if (!array2 || !Array.isArray(array2)) {
    return [...array1];
  }

  const set2 = new Set(array2);
  return array1.filter((item) => !set2.has(item));
};

/**
 * Retorna a união de dois arrays (todos os elementos únicos)
 */
export const union = <T>(array1: T[], array2: T[]): T[] => {
  return unique([...(array1 || []), ...(array2 || [])]);
};

/**
 * Move um elemento de uma posição para outra
 */
export const moveItem = <T>(
  array: T[],
  fromIndex: number,
  toIndex: number
): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  if (
    fromIndex < 0 ||
    fromIndex >= array.length ||
    toIndex < 0 ||
    toIndex >= array.length
  ) {
    return [...array];
  }

  const result = [...array];
  const [removed] = result.splice(fromIndex, 1) as [T];
  result.splice(toIndex, 0, removed);

  return result;
};

/**
 * Insere um elemento em uma posição específica
 */
export const insertAt = <T>(array: T[], index: number, item: T): T[] => {
  if (!array || !Array.isArray(array)) {
    return [item];
  }

  const result = [...array];
  result.splice(index, 0, item);
  return result;
};

/**
 * Remove um elemento de uma posição específica
 */
export const removeAt = <T>(array: T[], index: number): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  const result = [...array];
  result.splice(index, 1);
  return result;
};

/**
 * Remove um elemento específico do array (apenas a primeira ocorrência)
 */
export const removeItem = <T>(array: T[], item: T): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  const index = array.indexOf(item);
  if (index === -1) {
    return [...array];
  }

  const result = [...array];
  result.splice(index, 1);
  return result;
};

/**
 * Atualiza um elemento em uma posição específica
 */
export const updateAt = <T>(array: T[], index: number, item: T): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  if (index < 0 || index >= array.length) {
    return [...array];
  }

  const result = [...array];
  result[index] = item;
  return result;
};

/**
 * Retorna um elemento aleatório do array
 */
export const randomItem = <T>(array: T[]): T | undefined => {
  if (!array || !Array.isArray(array) || array.length === 0) {
    return undefined;
  }

  const index = Math.floor(Math.random() * array.length);
  return array[index];
};

/**
 * Embaralha um array (Fisher-Yates shuffle)
 */
export const shuffle = <T>(array: T[]): T[] => {
  if (!array || !Array.isArray(array)) {
    return [];
  }

  const result = [...array];

  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j]!, result[i]!];
  }

  return result;
};

/**
 * Conta ocorrências de valores em um array
 */
export const countBy = <T>(
  array: T[],
  keyGetter?: (item: T) => string | number
): Record<string | number, number> => {
  if (!array || !Array.isArray(array)) {
    return {};
  }

  return array.reduce((acc, item) => {
    const key = keyGetter ? keyGetter(item) : String(item);
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {} as Record<string | number, number>);
};

/**
 * Encontra o elemento com valor máximo de uma propriedade
 */
export const maxBy = <T>(array: T[], key: keyof T): T | undefined => {
  if (!array || !Array.isArray(array) || array.length === 0) {
    return undefined;
  }

  return array.reduce((max, item) => {
    const value = item[key];
    const maxValue = max[key];
    return value > maxValue ? item : max;
  });
};

/**
 * Encontra o elemento com valor mínimo de uma propriedade
 */
export const minBy = <T>(array: T[], key: keyof T): T | undefined => {
  if (!array || !Array.isArray(array) || array.length === 0) {
    return undefined;
  }

  return array.reduce((min, item) => {
    const value = item[key];
    const minValue = min[key];
    return value < minValue ? item : min;
  });
};

/**
 * Calcula a média de valores numéricos
 */
export const average = (array: number[]): number => {
  if (!array || !Array.isArray(array) || array.length === 0) {
    return 0;
  }

  const sum = array.reduce((acc, val) => acc + val, 0);
  return sum / array.length;
};

/**
 * Calcula a soma de valores numéricos
 */
export const sum = (array: number[]): number => {
  if (!array || !Array.isArray(array)) {
    return 0;
  }

  return array.reduce((acc, val) => acc + val, 0);
};

/**
 * Agrupa elementos em pares
 */
export const pairwise = <T>(array: T[]): Array<[T, T]> => {
  if (!array || !Array.isArray(array) || array.length < 2) {
    return [];
  }

  const pairs: Array<[T, T]> = [];
  for (let i = 0; i < array.length - 1; i++) {
    pairs.push([array[i]!, array[i + 1]!]);
  }

  return pairs;
};
