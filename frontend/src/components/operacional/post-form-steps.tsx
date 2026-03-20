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
        <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Nome do Posto *
        </label>
        <Input
          name="name"
          value={formData.name}
          onChange={onChange}
          placeholder="Ex: Portaria Principal - Condomínio ABC"
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Tipo de Posto *
          </label>
          <select
            name="post_type"
            value={formData.post_type}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            required
          >
            {Object.entries(POST_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Tipo de Turno *
          </label>
          <select
            name="shift_type"
            value={formData.shift_type}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            required
          >
            {Object.entries(SHIFT_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Descricao
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={onChange}
          rows={3}
          placeholder="Descricao detalhada do posto..."
          className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
        />
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
        <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Endereco
        </label>
        <Input
          name="address"
          value={formData.address}
          onChange={onChange}
          placeholder="Rua, numero, bairro..."
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Cidade
          </label>
          <Input
            name="city"
            value={formData.city}
            onChange={onChange}
            placeholder="Cidade"
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            UF
          </label>
          <select
            name="state"
            value={formData.state}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
          >
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
        <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          CEP
        </label>
        <div className="relative">
          <Input
            name="zip_code"
            value={formData.zip_code}
            onChange={onChange}
            placeholder="00000-000"
            maxLength={9}
            disabled={isFetchingCep}
          />
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
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Efetivo Necessario *
          </label>
          <Input
            type="number"
            name="required_headcount"
            value={formData.required_headcount}
            onChange={onChange}
            min={1}
            required
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Intervalo (minutos)
          </label>
          <Input
            type="number"
            name="break_duration_minutes"
            value={formData.break_duration_minutes}
            onChange={onChange}
            min={0}
          />
        </div>
      </div>
      <div>
        <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Observacoes sobre o turno
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={onChange}
          rows={4}
          placeholder="Detalhes sobre horarios, pausas, troca de turno..."
          className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
        />
      </div>
    </div>
  );
}

// Step 4: Requisitos
export function StepRequisitos({ formData, onChange }: StepProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
          Experiencia Minima (meses)
        </label>
        <Input
          type="number"
          name="requires_experience_months"
          value={formData.requires_experience_months}
          onChange={onChange}
          min={0}
          placeholder="0 = sem requisito de experiência"
        />
      </div>
      <div className="space-y-3">
        <label className="flex items-center gap-2 cursor-pointer p-3 rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] transition-colors">
          <input
            type="checkbox"
            name="requires_armed"
            checked={formData.requires_armed}
            onChange={onChange}
            className="w-4 h-4 rounded border-[hsl(var(--border))]"
          />
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
          />
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
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Valor Hora (R$)
          </label>
          <Input
            type="number"
            name="hourly_rate"
            value={formData.hourly_rate}
            onChange={onChange}
            min={0}
            step={0.01}
            placeholder="0.00"
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Custo Mensal (R$)
          </label>
          <Input
            type="number"
            name="monthly_cost"
            value={formData.monthly_cost}
            onChange={onChange}
            min={0}
            step={0.01}
            placeholder="0.00"
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Adicional Noturno (%)
          </label>
          <Input
            type="number"
            name="night_shift_bonus_percent"
            value={formData.night_shift_bonus_percent}
            onChange={onChange}
            min={0}
            placeholder="20"
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Periculosidade (%)
          </label>
          <Input
            type="number"
            name="hazard_pay_percent"
            value={formData.hazard_pay_percent}
            onChange={onChange}
            min={0}
            placeholder="0"
          />
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
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Nome do Supervisor
          </label>
          <Input
            name="supervisor_name"
            value={formData.supervisor_name}
            onChange={onChange}
            placeholder="Nome completo"
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone do Supervisor
          </label>
          <Input
            name="supervisor_phone"
            value={formData.supervisor_phone}
            onChange={onChange}
            placeholder="(00) 00000-0000"
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Contato de Emergencia
          </label>
          <Input
            name="emergency_contact"
            value={formData.emergency_contact}
            onChange={onChange}
            placeholder="Nome completo"
          />
        </div>
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone de Emergencia
          </label>
          <Input
            name="emergency_phone"
            value={formData.emergency_phone}
            onChange={onChange}
            placeholder="(00) 00000-0000"
          />
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
