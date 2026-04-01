'use client';

import { useState, useEffect, useMemo } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { NotificationTemplateResponse } from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

interface TemplateFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  template?: NotificationTemplateResponse | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

// Initial form state factory
const createInitialForm = (template?: NotificationTemplateResponse | null) => ({
  codigo: template?.codigo || '',
  nome: template?.nome || '',
  descricao: template?.descricao || '',
  channel: template?.channel || 'email',
  category: template?.category || 'system',
  email_subject: template?.email_subject || template?.subject || '',
  body_html: template?.body_html || '',
  body_text: template?.body_text || '',
  sms_body: template?.sms_body || '',
  push_title: template?.push_title || '',
  push_body: template?.push_body || '',
  in_app_title: template?.in_app_title || '',
  in_app_body: template?.in_app_body || '',
});

export function TemplateFormModal({
  isOpen,
  onClose,
  template,
  onSubmit,
  isLoading,
}: TemplateFormModalProps) {
  const isEditing = !!template;

  const formKey = useMemo(() => {
    return template?.id || template?.codigo || 'new';
  }, [template]);

  const [form, setForm] = useState(createInitialForm(template));

  useEffect(() => {
    if (isOpen) {

      setForm(createInitialForm(template));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, [isOpen, formKey]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Template' : 'Novo Template'}
      size="xl"
    >
      <div className="grid gap-4">
        {/* Basic Info */}
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="tpl_codigo">Codigo</Label>
            <Input
              id="tpl_codigo"
              value={form.codigo}
              onChange={(e) => setForm({ ...form, codigo: e.target.value })}
              placeholder="welcome_email"
              disabled={isEditing}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="tpl_nome">Nome</Label>
            <Input
              id="tpl_nome"
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              placeholder="Nome do template"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label>Canal</Label>
            <Select value={form.channel} onValueChange={(v) => setForm({ ...form, channel: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="email">E-mail</SelectItem>
                <SelectItem value="sms">SMS</SelectItem>
                <SelectItem value="push">Push</SelectItem>
                <SelectItem value="whatsapp">WhatsApp</SelectItem>
                <SelectItem value="in_app">In-App</SelectItem>
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
                <SelectItem value="system">Sistema</SelectItem>
                <SelectItem value="operational">Operacional</SelectItem>
                <SelectItem value="financial">Financeiro</SelectItem>
                <SelectItem value="marketing">Marketing</SelectItem>
                <SelectItem value="security">Seguranca</SelectItem>
                <SelectItem value="hr">RH</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="tpl_descricao">Descricao</Label>
          <Input
            id="tpl_descricao"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            placeholder="Descricao do template..."
          />
        </div>

        {/* Channel-specific content */}
        <Tabs defaultValue={form.channel} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="email">Email</TabsTrigger>
            <TabsTrigger value="sms">SMS</TabsTrigger>
            <TabsTrigger value="push">Push</TabsTrigger>
            <TabsTrigger value="in_app">In-App</TabsTrigger>
          </TabsList>

          <TabsContent value="email" className="space-y-3 mt-3">
            <div className="grid gap-2">
              <Label htmlFor="email_subject">Assunto</Label>
              <Input
                id="email_subject"
                value={form.email_subject}
                onChange={(e) => setForm({ ...form, email_subject: e.target.value })}
                placeholder="Assunto do email..."
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="body_html">Body HTML</Label>
              <Textarea
                id="body_html"
                value={form.body_html}
                onChange={(e) => setForm({ ...form, body_html: e.target.value })}
                placeholder="<html>...</html>"
                rows={6}
                className="font-mono text-xs"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="body_text">Body Texto</Label>
              <Textarea
                id="body_text"
                value={form.body_text}
                onChange={(e) => setForm({ ...form, body_text: e.target.value })}
                placeholder="Versao texto plano..."
                rows={3}
              />
            </div>
          </TabsContent>

          <TabsContent value="sms" className="space-y-3 mt-3">
            <div className="grid gap-2">
              <Label htmlFor="sms_body">Mensagem SMS</Label>
              <Textarea
                id="sms_body"
                value={form.sms_body}
                onChange={(e) => setForm({ ...form, sms_body: e.target.value })}
                placeholder="Mensagem SMS (max 160 caracteres)..."
                rows={3}
              />
              <p className="text-xs text-muted-foreground">{form.sms_body.length}/160 caracteres</p>
            </div>
          </TabsContent>

          <TabsContent value="push" className="space-y-3 mt-3">
            <div className="grid gap-2">
              <Label htmlFor="push_title">Titulo</Label>
              <Input
                id="push_title"
                value={form.push_title}
                onChange={(e) => setForm({ ...form, push_title: e.target.value })}
                placeholder="Titulo da notificacao push"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="push_body">Mensagem</Label>
              <Textarea
                id="push_body"
                value={form.push_body}
                onChange={(e) => setForm({ ...form, push_body: e.target.value })}
                placeholder="Corpo da notificacao push..."
                rows={3}
              />
            </div>
          </TabsContent>

          <TabsContent value="in_app" className="space-y-3 mt-3">
            <div className="grid gap-2">
              <Label htmlFor="in_app_title">Titulo</Label>
              <Input
                id="in_app_title"
                value={form.in_app_title}
                onChange={(e) => setForm({ ...form, in_app_title: e.target.value })}
                placeholder="Titulo da notificacao in-app"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="in_app_body">Mensagem</Label>
              <Textarea
                id="in_app_body"
                value={form.in_app_body}
                onChange={(e) => setForm({ ...form, in_app_body: e.target.value })}
                placeholder="Corpo da notificacao in-app..."
                rows={3}
              />
            </div>
          </TabsContent>
        </Tabs>

        <p className="text-xs text-muted-foreground">
          Use {'{{variavel}}'} para inserir variaveis dinamicas no conteudo.
        </p>
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
