'use client';

import { useState } from 'react';
import {
  Calendar,
  Users,
  TrendingUp,
  MoreVertical,
  Edit,
  Trash2,
  Play,
  Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ScaleTemplate } from '@/types/operacional';
import { SCALE_TYPE_LABELS } from '@/types/operacional';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface TemplateCardProps {
  template: ScaleTemplate;
  onUse: (template: ScaleTemplate) => void;
  onEdit: (template: ScaleTemplate) => void;
  onDelete: (template: ScaleTemplate) => void;
}

export function TemplateCard({ template, onUse, onEdit, onDelete }: TemplateCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Nunca';
    try {
      return formatDistanceToNow(new Date(dateString), {
        addSuffix: true,
        locale: ptBR,
      });
    } catch {
      return 'Data inválida';
    }
  };

  return (
    <div className="group bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-6 hover:border-[hsl(var(--primary))] hover:shadow-lg transition-all duration-300">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-semibold text-[hsl(var(--foreground))] text-lg mb-1 group-hover:text-[hsl(var(--primary))] transition-colors">
            {template.name}
          </h3>
          {template.description && (
            <p className="text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
              {template.description}
            </p>
          )}
        </div>

        {/* Menu Dropdown */}
        <div className="relative">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowMenu(!showMenu)}
            className="ml-2"
          >
            <MoreVertical className="w-4 h-4" />
          </Button>

          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 top-8 z-20 w-48 bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg shadow-lg overflow-hidden">
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onUse(template);
                  }}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-[hsl(var(--muted))] transition-colors flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Usar Template
                </button>
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onEdit(template);
                  }}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-[hsl(var(--muted))] transition-colors flex items-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Editar
                </button>
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onDelete(template);
                  }}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-red-500/10 text-red-500 transition-colors flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Excluir
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Template Info */}
      <div className="mb-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 text-xs font-medium">
          <Calendar className="w-3 h-3" />
          {SCALE_TYPE_LABELS[template.scale_type] || template.scale_type}
        </div>
        {template.post_name && (
          <div className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
            Posto: {template.post_name}
          </div>
        )}
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3 text-center">
          <Users className="w-4 h-4 mx-auto mb-1 text-[hsl(var(--muted-foreground))]" />
          <p className="text-lg font-bold text-[hsl(var(--foreground))]">
            {template.total_employees}
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Colaboradores</p>
        </div>
        <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3 text-center">
          <TrendingUp className="w-4 h-4 mx-auto mb-1 text-[hsl(var(--muted-foreground))]" />
          <p className="text-lg font-bold text-[hsl(var(--foreground))]">
            {template.coverage_percentage}%
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Cobertura</p>
        </div>
        <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3 text-center">
          <Clock className="w-4 h-4 mx-auto mb-1 text-[hsl(var(--muted-foreground))]" />
          <p className="text-lg font-bold text-[hsl(var(--foreground))]">
            {template.pattern_days}
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Dias</p>
        </div>
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between text-xs text-[hsl(var(--muted-foreground))] mb-4 pb-4 border-b border-[hsl(var(--border))]">
        <span>Usado {template.times_used}x</span>
        <span>Criado {formatDate(template.created_at)}</span>
      </div>
      {template.last_used_at && (
        <div className="text-xs text-[hsl(var(--muted-foreground))] mb-4">
          Último uso: {formatDate(template.last_used_at)}
        </div>
      )}

      {/* Action Button */}
      <Button
        className="w-full"
        onClick={() => onUse(template)}
      >
        <Play className="w-4 h-4 mr-2" />
        Usar este Template
      </Button>
    </div>
  );
}
