'use client';

import { useState, useEffect } from 'react';
import { X, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

export function DocumentUploadModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: DocumentUploadModalProps) {
  const [formData, setFormData] = useState({
    tipo_documento: 'contrato_social',
    nome: '',
    data_validade: '',
    arquivo_url: '',
    observacoes: '',
  });

  useEffect(() => {
    if (!isOpen) {
      setFormData({
        tipo_documento: 'contrato_social',
        nome: '',
        data_validade: '',
        arquivo_url: '',
        observacoes: '',
      });
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const tiposDocumento = [
    { value: 'contrato_social', label: 'Contrato Social' },
    { value: 'estatuto', label: 'Estatuto Social' },
    { value: 'ata_eleicao', label: 'Ata de Eleição' },
    { value: 'procuracao', label: 'Procuração' },
    { value: 'rg_cnh', label: 'RG/CNH' },
    { value: 'balanco_patrimonial', label: 'Balanço Patrimonial' },
    { value: 'declaracao_mei', label: 'Declaração MEI' },
    { value: 'alvara', label: 'Alvará de Funcionamento' },
    { value: 'certidao_cnd', label: 'Certidão Negativa' },
    { value: 'atestado_capacidade', label: 'Atestado de Capacidade Técnica' },
    { value: 'registro_profissional', label: 'Registro Profissional' },
    { value: 'outros', label: 'Outros' },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload de Documento</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="tipo_documento">Tipo de Documento *</Label>
            <Select
              value={formData.tipo_documento}
              onValueChange={(value) =>
                setFormData({ ...formData, tipo_documento: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {tiposDocumento.map((tipo) => (
                  <SelectItem key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="nome">Nome/Descrição *</Label>
            <Input
              id="nome"
              value={formData.nome}
              onChange={(e) =>
                setFormData({ ...formData, nome: e.target.value })
              }
              required
              placeholder="Ex: Contrato Social Atualizado 2024"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="data_validade">Data de Validade</Label>
            <Input
              id="data_validade"
              type="date"
              value={formData.data_validade}
              onChange={(e) =>
                setFormData({ ...formData, data_validade: e.target.value })
              }
            />
            <p className="text-xs text-muted-foreground">
              Deixe em branco se o documento não possui validade
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="arquivo_url">URL do Arquivo *</Label>
            <Input
              id="arquivo_url"
              value={formData.arquivo_url}
              onChange={(e) =>
                setFormData({ ...formData, arquivo_url: e.target.value })
              }
              required
              placeholder="https://..."
            />
            <p className="text-xs text-muted-foreground">
              Upload do arquivo será implementado. Por enquanto, use URL externa.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="observacoes">Observações</Label>
            <Textarea
              id="observacoes"
              value={formData.observacoes}
              onChange={(e) =>
                setFormData({ ...formData, observacoes: e.target.value })
              }
              placeholder="Informações adicionais sobre o documento"
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              <X className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
            <Button type="submit" disabled={isLoading}>
              <Upload className="h-4 w-4 mr-2" />
              {isLoading ? 'Enviando...' : 'Enviar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
