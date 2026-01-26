'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RestoreAlert } from '@/components/ui/restore-alert';
import { SaveIndicator } from '@/components/ui/save-indicator';
import { occurrencesService } from '@/lib/services/occurrences';
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
import { AlertCircle, Loader2, Save, User, MapPin } from 'lucide-react';
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
  }, [editData, isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
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
    if (!formData.title.trim()) {
      setError('Titulo e obrigatorio');
      return false;
    }
    if (!formData.description.trim()) {
      setError('Descricao e obrigatoria');
      return false;
    }
    if (!formData.employee_id) {
      setError('Funcionario e obrigatorio');
      return false;
    }
    if (!formData.post_id) {
      setError('Posto e obrigatorio');
      return false;
    }
    if (!formData.occurred_at) {
      setError('Data da ocorrencia e obrigatoria');
      return false;
    }
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
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
            Titulo *
          </label>
          <Input
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Titulo resumido da ocorrencia"
          />
        </div>

        {/* Tipo, Severidade e Categoria */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
              Tipo de Ocorrencia *
            </label>
            <select
              name="occurrence_type"
              value={formData.occurrence_type}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
            >
              {Object.entries(OCCURRENCE_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
              Severidade *
            </label>
            <select
              name="severity"
              value={formData.severity}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
            >
              {Object.entries(OCCURRENCE_SEVERITY_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
              Categoria *
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
            >
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
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1 flex items-center gap-1">
                <User className="w-4 h-4" />
                Funcionario Envolvido *
              </label>
              <select
                name="employee_id"
                value={formData.employee_id}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
                disabled={employeesLoading || isEditing}
              >
                <option value="">Selecione o funcionario</option>
                {employees?.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.full_name || emp.name || emp.email}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1 flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                Posto *
              </label>
              <select
                name="post_id"
                value={formData.post_id}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm"
                disabled={postsLoading || isEditing}
              >
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
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
            Descricao Detalhada *
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Descreva detalhadamente o ocorrido, incluindo circunstancias, local exato, e qualquer informacao relevante..."
            rows={4}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none text-sm"
          />
        </div>

        {/* Data e Testemunhas */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Data/Hora da Ocorrencia *
            </label>
            <Input
              type="datetime-local"
              name="occurred_at"
              value={formData.occurred_at}
              onChange={handleChange}
              max={new Date().toISOString().slice(0, 16)}
            />
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Testemunhas
            </label>
            <Input
              name="witnesses"
              value={formData.witnesses}
              onChange={handleChange}
              placeholder="Nomes das testemunhas (opcional)"
            />
          </div>
        </div>

        {/* Info sobre severidade */}
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-400">
          <p><strong>Severidades:</strong></p>
          <ul className="mt-1 space-y-1 text-xs">
            <li><strong>Leve:</strong> Advertencia verbal</li>
            <li><strong>Moderada:</strong> Advertencia escrita</li>
            <li><strong>Grave:</strong> Suspensao</li>
            <li><strong>Gravissima:</strong> Demissao</li>
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
