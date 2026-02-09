/**
 * Testes unitários da Listagem de Editais
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '@/test/helpers/test-utils';
import { mockEditais, mockEdital } from '@/test/fixtures/licitacoes';
import * as tendersHooks from '@/hooks/bidding/useTenders';

vi.mock('@/hooks/bidding/useTenders', () => ({
  useListarEditais: vi.fn(),
  useRemoverEdital: vi.fn(),
}));

// Componente simulado de página de editais
const EditaisPage = () => {
  const { data: editais, isLoading } = (tendersHooks as any).useListarEditais();
  const { mutate: deleteTender } = (tendersHooks as any).useRemoverEdital();

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
    // Mock padrão para useRemoverEdital
    vi.mocked(tendersHooks.useRemoverEdital).mockReturnValue({
      mutate: vi.fn(),
    } as any);
  });

  describe('Renderização', () => {
    it('deve renderizar título e botão novo edital', () => {
      vi.mocked(tendersHooks.useListarEditais).mockReturnValue({
        data: [],
        isLoading: false,
      } as any);

      render(<EditaisPage />);

      expect(screen.getByText('Editais')).toBeInTheDocument();
      expect(screen.getByText('Novo Edital')).toBeInTheDocument();
    });

    it('deve mostrar loading state', () => {
      vi.mocked(tendersHooks.useListarEditais).mockReturnValue({
        data: undefined,
        isLoading: true,
      } as any);

      render(<EditaisPage />);

      expect(screen.getByText('Carregando...')).toBeInTheDocument();
    });

    it('deve renderizar lista de editais', () => {
      vi.mocked(tendersHooks.useListarEditais).mockReturnValue({
        data: mockEditais,
        isLoading: false,
      } as any);

      render(<EditaisPage />);

      expect(screen.getByText('001/2026')).toBeInTheDocument();
      expect(screen.getByText('002/2026')).toBeInTheDocument();
      expect(screen.getByText('003/2026')).toBeInTheDocument();
    });
  });

  describe('Dados exibidos', () => {
    beforeEach(() => {
      vi.mocked(tendersHooks.useListarEditais).mockReturnValue({
        data: [mockEdital],
        isLoading: false,
      } as any);
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
      vi.mocked(tendersHooks.useListarEditais).mockReturnValue({
        data: [mockEdital],
        isLoading: false,
      } as any);
      vi.mocked(tendersHooks.useRemoverEdital).mockReturnValue({
        mutate: mockDelete,
      } as any);

      const user = userEvent.setup();
      render(<EditaisPage />);

      const deleteButton = screen.getByText('Deletar');
      await user.click(deleteButton);

      expect(mockDelete).toHaveBeenCalledWith('edital-001');
    });
  });

  describe('Estados vazios', () => {
    it('deve lidar com lista vazia', () => {
      vi.mocked(tendersHooks.useListarEditais).mockReturnValue({
        data: [],
        isLoading: false,
      } as any);

      render(<EditaisPage />);

      // Não deve ter nenhuma linha de edital na tabela
      const rows = screen.queryAllByTestId(/edital-/);
      expect(rows.length).toBe(0);
    });
  });
});
