'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Calendar,
  Plus,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Download,
  FileText,
  Sun,
  Umbrella,
  DollarSign
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { MainLayout } from '../../layouts/MainLayout';

// Types
interface VacationPeriod {
  id: string;
  periodStart: string;
  periodEnd: string;
  totalDays: number;
  usedDays: number;
  scheduledDays: number;
  availableDays: number;
  status: 'active' | 'expired' | 'upcoming';
}

interface VacationRequest {
  id: string;
  periodId: string;
  startDate: string;
  endDate: string;
  days: number;
  type: 'full' | 'partial' | 'sell';
  sellDays: number;
  advancePayment: boolean;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled' | 'completed';
  requestDate: string;
  approvedBy: string | null;
  approvedAt: string | null;
  notes: string;
}

// Mock Data
const currentPeriod: VacationPeriod = {
  id: '1',
  periodStart: '2023-03-15',
  periodEnd: '2024-03-14',
  totalDays: 30,
  usedDays: 10,
  scheduledDays: 5,
  availableDays: 15,
  status: 'active'
};

const vacationHistory: VacationRequest[] = [
  {
    id: '1',
    periodId: '1',
    startDate: '2024-03-20',
    endDate: '2024-03-25',
    days: 5,
    type: 'partial',
    sellDays: 0,
    advancePayment: true,
    status: 'approved',
    requestDate: '2024-02-10',
    approvedBy: 'Maria Fernanda Costa',
    approvedAt: '2024-02-12',
    notes: 'Aprovado'
  },
  {
    id: '2',
    periodId: '1',
    startDate: '2023-12-20',
    endDate: '2023-12-30',
    days: 10,
    type: 'partial',
    sellDays: 0,
    advancePayment: true,
    status: 'completed',
    requestDate: '2023-11-15',
    approvedBy: 'Maria Fernanda Costa',
    approvedAt: '2023-11-16',
    notes: 'Gozo concluído'
  },
  {
    id: '3',
    periodId: '0',
    startDate: '2023-07-01',
    endDate: '2023-07-20',
    days: 20,
    type: 'partial',
    sellDays: 10,
    advancePayment: true,
    status: 'completed',
    requestDate: '2023-05-20',
    approvedBy: 'Carlos Diretor',
    approvedAt: '2023-05-22',
    notes: 'Com venda de 10 dias'
  }
];

export function VacationPage() {
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestType, setRequestType] = useState<'full' | 'partial' | 'sell'>('partial');
  const [sellDays, setSellDays] = useState(0);
  const [startDate, setStartDate] = useState('');
  const [days, setDays] = useState(10);
  const [advancePayment, setAdvancePayment] = useState(true);

  const getStatusInfo = (status: VacationRequest['status']) => {
    const statuses = {
      pending: { label: 'Pendente', color: 'warning' as const, icon: Clock },
      approved: { label: 'Aprovada', color: 'success' as const, icon: CheckCircle },
      rejected: { label: 'Rejeitada', color: 'danger' as const, icon: XCircle },
      cancelled: { label: 'Cancelada', color: 'info' as const, icon: XCircle },
      completed: { label: 'Concluída', color: 'info' as const, icon: CheckCircle }
    };
    return statuses[status];
  };

  const getTypeLabel = (type: VacationRequest['type']) => {
    const types = {
      full: '30 dias completos',
      partial: 'Parcial',
      sell: 'Com venda de dias'
    };
    return types[type];
  };

  const calculateEndDate = (start: string, numDays: number) => {
    if (!start) return '';
    const date = new Date(start);
    date.setDate(date.getDate() + numDays - 1);
    return date.toISOString().split('T')[0];
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Minhas Férias
            </h1>
            <p className="text-text-secondary mt-1">
              Saldo e solicitações de férias
            </p>
          </div>
          <Button variant="primary" onClick={() => setShowRequestModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Solicitar Férias
          </Button>
        </div>

        {/* Balance Card */}
        <Card className="bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 border-accent-primary/30">
          <CardBody>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="p-4 rounded-2xl bg-accent-primary/20">
                  <Sun className="h-10 w-10 text-accent-primary" />
                </div>
                <div>
                  <p className="text-text-secondary">Período Aquisitivo</p>
                  <p className="text-xl font-semibold text-text-primary">
                    {new Date(currentPeriod.periodStart).toLocaleDateString('pt-BR')} - {new Date(currentPeriod.periodEnd).toLocaleDateString('pt-BR')}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={currentPeriod.status === 'active' ? 'success' : 'warning'}>
                      {currentPeriod.status === 'active' ? 'Período Ativo' : 'Período Expirado'}
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-8">
                <div className="text-center">
                  <div className="text-3xl font-bold text-accent-primary">{currentPeriod.totalDays}</div>
                  <p className="text-sm text-text-secondary">Direito Total</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-accent-success">{currentPeriod.availableDays}</div>
                  <p className="text-sm text-text-secondary">Disponível</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-accent-warning">{currentPeriod.scheduledDays}</div>
                  <p className="text-sm text-text-secondary">Agendado</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-text-secondary">{currentPeriod.usedDays}</div>
                  <p className="text-sm text-text-secondary">Utilizado</p>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-6">
              <div className="h-3 bg-bg-tertiary rounded-full overflow-hidden flex">
                <div
                  className="h-full bg-accent-secondary"
                  style={{ width: `${(currentPeriod.usedDays / currentPeriod.totalDays) * 100}%` }}
                />
                <div
                  className="h-full bg-accent-warning"
                  style={{ width: `${(currentPeriod.scheduledDays / currentPeriod.totalDays) * 100}%` }}
                />
                <div
                  className="h-full bg-accent-success"
                  style={{ width: `${(currentPeriod.availableDays / currentPeriod.totalDays) * 100}%` }}
                />
              </div>
              <div className="flex justify-between mt-2 text-xs text-text-secondary">
                <span>Utilizado ({currentPeriod.usedDays}d)</span>
                <span>Agendado ({currentPeriod.scheduledDays}d)</span>
                <span>Disponível ({currentPeriod.availableDays}d)</span>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Upcoming Vacation */}
        {vacationHistory.filter(v => v.status === 'approved').length > 0 && (
          <Card className="border-accent-success/30 bg-accent-success/5">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Umbrella className="h-5 w-5 text-accent-success" />
                <h3 className="text-lg font-semibold text-text-primary">
                  Próximas Férias
                </h3>
              </div>
            </CardHeader>
            <CardBody>
              {vacationHistory.filter(v => v.status === 'approved').map((vacation) => (
                <div key={vacation.id} className="flex items-center justify-between p-4 bg-bg-secondary rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-accent-success/20">
                      <Calendar className="h-6 w-6 text-accent-success" />
                    </div>
                    <div>
                      <p className="font-semibold text-text-primary">
                        {new Date(vacation.startDate).toLocaleDateString('pt-BR')} a {new Date(vacation.endDate).toLocaleDateString('pt-BR')}
                      </p>
                      <p className="text-sm text-text-secondary">
                        {vacation.days} dias | {vacation.advancePayment ? 'Com adiantamento' : 'Sem adiantamento'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="success">Aprovada</Badge>
                    <Button variant="outline" size="sm">
                      <FileText className="h-4 w-4 mr-2" />
                      Ver Recibo
                    </Button>
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>
        )}

        {/* History */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Histórico de Solicitações
            </h3>
          </CardHeader>
          <CardBody className="space-y-3">
            {vacationHistory.map((vacation, index) => {
              const statusInfo = getStatusInfo(vacation.status);
              const StatusIcon = statusInfo.icon;
              return (
                <motion.div
                  key={vacation.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-bg-tertiary rounded-xl"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg bg-accent-${statusInfo.color}/20`}>
                        <StatusIcon className={`h-5 w-5 text-accent-${statusInfo.color}`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-text-primary">
                            {new Date(vacation.startDate).toLocaleDateString('pt-BR')} - {new Date(vacation.endDate).toLocaleDateString('pt-BR')}
                          </p>
                          <Badge variant={statusInfo.color} size="sm">
                            {statusInfo.label}
                          </Badge>
                        </div>
                        <p className="text-sm text-text-secondary">
                          {vacation.days} dias | {getTypeLabel(vacation.type)}
                          {vacation.sellDays > 0 && ` (${vacation.sellDays} dias vendidos)`}
                        </p>
                        <p className="text-xs text-text-secondary mt-1">
                          Solicitado em {new Date(vacation.requestDate).toLocaleDateString('pt-BR')}
                          {vacation.approvedBy && ` | Aprovado por ${vacation.approvedBy}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      {vacation.status === 'completed' && (
                        <Button variant="ghost" size="sm">
                          <Download className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </CardBody>
        </Card>

        {/* Request Modal */}
        <Modal
          isOpen={showRequestModal}
          onClose={() => setShowRequestModal(false)}
          title="Solicitar Férias"
          size="lg"
        >
          <div className="space-y-6">
            {/* Available Balance Info */}
            <div className="p-4 bg-bg-tertiary rounded-lg flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Saldo disponível</p>
                <p className="text-2xl font-bold text-accent-success">{currentPeriod.availableDays} dias</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-text-secondary">Período aquisitivo</p>
                <p className="text-text-primary">
                  {new Date(currentPeriod.periodStart).toLocaleDateString('pt-BR')} - {new Date(currentPeriod.periodEnd).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>

            {/* Type Selection */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-3">
                Tipo de Férias
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { type: 'full', label: '30 dias', desc: 'Férias completas' },
                  { type: 'partial', label: 'Parcial', desc: 'Dividir em períodos' },
                  { type: 'sell', label: 'Com Abono', desc: 'Vender até 10 dias' }
                ].map((option) => (
                  <button
                    key={option.type}
                    type="button"
                    onClick={() => setRequestType(option.type as typeof requestType)}
                    className={`p-4 rounded-lg border-2 text-left transition-colors ${
                      requestType === option.type
                        ? 'border-accent-primary bg-accent-primary/10'
                        : 'border-border-default hover:border-accent-primary/50'
                    }`}
                  >
                    <p className="font-semibold text-text-primary">{option.label}</p>
                    <p className="text-sm text-text-secondary">{option.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Date and Days */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Data de Início *
                </label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Quantidade de Dias *
                </label>
                <Input
                  type="number"
                  value={days}
                  onChange={(e) => setDays(Math.min(Number(e.target.value), currentPeriod.availableDays))}
                  min={5}
                  max={requestType === 'full' ? 30 : currentPeriod.availableDays}
                />
              </div>
            </div>

            {startDate && (
              <div className="p-3 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-secondary">Data de término</p>
                <p className="font-semibold text-text-primary">
                  {new Date(calculateEndDate(startDate, days)).toLocaleDateString('pt-BR', {
                    weekday: 'long',
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric'
                  })}
                </p>
              </div>
            )}

            {/* Sell Days */}
            {requestType === 'sell' && (
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Dias a Vender (Abono Pecuniário)
                </label>
                <Input
                  type="number"
                  value={sellDays}
                  onChange={(e) => setSellDays(Math.min(Number(e.target.value), 10))}
                  min={1}
                  max={10}
                />
                <p className="text-xs text-text-secondary mt-1">
                  Máximo permitido: 10 dias (1/3 do período)
                </p>
              </div>
            )}

            {/* Advance Payment */}
            <div className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
              <div className="flex items-center gap-3">
                <DollarSign className="h-5 w-5 text-accent-success" />
                <div>
                  <p className="font-medium text-text-primary">Adiantamento de Salário</p>
                  <p className="text-sm text-text-secondary">Receber salário antecipado junto com as férias</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={advancePayment}
                  onChange={(e) => setAdvancePayment(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-bg-secondary peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent-primary"></div>
              </label>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Observações
              </label>
              <textarea
                className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                rows={3}
                placeholder="Informações adicionais para aprovação..."
              />
            </div>

            {/* Warning */}
            <div className="p-4 bg-accent-warning/10 border border-accent-warning/30 rounded-lg flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-accent-warning flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-text-primary">Atenção</p>
                <p className="text-sm text-text-secondary">
                  A solicitação será encaminhada para aprovação do seu gestor.
                  Solicite com no mínimo 30 dias de antecedência.
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setShowRequestModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                <Calendar className="h-4 w-4 mr-2" />
                Enviar Solicitação
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}

export default VacationPage;
