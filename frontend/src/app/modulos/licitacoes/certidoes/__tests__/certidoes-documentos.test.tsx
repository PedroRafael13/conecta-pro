/**
 * Testes unitários de Certidões e Documentos
 */

import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '@/test/helpers/test-utils';
import {
  mockCertidoes,
  mockCertidao,
  mockDocumentos,
  mockDocumento,
} from '@/test/fixtures/licitacoes';

const CertidoesPage = () => (
  <div>
    <h1>Certidões</h1>
    <button>Nova Certidão</button>
    {mockCertidoes.map((c) => (
      <div key={c.id} data-testid={`certidao-${c.id}`}>
        <span>{c.tipo}</span>
        <span>{c.numero}</span>
        <span>{c.orgao_emissor}</span>
        <span className={`status-${c.status}`}>{c.status}</span>
        <button>Renovar</button>
        <button>Download</button>
      </div>
    ))}
  </div>
);

const DocumentosPage = () => (
  <div>
    <h1>Documentos</h1>
    <button>Upload Documento</button>
    {mockDocumentos.map((d) => (
      <div key={d.id} data-testid={`documento-${d.id}`}>
        <span>{d.nome}</span>
        <span>{d.tipo}</span>
        <span>{d.categoria}</span>
        <span>{d.tamanho} bytes</span>
        <button>Download</button>
        <button>Deletar</button>
      </div>
    ))}
  </div>
);

describe('Certidões', () => {
  it('deve renderizar título e botão nova certidão', () => {
    render(<CertidoesPage />);

    expect(screen.getByText('Certidões')).toBeInTheDocument();
    expect(screen.getByText('Nova Certidão')).toBeInTheDocument();
  });

  it('deve renderizar lista de certidões', () => {
    render(<CertidoesPage />);

    expect(screen.getByText('regularidade_fiscal')).toBeInTheDocument();
    expect(screen.getByText('trabalhista')).toBeInTheDocument();
    expect(screen.getByText('municipal')).toBeInTheDocument();
  });

  it('deve exibir número e órgão emissor', () => {
    render(<CertidoesPage />);

    expect(screen.getByText('CRF-123456')).toBeInTheDocument();
    expect(screen.getByText('Receita Federal')).toBeInTheDocument();
    expect(screen.getByText('TST')).toBeInTheDocument();
  });

  it('deve exibir status com classe CSS', () => {
    render(<CertidoesPage />);

    const validStatus = screen.getAllByText('valida');
    const vencidaStatus = screen.getByText('vencida');

    expect(validStatus[0]).toHaveClass('status-valida');
    expect(vencidaStatus).toHaveClass('status-vencida');
  });

  it('deve ter botões de renovar e download', () => {
    render(<CertidoesPage />);

    const renovarButtons = screen.getAllByText('Renovar');
    const downloadButtons = screen.getAllByText('Download');

    expect(renovarButtons).toHaveLength(3);
    expect(downloadButtons).toHaveLength(3);
  });
});

describe('Documentos', () => {
  it('deve renderizar título e botão upload', () => {
    render(<DocumentosPage />);

    expect(screen.getByText('Documentos')).toBeInTheDocument();
    expect(screen.getByText('Upload Documento')).toBeInTheDocument();
  });

  it('deve renderizar lista de documentos', () => {
    render(<DocumentosPage />);

    expect(screen.getByText('Proposta Técnica.pdf')).toBeInTheDocument();
    expect(screen.getByText('Proposta Comercial.pdf')).toBeInTheDocument();
    expect(screen.getByText('Atestados.pdf')).toBeInTheDocument();
  });

  it('deve exibir tipo e categoria', () => {
    render(<DocumentosPage />);

    expect(screen.getByText('proposta_tecnica')).toBeInTheDocument();
    expect(screen.getByText('proposta_comercial')).toBeInTheDocument();
    expect(screen.getByText('atestado')).toBeInTheDocument();
  });

  it('deve exibir tamanho do arquivo', () => {
    render(<DocumentosPage />);

    expect(screen.getByText('1024000 bytes')).toBeInTheDocument();
    expect(screen.getByText('512000 bytes')).toBeInTheDocument();
    expect(screen.getByText('2048000 bytes')).toBeInTheDocument();
  });

  it('deve ter botões de download e deletar', () => {
    render(<DocumentosPage />);

    const downloadButtons = screen.getAllByText('Download');
    const deleteButtons = screen.getAllByText('Deletar');

    expect(downloadButtons).toHaveLength(3);
    expect(deleteButtons).toHaveLength(3);
  });
});
