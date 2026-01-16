'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  Search,
  Filter,
  Download,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  MapPin,
  User,
  Building2,
  ChevronLeft,
  ChevronRight,
  Camera,
  Fingerprint,
  QrCode,
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
  DataTable,
  type Column,
  SimpleTabBar,
  Select,
  Modal,
} from '@/design-system/components';

// Types
interface TimeRecord {
  id: string;
  employee: string;
  employeeId: string;
  department: string;
  client: string;
  date: string;
  entries: {
    time: string;
    type: 'entry' | 'exit' | 'break_start' | 'break_end';
    method: 'biometric' | 'facial' | 'qrcode' | 'manual';
    location: string;
    photo?: string;
  }[];
  totalHours: number;
  overtime: number;
  status: 'complete' | 'incomplete' | 'absent' | 'justified';
}

// Mock Data
const timeRecords: TimeRecord[] = [
  {
    id: '1',
    employee: 'Carlos Eduardo Silva',
    employeeId: 'EMP-001',
    department: 'Segurança',
    client: 'Shopping Center Norte',
    date: '2026-01-15',
    entries: [
      { time: '06:00', type: 'entry', method: 'biometric', location: 'Portaria Principal' },
      { time: '12:00', type: 'break_start', method: 'biometric', location: 'Refeitório' },
      { time: '13:00', type: 'break_end', method: 'biometric', location: 'Refeitório' },
      { time: '14:00', type: 'exit', method: 'biometric', location: 'Portaria Principal' },
    ],
    totalHours: 8,
    overtime: 0,
    status: 'complete',
  },
  {
    id: '2',
    employee: 'Maria Aparecida Santos',
    employeeId: 'EMP-002',
    department: 'Limpeza',
    client: 'Hospital São Lucas',
    date: '2026-01-15',
    entries: [
      { time: '07:00', type: 'entry', method: 'facial', location: 'Entrada Funcionários' },
      { time: '12:00', type: 'break_start', method: 'facial', location: 'Refeitório' },
      { time: '13:00', type: 'break_end', method: 'facial', location: 'Refeitório' },
      { time: '17:00', type: 'exit', method: 'facial', location: 'Entrada Funcionários' },
    ],
    totalHours: 9,
    overtime: 1,
    status: 'complete',
  },
  {
    id: '3',
    employee: 'José Roberto Lima',
    employeeId: 'EMP-003',
    department: 'Portaria',
    client: 'Condomínio Aurora',
    date: '2026-01-15',
    entries: [
      { time: '18:00', type: 'entry', method: 'qrcode', location: 'Guarita' },
    ],
    totalHours: 0,
    overtime: 0,
    status: 'incomplete',
  },
  {
    id: '4',
    employee: 'Ana Paula Oliveira',
    employeeId: 'EMP-004',
    department: 'Administrativo',
    client: 'Sede Central',
    date: '2026-01-15',
    entries: [],
    totalHours: 0,
    overtime: 0,
    status: 'justified',
  },
  {
    id: '5',
    employee: 'Pedro Henrique Costa',
    employeeId: 'EMP-005',
    department: 'Manutenção',
    client: 'Tech Park',
    date: '2026-01-15',
    entries: [],
    totalHours: 0,
    overtime: 0,
    status: 'absent',
  },
];

const statusConfig = {
  complete: { label: 'Completo', color: 'success' as const, icon: CheckCircle2 },
  incomplete: { label: 'Incompleto', color: 'warning' as const, icon: AlertTriangle },
  absent: { label: 'Falta', color: 'danger' as const, icon: XCircle },
  justified: { label: 'Justificado', color: 'info' as const, icon: Calendar },
};

const methodConfig = {
  biometric: { label: 'Biométrico', icon: Fingerprint },
  facial: { label: 'Facial', icon: Camera },
  qrcode: { label: 'QR Code', icon: QrCode },
  manual: { label: 'Manual', icon: User },
};

const columns: Column<TimeRecord>[] = [
  {
    key: 'employee',
    header: 'Funcionário',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.employee} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.employee}</p>
          <p className="text-xs text-text-muted">{row.employeeId}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'client',
    header: 'Alocação',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Building2 className="w-4 h-4 text-text-muted" />
        <div>
          <p className="text-sm text-text-secondary">{row.client}</p>
          <p className="text-xs text-text-muted">{row.department}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'entries',
    header: 'Registros',
    render: (row) => (
      <div className="flex items-center gap-2">
        {row.entries.length > 0 ? (
          row.entries.map((entry, idx) => {
            const MethodIcon = methodConfig[entry.method].icon;
            return (
              <div
                key={idx}
                className="flex items-center gap-1 px-2 py-1 bg-bg-tertiary rounded text-xs"
                title={`${entry.type === 'entry' ? 'Entrada' : entry.type === 'exit' ? 'Saída' : 'Intervalo'} - ${entry.method}`}
              >
                <MethodIcon className="w-3 h-3 text-text-muted" />
                <span className="font-mono">{entry.time}</span>
              </div>
            );
          })
        ) : (
          <span className="text-text-muted text-sm">Sem registros</span>
        )}
      </div>
    ),
  },
  {
    key: 'totalHours',
    header: 'Horas',
    render: (row) => (
      <div className="text-center">
        <p className="font-mono font-medium text-text-primary">{row.totalHours}h</p>
        {row.overtime > 0 && (
          <p className="text-xs text-success">+{row.overtime}h extra</p>
        )}
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return (
        <Badge variant={config.color} leftIcon={<config.icon className="w-3 h-3" />}>
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="sm">
          Detalhes
        </Button>
        {row.status === 'incomplete' && (
          <Button variant="outline" size="sm">
            Ajustar
          </Button>
        )}
      </div>
    ),
  },
];

export function TimeTrackingPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [selectedDate, setSelectedDate] = useState('2026-01-15');
  const [selectedClient, setSelectedClient] = useState('all');
  const [selectedRecord, setSelectedRecord] = useState<TimeRecord | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const filteredRecords = timeRecords.filter((record) => {
    const matchesSearch =
      record.employee.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.employeeId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || record.status === selectedTab;
    const matchesClient = selectedClient === 'all' || record.client === selectedClient;
    return matchesSearch && matchesTab && matchesClient;
  });

  // Stats
  const totalEmployees = timeRecords.length;
  const completeCount = timeRecords.filter((r) => r.status === 'complete').length;
  const incompleteCount = timeRecords.filter((r) => r.status === 'incomplete').length;
  const absentCount = timeRecords.filter((r) => r.status === 'absent').length;
  const totalOvertime = timeRecords.reduce((acc, r) => acc + r.overtime, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Ponto Eletrônico
            </h1>
            <p className="text-text-secondary mt-1">
              Controle de frequência e horas trabalhadas
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar Espelho
            </Button>
            <Button variant="primary" leftIcon={<Clock className="w-4 h-4" />}>
              Registro Manual
            </Button>
          </div>
        </div>

        {/* Date Navigation */}
        <Card>
          <CardBody className="py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon-sm">
                  <ChevronLeft className="w-5 h-5" />
                </Button>
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-accent-primary" />
                  <Input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="w-40"
                  />
                </div>
                <Button variant="ghost" size="icon-sm">
                  <ChevronRight className="w-5 h-5" />
                </Button>
                <Button variant="outline" size="sm">
                  Hoje
                </Button>
              </div>
              <Select
                options={[
                  { value: 'all', label: 'Todos os Clientes' },
                  { value: 'Shopping Center Norte', label: 'Shopping Center Norte' },
                  { value: 'Hospital São Lucas', label: 'Hospital São Lucas' },
                  { value: 'Condomínio Aurora', label: 'Condomínio Aurora' },
                  { value: 'Tech Park', label: 'Tech Park' },
                ]}
                value={selectedClient}
                onChange={setSelectedClient}
                className="w-56"
              />
            </div>
          </CardBody>
        </Card>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total Esperado"
              value={totalEmployees}
              icon={<User className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Completos"
              value={completeCount}
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
              title="Incompletos"
              value={incompleteCount}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Faltas"
              value={absentCount}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <StatCard
              title="Horas Extras"
              value={`${totalOvertime}h`}
              icon={<Clock className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todos (${timeRecords.length})` },
                  { value: 'complete', label: `Completos (${completeCount})` },
                  { value: 'incomplete', label: `Incompletos (${incompleteCount})` },
                  { value: 'absent', label: `Faltas (${absentCount})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar funcionário..."
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

        {/* Time Records Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredRecords}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => { setSelectedRecord(row); setShowDetailModal(true); }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Alerts */}
        {incompleteCount > 0 && (
          <Card className="border-warning/30 bg-warning/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-warning/10">
                  <AlertTriangle className="w-6 h-6 text-warning" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    {incompleteCount} funcionário(s) com ponto incompleto
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Verifique os registros e faça os ajustes necessários
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Notificar Supervisores
                </Button>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes do Ponto"
          description={selectedRecord ? `${selectedRecord.employee} - ${selectedRecord.date}` : ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              {selectedRecord?.status === 'incomplete' && (
                <Button variant="primary">Ajustar Ponto</Button>
              )}
            </>
          }
        >
          {selectedRecord && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <Avatar name={selectedRecord.employee} size="lg" />
                <div>
                  <p className="text-lg font-medium text-text-primary">{selectedRecord.employee}</p>
                  <p className="text-sm text-text-muted">{selectedRecord.employeeId}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={statusConfig[selectedRecord.status].color}>
                      {statusConfig[selectedRecord.status].label}
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Cliente</p>
                  <p className="font-medium text-text-primary">{selectedRecord.client}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Departamento</p>
                  <p className="font-medium text-text-primary">{selectedRecord.department}</p>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-text-primary mb-3">Registros do Dia</h4>
                <div className="space-y-2">
                  {selectedRecord.entries.length > 0 ? (
                    selectedRecord.entries.map((entry, idx) => {
                      const MethodIcon = methodConfig[entry.method].icon;
                      return (
                        <div key={idx} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-bg-primary rounded-lg">
                              <MethodIcon className="w-4 h-4 text-text-muted" />
                            </div>
                            <div>
                              <p className="font-medium text-text-primary">
                                {entry.type === 'entry' ? 'Entrada' : entry.type === 'exit' ? 'Saída' : entry.type === 'break_start' ? 'Início Intervalo' : 'Fim Intervalo'}
                              </p>
                              <p className="text-xs text-text-muted">{entry.location}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-mono font-bold text-text-primary">{entry.time}</p>
                            <p className="text-xs text-text-muted">{methodConfig[entry.method].label}</p>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-center text-text-muted py-4">Sem registros</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 p-4 bg-bg-tertiary rounded-lg">
                <div>
                  <p className="text-sm text-text-muted">Total de Horas</p>
                  <p className="text-2xl font-bold text-text-primary">{selectedRecord.totalHours}h</p>
                </div>
                <div>
                  <p className="text-sm text-text-muted">Horas Extras</p>
                  <p className="text-2xl font-bold text-success">{selectedRecord.overtime}h</p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
