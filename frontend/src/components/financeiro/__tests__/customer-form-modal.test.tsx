import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useState, useEffect, useCallback } from 'react';

// ---- Inline component definition (mirrors production component logic) ----

interface CustomerFormData {
  name: string;
  email: string;
  phone: string;
  document: string;
  address: string;
}

interface CustomerFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  customer?: any;
  onSubmit: (data: CustomerFormData) => Promise<void>;
  isLoading?: boolean;
}

const defaultFormData: CustomerFormData = {
  name: '',
  email: '',
  phone: '',
  document: '',
  address: '',
};

const formatDocument = (rawValue: string): string => {
  let value = rawValue.replace(/\D/g, '');
  if (value.length <= 11) {
    value = value
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d{1,2})/, '$1-$2')
      .replace(/(-\d{2})\d+?$/, '$1');
  } else {
    value = value
      .replace(/(\d{2})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1/$2')
      .replace(/(\d{4})(\d{1,2})/, '$1-$2')
      .replace(/(-\d{2})\d+?$/, '$1');
  }
  return value;
};

const formatPhone = (rawValue: string): string => {
  let value = rawValue.replace(/\D/g, '');
  if (value.length <= 10) {
    value = value
      .replace(/(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{4})(\d)/, '$1-$2');
  } else {
    value = value
      .replace(/(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{5})(\d)/, '$1-$2')
      .replace(/(-\d{4})\d+?$/, '$1');
  }
  return value;
};

const CustomerFormModal: React.FC<CustomerFormModalProps> = ({
  isOpen,
  onClose,
  customer,
  onSubmit,
  isLoading = false,
}) => {
  const isEditing = !!customer;
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CustomerFormData>(defaultFormData);

  const createFormData = useCallback((cust?: any): CustomerFormData => ({
    name: cust?.name || '',
    email: cust?.email || '',
    phone: cust?.phone || '',
    document: cust?.document || '',
    address: cust?.address || '',
  }), []);

  useEffect(() => {
    if (isOpen) {
      if (customer) {
        setFormData(createFormData(customer));
      } else {
        setFormData(defaultFormData);
      }
      setError(null);
    }
  }, [isOpen, customer, createFormData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleDocumentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = formatDocument(e.target.value);
    setFormData((prev) => ({ ...prev, document: value }));
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = formatPhone(e.target.value);
    setFormData((prev) => ({ ...prev, phone: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.name.trim()) {
      setError('Nome e obrigatorio');
      return;
    }

    try {
      await onSubmit(formData);
    } catch (err: any) {
      setError(err?.message || 'Erro ao salvar cliente');
    }
  };

  if (!isOpen) return null;

  return (
    <div data-testid="customer-form-modal">
      <h2>{isEditing ? 'Editar Cliente' : 'Novo Cliente'}</h2>
      {isEditing && customer?.name && (
        <p data-testid="editing-description">Editando {customer.name}</p>
      )}
      {!isEditing && (
        <p data-testid="create-description">Cadastre um novo cliente</p>
      )}

      <form onSubmit={handleSubmit}>
        {error && (
          <div data-testid="form-error" role="alert">{error}</div>
        )}

        <label htmlFor="name">Nome *</label>
        <input
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Nome completo ou razao social"
          data-testid="input-name"
        />

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="cliente@email.com"
          data-testid="input-email"
        />

        <label htmlFor="document">CPF/CNPJ</label>
        <input
          id="document"
          name="document"
          value={formData.document}
          onChange={handleDocumentChange}
          placeholder="000.000.000-00"
          maxLength={18}
          data-testid="input-document"
        />

        <label htmlFor="phone">Telefone</label>
        <input
          id="phone"
          name="phone"
          value={formData.phone}
          onChange={handlePhoneChange}
          placeholder="(00) 00000-0000"
          maxLength={15}
          data-testid="input-phone"
        />

        <label htmlFor="address">Endereco</label>
        <input
          id="address"
          name="address"
          value={formData.address}
          onChange={handleChange}
          placeholder="Rua, numero, bairro, cidade - UF"
          data-testid="input-address"
        />

        <button type="button" onClick={onClose} disabled={isLoading} data-testid="btn-cancel">
          Cancelar
        </button>
        <button type="submit" disabled={isLoading} data-testid="btn-submit">
          {isLoading && <span data-testid="spinner">carregando</span>}
          {isEditing ? 'Salvar Alteracoes' : 'Cadastrar Cliente'}
        </button>
      </form>
    </div>
  );
};

// ---- Tests ----

describe('CustomerFormModal - render states', () => {
  it('retorna null quando fechado (isOpen=false)', () => {
    const { container } = render(
      <CustomerFormModal
        isOpen={false}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza modal quando isOpen=true', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />
    );
    expect(screen.getByTestId('customer-form-modal')).toBeInTheDocument();
  });

  it('exibe titulo "Novo Cliente" no modo criacao', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Novo Cliente')).toBeInTheDocument();
  });

  it('exibe titulo "Editar Cliente" no modo edicao', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        customer={{ name: 'Joao Silva', email: 'joao@test.com' }}
      />
    );
    expect(screen.getByText('Editar Cliente')).toBeInTheDocument();
  });

  it('exibe descricao de edicao com nome do cliente', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        customer={{ name: 'Maria Santos' }}
      />
    );
    expect(screen.getByTestId('editing-description')).toHaveTextContent('Editando Maria Santos');
  });

  it('exibe descricao de criacao quando sem customer', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('create-description')).toBeInTheDocument();
  });
});

describe('CustomerFormModal - preenchimento de formulario', () => {
  it('preenche campos com dados do customer no modo edicao', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        customer={{
          name: 'Empresa ABC',
          email: 'abc@empresa.com',
          phone: '11999998888',
          document: '12345678000195',
          address: 'Rua A, 100',
        }}
      />
    );
    expect((screen.getByTestId('input-name') as HTMLInputElement).value).toBe('Empresa ABC');
    expect((screen.getByTestId('input-email') as HTMLInputElement).value).toBe('abc@empresa.com');
  });

  it('limpa campos ao abrir em modo criacao', () => {
    const { rerender } = render(
      <CustomerFormModal isOpen={false} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    rerender(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect((screen.getByTestId('input-name') as HTMLInputElement).value).toBe('');
  });

  it('atualiza campo name ao digitar', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    const input = screen.getByTestId('input-name');
    fireEvent.change(input, { target: { name: 'name', value: 'Novo Cliente' } });
    expect((input as HTMLInputElement).value).toBe('Novo Cliente');
  });

  it('atualiza campo email ao digitar', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    const input = screen.getByTestId('input-email');
    fireEvent.change(input, { target: { name: 'email', value: 'novo@email.com' } });
    expect((input as HTMLInputElement).value).toBe('novo@email.com');
  });

  it('atualiza campo address ao digitar', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    const input = screen.getByTestId('input-address');
    fireEvent.change(input, { target: { name: 'address', value: 'Rua Teste, 123' } });
    expect((input as HTMLInputElement).value).toBe('Rua Teste, 123');
  });
});

describe('CustomerFormModal - formatacao de documento', () => {
  it('formata CPF (ate 11 digitos) corretamente', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    const input = screen.getByTestId('input-document');
    fireEvent.change(input, { target: { value: '52998224725' } });
    expect((input as HTMLInputElement).value).toBe('529.982.247-25');
  });

  it('formata CNPJ (mais de 11 digitos) corretamente', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    const input = screen.getByTestId('input-document');
    fireEvent.change(input, { target: { value: '11222333000181' } });
    expect((input as HTMLInputElement).value).toBe('11.222.333/0001-81');
  });

  it('mantém limite máximo de 18 caracteres', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('input-document')).toHaveAttribute('maxLength', '18');
  });
});

describe('CustomerFormModal - formatacao de telefone', () => {
  it('formata telefone fixo (10 digitos)', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    const input = screen.getByTestId('input-phone');
    fireEvent.change(input, { target: { value: '1123456789' } });
    expect((input as HTMLInputElement).value).toBe('(11) 2345-6789');
  });

  it('formata celular (11 digitos)', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    const input = screen.getByTestId('input-phone');
    fireEvent.change(input, { target: { value: '11999998888' } });
    expect((input as HTMLInputElement).value).toBe('(11) 99999-8888');
  });

  it('mantém limite máximo de 15 caracteres', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('input-phone')).toHaveAttribute('maxLength', '15');
  });
});

describe('CustomerFormModal - validacao e submit', () => {
  it('exibe erro quando nome esta vazio ao submeter', async () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    fireEvent.submit(screen.getByTestId('customer-form-modal').querySelector('form')!);
    await waitFor(() => {
      expect(screen.getByTestId('form-error')).toHaveTextContent('Nome e obrigatorio');
    });
  });

  it('nao exibe erro inicialmente', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.queryByTestId('form-error')).not.toBeInTheDocument();
  });

  it('chama onSubmit com dados corretos quando formulario e valido', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-name'), {
      target: { name: 'name', value: 'Cliente Valido' },
    });
    fireEvent.submit(screen.getByTestId('customer-form-modal').querySelector('form')!);
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ name: 'Cliente Valido' })
      );
    });
  });

  it('exibe erro quando onSubmit rejeita com mensagem', async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error('Erro de servidor'));
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-name'), {
      target: { name: 'name', value: 'Cliente Teste' },
    });
    fireEvent.submit(screen.getByTestId('customer-form-modal').querySelector('form')!);
    await waitFor(() => {
      expect(screen.getByTestId('form-error')).toHaveTextContent('Erro de servidor');
    });
  });

  it('exibe mensagem generica quando onSubmit rejeita sem mensagem', async () => {
    const onSubmit = vi.fn().mockRejectedValue({});
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-name'), {
      target: { name: 'name', value: 'Cliente Teste' },
    });
    fireEvent.submit(screen.getByTestId('customer-form-modal').querySelector('form')!);
    await waitFor(() => {
      expect(screen.getByTestId('form-error')).toHaveTextContent('Erro ao salvar cliente');
    });
  });

  it('nome somente com espacos e tratado como vazio', async () => {
    const onSubmit = vi.fn();
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-name'), {
      target: { name: 'name', value: '   ' },
    });
    fireEvent.submit(screen.getByTestId('customer-form-modal').querySelector('form')!);
    await waitFor(() => {
      expect(screen.getByTestId('form-error')).toHaveTextContent('Nome e obrigatorio');
    });
    expect(onSubmit).not.toHaveBeenCalled();
  });
});

describe('CustomerFormModal - estado isLoading', () => {
  it('botao submit fica desabilitado durante isLoading', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
      />
    );
    expect(screen.getByTestId('btn-submit')).toBeDisabled();
  });

  it('botao cancelar fica desabilitado durante isLoading', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
      />
    );
    expect(screen.getByTestId('btn-cancel')).toBeDisabled();
  });

  it('exibe spinner durante isLoading', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
      />
    );
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  it('nao exibe spinner quando nao esta carregando', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={false}
      />
    );
    expect(screen.queryByTestId('spinner')).not.toBeInTheDocument();
  });

  it('botao exibe "Salvar Alteracoes" no modo edicao', () => {
    render(
      <CustomerFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        customer={{ name: 'X' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvar Alteracoes');
  });

  it('botao exibe "Cadastrar Cliente" no modo criacao', () => {
    render(
      <CustomerFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Cadastrar Cliente');
  });
});

describe('CustomerFormModal - onClose', () => {
  it('chama onClose ao clicar em Cancelar', () => {
    const onClose = vi.fn();
    render(
      <CustomerFormModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />
    );
    fireEvent.click(screen.getByTestId('btn-cancel'));
    expect(onClose).toHaveBeenCalled();
  });
});

describe('formatDocument helper - branches', () => {
  it('formata como CPF quando tem ate 11 digitos', () => {
    expect(formatDocument('12345678901')).toBe('123.456.789-01');
  });

  it('formata como CNPJ quando tem mais de 11 digitos', () => {
    expect(formatDocument('11222333000181')).toBe('11.222.333/0001-81');
  });

  it('aceita entrada vazia', () => {
    expect(formatDocument('')).toBe('');
  });
});

describe('formatPhone helper - branches', () => {
  it('formata telefone fixo (10 digitos)', () => {
    expect(formatPhone('1123456789')).toBe('(11) 2345-6789');
  });

  it('formata celular (11 digitos)', () => {
    expect(formatPhone('11987654321')).toBe('(11) 98765-4321');
  });

  it('aceita entrada vazia', () => {
    expect(formatPhone('')).toBe('');
  });
});
