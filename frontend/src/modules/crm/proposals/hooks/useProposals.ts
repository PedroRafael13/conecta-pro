import { useState, useEffect, useCallback } from 'react';
import type { Proposal, ProposalTemplate } from '../../types';
import { api } from '@/core/api';

export const useProposals = () => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [templates, setTemplates] = useState<ProposalTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProposals = useCallback(async () => {
    setLoading(true);
    try {
      const [proposalsData, templatesData] = await Promise.all([
        api.get<Proposal[]>('/crm/proposals'),
        api.get<ProposalTemplate[]>('/crm/proposal-templates')
      ]);

      setProposals(proposalsData);
      setTemplates(templatesData);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar propostas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProposals();
  }, [loadProposals]);

  const createProposal = async (proposalData: Omit<Proposal, 'id' | 'createdAt' | 'updatedAt' | 'version' | 'comments'>) => {
    try {
      const newProposal = await api.post<Proposal>('/crm/proposals', proposalData);
      setProposals(prev => [newProposal, ...prev]);
      return newProposal;
    } catch (err) {
      console.error('Erro ao criar proposta:', err);
      throw err;
    }
  };

  const updateProposal = async (id: string, updates: Partial<Proposal>) => {
    try {
      const updatedProposal = await api.patch<Proposal>(`/crm/proposals/${id}`, updates);
      setProposals(prev =>
        prev.map(proposal =>
          proposal.id === id ? { ...proposal, ...updatedProposal } : proposal
        )
      );
      return updatedProposal;
    } catch (err) {
      console.error('Erro ao atualizar proposta:', err);
      throw err;
    }
  };

  const sendProposal = async (id: string, recipientEmail?: string) => {
    try {
      const result = await api.post<{ sentAt: string }>(`/crm/proposals/${id}/send`, {
        recipientEmail
      });
      setProposals(prev =>
        prev.map(proposal =>
          proposal.id === id
            ? {
                ...proposal,
                status: 'sent' as const,
                sentAt: result.sentAt
              }
            : proposal
        )
      );
      return result;
    } catch (err) {
      console.error('Erro ao enviar proposta:', err);
      throw err;
    }
  };

  const duplicateProposal = async (id: string) => {
    try {
      const duplicated = await api.post<Proposal>(`/crm/proposals/${id}/duplicate`);
      setProposals(prev => [duplicated, ...prev]);
      return duplicated;
    } catch (err) {
      console.error('Erro ao duplicar proposta:', err);
      throw err;
    }
  };

  const generatePDF = async (id: string) => {
    try {
      const pdfData = await api.get<Blob>(`/crm/proposals/${id}/pdf`, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([pdfData]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `proposta-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erro ao gerar PDF:', err);
      throw err;
    }
  };

  const addComment = async (proposalId: string, comment: Omit<Proposal['comments'][0], 'id' | 'createdAt'>) => {
    try {
      type ProposalComment = Proposal['comments'][0];
      const newComment = await api.post<ProposalComment>(`/crm/proposals/${proposalId}/comments`, comment);
      setProposals(prev =>
        prev.map(proposal =>
          proposal.id === proposalId
            ? {
                ...proposal,
                comments: [newComment, ...proposal.comments]
              }
            : proposal
        )
      );
      return newComment;
    } catch (err) {
      console.error('Erro ao adicionar comentario:', err);
      throw err;
    }
  };

  const deleteProposal = async (id: string) => {
    try {
      await api.delete(`/crm/proposals/${id}`);
      setProposals(prev => prev.filter(proposal => proposal.id !== id));
    } catch (err) {
      console.error('Erro ao deletar proposta:', err);
      throw err;
    }
  };

  // Template management
  const createTemplate = async (templateData: Omit<ProposalTemplate, 'id' | 'createdAt'>) => {
    try {
      const newTemplate = await api.post<ProposalTemplate>('/crm/proposal-templates', templateData);
      setTemplates(prev => [newTemplate, ...prev]);
      return newTemplate;
    } catch (err) {
      console.error('Erro ao criar template:', err);
      throw err;
    }
  };

  const updateTemplate = async (id: string, updates: Partial<ProposalTemplate>) => {
    try {
      const updatedTemplate = await api.patch<ProposalTemplate>(`/crm/proposal-templates/${id}`, updates);
      setTemplates(prev =>
        prev.map(template =>
          template.id === id ? { ...template, ...updatedTemplate } : template
        )
      );
      return updatedTemplate;
    } catch (err) {
      console.error('Erro ao atualizar template:', err);
      throw err;
    }
  };

  const deleteTemplate = async (id: string) => {
    try {
      await api.delete(`/crm/proposal-templates/${id}`);
      setTemplates(prev => prev.filter(template => template.id !== id));
    } catch (err) {
      console.error('Erro ao deletar template:', err);
      throw err;
    }
  };

  return {
    proposals,
    templates,
    loading,
    error,
    loadProposals,
    createProposal,
    updateProposal,
    sendProposal,
    duplicateProposal,
    generatePDF,
    addComment,
    deleteProposal,
    createTemplate,
    updateTemplate,
    deleteTemplate,
  };
};
