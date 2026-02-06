'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ConfigValueEditor } from './config-value-editor';
import type { SystemConfigResponse } from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

interface SystemConfigFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  config?: SystemConfigResponse | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

export function SystemConfigFormModal({
  isOpen,
  onClose,
  config,
  onSubmit,
  isLoading,
}: SystemConfigFormModalProps) {
  const isEditing = !!config;
  const [form, setForm] = useState({
    chave: '',
    valor: '' as unknown,
    descricao: '',
    value_type: 'string',
    category: 'system',
    scope: 'global',
    admin_only: false,
    cacheable: true,
    requires_restart: false,
  });

  useEffect(() => {
    if (config) {
      setForm({
        chave: config.chave || '',
        valor: config.valor ?? '',
        descricao: config.descricao || '',
        value_type: config.value_type || 'string',
        category: config.category || 'system',
        scope: config.scope || 'global',
        admin_only: config.admin_only ?? false,
        cacheable: config.cacheable ?? true,
        requires_restart: config.requires_restart ?? false,
      });
    } else {
      setForm({
        chave: '',
        valor: '',
        descricao: '',
        value_type: 'string',
        category: 'system',
        scope: 'global',
        admin_only: false,
        cacheable: true,
        requires_restart: false,
      });
    }
  }, [config, isOpen]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Configuracao' : 'Nova Configuracao'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="sc_chave">Chave</Label>
            <Input
              id="sc_chave"
              value={form.chave}
              onChange={(e) => setForm({ ...form, chave: e.target.value })}
              placeholder="app.config.key"
              disabled={isEditing}
              className="font-mono"
            />
          </div>
          <div className="grid gap-2">
            <Label>Tipo de Valor</Label>
            <Select value={form.value_type} onValueChange={(v) => setForm({ ...form, value_type: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="string">String</SelectItem>
                <SelectItem value="number">Number</SelectItem>
                <SelectItem value="boolean">Boolean</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid gap-2">
          <Label>Valor</Label>
          <ConfigValueEditor
            value={form.valor}
            valueType={form.value_type}
            onChange={(v) => setForm({ ...form, valor: v })}
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="sc_descricao">Descricao</Label>
          <Textarea
            id="sc_descricao"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            placeholder="Descricao da configuracao..."
            rows={2}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label>Categoria</Label>
            <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="system">Sistema</SelectItem>
                <SelectItem value="application">Aplicacao</SelectItem>
                <SelectItem value="integrations">Integracoes</SelectItem>
                <SelectItem value="security">Seguranca</SelectItem>
                <SelectItem value="performance">Performance</SelectItem>
                <SelectItem value="maintenance">Manutencao</SelectItem>
                <SelectItem value="features">Funcionalidades</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label>Escopo</Label>
            <Select value={form.scope} onValueChange={(v) => setForm({ ...form, scope: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="global">Global</SelectItem>
                <SelectItem value="tenant">Por Tenant</SelectItem>
                <SelectItem value="user">Por Usuario</SelectItem>
                <SelectItem value="module">Por Modulo</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex flex-wrap gap-6 pt-2">
          <div className="flex items-center gap-2">
            <Switch
              checked={form.admin_only}
              onCheckedChange={(checked) => setForm({ ...form, admin_only: checked })}
            />
            <Label className="text-sm">Admin Only</Label>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              checked={form.cacheable}
              onCheckedChange={(checked) => setForm({ ...form, cacheable: checked })}
            />
            <Label className="text-sm">Cacheable</Label>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              checked={form.requires_restart}
              onCheckedChange={(checked) => setForm({ ...form, requires_restart: checked })}
            />
            <Label className="text-sm">Requires Restart</Label>
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
