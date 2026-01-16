export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadDate: string;
  lastModified: string;
  category: string;
  tags: string[];
  ocrText?: string;
  classification?: Classification;
  thumbnail?: string;
  url: string;
  version: number;
  uploadedBy: string;
  status: 'processing' | 'completed' | 'error';
}

export interface Classification {
  category: string;
  confidence: number;
  suggestedTags: string[];
  extractedEntities: {
    type: 'person' | 'company' | 'date' | 'amount';
    value: string;
    confidence: number;
  }[];
}

export interface DocumentCategory {
  id: string;
  name: string;
  color: string;
  icon: string;
  rules: ClassificationRule[];
}

export interface ClassificationRule {
  id: string;
  name: string;
  keywords: string[];
  patterns: string[];
  category: string;
  confidence: number;
}

export interface UploadProgress {
  fileId: string;
  fileName: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface SearchFilters {
  category?: string;
  tags?: string[];
  dateFrom?: string;
  dateTo?: string;
  fileType?: string;
  uploadedBy?: string;
}

export interface OCRResult {
  text: string;
  confidence: number;
  boundingBoxes: {
    text: string;
    x: number;
    y: number;
    width: number;
    height: number;
  }[];
}
