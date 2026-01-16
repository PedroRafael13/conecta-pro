'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';

interface RatingStarsProps {
  value: number;
  onChange?: (rating: number) => void;
  maxStars?: number;
  size?: 'sm' | 'md' | 'lg';
  showValue?: boolean;
  showCount?: boolean;
  count?: number;
  readonly?: boolean;
  precision?: 'full' | 'half';
  color?: string;
  emptyColor?: string;
  className?: string;
}

const sizeConfig = {
  sm: { star: 'w-4 h-4', text: 'text-sm', gap: 'gap-0.5' },
  md: { star: 'w-5 h-5', text: 'text-base', gap: 'gap-1' },
  lg: { star: 'w-6 h-6', text: 'text-lg', gap: 'gap-1.5' },
};

export function RatingStars({
  value,
  onChange,
  maxStars = 5,
  size = 'md',
  showValue = false,
  showCount = false,
  count = 0,
  readonly = false,
  precision = 'full',
  color = 'text-yellow-400',
  emptyColor = 'text-gray-300',
  className = '',
}: RatingStarsProps) {
  const [hoverValue, setHoverValue] = useState<number | null>(null);
  const config = sizeConfig[size];
  const displayValue = hoverValue !== null ? hoverValue : value;

  const getStarFill = useCallback((index: number) => {
    const starValue = index + 1;
    const currentValue = displayValue;

    if (currentValue >= starValue) {
      return 'full';
    }
    if (precision === 'half' && currentValue >= starValue - 0.5) {
      return 'half';
    }
    return 'empty';
  }, [displayValue, precision]);

  const handleClick = useCallback((index: number, e: React.MouseEvent) => {
    if (readonly || !onChange) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const isHalf = precision === 'half' && x < rect.width / 2;

    const newValue = index + (isHalf ? 0.5 : 1);
    // Toggle off if clicking the same value
    onChange(newValue === value ? 0 : newValue);
  }, [readonly, onChange, precision, value]);

  const handleMouseMove = useCallback((index: number, e: React.MouseEvent) => {
    if (readonly) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const isHalf = precision === 'half' && x < rect.width / 2;

    setHoverValue(index + (isHalf ? 0.5 : 1));
  }, [readonly, precision]);

  const handleMouseLeave = useCallback(() => {
    setHoverValue(null);
  }, []);

  return (
    <div className={`flex items-center ${config.gap} ${className}`}>
      <div
        className={`flex ${config.gap}`}
        onMouseLeave={handleMouseLeave}
      >
        {Array.from({ length: maxStars }).map((_, index) => {
          const fill = getStarFill(index);

          return (
            <motion.button
              key={index}
              type="button"
              disabled={readonly}
              onClick={(e) => handleClick(index, e)}
              onMouseMove={(e) => handleMouseMove(index, e)}
              whileHover={!readonly ? { scale: 1.1 } : undefined}
              whileTap={!readonly ? { scale: 0.95 } : undefined}
              className={`
                relative focus:outline-none
                ${readonly ? 'cursor-default' : 'cursor-pointer'}
              `}
            >
              {/* Empty star (background) */}
              <Star className={`${config.star} ${emptyColor}`} />

              {/* Filled star (overlay) */}
              {fill !== 'empty' && (
                <div
                  className="absolute inset-0 overflow-hidden"
                  style={{ width: fill === 'half' ? '50%' : '100%' }}
                >
                  <Star
                    className={`${config.star} ${color} fill-current`}
                  />
                </div>
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Value display */}
      {showValue && (
        <span className={`${config.text} font-medium text-gray-900 ml-1`}>
          {displayValue.toFixed(1)}
        </span>
      )}

      {/* Review count */}
      {showCount && count > 0 && (
        <span className={`${config.text} text-gray-500`}>
          ({count.toLocaleString('pt-BR')})
        </span>
      )}
    </div>
  );
}

// Componente de rating compacto para listas
export function RatingBadge({
  value,
  count,
  size = 'sm',
}: {
  value: number;
  count?: number;
  size?: 'sm' | 'md';
}) {
  const config = sizeConfig[size];

  return (
    <div className="inline-flex items-center gap-1 bg-gray-100 rounded-full px-2 py-0.5">
      <Star className={`${config.star} text-yellow-400 fill-yellow-400`} />
      <span className={`${config.text} font-medium`}>{value.toFixed(1)}</span>
      {count !== undefined && (
        <span className={`${config.text} text-gray-500`}>
          ({count})
        </span>
      )}
    </div>
  );
}

// Componente de input de rating para formularios
export function RatingInput({
  label,
  value,
  onChange,
  error,
  hint,
  required,
}: {
  label?: string;
  value: number;
  onChange: (rating: number) => void;
  error?: string;
  hint?: string;
  required?: boolean;
}) {
  const [hoveredLabel, setHoveredLabel] = useState<string | null>(null);

  const ratingLabels: Record<number, string> = {
    1: 'Pessimo',
    2: 'Ruim',
    3: 'Regular',
    4: 'Bom',
    5: 'Excelente',
  };

  return (
    <div className="w-full">
      {label && (
        <label className="label mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <div className="flex items-center gap-3">
        <div
          className="flex gap-1"
          onMouseLeave={() => setHoveredLabel(null)}
        >
          {Array.from({ length: 5 }).map((_, index) => {
            const starValue = index + 1;
            const isFilled = value >= starValue;

            return (
              <motion.button
                key={index}
                type="button"
                onClick={() => onChange(starValue === value ? 0 : starValue)}
                onMouseEnter={() => setHoveredLabel(ratingLabels[starValue])}
                whileHover={{ scale: 1.15 }}
                whileTap={{ scale: 0.95 }}
                className="focus:outline-none focus:ring-2 focus:ring-conecta-escuro focus:ring-offset-2 rounded-sm"
              >
                <Star
                  className={`w-8 h-8 transition-colors ${
                    isFilled
                      ? 'text-yellow-400 fill-yellow-400'
                      : 'text-gray-300 hover:text-yellow-200'
                  }`}
                />
              </motion.button>
            );
          })}
        </div>

        {(hoveredLabel || (value > 0 && ratingLabels[value])) && (
          <motion.span
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-sm font-medium text-gray-700"
          >
            {hoveredLabel || ratingLabels[value]}
          </motion.span>
        )}
      </div>

      {error && <p className="error-text mt-1">{error}</p>}
      {hint && !error && (
        <p className="text-sm text-gray-500 mt-1">{hint}</p>
      )}
    </div>
  );
}

// Distribuicao de ratings (para exibir breakdown)
export function RatingDistribution({
  distribution,
  total,
}: {
  distribution: { rating: number; count: number }[];
  total: number;
}) {
  const sortedDistribution = [...distribution].sort((a, b) => b.rating - a.rating);

  return (
    <div className="space-y-2">
      {sortedDistribution.map(({ rating, count }) => {
        const percentage = total > 0 ? (count / total) * 100 : 0;

        return (
          <div key={rating} className="flex items-center gap-2">
            <div className="flex items-center gap-1 w-16">
              <span className="text-sm text-gray-600">{rating}</span>
              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            </div>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${percentage}%` }}
                transition={{ duration: 0.5, delay: (5 - rating) * 0.1 }}
                className="h-full bg-yellow-400 rounded-full"
              />
            </div>
            <span className="text-sm text-gray-500 w-12 text-right">
              {count.toLocaleString('pt-BR')}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default RatingStars;
