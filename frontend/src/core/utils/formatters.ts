import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Date formatters
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(d)) return '-';
  return format(d, 'dd/MM/yyyy', { locale: ptBR });
}

export function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(d)) return '-';
  return format(d, 'dd/MM/yyyy HH:mm', { locale: ptBR });
}

export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(d)) return '-';
  return formatDistanceToNow(d, { addSuffix: true, locale: ptBR });
}

export function formatDateRange(start: Date, end: Date): string {
  return `${formatDate(start)} - ${formatDate(end)}`;
}

// Number formatters
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(value);
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
  }).format(value / 100);
}

export function formatCompactNumber(value: number): string {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)}B`;
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toString();
}

// Text formatters
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return `${text.slice(0, length)}...`;
}

export function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function initials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

// File formatters
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function getFileExtension(filename: string): string {
  const parts = filename.split('.');
  return parts.length > 1 ? parts.pop()?.toLowerCase() || '' : '';
}

export function isImageFile(filename: string): boolean {
  const ext = getFileExtension(filename);
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'].includes(ext);
}

export function isPdfFile(filename: string): boolean {
  return getFileExtension(filename) === 'pdf';
}

// Document formatters
export function formatCPF(cpf: string): string {
  const cleaned = cpf.replace(/\D/g, '');
  return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

export function formatCNPJ(cnpj: string): string {
  const cleaned = cnpj.replace(/\D/g, '');
  return cleaned.replace(
    /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
    '$1.$2.$3/$4-$5'
  );
}

export function formatCEP(cep: string): string {
  const cleaned = cep.replace(/\D/g, '');
  return cleaned.replace(/(\d{5})(\d{3})/, '$1-$2');
}

export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  }
  return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
}
