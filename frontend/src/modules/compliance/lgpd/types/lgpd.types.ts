export interface DataSubject {
  id: string;
  name: string;
  email: string;
  cpf: string;
  phone?: string;
  consents: Consent[];
  requests: RightsRequest[];
  createdAt: string;
  updatedAt: string;
}

export interface Consent {
  id: string;
  subjectId: string;
  type: 'marketing' | 'analytics' | 'essential' | 'third_party';
  purpose: string;
  status: 'active' | 'revoked' | 'expired';
  grantedAt: string;
  expiresAt: string;
  revokedAt?: string;
  version: string;
  ipAddress?: string;
}

export interface RightsRequest {
  id: string;
  subjectId: string;
  subjectName: string;
  type: 'acesso' | 'retificacao' | 'portabilidade' | 'exclusao' | 'oposicao';
  status: 'pendente' | 'em_andamento' | 'concluida' | 'recusada';
  description: string;
  createdAt: string;
  deadline: string;
  completedAt?: string;
  assignedTo?: {
    id: string;
    name: string;
  };
  attachments: string[];
  response?: string;
}

export interface ConsentTemplate {
  id: string;
  name: string;
  type: Consent['type'];
  content: string;
  version: string;
  isActive: boolean;
  validityDays: number;
  createdAt: string;
}

export interface LGPDStats {
  totalSubjects: number;
  activeConsents: number;
  pendingRequests: number;
  expiringConsents: number;
  complianceScore: number;
}
