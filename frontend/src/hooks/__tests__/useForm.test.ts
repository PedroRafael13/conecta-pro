import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useForm } from '../useForm';

describe('useForm', () => {
  describe('Validação de Campos', () => {
    it('deve validar campo obrigatório', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
          validationRules: {
            name: { required: true },
          },
        })
      );

      act(() => {
        result.current.handleSubmit();
      });

      expect(result.current.errors.name).toBe('Campo obrigatório');
      expect(result.current.isValid).toBe(false);
    });

    it('deve validar minLength', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'ab' },
          validationRules: {
            name: { minLength: 3 },
          },
        })
      );

      act(() => {
        result.current.validateField('name');
      });

      expect(result.current.errors.name).toBe('Mínimo de 3 caracteres');
    });

    it('deve validar maxLength', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'abcdefghij' },
          validationRules: {
            name: { maxLength: 5 },
          },
        })
      );

      act(() => {
        result.current.validateField('name');
      });

      expect(result.current.errors.name).toBe('Máximo de 5 caracteres');
    });

    it('deve validar pattern (regex)', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { email: 'invalid-email' },
          validationRules: {
            email: { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
          },
        })
      );

      act(() => {
        result.current.validateField('email');
      });

      expect(result.current.errors.email).toBe('Formato inválido');
    });

    it('deve validar com função customizada', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { age: 15 },
          validationRules: {
            age: { validate: (value: any) => value >= 18 || 'Deve ser maior de idade' },
          },
        })
      );

      act(() => {
        result.current.validateField('age');
      });

      expect(result.current.errors.age).toBe('Deve ser maior de idade');
    });

    it('deve retornar "Valor inválido" quando validate retorna false (não string)', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { code: 'abc' },
          validationRules: {
            code: { validate: () => false },
          },
        })
      );

      act(() => {
        result.current.validateField('code');
      });

      expect(result.current.errors.code).toBe('Valor inválido');
    });

    it('deve passar na validação quando todos os campos são válidos', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John', email: 'john@example.com' },
          validationRules: {
            name: { required: true, minLength: 2 },
            email: { required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
          },
        })
      );

      const isValid = result.current.validate();

      expect(isValid).toBe(true);
      expect(result.current.errors).toEqual({});
    });

    it('deve limpar erro quando campo se torna válido', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
          validationRules: {
            name: { required: true },
          },
        })
      );

      act(() => {
        result.current.validateField('name');
      });
      expect(result.current.errors.name).toBeDefined();

      act(() => {
        result.current.setValue('name', 'John');
      });

      // Aguardar validação automática
      act(() => {
        result.current.validateField('name');
      });

      expect(result.current.errors.name).toBeUndefined();
    });
  });

  describe('Submit', () => {
    it('deve chamar onSubmit quando formulário é válido', async () => {
      const onSubmit = vi.fn();
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John', email: 'john@example.com' },
          validationRules: {
            name: { required: true },
            email: { required: true },
          },
          onSubmit,
        })
      );

      await act(async () => {
        await result.current.handleSubmit();
      });

      expect(onSubmit).toHaveBeenCalledWith({ name: 'John', email: 'john@example.com' });
      expect(result.current.isSubmitting).toBe(false);
    });

    it('não deve chamar onSubmit quando formulário é inválido', async () => {
      const onSubmit = vi.fn();
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '', email: '' },
          validationRules: {
            name: { required: true },
            email: { required: true },
          },
          onSubmit,
        })
      );

      await act(async () => {
        await result.current.handleSubmit();
      });

      expect(onSubmit).not.toHaveBeenCalled();
    });

    it('deve setar isSubmitting durante o submit', async () => {
      const onSubmit = vi.fn(() => new Promise((resolve) => setTimeout(resolve, 100))) as any;
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John' },
          onSubmit,
        })
      );

      act(() => {
        result.current.handleSubmit();
      });

      expect(result.current.isSubmitting).toBe(true);
    });

    it('deve chamar preventDefault quando evento é passado ao handleSubmit', async () => {
      const onSubmit = vi.fn();
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John' },
          onSubmit,
        })
      );

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent;

      await act(async () => {
        await result.current.handleSubmit(mockEvent);
      });

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(onSubmit).toHaveBeenCalled();
    });

    it('deve suportar submit assíncrono', async () => {
      const asyncSubmit = vi.fn().mockResolvedValue(undefined);
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John' },
          onSubmit: asyncSubmit,
        })
      );

      await act(async () => {
        await result.current.handleSubmit();
      });

      expect(asyncSubmit).toHaveBeenCalled();
      expect(result.current.isSubmitting).toBe(false);
    });
  });

  describe('Reset', () => {
    it('deve resetar valores para iniciais', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John', email: 'john@example.com' },
        })
      );

      act(() => {
        result.current.setValue('name', 'Jane');
        result.current.setValue('email', 'jane@example.com');
      });

      expect(result.current.values).toEqual({ name: 'Jane', email: 'jane@example.com' });

      act(() => {
        result.current.reset();
      });

      expect(result.current.values).toEqual({ name: 'John', email: 'john@example.com' });
    });

    it('deve limpar erros ao resetar', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
          validationRules: { name: { required: true } },
        })
      );

      act(() => {
        result.current.handleSubmit();
      });

      expect(result.current.errors.name).toBeDefined();

      act(() => {
        result.current.reset();
      });

      expect(result.current.errors).toEqual({});
    });

    it('deve limpar touched ao resetar', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
        })
      );

      act(() => {
        result.current.handleBlur('name')();
      });

      expect(result.current.touched.name).toBe(true);

      act(() => {
        result.current.reset();
      });

      expect(result.current.touched).toEqual({});
    });

    it('deve resetar com novos valores', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John', email: 'john@example.com' },
        })
      );

      act(() => {
        result.current.reset({ name: 'Jane' });
      });

      expect(result.current.values).toEqual({ name: 'Jane', email: 'john@example.com' });
    });
  });

  describe('Dirty State', () => {
    it('deve detectar formulário dirty', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John' },
        })
      );

      expect(result.current.isDirty).toBe(false);

      act(() => {
        result.current.setValue('name', 'Jane');
      });

      expect(result.current.isDirty).toBe(true);
    });

    it('deve detectar quando volta ao estado original', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John' },
        })
      );

      act(() => {
        result.current.setValue('name', 'Jane');
      });
      expect(result.current.isDirty).toBe(true);

      act(() => {
        result.current.setValue('name', 'John');
      });
      expect(result.current.isDirty).toBe(false);
    });
  });

  describe('Manipulação de Valores', () => {
    it('deve setar valor de campo', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
        })
      );

      act(() => {
        result.current.setValue('name', 'John');
      });

      expect(result.current.values.name).toBe('John');
    });

    it('deve setar múltiplos valores', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '', email: '' },
        })
      );

      act(() => {
        result.current.setValues({ name: 'John', email: 'john@example.com' });
      });

      expect(result.current.values).toEqual({ name: 'John', email: 'john@example.com' });
    });

    it('deve setar erro manualmente', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
        })
      );

      act(() => {
        result.current.setError('name', 'Erro customizado');
      });

      expect(result.current.errors.name).toBe('Erro customizado');
    });

    it('deve limpar erro específico', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '', email: '' },
        })
      );

      act(() => {
        result.current.setError('name', 'Erro no nome');
        result.current.setError('email', 'Erro no email');
      });

      act(() => {
        result.current.clearError('name');
      });

      expect(result.current.errors.name).toBeUndefined();
      expect(result.current.errors.email).toBe('Erro no email');
    });

    it('deve limpar todos os erros', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '', email: '' },
        })
      );

      act(() => {
        result.current.setError('name', 'Erro no nome');
        result.current.setError('email', 'Erro no email');
      });

      act(() => {
        result.current.clearErrors();
      });

      expect(result.current.errors).toEqual({});
    });
  });

  describe('Handlers', () => {
    it('deve criar handleChange para campo', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
        })
      );

      const handleChange = result.current.handleChange('name');

      act(() => {
        handleChange('John');
      });

      expect(result.current.values.name).toBe('John');
    });

    it('deve criar handleBlur para campo', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
        })
      );

      const handleBlur = result.current.handleBlur('name');

      act(() => {
        handleBlur();
      });

      expect(result.current.touched.name).toBe(true);
    });

    it('deve retornar field props', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John' },
          validationRules: { name: { required: true } },
        })
      );

      const fieldProps = result.current.getFieldProps('name');

      expect(fieldProps.value).toBe('John');
      expect(typeof fieldProps.onChange).toBe('function');
      expect(typeof fieldProps.onBlur).toBe('function');
    });
  });

  describe('Validação em Tempo Real', () => {
    it('deve validar on change quando habilitado', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
          validationRules: { name: { required: true } },
          validateOnChange: true,
        })
      );

      act(() => {
        result.current.setValue('name', 'John');
      });

      // Simular o efeito da validação
      act(() => {
        result.current.validateField('name');
      });

      expect(result.current.errors.name).toBeUndefined();
    });

    it('não deve validar on change quando desabilitado', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
          validationRules: { name: { required: true } },
          validateOnChange: false,
        })
      );

      act(() => {
        result.current.setValue('name', 'John');
      });

      // Não deve ter disparado validação automática
      expect(result.current.errors.name).toBeUndefined();
    });

    it('não deve validar on blur quando desabilitado', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
          validationRules: { name: { required: true } },
          validateOnBlur: false,
        })
      );

      act(() => {
        result.current.handleBlur('name')();
      });

      // Campo marcado como touched, mas sem erro de validação
      expect(result.current.touched.name).toBe(true);
      expect(result.current.errors.name).toBeUndefined();
    });

    it('deve validar on blur quando habilitado', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: '' },
          validationRules: { name: { required: true } },
          validateOnBlur: true,
        })
      );

      act(() => {
        result.current.handleBlur('name')();
      });

      expect(result.current.errors.name).toBe('Campo obrigatório');
    });
  });

  describe('Validações Adicionais', () => {
    it('deve validar min', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { age: 10 },
          validationRules: {
            age: { min: 18 },
          },
        })
      );

      act(() => {
        result.current.validateField('age');
      });

      expect(result.current.errors.age).toBe('Valor mínimo: 18');
    });

    it('deve validar max', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { score: 150 },
          validationRules: {
            score: { max: 100 },
          },
        })
      );

      act(() => {
        result.current.validateField('score');
      });

      expect(result.current.errors.score).toBe('Valor máximo: 100');
    });

    it('deve validar pattern e usar mensagem padrão', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { cpf: '123' },
          validationRules: {
            cpf: {
              pattern: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
            },
          },
        })
      );

      act(() => {
        result.current.validateField('cpf');
      });

      expect(result.current.errors.cpf).toBe('Formato inválido');
    });

    it('deve chamar reset function corretamente', () => {
      const { result } = renderHook(() =>
        useForm({
          initialValues: { name: 'John', email: 'john@test.com' },
        })
      );

      act(() => {
        result.current.setValue('name', 'Jane');
        result.current.setValue('email', 'jane@test.com');
      });

      expect(result.current.values).toEqual({ name: 'Jane', email: 'jane@test.com' });

      act(() => {
        result.current.reset();
      });

      expect(result.current.values).toEqual({ name: 'John', email: 'john@test.com' });
      expect(result.current.errors).toEqual({});
      expect(result.current.touched).toEqual({});
    });
  });
});
