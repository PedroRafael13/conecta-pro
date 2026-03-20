'use client';

import { CheckCircle, Loader2, MapPin } from 'lucide-react';
import { Input } from '@/components/ui/input';
import type { DiaristFormData, FormChangeHandler } from './diarist-form-types';
import { ESTADOS } from './diarist-form-types';

interface DiaristDadosPessoaisTabProps {
  formData: DiaristFormData;
  onChange: FormChangeHandler;
  onCPFChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onCEPChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onPhoneChange: (field: 'telefone' | 'telefone_emergencia') => (e: React.ChangeEvent<HTMLInputElement>) => void;
  isFetchingCPF: boolean;
  cpfStatus: 'idle' | 'found' | 'not_found';
}

export function DiaristDadosPessoaisTab({
  formData,
  onChange,
  onCPFChange,
  onCEPChange,
  onPhoneChange,
  isFetchingCPF,
  cpfStatus,
}: DiaristDadosPessoaisTabProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Nome Completo *
          </label>
          <Input
            name="nome"
            value={formData.nome}
            onChange={onChange}
            placeholder="Nome completo do diarista"
            required
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            CPF * {cpfStatus === 'found' && <span className="text-green-500 text-xs ml-1">- Dados encontrados</span>}
          </label>
          <div className="relative">
            <Input
              value={formData.cpf}
              onChange={onCPFChange}
              placeholder="000.000.000-00"
              maxLength={14}
              required
            />
            {isFetchingCPF && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <Loader2 className="w-4 h-4 animate-spin text-[hsl(var(--muted-foreground))]" />
              </div>
            )}
            {!isFetchingCPF && cpfStatus === 'found' && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <CheckCircle className="w-4 h-4 text-green-500" />
              </div>
            )}
          </div>
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            RG
          </label>
          <Input
            name="rg"
            value={formData.rg}
            onChange={onChange}
            placeholder="RG"
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Data de Nascimento
          </label>
          <Input
            type="date"
            name="data_nascimento"
            value={formData.data_nascimento}
            onChange={onChange}
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Email
          </label>
          <Input
            type="email"
            name="email"
            value={formData.email}
            onChange={onChange}
            placeholder="email@exemplo.com"
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone
          </label>
          <Input
            value={formData.telefone}
            onChange={onPhoneChange('telefone')}
            placeholder="(00) 00000-0000"
            maxLength={15}
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone Emergencia
          </label>
          <Input
            value={formData.telefone_emergencia}
            onChange={onPhoneChange('telefone_emergencia')}
            placeholder="(00) 00000-0000"
            maxLength={15}
          />
        </div>
      </div>

      <div className="border-t border-[hsl(var(--border))] pt-4 mt-4">
        <div className="flex items-center gap-2 mb-3">
          <MapPin className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          <span className="text-sm font-medium text-[hsl(var(--foreground))]">Endereco</span>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              CEP
            </label>
            <Input
              value={formData.cep}
              onChange={onCEPChange}
              placeholder="00000-000"
              maxLength={9}
            />
          </div>
          <div className="col-span-2">
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Endereco
            </label>
            <Input
              name="endereco"
              value={formData.endereco}
              onChange={onChange}
              placeholder="Rua, numero, bairro"
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Cidade
            </label>
            <Input
              name="cidade"
              value={formData.cidade}
              onChange={onChange}
              placeholder="Cidade"
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Estado
            </label>
            <select
              name="estado"
              value={formData.estado}
              onChange={onChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            >
              <option value="">Selecione</option>
              {ESTADOS.map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
