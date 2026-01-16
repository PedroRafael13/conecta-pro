export interface Document {
  id: string;
  name: string;
  originalName: string;
  mimeType: string;
  size: number;
  category: string;
  tags: string[];
  status: 'processing' | 'ready' | 'error';
  ocrStatus: 'pending' | 'processing' | 'completed' | 'failed';
  ocrText?: string;
  ocrConfidence?: number;
  classification?: DocumentClassification;
  versions: DocumentVersion[];
  comments: DocumentComment[];
  metadata: Record<string, string>;
  uploadedBy: {
    id: string;
    name: string;
  };
  createdAt: string;
  updatedAt: string;
}

export interface DocumentClassification {
  category: string;
  subcategory?: string;
  tags: string[];
  confidence: number;
  suggestedBy: 'ai' | 'user';
}

export interface DocumentVersion {
  id: string;
  version: number;
  size: number;
  uploadedBy: string;
  createdAt: string;
  changes?: string;
}

export interface DocumentComment {
  id: string;
  userId: string;
  userName: string;
  content: string;
  createdAt: string;
  position?: {
    page: number;
    x: number;
    y: number;
  };
}

export interface DocumentCategory {
  id: string;
  name: string;
  color: string;
  icon: string;
  count: number;
}

export interface GEDStats {
  totalDocuments: number;
  storageUsed: number;
  storageLimit: number;
  ocrProcessed: number;
  ocrPending: number;
  recentUploads: number;
}

export interface SearchResult {
  document: Document;
  highlights: string[];
  score: number;
}

export interface UploadProgress {
  id: string;
  fileName: string;
  progress: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
}
