import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  title?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastState {
  toasts: Toast[];
}

interface ToastActions {
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  success: (message: string, title?: string) => void;
  error: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
}

type ToastStore = ToastState & ToastActions;

const generateId = () => Math.random().toString(36).substring(2, 9);

export const useToastStore = create<ToastStore>((set, get) => ({
  toasts: [],

  addToast: (toast) => {
    const id = generateId();
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }],
    }));

    // Auto remove after duration
    const duration = toast.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => {
        get().removeToast(id);
      }, duration);
    }

    return id;
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }));
  },

  clearToasts: () => set({ toasts: [] }),

  success: (message, title) => {
    get().addToast({ type: 'success', message, title });
  },

  error: (message, title) => {
    get().addToast({ type: 'error', message, title, duration: 8000 });
  },

  warning: (message, title) => {
    get().addToast({ type: 'warning', message, title });
  },

  info: (message, title) => {
    get().addToast({ type: 'info', message, title });
  },
}));

export default useToastStore;
