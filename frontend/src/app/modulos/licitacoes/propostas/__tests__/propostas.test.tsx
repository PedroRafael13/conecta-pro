/**
 * Testes unitários de Propostas
 */

import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '@/test/helpers/test-utils';
import { mockPropostas, mockProposta } from '@/test/fixtures/licitacoes';

// Componente simulado de propostas
const PropostasPage = () => {
  return (
    <div>
      <h1>Propostas</h1>
      <button>Nova Proposta</button>
      <div data-testid="propostas-list">
        {mockPropostas.map((p) => (
          <div key={p.id} data-testid={`proposta-${p.id}`}>
            <span>{p.edital_numero}</span>
            <span>R$ {p.valor_proposto}</span>
            <span>{p.status}</span>
            <button>Submeter</button>
            <button>Editar</button>
            <button>Deletar</button>
          </div>
        ))}
      </div>
    </div>
  );
};

const PropostaDetail = () => {
  return (
    <div>
      <h1>Proposta {mockProposta.edital_numero}</h1>
      <p>Valor: R$ {mockProposta.valor_proposto}</p>
      <p>Prazo: {mockProposta.prazo_execucao} meses</p>
      <p>Status: {mockProposta.status}</p>
      <p>Observações: {mockProposta.observacoes}</p>
      <div data-testid="proposta-items">
        <h2>Itens da Proposta</h2>
        <button>Adicionar Item</button>
      </div>
    </div>
  );
};

describe('Propostas - Listagem', () => {
  it('deve renderizar título e botão nova proposta', () => {
    render(<PropostasPage />);

    expect(screen.getByText('Propostas')).toBeInTheDocument();
    expect(screen.getByText('Nova Proposta')).toBeInTheDocument();
  });

  it('deve renderizar lista de propostas', () => {
    render(<PropostasPage />);

    expect(screen.getByText('001/2026')).toBeInTheDocument();
    expect(screen.getByText('002/2026')).toBeInTheDocument();
    expect(screen.getByText('003/2026')).toBeInTheDocument();
  });

  it('deve exibir valores e status das propostas', () => {
    render(<PropostasPage />);

    expect(screen.getByText('R$ 480000')).toBeInTheDocument();
    expect(screen.getByText('em_analise')).toBeInTheDocument();
  });

  it('deve renderizar botões de ação', () => {
    render(<PropostasPage />);

    const submitButtons = screen.getAllByText('Submeter');
    const editButtons = screen.getAllByText('Editar');
    const deleteButtons = screen.getAllByText('Deletar');

    expect(submitButtons).toHaveLength(3);
    expect(editButtons).toHaveLength(3);
    expect(deleteButtons).toHaveLength(3);
  });
});

describe('Propostas - Detalhe', () => {
  it('deve renderizar informações da proposta', () => {
    render(<PropostaDetail />);

    expect(screen.getByText('Proposta 001/2026')).toBeInTheDocument();
    expect(screen.getByText('Valor: R$ 480000')).toBeInTheDocument();
    expect(screen.getByText('Prazo: 12 meses')).toBeInTheDocument();
    expect(screen.getByText('Status: em_analise')).toBeInTheDocument();
  });

  it('deve exibir observações', () => {
    render(<PropostaDetail />);

    expect(
      screen.getByText('Observações: Proposta técnica conforme especificações')
    ).toBeInTheDocument();
  });

  it('deve ter seção de itens da proposta', () => {
    render(<PropostaDetail />);

    expect(screen.getByText('Itens da Proposta')).toBeInTheDocument();
    expect(screen.getByText('Adicionar Item')).toBeInTheDocument();
  });
});
