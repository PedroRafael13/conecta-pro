import React, { useState, useRef, useEffect } from 'react';
import { Search, Filter, X, Calendar, Tag, User } from 'lucide-react';
import type { SearchFilters } from '../types';

interface SearchBarProps {
  onSearch: (query: string, filters: SearchFilters) => void;
  suggestions?: string[];
  loading?: boolean;
  placeholder?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  suggestions = [],
  loading = false,
  placeholder = "Buscar documentos...",
}) => {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({});
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Handle search
  const handleSearch = (searchQuery?: string, searchFilters?: SearchFilters) => {
    const finalQuery = searchQuery ?? query;
    const finalFilters = searchFilters ?? filters;
    onSearch(finalQuery, finalFilters);
    setShowSuggestions(false);
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    handleSearch(suggestion);
    setShowSuggestions(false);
  };

  // Handle filter change
  const handleFilterChange = (key: keyof SearchFilters, value: SearchFilters[keyof SearchFilters]) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    handleSearch(query, newFilters);
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({});
    handleSearch(query, {});
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const hasActiveFilters = Object.values(filters).some(value => 
    value !== undefined && value !== '' && 
    (Array.isArray(value) ? value.length > 0 : true)
  );

  return (
    <div className="relative">
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowSuggestions(true);
          }}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          onFocus={() => setShowSuggestions(suggestions.length > 0)}
          className="block w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
          placeholder={placeholder}
        />

        {/* Loading Spinner */}
        {loading && (
          <div className="absolute inset-y-0 right-10 flex items-center">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Filter Button */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`absolute inset-y-0 right-0 pr-3 flex items-center ${
            hasActiveFilters ? 'text-blue-600' : 'text-gray-400'
          } hover:text-gray-600`}
        >
          <Filter className="h-5 w-5" />
          {hasActiveFilters && (
            <span className="ml-1 w-2 h-2 bg-blue-600 rounded-full" />
          )}
        </button>
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg"
        >
          <ul className="py-1">
            {suggestions.map((suggestion, index) => (
              <li key={index}>
                <button
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <Search className="inline w-4 h-4 mr-2 text-gray-400" />
                  {suggestion}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Filters Panel */}
      {showFilters && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-900">Filtros</h3>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Limpar todos
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Category Filter */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                <Tag className="inline w-3 h-3 mr-1" />
                Categoria
              </label>
              <select
                value={filters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todas</option>
                <option value="financial">Financeiro</option>
                <option value="legal">Jurídico</option>
                <option value="hr">RH</option>
                <option value="operational">Operacional</option>
                <option value="commercial">Comercial</option>
              </select>
            </div>

            {/* File Type Filter */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Tipo de Arquivo
              </label>
              <select
                value={filters.fileType || ''}
                onChange={(e) => handleFilterChange('fileType', e.target.value)}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todos</option>
                <option value="pdf">PDF</option>
                <option value="doc">Word</option>
                <option value="image">Imagem</option>
                <option value="excel">Excel</option>
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                <Calendar className="inline w-3 h-3 mr-1" />
                Data Inicial
              </label>
              <input
                type="date"
                value={filters.dateFrom || ''}
                onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                <Calendar className="inline w-3 h-3 mr-1" />
                Data Final
              </label>
              <input
                type="date"
                value={filters.dateTo || ''}
                onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Uploaded By */}
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-700 mb-1">
                <User className="inline w-3 h-3 mr-1" />
                Enviado por
              </label>
              <input
                type="text"
                value={filters.uploadedBy || ''}
                onChange={(e) => handleFilterChange('uploadedBy', e.target.value)}
                placeholder="Nome do usuário..."
                className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Active Filters */}
          {hasActiveFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex flex-wrap gap-2">
                {Object.entries(filters).map(([key, value]) => {
                  if (!value || (Array.isArray(value) && value.length === 0)) return null;
                  
                  return (
                    <span
                      key={key}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {key}: {Array.isArray(value) ? value.join(', ') : value}
                      <button
                        onClick={() => handleFilterChange(key as keyof SearchFilters, undefined)}
                        className="ml-1 text-blue-600 hover:text-blue-800"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
