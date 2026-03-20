'use client';

/**
 * Modal de Formulário de Edital
 * Criação e edição de editais com validação
 */

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, FileText, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useCriarEdital, useAtualizarEdital } from '@/hooks/bidding/useTenders';
import type { TenderResponse } from '@/types/generated/bidding';

const tenderSchema = z.object({
  title: z.string().min(3, 'Título deve ter no mínimo 3 caracteres'),
  description: z.string().optional(),
  modality: z.string().min(1, 'Modalidade é obrigatória'),
  opening_date: z.string().min(1, 'Data de abertura é obrigatória'),
  closing_date: z.string().optional(),
  estimated_value: z.number().optional(),
  number: z.string().optional(),
  entity: z.string().optional(),
  uf: z.string().optional(),
  city: z.string().optional(),
  segment: z.string().optional(),
  judgment_criteria: z.string().optional(),
  publication_date: z.string().optional(),
  deadline_date: z.string().optional(),
  link: z.string().url('Link inválido').optional().or(z.literal('')),
  observations: z.string().optional(),
});

type TenderFormData = z.infer<typeof tenderSchema>;

interface TenderFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  editData?: TenderResponse | null;
}

const MODALIDADES = [
  { value: 'pregao_eletronico', label: 'Pregão Eletrônico' },
  { value: 'pregao_presencial', label: 'Pregão Presencial' },
  { value: 'concorrencia', label: 'Concorrência' },
  { value: 'tomada_precos', label: 'Tomada de Preços' },
  { value: 'convite', label: 'Convite' },
  { value: 'concurso', label: 'Concurso' },
  { value: 'leilao', label: 'Leilão' },
  { value: 'credenciamento', label: 'Credenciamento' },
  { value: 'rdc', label: 'RDC' },
  { value: 'dialogo_competitivo', label: 'Diálogo Competitivo' },
  { value: 'dispensa', label: 'Dispensa' },
  { value: 'inexigibilidade', label: 'Inexigibilidade' },
];

const CRITERIOS = [
  { value: 'menor_preco', label: 'Menor Preço' },
  { value: 'maior_desconto', label: 'Maior Desconto' },
  { value: 'melhor_tecnica', label: 'Melhor Técnica' },
  { value: 'tecnica_preco', label: 'Técnica e Preço' },
  { value: 'maior_lance', label: 'Maior Lance' },
  { value: 'maior_retorno', label: 'Maior Retorno Econômico' },
];

const UFS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO'
];

const SEGMENTOS = [
  { value: 'limpeza', label: 'Limpeza' },
  { value: 'vigilancia', label: 'Vigilância' },
  { value: 'manutencao', label: 'Manutenção' },
  { value: 'obras', label: 'Obras' },
  { value: 'tecnologia', label: 'Tecnologia' },
  { value: 'consultoria', label: 'Consultoria' },
  { value: 'materiais', label: 'Materiais' },
  { value: 'equipamentos', label: 'Equipamentos' },
  { value: 'servicos_gerais', label: 'Serviços Gerais' },
];

export function TenderFormModal({
  isOpen,
  onClose,
  onSuccess,
  editData,
}: TenderFormModalProps) {
  const criarMutation = useCriarEdital();
  const atualizarMutation = useAtualizarEdital();
  const isEditing = !!editData;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TenderFormData>({
    resolver: zodResolver(tenderSchema),
  });

  useEffect(() => {
    if (isOpen && editData) {
      reset({
        title: editData.title || '',
        description: editData.description || '',
        modality: editData.modality || '',
        opening_date: editData.opening_date
          ? new Date(editData.opening_date).toISOString().slice(0, 16)
          : '',
        closing_date: editData.closing_date
          ? new Date(editData.closing_date).toISOString().slice(0, 16)
          : '',
        estimated_value: editData.estimated_value || undefined,
        number: (editData as any).number || '',
        entity: (editData as any).entity || '',
        uf: (editData as any).uf || '',
        city: (editData as any).city || '',
        segment: (editData as any).segment || '',
        judgment_criteria: (editData as any).judgment_criteria || '',
        publication_date: (editData as any).publication_date
          ? new Date((editData as any).publication_date).toISOString().slice(0, 10)
          : '',
        deadline_date: (editData as any).deadline_date
          ? new Date((editData as any).deadline_date).toISOString().slice(0, 10)
          : '',
        link: (editData as any).link || '',
        observations: (editData as any).observations || '',
      });
    } else if (isOpen && !editData) {
      reset({
        title: '',
        description: '',
        modality: '',
        opening_date: '',
        closing_date: '',
        estimated_value: undefined,
        number: '',
        entity: '',
        uf: '',
        city: '',
        segment: '',
        judgment_criteria: '',
        publication_date: '',
        deadline_date: '',
        link: '',
        observations: '',
      });
    }
  }, [isOpen, editData, reset]);

  const onSubmit = async (data: TenderFormData) => {
    try {
      if (isEditing && editData) {
        await atualizarMutation.mutateAsync({
          id: editData.id,
          data: data as any,
        });
      } else {
        await criarMutation.mutateAsync(data as any);
      }
      onSuccess?.();
      onClose();
    } catch (error) {
    }
  };

  const isLoading = criarMutation.isPending || atualizarMutation.isPending;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <DialogTitle>
                {isEditing ? 'Editar Edital' : 'Novo Edital'}
              </DialogTitle>
              <DialogDescription>
                {isEditing
                  ? 'Atualize as informações do edital'
                  : 'Preencha os dados do novo edital'}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Número e Órgão */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="number">
                Número do Edital <span className="text-red-500">*</span>
              </Label>
              <Input
                id="number"
                {...register('number')}
                placeholder="Ex: 001/2024"
              />
              {errors.number && (
                <p className="text-xs text-red-500 mt-1">{errors.number.message}</p>
              )}
            </div>
            <div>
              <Label htmlFor="entity">
                Órgão/Entidade <span className="text-red-500">*</span>
              </Label>
              <Input
                id="entity"
                {...register('entity')}
                placeholder="Ex: Prefeitura Municipal"
              />
              {errors.entity && (
                <p className="text-xs text-red-500 mt-1">{errors.entity.message}</p>
              )}
            </div>
          </div>

          {/* Título */}
          <div>
            <Label htmlFor="title">
              Objeto <span className="text-red-500">*</span>
            </Label>
            <textarea
              id="title"
              {...register('title')}
              placeholder="Descreva o objeto da licitação..."
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] min-h-[80px]"
            />
            {errors.title && (
              <p className="text-xs text-red-500 mt-1">{errors.title.message}</p>
            )}
          </div>

          {/* Modalidade e Critério */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="modality">
                Modalidade <span className="text-red-500">*</span>
              </Label>
              <select
                id="modality"
                {...register('modality')}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              >
                <option value="">Selecione...</option>
                {MODALIDADES.map((mod) => (
                  <option key={mod.value} value={mod.value}>
                    {mod.label}
                  </option>
                ))}
              </select>
              {errors.modality && (
                <p className="text-xs text-red-500 mt-1">{errors.modality.message}</p>
              )}
            </div>
            <div>
              <Label htmlFor="judgment_criteria">Critério de Julgamento</Label>
              <select
                id="judgment_criteria"
                {...register('judgment_criteria')}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              >
                <option value="">Selecione...</option>
                {CRITERIOS.map((crit) => (
                  <option key={crit.value} value={crit.value}>
                    {crit.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Valor Estimado e Segmento */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="estimated_value">Valor Estimado (R$)</Label>
              <Input
                id="estimated_value"
                type="number"
                step="0.01"
                {...register('estimated_value', { valueAsNumber: true })}
                placeholder="0,00"
              />
            </div>
            <div>
              <Label htmlFor="segment">Segmento</Label>
              <select
                id="segment"
                {...register('segment')}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              >
                <option value="">Selecione...</option>
                {SEGMENTOS.map((seg) => (
                  <option key={seg.value} value={seg.value}>
                    {seg.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Datas */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="publication_date">Data de Publicação</Label>
              <Input
                id="publication_date"
                type="date"
                {...register('publication_date')}
              />
            </div>
            <div>
              <Label htmlFor="opening_date">
                Data de Abertura <span className="text-red-500">*</span>
              </Label>
              <Input
                id="opening_date"
                type="datetime-local"
                {...register('opening_date')}
              />
              {errors.opening_date && (
                <p className="text-xs text-red-500 mt-1">
                  {errors.opening_date.message}
                </p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="deadline_date">Prazo para Proposta</Label>
              <Input
                id="deadline_date"
                type="date"
                {...register('deadline_date')}
              />
            </div>
            <div>
              <Label htmlFor="closing_date">Data de Encerramento</Label>
              <Input
                id="closing_date"
                type="datetime-local"
                {...register('closing_date')}
              />
            </div>
          </div>

          {/* UF e Cidade */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="uf">UF</Label>
              <select
                id="uf"
                {...register('uf')}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              >
                <option value="">Selecione...</option>
                {UFS.map((uf) => (
                  <option key={uf} value={uf}>
                    {uf}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="city">Cidade</Label>
              <Input id="city" {...register('city')} placeholder="Ex: São Paulo" />
            </div>
          </div>

          {/* Link */}
          <div>
            <Label htmlFor="link">Link do Edital</Label>
            <Input
              id="link"
              type="url"
              {...register('link')}
              placeholder="https://..."
            />
            {errors.link && (
              <p className="text-xs text-red-500 mt-1">{errors.link.message}</p>
            )}
          </div>

          {/* Observações */}
          <div>
            <Label htmlFor="observations">Observações</Label>
            <textarea
              id="observations"
              {...register('observations')}
              placeholder="Observações adicionais..."
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] min-h-[80px]"
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>{isEditing ? 'Atualizar' : 'Criar'} Edital</>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
