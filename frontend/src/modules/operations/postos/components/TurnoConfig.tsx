import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  Plus,
  Edit,
  Trash2,
  Users,
  Sun,
  Moon,
  Calendar,
  Save,
  X,
  AlertCircle,
  Coffee,
} from 'lucide-react';
import type { Turno, TurnoFormData, TipoTurno } from '../types/postos.types';

interface TurnoConfigProps {
  turnos: Turno[];
  onAddTurno?: (data: TurnoFormData) => Promise<void>;
  onUpdateTurno?: (id: string, data: Partial<TurnoFormData>) => Promise<void>;
  onDeleteTurno?: (id: string) => Promise<void>;
  readOnly?: boolean;
}

const DIAS_SEMANA = [
  { id: 0, nome: 'Dom', abrev: 'D' },
  { id: 1, nome: 'Seg', abrev: 'S' },
  { id: 2, nome: 'Ter', abrev: 'T' },
  { id: 3, nome: 'Qua', abrev: 'Q' },
  { id: 4, nome: 'Qui', abrev: 'Q' },
  { id: 5, nome: 'Sex', abrev: 'S' },
  { id: 6, nome: 'Sab', abrev: 'S' },
];

const TIPOS_TURNO: { value: TipoTurno; label: string; icon: React.ElementType }[] = [
  { value: 'diurno', label: 'Diurno', icon: Sun },
  { value: 'noturno', label: 'Noturno', icon: Moon },
  { value: 'misto', label: 'Misto', icon: Clock },
  { value: '12x36', label: '12x36', icon: Calendar },
  { value: '24h', label: '24 Horas', icon: Clock },
];

const initialFormData: TurnoFormData = {
  nome: '',
  horario_inicio: '08:00',
  horario_fim: '16:00',
  dias_semana: [1, 2, 3, 4, 5],
  profissionais_necessarios: 1,
  tipo: 'diurno',
  adicional_noturno: false,
  intervalo_minutos: 60,
};

export const TurnoConfig: React.FC<TurnoConfigProps> = ({
  turnos,
  onAddTurno,
  onUpdateTurno,
  onDeleteTurno,
  readOnly = false,
}) => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTurno, setEditingTurno] = useState<Turno | null>(null);
  const [formData, setFormData] = useState<TurnoFormData>(initialFormData);
  const [loading, setLoading] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const getTipoConfig = (tipo: TipoTurno) => {
    const config = TIPOS_TURNO.find((t) => t.value === tipo);
    return config || TIPOS_TURNO[0];
  };

  const formatDiasSemana = (dias: number[]) => {
    if (dias.length === 7) return 'Todos os dias';
    if (dias.length === 5 && !dias.includes(0) && !dias.includes(6)) {
      return 'Seg a Sex';
    }
    if (dias.length === 2 && dias.includes(0) && dias.includes(6)) {
      return 'Fim de semana';
    }
    return dias.map((d) => DIAS_SEMANA[d].abrev).join(', ');
  };

  const handleOpenForm = (turno?: Turno) => {
    if (turno) {
      setEditingTurno(turno);
      setFormData({
        nome: turno.nome,
        horario_inicio: turno.horario_inicio,
        horario_fim: turno.horario_fim,
        dias_semana: turno.dias_semana,
        profissionais_necessarios: turno.profissionais_necessarios,
        tipo: turno.tipo,
        adicional_noturno: turno.adicional_noturno,
        intervalo_minutos: turno.intervalo_minutos,
      });
    } else {
      setEditingTurno(null);
      setFormData(initialFormData);
    }
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingTurno(null);
    setFormData(initialFormData);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (editingTurno) {
        await onUpdateTurno?.(editingTurno.id, formData);
      } else {
        await onAddTurno?.(formData);
      }
      handleCloseForm();
    } catch (error) {
      console.error('Erro ao salvar turno:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    setLoading(true);
    try {
      await onDeleteTurno?.(id);
      setDeleteConfirm(null);
    } catch (error) {
      console.error('Erro ao deletar turno:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDiaSemana = (dia: number) => {
    setFormData((prev) => ({
      ...prev,
      dias_semana: prev.dias_semana.includes(dia)
        ? prev.dias_semana.filter((d) => d !== dia)
        : [...prev.dias_semana, dia].sort(),
    }));
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-600" />
          Configuracao de Turnos
        </h3>
        {!readOnly && (
          <button
            onClick={() => handleOpenForm()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            Novo Turno
          </button>
        )}
      </div>

      {/* Lista de Turnos */}
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {turnos.map((turno) => {
            const tipoConfig = getTipoConfig(turno.tipo);
            const TipoIcon = tipoConfig.icon;
            const ocupacao =
              turno.profissionais_necessarios > 0
                ? (turno.profissionais_alocados / turno.profissionais_necessarios) * 100
                : 0;

            return (
              <motion.div
                key={turno.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div
                        className={`p-2 rounded-lg ${
                          turno.tipo === 'noturno'
                            ? 'bg-indigo-100 text-indigo-600'
                            : turno.tipo === 'diurno'
                            ? 'bg-yellow-100 text-yellow-600'
                            : 'bg-blue-100 text-blue-600'
                        }`}
                      >
                        <TipoIcon className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{turno.nome}</h4>
                        <p className="text-sm text-gray-500">{tipoConfig.label}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                      {/* Horario */}
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span>
                          {turno.horario_inicio} - {turno.horario_fim}
                        </span>
                      </div>

                      {/* Dias */}
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <span>{formatDiasSemana(turno.dias_semana)}</span>
                      </div>

                      {/* Profissionais */}
                      <div className="flex items-center gap-2 text-sm">
                        <Users className="w-4 h-4 text-gray-400" />
                        <span
                          className={
                            ocupacao >= 100 ? 'text-green-600' : 'text-orange-600'
                          }
                        >
                          {turno.profissionais_alocados}/
                          {turno.profissionais_necessarios}
                        </span>
                      </div>

                      {/* Intervalo */}
                      {turno.intervalo_minutos && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Coffee className="w-4 h-4 text-gray-400" />
                          <span>{turno.intervalo_minutos} min</span>
                        </div>
                      )}
                    </div>

                    {/* Adicional noturno */}
                    {turno.adicional_noturno && (
                      <div className="mt-2 inline-flex items-center gap-1 px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded-full">
                        <Moon className="w-3 h-3" />
                        Adicional noturno
                      </div>
                    )}
                  </div>

                  {/* Acoes */}
                  {!readOnly && (
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => handleOpenForm(turno)}
                        className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Editar"
                      >
                        <Edit className="w-4 h-4" />
                      </button>

                      {deleteConfirm === turno.id ? (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleDelete(turno.id)}
                            disabled={loading}
                            className="p-2 text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                            title="Confirmar"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                            title="Cancelar"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(turno.id)}
                          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Excluir"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  )}
                </div>

                {/* Barra de ocupacao */}
                <div className="mt-3">
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all ${
                        ocupacao >= 100
                          ? 'bg-green-500'
                          : ocupacao >= 50
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(ocupacao, 100)}%` }}
                    />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {turnos.length === 0 && (
          <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
            <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <h4 className="text-gray-600 font-medium mb-1">Nenhum turno configurado</h4>
            <p className="text-sm text-gray-400">
              Adicione turnos para configurar a escala do posto
            </p>
          </div>
        )}
      </div>

      {/* Modal de Formulario */}
      <AnimatePresence>
        {isFormOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            onClick={handleCloseForm}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header do Modal */}
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  {editingTurno ? 'Editar Turno' : 'Novo Turno'}
                </h3>
                <button
                  onClick={handleCloseForm}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Formulario */}
              <form onSubmit={handleSubmit} className="p-6 space-y-5">
                {/* Nome */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nome do Turno
                  </label>
                  <input
                    type="text"
                    value={formData.nome}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, nome: e.target.value }))
                    }
                    placeholder="Ex: Turno A - Manha"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                {/* Tipo de Turno */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Turno
                  </label>
                  <div className="grid grid-cols-5 gap-2">
                    {TIPOS_TURNO.map((tipo) => {
                      const Icon = tipo.icon;
                      return (
                        <button
                          key={tipo.value}
                          type="button"
                          onClick={() =>
                            setFormData((prev) => ({ ...prev, tipo: tipo.value }))
                          }
                          className={`flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-all ${
                            formData.tipo === tipo.value
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-gray-300 text-gray-600'
                          }`}
                        >
                          <Icon className="w-5 h-5" />
                          <span className="text-xs font-medium">{tipo.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Horarios */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Inicio
                    </label>
                    <input
                      type="time"
                      value={formData.horario_inicio}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          horario_inicio: e.target.value,
                        }))
                      }
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fim
                    </label>
                    <input
                      type="time"
                      value={formData.horario_fim}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          horario_fim: e.target.value,
                        }))
                      }
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                </div>

                {/* Dias da Semana */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dias da Semana
                  </label>
                  <div className="flex gap-2">
                    {DIAS_SEMANA.map((dia) => (
                      <button
                        key={dia.id}
                        type="button"
                        onClick={() => toggleDiaSemana(dia.id)}
                        className={`w-10 h-10 rounded-full font-medium text-sm transition-all ${
                          formData.dias_semana.includes(dia.id)
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        {dia.abrev}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Profissionais e Intervalo */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Profissionais Necessarios
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={formData.profissionais_necessarios}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          profissionais_necessarios: parseInt(e.target.value) || 1,
                        }))
                      }
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Intervalo (minutos)
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="15"
                      value={formData.intervalo_minutos || ''}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          intervalo_minutos: parseInt(e.target.value) || undefined,
                        }))
                      }
                      placeholder="60"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                {/* Adicional Noturno */}
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Moon className="w-5 h-5 text-purple-600" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        Adicional Noturno
                      </p>
                      <p className="text-xs text-gray-500">
                        Turno entre 22h e 5h
                      </p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.adicional_noturno}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          adicional_noturno: e.target.checked,
                        }))
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {/* Alerta */}
                {formData.dias_semana.length === 0 && (
                  <div className="flex items-center gap-2 p-3 bg-yellow-50 text-yellow-800 rounded-lg text-sm">
                    <AlertCircle className="w-4 h-4" />
                    Selecione pelo menos um dia da semana
                  </div>
                )}

                {/* Botoes */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseForm}
                    className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={loading || formData.dias_semana.length === 0}
                    className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        {editingTurno ? 'Salvar' : 'Criar Turno'}
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TurnoConfig;
