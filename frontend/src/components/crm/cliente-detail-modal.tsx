'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { clientLabel } from '@/utils/crm/clientLabel';

interface ClienteDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  cliente: any | null;
}

const segmentoConfig: Record<string, { label: string; className: string }> = {
  residencial: { label: 'Residencial', className: 'bg-teal-100 text-teal-800' },
  comercial:   { label: 'Comercial',   className: 'bg-amber-100 text-amber-800' },
  industrial:  { label: 'Industrial',  className: 'bg-blue-100 text-blue-800' },
  publico:     { label: 'Público',     className: 'bg-purple-100 text-purple-800' },
  misto:       { label: 'Misto',       className: 'bg-indigo-100 text-indigo-800' },
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

  const segmento = segmentoConfig[cliente.segment] || {
    label: cliente.segment || '-',
    className: 'bg-gray-100 text-gray-800',
  };

  const status = statusConfig[cliente.status] || {
    label: cliente.status || '-',
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
          <p className="text-sm font-medium">{clientLabel(cliente)}</p>
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
          <Label className="text-muted-foreground text-xs">Segmento</Label>
          <div className="mt-1">
            <Badge className={segmento.className}>{segmento.label}</Badge>
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
          {/* endereco_texto = campo adicionado por T4 (P0.2 backend); fallback para objeto estruturado */}
          {cliente.endereco_texto ? (
            <p className="text-sm">{cliente.endereco_texto}</p>
          ) : (() => {
            const e = cliente.endereco;
            if (!e) return <p className="text-sm">-</p>;
            if (typeof e === 'string') return <p className="text-sm">{e}</p>;
            const partes = [
              e.rua && e.numero ? `${e.rua}, ${e.numero}` : e.rua,
              e.bairro,
              e.cidade && e.estado ? `${e.cidade}/${e.estado}` : e.cidade,
              e.cep ? `CEP ${e.cep}` : null,
            ].filter(Boolean);
            return <p className="text-sm">{partes.length ? partes.join(' — ') : '-'}</p>;
          })()}
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
