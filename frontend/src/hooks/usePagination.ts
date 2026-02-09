'use client';

import { useState, useCallback, useMemo } from 'react';

export interface UsePaginationOptions<T> {
  data: T[];
  pageSize?: number;
  initialPage?: number;
}

export interface UsePaginationReturn<T> {
  // Dados paginados
  data: T[];
  allData: T[];

  // Estados de paginação
  currentPage: number;
  pageSize: number;
  totalPages: number;
  totalItems: number;

  // Navegação
  goToPage: (page: number) => void;
  goToNextPage: () => void;
  goToPreviousPage: () => void;
  goToFirstPage: () => void;
  goToLastPage: () => void;

  // Estados
  canGoNext: boolean;
  canGoPrevious: boolean;
  isFirstPage: boolean;
  isLastPage: boolean;

  // Configuração
  setPageSize: (size: number) => void;

  // Range info
  startIndex: number;
  endIndex: number;
  showingText: string;

  // Páginas visíveis (para paginação com ellipsis)
  pageRange: (number | string)[];
}

export function usePagination<T>({
  data,
  pageSize: initialPageSize = 10,
  initialPage = 1,
}: UsePaginationOptions<T>): UsePaginationReturn<T> {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSizeState] = useState(initialPageSize);

  const totalItems = data.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

  // Garantir que a página atual seja válida
  const validCurrentPage = useMemo(() => {
    return Math.min(Math.max(1, currentPage), totalPages);
  }, [currentPage, totalPages]);

  // Atualizar página atual se for inválida
  if (validCurrentPage !== currentPage) {
    setCurrentPage(validCurrentPage);
  }

  // Calcular índices
  const startIndex = (validCurrentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalItems);

  // Dados da página atual
  const paginatedData = useMemo(() => {
    return data.slice(startIndex, endIndex);
  }, [data, startIndex, endIndex]);

  // Estados de navegação
  const canGoNext = validCurrentPage < totalPages;
  const canGoPrevious = validCurrentPage > 1;
  const isFirstPage = validCurrentPage === 1;
  const isLastPage = validCurrentPage === totalPages;

  // Handlers de navegação
  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.min(Math.max(1, page), totalPages));
  }, [totalPages]);

  const goToNextPage = useCallback(() => {
    if (canGoNext) {
      setCurrentPage(prev => prev + 1);
    }
  }, [canGoNext]);

  const goToPreviousPage = useCallback(() => {
    if (canGoPrevious) {
      setCurrentPage(prev => prev - 1);
    }
  }, [canGoPrevious]);

  const goToFirstPage = useCallback(() => {
    setCurrentPage(1);
  }, []);

  const goToLastPage = useCallback(() => {
    setCurrentPage(totalPages);
  }, [totalPages]);

  // Alterar tamanho da página
  const setPageSize = useCallback((size: number) => {
    setPageSizeState(size);
    setCurrentPage(1); // Resetar para primeira página
  }, []);

  // Texto de exibição
  const showingText = useMemo(() => {
    if (totalItems === 0) {
      return 'Nenhum item encontrado';
    }
    return `Mostrando ${startIndex + 1}-${endIndex} de ${totalItems}`;
  }, [startIndex, endIndex, totalItems]);

  // Calcular range de páginas visíveis (com ellipsis)
  const pageRange = useMemo<(number | string)[]>(() => {
    const delta = 2; // Número de páginas antes e depois da atual
    const range: number[] = [];
    const rangeWithDots: (number | string)[] = [];
    let l: number | undefined;

    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= validCurrentPage - delta && i <= validCurrentPage + delta)) {
        range.push(i);
      }
    }

    for (const i of range) {
      if (l !== undefined) {
        if (i - l === 2) {
          rangeWithDots.push(l + 1);
        } else if (i - l !== 1) {
          rangeWithDots.push('...');
        }
      }
      rangeWithDots.push(i);
      l = i;
    }

    return rangeWithDots;
  }, [validCurrentPage, totalPages]);

  return {
    data: paginatedData,
    allData: data,
    currentPage: validCurrentPage,
    pageSize,
    totalPages,
    totalItems,
    goToPage,
    goToNextPage,
    goToPreviousPage,
    goToFirstPage,
    goToLastPage,
    canGoNext,
    canGoPrevious,
    isFirstPage,
    isLastPage,
    setPageSize,
    startIndex,
    endIndex,
    showingText,
    pageRange,
  };
}

export default usePagination;
