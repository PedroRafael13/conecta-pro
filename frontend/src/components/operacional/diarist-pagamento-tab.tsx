'use client';

import { DollarSign } from 'lucide-react';
import { Input } from '@/components/ui/input';
import type { DiaristFormData, FormChangeHandler } from './diarist-form-types';

interface DiaristPagamentoTabProps {
  formData: DiaristFormData;
  onChange: FormChangeHandler;
}

export function DiaristPagamentoTab({ formData, onChange }: DiaristPagamentoTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Valor da Diaria (R$) *
          </label>
          <Input
            type="number"
            name="valor_diaria"
            value={formData.valor_diaria}
            onChange={onChange}
            min={0}
            step={0.01}
            placeholder="0.00"
            required
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Valor Hora Extra (R$)
          </label>
          <Input
            type="number"
            name="valor_hora_extra"
            value={formData.valor_hora_extra}
            onChange={onChange}
            min={0}
            step={0.01}
            placeholder="25.00"
          />
        </div>
      </div>

      <div className="border-t border-[hsl(var(--border))] pt-4">
        <div className="flex items-center gap-2 mb-3">
          <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          <span className="text-sm font-medium text-[hsl(var(--foreground))]">
            Dados Bancarios
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Banco
            </label>
            <Input
              name="banco"
              value={formData.banco}
              onChange={onChange}
              placeholder="Nome do banco"
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Tipo de Conta
            </label>
            <select
              name="tipo_conta"
              value={formData.tipo_conta}
              onChange={onChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            >
              <option value="">Selecione</option>
              <option value="corrente">Corrente</option>
              <option value="poupanca">Poupanca</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Agencia
            </label>
            <Input
              name="agencia"
              value={formData.agencia}
              onChange={onChange}
              placeholder="0000"
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Conta
            </label>
            <Input
              name="conta"
              value={formData.conta}
              onChange={onChange}
              placeholder="00000-0"
            />
          </div>
          <div className="col-span-2">
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Chave PIX
            </label>
            <Input
              name="pix"
              value={formData.pix}
              onChange={onChange}
              placeholder="CPF, Email, Telefone ou Chave Aleatoria"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
