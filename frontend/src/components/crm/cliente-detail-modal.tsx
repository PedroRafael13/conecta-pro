'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

interface ClienteDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  cliente: any | null;
}

const tipoConfig: Record<string, { label: string; className: string }> = {
  condominio: { label: 'Condomínio', className: 'bg-blue-100 text-blue-800' },
  empresa: { label: 'Empresa', className: 'bg-purple-100 text-purple-800' },
  residencial: { label: 'Residencial', className: 'bg-green-100 text-green-800' },
};

const statusConfig: Record<string, { label: string; className: string }> = {
  ativo: { label: 'Ativo', className: 'bg-green-100 text-green-800' },
  inativo: { label: 'Inativo', className: 'bg-red-100 text-red-800' },
  prospecto: { label: 'Prospecto', className: 'bg-yellow-100 text-yellow-800' },
};

export function ClienteDetailModal({
  isOpen,
  onClose,
  cliente,
}: ClienteDetailModalProps) {
  if (!cliente) return null;

  const tipo = tipoConfig[cliente.tipo] || {
    label: cliente.tipo,
    className: 'bg-gray-100 text-gray-800',
  };

  const status = statusConfig[cliente.status] || {
    label: cliente.status || 'Ativo',
    className: 'bg-gray-100 text-gray-800',
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Cliente"
      size="lg"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-muted-foreground text-xs">Nome</Label>
          <p className="text-sm font-medium">{cliente.nome}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">CNPJ</Label>
          <p className="text-sm font-mono">{cliente.cnpj || '-'}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Email</Label>
          <p className="text-sm">{cliente.email || '-'}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Telefone</Label>
          <p className="text-sm">{cliente.telefone || '-'}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Tipo</Label>
          <div className="mt-1">
            <Badge className={tipo.className}>{tipo.label}</Badge>
          </div>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Status</Label>
          <div className="mt-1">
            <Badge className={status.className}>{status.label}</Badge>
          </div>
        </div>
        <div className="col-span-2">
          <Label className="text-muted-foreground text-xs">Endereço</Label>
          <p className="text-sm">{cliente.endereco || '-'}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Criado em</Label>
          <p className="text-sm">
            {cliente.created_at
              ? new Date(cliente.created_at).toLocaleDateString('pt-BR')
              : '-'}
          </p>
        </div>
      </div>
    </Modal>
  );
}
