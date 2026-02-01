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

interface WebhookFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  webhook?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

export function WebhookFormModal({
  isOpen,
  onClose,
  webhook,
  onSubmit,
  isLoading,
}: WebhookFormModalProps) {
  const isEditing = !!webhook;
  const [form, setForm] = useState({
    name: '',
    url: '',
    events: '',
    status: 'active',
    headers: '',
  });

  useEffect(() => {
    if (webhook) {
      setForm({
        name: webhook.name || '',
        url: webhook.url || '',
        events: Array.isArray(webhook.events) ? webhook.events.join(', ') : webhook.events || '',
        status: webhook.status || 'active',
        headers: webhook.headers ? (typeof webhook.headers === 'string' ? webhook.headers : JSON.stringify(webhook.headers, null, 2)) : '',
      });
    } else {
      setForm({
        name: '',
        url: '',
        events: '',
        status: 'active',
        headers: '',
      });
    }
  }, [webhook, isOpen]);

  const handleSubmit = async () => {
    const eventsArray = form.events
      .split(',')
      .map((e) => e.trim())
      .filter((e) => e.length > 0);

    let parsedHeaders: Record<string, string> | undefined;
    if (form.headers.trim()) {
      try {
        parsedHeaders = JSON.parse(form.headers);
      } catch {
        parsedHeaders = undefined;
      }
    }

    await onSubmit({
      name: form.name,
      url: form.url,
      events: eventsArray,
      status: form.status,
      headers: parsedHeaders,
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Webhook' : 'Novo Webhook'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="webhook-name">Nome</Label>
            <Input
              id="webhook-name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Ex: Notificacao Slack"
            />
          </div>
          <div className="grid gap-2">
            <Label>Status</Label>
            <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Ativo</SelectItem>
                <SelectItem value="inactive">Inativo</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="webhook-url">URL</Label>
          <Input
            id="webhook-url"
            value={form.url}
            onChange={(e) => setForm({ ...form, url: e.target.value })}
            placeholder="https://exemplo.com/webhook"
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="webhook-events">Eventos</Label>
          <Input
            id="webhook-events"
            value={form.events}
            onChange={(e) => setForm({ ...form, events: e.target.value })}
            placeholder="user.created, order.completed, payment.received"
          />
          <p className="text-xs text-muted-foreground">
            Separe os eventos por virgula
          </p>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="webhook-headers">Headers (JSON)</Label>
          <textarea
            id="webhook-headers"
            value={form.headers}
            onChange={(e) => setForm({ ...form, headers: e.target.value })}
            placeholder='{"Authorization": "Bearer token", "X-Custom": "value"}'
            rows={3}
            className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
          />
          <p className="text-xs text-muted-foreground">
            Headers customizados em formato JSON (opcional)
          </p>
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
