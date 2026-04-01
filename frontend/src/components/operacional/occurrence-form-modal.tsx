'use client';

import { AlertCircle, Loader2, Save, User, MapPin } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RestoreAlert } from '@/components/ui/restore-alert';
import { SaveIndicator } from '@/components/ui/save-indicator';
import { getErrorMessage } from '@/lib/api';
import {
  OCCURRENCE_TYPE_LABELS,
  OCCURRENCE_SEVERITY_LABELS,
  OCCURRENCE_CATEGORY_LABELS,
  type Occurrence,
  type OccurrenceType,
  type OccurrenceSeverity,
  type OccurrenceCategory,
  type OccurrenceCreate,
} from '@/types/operacional';
import { occurrencesService } from '@/services/occurrences';
import { usePosts } from '@/hooks/usePosts';
import { useEmployees } from '@/hooks/useEmployees';
import { useAutoSave } from '@/hooks/useAutoSave';

interface OccurrenceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editData?: Occurrence | null;
}

interface FormData {
  title: string;
  description: string;
  occurrence_type: OccurrenceType;
  severity: OccurrenceSeverity;
  category: OccurrenceCategory;
  employee_id: string;
  post_id: string;
  occurred_at: string;
  witnesses: string;
}

const initialFormData: FormData = {
  title: '',
  description: '',
  occurrence_type: 'outros',
  severity: 'leve',
  category: 'disciplinar',
  employee_id: '',
  post_id: '',
  occurred_at: new Date().toISOString().slice(0, 16),
  witnesses: '',
};

export function OccurrenceFormModal({
  isOpen,
  onClose,
  onSuccess,
  editData,
}: OccurrenceFormModalProps) {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [fieldErrors, setFieldErrors] = useState<Set<string>>(new Set());
  const [showRestoreAlert, setShowRestoreAlert] = useState(false);

  const { posts, isLoading: postsLoading } = usePosts({ autoLoad: isOpen });
  const { employees, isLoading: employeesLoading, refresh: refreshEmployees } = useEmployees({ autoLoad: false });

  const isEditing = !!editData;

  // Auto-save hook
  const autoSave = useAutoSave({
    key: 'ocorrencia_form',
    data: formData,
    debounceMs: 2000,
    enabled: isOpen && !isEditing,
  });

  // Carregar funcionários quando o modal abre
  useEffect(() => {
    if (isOpen && employees.length === 0 && !employeesLoading) {
      refreshEmployees();
    }
  }, [isOpen, employees.length, employeesLoading, refreshEmployees]);

  // Verificar rascunho ao abrir modal
  useEffect(() => {
    if (isOpen && !isEditing && autoSave.hasDraft) {
      setShowRestoreAlert(true);
    } else {
      setShowRestoreAlert(false);
    }
  }, [isOpen, isEditing, autoSave.hasDraft]);

  useEffect(() => {
    if (editData) {
      setFormData({
        title: editData.title || '',
        description: editData.description || '',
        occurrence_type: editData.occurrence_type,
        severity: editData.severity,
        category: editData.category,
        employee_id: editData.employee_id || '',
        post_id: editData.post_id || '',
        occurred_at: editData.occurred_at ? editData.occurred_at.slice(0, 16) : new Date().toISOString().slice(0, 16),
        witnesses: editData.witnesses || '',
      });
    } else {
      setFormData(initialFormData);
    }
    setError(null);
    setErrors([]);
    setFieldErrors(new Set());
  }, [editData, isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
    setErrors([]);
    // Remove erro do campo quando usuario comecar a digitar
    setFieldErrors((prev) => {
      const newErrors = new Set(prev);
      newErrors.delete(name);
      return newErrors;
    });
  };

  // Funcoes para restaurar e descartar rascunho
  const handleRestoreDraft = () => {
    const draft = autoSave.restore();
    if (draft) {
      setFormData({ ...formData, ...draft });
      setShowRestoreAlert(false);
    }
  };

  const handleDiscardDraft = () => {
    autoSave.clear();
    setShowRestoreAlert(false);
  };

  const validateForm = (): boolean => {
    const validationErrors: string[] = [];
    const invalidFields = new Set<string>();

    // Validar todos os campos obrigatorios
    if (!formData.title.trim()) {
      validationErrors.push('Titulo e obrigatorio');
      invalidFields.add('title');
    }

    if (!formData.description.trim()) {
      validationErrors.push('Descricao e obrigatoria');
      invalidFields.add('description');
    }

    if (!formData.employee_id) {
      validationErrors.push('Funcionario e obrigatorio');
      invalidFields.add('employee_id');
    }

    if (!formData.post_id) {
      validationErrors.push('Posto e obrigatorio');
      invalidFields.add('post_id');
    }

    if (!formData.occurred_at) {
      validationErrors.push('Data da ocorrencia e obrigatoria');
      invalidFields.add('occurred_at');
    }

    // Se houver erros, atualizar estados
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      setFieldErrors(invalidFields);
      return false;
    }

    // Limpar erros se tudo estiver ok
    setErrors([]);
    setFieldErrors(new Set());
    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);

    try {
      const dataToSend: OccurrenceCreate = {
        title: formData.title,
        description: formData.description,
        occurrence_type: formData.occurrence_type,
        severity: formData.severity,
        category: formData.category,
        employee_id: formData.employee_id,
        post_id: formData.post_id,
        occurred_at: formData.occurred_at,
        witnesses: formData.witnesses || null,
      };

      if (isEditing && editData?.id) {
        await occurrencesService.update(editData.id, {
          title: dataToSend.title,
          description: dataToSend.description,
          occurrence_type: dataToSend.occurrence_type,
          severity: dataToSend.severity,
          category: dataToSend.category,
          witnesses: dataToSend.witnesses,
        });
      } else {
        await occurrencesService.create(dataToSend);
      }

      // Limpar rascunho apos sucesso
      if (!isEditing) {
        autoSave.clear();
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Ocorrencia' : 'Nova Ocorrencia Disciplinar'}
      description={isEditing ? `Editando ${editData?.code}` : 'Registrar nova ocorrencia disciplinar'}
      size="xl"
    >
      <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="space-y-6">
        {/* Restore Alert */}
        {showRestoreAlert && (
          <RestoreAlert
            onRestore={handleRestoreDraft}
            onDiscard={handleDiscardDraft}
            savedAt={autoSave.lastSaved}
          />
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Lista de erros de validacao */}
        {errors.length > 0 && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-red-500 font-medium text-sm mb-2">
                  {errors.length} {errors.length === 1 ? 'campo obrigatorio faltando' : 'campos obrigatorios faltando'}
                </p>
                <ul className="space-y-1">
                  {errors.map((err, idx) => (
                    <li key={idx} className="text-red-500 text-sm flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0" />
                      {err}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Save Indicator */}
        {!isEditing && isOpen && (
          <div className="flex justify-end">
            <SaveIndicator
              saving={autoSave.saving}
              lastSaved={autoSave.lastSaved}
              error={autoSave.error}
            />
          </div>
        )}

        {/* Titulo */}
        <div>
          <label htmlFor="field-occurrence-title" className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
            Titulo <span className="text-red-500">*</span>
          </label>
          <Input
            id="field-occurrence-title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Titulo resumido da ocorrencia"
            className={fieldErrors.has('title') ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}
           aria-label="Titulo Resumido Da Ocorrencia" />
        </div>

        {/* Tipo, Severidade e Categoria */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="field-occurrence-type" className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
              Tipo de Ocorrencia *
            </label>
            <select
              id="field-occurrence-type"
              name="occurrence_type"
              value={formData.occurrence_type}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
             aria-label="Occurrence Type">
              {Object.entries(OCCURRENCE_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="field-occurrence-severity" className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
              Severidade *
            </label>
            <select
              id="field-occurrence-severity"
              name="severity"
              value={formData.severity}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
             aria-label="Severity">
              {Object.entries(OCCURRENCE_SEVERITY_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="field-occurrence-category" className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
              Categoria *
            </label>
            <select
              id="field-occurrence-category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
             aria-label="Category">
              {Object.entries(OCCURRENCE_CATEGORY_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Funcionario e Posto */}
        <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="field-occurrence-employee-id" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1 flex items-center gap-1">
                <User className="w-4 h-4" />
                Funcionario Envolvido <span className="text-red-500">*</span>
              </label>
              <select
                id="field-occurrence-employee-id"
                name="employee_id"
                value={formData.employee_id}
                onChange={handleChange}
                className={`w-full px-3 py-2 rounded-lg border bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm ${
                  fieldErrors.has('employee_id')
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                    : 'border-[hsl(var(--border))]'
                }`}
                disabled={employeesLoading || isEditing}
               aria-label="Employee Id">
                <option value="">Selecione o funcionario</option>
                {employees?.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.full_name || emp.name || emp.email}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="field-occurrence-post-id" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1 flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                Posto <span className="text-red-500">*</span>
              </label>
              <select
                id="field-occurrence-post-id"
                name="post_id"
                value={formData.post_id}
                onChange={handleChange}
                className={`w-full px-3 py-2 rounded-lg border bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm ${
                  fieldErrors.has('post_id')
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                    : 'border-[hsl(var(--border))]'
                }`}
                disabled={postsLoading || isEditing}
               aria-label="Post Id">
                <option value="">Selecione o posto</option>
                {posts?.map((post) => (
                  <option key={post.id} value={post.id}>
                    {post.name} ({post.code})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Descricao */}
        <div>
          <label htmlFor="field-occurrence-description" className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
            Descricao Detalhada <span className="text-red-500">*</span>
          </label>
          <textarea
            id="field-occurrence-description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Descreva detalhadamente o ocorrido, incluindo circunstancias, local exato, e qualquer informacao relevante..."
            rows={4}
            className={`w-full px-3 py-2 rounded-lg border bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none text-sm ${
              fieldErrors.has('description')
                ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                : 'border-[hsl(var(--border))]'
            }`}
           aria-label="Descreva Detalhadamente O Ocorrido, Incluindo Circunstancias, Local Exato, E Qualquer Informacao Relevante..." />
        </div>

        {/* Data e Testemunhas */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="field-occurred-at" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Data/Hora da Ocorrencia <span className="text-red-500">*</span>
            </label>
            <Input
              id="field-occurred-at"
              type="datetime-local"
              name="occurred_at"
              value={formData.occurred_at}
              onChange={handleChange}
              max={new Date().toISOString().slice(0, 16)}
              className={fieldErrors.has('occurred_at') ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}
             aria-label="Occurred At" />
          </div>

          <div>
            <label htmlFor="field-witnesses" className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Testemunhas
            </label>
            <Input
              id="field-witnesses"
              name="witnesses"
              value={formData.witnesses}
              onChange={handleChange}
              placeholder="Nomes das testemunhas (opcional)"
             aria-label="Nomes Das Testemunhas (Opcional)" />
          </div>
        </div>

        {/* Info sobre severidade */}
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-400">
          <p><strong>Severidades:</strong></p>
          <ul className="mt-1 space-y-1 text-xs">
            <li><strong>Leve:</strong> Advertencia verbal</li>
            <li><strong>Moderada:</strong> Advertencia escrita</li>
            <li><strong>Grave:</strong> Suspensao</li>
            <li><strong>Gravíssima:</strong> Demissão</li>
          </ul>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>

          <Button
            type="submit"
            variant="primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            {isEditing ? 'Salvar Alteracoes' : 'Registrar Ocorrencia'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
