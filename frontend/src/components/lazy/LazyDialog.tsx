'use client';

import dynamic from 'next/dynamic';
import { ComponentProps } from 'react';
import { Dialog } from '@/components/ui/dialog';

// Lazy load do Dialog Root e componentes internos
const DialogContent = dynamic(
  () => import('@/components/ui/dialog').then((mod) => mod.DialogContent),
  {
    loading: () => (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div className="animate-pulse rounded-lg bg-white p-6 dark:bg-gray-800">
          <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    ),
  }
);

const DialogHeader = dynamic(
  () => import('@/components/ui/dialog').then((mod) => mod.DialogHeader),
  { ssr: false }
);

const DialogTitle = dynamic(
  () => import('@/components/ui/dialog').then((mod) => mod.DialogTitle),
  { ssr: false }
);

const DialogDescription = dynamic(
  () => import('@/components/ui/dialog').then((mod) => mod.DialogDescription),
  { ssr: false }
);

const DialogFooter = dynamic(
  () => import('@/components/ui/dialog').then((mod) => mod.DialogFooter),
  { ssr: false }
);

/**
 * Wrapper lazy-loaded para Dialog
 * Use este componente ao invés do Dialog direto para otimizar o bundle
 */
export function LazyDialog({
  children,
  ...props
}: ComponentProps<typeof Dialog>) {
  return <Dialog {...props}>{children}</Dialog>;
}

// Re-exportar componentes lazy-loaded
export { DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter };
