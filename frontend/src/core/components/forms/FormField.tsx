import { ReactNode } from 'react';
import { clsx } from 'clsx';

interface FormFieldProps {
  label?: string;
  error?: string;
  required?: boolean;
  hint?: string;
  children: ReactNode;
  className?: string;
}

export function FormField({
  label,
  error,
  required,
  hint,
  children,
  className
}: FormFieldProps) {
  return (
    <div className={clsx('w-full', className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      {children}
      {hint && !error && (
        <p className="mt-1 text-sm text-gray-500">{hint}</p>
      )}
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  );
}
