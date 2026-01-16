import { useState, useEffect, useCallback } from 'react';
import type { MarketplaceService, ServiceProvider, ServiceRequest, ServiceFilters } from '../../types';
import { api } from '@/core/api';

interface ServicesResponse {
  services: MarketplaceService[];
}

export const useMarketplace = (filters?: ServiceFilters) => {
  const [services, setServices] = useState<MarketplaceService[]>([]);
  const [providers, setProviders] = useState<ServiceProvider[]>([]);
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadServices = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<ServicesResponse>('/crm/marketplace/services', { params: filters });
      setServices(data.services);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar servicos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const loadRequests = useCallback(async () => {
    try {
      const data = await api.get<ServiceRequest[]>('/crm/marketplace/requests');
      setRequests(data);
    } catch (err) {
      console.error('Erro ao carregar solicitacoes:', err);
    }
  }, []);

  const loadProviders = useCallback(async () => {
    try {
      const data = await api.get<ServiceProvider[]>('/crm/marketplace/providers');
      setProviders(data);
    } catch (err) {
      console.error('Erro ao carregar provedores:', err);
    }
  }, []);

  useEffect(() => {
    loadServices();
    loadRequests();
    loadProviders();
  }, [loadServices, loadRequests, loadProviders]);

  const searchServices = async (query: string, searchFilters?: ServiceFilters) => {
    setLoading(true);
    try {
      const data = await api.get<ServicesResponse>('/crm/marketplace/services/search', {
        params: { q: query, ...searchFilters }
      });
      setServices(data.services);
    } catch (err) {
      console.error('Erro na busca:', err);
      setServices([]);
    } finally {
      setLoading(false);
    }
  };

  const createServiceRequest = async (requestData: Omit<ServiceRequest, 'id' | 'createdAt' | 'updatedAt' | 'quotes'>) => {
    try {
      const newRequest = await api.post<ServiceRequest>('/crm/marketplace/requests', requestData);
      setRequests(prev => [newRequest, ...prev]);
      return newRequest;
    } catch (err) {
      console.error('Erro ao criar solicitacao:', err);
      throw err;
    }
  };

  const updateRequestStatus = async (requestId: string, status: ServiceRequest['status']) => {
    try {
      const updatedRequest = await api.patch<ServiceRequest>(`/crm/marketplace/requests/${requestId}`, { status });
      setRequests(prev =>
        prev.map(request =>
          request.id === requestId
            ? { ...request, ...updatedRequest }
            : request
        )
      );
      return updatedRequest;
    } catch (err) {
      console.error('Erro ao atualizar status:', err);
      throw err;
    }
  };

  const acceptQuote = async (requestId: string, quoteId: string) => {
    try {
      const response = await api.post(`/crm/marketplace/requests/${requestId}/accept-quote`, {
        quoteId
      });
      
      setRequests(prev => 
        prev.map(request => 
          request.id === requestId 
            ? { 
                ...request, 
                status: 'accepted',
                quotes: request.quotes.map(quote =>
                  quote.id === quoteId 
                    ? { ...quote, status: 'accepted' }
                    : { ...quote, status: 'rejected' }
                )
              } 
            : request
        )
      );
      return response;
    } catch (err) {
      console.error('Erro ao aceitar cotação:', err);
      throw err;
    }
  };

  const rejectQuote = async (requestId: string, quoteId: string, reason?: string) => {
    try {
      const response = await api.post(`/crm/marketplace/requests/${requestId}/reject-quote`, {
        quoteId,
        reason
      });
      
      setRequests(prev => 
        prev.map(request => 
          request.id === requestId 
            ? { 
                ...request,
                quotes: request.quotes.map(quote =>
                  quote.id === quoteId 
                    ? { ...quote, status: 'rejected' }
                    : quote
                )
              } 
            : request
        )
      );
      return response;
    } catch (err) {
      console.error('Erro ao rejeitar cotação:', err);
      throw err;
    }
  };

  const rateProvider = async (providerId: string, rating: number, comment?: string) => {
    try {
      const result = await api.post<{ newRating: number }>(`/crm/marketplace/providers/${providerId}/rate`, {
        rating,
        comment
      });

      setProviders(prev =>
        prev.map(provider =>
          provider.id === providerId
            ? { ...provider, rating: result.newRating }
            : provider
        )
      );
      return result;
    } catch (err) {
      console.error('Erro ao avaliar provedor:', err);
      throw err;
    }
  };

  const getServiceDetail = async (serviceId: string) => {
    try {
      const data = await api.get<MarketplaceService>(`/crm/marketplace/services/${serviceId}`);
      return data;
    } catch (err) {
      console.error('Erro ao carregar detalhes do servico:', err);
      throw err;
    }
  };

  const getProviderProfile = async (providerId: string) => {
    try {
      const data = await api.get<ServiceProvider>(`/crm/marketplace/providers/${providerId}`);
      return data;
    } catch (err) {
      console.error('Erro ao carregar perfil do provedor:', err);
      throw err;
    }
  };

  // Filter services by category
  const getServicesByCategory = (category: string) => {
    return services.filter(service => service.category === category);
  };

  // Get featured services
  const getFeaturedServices = () => {
    return services.filter(service => service.isPremium).slice(0, 6);
  };

  // Get my requests summary
  const getRequestsSummary = () => {
    return {
      total: requests.length,
      pending: requests.filter(r => r.status === 'pending').length,
      quoted: requests.filter(r => r.status === 'quoted').length,
      accepted: requests.filter(r => r.status === 'accepted').length,
      completed: requests.filter(r => r.status === 'completed').length,
    };
  };

  return {
    services,
    providers,
    requests,
    loading,
    error,
    loadServices,
    searchServices,
    createServiceRequest,
    updateRequestStatus,
    acceptQuote,
    rejectQuote,
    rateProvider,
    getServiceDetail,
    getProviderProfile,
    getServicesByCategory,
    getFeaturedServices,
    getRequestsSummary,
  };
};
