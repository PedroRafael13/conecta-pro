'use client';

import { forwardRef, TextareaHTMLAttributes, useState, useEffect } from 'react';
import { clsx } from 'clsx';

type TextareaVariant = 'default' | 'filled' | 'outlined';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: TextareaVariant;
  error?: boolean;
  showCount?: boolean;
  maxLength?: number;
  autoResize?: boolean;
  fullWidth?: boolean;
}

const variantStyles: Record<TextareaVariant, string> = {
  default: 'bg-white border-gray-300 focus:border-[#FF6B35] focus:ring-[#FF6B35]',
  filled: 'bg-gray-100 border-transparent focus:bg-white focus:border-[#FF6B35] focus:ring-[#FF6B35]',
  outlined: 'bg-transparent border-[#0A2540] focus:border-[#FF6B35] focus:ring-[#FF6B35]',
};

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      variant = 'default',
      error = false,
      showCount = false,
      maxLength,
      autoResize = false,
      fullWidth = true,
      disabled,
      className,
      value,
      defaultValue,
      onChange,
      ...props
    },
    ref
  ) => {
    const [charCount, setCharCount] = useState(0);
    const [internalValue, setInternalValue] = useState(defaultValue || '');

    const currentValue = value !== undefined ? value : internalValue;

    useEffect(() => {
      setCharCount(String(currentValue).length);
    }, [currentValue]);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value;

      if (value === undefined) {
        setInternalValue(newValue);
      }

      if (autoResize) {
        e.target.style.height = 'auto';
        e.target.style.height = `${e.target.scrollHeight}px`;
      }

      onChange?.(e);
    };

    const isOverLimit = maxLength ? charCount > maxLength : false;

    return (
      <div className={clsx(fullWidth && 'w-full')}>
        <textarea
          ref={ref}
          value={currentValue}
          onChange={handleChange}
          disabled={disabled}
          maxLength={maxLength}
          className={clsx(
            'rounded-lg border transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            'px-4 py-3 min-h-[100px] resize-y',
            variantStyles[variant],
            fullWidth && 'w-full',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
            disabled && 'opacity-50 cursor-not-allowed bg-gray-100',
            autoResize && 'resize-none overflow-hidden',
            className
          )}
          {...props}
        />

        {showCount && (
          <div className="flex justify-end mt-1">
            <span
              className={clsx(
                'text-sm',
                isOverLimit ? 'text-red-500' : 'text-gray-500'
              )}
            >
              {charCount}
              {maxLength && ` / ${maxLength}`}
            </span>
          </div>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
