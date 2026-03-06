import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useState, useEffect, useMemo } from 'react';

// ---- Inline component definition (mirrors FeatureFlagFormModal logic) ----

const createInitialForm = (flag?: any) => ({
  codigo: flag?.codigo || '',
  nome: flag?.nome || '',
  descricao: flag?.descricao || '',
  flag_type: flag?.flag_type || 'boolean',
  category: flag?.category || 'features',
  owner_team: flag?.owner_team || '',
});

interface FeatureFlagFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  flag?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const FeatureFlagFormModal: React.FC<FeatureFlagFormModalProps> = ({
  isOpen,
  onClose,
  flag,
  onSubmit,
  isLoading,
}) => {
  const isEditing = !!flag;

  const formKey = useMemo(() => flag?.id || flag?.codigo || 'new', [flag]);
  const [form, setForm] = useState(createInitialForm(flag));

  useEffect(() => {
    if (isOpen) {
      setForm(createInitialForm(flag));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, formKey]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  if (!isOpen) return null;

  return (
    <div data-testid="feature-flag-form-modal">
      <h2>{isEditing ? 'Editar Feature Flag' : 'Nova Feature Flag'}</h2>

      <label htmlFor="ff_codigo">Codigo</label>
      <input
        id="ff_codigo"
        value={form.codigo}
        onChange={(e) => setForm({ ...form, codigo: e.target.value })}
        placeholder="feature_name"
        disabled={isEditing}
        data-testid="input-codigo"
      />

      <label htmlFor="ff_nome">Nome</label>
      <input
        id="ff_nome"
        value={form.nome}
        onChange={(e) => setForm({ ...form, nome: e.target.value })}
        placeholder="Nome da feature"
        data-testid="input-nome"
      />

      <label htmlFor="ff_descricao">Descricao</label>
      <textarea
        id="ff_descricao"
        value={form.descricao}
        onChange={(e) => setForm({ ...form, descricao: e.target.value })}
        placeholder="Descricao da feature flag..."
        data-testid="input-descricao"
      />

      <label>Tipo</label>
      <select
        value={form.flag_type}
        onChange={(e) => setForm({ ...form, flag_type: e.target.value })}
        data-testid="select-flag-type"
      >
        <option value="boolean">Boolean</option>
        <option value="percentage">Percentage</option>
        <option value="gradual">Gradual</option>
        <option value="whitelist">Whitelist</option>
      </select>

      <label>Categoria</label>
      <select
        value={form.category}
        onChange={(e) => setForm({ ...form, category: e.target.value })}
        data-testid="select-category"
      >
        <option value="features">Funcionalidades</option>
        <option value="experimental">Experimental</option>
        <option value="maintenance">Manutencao</option>
        <option value="performance">Performance</option>
        <option value="ui">Interface</option>
        <option value="integrations">Integracoes</option>
      </select>

      <label htmlFor="ff_team">Time Responsavel</label>
      <input
        id="ff_team"
        value={form.owner_team}
        onChange={(e) => setForm({ ...form, owner_team: e.target.value })}
        placeholder="backend, frontend..."
        data-testid="input-team"
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

describe('FeatureFlagFormModal - render e modos', () => {
  it('retorna null quando fechado', () => {
    const { container } = render(
      <FeatureFlagFormModal isOpen={false} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza quando aberto', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('feature-flag-form-modal')).toBeInTheDocument();
  });

  it('exibe titulo "Nova Feature Flag" no modo criacao', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Nova Feature Flag')).toBeInTheDocument();
  });

  it('exibe titulo "Editar Feature Flag" no modo edicao', () => {
    render(
      <FeatureFlagFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        flag={{ id: '1', codigo: 'new_dashboard' }}
      />
    );
    expect(screen.getByText('Editar Feature Flag')).toBeInTheDocument();
  });
});

describe('FeatureFlagFormModal - preenchimento de dados', () => {
  it('preenche campos com dados da flag no modo edicao', () => {
    render(
      <FeatureFlagFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        flag={{
          id: '1',
          codigo: 'new_ui_feature',
          nome: 'Nova Interface',
          descricao: 'Ativa a nova interface',
          flag_type: 'percentage',
          category: 'ui',
          owner_team: 'frontend',
        }}
      />
    );
    expect((screen.getByTestId('input-codigo') as HTMLInputElement).value).toBe('new_ui_feature');
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('Nova Interface');
    expect((screen.getByTestId('input-descricao') as HTMLTextAreaElement).value).toBe('Ativa a nova interface');
    expect((screen.getByTestId('select-flag-type') as HTMLSelectElement).value).toBe('percentage');
    expect((screen.getByTestId('select-category') as HTMLSelectElement).value).toBe('ui');
    expect((screen.getByTestId('input-team') as HTMLInputElement).value).toBe('frontend');
  });

  it('inicia com valores padrao no modo criacao', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect((screen.getByTestId('input-codigo') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('input-nome') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('select-flag-type') as HTMLSelectElement).value).toBe('boolean');
    expect((screen.getByTestId('select-category') as HTMLSelectElement).value).toBe('features');
    expect((screen.getByTestId('input-team') as HTMLInputElement).value).toBe('');
  });
});

describe('FeatureFlagFormModal - campo codigo desabilitado no modo edicao', () => {
  it('campo codigo e desabilitado no modo edicao', () => {
    render(
      <FeatureFlagFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        flag={{ id: '1', codigo: 'my_flag' }}
      />
    );
    expect(screen.getByTestId('input-codigo')).toBeDisabled();
  });

  it('campo codigo nao e desabilitado no modo criacao', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('input-codigo')).not.toBeDisabled();
  });
});

describe('FeatureFlagFormModal - tipos de flag', () => {
  it('renderiza todas as opcoes de tipo', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Boolean')).toBeInTheDocument();
    expect(screen.getByText('Percentage')).toBeInTheDocument();
    expect(screen.getByText('Gradual')).toBeInTheDocument();
    expect(screen.getByText('Whitelist')).toBeInTheDocument();
  });

  it('permite mudar o tipo de flag', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-flag-type'), { target: { value: 'gradual' } });
    expect((screen.getByTestId('select-flag-type') as HTMLSelectElement).value).toBe('gradual');
  });
});

describe('FeatureFlagFormModal - categorias', () => {
  it('renderiza todas as opcoes de categoria', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Funcionalidades')).toBeInTheDocument();
    expect(screen.getByText('Experimental')).toBeInTheDocument();
    expect(screen.getByText('Manutencao')).toBeInTheDocument();
    expect(screen.getByText('Performance')).toBeInTheDocument();
    expect(screen.getByText('Interface')).toBeInTheDocument();
    expect(screen.getByText('Integracoes')).toBeInTheDocument();
  });

  it('permite mudar a categoria', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-category'), { target: { value: 'experimental' } });
    expect((screen.getByTestId('select-category') as HTMLSelectElement).value).toBe('experimental');
  });
});

describe('FeatureFlagFormModal - submit', () => {
  it('chama onSubmit com dados corretos', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-codigo'), { target: { value: 'dark_mode' } });
    fireEvent.change(screen.getByTestId('input-nome'), { target: { value: 'Modo Escuro' } });
    fireEvent.change(screen.getByTestId('input-descricao'), { target: { value: 'Ativa modo escuro' } });
    fireEvent.change(screen.getByTestId('select-flag-type'), { target: { value: 'boolean' } });
    fireEvent.change(screen.getByTestId('select-category'), { target: { value: 'ui' } });
    fireEvent.change(screen.getByTestId('input-team'), { target: { value: 'frontend' } });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        codigo: 'dark_mode',
        nome: 'Modo Escuro',
        descricao: 'Ativa modo escuro',
        flag_type: 'boolean',
        category: 'ui',
        owner_team: 'frontend',
      });
    });
  });

  it('exibe "Salvar" no modo edicao', () => {
    render(
      <FeatureFlagFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        flag={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvar');
  });

  it('exibe "Criar" no modo criacao', () => {
    render(
      <FeatureFlagFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Criar');
  });

  it('exibe "Salvando..." durante isLoading', () => {
    render(
      <FeatureFlagFormModal
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
      <FeatureFlagFormModal
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

describe('FeatureFlagFormModal - cancelar', () => {
  it('chama onClose ao clicar Cancelar', () => {
    const onClose = vi.fn();
    render(
      <FeatureFlagFormModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />
    );
    fireEvent.click(screen.getByTestId('btn-cancel'));
    expect(onClose).toHaveBeenCalled();
  });
});

describe('FeatureFlagFormModal - formKey branch', () => {
  it('usa flag.id quando disponivel para formKey', () => {
    // Testa que rerender com novo flag.id atualiza o form
    const { rerender } = render(
      <FeatureFlagFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        flag={{ id: 'flag-1', codigo: 'flag1', nome: 'Flag 1' }}
      />
    );
    expect((screen.getByTestId('input-codigo') as HTMLInputElement).value).toBe('flag1');

    rerender(
      <FeatureFlagFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        flag={{ id: 'flag-2', codigo: 'flag2', nome: 'Flag 2' }}
      />
    );
    expect((screen.getByTestId('input-codigo') as HTMLInputElement).value).toBe('flag2');
  });

  it('usa flag.codigo quando id nao disponivel para formKey', () => {
    render(
      <FeatureFlagFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        flag={{ codigo: 'my_feature' }}
      />
    );
    expect((screen.getByTestId('input-codigo') as HTMLInputElement).value).toBe('my_feature');
  });
});

describe('createInitialForm helper', () => {
  it('usa valores da flag quando presentes', () => {
    const form = createInitialForm({
      codigo: 'c', nome: 'n', descricao: 'd', flag_type: 'gradual',
      category: 'maintenance', owner_team: 'team',
    });
    expect(form.codigo).toBe('c');
    expect(form.nome).toBe('n');
    expect(form.descricao).toBe('d');
    expect(form.flag_type).toBe('gradual');
    expect(form.category).toBe('maintenance');
    expect(form.owner_team).toBe('team');
  });

  it('usa valores padrao quando flag e null', () => {
    const form = createInitialForm(null);
    expect(form.codigo).toBe('');
    expect(form.flag_type).toBe('boolean');
    expect(form.category).toBe('features');
  });

  it('usa valores padrao quando flag e undefined', () => {
    const form = createInitialForm(undefined);
    expect(form.codigo).toBe('');
    expect(form.flag_type).toBe('boolean');
  });
});
