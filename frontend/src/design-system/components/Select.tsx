'use client';

import { forwardRef, Fragment, type ReactNode } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { Check, ChevronDown } from 'lucide-react';
import { cn } from '@/shared/utils/cn';

export interface SelectOption {
  value: string;
  label: string;
  icon?: ReactNode;
  disabled?: boolean;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  helperText?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-4 text-base',
};

export const Select = forwardRef<HTMLButtonElement, SelectProps>(
  (
    {
      options,
      value,
      onChange,
      placeholder = 'Selecione...',
      label,
      helperText,
      error,
      disabled,
      required,
      className,
      size = 'md',
    },
    ref
  ) => {
    const selectedOption = options.find((opt) => opt.value === value);

    return (
      <div className={cn('w-full', className)}>
        {label && (
          <label
            className={cn(
              'block text-sm font-medium text-text-secondary mb-1.5',
              required && "after:content-['*'] after:text-danger after:ml-0.5"
            )}
          >
            {label}
          </label>
        )}
        <Listbox value={value} onChange={onChange} disabled={disabled}>
          <div className="relative">
            <Listbox.Button
              ref={ref}
              className={cn(
                'relative w-full bg-bg-tertiary border rounded-lg text-left',
                'transition-all duration-200',
                'focus:outline-none focus:ring-1',
                error
                  ? 'border-danger focus:border-danger focus:ring-danger'
                  : 'border-border-default focus:border-accent-primary focus:ring-accent-primary',
                disabled && 'opacity-50 cursor-not-allowed',
                sizeClasses[size]
              )}
            >
              <span className="flex items-center gap-2 truncate">
                {selectedOption?.icon}
                <span
                  className={cn(
                    selectedOption ? 'text-text-primary' : 'text-text-muted'
                  )}
                >
                  {selectedOption?.label || placeholder}
                </span>
              </span>
              <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                <ChevronDown className="h-4 w-4 text-text-muted" aria-hidden="true" />
              </span>
            </Listbox.Button>
            <Transition
              as={Fragment}
              leave="transition ease-in duration-100"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <Listbox.Options
                className={cn(
                  'absolute z-50 mt-1 w-full overflow-auto rounded-xl',
                  'bg-bg-secondary border border-border-subtle shadow-dropdown',
                  'py-1 text-sm max-h-60',
                  'focus:outline-none'
                )}
              >
                {options.map((option) => (
                  <Listbox.Option
                    key={option.value}
                    value={option.value}
                    disabled={option.disabled}
                    className={({ active, disabled }) =>
                      cn(
                        'relative cursor-pointer select-none py-2.5 px-4',
                        active && 'bg-bg-tertiary',
                        disabled && 'opacity-50 cursor-not-allowed'
                      )
                    }
                  >
                    {({ selected }) => (
                      <div className="flex items-center justify-between gap-2">
                        <span className="flex items-center gap-2">
                          {option.icon}
                          <span
                            className={cn(
                              'block truncate',
                              selected
                                ? 'text-accent-primary font-medium'
                                : 'text-text-primary'
                            )}
                          >
                            {option.label}
                          </span>
                        </span>
                        {selected && (
                          <Check className="h-4 w-4 text-accent-primary" />
                        )}
                      </div>
                    )}
                  </Listbox.Option>
                ))}
              </Listbox.Options>
            </Transition>
          </div>
        </Listbox>
        {(helperText || error) && (
          <p
            className={cn(
              'text-sm mt-1.5',
              error ? 'text-danger' : 'text-text-muted'
            )}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
