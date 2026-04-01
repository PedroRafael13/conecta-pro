import { Loader2, FileText } from 'lucide-react';
import { Input } from '@/components/ui/input';
import type { PostCreate } from '@/types/operacional';
import { POST_TYPE_LABELS, SHIFT_TYPE_LABELS } from '@/types/operacional';
import { STATES, type PostFormChangeHandler } from './post-form-types';

interface StepProps {
  formData: PostCreate;
  onChange: PostFormChangeHandler;
}

// Step 1: Dados Básicos
export function StepDadosBasicos({ formData, onChange }: StepProps) {
  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="field-post-name" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Nome do Posto *
        </label>
        <Input
          id="field-post-name"
          name="name"
          value={formData.name}
          onChange={onChange}
          placeholder="Ex: Portaria Principal - Condomínio ABC"
          required
         aria-label="Ex: Portaria Principal - Condomínio ABC" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-post-type" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Tipo de Posto *
          </label>
          <select
            id="field-post-type"
            name="post_type"
            value={formData.post_type}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            required
           aria-label="Post Type">
            {Object.entries(POST_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="field-shift-type" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Tipo de Turno *
          </label>
          <select
            id="field-shift-type"
            name="shift_type"
            value={formData.shift_type}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            required
           aria-label="Shift Type">
            {Object.entries(SHIFT_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label htmlFor="field-post-description" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Descricao
        </label>
        <textarea
          id="field-post-description"
          name="description"
          value={formData.description}
          onChange={onChange}
          rows={3}
          placeholder="Descricao detalhada do posto..."
          className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
         aria-label="Descricao detalhada do posto..." />
      </div>
    </div>
  );
}

// Step 2: Localização
interface StepLocalizacaoProps extends StepProps {
  isFetchingCep: boolean;
  cepError: string | null;
}

export function StepLocalizacao({ formData, onChange, isFetchingCep, cepError }: StepLocalizacaoProps) {
  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="field-post-address" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Endereco
        </label>
        <Input
          id="field-post-address"
          name="address"
          value={formData.address}
          onChange={onChange}
          placeholder="Rua, numero, bairro..."
         aria-label="Rua, numero, bairro..." />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-post-city" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Cidade
          </label>
          <Input
            id="field-post-city"
            name="city"
            value={formData.city}
            onChange={onChange}
            placeholder="Cidade"
           aria-label="Cidade" />
        </div>
        <div>
          <label htmlFor="field-post-state" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            UF
          </label>
          <select
            id="field-post-state"
            name="state"
            value={formData.state}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
           aria-label="State">
            <option value="">-</option>
            {STATES.map((uf) => (
              <option key={uf} value={uf}>
                {uf}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label htmlFor="field-post-zip-code" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          CEP
        </label>
        <div className="relative">
          <Input
            id="field-post-zip-code"
            name="zip_code"
            value={formData.zip_code}
            onChange={onChange}
            placeholder="00000-000"
            maxLength={9}
            disabled={isFetchingCep}
           aria-label="00000-000" />
          {isFetchingCep && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <Loader2 className="w-4 h-4 animate-spin text-[hsl(var(--muted-foreground))]" />
            </div>
          )}
        </div>
        {cepError && (
          <p className="text-xs text-red-500 mt-1">{cepError}</p>
        )}
      </div>
    </div>
  );
}

// Step 3: Configuração
export function StepConfiguracao({ formData, onChange }: StepProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-required-headcount" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Efetivo Necessario *
          </label>
          <Input
            id="field-required-headcount"
            type="number"
            name="required_headcount"
            value={formData.required_headcount}
            onChange={onChange}
            min={1}
            required
           aria-label="Required Headcount" />
        </div>
        <div>
          <label htmlFor="field-break-duration-minutes" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Intervalo (minutos)
          </label>
          <Input
            id="field-break-duration-minutes"
            type="number"
            name="break_duration_minutes"
            value={formData.break_duration_minutes}
            onChange={onChange}
            min={0}
           aria-label="Break Duration Minutes" />
        </div>
      </div>
      <div>
        <label htmlFor="field-post-notes" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Observações sobre o turno
        </label>
        <textarea
          id="field-post-notes"
          name="notes"
          value={formData.notes}
          onChange={onChange}
          rows={4}
          placeholder="Detalhes sobre horarios, pausas, troca de turno..."
          className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
         aria-label="Detalhes sobre horarios, pausas, troca de turno..." />
      </div>
    </div>
  );
}

// Step 4: Requisitos
export function StepRequisitos({ formData, onChange }: StepProps) {
  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="field-requires-experience-months" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Experiencia Minima (meses)
        </label>
        <Input
          id="field-requires-experience-months"
          type="number"
          name="requires_experience_months"
          value={formData.requires_experience_months}
          onChange={onChange}
          min={0}
          placeholder="0 = sem requisito de experiência"
         aria-label="0 = sem requisito de experiência" />
      </div>
      <div className="space-y-3">
        <label className="flex items-center gap-2 cursor-pointer p-3 rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] transition-colors">
          <input
            type="checkbox"
            name="requires_armed"
            checked={formData.requires_armed}
            onChange={onChange}
            className="w-4 h-4 rounded border-[hsl(var(--border))]"
           aria-label="Requires Armed" />
          <div className="flex-1">
            <div className="text-sm font-medium text-[hsl(var(--foreground))]">
              Requer Armamento
            </div>
            <div className="text-xs text-[hsl(var(--muted-foreground))]">
              Colaborador precisa estar armado
            </div>
          </div>
        </label>
        <label className="flex items-center gap-2 cursor-pointer p-3 rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] transition-colors">
          <input
            type="checkbox"
            name="requires_vehicle"
            checked={formData.requires_vehicle}
            onChange={onChange}
            className="w-4 h-4 rounded border-[hsl(var(--border))]"
           aria-label="Requires Vehicle" />
          <div className="flex-1">
            <div className="text-sm font-medium text-[hsl(var(--foreground))]">
              Requer Veiculo
            </div>
            <div className="text-xs text-[hsl(var(--muted-foreground))]">
              Colaborador precisa ter veículo próprio
            </div>
          </div>
        </label>
      </div>
    </div>
  );
}

// Step 5: Financeiro
export function StepFinanceiro({ formData, onChange }: StepProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-hourly-rate" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Valor Hora (R$)
          </label>
          <Input
            id="field-hourly-rate"
            type="number"
            name="hourly_rate"
            value={formData.hourly_rate}
            onChange={onChange}
            min={0}
            step={0.01}
            placeholder="0.00"
           aria-label="0.00" />
        </div>
        <div>
          <label htmlFor="field-monthly-cost" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Custo Mensal (R$)
          </label>
          <Input
            id="field-monthly-cost"
            type="number"
            name="monthly_cost"
            value={formData.monthly_cost}
            onChange={onChange}
            min={0}
            step={0.01}
            placeholder="0.00"
           aria-label="0.00" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-night-shift-bonus-percent" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Adicional Noturno (%)
          </label>
          <Input
            id="field-night-shift-bonus-percent"
            type="number"
            name="night_shift_bonus_percent"
            value={formData.night_shift_bonus_percent}
            onChange={onChange}
            min={0}
            placeholder="20"
           aria-label="20" />
        </div>
        <div>
          <label htmlFor="field-hazard-pay-percent" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Periculosidade (%)
          </label>
          <Input
            id="field-hazard-pay-percent"
            type="number"
            name="hazard_pay_percent"
            value={formData.hazard_pay_percent}
            onChange={onChange}
            min={0}
            placeholder="0"
           aria-label="0" />
        </div>
      </div>
    </div>
  );
}

// Step 6: Contatos
export function StepContatos({ formData, onChange }: StepProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-supervisor-name" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Nome do Supervisor
          </label>
          <Input
            id="field-supervisor-name"
            name="supervisor_name"
            value={formData.supervisor_name}
            onChange={onChange}
            placeholder="Nome completo"
           aria-label="Nome completo" />
        </div>
        <div>
          <label htmlFor="field-supervisor-phone" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone do Supervisor
          </label>
          <Input
            id="field-supervisor-phone"
            name="supervisor_phone"
            value={formData.supervisor_phone}
            onChange={onChange}
            placeholder="(00) 00000-0000"
           aria-label="(00) 00000-0000" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="field-emergency-contact" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Contato de Emergencia
          </label>
          <Input
            id="field-emergency-contact"
            name="emergency_contact"
            value={formData.emergency_contact}
            onChange={onChange}
            placeholder="Nome completo"
           aria-label="Nome completo" />
        </div>
        <div>
          <label htmlFor="field-emergency-phone" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone de Emergencia
          </label>
          <Input
            id="field-emergency-phone"
            name="emergency_phone"
            value={formData.emergency_phone}
            onChange={onChange}
            placeholder="(00) 00000-0000"
           aria-label="(00) 00000-0000" />
        </div>
      </div>
    </div>
  );
}

// Summary / Review step
export function StepSummary({ formData }: { formData: PostCreate }) {
  return (
    <div className="space-y-6">
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <FileText className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-500 mb-1">Resumo do Posto</h4>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Revise as informações antes de salvar
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-[hsl(var(--muted-foreground))] mb-1">Nome</div>
          <div className="text-[hsl(var(--foreground))] font-medium">{formData.name || '-'}</div>
        </div>
        <div>
          <div className="text-[hsl(var(--muted-foreground))] mb-1">Tipo</div>
          <div className="text-[hsl(var(--foreground))] font-medium">
            {POST_TYPE_LABELS[formData.post_type]}
          </div>
        </div>
        <div>
          <div className="text-[hsl(var(--muted-foreground))] mb-1">Turno</div>
          <div className="text-[hsl(var(--foreground))] font-medium">
            {SHIFT_TYPE_LABELS[formData.shift_type]}
          </div>
        </div>
        <div>
          <div className="text-[hsl(var(--muted-foreground))] mb-1">Efetivo</div>
          <div className="text-[hsl(var(--foreground))] font-medium">
            {formData.required_headcount} {formData.required_headcount === 1 ? 'pessoa' : 'pessoas'}
          </div>
        </div>
        {formData.address && (
          <div className="md:col-span-2">
            <div className="text-[hsl(var(--muted-foreground))] mb-1">Endereço</div>
            <div className="text-[hsl(var(--foreground))] font-medium">
              {formData.address}
              {formData.city && `, ${formData.city}`}
              {formData.state && ` - ${formData.state}`}
            </div>
          </div>
        )}
        {((formData.hourly_rate ?? 0) > 0 || (formData.monthly_cost ?? 0) > 0) && (
          <>
            {(formData.hourly_rate ?? 0) > 0 && (
              <div>
                <div className="text-[hsl(var(--muted-foreground))] mb-1">Valor Hora</div>
                <div className="text-[hsl(var(--foreground))] font-medium">
                  R$ {(formData.hourly_rate ?? 0).toFixed(2)}
                </div>
              </div>
            )}
            {(formData.monthly_cost ?? 0) > 0 && (
              <div>
                <div className="text-[hsl(var(--muted-foreground))] mb-1">Custo Mensal</div>
                <div className="text-[hsl(var(--foreground))] font-medium">
                  R$ {(formData.monthly_cost ?? 0).toFixed(2)}
                </div>
              </div>
            )}
          </>
        )}
        {(formData.requires_armed || formData.requires_vehicle) && (
          <div className="md:col-span-2">
            <div className="text-[hsl(var(--muted-foreground))] mb-1">Requisitos</div>
            <div className="flex gap-2">
              {formData.requires_armed && (
                <span className="px-2 py-1 rounded bg-orange-500/10 text-orange-500 text-xs font-medium">
                  Armado
                </span>
              )}
              {formData.requires_vehicle && (
                <span className="px-2 py-1 rounded bg-blue-500/10 text-blue-500 text-xs font-medium">
                  Veículo
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
