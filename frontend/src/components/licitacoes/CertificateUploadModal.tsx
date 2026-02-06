'use client';

import { useState, useEffect } from 'react';
import { X, Upload } from 'lucide-react';
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';

interface CertificateUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

export function CertificateUploadModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: CertificateUploadModalProps) {
  const [formData, setFormData] = useState({
    cnpj: '',
    tipo_certidao: 'federal_receita',
    numero_certidao: '',
    data_emissao: '',
    data_validade: '',
    arquivo_url: '',
  });

  useEffect(() => {
    if (!isOpen) {
      setFormData({
        cnpj: '',
        tipo_certidao: 'federal_receita',
        numero_certidao: '',
        data_emissao: '',
        data_validade: '',
        arquivo_url: '',
      });
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const tiposCertidao = [
    { value: 'federal_receita', label: 'Federal - Receita Federal' },
    { value: 'federal_pgfn', label: 'Federal - PGFN (Dívida Ativa)' },
    { value: 'federal_fgts', label: 'Federal - FGTS' },
    { value: 'federal_inss', label: 'Federal - INSS (CND Previdenciária)' },
    { value: 'federal_cndt', label: 'Federal - CNDT (TST)' },
    { value: 'estadual_receita', label: 'Estadual - Receita Estadual' },
    { value: 'estadual_divida', label: 'Estadual - Dívida Ativa' },
    { value: 'municipal_iss', label: 'Municipal - ISS' },
    { value: 'municipal_iptu', label: 'Municipal - IPTU' },
    { value: 'municipal_divida', label: 'Municipal - Dívida Ativa' },
    { value: 'trabalhista_tst', label: 'Trabalhista - TST' },
    { value: 'trabalhista_trt', label: 'Trabalhista - TRT' },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload de Certidão</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cnpj">CNPJ da Empresa *</Label>
            <Input
              id="cnpj"
              value={formData.cnpj}
              onChange={(e) =>
                setFormData({ ...formData, cnpj: e.target.value })
              }
              required
              placeholder="00.000.000/0000-00"
              maxLength={18}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="tipo_certidao">Tipo de Certidão *</Label>
            <Select
              value={formData.tipo_certidao}
              onValueChange={(value) =>
                setFormData({ ...formData, tipo_certidao: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="max-h-60">
                {tiposCertidao.map((tipo) => (
                  <SelectItem key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="numero_certidao">Número da Certidão *</Label>
            <Input
              id="numero_certidao"
              value={formData.numero_certidao}
              onChange={(e) =>
                setFormData({ ...formData, numero_certidao: e.target.value })
              }
              required
              placeholder="Ex: 123456789"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="data_emissao">Data de Emissão *</Label>
              <Input
                id="data_emissao"
                type="date"
                value={formData.data_emissao}
                onChange={(e) =>
                  setFormData({ ...formData, data_emissao: e.target.value })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_validade">Data de Validade *</Label>
              <Input
                id="data_validade"
                type="date"
                value={formData.data_validade}
                onChange={(e) =>
                  setFormData({ ...formData, data_validade: e.target.value })
                }
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="arquivo_url">URL do Arquivo (PDF) *</Label>
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
