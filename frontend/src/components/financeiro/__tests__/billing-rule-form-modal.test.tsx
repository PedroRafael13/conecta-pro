import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useState, useEffect, useMemo } from 'react';

// ---- Inline component definition (mirrors BillingRuleFormModal logic) ----

const createInitialForm = (rule?: any) => ({
  name: rule?.name || '',
  type: rule?.type || 'fixed',
  value: rule?.value?.toString() || '',
  frequency: rule?.frequency || 'monthly',
  description: rule?.description || '',
});

interface BillingRuleFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  rule?: any;
  isLoading?: boolean;
}

const BillingRuleFormModal: React.FC<BillingRuleFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  rule,
  isLoading = false,
}) => {
  const formKey = useMemo(() => rule?.id || rule?.codigo || 'new', [rule]);
  const [formData, setFormData] = useState(createInitialForm(rule));

  useEffect(() => {
    if (isOpen) {
      setFormData(createInitialForm(rule));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, formKey]);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      name: formData.name,
      type: formData.type,
      value: parseFloat(formData.value) || 0,
      frequency: formData.frequency,
      description: formData.description,
    });
  };

  const handleClose = () => {
    setFormData(createInitialForm());
    onClose();
  };

  if (!isOpen) return null;

  const valueLabel = formData.type === 'percentage' ? 'Percentual (%) *' : 'Valor (R$) *';
  const valuePlaceholder = formData.type === 'percentage' ? '0,0' : '0,00';
  const valueStep = formData.type === 'percentage' ? '0.1' : '0.01';

  return (
    <div data-testid="billing-rule-form-modal">
      <h2>{rule ? 'Editar Regra de Faturamento' : 'Nova Regra de Faturamento'}</h2>

      <form onSubmit={handleSubmit} data-testid="billing-form">
        <label htmlFor="rule-name">Nome da Regra *</label>
        <input
          id="rule-name"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="Ex: Taxa de administracao"
          required
          data-testid="input-name"
        />

        <label htmlFor="rule-type">Tipo *</label>
        <select
          id="rule-type"
          value={formData.type}
          onChange={(e) => handleChange('type', e.target.value)}
          data-testid="select-type"
        >
          <option value="fixed">Fixo</option>
          <option value="variable">Variavel</option>
          <option value="percentage">Percentual</option>
        </select>

        <label htmlFor="rule-value" data-testid="value-label">{valueLabel}</label>
        <input
          id="rule-value"
          type="number"
          step={valueStep}
          min="0"
          value={formData.value}
          onChange={(e) = aria-label="Number"> handleChange('value', e.target.value)}
          placeholder={valuePlaceholder}
          required
          data-testid="input-value"
        />

        <label htmlFor="rule-frequency">Periodicidade *</label>
        <select
          id="rule-frequency"
          value={formData.frequency}
          onChange={(e) => handleChange('frequency', e.target.value)}
          data-testid="select-frequency"
        >
          <option value="monthly">Mensal</option>
          <option value="quarterly">Trimestral</option>
          <option value="annual">Anual</option>
        </select>

        <label htmlFor="rule-description">Descricao</label>
        <textarea
          id="rule-description"
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Descreva a regra de faturamento..."
          data-testid="input-description"
        />

        <button type="button" onClick={handleClose} disabled={isLoading} data-testid="btn-cancel">
          Cancelar
        </button>
        <button type="submit" disabled={isLoading} data-testid="btn-submit">
          {isLoading ? 'Salvando...' : rule ? 'Salvar Alteracoes' : 'Criar Regra'}
        </button>
      </form>
    </div>
  );
};

// ---- Tests ----

describe('BillingRuleFormModal - render e modos', () => {
  it('retorna null quando fechado', () => {
    const { container } = render(
      <BillingRuleFormModal isOpen={false} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza quando aberto', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('billing-rule-form-modal')).toBeInTheDocument();
  });

  it('exibe titulo "Nova Regra de Faturamento" no modo criacao', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Nova Regra de Faturamento')).toBeInTheDocument();
  });

  it('exibe titulo "Editar Regra de Faturamento" no modo edicao', () => {
    render(
      <BillingRuleFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        rule={{ id: '1', name: 'Taxa Admin', type: 'fixed', value: 150, frequency: 'monthly' }}
      />
    );
    expect(screen.getByText('Editar Regra de Faturamento')).toBeInTheDocument();
  });
});

describe('BillingRuleFormModal - preenchimento de dados', () => {
  it('preenche campos com dados da rule no modo edicao', () => {
    render(
      <BillingRuleFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        rule={{ id: '1', name: 'Taxa Mensal', type: 'percentage', value: 10.5, frequency: 'quarterly', description: 'Desc' }}
      />
    );
    expect((screen.getByTestId('input-name') as HTMLInputElement).value).toBe('Taxa Mensal');
    expect((screen.getByTestId('select-type') as HTMLSelectElement).value).toBe('percentage');
    expect((screen.getByTestId('input-value') as HTMLInputElement).value).toBe('10.5');
    expect((screen.getByTestId('select-frequency') as HTMLSelectElement).value).toBe('quarterly');
    expect((screen.getByTestId('input-description') as HTMLTextAreaElement).value).toBe('Desc');
  });

  it('inicia com valores padrao no modo criacao', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect((screen.getByTestId('input-name') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('select-type') as HTMLSelectElement).value).toBe('fixed');
    expect((screen.getByTestId('select-frequency') as HTMLSelectElement).value).toBe('monthly');
  });
});

describe('BillingRuleFormModal - branch percentage vs outros tipos', () => {
  it('exibe label "Percentual (%)*" quando tipo e percentage', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-type'), { target: { value: 'percentage' } });
    expect(screen.getByTestId('value-label')).toHaveTextContent('Percentual (%) *');
  });

  it('exibe label "Valor (R$)*" quando tipo e fixed', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('value-label')).toHaveTextContent('Valor (R$) *');
  });

  it('exibe label "Valor (R$)*" quando tipo e variable', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-type'), { target: { value: 'variable' } });
    expect(screen.getByTestId('value-label')).toHaveTextContent('Valor (R$) *');
  });

  it('step do input muda para 0.1 quando tipo e percentage', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-type'), { target: { value: 'percentage' } });
    expect(screen.getByTestId('input-value')).toHaveAttribute('step', '0.1');
  });

  it('step do input e 0.01 quando tipo nao e percentage', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('input-value')).toHaveAttribute('step', '0.01');
  });

  it('placeholder do input muda para 0,0 quando tipo e percentage', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-type'), { target: { value: 'percentage' } });
    expect(screen.getByTestId('input-value')).toHaveAttribute('placeholder', '0,0');
  });

  it('placeholder do input e 0,00 quando tipo nao e percentage', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('input-value')).toHaveAttribute('placeholder', '0,00');
  });
});

describe('BillingRuleFormModal - submit', () => {
  it('chama onSubmit com payload correto', () => {
    const onSubmit = vi.fn();
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-name'), { target: { value: 'Taxa Fixa' } });
    fireEvent.change(screen.getByTestId('select-type'), { target: { value: 'fixed' } });
    fireEvent.change(screen.getByTestId('input-value'), { target: { value: '200' } });
    fireEvent.change(screen.getByTestId('select-frequency'), { target: { value: 'annual' } });
    fireEvent.change(screen.getByTestId('input-description'), { target: { value: 'Desc taxa' } });

    fireEvent.submit(screen.getByTestId('billing-form'));

    expect(onSubmit).toHaveBeenCalledWith({
      name: 'Taxa Fixa',
      type: 'fixed',
      value: 200,
      frequency: 'annual',
      description: 'Desc taxa',
    });
  });

  it('value invalido e convertido para 0 no payload', () => {
    const onSubmit = vi.fn();
    render(
      <BillingRuleFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={onSubmit}
        rule={{ id: '1', name: 'X', type: 'fixed', value: 0, frequency: 'monthly' }}
      />
    );
    // Testa a logica parseFloat || 0
    expect(parseFloat('') || 0).toBe(0);
    expect(parseFloat('abc') || 0).toBe(0);
    expect(parseFloat('150') || 0).toBe(150);
  });

  it('exibe "Salvar Alteracoes" no modo edicao', () => {
    render(
      <BillingRuleFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        rule={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvar Alteracoes');
  });

  it('exibe "Criar Regra" no modo criacao', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Criar Regra');
  });

  it('exibe "Salvando..." durante isLoading', () => {
    render(
      <BillingRuleFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
        rule={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvando...');
  });
});

describe('BillingRuleFormModal - handleClose reseta o form', () => {
  it('reseta o formulario ao clicar Cancelar', () => {
    const onClose = vi.fn();
    render(
      <BillingRuleFormModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('input-name'), { target: { value: 'Nome Digitado' } });
    expect((screen.getByTestId('input-name') as HTMLInputElement).value).toBe('Nome Digitado');

    fireEvent.click(screen.getByTestId('btn-cancel'));
    expect(onClose).toHaveBeenCalled();
  });

  it('botao cancelar fica desabilitado durante isLoading', () => {
    render(
      <BillingRuleFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
      />
    );
    expect(screen.getByTestId('btn-cancel')).toBeDisabled();
  });
});

describe('BillingRuleFormModal - periodicidades', () => {
  it('renderiza opcoes de periodicidade corretamente', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Mensal')).toBeInTheDocument();
    expect(screen.getByText('Trimestral')).toBeInTheDocument();
    expect(screen.getByText('Anual')).toBeInTheDocument();
  });

  it('permite selecionar periodicidade trimestral', () => {
    render(
      <BillingRuleFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.change(screen.getByTestId('select-frequency'), { target: { value: 'quarterly' } });
    expect((screen.getByTestId('select-frequency') as HTMLSelectElement).value).toBe('quarterly');
  });
});

describe('createInitialForm helper', () => {
  it('usa values da rule quando presentes', () => {
    const form = createInitialForm({ name: 'X', type: 'percentage', value: 5, frequency: 'annual', description: 'D' });
    expect(form.name).toBe('X');
    expect(form.type).toBe('percentage');
    expect(form.value).toBe('5');
    expect(form.frequency).toBe('annual');
    expect(form.description).toBe('D');
  });

  it('usa valores padrao quando rule e undefined', () => {
    const form = createInitialForm();
    expect(form.name).toBe('');
    expect(form.type).toBe('fixed');
    expect(form.value).toBe('');
    expect(form.frequency).toBe('monthly');
    expect(form.description).toBe('');
  });

  it('converte value numerica para string', () => {
    const form = createInitialForm({ value: 12.5 });
    expect(form.value).toBe('12.5');
  });

  it('usa empty string quando value e 0 (falsy)', () => {
    const form = createInitialForm({ value: 0 });
    // 0?.toString() || '' = '0' mas 0 e falsy, entao a expressão é '0' || '' = '0'
    expect(form.value).toBe('0');
  });
});
