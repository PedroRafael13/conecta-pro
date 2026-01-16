import { useState, useCallback } from 'react';
import type { Document, SearchFilters } from '../types';
import { api } from '@/core/api';

interface SearchResponse {
  documents: Document[];
  suggestions?: string[];
}

interface SuggestionsResponse {
  suggestions: string[];
}

export const useSearch = () => {
  const [results, setResults] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const search = useCallback(async (searchQuery: string, searchFilters?: SearchFilters) => {
    if (!searchQuery.trim() && !searchFilters) {
      setResults([]);
      return;
    }

    setLoading(true);
    setQuery(searchQuery);

    try {
      const data = await api.get<SearchResponse>('/ged/search', {
        params: {
          q: searchQuery,
          ...searchFilters,
        },
      });

      setResults(data.documents);
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Erro na busca:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const getSuggestions = useCallback(async (partialQuery: string) => {
    if (partialQuery.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      const data = await api.get<SuggestionsResponse>('/ged/suggestions', {
        params: { q: partialQuery },
      });
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error('Erro ao buscar sugestoes:', error);
    }
  }, []);

  const updateFilters = useCallback((newFilters: SearchFilters) => {
    setFilters(newFilters);
    if (query) {
      search(query, newFilters);
    }
  }, [query, search]);

  const clearSearch = useCallback(() => {
    setQuery('');
    setResults([]);
    setFilters({});
    setSuggestions([]);
  }, []);

  return {
    results,
    loading,
    query,
    filters,
    suggestions,
    search,
    getSuggestions,
    updateFilters,
    clearSearch,
  };
};
