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
          <label htmlFor="field-nome" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Nome Completo *
          </label>
          <Input
            id="field-nome"
            name="nome"
            value={formData.nome}
            onChange={onChange}
            placeholder="Nome completo do diarista"
            required
           aria-label="Nome Completo Do Diarista" />
        </div>
        <div>
          <label htmlFor="field-cpf" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            CPF * {cpfStatus === 'found' && <span className="text-green-500 text-xs ml-1">- Dados encontrados</span>}
          </label>
          <div className="relative">
            <Input
              id="field-cpf"
              value={formData.cpf}
              onChange={onCPFChange}
              placeholder="000.000.000-00"
              maxLength={14}
              required
             aria-label="000.000.000 00" />
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
          <label htmlFor="field-rg" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            RG
          </label>
          <Input
            id="field-rg"
            name="rg"
            value={formData.rg}
            onChange={onChange}
            placeholder="RG"
           aria-label="R G" />
        </div>
        <div>
          <label htmlFor="field-data-nascimento" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Data de Nascimento
          </label>
          <Input
            id="field-data-nascimento"
            type="date"
            name="data_nascimento"
            value={formData.data_nascimento}
            onChange={onChange}
           aria-label="Data Nascimento" />
        </div>
        <div>
          <label htmlFor="field-email" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Email
          </label>
          <Input
            id="field-email"
            type="email"
            name="email"
            value={formData.email}
            onChange={onChange}
            placeholder="email@exemplo.com"
           aria-label="Email@Exemplo.Com" />
        </div>
        <div>
          <label htmlFor="field-telefone" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone
          </label>
          <Input
            id="field-telefone"
            value={formData.telefone}
            onChange={onPhoneChange('telefone')}
            placeholder="(00) 00000-0000"
            maxLength={15}
           aria-label="(00) 00000 0000" />
        </div>
        <div>
          <label htmlFor="field-telefone-emergencia" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone Emergencia
          </label>
          <Input
            id="field-telefone-emergencia"
            value={formData.telefone_emergencia}
            onChange={onPhoneChange('telefone_emergencia')}
            placeholder="(00) 00000-0000"
            maxLength={15}
           aria-label="(00) 00000 0000" />
        </div>
      </div>

      <div className="border-t border-[hsl(var(--border))] pt-4 mt-4">
        <div className="flex items-center gap-2 mb-3">
          <MapPin className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          <span className="text-sm font-medium text-[hsl(var(--foreground))]">Endereco</span>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label htmlFor="field-cep" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              CEP
            </label>
            <Input
              id="field-cep"
              value={formData.cep}
              onChange={onCEPChange}
              placeholder="00000-000"
              maxLength={9}
             aria-label="00000 000" />
          </div>
          <div className="col-span-2">
            <label htmlFor="field-endereco" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Endereco
            </label>
            <Input
              id="field-endereco"
              name="endereco"
              value={formData.endereco}
              onChange={onChange}
              placeholder="Rua, numero, bairro"
             aria-label="Rua, Numero, Bairro" />
          </div>
          <div>
            <label htmlFor="field-cidade" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Cidade
            </label>
            <Input
              id="field-cidade"
              name="cidade"
              value={formData.cidade}
              onChange={onChange}
              placeholder="Cidade"
             aria-label="Cidade" />
          </div>
          <div>
            <label htmlFor="field-estado" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Estado
            </label>
            <select
              id="field-estado"
              name="estado"
              value={formData.estado}
              onChange={onChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
             aria-label="Estado">
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
