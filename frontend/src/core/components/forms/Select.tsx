'use client';

import { forwardRef, SelectHTMLAttributes } from 'react';
import { clsx } from 'clsx';
import { ChevronDown, Loader2 } from 'lucide-react';

type SelectVariant = 'default' | 'filled' | 'outlined';
type SelectSize = 'sm' | 'md' | 'lg';

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  options: SelectOption[];
  placeholder?: string;
  variant?: SelectVariant;
  size?: SelectSize;
  loading?: boolean;
  error?: boolean;
  fullWidth?: boolean;
}

const variantStyles: Record<SelectVariant, string> = {
  default: 'bg-white border-gray-300 focus:border-[#FF6B35] focus:ring-[#FF6B35]',
  filled: 'bg-gray-100 border-transparent focus:bg-white focus:border-[#FF6B35] focus:ring-[#FF6B35]',
  outlined: 'bg-transparent border-[#0A2540] focus:border-[#FF6B35] focus:ring-[#FF6B35]',
};

const sizeStyles: Record<SelectSize, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-5 py-3 text-lg',
};

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      options,
      placeholder = 'Selecione...',
      variant = 'default',
      size = 'md',
      loading = false,
      error = false,
      fullWidth = true,
      disabled,
      className,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <div className={clsx('relative', fullWidth && 'w-full')}>
        <select
          ref={ref}
          disabled={isDisabled}
          className={clsx(
            'appearance-none rounded-lg border transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            'pr-10',
            variantStyles[variant],
            sizeStyles[size],
            fullWidth && 'w-full',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
            isDisabled && 'opacity-50 cursor-not-allowed bg-gray-100',
            className
          )}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>

        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          {loading ? (
            <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </div>
    );
  }
);

Select.displayName = 'Select';
