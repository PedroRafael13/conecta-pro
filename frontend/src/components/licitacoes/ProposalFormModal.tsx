'use client';

import { useState, useEffect } from 'react';
import { FileText, Loader2 } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert } from '@/components/ui/alert';
import { statusOptions, type ProposalStatus } from './ProposalStatusBadge';
import type { BiddingProposalResponse } from '@/services/bidding/proposals.service';

interface ProposalFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  proposal?: BiddingProposalResponse | null;
  onSubmit: (data: ProposalFormData) => Promise<void>;
  isLoading?: boolean;
}

export interface ProposalFormData {
  tender_id: string;
  cnpj: string;
  razao_social: string;
  numero_proposta?: string;
  valor_global: number;
  prazo_entrega?: number;
  validade_proposta?: number;
  observacoes_tecnicas?: string;
  observacoes_comerciais?: string;
  status?: ProposalStatus;
}

export function ProposalFormModal({
  isOpen,
  onClose,
  proposal,
  onSubmit,
  isLoading = false,
}: ProposalFormModalProps) {
  const isEditing = !!proposal;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<ProposalFormData>({
    tender_id: '',
    cnpj: '',
    razao_social: '',
    numero_proposta: '',
    valor_global: 0,
    prazo_entrega: 30,
    validade_proposta: 60,
    observacoes_tecnicas: '',
    observacoes_comerciais: '',
    status: 'rascunho',
  });

  useEffect(() => {
    if (isOpen) {
      if (proposal) {
        setFormData({
          tender_id: proposal.tender_id || '',
          cnpj: String(proposal.cnpj || ''),
          razao_social: String(proposal.razao_social || ''),
          numero_proposta: (proposal as any).numero_proposta || '',
          valor_global:
            typeof proposal.valor_global === 'string'
              ? parseFloat(proposal.valor_global)
              : Number(proposal.valor_global) || 0,
          prazo_entrega: (proposal as any).prazo_entrega || 30,
          validade_proposta: (proposal as any).validade_proposta || 60,
          observacoes_tecnicas: (proposal as any).observacoes_tecnicas || '',
          observacoes_comerciais: (proposal as any).observacoes_comerciais || '',
          status: (proposal.status as ProposalStatus) || 'rascunho',
        });
      } else {
        setFormData({
          tender_id: '',
          cnpj: '',
          razao_social: '',
          numero_proposta: '',
          valor_global: 0,
          prazo_entrega: 30,
          validade_proposta: 60,
          observacoes_tecnicas: '',
          observacoes_comerciais: '',
          status: 'rascunho',
        });
      }
      setError(null);
    }
  }, [isOpen, proposal]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleNumberChange = (name: keyof ProposalFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value ? parseFloat(value) : undefined,
    }));
  };

  const handleCNPJChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '');

    // Formata CNPJ: 00.000.000/0000-00
    value = value
      .replace(/(\d{2})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1/$2')
      .replace(/(\d{4})(\d{1,2})/, '$1-$2')
      .replace(/(-\d{2})\d+?$/, '$1');

    setFormData((prev) => ({ ...prev, cnpj: value }));
  };

  const handleSubmit = async () => {
    setError(null);

    // Validações
    if (!formData.tender_id?.trim()) {
      setError('Selecione um edital');
      return;
    }

    if (!formData.cnpj?.trim()) {
      setError('CNPJ é obrigatório');
      return;
    }

    if (!formData.razao_social?.trim()) {
      setError('Razão Social é obrigatória');
      return;
    }

    if (formData.valor_global <= 0) {
      setError('Valor Global deve ser maior que zero');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Erro ao salvar proposta');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Proposta' : 'Nova Proposta'}
      size="xl"
    >
      <div className="space-y-6">
        {error && (
          <Alert variant="destructive">
            <p>{error}</p>
          </Alert>
        )}

        {/* Informações do Edital */}
        <div className="space-y-4">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase">
            Informações do Edital
          </h3>

          <div className="space-y-2">
            <Label htmlFor="tender_id">
              Edital <span className="text-destructive">*</span>
            </Label>
            <Input
              id="tender_id"
              name="tender_id"
              value={formData.tender_id}
              onChange={handleChange}
              placeholder="ID do Edital"
              disabled={isSubmitting || isEditing}
             aria-label="I D Do  Edital" />
            <p className="text-xs text-muted-foreground">
              Selecione o edital ao qual esta proposta se refere
            </p>
          </div>
        </div>

        {/* Dados da Empresa */}
        <div className="space-y-4">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase">
            Dados da Empresa
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="cnpj">
                CNPJ <span className="text-destructive">*</span>
              </Label>
              <Input
                id="cnpj"
                name="cnpj"
                value={formData.cnpj}
                onChange={handleCNPJChange}
                placeholder="00.000.000/0000-00"
                disabled={isSubmitting}
                maxLength={18}
               aria-label="00.000.000/0000 00" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="razao_social">
                Razão Social <span className="text-destructive">*</span>
              </Label>
              <Input
                id="razao_social"
                name="razao_social"
                value={formData.razao_social}
                onChange={handleChange}
                placeholder="Nome da empresa"
                disabled={isSubmitting}
               aria-label="Nome Da Empresa" />
            </div>
          </div>
        </div>

        {/* Dados da Proposta */}
        <div className="space-y-4">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase">
            Dados da Proposta
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="numero_proposta">Número da Proposta</Label>
              <Input
                id="numero_proposta"
                name="numero_proposta"
                value={formData.numero_proposta}
                onChange={handleChange}
                placeholder="Gerado automaticamente"
                disabled={isSubmitting}
               aria-label="Gerado Automaticamente" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="valor_global">
                Valor Global (R$) <span className="text-destructive">*</span>
              </Label>
              <Input
                id="valor_global"
                type="number"
                step="0.01"
                min="0"
                value={formData.valor_global}
                onChange={(e) = aria-label="Number">
                  handleNumberChange('valor_global', e.target.value)
                }
                placeholder="0.00"
                disabled={isSubmitting}
              />
              {formData.valor_global > 0 && (
                <p className="text-xs text-muted-foreground">
                  {formatCurrency(formData.valor_global)}
                </p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="prazo_entrega">Prazo de Entrega (dias)</Label>
              <Input
                id="prazo_entrega"
                type="number"
                min="0"
                value={formData.prazo_entrega || ''}
                onChange={(e) = aria-label="Number">
                  handleNumberChange('prazo_entrega', e.target.value)
                }
                placeholder="30"
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="validade_proposta">
                Validade da Proposta (dias)
              </Label>
              <Input
                id="validade_proposta"
                type="number"
                min="0"
                value={formData.validade_proposta || ''}
                onChange={(e) = aria-label="Number">
                  handleNumberChange('validade_proposta', e.target.value)
                }
                placeholder="60"
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                disabled={isSubmitting}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
               aria-label="Status">
                {statusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Observações */}
        <div className="space-y-4">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase">
            Observações
          </h3>

          <div className="space-y-2">
            <Label htmlFor="observacoes_tecnicas">Observações Técnicas</Label>
            <Textarea
              id="observacoes_tecnicas"
              name="observacoes_tecnicas"
              value={formData.observacoes_tecnicas}
              onChange={handleChange}
              placeholder="Especificações técnicas, requisitos, etc..."
              rows={4}
              disabled={isSubmitting}
             aria-label="Especificações Técnicas, Requisitos, Etc..." />
          </div>

          <div className="space-y-2">
            <Label htmlFor="observacoes_comerciais">
              Observações Comerciais
            </Label>
            <Textarea
              id="observacoes_comerciais"
              name="observacoes_comerciais"
              value={formData.observacoes_comerciais}
              onChange={handleChange}
              placeholder="Condições comerciais, prazos de pagamento, etc..."
              rows={4}
              disabled={isSubmitting}
             aria-label="Condições Comerciais, Prazos De Pagamento, Etc..." />
          </div>
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isSubmitting}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Salvando...
            </>
          ) : isEditing ? (
            'Atualizar Proposta'
          ) : (
            'Criar Proposta'
          )}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
