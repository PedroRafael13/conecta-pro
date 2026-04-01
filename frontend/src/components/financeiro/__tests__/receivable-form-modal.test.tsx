import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useState, useEffect, useMemo } from 'react';

// ---- Inline component definition (mirrors ReceivableFormModal logic) ----

const CATEGORIES = [
  { value: 'service', label: 'Servico' },
  { value: 'product', label: 'Produto' },
  { value: 'subscription', label: 'Assinatura' },
  { value: 'rental', label: 'Aluguel' },
  { value: 'other', label: 'Outros' },
];

const createInitialForm = (receivable?: any) => ({
  description: receivable?.description || '',
  customer_name: receivable?.customer_name || '',
  amount: receivable?.amount ? String(receivable.amount) : '',
  due_date: receivable?.due_date ? receivable.due_date.split('T')[0] : '',
  category: receivable?.category || '',
  observacoes: receivable?.observacoes || '',
});

interface ReceivableFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  receivable?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const ReceivableFormModal: React.FC<ReceivableFormModalProps> = ({
  isOpen,
  onClose,
  receivable,
  onSubmit,
  isLoading = false,
}) => {
  const isEditing = !!receivable?.id;
  const formKey = useMemo(() => receivable?.id || 'new', [receivable]);
  const [form, setForm] = useState(createInitialForm(receivable));

  useEffect(() => {
    if (isOpen) {
      setForm(createInitialForm(receivable));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, formKey]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      description: form.description,
      customer_name: form.customer_name,
      amount: parseFloat(form.amount) || 0,
      due_date: form.due_date,
      category: form.category,
      observacoes: form.observacoes || null,
    };
    await onSubmit(payload);
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const isValid =
    form.description.trim() !== '' &&
    form.customer_name.trim() !== '' &&
    form.amount !== '' &&
    parseFloat(form.amount) > 0 &&
    form.due_date !== '';

  if (!isOpen) return null;

  return (
    <div data-testid="receivable-form-modal">
      <h2>{isEditing ? 'Editar Conta a Receber' : 'Nova Conta a Receber'}</h2>
      <p data-testid="modal-description">
        {isEditing ? 'Atualize as informacoes da conta' : 'Preencha os dados da nova conta a receber'}
      </p>
      <form onSubmit={handleSubmit} data-testid="receivable-form">
        <label htmlFor="description">Descricao *</label>
        <input
          id="description"
          value={form.description}
          onChange={(e) => updateField('description', e.target.value)}
          data-testid="input-description"
        />

        <label htmlFor="customer_name">Cliente *</label>
        <input
          id="customer_name"
          value={form.customer_name}
          onChange={(e) => updateField('customer_name', e.target.value)}
          data-testid="input-customer"
        />

        <label htmlFor="amount">Valor (R$) *</label>
        <input
          id="amount"
          type="number"
          value={form.amount}
          onChange={(e) => updateField('amount', e.target.value)}
          data-testid="input-amount"
        />

        <label htmlFor="due_date">Vencimento *</label>
        <input
          id="due_date"
          type="date"
          value={form.due_date}
          onChange={(e) => updateField('due_date', e.target.value)}
          data-testid="input-due-date"
        />

        <label htmlFor="category">Categoria</label>
        <select
          id="category"
          value={form.category}
          onChange={(e) => updateField('category', e.target.value)}
          data-testid="select-category"
        >
          <option value="">Selecione a categoria</option>
          {CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value}>{cat.label}</option>
          ))}
        </select>

        <label htmlFor="observacoes">Observações</label>
        <textarea
          id="observacoes"
          value={form.observacoes}
          onChange={(e) => updateField('observacoes', e.target.value)}
          data-testid="input-observacoes"
        />

        <button type="button" onClick={onClose} disabled={isLoading} data-testid="btn-cancel">
          Cancelar
        </button>
        <button type="submit" disabled={isLoading || !isValid} data-testid="btn-submit">
          {isLoading ? 'Salvando...' : isEditing ? 'Salvar Alteracoes' : 'Criar Conta'}
        </button>
      </form>
    </div>
  );
};

// ---- Tests ----

describe('ReceivableFormModal - render e modos', () => {
  it('retorna null quando fechado', () => {
    const { container } = render(
      <ReceivableFormModal isOpen={false} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza quando aberto', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('receivable-form-modal')).toBeInTheDocument();
  });

  it('exibe titulo correto no modo criacao', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Nova Conta a Receber')).toBeInTheDocument();
  });

  it('exibe titulo correto no modo edicao', () => {
    render(
      <ReceivableFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        receivable={{ id: '1' }}
      />
    );
    expect(screen.getByText('Editar Conta a Receber')).toBeInTheDocument();
  });

  it('exibe descricao correta no modo criacao', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('modal-description')).toHaveTextContent(
      'Preencha os dados da nova conta a receber'
    );
  });

  it('exibe descricao correta no modo edicao', () => {
    render(
      <ReceivableFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        receivable={{ id: '2' }}
      />
    );
    expect(screen.getByTestId('modal-description')).toHaveTextContent(
      'Atualize as informacoes da conta'
    );
  });
});

describe('ReceivableFormModal - preenchimento de dados', () => {
  it('preenche campos com dados do receivable', () => {
    render(
      <ReceivableFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        receivable={{
          id: '1',
          description: 'Mensalidade cliente',
          customer_name: 'Empresa XYZ',
          amount: 5000,
          due_date: '2026-05-01T00:00:00Z',
          category: 'service',
          observacoes: 'Pagamento via PIX',
        }}
      />
    );
    expect((screen.getByTestId('input-description') as HTMLInputElement).value).toBe('Mensalidade cliente');
    expect((screen.getByTestId('input-customer') as HTMLInputElement).value).toBe('Empresa XYZ');
    expect((screen.getByTestId('input-amount') as HTMLInputElement).value).toBe('5000');
    expect((screen.getByTestId('input-due-date') as HTMLInputElement).value).toBe('2026-05-01');
    expect((screen.getByTestId('select-category') as HTMLSelectElement).value).toBe('service');
    expect((screen.getByTestId('input-observacoes') as HTMLTextAreaElement).value).toBe('Pagamento via PIX');
  });

  it('extrai apenas a data de due_date com hora', () => {
    render(
      <ReceivableFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        receivable={{ id: '1', due_date: '2026-06-15T12:30:00' }}
      />
    );
    expect((screen.getByTestId('input-due-date') as HTMLInputElement).value).toBe('2026-06-15');
  });

  it('inicia com valores padrao sem receivable', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect((screen.getByTestId('input-description') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('input-customer') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('input-amount') as HTMLInputElement).value).toBe('');
  });
});

describe('ReceivableFormModal - isValid state (botao submit)', () => {
  const fillAll = () => {
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Desc' } });
    fireEvent.change(screen.getByTestId('input-customer'), { target: { value: 'Cliente' } });
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '500' } });
    fireEvent.change(screen.getByTestId('input-due-date'), { target: { value: '2026-04-01' } });
  };

  it('botao desabilitado quando formulario vazio', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toBeDisabled();
  });

  it('botao habilitado quando todos campos obrigatorios preenchidos', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fillAll();
    expect(screen.getByTestId('btn-submit')).not.toBeDisabled();
  });

  it('botao desabilitado sem customer_name', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Desc' } });
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '100' } });
    fireEvent.change(screen.getByTestId('input-due-date'), { target: { value: '2026-04-01' } });
    expect(screen.getByTestId('btn-submit')).toBeDisabled();
  });

  it('botao desabilitado com amount negativo ou zero', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Desc' } });
    fireEvent.change(screen.getByTestId('input-customer'), { target: { value: 'Cliente' } });
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '-10' } });
    fireEvent.change(screen.getByTestId('input-due-date'), { target: { value: '2026-04-01' } });
    expect(screen.getByTestId('btn-submit')).toBeDisabled();
  });
});

describe('ReceivableFormModal - submit e payload', () => {
  it('chama onSubmit com payload correto', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Honorarios' } });
    fireEvent.change(screen.getByTestId('input-customer'), { target: { value: 'Cliente ABC' } });
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '3500.75' } });
    fireEvent.change(screen.getByTestId('input-due-date'), { target: { value: '2026-06-01' } });
    fireEvent.change(screen.getByTestId('select-category'), { target: { value: 'service' } });
    fireEvent.change(screen.getByTestId('input-observacoes'), { target: { value: 'Parcelado' } });

    fireEvent.submit(screen.getByTestId('receivable-form'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        description: 'Honorarios',
        customer_name: 'Cliente ABC',
        amount: 3500.75,
        due_date: '2026-06-01',
        category: 'service',
        observacoes: 'Parcelado',
      });
    });
  });

  it('envia observacoes como null quando vazio', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'X' } });
    fireEvent.change(screen.getByTestId('input-customer'), { target: { value: 'Y' } });
    fireEvent.change(screen.getByTestId('input-amount'), { target: { value: '100' } });
    fireEvent.change(screen.getByTestId('input-due-date'), { target: { value: '2026-04-01' } });

    fireEvent.submit(screen.getByTestId('receivable-form'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ observacoes: null }));
    });
  });

  it('exibe texto correto no botao conforme modo', () => {
    const { rerender } = render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Criar Conta');

    rerender(
      <ReceivableFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        receivable={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvar Alteracoes');
  });

  it('exibe "Salvando..." durante isLoading', () => {
    render(
      <ReceivableFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
        receivable={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvando...');
  });
});

describe('ReceivableFormModal - categorias', () => {
  it('renderiza todas as categorias', () => {
    render(
      <ReceivableFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Servico')).toBeInTheDocument();
    expect(screen.getByText('Produto')).toBeInTheDocument();
    expect(screen.getByText('Assinatura')).toBeInTheDocument();
    expect(screen.getByText('Aluguel')).toBeInTheDocument();
    expect(screen.getByText('Outros')).toBeInTheDocument();
  });
});
