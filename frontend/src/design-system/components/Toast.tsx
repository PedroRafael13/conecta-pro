'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle2, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/shared/utils/cn';

// Types
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  success: (title: string, description?: string) => void;
  error: (title: string, description?: string) => void;
  warning: (title: string, description?: string) => void;
  info: (title: string, description?: string) => void;
}

// Context
const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

// Provider
interface ToastProviderProps {
  children: ReactNode;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export function ToastProvider({ children, position = 'top-right' }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { ...toast, id }]);

    // Auto remove after duration
    const duration = toast.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const success = useCallback(
    (title: string, description?: string) => {
      addToast({ type: 'success', title, description });
    },
    [addToast]
  );

  const error = useCallback(
    (title: string, description?: string) => {
      addToast({ type: 'error', title, description });
    },
    [addToast]
  );

  const warning = useCallback(
    (title: string, description?: string) => {
      addToast({ type: 'warning', title, description });
    },
    [addToast]
  );

  const info = useCallback(
    (title: string, description?: string) => {
      addToast({ type: 'info', title, description });
    },
    [addToast]
  );

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  };

  return (
    <ToastContext.Provider
      value={{ toasts, addToast, removeToast, success, error, warning, info }}
    >
      {children}
      <div
        className={cn(
          'fixed z-[100] flex flex-col gap-2 pointer-events-none',
          positionClasses[position]
        )}
      >
        <AnimatePresence mode="popLayout">
          {toasts.map((toast) => (
            <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

// Toast Item
interface ToastItemProps {
  toast: Toast;
  onClose: () => void;
}

const toastConfig = {
  success: {
    icon: CheckCircle2,
    className: 'border-success/30 bg-success/5',
    iconClassName: 'text-success',
  },
  error: {
    icon: AlertCircle,
    className: 'border-danger/30 bg-danger/5',
    iconClassName: 'text-danger',
  },
  warning: {
    icon: AlertTriangle,
    className: 'border-warning/30 bg-warning/5',
    iconClassName: 'text-warning',
  },
  info: {
    icon: Info,
    className: 'border-info/30 bg-info/5',
    iconClassName: 'text-info',
  },
};

function ToastItem({ toast, onClose }: ToastItemProps) {
  const config = toastConfig[toast.type];
  const Icon = config.icon;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.15 } }}
      className={cn(
        'pointer-events-auto w-80 rounded-xl border bg-bg-secondary/95 backdrop-blur-xl shadow-dropdown',
        'flex items-start gap-3 p-4',
        config.className
      )}
    >
      <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', config.iconClassName)} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary">{toast.title}</p>
        {toast.description && (
          <p className="text-sm text-text-secondary mt-1">{toast.description}</p>
        )}
      </div>
      <button
        onClick={onClose}
        className="flex-shrink-0 p-1 rounded-md text-text-muted hover:text-text-primary hover:bg-bg-tertiary transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
}

// Standalone Toast (for use without provider)
export function showToast(toast: Omit<Toast, 'id'>) {
  // This is a placeholder for server-side or edge cases
  // In a real app, you'd use a global event emitter or similar
  console.warn('showToast called outside of ToastProvider context');
}
