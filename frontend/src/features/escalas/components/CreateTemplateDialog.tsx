'use client';

import { Calendar, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
;
import type { Scale, ScaleTemplateCreate } from '@/types/operacional';
import { SCALE_TYPE_LABELS } from '@/types/operacional';

interface CreateTemplateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  scales: Scale[];
  onSubmit: (data: ScaleTemplateCreate) => Promise<void>;
  isLoading?: boolean;
}

const monthNames = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

export function CreateTemplateDialog({
  isOpen,
  onClose,
  scales,
  onSubmit,
  isLoading = false,
}: CreateTemplateDialogProps) {
  const [formData, setFormData] = useState<ScaleTemplateCreate>({
    name: '',
    description: '',
    source_scale_id: '',
  });
  const [selectedScale, setSelectedScale] = useState<Scale | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        name: '',
        description: '',
        source_scale_id: '',
      });
      setSelectedScale(null);
      setErrors({});
    }
  }, [isOpen]);

  // Update selected scale when source_scale_id changes
  useEffect(() => {
    if (formData.source_scale_id) {
      const scale = scales.find(s => s.id === formData.source_scale_id);
      setSelectedScale(scale || null);
    } else {
      setSelectedScale(null);
    }
  }, [formData.source_scale_id, scales]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    }

    if (!formData.source_scale_id) {
      newErrors.source_scale_id = 'Selecione uma escala';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Erro ao criar template:', error);
    }
  };

  const publishedScales = scales.filter(
    s => s.status === 'published' || s.status === 'completed'
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Criar Template de Escala"
      description="Crie um template reutilizável a partir de uma escala existente"
      size="lg"
    >
      <div className="space-y-6">
        {/* Scale Selection */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Selecionar Escala Base *
          </label>
          <select
            value={formData.source_scale_id}
            onChange={(e) => setFormData({ ...formData, source_scale_id: e.target.value })}
            className={`w-full h-10 px-3 rounded-lg border bg-[hsl(var(--background))] text-sm ${
              errors.source_scale_id
                ? 'border-red-500'
                : 'border-[hsl(var(--border))]'
            }`}
          >
            <option value="">Selecione uma escala...</option>
            {publishedScales.map((scale) => (
              <option key={scale.id} value={scale.id}>
                {monthNames[scale.month - 1]}/{scale.year} - {SCALE_TYPE_LABELS[scale.scale_type]}
              </option>
            ))}
          </select>
          {errors.source_scale_id && (
            <p className="text-red-500 text-xs mt-1 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {errors.source_scale_id}
            </p>
          )}
          {publishedScales.length === 0 && (
            <p className="text-yellow-500 text-xs mt-1 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              Nenhuma escala publicada disponível
            </p>
          )}
        </div>

        {/* Scale Preview */}
        {selectedScale && (
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <Calendar className="w-5 h-5 text-blue-500" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-[hsl(var(--foreground))] mb-1">
                  {monthNames[selectedScale.month - 1]} {selectedScale.year}
                </h4>
                <p className="text-sm text-[hsl(var(--muted-foreground))] mb-2">
                  {SCALE_TYPE_LABELS[selectedScale.scale_type]}
                </p>
                <div className="grid grid-cols-3 gap-3">
                  <div className="text-center">
                    <p className="text-lg font-bold text-[hsl(var(--foreground))]">
                      {selectedScale.total_shifts}
                    </p>
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Turnos</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-[hsl(var(--foreground))]">
                      {selectedScale.total_hours.toFixed(0)}h
                    </p>
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Horas</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-[hsl(var(--foreground))]">
                      {selectedScale.fill_rate?.toFixed(0) || 0}%
                    </p>
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Preenchido</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Template Name */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Nome do Template *
          </label>
          <Input
            placeholder="Ex: Escala Padrão 12x36 Segurança"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className={errors.name ? 'border-red-500' : ''}
          />
          {errors.name && (
            <p className="text-red-500 text-xs mt-1 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {errors.name}
            </p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Descrição (opcional)
          </label>
          <textarea
            placeholder="Descreva quando usar este template..."
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full min-h-[100px] px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm resize-none"
          />
        </div>

        {/* Info */}
        <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-4 text-sm text-[hsl(var(--muted-foreground))]">
          <p className="mb-2">
            <strong>O que será salvo no template:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Padrão de distribuição de turnos</li>
            <li>Tipo de escala (12x36, 5x2, etc)</li>
            <li>Colaboradores alocados</li>
            <li>Configurações de horários</li>
          </ul>
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading || publishedScales.length === 0}>
          {isLoading ? 'Criando...' : 'Criar Template'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
