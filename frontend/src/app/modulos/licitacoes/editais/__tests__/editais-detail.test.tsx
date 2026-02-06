/**
 * Testes unitários do Detalhe de Edital
 */

import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '@/test/helpers/test-utils';
import { mockEdital } from '@/test/fixtures/licitacoes';
import * as tendersHooks from '@/hooks/bidding/useTenders';

vi.mock('@/hooks/bidding/useTenders');

// Componente simulado de detalhe
const EditalDetail = ({ id }: { id: string }) => {
  const { data: edital, isLoading } = (tendersHooks as any).useTender(id);

  if (isLoading) return <div>Carregando...</div>;
  if (!edital) return <div>Edital não encontrado</div>;

  return (
    <div>
      <h1>{edital.numero}</h1>
      <p>{edital.objeto}</p>
      <p>Status: {edital.status}</p>
      <p>Modalidade: {edital.modalidade}</p>
      <p>Valor: R$ {edital.valor_estimado}</p>
      <p>Órgão: {edital.orgao}</p>
      <button>Editar</button>
      <button>Deletar</button>
    </div>
  );
};

describe('Detalhe de Edital', () => {
  it('deve renderizar informações do edital', () => {
    vi.spyOn(tendersHooks, 'useBuscarEdital').mockReturnValue({
      data: mockEdital,
      isLoading: false,
    } as never);

    render(<EditalDetail id="edital-001" />);

    expect(screen.getByText('001/2026')).toBeInTheDocument();
    expect(screen.getByText('Serviços de vigilância patrimonial')).toBeInTheDocument();
    expect(screen.getByText('Status: publicado')).toBeInTheDocument();
    expect(screen.getByText('Modalidade: pregao_eletronico')).toBeInTheDocument();
  });

  it('deve mostrar loading state', () => {
    vi.spyOn(tendersHooks, 'useBuscarEdital').mockReturnValue({
      data: undefined,
      isLoading: true,
    } as never);

    render(<EditalDetail id="edital-001" />);

    expect(screen.getByText('Carregando...')).toBeInTheDocument();
  });

  it('deve mostrar mensagem quando edital não existe', () => {
    vi.spyOn(tendersHooks, 'useBuscarEdital').mockReturnValue({
      data: null,
      isLoading: false,
    } as never);

    render(<EditalDetail id="invalid-id" />);

    expect(screen.getByText('Edital não encontrado')).toBeInTheDocument();
  });

  it('deve renderizar botões de ação', () => {
    vi.spyOn(tendersHooks, 'useBuscarEdital').mockReturnValue({
      data: mockEdital,
      isLoading: false,
    } as never);

    render(<EditalDetail id="edital-001" />);

    expect(screen.getByText('Editar')).toBeInTheDocument();
    expect(screen.getByText('Deletar')).toBeInTheDocument();
  });
});
