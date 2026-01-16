'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Calendar,
  Clock,
  Users,
  ChevronLeft,
  ChevronRight,
  Eye,
  Edit,
  Copy,
  Download,
  CheckCircle2,
  AlertTriangle,
  User,
  Building2,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  SimpleTabBar,
  Modal,
  Select,
} from '@/design-system/components';

// Types
interface Scale {
  id: string;
  name: string;
  client: string;
  post: string;
  period: string;
  type: '12x36' | '24h' | '6x1' | '5x2' | 'custom';
  totalShifts: number;
  coveredShifts: number;
  employees: {
    id: string;
    name: string;
    role: string;
    shifts: number[];
  }[];
  status: 'active' | 'draft' | 'archived';
}

interface ShiftCell {
  employee: string;
  shift: 'day' | 'night' | 'off' | 'vacation' | 'leave';
}

// Mock Data
const scales: Scale[] = [
  {
    id: '1',
    name: 'Escala Janeiro - Segurança',
    client: 'Shopping Center Norte',
    post: 'Portaria Principal',
    period: 'Janeiro 2026',
    type: '12x36',
    totalShifts: 62,
    coveredShifts: 62,
    employees: [
      { id: '1', name: 'Carlos Eduardo', role: 'Vigilante', shifts: [1, 0, 1, 0, 1, 0, 1] },
      { id: '2', name: 'José Roberto', role: 'Vigilante', shifts: [0, 1, 0, 1, 0, 1, 0] },
      { id: '3', name: 'André Silva', role: 'Vigilante', shifts: [1, 0, 1, 0, 1, 0, 1] },
      { id: '4', name: 'Paulo Santos', role: 'Vigilante', shifts: [0, 1, 0, 1, 0, 1, 0] },
    ],
    status: 'active',
  },
  {
    id: '2',
    name: 'Escala Janeiro - Limpeza',
    client: 'Hospital São Lucas',
    post: 'UTI Adulto',
    period: 'Janeiro 2026',
    type: '6x1',
    totalShifts: 186,
    coveredShifts: 180,
    employees: [
      { id: '5', name: 'Maria Aparecida', role: 'Aux. Limpeza', shifts: [1, 1, 1, 1, 1, 1, 0] },
      { id: '6', name: 'Ana Paula', role: 'Aux. Limpeza', shifts: [1, 1, 1, 1, 1, 1, 0] },
      { id: '7', name: 'Lucia Ferreira', role: 'Aux. Limpeza', shifts: [1, 1, 1, 1, 1, 1, 0] },
    ],
    status: 'active',
  },
  {
    id: '3',
    name: 'Escala Fevereiro - Segurança',
    client: 'Shopping Center Norte',
    post: 'Portaria Principal',
    period: 'Fevereiro 2026',
    type: '12x36',
    totalShifts: 56,
    coveredShifts: 0,
    employees: [],
    status: 'draft',
  },
];

const typeConfig = {
  '12x36': { label: '12x36', description: '12h trabalho, 36h folga' },
  '24h': { label: '24 horas', description: '24h trabalho, 72h folga' },
  '6x1': { label: '6x1', description: '6 dias trabalho, 1 folga' },
  '5x2': { label: '5x2', description: 'Seg-Sex, folga Sáb-Dom' },
  custom: { label: 'Personalizada', description: 'Escala customizada' },
};

const weekDays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];

function ScaleCalendar({ scale }: { scale: Scale }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[600px]">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left py-3 px-4 text-sm font-medium text-text-secondary">
              Funcionário
            </th>
            {weekDays.map((day, i) => (
              <th
                key={day}
                className="text-center py-3 px-2 text-sm font-medium text-text-secondary w-14"
              >
                <div>{day}</div>
                <div className="text-xs text-text-muted">{13 + i}/01</div>
              </th>
            ))}
            <th className="text-center py-3 px-4 text-sm font-medium text-text-secondary">
              Total
            </th>
          </tr>
        </thead>
        <tbody>
          {scale.employees.map((employee) => (
            <tr key={employee.id} className="border-b border-border-subtle">
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  <Avatar name={employee.name} size="xs" />
                  <div>
                    <p className="text-sm font-medium text-text-primary">{employee.name}</p>
                    <p className="text-xs text-text-muted">{employee.role}</p>
                  </div>
                </div>
              </td>
              {employee.shifts.map((shift, idx) => (
                <td key={idx} className="text-center py-3 px-2">
                  {shift === 1 ? (
                    <div className="w-8 h-8 mx-auto rounded-lg bg-success/20 flex items-center justify-center">
                      <span className="text-xs font-medium text-success">D</span>
                    </div>
                  ) : (
                    <div className="w-8 h-8 mx-auto rounded-lg bg-bg-tertiary flex items-center justify-center">
                      <span className="text-xs text-text-muted">-</span>
                    </div>
                  )}
                </td>
              ))}
              <td className="text-center py-3 px-4">
                <span className="font-mono text-sm font-medium text-text-primary">
                  {employee.shifts.filter((s) => s === 1).length}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ScaleCard({ scale, onView }: { scale: Scale; onView: () => void }) {
  const coverage = Math.round((scale.coveredShifts / scale.totalShifts) * 100);
  const statusConfig = {
    active: { label: 'Ativa', color: 'success' as const },
    draft: { label: 'Rascunho', color: 'warning' as const },
    archived: { label: 'Arquivada', color: 'neutral' as const },
  };

  return (
    <Card className="hover:border-accent-primary/50 transition-colors cursor-pointer" onClick={onView}>
      <CardBody>
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-medium text-text-primary">{scale.name}</h3>
            <p className="text-sm text-text-muted mt-1">{scale.period}</p>
          </div>
          <Badge variant={statusConfig[scale.status].color}>
            {statusConfig[scale.status].label}
          </Badge>
        </div>

        <div className="space-y-3 mb-4">
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Building2 className="w-4 h-4 text-text-muted" />
            <span>{scale.client}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Clock className="w-4 h-4 text-text-muted" />
            <span>{typeConfig[scale.type].label} - {typeConfig[scale.type].description}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Users className="w-4 h-4 text-text-muted" />
            <span>{scale.employees.length} funcionários</span>
          </div>
        </div>

        <div className="mb-4">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-text-muted">Cobertura</span>
            <span className={`font-medium ${coverage >= 90 ? 'text-success' : coverage >= 70 ? 'text-warning' : 'text-danger'}`}>
              {coverage}%
            </span>
          </div>
          <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                coverage >= 90 ? 'bg-success' : coverage >= 70 ? 'bg-warning' : 'bg-danger'
              }`}
              style={{ width: `${coverage}%` }}
            />
          </div>
          <p className="text-xs text-text-muted mt-1">
            {scale.coveredShifts} de {scale.totalShifts} turnos cobertos
          </p>
        </div>

        <div className="flex items-center gap-2 pt-4 border-t border-border-subtle">
          <Button variant="ghost" size="sm" leftIcon={<Eye className="w-4 h-4" />}>
            Ver
          </Button>
          <Button variant="ghost" size="sm" leftIcon={<Edit className="w-4 h-4" />}>
            Editar
          </Button>
          <Button variant="ghost" size="sm" leftIcon={<Copy className="w-4 h-4" />}>
            Duplicar
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}

export function ScalesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedScale, setSelectedScale] = useState<Scale | null>(null);

  const filteredScales = scales.filter((scale) => {
    const matchesSearch =
      scale.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scale.client.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || scale.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  // Stats
  const totalScales = scales.length;
  const activeScales = scales.filter((s) => s.status === 'active').length;
  const totalShifts = scales.reduce((acc, s) => acc + s.totalShifts, 0);
  const coveredShifts = scales.reduce((acc, s) => acc + s.coveredShifts, 0);
  const uncoveredShifts = totalShifts - coveredShifts;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Escalas de Trabalho
            </h1>
            <p className="text-text-secondary mt-1">
              Monte e gerencie as escalas dos funcionários
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Escala
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total de Escalas"
              value={totalScales}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Escalas Ativas"
              value={activeScales}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Total de Turnos"
              value={totalShifts}
              icon={<Clock className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Turnos Cobertos"
              value={coveredShifts}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <StatCard
              title="Turnos Descobertos"
              value={uncoveredShifts}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todas (${scales.length})` },
                  { value: 'active', label: `Ativas (${activeScales})` },
                  { value: 'draft', label: `Rascunhos (${scales.filter((s) => s.status === 'draft').length})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar escalas..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Scales Grid */}
        <div className="grid grid-cols-3 gap-6">
          {filteredScales.map((scale) => (
            <motion.div
              key={scale.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <ScaleCard
                scale={scale}
                onView={() => setSelectedScale(scale)}
              />
            </motion.div>
          ))}
        </div>

        {/* Scale Detail Modal */}
        <Modal
          isOpen={!!selectedScale}
          onClose={() => setSelectedScale(null)}
          title={selectedScale?.name || ''}
          description={`${selectedScale?.client} - ${selectedScale?.post}`}
          size="xl"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedScale(null)}>
                Fechar
              </Button>
              <Button variant="primary">
                Editar Escala
              </Button>
            </>
          }
        >
          {selectedScale && (
            <div className="space-y-6">
              {/* Scale Info */}
              <div className="grid grid-cols-4 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-xs text-text-muted mb-1">Período</p>
                  <p className="font-medium text-text-primary">{selectedScale.period}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-xs text-text-muted mb-1">Tipo</p>
                  <p className="font-medium text-text-primary">{typeConfig[selectedScale.type].label}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-xs text-text-muted mb-1">Funcionários</p>
                  <p className="font-medium text-text-primary">{selectedScale.employees.length}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-xs text-text-muted mb-1">Cobertura</p>
                  <p className="font-medium text-text-primary">
                    {Math.round((selectedScale.coveredShifts / selectedScale.totalShifts) * 100)}%
                  </p>
                </div>
              </div>

              {/* Scale Calendar */}
              <div>
                <h4 className="text-sm font-medium text-text-primary mb-4">Semana 13-19 Janeiro</h4>
                <ScaleCalendar scale={selectedScale} />
              </div>
            </div>
          )}
        </Modal>

        {/* New Scale Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Escala"
          description="Configure uma nova escala de trabalho"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar Escala
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome da Escala" placeholder="Ex: Escala Janeiro - Segurança" required />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Cliente"
                options={[
                  { value: '1', label: 'Shopping Center Norte' },
                  { value: '2', label: 'Hospital São Lucas' },
                  { value: '3', label: 'Condomínio Aurora' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Posto"
                options={[
                  { value: '1', label: 'Portaria Principal' },
                  { value: '2', label: 'UTI Adulto' },
                  { value: '3', label: 'Guarita' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Escala"
                options={[
                  { value: '12x36', label: '12x36' },
                  { value: '24h', label: '24 horas' },
                  { value: '6x1', label: '6x1' },
                  { value: '5x2', label: '5x2' },
                  { value: 'custom', label: 'Personalizada' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Período"
                options={[
                  { value: '2026-01', label: 'Janeiro 2026' },
                  { value: '2026-02', label: 'Fevereiro 2026' },
                  { value: '2026-03', label: 'Março 2026' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
