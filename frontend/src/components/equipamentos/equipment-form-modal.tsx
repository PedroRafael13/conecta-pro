'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
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
import { Textarea } from '@/components/ui/textarea';

interface EquipmentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  equipment?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

export function EquipmentFormModal({
  isOpen,
  onClose,
  equipment,
  onSubmit,
  isLoading,
}: EquipmentFormModalProps) {
  const isEditing = !!equipment;
  const [form, setForm] = useState({
    nome: '',
    equipment_type: 'camera',
    serial_number: '',
    marca: '',
    modelo: '',
    location: '',
    observacoes: '',
  });

  useEffect(() => {
    if (equipment) {
      setForm({
        nome: equipment.nome || '',
        equipment_type: equipment.equipment_type || 'camera',
        serial_number: equipment.serial_number || '',
        marca: equipment.marca || '',
        modelo: equipment.modelo || '',
        location: equipment.location || '',
        observacoes: equipment.observacoes || '',
      });
    } else {
      setForm({
        nome: '',
        equipment_type: 'camera',
        serial_number: '',
        marca: '',
        modelo: '',
        location: '',
        observacoes: '',
      });
    }
  }, [equipment, isOpen]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Equipamento' : 'Novo Equipamento'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="nome">Nome *</Label>
            <Input
              id="nome"
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              placeholder="Nome do equipamento"
            />
          </div>
          <div className="grid gap-2">
            <Label>Tipo</Label>
            <Select value={form.equipment_type} onValueChange={(v) => setForm({ ...form, equipment_type: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="camera">Câmera</SelectItem>
                <SelectItem value="controle_acesso">Controle de Acesso</SelectItem>
                <SelectItem value="alarme">Alarme</SelectItem>
                <SelectItem value="radio">Rádio</SelectItem>
                <SelectItem value="sensor">Sensor</SelectItem>
                <SelectItem value="outro">Outro</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="serial_number">Número de Série</Label>
            <Input
              id="serial_number"
              value={form.serial_number}
              onChange={(e) => setForm({ ...form, serial_number: e.target.value })}
              placeholder="SN-000000"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="marca">Marca</Label>
            <Input
              id="marca"
              value={form.marca}
              onChange={(e) => setForm({ ...form, marca: e.target.value })}
              placeholder="Ex: Intelbras, Hikvision..."
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="modelo">Modelo</Label>
            <Input
              id="modelo"
              value={form.modelo}
              onChange={(e) => setForm({ ...form, modelo: e.target.value })}
              placeholder="Modelo do equipamento"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="location">Localização</Label>
            <Input
              id="location"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              placeholder="Local de instalação"
            />
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="observacoes">Observações</Label>
          <Textarea
            id="observacoes"
            value={form.observacoes}
            onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
            placeholder="Informações adicionais sobre o equipamento..."
            rows={3}
          />
        </div>
      </div>
      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading || !form.nome.trim()}>
          {isLoading ? 'Salvando...' : isEditing ? 'Salvar' : 'Criar'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
