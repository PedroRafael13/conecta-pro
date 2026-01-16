'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import {
  Calendar,
  Clock,
  MapPin,
  Building2,
  FileText,
  ChevronRight,
  Star,
  AlertTriangle,
  TrendingUp,
  Bookmark,
  BookmarkCheck,
} from 'lucide-react';
import { ScoreIndicator } from './ScoreIndicator';

type BiddingType = 'pregao' | 'concorrencia' | 'tomada_precos' | 'convite' | 'leilao' | 'concurso';
type BiddingStatus = 'open' | 'closing_soon' | 'closed' | 'suspended' | 'canceled';

interface OpportunityCardProps {
  id: string;
  title: string;
  description?: string;
  type: BiddingType;
  status: BiddingStatus;
  number: string; // e.g., "PE 001/2024"
  agency: string;
  agencyAcronym?: string;
  location: string;
  state: string;
  publishDate: Date;
  deadline: Date;
  estimatedValue?: number;
  aiScore: number; // 0-100
  aiInsights?: string[];
  isBookmarked?: boolean;
  matchedKeywords?: string[];
  onClick?: (id: string) => void;
  onBookmark?: (id: string) => void;
  onViewDocuments?: (id: string) => void;
  className?: string;
}

const typeLabels: Record<BiddingType, string> = {
  pregao: 'Pregao',
  concorrencia: 'Concorrencia',
  tomada_precos: 'Tomada de Precos',
  convite: 'Convite',
  leilao: 'Leilao',
  concurso: 'Concurso',
};

const statusConfig: Record<
  BiddingStatus,
  { label: string; color: string; bgColor: string }
> = {
  open: { label: 'Aberto', color: 'text-green-600', bgColor: 'bg-green-100' },
  closing_soon: { label: 'Encerrando', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
  closed: { label: 'Encerrado', color: 'text-gray-600', bgColor: 'bg-gray-100' },
  suspended: { label: 'Suspenso', color: 'text-orange-600', bgColor: 'bg-orange-100' },
  canceled: { label: 'Cancelado', color: 'text-red-600', bgColor: 'bg-red-100' },
};

function formatDate(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function formatDateTime(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

function getDaysUntilDeadline(deadline: Date): number {
  const now = new Date();
  const diffTime = deadline.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function getHoursUntilDeadline(deadline: Date): number {
  const now = new Date();
  const diffTime = deadline.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60));
}

export function OpportunityCard({
  id,
  title,
  description,
  type,
  status,
  number,
  agency,
  agencyAcronym,
  location,
  state,
  publishDate,
  deadline,
  estimatedValue,
  aiScore,
  aiInsights,
  isBookmarked = false,
  matchedKeywords,
  onClick,
  onBookmark,
  onViewDocuments,
  className,
}: OpportunityCardProps) {
  const statusStyle = statusConfig[status];
  const daysUntil = getDaysUntilDeadline(deadline);
  const hoursUntil = getHoursUntilDeadline(deadline);
  const isUrgent = status === 'open' && daysUntil <= 3 && daysUntil > 0;
  const isClosingSoon = status === 'closing_soon' || isUrgent;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx(
        'group bg-white rounded-xl border shadow-sm overflow-hidden',
        'hover:shadow-lg transition-all duration-200 cursor-pointer',
        isClosingSoon && !['closed', 'canceled', 'suspended'].includes(status) && 'border-yellow-300',
        aiScore >= 80 && 'ring-2 ring-[#FF6B35]/20',
        !isClosingSoon && aiScore < 80 && 'border-gray-200',
        className
      )}
      onClick={() => onClick?.(id)}
    >
      {/* Top highlight for high score */}
      {aiScore >= 80 && (
        <div className="h-1 bg-gradient-to-r from-[#FF6B35] to-[#FF8F5E]" />
      )}

      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Type and Number */}
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-0.5 text-xs font-medium bg-[#0A2540] text-white rounded">
                {typeLabels[type]}
              </span>
              <span className="text-sm font-mono text-gray-500">{number}</span>
              <span
                className={clsx(
                  'px-2 py-0.5 text-xs font-medium rounded-full',
                  statusStyle.bgColor,
                  statusStyle.color
                )}
              >
                {statusStyle.label}
              </span>
            </div>

            {/* Title */}
            <h3 className="text-lg font-semibold text-[#0A2540] group-hover:text-[#FF6B35] transition-colors line-clamp-2">
              {title}
            </h3>

            {/* Description */}
            {description && (
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">{description}</p>
            )}
          </div>

          {/* AI Score */}
          <div className="flex flex-col items-center gap-2">
            <ScoreIndicator score={aiScore} size="md" showLabel />
            {onBookmark && (
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={(e) => {
                  e.stopPropagation();
                  onBookmark(id);
                }}
                className={clsx(
                  'p-1.5 rounded-lg transition-colors',
                  isBookmarked
                    ? 'text-[#FF6B35] bg-orange-50'
                    : 'text-gray-400 hover:text-[#FF6B35] hover:bg-orange-50'
                )}
              >
                {isBookmarked ? (
                  <BookmarkCheck className="w-5 h-5" />
                ) : (
                  <Bookmark className="w-5 h-5" />
                )}
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="p-4 space-y-3">
        {/* Agency */}
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-700 truncate">
            {agencyAcronym && <span className="font-medium">{agencyAcronym} - </span>}
            {agency}
          </span>
        </div>

        {/* Location */}
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-700">
            {location}, {state}
          </span>
        </div>

        {/* Dates */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-700">{formatDate(publishDate)}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock
              className={clsx(
                'w-4 h-4',
                isClosingSoon ? 'text-yellow-500' : 'text-gray-400'
              )}
            />
            <span
              className={clsx(
                'text-sm font-medium',
                isClosingSoon ? 'text-yellow-600' : 'text-gray-700'
              )}
            >
              {formatDateTime(deadline)}
            </span>
          </div>
        </div>

        {/* Estimated Value */}
        {estimatedValue && (
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-semibold text-[#0A2540]">
              {formatCurrency(estimatedValue)}
            </span>
          </div>
        )}

        {/* Deadline Alert */}
        {status === 'open' && daysUntil > 0 && (
          <div
            className={clsx(
              'flex items-center gap-2 px-3 py-2 rounded-lg',
              daysUntil <= 1 ? 'bg-red-50' : daysUntil <= 3 ? 'bg-yellow-50' : 'bg-blue-50'
            )}
          >
            {daysUntil <= 3 && <AlertTriangle className="w-4 h-4 text-yellow-500" />}
            <span
              className={clsx(
                'text-sm font-medium',
                daysUntil <= 1
                  ? 'text-red-600'
                  : daysUntil <= 3
                  ? 'text-yellow-600'
                  : 'text-blue-600'
              )}
            >
              {daysUntil <= 1
                ? `${hoursUntil}h restantes`
                : `${daysUntil} dias restantes`}
            </span>
          </div>
        )}
      </div>

      {/* AI Insights */}
      {aiInsights && aiInsights.length > 0 && (
        <div className="px-4 pb-4">
          <div className="p-3 bg-gradient-to-r from-[#0A2540]/5 to-[#FF6B35]/5 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Star className="w-4 h-4 text-[#FF6B35]" />
              <span className="text-xs font-semibold text-[#0A2540]">Insights IA</span>
            </div>
            <ul className="space-y-1">
              {aiInsights.slice(0, 2).map((insight, index) => (
                <li key={index} className="text-xs text-gray-600 flex items-start gap-1">
                  <span className="text-[#FF6B35]">*</span>
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Matched Keywords */}
      {matchedKeywords && matchedKeywords.length > 0 && (
        <div className="px-4 pb-4">
          <div className="flex flex-wrap gap-1">
            {matchedKeywords.slice(0, 5).map((keyword) => (
              <span
                key={keyword}
                className="px-2 py-0.5 text-xs bg-[#FF6B35]/10 text-[#FF6B35] rounded-full"
              >
                {keyword}
              </span>
            ))}
            {matchedKeywords.length > 5 && (
              <span className="px-2 py-0.5 text-xs text-gray-500">
                +{matchedKeywords.length - 5}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between">
          {onViewDocuments && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={(e) => {
                e.stopPropagation();
                onViewDocuments(id);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-[#0A2540] hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FileText className="w-4 h-4" />
              Ver Documentos
            </motion.button>
          )}
          <div className="flex items-center gap-1 text-sm text-[#FF6B35] font-medium group-hover:gap-2 transition-all">
            Ver detalhes
            <ChevronRight className="w-4 h-4" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
