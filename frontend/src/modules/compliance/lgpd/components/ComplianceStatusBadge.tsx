'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Shield,
  ShieldCheck,
  ShieldX,
  ShieldAlert,
} from 'lucide-react';
import { LucideIcon } from 'lucide-react';

export type ConsentStatus = 'active' | 'pending' | 'revoked' | 'expired';
export type ComplianceLevel = 'compliant' | 'partial' | 'non_compliant' | 'under_review';
export type RequestStatus = 'open' | 'in_progress' | 'completed' | 'overdue' | 'rejected';

type BadgeType = 'consent' | 'compliance' | 'request';
type BadgeSize = 'xs' | 'sm' | 'md' | 'lg';

interface ComplianceStatusBadgeProps {
  status: ConsentStatus | ComplianceLevel | RequestStatus;
  type?: BadgeType;
  size?: BadgeSize;
  showIcon?: boolean;
  showLabel?: boolean;
  animate?: boolean;
  className?: string;
}

type StatusConfig = {
  label: string;
  icon: LucideIcon;
  color: string;
  bgColor: string;
  borderColor: string;
};

const consentStatusConfig: Record<ConsentStatus, StatusConfig> = {
  active: {
    label: 'Ativo',
    icon: CheckCircle,
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    borderColor: 'border-green-200',
  },
  pending: {
    label: 'Pendente',
    icon: Clock,
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    borderColor: 'border-yellow-200',
  },
  revoked: {
    label: 'Revogado',
    icon: XCircle,
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-200',
  },
  expired: {
    label: 'Expirado',
    icon: AlertTriangle,
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-200',
  },
};

const complianceStatusConfig: Record<ComplianceLevel, StatusConfig> = {
  compliant: {
    label: 'Conforme',
    icon: ShieldCheck,
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    borderColor: 'border-green-200',
  },
  partial: {
    label: 'Parcial',
    icon: ShieldAlert,
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    borderColor: 'border-yellow-200',
  },
  non_compliant: {
    label: 'Nao Conforme',
    icon: ShieldX,
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-200',
  },
  under_review: {
    label: 'Em Analise',
    icon: Shield,
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-200',
  },
};

const requestStatusConfig: Record<RequestStatus, StatusConfig> = {
  open: {
    label: 'Aberto',
    icon: Clock,
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-200',
  },
  in_progress: {
    label: 'Em Andamento',
    icon: Clock,
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    borderColor: 'border-yellow-200',
  },
  completed: {
    label: 'Concluido',
    icon: CheckCircle,
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    borderColor: 'border-green-200',
  },
  overdue: {
    label: 'Atrasado',
    icon: AlertTriangle,
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-200',
  },
  rejected: {
    label: 'Rejeitado',
    icon: XCircle,
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-200',
  },
};

const sizeStyles: Record<BadgeSize, { container: string; icon: string; text: string }> = {
  xs: { container: 'px-1.5 py-0.5 gap-1', icon: 'w-3 h-3', text: 'text-xs' },
  sm: { container: 'px-2 py-1 gap-1.5', icon: 'w-3.5 h-3.5', text: 'text-xs' },
  md: { container: 'px-2.5 py-1.5 gap-1.5', icon: 'w-4 h-4', text: 'text-sm' },
  lg: { container: 'px-3 py-2 gap-2', icon: 'w-5 h-5', text: 'text-base' },
};

function getConfig(
  status: ConsentStatus | ComplianceLevel | RequestStatus,
  type: BadgeType
): StatusConfig {
  switch (type) {
    case 'consent':
      return consentStatusConfig[status as ConsentStatus];
    case 'compliance':
      return complianceStatusConfig[status as ComplianceLevel];
    case 'request':
      return requestStatusConfig[status as RequestStatus];
    default:
      return consentStatusConfig[status as ConsentStatus];
  }
}

export function ComplianceStatusBadge({
  status,
  type = 'consent',
  size = 'sm',
  showIcon = true,
  showLabel = true,
  animate = false,
  className,
}: ComplianceStatusBadgeProps) {
  const config = getConfig(status, type);
  const sizeConfig = sizeStyles[size];
  const Icon = config.icon;

  const isWarning =
    status === 'pending' ||
    status === 'partial' ||
    status === 'in_progress' ||
    status === 'overdue';

  return (
    <motion.span
      initial={animate ? { scale: 0.8, opacity: 0 } : false}
      animate={animate ? { scale: 1, opacity: 1 } : false}
      className={clsx(
        'inline-flex items-center rounded-full border font-medium',
        config.bgColor,
        config.borderColor,
        config.color,
        sizeConfig.container,
        className
      )}
    >
      {showIcon && (
        <span className="flex-shrink-0">
          {isWarning && animate ? (
            <motion.div
              animate={{ rotate: [0, -10, 10, -10, 0] }}
              transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 3 }}
            >
              <Icon className={sizeConfig.icon} />
            </motion.div>
          ) : (
            <Icon className={sizeConfig.icon} />
          )}
        </span>
      )}
      {showLabel && <span className={sizeConfig.text}>{config.label}</span>}
    </motion.span>
  );
}
