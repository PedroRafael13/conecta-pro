import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePagination } from '../usePagination';

describe('usePagination', () => {
  const mockData = Array.from({ length: 50 }, (_, i) => ({ id: i + 1, name: `Item ${i + 1}` }));

  describe('Cálculo de Páginas', () => {
    it('deve calcular total de páginas corretamente', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      expect(result.current.totalPages).toBe(5);
      expect(result.current.totalItems).toBe(50);
    });

    it('deve calcular índices corretamente', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 2 })
      );

      expect(result.current.startIndex).toBe(10);
      expect(result.current.endIndex).toBe(20);
    });

    it('deve retornar dados paginados corretos', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 1 })
      );

      expect(result.current.data).toHaveLength(10);
      expect(result.current.data[0]!.id).toBe(1);
      expect(result.current.data[9]!.id).toBe(10);
    });

    it('deve ajustar página inicial se for maior que total', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 10 })
      );

      expect(result.current.currentPage).toBe(5);
    });

    it('deve garantir pelo menos 1 página mesmo sem dados', () => {
      const { result } = renderHook(() =>
        usePagination({ data: [], pageSize: 10 })
      );

      expect(result.current.totalPages).toBe(1);
    });
  });

  describe('Navegação', () => {
    it('deve navegar para próxima página', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      act(() => {
        result.current.goToNextPage();
      });

      expect(result.current.currentPage).toBe(2);
      expect(result.current.data[0]!.id).toBe(11);
    });

    it('deve navegar para página anterior', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 2 })
      );

      act(() => {
        result.current.goToPreviousPage();
      });

      expect(result.current.currentPage).toBe(1);
      expect(result.current.data[0]!.id).toBe(1);
    });

    it('deve navegar para página específica', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      act(() => {
        result.current.goToPage(3);
      });

      expect(result.current.currentPage).toBe(3);
      expect(result.current.data[0]!.id).toBe(21);
    });

    it('deve navegar para primeira página', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 5 })
      );

      act(() => {
        result.current.goToFirstPage();
      });

      expect(result.current.currentPage).toBe(1);
    });

    it('deve navegar para última página', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      act(() => {
        result.current.goToLastPage();
      });

      expect(result.current.currentPage).toBe(5);
      expect(result.current.data[0]!.id).toBe(41);
    });

    it('deve impedir navegação além dos limites', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      act(() => {
        result.current.goToPage(0); // Tentar página 0
      });
      expect(result.current.currentPage).toBe(1);

      act(() => {
        result.current.goToPage(100); // Tentar página além do total
      });
      expect(result.current.currentPage).toBe(5);
    });

    it('não deve ir para próxima se estiver na última página', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 5 })
      );

      act(() => {
        result.current.goToNextPage();
      });

      expect(result.current.currentPage).toBe(5);
    });

    it('não deve ir para anterior se estiver na primeira página', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 1 })
      );

      act(() => {
        result.current.goToPreviousPage();
      });

      expect(result.current.currentPage).toBe(1);
    });
  });

  describe('Page Size', () => {
    it('deve permitir alterar tamanho da página', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      act(() => {
        result.current.setPageSize(20);
      });

      expect(result.current.pageSize).toBe(20);
      expect(result.current.totalPages).toBe(3);
    });

    it('deve resetar para primeira página ao mudar tamanho', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 5 })
      );

      act(() => {
        result.current.setPageSize(20);
      });

      expect(result.current.currentPage).toBe(1);
    });

    it('deve retornar quantidade correta de itens com novo pageSize', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      act(() => {
        result.current.setPageSize(25);
      });

      expect(result.current.data).toHaveLength(25);
    });
  });

  describe('Estados de Navegação', () => {
    it('deve indicar quando pode ir para próxima', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 1 })
      );

      expect(result.current.canGoNext).toBe(true);
      expect(result.current.canGoPrevious).toBe(false);
      expect(result.current.isFirstPage).toBe(true);
      expect(result.current.isLastPage).toBe(false);
    });

    it('deve indicar quando pode ir para anterior', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 5 })
      );

      expect(result.current.canGoNext).toBe(false);
      expect(result.current.canGoPrevious).toBe(true);
      expect(result.current.isFirstPage).toBe(false);
      expect(result.current.isLastPage).toBe(true);
    });

    it('deve indicar quando pode ir para ambas direções', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 3 })
      );

      expect(result.current.canGoNext).toBe(true);
      expect(result.current.canGoPrevious).toBe(true);
      expect(result.current.isFirstPage).toBe(false);
      expect(result.current.isLastPage).toBe(false);
    });
  });

  describe('Texto de Exibição', () => {
    it('deve formatar texto de exibição corretamente', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 1 })
      );

      expect(result.current.showingText).toBe('Mostrando 1-10 de 50');
    });

    it('deve formatar texto na página intermediária', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 3 })
      );

      expect(result.current.showingText).toBe('Mostrando 21-30 de 50');
    });

    it('deve formatar texto na última página', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 5 })
      );

      expect(result.current.showingText).toBe('Mostrando 41-50 de 50');
    });

    it('deve mostrar mensagem quando não há itens', () => {
      const { result } = renderHook(() =>
        usePagination({ data: [], pageSize: 10 })
      );

      expect(result.current.showingText).toBe('Nenhum item encontrado');
    });
  });

  describe('Range de Páginas', () => {
    it('deve retornar range de páginas visíveis', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10, initialPage: 3 })
      );

      // Página 3 deve mostrar: 1, ..., 2, 3, 4, ..., 5
      expect(result.current.pageRange).toContain(1);
      expect(result.current.pageRange).toContain(3);
      expect(result.current.pageRange).toContain(5);
    });

    it('deve incluir ellipsis quando há muitas páginas', () => {
      const largeData = Array.from({ length: 100 }, (_, i) => ({ id: i }));
      const { result } = renderHook(() =>
        usePagination({ data: largeData, pageSize: 10, initialPage: 5 })
      );

      expect(result.current.pageRange).toContain('...');
    });

    it('deve mostrar todas páginas quando poucas', () => {
      const smallData = Array.from({ length: 30 }, (_, i) => ({ id: i }));
      const { result } = renderHook(() =>
        usePagination({ data: smallData, pageSize: 10 })
      );

      expect(result.current.pageRange).toEqual([1, 2, 3]);
    });
  });

  describe('Edge Cases', () => {
    it('deve lidar com dados menores que pageSize', () => {
      const smallData = [{ id: 1 }, { id: 2 }];
      const { result } = renderHook(() =>
        usePagination({ data: smallData, pageSize: 10 })
      );

      expect(result.current.data).toHaveLength(2);
      expect(result.current.totalPages).toBe(1);
    });

    it('deve manter allData com todos os dados originais', () => {
      const { result } = renderHook(() =>
        usePagination({ data: mockData, pageSize: 10 })
      );

      expect(result.current.allData).toHaveLength(50);
      expect(result.current.data).toHaveLength(10);
    });

    it('deve lidar com pageSize maior que dados', () => {
      const smallData = [{ id: 1 }, { id: 2 }];
      const { result } = renderHook(() =>
        usePagination({ data: smallData, pageSize: 100 })
      );

      expect(result.current.endIndex).toBe(2);
      expect(result.current.showingText).toBe('Mostrando 1-2 de 2');
    });
  });
});
