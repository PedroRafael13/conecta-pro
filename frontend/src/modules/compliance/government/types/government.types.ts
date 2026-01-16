export interface GovernmentAPI {
  id: string;
  name: string;
  code: string;
  description: string;
  status: 'online' | 'offline' | 'manutencao';
  lastSync: string;
  nextSync?: string;
  successRate: number;
  icon: string;
}

export interface Obligation {
  id: string;
  name: string;
  apiId: string;
  apiName: string;
  type: 'mensal' | 'anual' | 'eventual';
  deadline: string;
  status: 'pendente' | 'enviado' | 'aprovado' | 'rejeitado';
  documents: string[];
  submittedAt?: string;
  responseAt?: string;
  responseMessage?: string;
}

export interface SyncLog {
  id: string;
  apiId: string;
  apiName: string;
  status: 'success' | 'error' | 'warning';
  message: string;
  startedAt: string;
  completedAt: string;
  recordsProcessed: number;
  errors: string[];
}

export interface GovernmentStats {
  apisConnected: number;
  obligationsPending: number;
  syncSuccess: number;
  nearDeadlines: number;
}
