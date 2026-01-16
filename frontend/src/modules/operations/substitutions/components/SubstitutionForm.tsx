import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Upload,
  AlertTriangle,
  FileText,
  Calendar,
  Clock,
  MapPin,
  User,
  Save,
  Trash2,
  Info,
} from 'lucide-react';
import type {
  SubstitutionFormData,
  SubstitutionReason,
  AvailableSubstitute,
} from '../types/substitutions.types';

interface SubstitutionFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: SubstitutionFormData) => Promise<void>;
  scheduleInfo?: {
    id: string;
    posto_nome: string;
    data: string;
    turno: string;
    horario_inicio: string;
    horario_fim: string;
  };
  availableSubstitutes?: AvailableSubstitute[];
  isLoading?: boolean;
}

const MOTIVOS: { value: SubstitutionReason; label: string; description: string }[] = [
  {
    value: 'atestado_medico',
    label: 'Atestado Medico',
    description: 'Impossibilitado por motivo de saude',
  },
  {
    value: 'emergencia_pessoal',
    label: 'Emergencia Pessoal',
    description: 'Situacao familiar ou pessoal urgente',
  },
  {
    value: 'problema_transporte',
    label: 'Problema de Transporte',
    description: 'Impossibilidade de deslocamento',
  },
  {
    value: 'ferias',
    label: 'Ferias',
    description: 'Periodo de ferias programado',
  },
  {
    value: 'licenca',
    label: 'Licenca',
    description: 'Licenca aprovada (paternidade, casamento, etc)',
  },
  {
    value: 'folga_compensatoria',
    label: 'Folga Compensatoria',
    description: 'Compensacao de horas extras',
  },
  {
    value: 'troca_turno',
    label: 'Troca de Turno',
    description: 'Acordo de troca com outro profissional',
  },
  {
    value: 'outro',
    label: 'Outro',
    description: 'Outro motivo nao listado',
  },
];

export const SubstitutionForm: React.FC<SubstitutionFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  scheduleInfo,
  availableSubstitutes = [],
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<SubstitutionFormData>({
    schedule_id: scheduleInfo?.id || '',
    motivo: 'atestado_medico',
    motivo_descricao: '',
    substituto_id: undefined,
    urgente: false,
    documentos: [],
  });

  const [files, setFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleMotivoChange = (motivo: SubstitutionReason) => {
    setFormData((prev) => ({ ...prev, motivo }));
    setErrors((prev) => ({ ...prev, motivo: '' }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    const validFiles = selectedFiles.filter((file) => {
      const isValid = file.size <= 5 * 1024 * 1024; // 5MB max
      const isAllowedType = ['application/pdf', 'image/jpeg', 'image/png'].includes(
        file.type
      );
      return isValid && isAllowedType;
    });

    setFiles((prev) => [...prev, ...validFiles]);
    setFormData((prev) => ({
      ...prev,
      documentos: [...(prev.documentos || []), ...validFiles],
    }));
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    setFormData((prev) => ({
      ...prev,
      documentos: (prev.documentos || []).filter((_, i) => i !== index),
    }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.motivo) {
      newErrors.motivo = 'Selecione um motivo';
    }

    if (formData.motivo === 'outro' && !formData.motivo_descricao?.trim()) {
      newErrors.motivo_descricao = 'Descreva o motivo';
    }

    if (
      formData.motivo === 'atestado_medico' &&
      (!formData.documentos || formData.documentos.length === 0)
    ) {
      newErrors.documentos = 'Anexe o atestado medico';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    try {
      await onSubmit({
        ...formData,
        schedule_id: scheduleInfo?.id || formData.schedule_id,
      });
      onClose();
    } catch (error) {
      console.error('Erro ao enviar solicitacao:', error);
    }
  };

  const getDisponibilidadeColor = (disp: string) => {
    const colors = {
      disponivel: 'bg-green-100 text-green-800',
      parcial: 'bg-yellow-100 text-yellow-800',
      indisponivel: 'bg-red-100 text-red-800',
    };
    return colors[disp as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
            <h2 className="text-xl font-semibold text-gray-900">
              Solicitar Substituicao
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Conteudo scrollavel */}
          <div className="flex-1 overflow-y-auto">
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Info da Escala */}
              {scheduleInfo && (
                <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                  <h3 className="text-sm font-semibold text-blue-800 mb-3">
                    Escala a ser substituida
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center gap-2 text-sm text-blue-700">
                      <MapPin className="w-4 h-4" />
                      {scheduleInfo.posto_nome}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-blue-700">
                      <Calendar className="w-4 h-4" />
                      {new Date(scheduleInfo.data).toLocaleDateString('pt-BR')}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-blue-700">
                      <Clock className="w-4 h-4" />
                      {scheduleInfo.horario_inicio} - {scheduleInfo.horario_fim}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-blue-700">
                      <Info className="w-4 h-4" />
                      {scheduleInfo.turno}
                    </div>
                  </div>
                </div>
              )}

              {/* Urgente */}
              <div className="flex items-center justify-between p-4 bg-amber-50 rounded-xl border border-amber-200">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                  <div>
                    <p className="font-medium text-amber-800">
                      Solicitacao Urgente
                    </p>
                    <p className="text-sm text-amber-600">
                      Marque se a substituicao e para hoje ou amanha
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.urgente}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, urgente: e.target.checked }))
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-amber-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>

              {/* Motivo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Motivo da Substituicao *
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {MOTIVOS.map((motivo) => (
                    <button
                      key={motivo.value}
                      type="button"
                      onClick={() => handleMotivoChange(motivo.value)}
                      className={`p-3 rounded-lg border-2 text-left transition-all ${
                        formData.motivo === motivo.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <p
                        className={`font-medium text-sm ${
                          formData.motivo === motivo.value
                            ? 'text-blue-700'
                            : 'text-gray-700'
                        }`}
                      >
                        {motivo.label}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {motivo.description}
                      </p>
                    </button>
                  ))}
                </div>
                {errors.motivo && (
                  <p className="text-sm text-red-600 mt-1">{errors.motivo}</p>
                )}
              </div>

              {/* Descricao */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descricao {formData.motivo === 'outro' && '*'}
                </label>
                <textarea
                  value={formData.motivo_descricao}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      motivo_descricao: e.target.value,
                    }))
                  }
                  placeholder="Descreva detalhes adicionais sobre o motivo..."
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
                {errors.motivo_descricao && (
                  <p className="text-sm text-red-600 mt-1">
                    {errors.motivo_descricao}
                  </p>
                )}
              </div>

              {/* Upload de Documentos */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Documentos {formData.motivo === 'atestado_medico' && '*'}
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png"
                    multiple
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer flex flex-col items-center"
                  >
                    <Upload className="w-10 h-10 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-600 font-medium">
                      Clique para enviar arquivos
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      PDF, JPG ou PNG ate 5MB
                    </p>
                  </label>
                </div>

                {/* Lista de arquivos */}
                {files.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-700 truncate max-w-[200px]">
                            {file.name}
                          </span>
                          <span className="text-xs text-gray-400">
                            ({(file.size / 1024).toFixed(1)} KB)
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(index)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {errors.documentos && (
                  <p className="text-sm text-red-600 mt-1">{errors.documentos}</p>
                )}
              </div>

              {/* Sugerir Substituto */}
              {availableSubstitutes.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sugerir Substituto (opcional)
                  </label>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {availableSubstitutes.map((sub) => (
                      <button
                        key={sub.id}
                        type="button"
                        onClick={() =>
                          setFormData((prev) => ({
                            ...prev,
                            substituto_id:
                              prev.substituto_id === sub.id ? undefined : sub.id,
                          }))
                        }
                        className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                          formData.substituto_id === sub.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                          {sub.avatar ? (
                            <img
                              src={sub.avatar}
                              alt={sub.nome}
                              className="w-10 h-10 rounded-full object-cover"
                            />
                          ) : (
                            <User className="w-5 h-5 text-gray-500" />
                          )}
                        </div>
                        <div className="flex-1 text-left">
                          <p className="font-medium text-gray-900 text-sm">
                            {sub.nome}
                          </p>
                          <p className="text-xs text-gray-500">{sub.funcao}</p>
                        </div>
                        <div className="text-right">
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${getDisponibilidadeColor(
                              sub.disponibilidade
                            )}`}
                          >
                            {sub.disponibilidade === 'disponivel'
                              ? 'Disponivel'
                              : sub.disponibilidade === 'parcial'
                              ? 'Parcial'
                              : 'Indisponivel'}
                          </span>
                          <p className="text-xs text-gray-400 mt-1">
                            {sub.horas_trabalhadas_semana}h/semana
                          </p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </form>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex gap-3 flex-shrink-0">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancelar
            </button>
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Enviar Solicitacao
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SubstitutionForm;
