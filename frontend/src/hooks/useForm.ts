'use client';

import { useState, useCallback, useRef, useEffect } from 'react';

export type ValidationRule<T = string> = {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  min?: number;
  max?: number;
  validate?: (value: T) => boolean | string;
};

export type ValidationRules<T extends Record<string, unknown>> = {
  [K in keyof T]?: ValidationRule<T[K] extends string ? string : unknown>;
};

export type FormErrors<T> = {
  [K in keyof T]?: string;
};

export type FormTouched<T> = {
  [K in keyof T]?: boolean;
};

export interface UseFormOptions<T extends Record<string, unknown>> {
  initialValues: T;
  validationRules?: ValidationRules<T>;
  onSubmit?: (values: T) => void | Promise<void>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

export interface UseFormReturn<T extends Record<string, unknown>> {
  values: T;
  errors: FormErrors<T>;
  touched: FormTouched<T>;
  isSubmitting: boolean;
  isDirty: boolean;
  isValid: boolean;
  setValue: <K extends keyof T>(field: K, value: T[K]) => void;
  setValues: (values: Partial<T>) => void;
  setError: (field: keyof T, message: string) => void;
  clearError: (field: keyof T) => void;
  clearErrors: () => void;
  handleChange: (field: keyof T) => (value: unknown) => void;
  handleBlur: (field: keyof T) => () => void;
  handleSubmit: (e?: React.FormEvent) => Promise<void>;
  reset: (newValues?: Partial<T>) => void;
  validate: () => boolean;
  validateField: (field: keyof T) => boolean;
  getFieldProps: (field: keyof T) => {
    value: T[keyof T];
    onChange: (value: unknown) => void;
    onBlur: () => void;
    error?: string;
    touched?: boolean;
  };
}

export function useForm<T extends Record<string, unknown>>(
  options: UseFormOptions<T>
): UseFormReturn<T> {
  const {
    initialValues,
    validationRules = {} as ValidationRules<T>,
    onSubmit,
    validateOnChange = true,
    validateOnBlur = true,
  } = options;

  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<FormErrors<T>>({} as FormErrors<T>);
  const [touched, setTouched] = useState<FormTouched<T>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const initialValuesRef = useRef(initialValues);

  // Verificar se o formulário foi modificado
  const isDirty = JSON.stringify(values) !== JSON.stringify(initialValuesRef.current);

  // Verificar se o formulário é válido
  const isValid = Object.keys(errors).length === 0;

  // Validar um campo específico
  const validateField = useCallback((field: keyof T): boolean => {
    const rules = validationRules[field];
    const value = values[field];

    if (!rules) return true;

    // Required
    if (rules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
      setErrors(prev => ({ ...prev, [field]: 'Campo obrigatório' }));
      return false;
    }

    const stringValue = String(value || '');

    // Min length
    if (rules.minLength !== undefined && stringValue.length < rules.minLength) {
      setErrors(prev => ({ ...prev, [field]: `Mínimo de ${rules.minLength} caracteres` }));
      return false;
    }

    // Max length
    if (rules.maxLength !== undefined && stringValue.length > rules.maxLength) {
      setErrors(prev => ({ ...prev, [field]: `Máximo de ${rules.maxLength} caracteres` }));
      return false;
    }

    // Pattern
    if (rules.pattern && !rules.pattern.test(stringValue)) {
      setErrors(prev => ({ ...prev, [field]: 'Formato inválido' }));
      return false;
    }

    // Min/Max para números
    if (typeof value === 'number') {
      if (rules.min !== undefined && value < rules.min) {
        setErrors(prev => ({ ...prev, [field]: `Valor mínimo: ${rules.min}` }));
        return false;
      }
      if (rules.max !== undefined && value > rules.max) {
        setErrors(prev => ({ ...prev, [field]: `Valor máximo: ${rules.max}` }));
        return false;
      }
    }

    // Custom validation
    if (rules.validate) {
      const result = rules.validate(value as string);
      if (result !== true) {
        setErrors(prev => ({ ...prev, [field]: typeof result === 'string' ? result : 'Valor inválido' }));
        return false;
      }
    }

    // Limpar erro se validação passar
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });

    return true;
  }, [values, validationRules]);

  // Validar todos os campos
  const validate = useCallback((): boolean => {
    let isFormValid = true;

    for (const field of Object.keys(validationRules) as Array<keyof T>) {
      const isFieldValid = validateField(field);
      if (!isFieldValid) {
        isFormValid = false;
      }
    }

    return isFormValid;
  }, [validateField, validationRules]);

  // Setar valor de um campo
  const setValue = useCallback(<K extends keyof T>(field: K, value: T[K]) => {
    setValues(prev => ({ ...prev, [field]: value }));

    if (validateOnChange) {
      // Usar setTimeout para garantir que o estado foi atualizado
      setTimeout(() => validateField(field), 0);
    }
  }, [validateOnChange, validateField]);

  // Setar múltiplos valores
  const setValuesWrapper = useCallback((newValues: Partial<T>) => {
    setValues(prev => ({ ...prev, ...newValues }));
  }, []);

  // Setar erro manualmente
  const setError = useCallback((field: keyof T, message: string) => {
    setErrors(prev => ({ ...prev, [field]: message }));
  }, []);

  // Limpar erro de um campo
  const clearError = useCallback((field: keyof T) => {
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
  }, []);

  // Limpar todos os erros
  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  // Handler de change
  const handleChange = useCallback((field: keyof T) => (value: unknown) => {
    setValue(field, value as T[typeof field]);
  }, [setValue]);

  // Handler de blur
  const handleBlur = useCallback((field: keyof T) => () => {
    setTouched(prev => ({ ...prev, [field]: true }));

    if (validateOnBlur) {
      validateField(field);
    }
  }, [validateOnBlur, validateField]);

  // Handler de submit
  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    // Marcar todos como touched
    const allTouched: FormTouched<T> = {};
    for (const key of Object.keys(values)) {
      allTouched[key as keyof T] = true;
    }
    setTouched(allTouched);

    // Validar
    const isFormValid = validate();

    if (!isFormValid) {
      return;
    }

    if (onSubmit) {
      setIsSubmitting(true);
      try {
        await onSubmit(values);
      } finally {
        setIsSubmitting(false);
      }
    }
  }, [values, validate, onSubmit]);

  // Resetar formulário
  const reset = useCallback((newValues?: Partial<T>) => {
    const resetValues = newValues
      ? { ...initialValuesRef.current, ...newValues }
      : initialValuesRef.current;

    setValues(resetValues);
    setErrors({});
    setTouched({});
  }, []);

  // Get field props
  const getFieldProps = useCallback((field: keyof T) => ({
    value: values[field],
    onChange: handleChange(field),
    onBlur: handleBlur(field),
    error: errors[field],
    touched: touched[field],
  }), [values, errors, touched, handleChange, handleBlur]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    isDirty,
    isValid,
    setValue,
    setValues: setValuesWrapper,
    setError,
    clearError,
    clearErrors,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    validate,
    validateField,
    getFieldProps,
  };
}

export default useForm;
