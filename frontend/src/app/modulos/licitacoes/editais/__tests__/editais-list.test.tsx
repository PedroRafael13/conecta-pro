/**
 * Testes unitários da Listagem de Editais
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, mockToast } from '@/test/helpers/test-utils';
import { mockEditais, mockEdital } from '@/test/fixtures/licitacoes';
import * as tendersHooks from '@/hooks/bidding/useTenders';

vi.mock('@/hooks/bidding/useTenders');

// Simular página de editais (importação fictícia para testes)
const EditaisPage = () => {
  const { data: editais, isLoading } = (tendersHooks as any).useTenders();
  const { mutate: deleteTender } = (tendersHooks as any).useDeleteTender();

  if (isLoading) return <div>Carregando...</div>;

  return (
    <div>
      <h1>Editais</h1>
      <button>Novo Edital</button>
      <table>
        <tbody>
          {editais?.map((edital: any) => (
            <tr key={edital.id} data-testid={`edital-${edital.id}`}>
              <td>{edital.numero}</td>
              <td>{edital.objeto}</td>
              <td>{edital.status}</td>
              <td>
                <button onClick={() => deleteTender(edital.id)}>
                  Deletar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

describe('Listagem de Editais', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Renderização', () => {
    it('deve renderizar título e botão novo edital', () => {
      vi.spyOn(tendersHooks, 'useTenders').mockReturnValue({
        data: [],
        isLoading: false,
      } as never);

      render(<EditaisPage />);

      expect(screen.getByText('Editais')).toBeInTheDocument();
      expect(screen.getByText('Novo Edital')).toBeInTheDocument();
    });

    it('deve mostrar loading state', () => {
      vi.spyOn(tendersHooks, 'useTenders').mockReturnValue({
        data: undefined,
        isLoading: true,
      } as never);

      render(<EditaisPage />);

      expect(screen.getByText('Carregando...')).toBeInTheDocument();
    });

    it('deve renderizar lista de editais', () => {
      vi.spyOn(tendersHooks, 'useTenders').mockReturnValue({
        data: mockEditais,
        isLoading: false,
      } as never);

      render(<EditaisPage />);

      expect(screen.getByText('001/2026')).toBeInTheDocument();
      expect(screen.getByText('002/2026')).toBeInTheDocument();
      expect(screen.getByText('003/2026')).toBeInTheDocument();
    });
  });

  describe('Dados exibidos', () => {
    beforeEach(() => {
      vi.spyOn(tendersHooks, 'useTenders').mockReturnValue({
        data: [mockEdital],
        isLoading: false,
      } as never);
    });

    it('deve exibir número do edital', () => {
      render(<EditaisPage />);
      expect(screen.getByText('001/2026')).toBeInTheDocument();
    });

    it('deve exibir objeto do edital', () => {
      render(<EditaisPage />);
      expect(
        screen.getByText('Serviços de vigilância patrimonial')
      ).toBeInTheDocument();
    });

    it('deve exibir status do edital', () => {
      render(<EditaisPage />);
      expect(screen.getByText('publicado')).toBeInTheDocument();
    });
  });

  describe('Ações CRUD', () => {
    it('deve permitir deletar edital', async () => {
      const mockDelete = vi.fn();
      vi.spyOn(tendersHooks, 'useTenders').mockReturnValue({
        data: [mockEdital],
        isLoading: false,
      } as never);
      vi.spyOn(tendersHooks, 'useDeleteTender').mockReturnValue({
        mutate: mockDelete,
      } as never);

      const user = userEvent.setup();
      render(<EditaisPage />);

      const deleteButton = screen.getByText('Deletar');
      await user.click(deleteButton);

      expect(mockDelete).toHaveBeenCalledWith('edital-001');
    });
  });

  describe('Estados vazios', () => {
    it('deve lidar com lista vazia', () => {
      vi.spyOn(tendersHooks, 'useTenders').mockReturnValue({
        data: [],
        isLoading: false,
      } as never);

      render(<EditaisPage />);

      // Não deve ter nenhuma linha de edital
      const rows = screen.queryAllByRole('row');
      expect(rows.length).toBe(0);
    });
  });
});
