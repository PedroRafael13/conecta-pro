'use client';

;
import { Search } from 'lucide-react';
import { useProductivity } from './ProductivityProvider';

export function SearchTrigger() {
  const { openSearch } = useProductivity();

  return (
    <button
      onClick={openSearch}
      className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground border border-border rounded-lg hover:bg-accent transition-colors"
      aria-label="Abrir busca global"
    >
      <Search className="w-4 h-4" />
      <span className="hidden sm:inline">Buscar...</span>
      <kbd className="hidden md:inline-flex items-center gap-1 px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">
        /
      </kbd>
    </button>
  );
}
