import React from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  UserCheck,
  Search,
  CheckCircle,
  Flag,
  Clock,
  ArrowRight,
  X,
  User,
  Calendar,
} from 'lucide-react';
import type { WorkflowStep, Substitution } from '../types/substitutions.types';

interface ApprovalWorkflowProps {
  substitution: Substitution;
  steps: WorkflowStep[];
  variant?: 'horizontal' | 'vertical';
  showDetails?: boolean;
}

const ICONS: Record<string, React.ElementType> = {
  FileText,
  UserCheck,
  Search,
  CheckCircle,
  Flag,
  Clock,
};

export const ApprovalWorkflow: React.FC<ApprovalWorkflowProps> = ({
  substitution,
  steps,
  variant = 'horizontal',
  showDetails = true,
}) => {
  const getStepConfig = (status: string) => {
    const configs = {
      pendente: {
        color: 'bg-gray-200 text-gray-400',
        lineColor: 'bg-gray-200',
        iconBg: 'bg-gray-100',
      },
      atual: {
        color: 'bg-blue-500 text-white',
        lineColor: 'bg-blue-500',
        iconBg: 'bg-blue-100',
      },
      concluido: {
        color: 'bg-green-500 text-white',
        lineColor: 'bg-green-500',
        iconBg: 'bg-green-100',
      },
      pulado: {
        color: 'bg-gray-300 text-gray-500',
        lineColor: 'bg-gray-300',
        iconBg: 'bg-gray-100',
      },
    };
    return configs[status as keyof typeof configs] || configs.pendente;
  };

  // Versao Horizontal
  if (variant === 'horizontal') {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          Fluxo de Aprovacao
        </h3>

        {/* Timeline Horizontal */}
        <div className="relative">
          {/* Linha de conexao */}
          <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200" />

          {/* Steps */}
          <div className="relative flex justify-between">
            {steps.map((step, index) => {
              const config = getStepConfig(step.status);
              const Icon = ICONS[step.icone] || CheckCircle;
              const isLast = index === steps.length - 1;

              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex flex-col items-center relative"
                  style={{ width: `${100 / steps.length}%` }}
                >
                  {/* Linha de progresso */}
                  {!isLast && (
                    <div
                      className={`absolute top-5 left-1/2 w-full h-0.5 ${
                        step.status === 'concluido' ? config.lineColor : 'bg-gray-200'
                      }`}
                    />
                  )}

                  {/* Icone */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center z-10 ${config.color} ${
                      step.status === 'atual' ? 'ring-4 ring-blue-200' : ''
                    }`}
                  >
                    {step.status === 'concluido' ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : step.status === 'pulado' ? (
                      <X className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>

                  {/* Label */}
                  <div className="mt-3 text-center">
                    <p
                      className={`text-sm font-medium ${
                        step.status === 'atual'
                          ? 'text-blue-600'
                          : step.status === 'concluido'
                          ? 'text-green-600'
                          : 'text-gray-500'
                      }`}
                    >
                      {step.titulo}
                    </p>

                    {showDetails && (
                      <>
                        <p className="text-xs text-gray-400 mt-1 max-w-[120px] mx-auto">
                          {step.descricao}
                        </p>

                        {step.responsavel && (
                          <p className="text-xs text-gray-500 mt-1">
                            {step.responsavel}
                          </p>
                        )}

                        {step.data_conclusao && (
                          <p className="text-xs text-gray-400 mt-0.5">
                            {new Date(step.data_conclusao).toLocaleString('pt-BR', {
                              day: '2-digit',
                              month: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </p>
                        )}
                      </>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Informacoes adicionais */}
        {showDetails && (
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <User className="w-4 h-4" />
                  <span className="text-sm font-medium">Solicitante</span>
                </div>
                <p className="text-gray-900 font-medium">
                  {substitution.solicitante_nome}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Calendar className="w-4 h-4" />
                  <span className="text-sm font-medium">Data da Escala</span>
                </div>
                <p className="text-gray-900 font-medium">
                  {new Date(substitution.data).toLocaleDateString('pt-BR')}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm font-medium">Tempo Decorrido</span>
                </div>
                <p className="text-gray-900 font-medium">
                  {Math.round(
                    (new Date().getTime() - new Date(substitution.created_at).getTime()) /
                      (1000 * 60 * 60)
                  )}
                  h
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Versao Vertical
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        Fluxo de Aprovacao
      </h3>

      {/* Timeline Vertical */}
      <div className="relative">
        {steps.map((step, index) => {
          const config = getStepConfig(step.status);
          const Icon = ICONS[step.icone] || CheckCircle;
          const isLast = index === steps.length - 1;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative flex gap-4 pb-8 last:pb-0"
            >
              {/* Linha de conexao */}
              {!isLast && (
                <div
                  className={`absolute left-5 top-10 w-0.5 h-full -ml-px ${
                    step.status === 'concluido' ? config.lineColor : 'bg-gray-200'
                  }`}
                />
              )}

              {/* Icone */}
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 z-10 ${
                  config.color
                } ${step.status === 'atual' ? 'ring-4 ring-blue-200' : ''}`}
              >
                {step.status === 'concluido' ? (
                  <CheckCircle className="w-5 h-5" />
                ) : step.status === 'pulado' ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Icon className="w-5 h-5" />
                )}
              </div>

              {/* Conteudo */}
              <div className="flex-1 pt-1">
                <div className="flex items-start justify-between">
                  <div>
                    <h4
                      className={`font-medium ${
                        step.status === 'atual'
                          ? 'text-blue-600'
                          : step.status === 'concluido'
                          ? 'text-green-600'
                          : step.status === 'pulado'
                          ? 'text-gray-400 line-through'
                          : 'text-gray-500'
                      }`}
                    >
                      {step.titulo}
                    </h4>
                    <p className="text-sm text-gray-500 mt-0.5">{step.descricao}</p>
                  </div>

                  {step.data_conclusao && (
                    <span className="text-xs text-gray-400">
                      {new Date(step.data_conclusao).toLocaleString('pt-BR', {
                        day: '2-digit',
                        month: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  )}
                </div>

                {step.responsavel && (
                  <div className="flex items-center gap-1 mt-2 text-sm text-gray-600">
                    <User className="w-3.5 h-3.5" />
                    <span>{step.responsavel}</span>
                  </div>
                )}

                {/* Badge de status atual */}
                {step.status === 'atual' && (
                  <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                    <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                    Em andamento
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Legenda */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center gap-6 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-600">Concluido</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-gray-600">Em andamento</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-gray-300" />
            <span className="text-gray-600">Pendente</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Componente de resumo do workflow
interface WorkflowSummaryProps {
  substitution: Substitution;
  currentStep: number;
  totalSteps: number;
}

export const WorkflowSummary: React.FC<WorkflowSummaryProps> = ({
  substitution,
  currentStep,
  totalSteps,
}) => {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-medium">Progresso da Solicitacao</h4>
        <span className="text-sm text-blue-100">
          {currentStep} de {totalSteps} etapas
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-blue-400/50 rounded-full h-2 mb-3">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-full h-2"
        />
      </div>

      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2 text-blue-100">
          <Clock className="w-4 h-4" />
          <span>
            Iniciado em{' '}
            {new Date(substitution.created_at).toLocaleDateString('pt-BR')}
          </span>
        </div>
        <div className="flex items-center gap-1 text-blue-100">
          <span>Proxima etapa</span>
          <ArrowRight className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
};

export default ApprovalWorkflow;
