'use client';

import {
  forwardRef,
  type HTMLAttributes,
  type ThHTMLAttributes,
  type TdHTMLAttributes,
  type ReactNode,
  useState,
} from 'react';
import { cn } from '@/shared/utils/cn';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';

// Table Container
export const TableContainer = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'overflow-x-auto rounded-xl border border-border-subtle',
      className
    )}
    {...props}
  />
));
TableContainer.displayName = 'TableContainer';

// Table
export const Table = forwardRef<
  HTMLTableElement,
  HTMLAttributes<HTMLTableElement>
>(({ className, ...props }, ref) => (
  <table
    ref={ref}
    className={cn('w-full text-sm', className)}
    {...props}
  />
));
Table.displayName = 'Table';

// Table Header
export const TableHeader = forwardRef<
  HTMLTableSectionElement,
  HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead
    ref={ref}
    className={cn('bg-bg-tertiary border-b border-border-default', className)}
    {...props}
  />
));
TableHeader.displayName = 'TableHeader';

// Table Body
export const TableBody = forwardRef<
  HTMLTableSectionElement,
  HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={cn('divide-y divide-border-subtle', className)}
    {...props}
  />
));
TableBody.displayName = 'TableBody';

// Table Row
export interface TableRowProps extends HTMLAttributes<HTMLTableRowElement> {
  selected?: boolean;
  clickable?: boolean;
}

export const TableRow = forwardRef<HTMLTableRowElement, TableRowProps>(
  ({ className, selected, clickable, ...props }, ref) => (
    <tr
      ref={ref}
      className={cn(
        'bg-bg-secondary transition-colors duration-150',
        clickable && 'hover:bg-bg-tertiary cursor-pointer',
        selected && 'bg-accent-primary/5',
        className
      )}
      {...props}
    />
  )
);
TableRow.displayName = 'TableRow';

// Table Head Cell
export interface TableHeadProps extends ThHTMLAttributes<HTMLTableCellElement> {
  sortable?: boolean;
  sortDirection?: 'asc' | 'desc' | null;
  onSort?: () => void;
}

export const TableHead = forwardRef<HTMLTableCellElement, TableHeadProps>(
  ({ className, sortable, sortDirection, onSort, children, ...props }, ref) => (
    <th
      ref={ref}
      className={cn(
        'px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider',
        sortable && 'cursor-pointer select-none hover:text-text-primary',
        className
      )}
      onClick={sortable ? onSort : undefined}
      {...props}
    >
      <div className="flex items-center gap-1">
        {children}
        {sortable && (
          <span className="text-text-muted">
            {sortDirection === 'asc' ? (
              <ChevronUp className="w-4 h-4" />
            ) : sortDirection === 'desc' ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronsUpDown className="w-4 h-4" />
            )}
          </span>
        )}
      </div>
    </th>
  )
);
TableHead.displayName = 'TableHead';

// Table Cell
export const TableCell = forwardRef<
  HTMLTableCellElement,
  TdHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <td
    ref={ref}
    className={cn('px-4 py-3 text-text-primary', className)}
    {...props}
  />
));
TableCell.displayName = 'TableCell';

// Empty State
interface TableEmptyProps {
  icon?: ReactNode;
  title?: string;
  description?: string;
  action?: ReactNode;
  colSpan?: number;
}

export function TableEmpty({
  icon,
  title = 'Nenhum registro encontrado',
  description,
  action,
  colSpan = 1,
}: TableEmptyProps) {
  return (
    <tr>
      <td colSpan={colSpan} className="py-12">
        <div className="flex flex-col items-center justify-center text-center">
          {icon && (
            <div className="mb-4 text-text-muted opacity-50">{icon}</div>
          )}
          <h3 className="text-lg font-medium text-text-primary mb-1">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-text-secondary mb-4">{description}</p>
          )}
          {action}
        </div>
      </td>
    </tr>
  );
}

// Data Table (com features built-in)
export interface Column<T> {
  key: keyof T | string;
  header: string;
  sortable?: boolean;
  render?: (row: T, index: number) => ReactNode;
  className?: string;
  width?: string | number;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor?: (row: T) => string;
  loading?: boolean;
  emptyState?: TableEmptyProps;
  onRowClick?: (row: T) => void;
  selectedRows?: string[];
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  loading,
  emptyState,
  onRowClick,
  selectedRows = [],
  className,
}: DataTableProps<T>) {
  // Default key extractor uses 'id' property or index
  const getKey = keyExtractor ?? ((row: T, index?: number) => {
    if (typeof row === 'object' && row !== null && 'id' in row) {
      return String((row as { id: unknown }).id);
    }
    return String(index ?? 0);
  });
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const handleSort = (key: string) => {
    setSortConfig((current) => {
      if (current?.key === key) {
        if (current.direction === 'asc') {
          return { key, direction: 'desc' };
        }
        return null;
      }
      return { key, direction: 'asc' };
    });
  };

  const sortedData = sortConfig
    ? [...data].sort((a, b) => {
        const aValue = (a as Record<string, unknown>)[sortConfig.key];
        const bValue = (b as Record<string, unknown>)[sortConfig.key];

        if (aValue === bValue) return 0;

        const comparison = aValue! < bValue! ? -1 : 1;
        return sortConfig.direction === 'asc' ? comparison : -comparison;
      })
    : data;

  if (loading) {
    return (
      <TableContainer className={className}>
        <Table>
          <TableHeader>
            <tr>
              {columns.map((col) => (
                <TableHead key={String(col.key)}>{col.header}</TableHead>
              ))}
            </tr>
          </TableHeader>
          <TableBody>
            {Array.from({ length: 5 }).map((_, i) => (
              <TableRow key={i}>
                {columns.map((col) => (
                  <TableCell key={String(col.key)}>
                    <div className="h-4 bg-bg-tertiary rounded animate-pulse" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return (
    <TableContainer className={className}>
      <Table>
        <TableHeader>
          <tr>
            {columns.map((col) => (
              <TableHead
                key={String(col.key)}
                sortable={col.sortable}
                sortDirection={
                  sortConfig?.key === col.key ? sortConfig.direction : null
                }
                onSort={() => col.sortable && handleSort(String(col.key))}
                style={{ width: col.width }}
                className={col.className}
              >
                {col.header}
              </TableHead>
            ))}
          </tr>
        </TableHeader>
        <TableBody>
          {sortedData.length === 0 ? (
            <TableEmpty {...emptyState} colSpan={columns.length} />
          ) : (
            sortedData.map((row, index) => {
              const key = getKey(row, index);
              return (
                <TableRow
                  key={key}
                  clickable={!!onRowClick}
                  selected={selectedRows.includes(key)}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((col) => (
                    <TableCell
                      key={String(col.key)}
                      className={col.className}
                    >
                      {col.render
                        ? col.render(row, index)
                        : String((row as Record<string, unknown>)[String(col.key)] ?? '')}
                    </TableCell>
                  ))}
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
