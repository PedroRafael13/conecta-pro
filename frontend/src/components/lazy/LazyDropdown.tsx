'use client';

import dynamic from 'next/dynamic';
import { ComponentProps } from 'react';
import { DropdownMenu } from '@/components/ui/dropdown-menu';

// Lazy load dos componentes de Dropdown
const DropdownMenuTrigger = dynamic(
  () => import('@/components/ui/dropdown-menu').then((mod) => mod.DropdownMenuTrigger),
  { ssr: false }
);

const DropdownMenuContent = dynamic(
  () => import('@/components/ui/dropdown-menu').then((mod) => mod.DropdownMenuContent),
  {
    loading: () => (
      <div className="animate-pulse rounded-md border bg-white p-2 shadow-md dark:bg-gray-800">
        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700" />
      </div>
    ),
  }
);

const DropdownMenuItem = dynamic(
  () => import('@/components/ui/dropdown-menu').then((mod) => mod.DropdownMenuItem),
  { ssr: false }
);

const DropdownMenuSeparator = dynamic(
  () => import('@/components/ui/dropdown-menu').then((mod) => mod.DropdownMenuSeparator),
  { ssr: false }
);

const DropdownMenuLabel = dynamic(
  () => import('@/components/ui/dropdown-menu').then((mod) => mod.DropdownMenuLabel),
  { ssr: false }
);

/**
 * Wrapper lazy-loaded para DropdownMenu
 * Use este componente ao invés do DropdownMenu direto para otimizar o bundle
 */
export function LazyDropdownMenu({
  children,
  ...props
}: ComponentProps<typeof DropdownMenu>) {
  return <DropdownMenu {...props}>{children}</DropdownMenu>;
}

// Re-exportar componentes lazy-loaded
export {
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
};
