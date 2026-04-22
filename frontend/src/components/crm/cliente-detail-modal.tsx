'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { clientLabel } from '@/utils/crm/clientLabel';
import { CLIENT_SEGMENT_LABELS, CLIENT_SEGMENT_COLORS } from '@/constants/crm/clientSegment';
import { CLIENT_STATUS_LABELS, CLIENT_STATUS_COLORS } from '@/constants/crm/clientStatus';

interface ClienteDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  cliente: any | null;
}

export function ClienteDetailModal({
  isOpen,
  onClose,
  cliente,
}: ClienteDetailModalProps) {
  if (!cliente) return null;

  const segmento = {
    label: CLIENT_SEGMENT_LABELS[cliente.segment] ?? cliente.segment ?? '-',
    className: CLIENT_SEGMENT_COLORS[cliente.segment] ?? 'bg-gray-100 text-gray-800',
  };

  const status = {
    label: CLIENT_STATUS_LABELS[cliente.status] ?? cliente.status ?? '-',
    className: CLIENT_STATUS_COLORS[cliente.status] ?? 'bg-gray-100 text-gray-800',
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
