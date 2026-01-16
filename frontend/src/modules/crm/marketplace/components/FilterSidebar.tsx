'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Filter,
  X,
  ChevronDown,
  ChevronUp,
  Star,
  MapPin,
  BadgeCheck,
  Sparkles,
  RotateCcw,
} from 'lucide-react';
import { Button } from '@/core/components/ui/Button';
import { Badge } from '@/core/components/ui/Badge';
import type { ServiceFilters } from '../../types';

interface FilterSidebarProps {
  filters: ServiceFilters;
  onFiltersChange: (filters: ServiceFilters) => void;
  onClear: () => void;
  categories?: Category[];
  locations?: string[];
  isCollapsible?: boolean;
  className?: string;
}

interface Category {
  id: string;
  name: string;
  count: number;
  subcategories?: { id: string; name: string; count: number }[];
}

const defaultCategories: Category[] = [
  {
    id: 'manutencao',
    name: 'Manutencao',
    count: 45,
    subcategories: [
      { id: 'predial', name: 'Predial', count: 20 },
      { id: 'eletrica', name: 'Eletrica', count: 15 },
      { id: 'hidraulica', name: 'Hidraulica', count: 10 },
    ],
  },
  {
    id: 'limpeza',
    name: 'Limpeza',
    count: 38,
    subcategories: [
      { id: 'areas-comuns', name: 'Areas Comuns', count: 25 },
      { id: 'fachadas', name: 'Fachadas', count: 8 },
      { id: 'pos-obra', name: 'Pos-Obra', count: 5 },
    ],
  },
  {
    id: 'seguranca',
    name: 'Seguranca',
    count: 32,
    subcategories: [
      { id: 'portaria', name: 'Portaria', count: 18 },
      { id: 'cftv', name: 'CFTV', count: 10 },
      { id: 'controle-acesso', name: 'Controle de Acesso', count: 4 },
    ],
  },
  { id: 'jardinagem', name: 'Jardinagem', count: 22 },
  { id: 'elevadores', name: 'Elevadores', count: 15 },
  { id: 'piscinas', name: 'Piscinas', count: 12 },
  { id: 'dedetizacao', name: 'Dedetizacao', count: 18 },
  { id: 'contabilidade', name: 'Contabilidade', count: 25 },
];

const defaultLocations: string[] = [
  'Sao Paulo, SP',
  'Rio de Janeiro, RJ',
  'Belo Horizonte, MG',
  'Curitiba, PR',
  'Porto Alegre, RS',
  'Salvador, BA',
  'Brasilia, DF',
];

interface FilterSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  badge?: number;
}

function FilterSection({ title, children, defaultOpen = true, badge }: FilterSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-gray-200 pb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full py-2 text-left"
      >
        <span className="font-medium text-gray-900 flex items-center gap-2">
          {title}
          {badge !== undefined && badge > 0 && (
            <Badge variant="primary" size="sm">{badge}</Badge>
          )}
        </span>
        {isOpen ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="pt-2">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function FilterSidebar({
  filters,
  onFiltersChange,
  onClear,
  categories = defaultCategories,
  locations = defaultLocations,
  isCollapsible = false,
  className = '',
}: FilterSidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<string[]>([]);

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleCategoryChange = useCallback((categoryId: string, checked: boolean) => {
    const currentCategories = filters.categories || [];
    const newCategories = checked
      ? [...currentCategories, categoryId]
      : currentCategories.filter(c => c !== categoryId);
    onFiltersChange({ ...filters, categories: newCategories });
  }, [filters, onFiltersChange]);

  const handlePriceChange = useCallback((field: 'priceMin' | 'priceMax', value: number | undefined) => {
    onFiltersChange({ ...filters, [field]: value });
  }, [filters, onFiltersChange]);

  const handleRatingChange = useCallback((rating: number | undefined) => {
    onFiltersChange({ ...filters, rating });
  }, [filters, onFiltersChange]);

  const handleLocationChange = useCallback((location: string | undefined) => {
    onFiltersChange({ ...filters, location });
  }, [filters, onFiltersChange]);

  const handleVerifiedChange = useCallback((isVerified: boolean | undefined) => {
    onFiltersChange({ ...filters, isVerified });
  }, [filters, onFiltersChange]);

  const handlePremiumChange = useCallback((isPremium: boolean | undefined) => {
    onFiltersChange({ ...filters, isPremium });
  }, [filters, onFiltersChange]);

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.categories && filters.categories.length > 0) count += filters.categories.length;
    if (filters.priceMin !== undefined) count++;
    if (filters.priceMax !== undefined) count++;
    if (filters.rating !== undefined) count++;
    if (filters.location !== undefined) count++;
    if (filters.isVerified !== undefined) count++;
    if (filters.isPremium !== undefined) count++;
    return count;
  };

  const activeCount = getActiveFiltersCount();

  const sidebarContent = (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-conecta-escuro" />
          <h3 className="font-semibold text-gray-900">Filtros</h3>
          {activeCount > 0 && (
            <Badge variant="orange">{activeCount}</Badge>
          )}
        </div>
        {activeCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            leftIcon={<RotateCcw className="w-4 h-4" />}
          >
            Limpar
          </Button>
        )}
      </div>

      {/* Categories */}
      <FilterSection
        title="Categorias"
        badge={filters.categories?.length}
      >
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {categories.map(category => (
            <div key={category.id}>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id={category.id}
                  checked={filters.categories?.includes(category.id) || false}
                  onChange={e => handleCategoryChange(category.id, e.target.checked)}
                  className="rounded border-gray-300 text-conecta-escuro focus:ring-conecta-escuro"
                />
                <label
                  htmlFor={category.id}
                  className="flex-1 text-sm text-gray-700 cursor-pointer flex items-center justify-between"
                >
                  <span>{category.name}</span>
                  <span className="text-gray-400">({category.count})</span>
                </label>
                {category.subcategories && (
                  <button
                    onClick={() => toggleCategory(category.id)}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    {expandedCategories.includes(category.id) ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>
                )}
              </div>
              <AnimatePresence>
                {category.subcategories && expandedCategories.includes(category.id) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="ml-6 mt-2 space-y-2"
                  >
                    {category.subcategories.map(sub => (
                      <div key={sub.id} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id={sub.id}
                          checked={filters.categories?.includes(sub.id) || false}
                          onChange={e => handleCategoryChange(sub.id, e.target.checked)}
                          className="rounded border-gray-300 text-conecta-escuro focus:ring-conecta-escuro"
                        />
                        <label
                          htmlFor={sub.id}
                          className="text-sm text-gray-600 cursor-pointer flex-1 flex justify-between"
                        >
                          <span>{sub.name}</span>
                          <span className="text-gray-400">({sub.count})</span>
                        </label>
                      </div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </FilterSection>

      {/* Price Range */}
      <FilterSection title="Faixa de Preco">
        <div className="space-y-3">
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="text-xs text-gray-500">Minimo</label>
              <input
                type="number"
                min={0}
                placeholder="R$ 0"
                value={filters.priceMin || ''}
                onChange={e => handlePriceChange('priceMin', e.target.value ? parseInt(e.target.value) : undefined)}
                className="input text-sm"
              />
            </div>
            <div className="flex-1">
              <label className="text-xs text-gray-500">Maximo</label>
              <input
                type="number"
                min={0}
                placeholder="R$ 50.000"
                value={filters.priceMax || ''}
                onChange={e => handlePriceChange('priceMax', e.target.value ? parseInt(e.target.value) : undefined)}
                className="input text-sm"
              />
            </div>
          </div>
          {/* Quick price filters */}
          <div className="flex flex-wrap gap-2">
            {[
              { label: 'Ate R$ 5k', min: 0, max: 5000 },
              { label: 'R$ 5k-15k', min: 5000, max: 15000 },
              { label: 'R$ 15k+', min: 15000, max: undefined },
            ].map(range => (
              <button
                key={range.label}
                onClick={() => {
                  handlePriceChange('priceMin', range.min);
                  handlePriceChange('priceMax', range.max);
                }}
                className={`
                  px-2 py-1 text-xs rounded-full border transition-colors
                  ${filters.priceMin === range.min && filters.priceMax === range.max
                    ? 'bg-conecta-escuro text-white border-conecta-escuro'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                  }
                `}
              >
                {range.label}
              </button>
            ))}
          </div>
        </div>
      </FilterSection>

      {/* Rating */}
      <FilterSection title="Avaliacao Minima">
        <div className="space-y-2">
          {[4, 3, 2, 1].map(rating => (
            <button
              key={rating}
              onClick={() => handleRatingChange(filters.rating === rating ? undefined : rating)}
              className={`
                w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors
                ${filters.rating === rating
                  ? 'bg-conecta-escuro/10 text-conecta-escuro'
                  : 'hover:bg-gray-50 text-gray-600'
                }
              `}
            >
              <div className="flex items-center">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={`w-4 h-4 ${
                      i < rating
                        ? 'text-yellow-400 fill-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm">{rating}+ estrelas</span>
            </button>
          ))}
        </div>
      </FilterSection>

      {/* Location */}
      <FilterSection title="Localizacao" defaultOpen={false}>
        <div className="space-y-2">
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={filters.location || ''}
              onChange={e => handleLocationChange(e.target.value || undefined)}
              className="input pl-10 text-sm"
            >
              <option value="">Todas as localizacoes</option>
              {locations.map(location => (
                <option key={location} value={location}>
                  {location}
                </option>
              ))}
            </select>
          </div>
        </div>
      </FilterSection>

      {/* Special Filters */}
      <FilterSection title="Especiais" defaultOpen={false}>
        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.isVerified || false}
              onChange={e => handleVerifiedChange(e.target.checked || undefined)}
              className="rounded border-gray-300 text-conecta-escuro focus:ring-conecta-escuro"
            />
            <div className="flex items-center gap-2">
              <BadgeCheck className="w-4 h-4 text-green-500" />
              <span className="text-sm text-gray-700">Apenas Verificados</span>
            </div>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.isPremium || false}
              onChange={e => handlePremiumChange(e.target.checked || undefined)}
              className="rounded border-gray-300 text-conecta-escuro focus:ring-conecta-escuro"
            />
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-orange-500" />
              <span className="text-sm text-gray-700">Apenas Premium</span>
            </div>
          </label>
        </div>
      </FilterSection>
    </div>
  );

  // Mobile toggle button
  if (isCollapsible) {
    return (
      <>
        {/* Mobile Toggle */}
        <Button
          variant="outline"
          onClick={() => setIsMobileOpen(true)}
          leftIcon={<Filter className="w-4 h-4" />}
          className="lg:hidden"
        >
          Filtros
          {activeCount > 0 && (
            <Badge variant="orange" size="sm" className="ml-2">
              {activeCount}
            </Badge>
          )}
        </Button>

        {/* Mobile Sidebar */}
        <AnimatePresence>
          {isMobileOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                onClick={() => setIsMobileOpen(false)}
              />
              <motion.div
                initial={{ x: '-100%' }}
                animate={{ x: 0 }}
                exit={{ x: '-100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="fixed left-0 top-0 h-full w-80 bg-white shadow-xl z-50 lg:hidden overflow-y-auto"
              >
                <div className="sticky top-0 bg-white p-4 border-b flex items-center justify-between">
                  <h3 className="font-semibold">Filtros</h3>
                  <button
                    onClick={() => setIsMobileOpen(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <div className="p-4">{sidebarContent}</div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Desktop Sidebar */}
        <div className={`hidden lg:block ${className}`}>
          {sidebarContent}
        </div>
      </>
    );
  }

  return (
    <div className={className}>
      {sidebarContent}
    </div>
  );
}

export default FilterSidebar;
