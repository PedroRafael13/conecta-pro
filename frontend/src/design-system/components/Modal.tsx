'use client';

import {
  forwardRef,
  type HTMLAttributes,
  type ReactNode,
  useEffect,
  useCallback,
} from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '@/shared/utils/cn';
import { Button } from './Button';

export interface ModalProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  isOpen: boolean;
  onClose: () => void;
  title?: ReactNode;
  description?: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  showCloseButton?: boolean;
  closeOnOverlayClick?: boolean;
  closeOnEsc?: boolean;
  footer?: ReactNode;
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-[calc(100vw-2rem)] max-h-[calc(100vh-2rem)]',
};

export const Modal = forwardRef<HTMLDivElement, ModalProps>(
  (
    {
      isOpen,
      onClose,
      title,
      description,
      size = 'md',
      showCloseButton = true,
      closeOnOverlayClick = true,
      closeOnEsc = true,
      footer,
      children,
      className,
      ...props
    },
    ref
  ) => {
    const handleEscKey = useCallback(
      (e: KeyboardEvent) => {
        if (e.key === 'Escape' && closeOnEsc) {
          onClose();
        }
      },
      [closeOnEsc, onClose]
    );

    useEffect(() => {
      if (isOpen) {
        document.addEventListener('keydown', handleEscKey);
        document.body.style.overflow = 'hidden';
      }
      return () => {
        document.removeEventListener('keydown', handleEscKey);
        document.body.style.overflow = 'unset';
      };
    }, [isOpen, handleEscKey]);

    if (typeof document === 'undefined') return null;

    return createPortal(
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={closeOnOverlayClick ? onClose : undefined}
              aria-hidden="true"
            />

            {/* Modal Content */}
            <motion.div
              ref={ref}
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className={cn(
                'relative w-full bg-bg-secondary rounded-2xl border border-border-subtle shadow-dropdown',
                'max-h-[90vh] overflow-hidden flex flex-col',
                sizeClasses[size],
                className
              )}
              role="dialog"
              aria-modal="true"
              aria-labelledby={title ? 'modal-title' : undefined}
              aria-describedby={description ? 'modal-description' : undefined}
            >
              {/* Header */}
              {(title || showCloseButton) && (
                <div className="px-6 py-4 border-b border-border-subtle flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    {title && (
                      <h2
                        id="modal-title"
                        className="text-lg font-semibold text-text-primary"
                      >
                        {title}
                      </h2>
                    )}
                    {description && (
                      <p
                        id="modal-description"
                        className="text-sm text-text-secondary"
                      >
                        {description}
                      </p>
                    )}
                  </div>
                  {showCloseButton && (
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={onClose}
                      aria-label="Fechar modal"
                      className="flex-shrink-0 -mr-2 -mt-1"
                    >
                      <X className="h-5 w-5" />
                    </Button>
                  )}
                </div>
              )}

              {/* Body */}
              <div className="flex-1 overflow-y-auto p-6">{children}</div>

              {/* Footer */}
              {footer && (
                <div className="px-6 py-4 border-t border-border-subtle bg-bg-primary/50 flex items-center justify-end gap-3">
                  {footer}
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>,
      document.body
    );
  }
);

Modal.displayName = 'Modal';
