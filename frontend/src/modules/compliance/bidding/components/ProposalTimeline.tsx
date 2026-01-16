'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import {
  Search,
  FileText,
  Calculator,
  Send,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Trophy,
  Ban,
  Gavel,
} from 'lucide-react';
import { LucideIcon } from 'lucide-react';

type ProposalStage =
  | 'analysis'
  | 'documentation'
  | 'pricing'
  | 'review'
  | 'submission'
  | 'evaluation'
  | 'adjudication'
  | 'result';

type StageStatus = 'pending' | 'in_progress' | 'completed' | 'blocked' | 'skipped';

interface TimelineStage {
  id: string;
  stage: ProposalStage;
  status: StageStatus;
  title: string;
  description?: string;
  startDate?: Date;
  endDate?: Date;
  assignee?: string;
  blockerReason?: string;
  notes?: string;
}

interface ProposalTimelineProps {
  stages: TimelineStage[];
  currentStage?: ProposalStage;
  result?: 'won' | 'lost' | 'canceled' | 'pending';
  vertical?: boolean;
  compact?: boolean;
  className?: string;
}

const stageConfig: Record<
  ProposalStage,
  { icon: LucideIcon; label: string }
> = {
  analysis: { icon: Search, label: 'Analise' },
  documentation: { icon: FileText, label: 'Documentacao' },
  pricing: { icon: Calculator, label: 'Precificacao' },
  review: { icon: CheckCircle, label: 'Revisao' },
  submission: { icon: Send, label: 'Envio' },
  evaluation: { icon: Clock, label: 'Avaliacao' },
  adjudication: { icon: Gavel, label: 'Adjudicacao' },
  result: { icon: Trophy, label: 'Resultado' },
};

const statusConfig: Record<
  StageStatus,
  { color: string; bgColor: string; borderColor: string }
> = {
  pending: { color: 'text-gray-400', bgColor: 'bg-gray-100', borderColor: 'border-gray-200' },
  in_progress: { color: 'text-blue-600', bgColor: 'bg-blue-100', borderColor: 'border-blue-300' },
  completed: { color: 'text-green-600', bgColor: 'bg-green-100', borderColor: 'border-green-300' },
  blocked: { color: 'text-red-600', bgColor: 'bg-red-100', borderColor: 'border-red-300' },
  skipped: { color: 'text-gray-400', bgColor: 'bg-gray-50', borderColor: 'border-gray-200' },
};

const resultConfig = {
  won: { icon: Trophy, color: 'text-green-600', bgColor: 'bg-green-100', label: 'Vencedor' },
  lost: { icon: Ban, color: 'text-red-600', bgColor: 'bg-red-100', label: 'Nao vencedor' },
  canceled: { icon: XCircle, color: 'text-gray-600', bgColor: 'bg-gray-100', label: 'Cancelado' },
  pending: { icon: Clock, color: 'text-yellow-600', bgColor: 'bg-yellow-100', label: 'Aguardando' },
};

function formatDate(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
  });
}


export function ProposalTimeline({
  stages,
  currentStage,
  result,
  vertical = true,
  compact = false,
  className,
}: ProposalTimelineProps) {
  if (vertical) {
    return (
      <div className={clsx('relative', className)}>
        {/* Timeline line */}
        <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />

        <div className="space-y-4">
          {stages.map((stage, index) => {
            const config = stageConfig[stage.stage];
            const status = statusConfig[stage.status];
            const Icon = config.icon;
            const isCurrent = stage.stage === currentStage;
            const isLast = index === stages.length - 1;

            return (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="relative flex gap-4"
              >
                {/* Icon */}
                <div className="relative z-10 flex-shrink-0">
                  <div
                    className={clsx(
                      'w-10 h-10 rounded-full flex items-center justify-center border-2',
                      status.bgColor,
                      status.borderColor,
                      isCurrent && 'ring-2 ring-offset-2 ring-[#FF6B35]'
                    )}
                  >
                    {stage.status === 'in_progress' ? (
                      <motion.div
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      >
                        <Icon className={clsx('w-5 h-5', status.color)} />
                      </motion.div>
                    ) : stage.status === 'blocked' ? (
                      <AlertTriangle className="w-5 h-5 text-red-500" />
                    ) : stage.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <Icon className={clsx('w-5 h-5', status.color)} />
                    )}
                  </div>
                </div>

                {/* Content */}
                <div className={clsx('flex-1 pb-4', isLast && 'pb-0')}>
                  <div
                    className={clsx(
                      'rounded-lg border p-3',
                      isCurrent ? 'border-[#FF6B35] bg-orange-50/50' : 'border-gray-200 bg-white',
                      stage.status === 'blocked' && 'border-red-200 bg-red-50/50'
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className={clsx('font-medium', isCurrent ? 'text-[#FF6B35]' : 'text-[#0A2540]')}>
                            {stage.title || config.label}
                          </h4>
                          {isCurrent && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-[#FF6B35] text-white rounded-full">
                              Atual
                            </span>
                          )}
                        </div>
                        {stage.description && !compact && (
                          <p className="text-sm text-gray-600 mt-1">{stage.description}</p>
                        )}
                      </div>

                      {/* Status indicator */}
                      <span
                        className={clsx(
                          'px-2 py-0.5 text-xs font-medium rounded-full',
                          status.bgColor,
                          status.color
                        )}
                      >
                        {stage.status === 'pending' && 'Pendente'}
                        {stage.status === 'in_progress' && 'Em andamento'}
                        {stage.status === 'completed' && 'Concluido'}
                        {stage.status === 'blocked' && 'Bloqueado'}
                        {stage.status === 'skipped' && 'Pulado'}
                      </span>
                    </div>

                    {/* Dates and Assignee */}
                    {!compact && (stage.startDate || stage.assignee) && (
                      <div className="flex items-center gap-4 mt-2 pt-2 border-t border-gray-100">
                        {stage.startDate && (
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <Clock className="w-3 h-3" />
                            <span>
                              {formatDate(stage.startDate)}
                              {stage.endDate && ` - ${formatDate(stage.endDate)}`}
                            </span>
                          </div>
                        )}
                        {stage.assignee && (
                          <span className="text-xs text-gray-500">
                            Resp: {stage.assignee}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Blocker */}
                    {stage.status === 'blocked' && stage.blockerReason && (
                      <div className="mt-2 p-2 bg-red-100 rounded text-xs text-red-700">
                        <strong>Bloqueio:</strong> {stage.blockerReason}
                      </div>
                    )}

                    {/* Notes */}
                    {!compact && stage.notes && (
                      <p className="mt-2 text-xs text-gray-500 italic">{stage.notes}</p>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}

          {/* Result */}
          {result && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: stages.length * 0.1, duration: 0.3 }}
              className="relative flex gap-4"
            >
              <div className="relative z-10 flex-shrink-0">
                <div
                  className={clsx(
                    'w-10 h-10 rounded-full flex items-center justify-center',
                    resultConfig[result].bgColor
                  )}
                >
                  {(() => {
                    const ResultIcon = resultConfig[result].icon;
                    return <ResultIcon className={clsx('w-5 h-5', resultConfig[result].color)} />;
                  })()}
                </div>
              </div>
              <div className="flex-1">
                <div
                  className={clsx(
                    'rounded-lg border p-4',
                    result === 'won' && 'border-green-300 bg-green-50',
                    result === 'lost' && 'border-red-300 bg-red-50',
                    result === 'canceled' && 'border-gray-300 bg-gray-50',
                    result === 'pending' && 'border-yellow-300 bg-yellow-50'
                  )}
                >
                  <h4 className={clsx('font-semibold text-lg', resultConfig[result].color)}>
                    {resultConfig[result].label}
                  </h4>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    );
  }

  // Horizontal timeline
  return (
    <div className={clsx('relative', className)}>
      <div className="flex items-center justify-between">
        {stages.map((stage, index) => {
          const config = stageConfig[stage.stage];
          const status = statusConfig[stage.status];
          const Icon = config.icon;
          const isCurrent = stage.stage === currentStage;
          const isLast = index === stages.length - 1;

          return (
            <div key={stage.id} className="flex items-center flex-1">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex flex-col items-center"
              >
                <div
                  className={clsx(
                    'w-10 h-10 rounded-full flex items-center justify-center border-2',
                    status.bgColor,
                    status.borderColor,
                    isCurrent && 'ring-2 ring-offset-2 ring-[#FF6B35]'
                  )}
                >
                  {stage.status === 'completed' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <Icon className={clsx('w-5 h-5', status.color)} />
                  )}
                </div>
                <span
                  className={clsx(
                    'mt-2 text-xs font-medium text-center',
                    isCurrent ? 'text-[#FF6B35]' : 'text-gray-600'
                  )}
                >
                  {config.label}
                </span>
              </motion.div>

              {/* Connector line */}
              {!isLast && (
                <div className="flex-1 h-0.5 bg-gray-200 mx-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{
                      width: stage.status === 'completed' ? '100%' : '0%',
                    }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="h-full bg-green-500"
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
