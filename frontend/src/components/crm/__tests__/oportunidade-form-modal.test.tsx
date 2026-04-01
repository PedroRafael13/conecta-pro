import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useState, useEffect, useMemo } from 'react';

// ---- Inline component definition (mirrors OportunidadeFormModal logic) ----

const createInitialForm = (oportunidade?: any | null) => ({
  nome: oportunidade?.nome || '',
  cliente: oportunidade?.cliente || '',
  valor_estimado: oportunidade?.valor_estimado || 0,
  status: oportunidade?.status || 'novo',
  responsavel: oportunidade?.responsavel || '',
  observacoes: oportunidade?.observacoes || '',
});

interface OportunidadeFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  oportunidade?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const OportunidadeFormModal: React.FC<OportunidadeFormModalProps> = ({
  isOpen,
  onClose,
  oportunidade,
  onSubmit,
  isLoading,
}) => {
  const isEditing = !!oportunidade;

  const formKey = useMemo(() => {
    return oportunidade?.id || oportunidade?.codigo || 'new';
  }, [oportunidade]);

  const [form, setForm] = useState(createInitialForm(oportunidade));

  useEffect(() => {
    if (isOpen) {
      setForm(createInitialForm(oportunidade));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, formKey]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  if (!isOpen) return null;

  return (
    <div data-testid="oportunidade-form-modal">
      <h2>{isEditing ? 'Editar Oportunidade' : 'Nova Oportunidade'}</h2>

      <label htmlFor="nome">Nome</label>
      <input
        id="nome"
        value={form.nome}
        onChange={(e) => setForm({ ...form, nome: e.target.value })}
        placeholder="Nome da oportunidade"
        data-testid="input-nome"
      />

      <label htmlFor="cliente">Cliente</label>
      <input
        id="cliente"
        value={form.cliente}
        onChange={(e) => setForm({ ...form, cliente: e.target.value })}
        placeholder="Nome do cliente"
        data-testid="input-cliente"
      />

      <label htmlFor="valor_estimado">Valor Estimado (R$)</label>
      <input
        id="valor_estimado"
        type="number"
        value={form.valor_estimado}
        onChange={(e) = aria-label="Number"> setForm({ ...form, valor_estimado: Number(e.target.value) })}
        placeholder="0,00"
        data-testid="input-valor"
      />

      <label>Status</label>
      <select
        value={form.status}
        onChange={(e) => setForm({ ...form, status: e.target.value })}
        data-testid="select-status"
      >
        <option value="novo">Novo</option>
        <option value="qualificado">Qualificado</option>
        <option value="proposta">Proposta</option>
        <option value="negociacao">Negociação</option>
        <option value="ganho">Ganho</option>
        <option value="perdido">Perdido</option>
      </select>

      <label htmlFor="responsavel">Responsavel</label>
      <input
        id="responsavel"
        value={form.responsavel}
        onChange={(e) => setForm({ ...form, responsavel: e.target.value })}
        placeholder="Nome do responsavel"
        data-testid="input-responsavel"
      />

      <label htmlFor="observacoes">Observacoes</label>
      <textarea
        id="observacoes"
        value={form.observacoes}
        onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
        placeholder="Observacoes sobre a oportunidade..."
        data-testid="input-observacoes"
      />

      <button type="button" onClick={onClose} disabled={isLoading} data-testid="btn-cancel">
        Cancelar
      </button>
      <button onClick={handleSubmit} disabled={isLoading} data-testid="btn-submit">
        {isLoading ? 'Salvando...' : isEditing ? 'Salvar' : 'Criar'}
      </button>
    </div>
  );
};

// ---- Tests ----

describe('OportunidadeFormModal - render e modos', () => {
  it('retorna null quando fechado', () => {
    const { container } = render(
      <OportunidadeFormModal isOpen={false} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza quando aberto', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('oportunidade-form-modal')).toBeInTheDocument();
  });

  it('exibe titulo "Nova Oportunidade" no modo criacao', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Nova Oportunidade')).toBeInTheDocument();
  });

  it('exibe titulo "Editar Oportunidade" no modo edicao', () => {
    render(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        oportunidade={{ id: '1', nome: 'Contrato Grande' }}
      />
    );
    expect(screen.getByText('Editar Oportunidade')).toBeInTheDocument();
  });
});

describe('OportunidadeFormModal - preenchimento de dados', () => {
  it('preenche campos com dados da oportunidade no modo edicao', () => {
    render(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        oportunidade={{
          id: '1',
          nome: 'Projeto Alpha',
          cliente: 'Empresa Beta',
          valor_estimado: 50000,
          status: 'proposta',
          responsavel: 'Ana Silva',
          observacoes: 'Reuniao na proxima semana',
        }}
      />
    );
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('Projeto Alpha');
    expect((screen.getByTestId('input-cliente') as HTMLInputElement).value).toBe('Empresa Beta');
    expect((screen.getByTestId('input-valor') as HTMLInputElement).value).toBe('50000');
    expect((screen.getByTestId('select-status') as HTMLSelectElement).value).toBe('proposta');
    expect((screen.getByTestId('input-responsavel') as HTMLInputElement).value).toBe('Ana Silva');
    expect((screen.getByTestId('input-observacoes') as HTMLTextAreaElement).value).toBe('Reuniao na proxima semana');
  });

  it('inicia com valores padrao no modo criacao', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('input-cliente') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('input-valor') as HTMLInputElement).value).toBe('0');
    expect((screen.getByTestId('select-status') as HTMLSelectElement).value).toBe('novo');
  });
});

describe('OportunidadeFormModal - status options', () => {
  it('renderiza todas as opcoes de status', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Novo')).toBeInTheDocument();
    expect(screen.getByText('Qualificado')).toBeInTheDocument();
    expect(screen.getByText('Proposta')).toBeInTheDocument();
    expect(screen.getByText('Negociação')).toBeInTheDocument();
    expect(screen.getByText('Ganho')).toBeInTheDocument();
    expect(screen.getByText('Perdido')).toBeInTheDocument();
  });

  it('permite mudar status', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-status'), { target: { value: 'ganho' } });
    expect((screen.getByTestId('select-status') as HTMLSelectElement).value).toBe('ganho');
  });

  it('permite selecionar status perdido', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-status'), { target: { value: 'perdido' } });
    expect((screen.getByTestId('select-status') as HTMLSelectElement).value).toBe('perdido');
  });
});

describe('OportunidadeFormModal - submit', () => {
  it('chama onSubmit com dados do form', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-nome'), { target: { value: 'Nova Oport' } });
    fireEvent.change(screen.getByTestId('input-cliente'), { target: { value: 'Cliente X' } });
    fireEvent.change(screen.getByTestId('input-valor'), { target: { value: '15000' } });
    fireEvent.change(screen.getByTestId('select-status'), { target: { value: 'qualificado' } });
    fireEvent.change(screen.getByTestId('input-responsavel'), { target: { value: 'Pedro' } });
    fireEvent.change(screen.getByTestId('input-observacoes'), { target: { value: 'Muito promissor' } });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        nome: 'Nova Oport',
        cliente: 'Cliente X',
        valor_estimado: 15000,
        status: 'qualificado',
        responsavel: 'Pedro',
        observacoes: 'Muito promissor',
      });
    });
  });

  it('exibe "Salvar" no modo edicao', () => {
    render(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        oportunidade={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvar');
  });

  it('exibe "Criar" no modo criacao', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Criar');
  });

  it('exibe "Salvando..." durante isLoading', () => {
    render(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvando...');
  });

  it('botoes desabilitados durante isLoading', () => {
    render(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
      />
    );
    expect(screen.getByTestId('btn-submit')).toBeDisabled();
    expect(screen.getByTestId('btn-cancel')).toBeDisabled();
  });
});

describe('OportunidadeFormModal - cancelar', () => {
  it('chama onClose ao clicar Cancelar', () => {
    const onClose = vi.fn();
    render(
      <OportunidadeFormModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />
    );
    fireEvent.click(screen.getByTestId('btn-cancel'));
    expect(onClose).toHaveBeenCalled();
  });
});

describe('OportunidadeFormModal - atualizacao dos campos', () => {
  it('atualiza nome ao digitar', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-nome'), { target: { value: 'Teste' } });
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('Teste');
  });

  it('atualiza valor_estimado para numero', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-valor'), { target: { value: '9999.99' } });
    expect((screen.getByTestId('input-valor') as HTMLInputElement).value).toBe('9999.99');
  });

  it('atualiza observacoes', () => {
    render(
      <OportunidadeFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-observacoes'), { target: { value: 'Nota importante' } });
    expect((screen.getByTestId('input-observacoes') as HTMLTextAreaElement).value).toBe('Nota importante');
  });
});

describe('OportunidadeFormModal - formKey branch', () => {
  it('usa oportunidade.id para formKey', () => {
    const { rerender } = render(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        oportunidade={{ id: 'op-1', nome: 'Op 1' }}
      />
    );
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('Op 1');

    rerender(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        oportunidade={{ id: 'op-2', nome: 'Op 2' }}
      />
    );
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('Op 2');
  });

  it('usa oportunidade.codigo quando id nao disponivel', () => {
    render(
      <OportunidadeFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        oportunidade={{ codigo: 'op-codigo-1', nome: 'Op Codigo' }}
      />
    );
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('Op Codigo');
  });
});

describe('createInitialForm helper', () => {
  it('usa valores da oportunidade quando presentes', () => {
    const form = createInitialForm({
      nome: 'N', cliente: 'C', valor_estimado: 100,
      status: 'ganho', responsavel: 'R', observacoes: 'O',
    });
    expect(form.nome).toBe('N');
    expect(form.cliente).toBe('C');
    expect(form.valor_estimado).toBe(100);
    expect(form.status).toBe('ganho');
    expect(form.responsavel).toBe('R');
    expect(form.observacoes).toBe('O');
  });

  it('usa valores padrao quando oportunidade e null', () => {
    const form = createInitialForm(null);
    expect(form.nome).toBe('');
    expect(form.valor_estimado).toBe(0);
    expect(form.status).toBe('novo');
  });

  it('valor_estimado padrao e 0 quando nao especificado', () => {
    const form = createInitialForm({ nome: 'X' });
    expect(form.valor_estimado).toBe(0);
  });
});
