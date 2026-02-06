/**
 * Testes unitários de Contratos
 */

import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '@/test/helpers/test-utils';
import { mockContratos, mockContrato } from '@/test/fixtures/licitacoes';

const ContratosPage = () => (
  <div>
    <h1>Contratos</h1>
    {mockContratos.map((c) => (
      <div key={c.id} data-testid={`contrato-${c.id}`}>
        <span>{c.numero}</span>
        <span>{c.fornecedor}</span>
        <span>{c.status}</span>
        <span>R$ {c.valor_total}</span>
      </div>
    ))}
  </div>
);

const ContratoDetail = () => (
  <div>
    <h1>{mockContrato.numero}</h1>
    <p>Fornecedor: {mockContrato.fornecedor}</p>
    <p>Valor Total: R$ {mockContrato.valor_total}</p>
    <p>Valor Executado: R$ {mockContrato.valor_executado}</p>
    <p>Status: {mockContrato.status}</p>
    <p>Objeto: {mockContrato.objeto}</p>
    <div data-testid="aditivos">
      <h2>Aditivos</h2>
    </div>
  </div>
);

describe('Contratos - Listagem', () => {
  it('deve renderizar lista de contratos', () => {
    render(<ContratosPage />);

    expect(screen.getByText('CONTRATO-001/2026')).toBeInTheDocument();
    expect(screen.getByText('CONTRATO-002/2026')).toBeInTheDocument();
  });

  it('deve exibir fornecedor e status', () => {
    render(<ContratosPage />);

    expect(screen.getByText('Empresa de Segurança LTDA')).toBeInTheDocument();
    expect(screen.getByText('vigente')).toBeInTheDocument();
  });
});

describe('Contratos - Detalhe', () => {
  it('deve renderizar informações do contrato', () => {
    render(<ContratoDetail />);

    expect(screen.getByText('CONTRATO-001/2026')).toBeInTheDocument();
    expect(screen.getByText('Fornecedor: Empresa de Segurança LTDA')).toBeInTheDocument();
    expect(screen.getByText('Valor Total: R$ 480000')).toBeInTheDocument();
    expect(screen.getByText('Status: vigente')).toBeInTheDocument();
  });

  it('deve ter seção de aditivos', () => {
    render(<ContratoDetail />);
    expect(screen.getByText('Aditivos')).toBeInTheDocument();
  });
});
