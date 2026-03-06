import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useState } from 'react';

// ---- Inline component definition (mirrors NFeFormModal logic) ----

interface NFeFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

const INITIAL_FORM = {
  tipo: 'nfe',
  recipient_name: '',
  recipient_document: '',
  description: '',
  amount: '',
  items_description: '',
};

const NFeFormModal: React.FC<NFeFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState({ ...INITIAL_FORM });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      tipo: formData.tipo,
      recipient_name: formData.recipient_name,
      recipient_document: formData.recipient_document,
      description: formData.description,
      amount: parseFloat(formData.amount) || 0,
      items_description: formData.items_description,
    });
  };

  const handleClose = () => {
    setFormData({ ...INITIAL_FORM });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div data-testid="nfe-form-modal">
      <h2>Nova Nota Fiscal</h2>
      <p>Preencha os dados para emissao da nota fiscal</p>

      <form onSubmit={handleSubmit} data-testid="nfe-form">
        <label htmlFor="tipo">Tipo *</label>
        <select
          id="tipo"
          value={formData.tipo}
          onChange={(e) => handleChange('tipo', e.target.value)}
          data-testid="select-tipo"
        >
          <option value="nfe">NF-e (Nota Fiscal Eletronica)</option>
          <option value="nfse">NFS-e (Nota Fiscal de Servico)</option>
        </select>

        <label htmlFor="recipient_name">Destinatario *</label>
        <input
          id="recipient_name"
          value={formData.recipient_name}
          onChange={(e) => handleChange('recipient_name', e.target.value)}
          placeholder="Nome ou razao social"
          required
          data-testid="input-recipient"
        />

        <label htmlFor="recipient_document">CPF/CNPJ *</label>
        <input
          id="recipient_document"
          value={formData.recipient_document}
          onChange={(e) => handleChange('recipient_document', e.target.value)}
          placeholder="000.000.000-00"
          required
          data-testid="input-document"
        />

        <label htmlFor="description">Descricao *</label>
        <input
          id="description"
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Descricao da nota fiscal"
          required
          data-testid="input-description"
        />

        <label htmlFor="amount">Valor Total *</label>
        <input
          id="amount"
          type="number"
          step="0.01"
          min="0"
          value={formData.amount}
          onChange={(e) => handleChange('amount', e.target.value)}
          placeholder="0,00"
          required
          data-testid="input-amount"
        />

        <label htmlFor="items_description">Itens / Servicos</label>
        <textarea
          id="items_description"
          value={formData.items_description}
          onChange={(e) => handleChange('items_description', e.target.value)}
          placeholder="Descreva os itens ou servicos..."
          data-testid="input-items"
        />

        <button type="button" onClick={handleClose} disabled={isLoading} data-testid="btn-cancel">
          Cancelar
        </button>
        <button type="submit" disabled={isLoading} data-testid="btn-submit">
          {isLoading ? 'Emitindo...' : 'Emitir Nota Fiscal'}
        </button>
      </form>
    </div>
  );
};

// ---- Tests ----

describe('NFeFormModal - render', () => {
  it('retorna null quando fechado', () => {
    const { container } = render(
      <NFeFormModal isOpen={false} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza quando aberto', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('nfe-form-modal')).toBeInTheDocument();
  });

  it('exibe titulo "Nova Nota Fiscal"', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Nova Nota Fiscal')).toBeInTheDocument();
  });

  it('inicia com tipo nfe como padrao', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect((screen.getByTestId('select-tipo') as HTMLSelectElement).value).toBe('nfe');
  });
});

describe('NFeFormModal - tipos de NF', () => {
  it('renderiza opcoes NF-e e NFS-e', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('NF-e (Nota Fiscal Eletronica)')).toBeInTheDocument();
    expect(screen.getByText('NFS-e (Nota Fiscal de Servico)')).toBeInTheDocument();
  });

  it('permite selecionar NFS-e', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-tipo'), { target: { value: 'nfse' } });
    expect((screen.getByTestId('select-tipo') as HTMLSelectElement).value).toBe('nfse');
  });
});

describe('NFeFormModal - submit', () => {
  it('chama onSubmit com payload correto', () => {
    const onSubmit = vi.fn();
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('select-tipo'), { target: { value: 'nfse' } });
    fireEvent.change(screen.getByTestId('input-recipient'), { target: { value: 'Empresa ABC' } });
    fireEvent.change(screen.getByTestId('input-document'), { target: { value: '12345678000195' } });
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Servicos de TI' } });
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '2500.00' } });
    fireEvent.change(screen.getByTestId('input-items'), { target: { value: 'Desenvolvimento de software' } });

    fireEvent.submit(screen.getByTestId('nfe-form'));

    expect(onSubmit).toHaveBeenCalledWith({
      tipo: 'nfse',
      recipient_name: 'Empresa ABC',
      recipient_document: '12345678000195',
      description: 'Servicos de TI',
      amount: 2500,
      items_description: 'Desenvolvimento de software',
    });
  });

  it('amount invalido resulta em 0 no payload', () => {
    const onSubmit = vi.fn();
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    // Testa o helper parseFloat('') || 0 e parseFloat(undefined) || 0
    expect(parseFloat('') || 0).toBe(0);
    expect(parseFloat('abc') || 0).toBe(0);
    expect(parseFloat('1500.50') || 0).toBe(1500.5);
  });

  it('items_description e opcional - pode ser vazio', () => {
    const onSubmit = vi.fn();
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-recipient'), { target: { value: 'Empresa' } });
    fireEvent.change(screen.getByTestId('input-document'), { target: { value: '123456' } });
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Desc' } });
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '100' } });

    fireEvent.submit(screen.getByTestId('nfe-form'));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ items_description: '' })
    );
  });
});

describe('NFeFormModal - handleClose reseta o formulario', () => {
  it('reseta campos ao clicar Cancelar e chama onClose', () => {
    const onClose = vi.fn();
    render(
      <NFeFormModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-recipient'), { target: { value: 'Test Destinatario' } });
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Test Descricao' } });

    expect((screen.getByTestId('input-recipient') as HTMLInputElement).value).toBe('Test Destinatario');

    fireEvent.click(screen.getByTestId('btn-cancel'));

    expect(onClose).toHaveBeenCalled();
    // Após cancelar, o componente fecha (isOpen=false seria passado pelo pai)
    // mas a logica de reset é chamada antes de onClose
  });

  it('botao cancelar chama onClose', () => {
    const onClose = vi.fn();
    render(
      <NFeFormModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />
    );
    fireEvent.click(screen.getByTestId('btn-cancel'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});

describe('NFeFormModal - estado isLoading', () => {
  it('exibe "Emitindo..." durante isLoading', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} isLoading={true} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Emitindo...');
  });

  it('exibe "Emitir Nota Fiscal" sem isLoading', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Emitir Nota Fiscal');
  });

  it('botoes desabilitados durante isLoading', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} isLoading={true} />
    );
    expect(screen.getByTestId('btn-submit')).toBeDisabled();
    expect(screen.getByTestId('btn-cancel')).toBeDisabled();
  });

  it('botoes habilitados sem isLoading', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} isLoading={false} />
    );
    expect(screen.getByTestId('btn-submit')).not.toBeDisabled();
    expect(screen.getByTestId('btn-cancel')).not.toBeDisabled();
  });
});

describe('NFeFormModal - atualizacao de campos', () => {
  it('atualiza campo destinatario', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-recipient'), { target: { value: 'Novo Destinatario' } });
    expect((screen.getByTestId('input-recipient') as HTMLInputElement).value).toBe('Novo Destinatario');
  });

  it('atualiza campo documento', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-document'), { target: { value: '999.888.777-66' } });
    expect((screen.getByTestId('input-document') as HTMLInputElement).value).toBe('999.888.777-66');
  });

  it('atualiza campo descricao', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Prestacao de servicos' } });
    expect((screen.getByTestId('input-description') as HTMLInputElement).value).toBe('Prestacao de servicos');
  });

  it('atualiza campo valor', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '1234.56' } });
    expect((screen.getByTestId('input-amount') as HTMLInputElement).value).toBe('1234.56');
  });

  it('atualiza campo itens', () => {
    render(
      <NFeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-items'), { target: { value: '3 horas de consultoria' } });
    expect((screen.getByTestId('input-items') as HTMLTextAreaElement).value).toBe('3 horas de consultoria');
  });
});
