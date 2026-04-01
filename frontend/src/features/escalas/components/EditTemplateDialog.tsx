'use client';

import { AlertCircle } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
;
import type { ScaleTemplate, ScaleTemplateUpdate } from '@/types/operacional';

interface EditTemplateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  template: ScaleTemplate | null;
  onSubmit: (id: string, data: ScaleTemplateUpdate) => Promise<void>;
  isLoading?: boolean;
}

// Initial form state factory
const createInitialFormData = (): ScaleTemplateUpdate => ({
  name: '',
  description: '',
});

export function EditTemplateDialog({
  isOpen,
  onClose,
  template,
  onSubmit,
  isLoading = false,
}: EditTemplateDialogProps) {
  const [formData, setFormData] = useState<ScaleTemplateUpdate>(createInitialFormData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const prevIsOpenRef = useRef(isOpen);
  const prevTemplateIdRef = useRef<string | null>(null);

  // Load template data when modal opens (transition from closed to open)
  useEffect(() => {
    const prevIsOpen = prevIsOpenRef.current;
    const prevTemplateId = prevTemplateIdRef.current;
    prevIsOpenRef.current = isOpen;
    prevTemplateIdRef.current = template?.id || null;

    // Load data when opening with a different template
    const shouldLoadData = isOpen && template && (!prevIsOpen || template.id !== prevTemplateId);

    if (shouldLoadData) {
      const rafId = requestAnimationFrame(() => {

        setFormData({
          name: template.name,
          description: template.description || '',
        });
        setErrors({});
      });
      return () => cancelAnimationFrame(rafId);
    }

    // Reset when closing
    if (prevIsOpen && !isOpen) {
      const rafId = requestAnimationFrame(() => {
        setFormData(createInitialFormData());
        setErrors({});
      });
      return () => cancelAnimationFrame(rafId);
    }
  }, [isOpen, template]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Nome é obrigatório';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate() || !template) return;

    try {
      await onSubmit(template.id, formData);
      onClose();
    } catch (error) {
      console.error('Erro ao atualizar template:', error);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Editar Template"
      description="Altere o nome e descrição do template"
      size="md"
    >
      <div className="space-y-6">
        {/* Template Name */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Nome do Template *
          </label>
          <Input
            placeholder="Ex: Escala Padrão 12x36 Segurança"
            value={formData.name || ''}
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
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? 'Salvando...' : 'Salvar Alterações'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
