export interface BiddingOpportunity {
  id: string;
  title: string;
  number: string;
  organ: string;
  modalidade: 'pregao' | 'concorrencia' | 'tomada_precos' | 'convite' | 'leilao';
  status: 'nova' | 'em_analise' | 'proposta_enviada' | 'aguardando_resultado' | 'ganha' | 'perdida';
  value: number;
  publishedAt: string;
  deadline: string;
  aiScore: number;
  categories: string[];
  requirements: string[];
  documents: string[];
  matchReasons: string[];
}

export interface BiddingProposal {
  id: string;
  opportunityId: string;
  opportunityTitle: string;
  status: 'rascunho' | 'em_revisao' | 'aprovada' | 'enviada' | 'aceita' | 'rejeitada';
  value: number;
  createdAt: string;
  updatedAt: string;
  submittedAt?: string;
  documents: ProposalDocument[];
  timeline: ProposalEvent[];
}

export interface ProposalDocument {
  id: string;
  name: string;
  type: string;
  required: boolean;
  uploaded: boolean;
  uploadedAt?: string;
}

export interface ProposalEvent {
  id: string;
  action: string;
  user: string;
  timestamp: string;
  details?: string;
}

export interface BiddingStats {
  totalOpportunities: number;
  proposalsSent: number;
  winRate: number;
  avgROI: number;
  totalValue: number;
}
