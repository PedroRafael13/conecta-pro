export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

export interface TableColumn<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  render?: (value: unknown, row: T) => React.ReactNode;
}

export interface FilterConfig {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'contains' | 'in';
  value: unknown;
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export type ThemeMode = 'light' | 'dark' | 'system';

export interface Address {
  cep: string;
  street: string;
  number: string;
  complement?: string;
  neighborhood: string;
  city: string;
  state: string;
}

export interface Contact {
  id: string;
  type: 'email' | 'phone' | 'whatsapp';
  value: string;
  is_primary: boolean;
}

export interface Timestamps {
  created_at: string;
  updated_at: string;
}

export interface SoftDelete {
  deleted_at?: string;
  is_active: boolean;
}

export interface BaseEntity extends Timestamps {
  id: string;
}

export interface AuditInfo {
  created_by: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export type Status =
  | 'active'
  | 'inactive'
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'cancelled'
  | 'completed'
  | 'in_progress'
  | 'draft';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
  read: boolean;
  created_at: string;
  link?: string;
}

export interface FileUpload {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  uploaded_at: string;
}
