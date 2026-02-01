'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Loader2 } from 'lucide-react';

interface PIAFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description: string;
    responsible: string;
    data_types: string;
    processing_purpose: string;
  }) => void;
  isLoading?: boolean;
  piaType: 'simple' | 'complete';
}

export function PIAFormModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  piaType,
}: PIAFormModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    responsible: '',
    data_types: '',
    processing_purpose: '',
  });

  const handleSubmit = () => {
    onSubmit(formData);
    setFormData({
      title: '',
      description: '',
      responsible: '',
      data_types: '',
      processing_purpose: '',
    });
  };

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      responsible: '',
      data_types: '',
      processing_purpose: '',
    });
    onClose();
  };

  const isValid =
    formData.title.trim().length > 0 &&
    formData.description.trim().length > 0 &&
    formData.responsible.trim().length > 0 &&
    formData.data_types.trim().length > 0;

  const modalTitle =
    piaType === 'simple'
      ? 'Nova PIA Simplificada'
      : 'Nova PIA Completa (DPIA)';

  const modalDescription =
    piaType === 'simple'
      ? 'Crie uma avaliacao de impacto simplificada para o projeto.'
      : 'Crie uma avaliacao de impacto completa com analise detalhada de riscos.';

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={modalTitle}
      description={modalDescription}
      size="lg"
    >
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="pia-title">Titulo</Label>
          <Input
            id="pia-title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Nome do projeto ou processo"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pia-description">Descricao</Label>
          <Textarea
            id="pia-description"
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            placeholder="Descreva o projeto e o tratamento de dados envolvido"
            rows={3}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pia-responsible">Responsavel</Label>
          <Input
            id="pia-responsible"
            value={formData.responsible}
            onChange={(e) =>
              setFormData({ ...formData, responsible: e.target.value })
            }
            placeholder="Nome do responsavel pela avaliacao"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pia-data-types">Tipos de Dados</Label>
          <Textarea
            id="pia-data-types"
            value={formData.data_types}
            onChange={(e) =>
              setFormData({ ...formData, data_types: e.target.value })
            }
            placeholder="Liste os tipos de dados tratados (um por linha)"
            rows={3}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pia-purpose">Finalidade do Tratamento</Label>
          <Textarea
            id="pia-purpose"
            value={formData.processing_purpose}
            onChange={(e) =>
              setFormData({ ...formData, processing_purpose: e.target.value })
            }
            placeholder={
              piaType === 'complete'
                ? 'Liste as finalidades do tratamento (uma por linha)'
                : 'Descreva a finalidade do tratamento de dados'
            }
            rows={3}
          />
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={handleClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={!isValid || isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Criando...
            </>
          ) : (
            'Criar Avaliacao'
          )}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
