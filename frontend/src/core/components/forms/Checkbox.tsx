'use client';

import { forwardRef, InputHTMLAttributes, ReactNode, useId } from 'react';
import { clsx } from 'clsx';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

type CheckboxSize = 'sm' | 'md' | 'lg';

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  label?: ReactNode;
  description?: string;
  size?: CheckboxSize;
  error?: boolean;
  indeterminate?: boolean;
}

const sizeStyles: Record<CheckboxSize, { box: string; icon: string; label: string }> = {
  sm: {
    box: 'w-4 h-4',
    icon: 'w-3 h-3',
    label: 'text-sm',
  },
  md: {
    box: 'w-5 h-5',
    icon: 'w-3.5 h-3.5',
    label: 'text-base',
  },
  lg: {
    box: 'w-6 h-6',
    icon: 'w-4 h-4',
    label: 'text-lg',
  },
};

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  (
    {
      label,
      description,
      size = 'md',
      error = false,
      indeterminate = false,
      disabled,
      checked,
      className,
      id,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const checkboxId = id || generatedId;
    const styles = sizeStyles[size];

    return (
      <label
        htmlFor={checkboxId}
        className={clsx(
          'inline-flex items-start gap-3 cursor-pointer group',
          disabled && 'cursor-not-allowed opacity-50',
          className
        )}
      >
        <div className="relative flex-shrink-0">
          <input
            ref={ref}
            type="checkbox"
            id={checkboxId}
            checked={checked}
            disabled={disabled}
            className="sr-only peer"
            {...props}
          />
          <div
            className={clsx(
              'rounded border-2 transition-all duration-200',
              'flex items-center justify-center',
              styles.box,
              error
                ? 'border-red-500'
                : checked
                ? 'bg-[#FF6B35] border-[#FF6B35]'
                : 'border-gray-300 bg-white group-hover:border-[#FF6B35]',
              disabled && 'bg-gray-100'
            )}
          >
            <motion.div
              initial={false}
              animate={{
                scale: checked || indeterminate ? 1 : 0,
                opacity: checked || indeterminate ? 1 : 0,
              }}
              transition={{ duration: 0.15 }}
            >
              {indeterminate ? (
                <div className={clsx('bg-white rounded-sm', size === 'sm' ? 'w-2 h-0.5' : 'w-2.5 h-0.5')} />
              ) : (
                <Check className={clsx('text-white', styles.icon)} strokeWidth={3} />
              )}
            </motion.div>
          </div>
        </div>

        {(label || description) && (
          <div className="flex flex-col">
            {label && (
              <span className={clsx('text-gray-900 font-medium', styles.label)}>
                {label}
              </span>
            )}
            {description && (
              <span className="text-sm text-gray-500 mt-0.5">{description}</span>
            )}
          </div>
        )}
      </label>
    );
  }
);

Checkbox.displayName = 'Checkbox';
