import { useState, useEffect, useCallback } from 'react';
import type { Contact, ContactFilters } from '../../types';
import { api } from '@/core/api';

interface ContactsResponse {
  contacts: Contact[];
  total: number;
}

export const useContacts = (filters?: ContactFilters) => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const loadContacts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get<ContactsResponse>('/crm/contacts', { params: filters });
      setContacts(response.contacts);
      setTotal(response.total);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar contatos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadContacts();
  }, [loadContacts]);

  const createContact = async (contactData: Omit<Contact, 'id' | 'createdAt' | 'interactions'>) => {
    try {
      const newContact = await api.post<Contact>('/crm/contacts', contactData);
      setContacts(prev => [newContact, ...prev]);
      setTotal(prev => prev + 1);
      return newContact;
    } catch (err) {
      console.error('Erro ao criar contato:', err);
      throw err;
    }
  };

  const updateContact = async (id: string, updates: Partial<Contact>) => {
    try {
      const updatedContact = await api.patch<Contact>(`/crm/contacts/${id}`, updates);
      setContacts(prev =>
        prev.map(contact =>
          contact.id === id ? { ...contact, ...updatedContact } : contact
        )
      );
      return updatedContact;
    } catch (err) {
      console.error('Erro ao atualizar contato:', err);
      throw err;
    }
  };

  const deleteContact = async (id: string) => {
    try {
      await api.delete(`/crm/contacts/${id}`);
      setContacts(prev => prev.filter(contact => contact.id !== id));
      setTotal(prev => prev - 1);
    } catch (err) {
      console.error('Erro ao deletar contato:', err);
      throw err;
    }
  };

  const updateLeadScore = async (id: string, score: number) => {
    try {
      const result = await api.patch<{ leadScore: number }>(`/crm/contacts/${id}/lead-score`, { score });
      setContacts(prev =>
        prev.map(contact =>
          contact.id === id ? { ...contact, leadScore: result.leadScore } : contact
        )
      );
      return result;
    } catch (err) {
      console.error('Erro ao atualizar lead score:', err);
      throw err;
    }
  };

  const addInteraction = async (contactId: string, interaction: Omit<Contact['interactions'][0], 'id'>) => {
    try {
      type Interaction = Contact['interactions'][0];
      const newInteraction = await api.post<Interaction>(`/crm/contacts/${contactId}/interactions`, interaction);
      setContacts(prev =>
        prev.map(contact =>
          contact.id === contactId
            ? {
                ...contact,
                interactions: [newInteraction, ...contact.interactions],
                lastContact: newInteraction.date
              }
            : contact
        )
      );
      return newInteraction;
    } catch (err) {
      console.error('Erro ao adicionar interacao:', err);
      throw err;
    }
  };

  return {
    contacts,
    loading,
    error,
    total,
    loadContacts,
    createContact,
    updateContact,
    deleteContact,
    updateLeadScore,
    addInteraction,
  };
};
