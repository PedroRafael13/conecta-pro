'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface Column<T = any> {
  key: string;
  label: string;
  render?: (item: T) => ReactNode;
  className?: string;
  headerClassName?: string;
  mobileLabel?: string; // Label customizado para mobile
  hiddenOnMobile?: boolean; // Ocultar coluna no mobile
}

interface ResponsiveTableProps<T = any> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
  rowKey: string | ((item: T) => string);
  emptyState?: ReactNode;
  className?: string;
  cardActions?: (item: T) => ReactNode; // Ações para modo card
}

export function ResponsiveTable<T = any>({
  data,
  columns,
  onRowClick,
  rowKey,
  emptyState,
  className,
  cardActions,
}: ResponsiveTableProps<T>) {
  const getRowKey = (item: T): string => {
    if (typeof rowKey === 'function') {
      return rowKey(item);
    }
    return (item as any)[rowKey];
  };

  const getValue = (item: T, column: Column<T>) => {
    if (column.render) {
      return column.render(item);
    }
    return (item as any)[column.key];
  };

  // Empty state
  if (data.length === 0) {
    return (
      <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-8">
        {emptyState || (
          <div className="text-center text-[hsl(var(--muted-foreground))]">
            Nenhum registro encontrado
          </div>
        )}
      </div>
    );
  }

  return (
    <>
      {/* Desktop Table */}
      <div className={cn('hidden md:block bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden', className)}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[hsl(var(--muted))]">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className={cn(
                      'px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider',
                      column.headerClassName
                    )}
                  >
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[hsl(var(--border))]">
              {data.map((item) => (
                <tr
                  key={getRowKey(item)}
                  onClick={() => onRowClick?.(item)}
                  className={cn(
                    'transition-colors',
                    onRowClick && 'hover:bg-[hsl(var(--muted))]/50 cursor-pointer'
                  )}
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={cn('px-4 py-4', column.className)}
                    >
                      {getValue(item, column)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-3">
        {data.map((item) => (
          <div
            key={getRowKey(item)}
            onClick={() => onRowClick?.(item)}
            className={cn(
              'bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4 transition-all',
              onRowClick && 'active:scale-[0.98] active:bg-[hsl(var(--muted))]/50'
            )}
          >
            {/* Campos principais */}
            <div className="space-y-3">
              {columns
                .filter((col) => !col.hiddenOnMobile)
                .map((column) => {
                  const value = getValue(item, column);
                  const label = column.mobileLabel || column.label;

                  return (
                    <div key={column.key} className="flex items-start justify-between gap-3">
                      <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider min-w-[80px]">
                        {label}
                      </span>
                      <div className="flex-1 text-right text-sm text-[hsl(var(--foreground))]">
                        {value}
                      </div>
                    </div>
                  );
                })}
            </div>

            {/* Ações no card */}
            {cardActions && (
              <div className="mt-4 pt-3 border-t border-[hsl(var(--border))] flex items-center justify-end gap-2">
                {cardActions(item)}
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  );
}

// Variação compacta para listas simples
interface ResponsiveListProps<T = any> {
  data: T[];
  renderItem: (item: T) => ReactNode;
  onItemClick?: (item: T) => void;
  rowKey: string | ((item: T) => string);
  emptyState?: ReactNode;
  className?: string;
}

export function ResponsiveList<T = any>({
  data,
  renderItem,
  onItemClick,
  rowKey,
  emptyState,
  className,
}: ResponsiveListProps<T>) {
  const getRowKey = (item: T): string => {
    if (typeof rowKey === 'function') {
      return rowKey(item);
    }
    return (item as any)[rowKey];
  };

  if (data.length === 0) {
    return (
      <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-8">
        {emptyState || (
          <div className="text-center text-[hsl(var(--muted-foreground))]">
            Nenhum registro encontrado
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={cn('space-y-2', className)}>
      {data.map((item) => (
        <div
          key={getRowKey(item)}
          onClick={() => onItemClick?.(item)}
          className={cn(
            'bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl transition-all',
            onItemClick && 'cursor-pointer hover:bg-[hsl(var(--muted))]/50 active:scale-[0.98]'
          )}
        >
          {renderItem(item)}
        </div>
      ))}
    </div>
  );
}
