'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Stethoscope,
  Search,
  Plus,
  Download,
  Upload,
  Calendar,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  Edit,
  FileText,
  User,
  Filter,
  Printer,
  Mail,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
  Avatar,
} from '@/design-system/components';

// Types
interface MedicalExam {
  id: string;
  employeeId: string;
  employeeName: string;
  employeePosition: string;
  examType: 'admissional' | 'periodico' | 'retorno' | 'mudanca_funcao' | 'demissional';
  scheduledDate: string;
  examDate: string | null;
  result: 'apto' | 'inapto' | 'apto_restricao' | 'pending' | null;
  nextExam: string | null;
  doctor: string | null;
  clinic: string;
  status: 'scheduled' | 'completed' | 'missed' | 'cancelled';
  asoNumber: string | null;
}

interface ASO {
  id: string;
  number: string;
  employeeName: string;
  examType: string;
  examDate: string;
  result: 'apto' | 'inapto' | 'apto_restricao';
  validUntil: string;
  doctor: string;
  crm: string;
}

// Mock Data
const exams: MedicalExam[] = [
  {
    id: '1',
    employeeId: 'EMP001',
    employeeName: 'Roberto Silva',
    employeePosition: 'Vigilante',
    examType: 'periodico',
    scheduledDate: '2026-01-20',
    examDate: null,
    result: null,
    nextExam: null,
    doctor: null,
    clinic: 'Clínica MedOcup',
    status: 'scheduled',
    asoNumber: null,
  },
  {
    id: '2',
    employeeId: 'EMP002',
    employeeName: 'Maria Santos',
    employeePosition: 'Vigilante',
    examType: 'retorno',
    scheduledDate: '2026-01-18',
    examDate: null,
    result: null,
    nextExam: null,
    doctor: null,
    clinic: 'Clínica MedOcup',
    status: 'scheduled',
    asoNumber: null,
  },
  {
    id: '3',
    employeeId: 'EMP003',
    employeeName: 'Carlos Eduardo',
    employeePosition: 'Supervisor',
    examType: 'periodico',
    scheduledDate: '2026-01-10',
    examDate: '2026-01-10',
    result: 'apto',
    nextExam: '2027-01-10',
    doctor: 'Dr. José Almeida',
    clinic: 'Clínica MedOcup',
    status: 'completed',
    asoNumber: 'ASO-2026-0045',
  },
  {
    id: '4',
    employeeId: 'EMP004',
    employeeName: 'Ana Paula',
    employeePosition: 'Porteira',
    examType: 'mudanca_funcao',
    scheduledDate: '2026-01-22',
    examDate: null,
    result: null,
    nextExam: null,
    doctor: null,
    clinic: 'Clínica Saúde Total',
    status: 'scheduled',
    asoNumber: null,
  },
  {
    id: '5',
    employeeId: 'EMP005',
    employeeName: 'João Pereira',
    employeePosition: 'Vigilante',
    examType: 'admissional',
    scheduledDate: '2026-01-05',
    examDate: '2026-01-05',
    result: 'apto',
    nextExam: '2027-01-05',
    doctor: 'Dra. Maria Fernandes',
    clinic: 'Clínica MedOcup',
    status: 'completed',
    asoNumber: 'ASO-2026-0042',
  },
  {
    id: '6',
    employeeId: 'EMP006',
    employeeName: 'Pedro Almeida',
    employeePosition: 'Vigilante',
    examType: 'periodico',
    scheduledDate: '2026-01-08',
    examDate: null,
    result: null,
    nextExam: null,
    doctor: null,
    clinic: 'Clínica MedOcup',
    status: 'missed',
    asoNumber: null,
  },
];

const asos: ASO[] = [
  { id: '1', number: 'ASO-2026-0045', employeeName: 'Carlos Eduardo', examType: 'Periódico', examDate: '2026-01-10', result: 'apto', validUntil: '2027-01-10', doctor: 'Dr. José Almeida', crm: 'CRM-SP 123456' },
  { id: '2', number: 'ASO-2026-0044', employeeName: 'Juliana Costa', examType: 'Periódico', examDate: '2026-01-09', result: 'apto', validUntil: '2027-01-09', doctor: 'Dra. Maria Fernandes', crm: 'CRM-SP 654321' },
  { id: '3', number: 'ASO-2026-0043', employeeName: 'Marcos Lima', examType: 'Admissional', examDate: '2026-01-08', result: 'apto_restricao', validUntil: '2027-01-08', doctor: 'Dr. José Almeida', crm: 'CRM-SP 123456' },
  { id: '4', number: 'ASO-2026-0042', employeeName: 'João Pereira', examType: 'Admissional', examDate: '2026-01-05', result: 'apto', validUntil: '2027-01-05', doctor: 'Dra. Maria Fernandes', crm: 'CRM-SP 654321' },
];

const examTypeLabels = {
  admissional: 'Admissional',
  periodico: 'Periódico',
  retorno: 'Retorno ao Trabalho',
  mudanca_funcao: 'Mudança de Função',
  demissional: 'Demissional',
};

const resultConfig = {
  apto: { label: 'Apto', color: 'success' as const },
  inapto: { label: 'Inapto', color: 'danger' as const },
  apto_restricao: { label: 'Apto c/ Restrição', color: 'warning' as const },
  pending: { label: 'Aguardando', color: 'info' as const },
};

const statusConfig = {
  scheduled: { label: 'Agendado', color: 'info' as const },
  completed: { label: 'Realizado', color: 'success' as const },
  missed: { label: 'Não Compareceu', color: 'danger' as const },
  cancelled: { label: 'Cancelado', color: 'info' as const },
};

const examColumns: Column<MedicalExam>[] = [
  {
    key: 'employeeName',
    header: 'Funcionário',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.employeeName} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.employeeName}</p>
          <p className="text-xs text-text-muted">{row.employeeId} • {row.employeePosition}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'examType',
    header: 'Tipo de Exame',
    render: (row) => <Badge variant="info">{examTypeLabels[row.examType]}</Badge>,
  },
  {
    key: 'scheduledDate',
    header: 'Data Agendada',
    render: (row) => (
      <span className="text-sm">{new Date(row.scheduledDate).toLocaleDateString('pt-BR')}</span>
    ),
  },
  {
    key: 'clinic',
    header: 'Clínica',
    render: (row) => <span className="text-sm text-text-secondary">{row.clinic}</span>,
  },
  {
    key: 'result',
    header: 'Resultado',
    render: (row) => {
      if (!row.result) return <span className="text-text-muted">-</span>;
      const config = resultConfig[row.result];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'scheduled' && (
          <Button variant="ghost" size="icon-sm" title="Editar">
            <Edit className="w-4 h-4" />
          </Button>
        )}
        {row.status === 'completed' && row.asoNumber && (
          <Button variant="ghost" size="icon-sm" title="ASO">
            <FileText className="w-4 h-4" />
          </Button>
        )}
      </div>
    ),
  },
];

const asoColumns: Column<ASO>[] = [
  {
    key: 'number',
    header: 'Número ASO',
    render: (row) => <span className="font-medium text-text-primary">{row.number}</span>,
  },
  {
    key: 'employeeName',
    header: 'Funcionário',
    render: (row) => <span className="text-text-primary">{row.employeeName}</span>,
  },
  {
    key: 'examType',
    header: 'Tipo',
    render: (row) => <Badge variant="info">{row.examType}</Badge>,
  },
  {
    key: 'examDate',
    header: 'Data Exame',
    render: (row) => <span className="text-sm">{new Date(row.examDate).toLocaleDateString('pt-BR')}</span>,
  },
  {
    key: 'result',
    header: 'Resultado',
    render: (row) => {
      const config = resultConfig[row.result];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'validUntil',
    header: 'Válido Até',
    render: (row) => <span className="text-sm">{new Date(row.validUntil).toLocaleDateString('pt-BR')}</span>,
  },
  {
    key: 'doctor',
    header: 'Médico',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.doctor}</p>
        <p className="text-xs text-text-muted">{row.crm}</p>
      </div>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Imprimir">
          <Printer className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Download">
          <Download className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Enviar">
          <Mail className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function PCMSOPage() {
  const [selectedTab, setSelectedTab] = useState('exams');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter states
  const [filterExamType, setFilterExamType] = useState('all');
  const [filterExamStatus, setFilterExamStatus] = useState('all');

  // Modal form states
  const [newEmployee, setNewEmployee] = useState('');
  const [newExamType, setNewExamType] = useState('');
  const [newClinic, setNewClinic] = useState('');

  // Stats
  const scheduledExams = exams.filter(e => e.status === 'scheduled').length;
  const completedExams = exams.filter(e => e.status === 'completed').length;
  const missedExams = exams.filter(e => e.status === 'missed').length;
  const aptoCount = exams.filter(e => e.result === 'apto').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              PCMSO - Programa de Controle Médico
            </h1>
            <p className="text-text-secondary mt-1">
              NR-7 - Gestão de exames ocupacionais
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Upload className="w-4 h-4" />}>
              Importar
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Agendar Exame
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Exames Agendados"
              value={scheduledExams}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Realizados (Mês)"
              value={completedExams}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Não Compareceram"
              value={missedExams}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Aptos"
              value={aptoCount}
              icon={<Stethoscope className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'exams', label: 'Exames' },
                { value: 'asos', label: 'ASOs Emitidos' },
                { value: 'calendar', label: 'Calendário' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="border-b border-border-subtle">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Buscar funcionário..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                {selectedTab === 'exams' && (
                  <>
                    <Select
                      options={[
                        { value: 'all', label: 'Todos os Tipos' },
                        { value: 'admissional', label: 'Admissional' },
                        { value: 'periodico', label: 'Periódico' },
                        { value: 'retorno', label: 'Retorno' },
                        { value: 'mudanca_funcao', label: 'Mudança de Função' },
                        { value: 'demissional', label: 'Demissional' },
                      ]}
                      value={filterExamType}
                      onChange={(value) => setFilterExamType(value)}
                      className="w-48"
                    />
                    <Select
                      options={[
                        { value: 'all', label: 'Todos os Status' },
                        { value: 'scheduled', label: 'Agendados' },
                        { value: 'completed', label: 'Realizados' },
                        { value: 'missed', label: 'Não Compareceram' },
                      ]}
                      value={filterExamStatus}
                      onChange={(value) => setFilterExamStatus(value)}
                      className="w-44"
                    />
                  </>
                )}
              </div>
            </CardBody>
            <CardBody className="p-0">
              {selectedTab === 'exams' ? (
                <DataTable
                  columns={examColumns}
                  data={exams}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'asos' ? (
                <DataTable
                  columns={asoColumns}
                  data={asos}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <div className="p-8 text-center">
                  <Calendar className="w-12 h-12 text-text-muted mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-text-primary">Calendário de Exames</h3>
                  <p className="text-text-secondary mt-1">Visualize os exames agendados no calendário</p>
                </div>
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* Schedule Exam Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Agendar Exame Médico"
          description="Agende um novo exame ocupacional"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Agendar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Funcionário"
              options={[
                { value: '1', label: 'Roberto Silva - Vigilante' },
                { value: '2', label: 'Maria Santos - Vigilante' },
                { value: '3', label: 'Carlos Eduardo - Supervisor' },
              ]}
              value={newEmployee}
              onChange={(value) => setNewEmployee(value)}
              placeholder="Selecione o funcionário..."
            />
            <Select
              label="Tipo de Exame"
              options={[
                { value: 'admissional', label: 'Admissional' },
                { value: 'periodico', label: 'Periódico' },
                { value: 'retorno', label: 'Retorno ao Trabalho' },
                { value: 'mudanca_funcao', label: 'Mudança de Função' },
                { value: 'demissional', label: 'Demissional' },
              ]}
              value={newExamType}
              onChange={(value) => setNewExamType(value)}
              placeholder="Selecione..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data" type="date" />
              <Input label="Horário" type="time" />
            </div>
            <Select
              label="Clínica"
              options={[
                { value: '1', label: 'Clínica MedOcup' },
                { value: '2', label: 'Clínica Saúde Total' },
                { value: '3', label: 'Centro Médico Ocupacional' },
              ]}
              value={newClinic}
              onChange={(value) => setNewClinic(value)}
              placeholder="Selecione a clínica..."
            />
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Observações</label>
              <textarea
                className="w-full h-20 px-3 py-2 bg-bg-tertiary border border-border-default rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent"
                placeholder="Observações adicionais..."
              />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
