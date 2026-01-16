import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { AlertTriangle, Info, Loader2 } from 'lucide-react';

export interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void | Promise<void>;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
}

const variantStyles = {
  danger: {
    icon: AlertTriangle,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    buttonClass: 'btn-danger',
  },
  warning: {
    icon: AlertTriangle,
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600',
    buttonClass: 'bg-yellow-600 text-white hover:bg-yellow-700',
  },
  info: {
    icon: Info,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    buttonClass: 'btn-primary',
  },
};

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  variant = 'danger',
}: ConfirmDialogProps) {
  const [loading, setLoading] = useState(false);
  const styles = variantStyles[variant];
  const Icon = styles.icon;

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-lg bg-white shadow-xl transition-all">
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    <div
                      className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${styles.iconBg}`}
                    >
                      <Icon className={`w-5 h-5 ${styles.iconColor}`} />
                    </div>
                    <div>
                      <Dialog.Title className="text-lg font-semibold text-gray-900">
                        {title}
                      </Dialog.Title>
                      <Dialog.Description className="mt-2 text-sm text-gray-600">
                        {message}
                      </Dialog.Description>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 px-6 py-4 bg-gray-50 justify-end">
                  <button
                    type="button"
                    className="btn-ghost"
                    onClick={onClose}
                    disabled={loading}
                  >
                    {cancelLabel}
                  </button>
                  <button
                    type="button"
                    className={`btn ${styles.buttonClass}`}
                    onClick={handleConfirm}
                    disabled={loading}
                  >
                    {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                    {confirmLabel}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}

export default ConfirmDialog;
