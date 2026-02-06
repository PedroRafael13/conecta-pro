'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
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
import type { FeatureFlagResponse } from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

interface FeatureFlagFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  flag?: FeatureFlagResponse | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

export function FeatureFlagFormModal({
  isOpen,
  onClose,
  flag,
  onSubmit,
  isLoading,
}: FeatureFlagFormModalProps) {
  const isEditing = !!flag;
  const [form, setForm] = useState({
    codigo: '',
    nome: '',
    descricao: '',
    flag_type: 'boolean',
    category: 'features',
    owner_team: '',
  });

  useEffect(() => {
    if (flag) {
      setForm({
        codigo: flag.codigo || '',
        nome: flag.nome || '',
        descricao: flag.descricao || '',
        flag_type: flag.flag_type || 'boolean',
        category: flag.category || 'features',
        owner_team: flag.owner_team || '',
      });
    } else {
      setForm({
        codigo: '',
        nome: '',
        descricao: '',
        flag_type: 'boolean',
        category: 'features',
        owner_team: '',
      });
    }
  }, [flag, isOpen]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Feature Flag' : 'Nova Feature Flag'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="ff_codigo">Codigo</Label>
            <Input
              id="ff_codigo"
              value={form.codigo}
              onChange={(e) => setForm({ ...form, codigo: e.target.value })}
              placeholder="feature_name"
              disabled={isEditing}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="ff_nome">Nome</Label>
            <Input
              id="ff_nome"
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              placeholder="Nome da feature"
            />
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="ff_descricao">Descricao</Label>
          <Textarea
            id="ff_descricao"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            placeholder="Descricao da feature flag..."
            rows={3}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <Label>Tipo</Label>
            <Select value={form.flag_type} onValueChange={(v) => setForm({ ...form, flag_type: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="boolean">Boolean</SelectItem>
                <SelectItem value="percentage">Percentage</SelectItem>
                <SelectItem value="gradual">Gradual</SelectItem>
                <SelectItem value="whitelist">Whitelist</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label>Categoria</Label>
            <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="features">Funcionalidades</SelectItem>
                <SelectItem value="experimental">Experimental</SelectItem>
                <SelectItem value="maintenance">Manutencao</SelectItem>
                <SelectItem value="performance">Performance</SelectItem>
                <SelectItem value="ui">Interface</SelectItem>
                <SelectItem value="integrations">Integracoes</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="ff_team">Time Responsavel</Label>
            <Input
              id="ff_team"
              value={form.owner_team}
              onChange={(e) => setForm({ ...form, owner_team: e.target.value })}
              placeholder="backend, frontend..."
            />
          </div>
        </div>
      </div>
      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? 'Salvando...' : isEditing ? 'Salvar' : 'Criar'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
