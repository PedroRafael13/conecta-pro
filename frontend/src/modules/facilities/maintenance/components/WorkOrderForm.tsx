'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Wrench,
  Calendar,
  User,
  Clock,
  DollarSign,
  FileText,
  Plus,
  X,
  Save,
  ChevronDown
} from 'lucide-react';
import type {
  CreateMaintenanceOrderDTO,
  MaintenanceType,
  MaintenancePriority,
  Technician
} from '../types/maintenance.types';
import type { Equipment } from '../../equipment/types/equipment.types';

interface WorkOrderFormProps {
  equipments: Equipment[];
  technicians: Technician[];
  onSubmit: (data: CreateMaintenanceOrderDTO) => Promise<void>;
  onCancel: () => void;
  initialData?: Partial<CreateMaintenanceOrderDTO>;
  isLoading?: boolean;
}

export function WorkOrderForm({
  equipments,
  technicians,
  onSubmit,
  onCancel,
  initialData,
  isLoading = false
}: WorkOrderFormProps) {
  const [formData, setFormData] = useState<CreateMaintenanceOrderDTO>({
    equipment_id: initialData?.equipment_id || '',
    tipo: initialData?.tipo || 'preventiva',
    prioridade: initialData?.prioridade || 'normal',
    descricao: initialData?.descricao || '',
    data_agendada: initialData?.data_agendada || new Date().toISOString().split('T')[0],
    tecnico_id: initialData?.tecnico_id,
    tempo_estimado_horas: initialData?.tempo_estimado_horas,
    custo_estimado: initialData?.custo_estimado,
    checklist: initialData?.checklist || []
  });

  const [checklistItem, setChecklistItem] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: keyof CreateMaintenanceOrderDTO, value: CreateMaintenanceOrderDTO[keyof CreateMaintenanceOrderDTO]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const addChecklistItem = () => {
    if (checklistItem.trim()) {
      handleChange('checklist', [...(formData.checklist || []), checklistItem.trim()]);
      setChecklistItem('');
    }
  };

  const removeChecklistItem = (index: number) => {
    handleChange(
      'checklist',
      formData.checklist?.filter((_, i) => i !== index)
    );
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.equipment_id) {
      newErrors.equipment_id = 'Selecione um equipamento';
    }
    if (!formData.descricao.trim()) {
      newErrors.descricao = 'Descricao e obrigatoria';
    }
    if (!formData.data_agendada) {
      newErrors.data_agendada = 'Data e obrigatoria';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    try {
      await onSubmit(formData);
    } catch (err) {
      console.error('Erro ao criar ordem:', err);
    }
  };

  const tipoOptions: Array<{ value: MaintenanceType; label: string }> = [
    { value: 'preventiva', label: 'Preventiva' },
    { value: 'corretiva', label: 'Corretiva' },
    { value: 'preditiva', label: 'Preditiva' }
  ];

  const prioridadeOptions: Array<{ value: MaintenancePriority; label: string }> = [
    { value: 'urgente', label: 'Urgente' },
    { value: 'alta', label: 'Alta' },
    { value: 'normal', label: 'Normal' },
    { value: 'baixa', label: 'Baixa' }
  ];

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Wrench className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Nova Ordem de Manutencao</h2>
            <p className="text-sm text-gray-500">Preencha os dados da ordem de servico</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onCancel}
          className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Form Content */}
      <div className="p-6 space-y-6">
        {/* Equipment Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Equipamento *
          </label>
          <div className="relative">
            <select
              value={formData.equipment_id}
              onChange={(e) => handleChange('equipment_id', e.target.value)}
              className={`w-full px-3 py-2.5 border rounded-lg appearance-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.equipment_id ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Selecione um equipamento</option>
              {equipments.map(eq => (
                <option key={eq.id} value={eq.id}>
                  {eq.codigo} - {eq.nome}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
          {errors.equipment_id && (
            <p className="mt-1 text-sm text-red-600">{errors.equipment_id}</p>
          )}
        </div>

        {/* Type and Priority */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Tipo de Manutencao
            </label>
            <div className="flex space-x-2">
              {tipoOptions.map(option => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleChange('tipo', option.value)}
                  className={`flex-1 px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
                    formData.tipo === option.value
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Prioridade
            </label>
            <div className="flex space-x-2">
              {prioridadeOptions.map(option => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleChange('prioridade', option.value)}
                  className={`flex-1 px-2 py-2 text-xs font-medium rounded-lg border transition-colors ${
                    formData.prioridade === option.value
                      ? option.value === 'urgente' ? 'bg-red-50 border-red-500 text-red-700' :
                        option.value === 'alta' ? 'bg-orange-50 border-orange-500 text-orange-700' :
                        option.value === 'normal' ? 'bg-blue-50 border-blue-500 text-blue-700' :
                        'bg-gray-50 border-gray-500 text-gray-700'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Descricao *
          </label>
          <textarea
            value={formData.descricao}
            onChange={(e) => handleChange('descricao', e.target.value)}
            rows={3}
            placeholder="Descreva o servico a ser realizado..."
            className={`w-full px-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none ${
              errors.descricao ? 'border-red-300' : 'border-gray-300'
            }`}
          />
          {errors.descricao && (
            <p className="mt-1 text-sm text-red-600">{errors.descricao}</p>
          )}
        </div>

        {/* Date and Technician */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              <Calendar className="w-4 h-4 inline mr-1" />
              Data Agendada *
            </label>
            <input
              type="date"
              value={formData.data_agendada}
              onChange={(e) => handleChange('data_agendada', e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className={`w-full px-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.data_agendada ? 'border-red-300' : 'border-gray-300'
              }`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              <User className="w-4 h-4 inline mr-1" />
              Tecnico Responsavel
            </label>
            <div className="relative">
              <select
                value={formData.tecnico_id || ''}
                onChange={(e) => handleChange('tecnico_id', e.target.value || undefined)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg appearance-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Selecione (opcional)</option>
                {technicians.filter(t => t.disponivel).map(tech => (
                  <option key={tech.id} value={tech.id}>
                    {tech.nome} ({tech.ordens_ativas} ordens ativas)
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Time and Cost Estimates */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              <Clock className="w-4 h-4 inline mr-1" />
              Tempo Estimado (horas)
            </label>
            <input
              type="number"
              value={formData.tempo_estimado_horas || ''}
              onChange={(e) => handleChange('tempo_estimado_horas', e.target.value ? parseFloat(e.target.value) : undefined)}
              min="0"
              step="0.5"
              placeholder="Ex: 2.5"
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              <DollarSign className="w-4 h-4 inline mr-1" />
              Custo Estimado (R$)
            </label>
            <input
              type="number"
              value={formData.custo_estimado || ''}
              onChange={(e) => handleChange('custo_estimado', e.target.value ? parseFloat(e.target.value) : undefined)}
              min="0"
              step="0.01"
              placeholder="Ex: 500.00"
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Checklist */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            <FileText className="w-4 h-4 inline mr-1" />
            Checklist de Atividades
          </label>

          {/* Add item input */}
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={checklistItem}
              onChange={(e) => setChecklistItem(e.target.value)}
              placeholder="Adicionar item ao checklist..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addChecklistItem();
                }
              }}
            />
            <button
              type="button"
              onClick={addChecklistItem}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Plus className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Checklist items */}
          {formData.checklist && formData.checklist.length > 0 && (
            <div className="space-y-2 bg-gray-50 rounded-lg p-3">
              {formData.checklist.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-2 bg-white rounded border border-gray-200"
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-700">{index + 1}.</span>
                    <span className="text-sm text-gray-700">{item}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeChecklistItem(index)}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                  >
                    <X className="w-4 h-4 text-gray-400" />
                  </button>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-end space-x-3 p-4 border-t border-gray-200 bg-gray-50">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="flex items-center space-x-2 px-6 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 rounded-lg transition-colors"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Criando...</span>
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>Criar Ordem</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}

export default WorkOrderForm;
