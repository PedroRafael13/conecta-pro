import { useState, useEffect, useCallback } from 'react';
import type { Deal, DealStage, DealFilters } from '../../types';
import { api } from '@/core/api';

interface DealsResponse {
  deals: Deal[];
  total: number;
}

export const useDeals = (filters?: DealFilters) => {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [stages, setStages] = useState<DealStage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const loadDeals = useCallback(async () => {
    setLoading(true);
    try {
      const [dealsData, stagesData] = await Promise.all([
        api.get<DealsResponse>('/crm/deals', { params: filters }),
        api.get<DealStage[]>('/crm/deal-stages')
      ]);

      setDeals(dealsData.deals);
      setTotal(dealsData.total);
      setStages(stagesData);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar deals');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadDeals();
  }, [loadDeals]);

  const createDeal = async (dealData: Omit<Deal, 'id' | 'createdAt' | 'updatedAt' | 'activities'>) => {
    try {
      const newDeal = await api.post<Deal>('/crm/deals', dealData);
      setDeals(prev => [newDeal, ...prev]);
      setTotal(prev => prev + 1);
      return newDeal;
    } catch (err) {
      console.error('Erro ao criar deal:', err);
      throw err;
    }
  };

  const updateDeal = async (id: string, updates: Partial<Deal>) => {
    try {
      const updatedDeal = await api.patch<Deal>(`/crm/deals/${id}`, updates);
      setDeals(prev =>
        prev.map(deal =>
          deal.id === id ? { ...deal, ...updatedDeal } : deal
        )
      );
      return updatedDeal;
    } catch (err) {
      console.error('Erro ao atualizar deal:', err);
      throw err;
    }
  };

  const updateDealStage = async (dealId: string, newStageId: string) => {
    try {
      const updatedDeal = await api.patch<Deal>(`/crm/deals/${dealId}/stage`, {
        stageId: newStageId
      });

      setDeals(prev =>
        prev.map(deal =>
          deal.id === dealId ? { ...deal, ...updatedDeal } : deal
        )
      );
      return updatedDeal;
    } catch (err) {
      console.error('Erro ao mover deal:', err);
      throw err;
    }
  };

  const deleteDeal = async (id: string) => {
    try {
      await api.delete(`/crm/deals/${id}`);
      setDeals(prev => prev.filter(deal => deal.id !== id));
      setTotal(prev => prev - 1);
    } catch (err) {
      console.error('Erro ao deletar deal:', err);
      throw err;
    }
  };

  const addActivity = async (dealId: string, activity: Omit<Deal['activities'][0], 'id'>) => {
    try {
      type DealActivity = Deal['activities'][0];
      const newActivity = await api.post<DealActivity>(`/crm/deals/${dealId}/activities`, activity);
      setDeals(prev =>
        prev.map(deal =>
          deal.id === dealId
            ? {
                ...deal,
                activities: [newActivity, ...deal.activities]
              }
            : deal
        )
      );
      return newActivity;
    } catch (err) {
      console.error('Erro ao adicionar atividade:', err);
      throw err;
    }
  };

  // Organize deals by stage for Kanban view
  const dealsByStage = stages.reduce((acc, stage) => {
    acc[stage.id] = deals.filter(deal => deal.stage.id === stage.id);
    return acc;
  }, {} as Record<string, Deal[]>);

  // Calculate pipeline value
  const pipelineValue = deals.reduce((sum, deal) => {
    if (!deal.stage.isClosedLost) {
      return sum + (deal.value * deal.probability / 100);
    }
    return sum;
  }, 0);

  // Calculate won/lost deals
  const wonDeals = deals.filter(deal => deal.stage.isClosedWon);
  const lostDeals = deals.filter(deal => deal.stage.isClosedLost);
  const wonValue = wonDeals.reduce((sum, deal) => sum + deal.value, 0);

  return {
    deals,
    stages,
    dealsByStage,
    loading,
    error,
    total,
    pipelineValue,
    wonDeals,
    lostDeals,
    wonValue,
    loadDeals,
    createDeal,
    updateDeal,
    updateDealStage,
    deleteDeal,
    addActivity,
  };
};
