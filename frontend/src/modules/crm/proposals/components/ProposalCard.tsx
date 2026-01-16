'use client';

import { motion } from 'framer-motion';
import {
  FileText,
  Calendar,
  DollarSign,
  User,
  MoreVertical,
  Edit,
  Copy,
  Send,
  Trash2,
  Eye
} from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/core/components/ui/Badge';
import { Button } from '@/core/components/ui/Button';
import type { Proposal } from '../../types';

interface ProposalCardProps {
  proposal: Proposal;
  onEdit?: (id: string) => void;
  onDuplicate?: (id: string) => void;
  onSend?: (id: string) => void;
  onDelete?: (id: string) => void;
  onView?: (id: string) => void;
}

const statusConfig: Record<Proposal['status'], { label: string; variant: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info' }> = {
  draft: { label: 'Rascunho', variant: 'default' },
  sent: { label: 'Enviada', variant: 'info' },
  viewed: { label: 'Visualizada', variant: 'primary' },
  accepted: { label: 'Aceita', variant: 'success' },
  rejected: { label: 'Rejeitada', variant: 'danger' },
  expired: { label: 'Expirada', variant: 'warning' },
};

export function ProposalCard({
  proposal,
  onEdit,
  onDuplicate,
  onSend,
  onDelete,
  onView,
}: ProposalCardProps) {
  const [showMenu, setShowMenu] = useState(false);
  const statusInfo = statusConfig[proposal.status];

  const formatCurrency = (value: number, currency: 'BRL' | 'USD') => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className="bg-white rounded-lg shadow-card border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-conecta-escuro/10 rounded-lg">
              <FileText className="w-5 h-5 text-conecta-escuro" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 line-clamp-1">
                {proposal.title}
              </h3>
              <p className="text-sm text-gray-500">v{proposal.version}</p>
            </div>
          </div>
          <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <User className="w-4 h-4" />
          <span>Cliente #{proposal.contactId.slice(0, 8)}</span>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <DollarSign className="w-4 h-4" />
          <span className="font-semibold text-conecta-escuro">
            {formatCurrency(proposal.total, proposal.currency)}
          </span>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="w-4 h-4" />
          <span>Valida ate {formatDate(proposal.validUntil)}</span>
        </div>

        {proposal.sentAt && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Send className="w-4 h-4" />
            <span>Enviada em {formatDate(proposal.sentAt)}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onView?.(proposal.id)}
              leftIcon={<Eye className="w-4 h-4" />}
            >
              Ver
            </Button>
            {proposal.status === 'draft' && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit?.(proposal.id)}
                leftIcon={<Edit className="w-4 h-4" />}
              >
                Editar
              </Button>
            )}
          </div>

          {/* Dropdown Menu */}
          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowMenu(!showMenu)}
            >
              <MoreVertical className="w-4 h-4" />
            </Button>

            {showMenu && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="absolute right-0 bottom-full mb-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10"
              >
                <button
                  onClick={() => {
                    onDuplicate?.(proposal.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <Copy className="w-4 h-4" />
                  Duplicar
                </button>
                {proposal.status === 'draft' && (
                  <button
                    onClick={() => {
                      onSend?.(proposal.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Enviar
                  </button>
                )}
                <button
                  onClick={() => {
                    onDelete?.(proposal.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Excluir
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Mock data para demonstracao
// eslint-disable-next-line react-refresh/only-export-components
export const mockProposals: Proposal[] = [
  {
    id: '1',
    contactId: 'contact-001',
    title: 'Proposta Manutencao Predial 2024',
    status: 'sent',
    sections: [],
    total: 45000,
    currency: 'BRL',
    validUntil: '2024-03-15',
    sentAt: '2024-02-15',
    createdBy: 'user-001',
    createdAt: '2024-02-10',
    updatedAt: '2024-02-15',
    comments: [],
    version: 1,
  },
  {
    id: '2',
    contactId: 'contact-002',
    title: 'Servicos de Portaria - Trimestre',
    status: 'draft',
    sections: [],
    total: 28500,
    currency: 'BRL',
    validUntil: '2024-03-20',
    createdBy: 'user-001',
    createdAt: '2024-02-18',
    updatedAt: '2024-02-18',
    comments: [],
    version: 1,
  },
  {
    id: '3',
    contactId: 'contact-003',
    title: 'Contrato Limpeza Anual',
    status: 'accepted',
    sections: [],
    total: 120000,
    currency: 'BRL',
    validUntil: '2024-02-28',
    sentAt: '2024-02-01',
    viewedAt: '2024-02-02',
    respondedAt: '2024-02-05',
    signedBy: 'Cliente ABC',
    signedAt: '2024-02-05',
    createdBy: 'user-001',
    createdAt: '2024-01-25',
    updatedAt: '2024-02-05',
    comments: [],
    version: 2,
  },
  {
    id: '4',
    contactId: 'contact-004',
    title: 'Projeto Seguranca Eletronica',
    status: 'rejected',
    sections: [],
    total: 85000,
    currency: 'BRL',
    validUntil: '2024-02-20',
    sentAt: '2024-02-08',
    viewedAt: '2024-02-09',
    respondedAt: '2024-02-12',
    createdBy: 'user-001',
    createdAt: '2024-02-05',
    updatedAt: '2024-02-12',
    comments: [],
    version: 1,
  },
];

export default ProposalCard;
