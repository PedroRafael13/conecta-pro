/**
 * Barrel file para tipos GED.
 * Re-exporta dos schemas gerados pelo Orval + aliases e utilitários usados pelas páginas.
 */

// Re-export schemas gerados
export type { FolderResponse } from './schemas/folderResponse';
export type { DocumentResponse } from './schemas/documentResponse';
export { FolderType } from './schemas/folderType';
export { DocumentType } from './schemas/documentType';
export { DocumentCategory } from './schemas/documentCategory';
export { DocumentStatus } from './schemas/documentStatus';
export { DocumentConfidentiality } from './schemas/documentConfidentiality';

// Aliases usados pelas páginas
export type { FolderResponse as Folder } from './schemas/folderResponse';
export type { DocumentResponse as Document } from './schemas/documentResponse';

// Re-export DocumentType/Category/Status como constantes usadas pelas páginas
export { DocumentType as DOCUMENT_TYPES } from './schemas/documentType';
export { DocumentCategory as DOCUMENT_CATEGORIES } from './schemas/documentCategory';
export { DocumentStatus as DOCUMENT_STATUS } from './schemas/documentStatus';

// GEDStats (tipo genérico baseado no endpoint /api/v1/ged/stats)
export interface GEDStats {
  total_documents: number;
  total_folders: number;
  total_size_bytes: number;
  documents_by_status: Record<string, number>;
  documents_by_type: Record<string, number>;
  documents_by_category: Record<string, number>;
  recent_uploads: number;
  pending_approvals: number;
  expiring_soon: number;
}

// FOLDER_TYPES com labels amigáveis
export const FOLDER_TYPES = [
  { value: 'sistema', label: 'Sistema' },
  { value: 'condominio', label: 'Condomínio' },
  { value: 'contrato', label: 'Contrato' },
  { value: 'funcionario', label: 'Funcionário' },
  { value: 'cliente', label: 'Cliente' },
  { value: 'projeto', label: 'Projeto' },
  { value: 'departamento', label: 'Departamento' },
  { value: 'pessoal', label: 'Pessoal' },
  { value: 'compartilhada', label: 'Compartilhada' },
  { value: 'arquivo', label: 'Arquivo' },
] as const;

// Utilitário: formata tamanho de arquivo
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

// Utilitário: retorna ícone baseado na extensão do arquivo
export function getFileIcon(extension: string): string {
  const ext = extension.toLowerCase().replace('.', '');
  const iconMap: Record<string, string> = {
    pdf: 'file-text',
    doc: 'file-text',
    docx: 'file-text',
    xls: 'file-spreadsheet',
    xlsx: 'file-spreadsheet',
    csv: 'file-spreadsheet',
    ppt: 'presentation',
    pptx: 'presentation',
    jpg: 'image',
    jpeg: 'image',
    png: 'image',
    gif: 'image',
    svg: 'image',
    zip: 'archive',
    rar: 'archive',
  };
  return iconMap[ext] || 'file';
}

// Types de DocumentKit (anteriormente re-exportados do service legado)
export type DocumentKit = {
  id: string;
  name: string;
  type: string;
  description?: string;
  items?: DocumentKitItem[];
  created_at?: string;
  updated_at?: string;
};

export type DocumentKitItem = {
  id: string;
  kit_id: string;
  document_type: string;
  name: string;
  required: boolean;
  status?: string;
};

export const KIT_TYPES = ['mensal', 'admissional', 'demissional', 'periodico', 'especial'] as const;

export const KIT_TYPE_LABELS: Record<string, string> = {
  mensal: 'Mensal',
  admissional: 'Admissional',
  demissional: 'Demissional',
  periodico: 'Periodico',
  especial: 'Especial',
};
