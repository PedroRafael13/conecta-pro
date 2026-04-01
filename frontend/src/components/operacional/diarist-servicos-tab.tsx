'use client';

import { Input } from '@/components/ui/input';
import type { DiaristFormData, FormChangeHandler } from './diarist-form-types';
import { TIPOS_SERVICO, DIAS_SEMANA } from './diarist-form-types';

interface DiaristServicosTabProps {
  formData: DiaristFormData;
  onChange: FormChangeHandler;
  onTipoServicoChange: (tipo: string) => void;
  onDiaDisponivelChange: (dia: string) => void;
}

export function DiaristServicosTab({
  formData,
  onChange,
  onTipoServicoChange,
  onDiaDisponivelChange,
}: DiaristServicosTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-3">
          Tipos de Servico *
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {TIPOS_SERVICO.map((tipo) => (
            <label
              key={tipo.value}
              className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${
                formData.tipos_servico.includes(tipo.value)
                  ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/10'
                  : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]'
              }`}
            >
              <input
                type="checkbox"
                checked={formData.tipos_servico.includes(tipo.value)}
                onChange={() => onTipoServicoChange(tipo.value)}
                className="w-4 h-4 rounded"
              />
              <span className="text-sm text-[hsl(var(--foreground))]">{tipo.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-3">
          Dias Disponiveis
        </label>
        <div className="flex flex-wrap gap-2">
          {DIAS_SEMANA.map((dia) => (
            <label
              key={dia.value}
              className={`px-3 py-2 rounded-lg border cursor-pointer transition-colors ${
                formData.dias_disponiveis.includes(dia.value)
                  ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/10 text-[hsl(var(--primary))]'
                  : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] text-[hsl(var(--foreground))]'
              }`}
            >
              <input
                type="checkbox"
                checked={formData.dias_disponiveis.includes(dia.value)}
                onChange={() => onDiaDisponivelChange(dia.value)}
                className="sr-only"
              />
              <span className="text-sm">{dia.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-hora-inicio-disponivel" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Horario Inicio
          </label>
          <Input
            id="field-hora-inicio-disponivel"
            type="time"
            name="hora_inicio_disponivel"
            value={formData.hora_inicio_disponivel}
            onChange={onChange}
           aria-label="Hora Inicio Disponivel" />
        </div>
        <div>
          <label htmlFor="field-hora-fim-disponivel" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Horario Fim
          </label>
          <Input
            id="field-hora-fim-disponivel"
            type="time"
            name="hora_fim_disponivel"
            value={formData.hora_fim_disponivel}
            onChange={onChange}
           aria-label="Hora Fim Disponivel" />
        </div>
      </div>

      <div>
        <label htmlFor="field-experiencia-anos" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Anos de Experiencia
        </label>
        <Input
          id="field-experiencia-anos"
          type="number"
          name="experiencia_anos"
          value={formData.experiencia_anos}
          onChange={onChange}
          min={0}
         aria-label="Experiencia Anos" />
      </div>

      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          name="aceita_hora_extra"
          checked={formData.aceita_hora_extra}
          onChange={onChange}
          className="w-4 h-4 rounded"
         aria-label="Aceita Hora Extra" />
        <span className="text-sm text-[hsl(var(--foreground))]">Aceita hora extra</span>
      </label>
    </div>
  );
}
