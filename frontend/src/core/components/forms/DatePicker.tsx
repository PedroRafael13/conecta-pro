'use client';

import { forwardRef, InputHTMLAttributes, useState, useCallback } from 'react';
import { clsx } from 'clsx';
import { Calendar, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

type DatePickerVariant = 'default' | 'filled' | 'outlined';
type DatePickerSize = 'sm' | 'md' | 'lg';

interface DatePickerProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type' | 'value' | 'onChange'> {
  value?: Date | string | null;
  onChange?: (date: Date | null) => void;
  variant?: DatePickerVariant;
  size?: DatePickerSize;
  error?: boolean;
  clearable?: boolean;
  minDate?: Date;
  maxDate?: Date;
  fullWidth?: boolean;
  dateFormat?: 'dd/MM/yyyy' | 'yyyy-MM-dd';
}

const variantStyles: Record<DatePickerVariant, string> = {
  default: 'bg-white border-gray-300 focus-within:border-[#FF6B35] focus-within:ring-[#FF6B35]',
  filled: 'bg-gray-100 border-transparent focus-within:bg-white focus-within:border-[#FF6B35] focus-within:ring-[#FF6B35]',
  outlined: 'bg-transparent border-[#0A2540] focus-within:border-[#FF6B35] focus-within:ring-[#FF6B35]',
};

const sizeStyles: Record<DatePickerSize, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-5 py-3 text-lg',
};

function formatDateBR(date: Date): string {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

function formatDateISO(date: Date): string {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${year}-${month}-${day}`;
}

function parseDateBR(dateString: string): Date | null {
  const match = dateString.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (!match) return null;

  const [, day, month, year] = match;
  const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));

  if (isNaN(date.getTime())) return null;
  return date;
}

function parseDate(value: Date | string | null | undefined): Date | null {
  if (!value) return null;
  if (value instanceof Date) return value;

  // Try BR format first
  const brDate = parseDateBR(value);
  if (brDate) return brDate;

  // Try ISO format
  const isoDate = new Date(value);
  if (!isNaN(isoDate.getTime())) return isoDate;

  return null;
}

export const DatePicker = forwardRef<HTMLInputElement, DatePickerProps>(
  (
    {
      value,
      onChange,
      variant = 'default',
      size = 'md',
      error = false,
      clearable = true,
      minDate,
      maxDate,
      fullWidth = true,
      dateFormat = 'dd/MM/yyyy',
      disabled,
      placeholder = 'dd/mm/aaaa',
      className,
      ...props
    },
    ref
  ) => {
    const [inputValue, setInputValue] = useState('');

    const parsedValue = parseDate(value);

    const displayValue = parsedValue
      ? dateFormat === 'dd/MM/yyyy'
        ? formatDateBR(parsedValue)
        : formatDateISO(parsedValue)
      : inputValue;

    const handleInputChange = useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        let newValue = e.target.value;

        // Auto-format as user types (BR format)
        if (dateFormat === 'dd/MM/yyyy') {
          // Remove non-digits
          const digits = newValue.replace(/\D/g, '');

          // Format with slashes
          if (digits.length <= 2) {
            newValue = digits;
          } else if (digits.length <= 4) {
            newValue = `${digits.slice(0, 2)}/${digits.slice(2)}`;
          } else {
            newValue = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4, 8)}`;
          }
        }

        setInputValue(newValue);

        // Try to parse the date
        const date = parseDateBR(newValue);
        if (date) {
          // Validate min/max
          if (minDate && date < minDate) return;
          if (maxDate && date > maxDate) return;

          onChange?.(date);
        }
      },
      [dateFormat, minDate, maxDate, onChange]
    );

    const handleNativeDateChange = useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        const dateValue = e.target.value;
        if (!dateValue) {
          onChange?.(null);
          return;
        }

        const date = new Date(dateValue + 'T00:00:00');
        if (!isNaN(date.getTime())) {
          // Validate min/max
          if (minDate && date < minDate) return;
          if (maxDate && date > maxDate) return;

          onChange?.(date);
        }
      },
      [minDate, maxDate, onChange]
    );

    const handleClear = useCallback(() => {
      setInputValue('');
      onChange?.(null);
    }, [onChange]);

    const nativeValue = parsedValue ? formatDateISO(parsedValue) : '';

    return (
      <div
        className={clsx(
          'relative rounded-lg border transition-colors duration-200',
          'focus-within:ring-2 focus-within:ring-offset-0',
          variantStyles[variant],
          fullWidth && 'w-full',
          error && 'border-red-500 focus-within:border-red-500 focus-within:ring-red-500',
          disabled && 'opacity-50 cursor-not-allowed bg-gray-100',
          className
        )}
      >
        <div className="flex items-center">
          <Calendar className={clsx(
            'absolute left-3 text-gray-400 pointer-events-none',
            size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5'
          )} />

          {/* Visible formatted input */}
          <input
            type="text"
            value={displayValue}
            onChange={handleInputChange}
            disabled={disabled}
            placeholder={placeholder}
            className={clsx(
              'w-full bg-transparent border-none focus:outline-none focus:ring-0',
              'pl-10',
              sizeStyles[size],
              clearable && parsedValue && 'pr-10'
            )}
            {...props}
          />

          {/* Hidden native date input for calendar popup */}
          <input
            ref={ref}
            type="date"
            value={nativeValue}
            onChange={handleNativeDateChange}
            min={minDate ? formatDateISO(minDate) : undefined}
            max={maxDate ? formatDateISO(maxDate) : undefined}
            disabled={disabled}
            className="absolute inset-0 opacity-0 cursor-pointer"
            tabIndex={-1}
          />

          <AnimatePresence>
            {clearable && parsedValue && !disabled && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                type="button"
                onClick={handleClear}
                className="absolute right-3 p-1 rounded-full hover:bg-gray-100 transition-colors"
              >
                <X className="w-4 h-4 text-gray-400" />
              </motion.button>
            )}
          </AnimatePresence>
        </div>
      </div>
    );
  }
);

DatePicker.displayName = 'DatePicker';
