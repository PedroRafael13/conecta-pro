'use client';

import { useMemo, useState } from 'react';
import { Calendar, Users, Settings, AlertCircle } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useScaleOperations } from '@/hooks/useScales';
import { useEmployees } from '@/hooks/useEmployees';
import type { Employee, Post, ScaleType, ScaleGenerateRequest } from '@/types/operacional';
import { SCALE_TYPE_LABELS } from '@/types/operacional';

interface ScaleGenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
  posts: Post[];
  onSuccess: () => void;
}

export function ScaleGenerateModal({
  isOpen,
  onClose,
  posts,
  onSuccess,
}: ScaleGenerateModalProps) {
  const { generateScale, isLoading, error } = useScaleOperations();
  const { employees, isLoading: employeesLoading } = useEmployees({ initialPageSize: 200 });
  const currentDate = new Date();

  // Form state
  const [postId, setPostId] = useState('');
  const [month, setMonth] = useState(currentDate.getMonth() + 1);
  const [year, setYear] = useState(currentDate.getFullYear());
  const [scaleType, setScaleType] = useState<ScaleType>('12x36');
  const [employeeIds, setEmployeeIds] = useState<string[]>([]);
  const [config, setConfig] = useState({
    consider_holidays: true,
    balance_night_shifts: true,
    max_consecutive_days: 6,
    min_rest_hours: 11,
  });

  // Validation
  const [validationError, setValidationError] = useState<string | null>(null);
  const [employeeSearch, setEmployeeSearch] = useState('');

  // Month names
  const monthNames = [
    'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ];

  const handleSubmit = async () => {
    setValidationError(null);

    // Validation
    if (!postId) {
      setValidationError('Selecione um posto');
      return;
    }

    if (employeeIds.length === 0) {
      setValidationError('Selecione pelo menos um funcionario');
      return;
    }

    const data: ScaleGenerateRequest = {
      post_id: postId,
      month,
      year,
      scale_type: scaleType,
      employee_ids: employeeIds,
      config,
    };

    const result = await generateScale(data);
    if (result) {
      // Reset form
      setPostId('');
      setMonth(currentDate.getMonth() + 1);
      setYear(currentDate.getFullYear());
      setScaleType('12x36');
      setEmployeeIds([]);
      setEmployeeSearch('');
      onSuccess();
    }
  };

  const handleClose = () => {
    setValidationError(null);
    onClose();
  };

  const getEmployeeLabel = (employee: Employee) => {
    return (
      employee.full_name ||
      employee.name ||
      employee.email ||
      employee.registration ||
      employee.id
    );
  };

  const filteredEmployees = useMemo(() => {
    const term = employeeSearch.trim().toLowerCase();
    if (!term) return employees;
    return employees.filter((employee) =>
      getEmployeeLabel(employee).toLowerCase().includes(term)
    );
  }, [employees, employeeSearch]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Gerar Nova Escala"
      description="Configure os parametros para gerar a escala automaticamente"
      size="lg"
    >
      <div className="space-y-6">
        {/* Error message */}
        {(validationError || error) && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{validationError || error}</span>
          </div>
        )}

        {/* Posto Selection */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Posto de Trabalho *
          </label>
          <select
            className="w-full h-10 px-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
            value={postId}
            onChange={(e) => setPostId(e.target.value)}
          >
            <option value="">Selecione um posto</option>
            {posts.map((post) => (
              <option key={post.id} value={post.id}>
                {post.name} ({post.code})
              </option>
            ))}
          </select>
        </div>

        {/* Period Selection */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
              Mes *
            </label>
            <select
              className="w-full h-10 px-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
            >
              {monthNames.map((name, index) => (
                <option key={index} value={index + 1}>{name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
              Ano *
            </label>
            <select
              className="w-full h-10 px-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
            >
              {[2024, 2025, 2026, 2027].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Scale Type */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Tipo de Escala *
          </label>
          <select
            className="w-full h-10 px-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
            value={scaleType}
            onChange={(e) => setScaleType(e.target.value as ScaleType)}
          >
            {Object.entries(SCALE_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>

        {/* Employees Selection */}
        <div className="bg-[hsl(var(--muted))]/30 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-[hsl(var(--foreground))] flex items-center gap-2">
              <Users className="w-4 h-4" />
              Funcionarios
            </h3>
            <span className="text-xs text-[hsl(var(--muted-foreground))]">
              {employeeIds.length} selecionado(s)
            </span>
          </div>
          <Input
            placeholder="Buscar funcionario..."
            value={employeeSearch}
            onChange={(e) => setEmployeeSearch(e.target.value)}
            className="mb-3"
          />
          <div className="max-h-48 overflow-y-auto space-y-2 pr-2">
            {employeesLoading ? (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Carregando funcionarios...
              </p>
            ) : filteredEmployees.length === 0 ? (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Nenhum funcionario encontrado
              </p>
            ) : (
              filteredEmployees.map((employee) => {
                const label = getEmployeeLabel(employee);
                const isChecked = employeeIds.includes(employee.id);
                return (
                  <label key={employee.id} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setEmployeeIds((prev) => [...prev, employee.id]);
                        } else {
                          setEmployeeIds((prev) => prev.filter((id) => id !== employee.id));
                        }
                      }}
                      className="rounded border-[hsl(var(--border))]"
                    />
                    <span className="text-[hsl(var(--foreground))]">{label}</span>
                  </label>
                );
              })
            )}
          </div>
        </div>

        {/* Config Options */}
        <div className="bg-[hsl(var(--muted))]/50 rounded-xl p-4">
          <h3 className="text-sm font-medium text-[hsl(var(--foreground))] mb-3 flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Configuracoes da Escala
          </h3>
          <div className="space-y-3">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={config.consider_holidays}
                onChange={(e) => setConfig({ ...config, consider_holidays: e.target.checked })}
                className="rounded border-[hsl(var(--border))]"
              />
              <span className="text-sm text-[hsl(var(--foreground))]">
                Considerar feriados
              </span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={config.balance_night_shifts}
                onChange={(e) => setConfig({ ...config, balance_night_shifts: e.target.checked })}
                className="rounded border-[hsl(var(--border))]"
              />
              <span className="text-sm text-[hsl(var(--foreground))]">
                Balancear turnos noturnos
              </span>
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                  Max. dias consecutivos
                </label>
                <Input
                  type="number"
                  value={config.max_consecutive_days}
                  onChange={(e) => setConfig({ ...config, max_consecutive_days: Number(e.target.value) })}
                  min={1}
                  max={7}
                />
              </div>
              <div>
                <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                  Min. horas de descanso
                </label>
                <Input
                  type="number"
                  value={config.min_rest_hours}
                  onChange={(e) => setConfig({ ...config, min_rest_hours: Number(e.target.value) })}
                  min={8}
                  max={24}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-500/10 text-blue-500 text-sm">
          <Calendar className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Geracao Automatica</p>
            <p className="text-xs opacity-80 mt-1">
              A escala sera gerada automaticamente com base no tipo selecionado e nas configuracoes definidas.
              Os funcionarios alocados ao posto serao automaticamente incluidos na escala.
            </p>
          </div>
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={handleClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? 'Gerando...' : 'Gerar Escala'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
