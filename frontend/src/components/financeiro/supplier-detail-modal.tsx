'use client';

import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Users, Mail, Phone, MapPin, Tag, FileText, Star } from 'lucide-react';

interface SupplierDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  supplier: any;
}

export function SupplierDetailModal({
  isOpen,
  onClose,
  supplier,
}: SupplierDetailModalProps) {
  if (!supplier) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'blocked':
        return 'bg-red-500/10 text-red-500 border-red-500/30';
      case 'inactive':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Ativo';
      case 'blocked':
        return 'Bloqueado';
      case 'inactive':
        return 'Inativo';
      default:
        return status;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Fornecedor"
      size="lg"
    >
      <div className="space-y-6">
        {/* Header com nome e status */}
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-lg bg-orange-500/10 flex items-center justify-center flex-shrink-0">
            <Users className="w-7 h-7 text-orange-500" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-[hsl(var(--foreground))]">
              {supplier.name}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <span
                className={cn(
                  'inline-flex px-2 py-1 text-xs font-medium rounded-full border',
                  getStatusColor(supplier.status)
                )}
              >
                {getStatusLabel(supplier.status)}
              </span>
              {supplier.category && (
                <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full border bg-blue-500/10 text-blue-500 border-blue-500/30">
                  <Tag className="w-3 h-3" />
                  {supplier.category}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Informacoes */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {supplier.document && (
            <div className="flex items-start gap-3">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))] mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">CNPJ/CPF</p>
                <p className="text-sm font-medium font-mono text-[hsl(var(--foreground))]">
                  {supplier.document}
                </p>
              </div>
            </div>
          )}

          {supplier.email && (
            <div className="flex items-start gap-3">
              <Mail className="w-4 h-4 text-[hsl(var(--muted-foreground))] mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Email</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {supplier.email}
                </p>
              </div>
            </div>
          )}

          {supplier.phone && (
            <div className="flex items-start gap-3">
              <Phone className="w-4 h-4 text-[hsl(var(--muted-foreground))] mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Telefone</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {supplier.phone}
                </p>
              </div>
            </div>
          )}

          {supplier.address && (
            <div className="flex items-start gap-3">
              <MapPin className="w-4 h-4 text-[hsl(var(--muted-foreground))] mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Endereco</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {supplier.address}
                </p>
              </div>
            </div>
          )}

          {supplier.qualification_score != null && (
            <div className="flex items-start gap-3">
              <Star className="w-4 h-4 text-[hsl(var(--muted-foreground))] mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Qualificacao</p>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                    {supplier.qualification_score}/10
                  </p>
                  <div className="flex-1 h-2 bg-[hsl(var(--secondary))] rounded-full max-w-[100px]">
                    <div
                      className={cn(
                        'h-full rounded-full',
                        supplier.qualification_score >= 7
                          ? 'bg-green-500'
                          : supplier.qualification_score >= 4
                          ? 'bg-orange-500'
                          : 'bg-red-500'
                      )}
                      style={{ width: `${(supplier.qualification_score / 10) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Observacoes */}
        {(supplier.observacoes || supplier.notes) && (
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Observacoes</p>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {supplier.observacoes || supplier.notes}
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t border-[hsl(var(--border))]">
          <Button variant="outline" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </div>
    </Modal>
  );
}
