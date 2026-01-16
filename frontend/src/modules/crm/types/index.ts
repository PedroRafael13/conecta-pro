// === CONTACTS ===
export interface Contact {
  id: string;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  position?: string;
  avatar?: string;
  tags: string[];
  status: 'active' | 'inactive' | 'lead' | 'customer';
  leadScore?: number;
  segment: 'enterprise' | 'mid-market' | 'small-business';
  source: 'website' | 'referral' | 'cold-outreach' | 'event' | 'social-media';
  assignedTo?: string;
  createdAt: string;
  lastContact?: string;
  interactions: Interaction[];
}

export interface Interaction {
  id: string;
  type: 'call' | 'email' | 'meeting' | 'note' | 'proposal' | 'task';
  subject: string;
  description?: string;
  date: string;
  duration?: number; // minutes
  outcome?: string;
  nextAction?: string;
  createdBy: string;
  attachments?: string[];
}

// === DEALS ===
export interface Deal {
  id: string;
  title: string;
  contactId: string;
  contact?: Contact;
  value: number;
  currency: 'BRL' | 'USD';
  stage: DealStage;
  probability: number; // 0-100
  expectedCloseDate: string;
  actualCloseDate?: string;
  assignedTo: string;
  tags: string[];
  description?: string;
  activities: DealActivity[];
  products: DealProduct[];
  documents: string[];
  createdAt: string;
  updatedAt: string;
  lostReason?: string;
  competitors?: string[];
}

export interface DealStage {
  id: string;
  name: string;
  order: number;
  probability: number;
  color: string;
  isClosedWon: boolean;
  isClosedLost: boolean;
}

export interface DealActivity {
  id: string;
  type: 'note' | 'call' | 'meeting' | 'email' | 'proposal' | 'stage-change';
  description: string;
  date: string;
  createdBy: string;
  previousStage?: string;
  newStage?: string;
}

export interface DealProduct {
  id: string;
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  total: number;
}

// === PROPOSALS ===
export interface Proposal {
  id: string;
  dealId?: string;
  contactId: string;
  title: string;
  status: 'draft' | 'sent' | 'viewed' | 'accepted' | 'rejected' | 'expired';
  templateId?: string;
  sections: ProposalSection[];
  total: number;
  currency: 'BRL' | 'USD';
  validUntil: string;
  sentAt?: string;
  viewedAt?: string;
  respondedAt?: string;
  signedBy?: string;
  signedAt?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  comments: ProposalComment[];
  version: number;
}

export interface ProposalSection {
  id: string;
  type: 'intro' | 'products' | 'services' | 'terms' | 'pricing' | 'custom';
  title: string;
  content: string;
  order: number;
  products?: ProposalProduct[];
}

export interface ProposalProduct {
  id: string;
  name: string;
  description?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  total: number;
}

export interface ProposalComment {
  id: string;
  text: string;
  createdBy: string;
  createdAt: string;
  isInternal: boolean;
}

export interface ProposalTemplate {
  id: string;
  name: string;
  description?: string;
  sections: Omit<ProposalSection, 'id'>[];
  isActive: boolean;
  createdBy: string;
  createdAt: string;
}

// === MARKETPLACE B2B ===
export interface MarketplaceService {
  id: string;
  providerId: string;
  provider: ServiceProvider;
  title: string;
  description: string;
  category: string;
  subcategory?: string;
  images: string[];
  pricing: ServicePricing[];
  features: string[];
  tags: string[];
  rating: number;
  reviewCount: number;
  isActive: boolean;
  isPremium: boolean;
  createdAt: string;
}

export interface ServiceProvider {
  id: string;
  companyName: string;
  contactName: string;
  email: string;
  phone: string;
  avatar?: string;
  description?: string;
  location: string;
  website?: string;
  certifications: string[];
  portfolio: PortfolioItem[];
  rating: number;
  completedProjects: number;
  responseTime: number; // hours
  isVerified: boolean;
}

export interface ServicePricing {
  id: string;
  name: string;
  description?: string;
  price: number;
  currency: 'BRL' | 'USD';
  period?: 'hour' | 'day' | 'week' | 'month' | 'project';
  features: string[];
}

export interface PortfolioItem {
  id: string;
  title: string;
  description: string;
  images: string[];
  category: string;
  completedAt: string;
  clientTestimonial?: string;
}

export interface ServiceRequest {
  id: string;
  serviceId: string;
  service: MarketplaceService;
  requesterId: string;
  requester: Contact;
  status: 'pending' | 'quoted' | 'accepted' | 'rejected' | 'completed' | 'cancelled';
  description: string;
  budget?: number;
  deadline?: string;
  quotes: ServiceQuote[];
  createdAt: string;
  updatedAt: string;
}

export interface ServiceQuote {
  id: string;
  providerId: string;
  provider: ServiceProvider;
  amount: number;
  currency: 'BRL' | 'USD';
  description: string;
  deliveryTime: number; // days
  terms: string;
  validUntil: string;
  status: 'pending' | 'accepted' | 'rejected';
  createdAt: string;
}

// === ANALYTICS ===
export interface CRMStats {
  contacts: {
    total: number;
    leads: number;
    customers: number;
    active: number;
  };
  deals: {
    total: number;
    value: number;
    wonValue: number;
    avgDealValue: number;
    conversionRate: number;
    avgDealCycle: number; // days
  };
  proposals: {
    total: number;
    sent: number;
    accepted: number;
    acceptanceRate: number;
    avgResponseTime: number; // hours
  };
  marketplace: {
    activeServices: number;
    totalRequests: number;
    completionRate: number;
    avgRating: number;
  };
}

// === FILTERS ===
export interface ContactFilters {
  status?: Contact['status'][];
  segment?: Contact['segment'][];
  source?: Contact['source'][];
  tags?: string[];
  assignedTo?: string[];
  leadScoreMin?: number;
  leadScoreMax?: number;
  dateFrom?: string;
  dateTo?: string;
}

export interface DealFilters {
  stages?: string[];
  assignedTo?: string[];
  valueMin?: number;
  valueMax?: number;
  probabilityMin?: number;
  probabilityMax?: number;
  expectedCloseFrom?: string;
  expectedCloseTo?: string;
  tags?: string[];
}

export interface ServiceFilters {
  categories?: string[];
  priceMin?: number;
  priceMax?: number;
  rating?: number;
  location?: string;
  isVerified?: boolean;
  isPremium?: boolean;
}
