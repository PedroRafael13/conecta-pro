import { motion } from 'framer-motion';
import { Play, Edit, Trash2, ToggleLeft, ToggleRight } from 'lucide-react';
import type { AuditRule } from '../types/audit.types';

interface RuleCardProps {
  rule: AuditRule;
  onEdit?: (rule: AuditRule) => void;
  onDelete?: (id: string) => void;
  onToggle?: (id: string) => void;
  onRun?: (id: string) => void;
}

const categoryColors = {
  lgpd: 'bg-purple-100 text-purple-700',
  financeiro: 'bg-green-100 text-green-700',
  operacional: 'bg-blue-100 text-blue-700',
};

const severityColors = {
  alta: 'bg-red-100 text-red-700',
  media: 'bg-yellow-100 text-yellow-700',
  baixa: 'bg-gray-100 text-gray-700',
};

export function RuleCard({ rule, onEdit, onDelete, onToggle, onRun }: RuleCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-xl shadow-card p-5 border-l-4 ${
        rule.status === 'ativa' ? 'border-green-500' : 'border-gray-300'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-semibold text-gray-900">{rule.name}</h4>
            {rule.status === 'inativa' && (
              <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">
                Inativa
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 mb-3">{rule.description}</p>

          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded-full ${categoryColors[rule.category]}`}>
              {rule.category.toUpperCase()}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${severityColors[rule.severity]}`}>
              Severidade: {rule.severity}
            </span>
            <span className="text-xs text-gray-400">
              {rule.conditions.length} condicoes
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => onToggle?.(rule.id)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title={rule.status === 'ativa' ? 'Desativar' : 'Ativar'}
          >
            {rule.status === 'ativa' ? (
              <ToggleRight className="w-5 h-5 text-green-500" />
            ) : (
              <ToggleLeft className="w-5 h-5 text-gray-400" />
            )}
          </button>
          <button
            onClick={() => onRun?.(rule.id)}
            className="p-2 hover:bg-green-100 rounded-lg transition-colors"
            title="Executar"
            disabled={rule.status === 'inativa'}
          >
            <Play className={`w-5 h-5 ${rule.status === 'ativa' ? 'text-green-600' : 'text-gray-300'}`} />
          </button>
          <button
            onClick={() => onEdit?.(rule)}
            className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
            title="Editar"
          >
            <Edit className="w-5 h-5 text-blue-600" />
          </button>
          <button
            onClick={() => onDelete?.(rule.id)}
            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
            title="Excluir"
          >
            <Trash2 className="w-5 h-5 text-red-600" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export default RuleCard;
