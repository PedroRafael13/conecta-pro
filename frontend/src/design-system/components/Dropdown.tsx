'use client';

import { useState, useRef, useEffect, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/shared/utils/cn';
import { ChevronDown } from 'lucide-react';

export interface DropdownItem {
  value?: string;
  label: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
  danger?: boolean;
  onClick?: () => void;
  description?: string;
}

export interface DropdownProps {
  trigger: ReactNode;
  items: DropdownItem[];
  onSelect?: (value: string) => void;
  align?: 'left' | 'right';
  className?: string;
}

export function Dropdown({
  trigger,
  items,
  onSelect,
  align = 'left',
  className,
}: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (item: DropdownItem, index: number) => {
    if (item.onClick) {
      item.onClick();
    } else if (onSelect) {
      onSelect(item.value ?? String(index));
    }
    setIsOpen(false);
  };

  return (
    <div ref={dropdownRef} className={cn('relative inline-block', className)}>
      <div onClick={() => setIsOpen(!isOpen)} className="cursor-pointer">
        {trigger}
      </div>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className={cn(
              'absolute z-50 mt-2 min-w-[200px]',
              'bg-bg-elevated rounded-lg shadow-lg border border-border-subtle',
              'py-1 overflow-hidden',
              align === 'right' ? 'right-0' : 'left-0'
            )}
          >
            {items.map((item, index) => (
              <button
                key={item.value ?? index}
                disabled={item.disabled}
                onClick={() => handleSelect(item, index)}
                className={cn(
                  'w-full px-4 py-2 text-sm text-left',
                  'flex items-center gap-3',
                  'transition-colors duration-150',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  item.danger
                    ? 'text-danger hover:bg-danger/10'
                    : 'text-text-primary hover:bg-bg-tertiary'
                )}
              >
                {item.icon && <span className="w-4 h-4">{item.icon}</span>}
                <div className="flex flex-col">
                  <span>{item.label}</span>
                  {item.description && (
                    <span className="text-xs text-text-muted">{item.description}</span>
                  )}
                </div>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Simple Dropdown Button
export interface DropdownButtonProps {
  label: string;
  items: DropdownItem[];
  onSelect?: (value: string) => void;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function DropdownButton({
  label,
  items,
  onSelect,
  variant = 'default',
  size = 'md',
  className,
}: DropdownButtonProps) {
  const variantClasses = {
    default: 'bg-bg-tertiary text-text-primary border border-border-default hover:bg-bg-elevated',
    outline: 'bg-transparent border-2 border-accent-primary text-accent-primary hover:bg-accent-primary/10',
    ghost: 'bg-transparent text-text-secondary hover:bg-bg-tertiary hover:text-text-primary',
  };

  const sizeClasses = {
    sm: 'h-8 px-3 text-xs gap-1',
    md: 'h-10 px-4 text-sm gap-2',
    lg: 'h-12 px-6 text-base gap-2',
  };

  return (
    <Dropdown
      items={items}
      onSelect={onSelect}
      trigger={
        <button
          className={cn(
            'inline-flex items-center justify-center rounded-lg font-medium',
            'transition-all duration-200',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary',
            variantClasses[variant],
            sizeClasses[size],
            className
          )}
        >
          {label}
          <ChevronDown className="w-4 h-4" />
        </button>
      }
    />
  );
}
