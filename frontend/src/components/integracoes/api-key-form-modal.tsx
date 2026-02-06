'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface APIKeyFormData {
  name: string;
  description: string;
  expires_in: string;
  permissions: string;
}

interface APIKeyFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: APIKeyFormData) => void;
  isLoading?: boolean;
}

const EXPIRATION_OPTIONS = [
  { value: '30', label: '30 dias' },
  { value: '90', label: '90 dias' },
  { value: '365', label: '1 ano' },
  { value: 'never', label: 'Nunca' },
];

const initialFormData: APIKeyFormData = {
  name: '',
  description: '',
  expires_in: '90',
  permissions: '',
};

export function APIKeyFormModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: APIKeyFormModalProps) {
  const [formData, setFormData] = useState<APIKeyFormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<Record<keyof APIKeyFormData, string>>>({});

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData(initialFormData);
      setErrors({});
    }
  }, [isOpen]);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof APIKeyFormData, string>> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    } else if (formData.name.trim().length < 3) {
      newErrors.name = 'Nome deve ter pelo menos 3 caracteres';
    } else if (formData.name.trim().length > 100) {
      newErrors.name = 'Nome deve ter no máximo 100 caracteres';
    }

    if (formData.description && formData.description.length > 500) {
      newErrors.description = 'Descrição deve ter no máximo 500 caracteres';
    }

    if (!formData.expires_in) {
      newErrors.expires_in = 'Selecione uma opção de expiração';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    onSubmit({
      ...formData,
      name: formData.name.trim(),
      description: formData.description.trim(),
      permissions: formData.permissions.trim(),
    });
  };

  const handleChange = (field: keyof APIKeyFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error on change
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Criar API Key"
      description="Preencha os campos para gerar uma nova chave de acesso"
      size="md"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          {/* Nome */}
          <div className="space-y-2">
            <Label htmlFor="api-key-name">
              Nome <span className="text-red-500">*</span>
            </Label>
            <Input
              id="api-key-name"
              placeholder="Ex: Integração ERP, Webhook Portaria..."
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              disabled={isLoading}
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && (
              <p className="text-xs text-red-500">{errors.name}</p>
            )}
          </div>

          {/* Descrição */}
          <div className="space-y-2">
            <Label htmlFor="api-key-description">Descrição</Label>
            <Input
              id="api-key-description"
              placeholder="Descreva o propósito desta chave..."
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              disabled={isLoading}
              className={errors.description ? 'border-red-500' : ''}
            />
            {errors.description && (
              <p className="text-xs text-red-500">{errors.description}</p>
            )}
          </div>

          {/* Expiração */}
          <div className="space-y-2">
            <Label htmlFor="api-key-expires">
              Expiração <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.expires_in}
              onValueChange={(value) => handleChange('expires_in', value)}
              disabled={isLoading}
            >
              <SelectTrigger
                id="api-key-expires"
                className={errors.expires_in ? 'border-red-500' : ''}
              >
                <SelectValue placeholder="Selecione o prazo de expiração" />
              </SelectTrigger>
              <SelectContent>
                {EXPIRATION_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.expires_in && (
              <p className="text-xs text-red-500">{errors.expires_in}</p>
            )}
          </div>

          {/* Permissões */}
          <div className="space-y-2">
            <Label htmlFor="api-key-permissions">Permissões</Label>
            <Input
              id="api-key-permissions"
              placeholder="Ex: read, write, admin (separadas por vírgula)"
              value={formData.permissions}
              onChange={(e) => handleChange('permissions', e.target.value)}
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground">
              Informe as permissões separadas por vírgula. Deixe vazio para permissões padrão.
            </p>
          </div>
        </div>

        <ModalFooter>
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Criando...' : 'Criar API Key'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
