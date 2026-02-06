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

interface ComunicadoFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  comunicado?: any;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

export function ComunicadoFormModal({
  isOpen,
  onClose,
  comunicado,
  onSubmit,
  isLoading,
}: ComunicadoFormModalProps) {
  const isEditing = !!comunicado;

  const [form, setForm] = useState({
    titulo: '',
    mensagem: '',
    tipo: 'informativo' as string,
    destinatarios: '',
    data_envio: new Date().toISOString().substring(0, 10),
  });

  useEffect(() => {
    if (comunicado) {
      setForm({
        titulo: comunicado.titulo || '',
        mensagem: comunicado.mensagem || '',
        tipo: comunicado.tipo || 'informativo',
        destinatarios: comunicado.destinatarios || '',
        data_envio: comunicado.data_envio
          ? comunicado.data_envio.substring(0, 10)
          : new Date().toISOString().substring(0, 10),
      });
    } else {
      setForm({
        titulo: '',
        mensagem: '',
        tipo: 'informativo',
        destinatarios: '',
        data_envio: new Date().toISOString().substring(0, 10),
      });
    }
  }, [comunicado, isOpen]);

  const handleSubmit = () => {
    if (!form.titulo.trim() || !form.mensagem.trim()) return;
    onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Comunicado' : 'Novo Comunicado'}
      description={isEditing ? 'Altere os dados do comunicado' : 'Preencha os dados do comunicado'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid gap-2">
          <Label htmlFor="com_titulo">Titulo</Label>
          <Input
            id="com_titulo"
            value={form.titulo}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
            placeholder="Titulo do comunicado..."
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="com_mensagem">Mensagem</Label>
          <Textarea
            id="com_mensagem"
            value={form.mensagem}
            onChange={(e) => setForm({ ...form, mensagem: e.target.value })}
            placeholder="Conteudo do comunicado..."
            rows={5}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label>Tipo</Label>
            <Select value={form.tipo} onValueChange={(v) => setForm({ ...form, tipo: v })}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="informativo">Informativo</SelectItem>
                <SelectItem value="urgente">Urgente</SelectItem>
                <SelectItem value="operacional">Operacional</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="com_data_envio">Data de Envio</Label>
            <Input
              id="com_data_envio"
              type="date"
              value={form.data_envio}
              onChange={(e) => setForm({ ...form, data_envio: e.target.value })}
            />
          </div>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="com_destinatarios">Destinatarios</Label>
          <Input
            id="com_destinatarios"
            value={form.destinatarios}
            onChange={(e) => setForm({ ...form, destinatarios: e.target.value })}
            placeholder="Ex: Todos, Equipe A, Supervisores..."
          />
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading || !form.titulo.trim() || !form.mensagem.trim()}>
          {isLoading ? 'Salvando...' : isEditing ? 'Salvar' : 'Criar'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
