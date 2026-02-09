'use client';

import { Search, X, Loader2, User, MapPin, Calendar, FileText, Users } from 'lucide-react';
import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
;
import { useGlobalSearch } from '@/hooks/search/useGlobalSearch';
import type { SearchResult } from '@/types/generated/search/models';
import { useDebounce } from '@/hooks/useDebounce';

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

const typeIcons: Record<string, React.ReactNode> = {
  colaborador: <User className="w-4 h-4" />,
  posto: <MapPin className="w-4 h-4" />,
  escala: <Calendar className="w-4 h-4" />,
  ocorrencia: <FileText className="w-4 h-4" />,
  ronda: <Users className="w-4 h-4" />,
};

const typeLabels: Record<string, string> = {
  colaborador: 'Colaborador',
  posto: 'Posto',
  escala: 'Escala',
  ocorrencia: 'Ocorrência',
  ronda: 'Ronda',
};

export function GlobalSearch({ isOpen, onClose }: GlobalSearchProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Debounce do query
  const debouncedQuery = useDebounce(query, 300);

  // Hook de busca
  const { data, isLoading } = useGlobalSearch(
    { q: debouncedQuery },
    { enabled: debouncedQuery.length >= 1 }
  );

  const results = data?.results || [];
  const tookMs = data?.took_ms || 0;

  // Navegação com teclado
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev =>
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Enter':
        e.preventDefault();
        if (results[selectedIndex]) {
          router.push(results[selectedIndex].url);
          onClose();
        }
        break;
      case 'Escape':
        e.preventDefault();
        onClose();
        break;
    }
  }, [results, selectedIndex, router, onClose]);

  // Reset quando abrir/fechar - usando queueMicrotask
  useEffect(() => {
    if (isOpen) {
      queueMicrotask(() => {
        setQuery('');
        setSelectedIndex(0);
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  // Agrupar resultados por tipo
  const groupedResults = results.reduce((acc, result) => {
    return {
      ...acc,
      [result.type]: [...(acc[result.type] || []), result],
    };
  }, {} as Record<string, SearchResult[]>);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-3xl bg-[hsl(var(--background))] rounded-lg shadow-2xl border border-[hsl(var(--border))]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header com busca */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-[hsl(var(--border))]">
          <Search className="w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Buscar colaboradores, postos, escalas, ocorrências..."
            className="flex-1 bg-transparent outline-none text-sm placeholder:text-muted-foreground"
            autoFocus
          />
          {isLoading && (
            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
          )}
          <button
            onClick={onClose}
            className="p-1 hover:bg-accent rounded transition-colors"
            aria-label="Fechar"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Resultados */}
        <div className="max-h-[500px] overflow-y-auto">
          {!query.trim() && (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              Digite para buscar...
            </div>
          )}

          {query.trim() && !isLoading && results.length === 0 && (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              Nenhum resultado encontrado
            </div>
          )}

          {Object.entries(groupedResults).map(([type, items]) => (
            <div key={type}>
              <div className="sticky top-0 px-4 py-2 text-xs font-semibold text-muted-foreground bg-muted/80 backdrop-blur-sm flex items-center gap-2">
                {typeIcons[type]}
                <span>{typeLabels[type]}</span>
                <span className="text-xs opacity-60">({items.length})</span>
              </div>
              {items.map((result) => {
                const globalIndex = results.indexOf(result);
                const isSelected = globalIndex === selectedIndex;

                return (
                  <button
                    key={result.id}
                    onClick={() => {
                      router.push(result.url);
                      onClose();
                    }}
                    onMouseEnter={() => setSelectedIndex(globalIndex)}
                    className={`w-full flex items-start gap-3 px-4 py-3 text-left transition-colors ${
                      isSelected
                        ? 'bg-accent text-accent-foreground'
                        : 'hover:bg-accent/50'
                    }`}
                  >
                    <div className="flex-shrink-0 mt-0.5 text-muted-foreground">
                      {typeIcons[type]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium">{result.title}</div>
                      <div className="text-xs text-muted-foreground truncate">
                        {result.description}
                      </div>
                    </div>
                    {isSelected && (
                      <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs font-mono bg-background border border-border rounded">
                        Enter
                      </kbd>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        {/* Footer com dicas e métricas */}
        <div className="flex items-center justify-between px-4 py-2 text-xs text-muted-foreground border-t border-[hsl(var(--border))]">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">↑↓</kbd>
              <span>Navegar</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Enter</kbd>
              <span>Abrir</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Esc</kbd>
              <span>Fechar</span>
            </div>
          </div>
          {tookMs > 0 && (
            <div className="text-xs opacity-60">
              {results.length} resultados em {tookMs}ms
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
