'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';

interface EquipmentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  equipment: any;
}

export function EquipmentDetailModal({
  isOpen,
  onClose,
  equipment,
}: EquipmentDetailModalProps) {
  if (!equipment) return null;

  const getStatusBadge = (status: string) => {
    const map: Record<string, string> = {
      em_estoque: 'bg-blue-100 text-blue-800',
      em_campo: 'bg-green-100 text-green-800',
      em_manutencao: 'bg-yellow-100 text-yellow-800',
      inativo: 'bg-gray-100 text-gray-800',
    };
    const labels: Record<string, string> = {
      em_estoque: 'Em Estoque',
      em_campo: 'Em Campo',
      em_manutencao: 'Em Manutenção',
      inativo: 'Inativo',
    };
    return <Badge className={map[status] || ''}>{labels[status] || status}</Badge>;
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      camera: 'Câmera',
      controle_acesso: 'Controle de Acesso',
      alarme: 'Alarme',
      radio: 'Rádio',
      sensor: 'Sensor',
      outro: 'Outro',
    };
    return labels[type] || type;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={equipment.nome}
      description={equipment.codigo ? `Código: ${equipment.codigo}` : undefined}
      size="lg"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-muted-foreground">Código</p>
          <p className="text-sm font-mono">{equipment.codigo || '-'}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Nome</p>
          <p className="text-sm font-medium">{equipment.nome}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Tipo</p>
          <p className="text-sm">{getTypeLabel(equipment.equipment_type)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">N.Série</p>
          <p className="text-sm font-mono">{equipment.serial_number || '-'}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Marca</p>
          <p className="text-sm">{equipment.marca || '-'}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Modelo</p>
          <p className="text-sm">{equipment.modelo || '-'}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Status</p>
          <div className="mt-1">{getStatusBadge(equipment.status)}</div>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Localização</p>
          <p className="text-sm">{equipment.location || '-'}</p>
        </div>
        {equipment.observacoes && (
          <div className="col-span-2">
            <p className="text-xs text-muted-foreground">Observações</p>
            <p className="text-sm whitespace-pre-wrap">{equipment.observacoes}</p>
          </div>
        )}
      </div>
    </Modal>
  );
}
