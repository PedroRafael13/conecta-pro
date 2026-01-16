'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  type Column,
  Modal,
  Select
} from '@/design-system/components';
import {
  UserCog,
  Plus,
  Search,
  Filter,
  Download,
  Check,
  X,
  Clock,
  User,
  Users,
  Calendar,
  Building2,
  ArrowRightLeft,
  CheckCircle,
  AlertTriangle,
  Eye
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

// Types
interface Substitution {
  id: string;
  originalEmployee: string;
  substituteEmployee: string;
  date: string;
  shift: string;
  post: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  requestedBy: string;
  requestedAt: string;
  approvedBy?: string;
}

interface AvailableSubstitute {
  id: string;
  name: string;
  department: string;
  currentShift: string;
  skills: string[];
  available: boolean;
  rating: number;
}

// Mock data
const mockSubstitutions: Substitution[] = [
  {
    id: '1',
    originalEmployee: 'João Silva',
    substituteEmployee: 'Carlos Santos',
    date: '2026-01-16',
    shift: 'Matutino',
    post: 'Portaria Principal',
    reason: 'Consulta médica',
    status: 'approved',
    requestedBy: 'Supervisor Maria',
    requestedAt: '2026-01-15T10:00:00',
    approvedBy: 'Gerente Pedro'
  },
  {
    id: '2',
    originalEmployee: 'Maria Costa',
    substituteEmployee: 'Ana Lima',
    date: '2026-01-17',
    shift: 'Vespertino',
    post: 'Recepção',
    reason: 'Licença pessoal',
    status: 'pending',
    requestedBy: 'Supervisor João',
    requestedAt: '2026-01-16T08:30:00'
  },
  {
    id: '3',
    originalEmployee: 'Pedro Souza',
    substituteEmployee: 'Roberto Alves',
    date: '2026-01-15',
    shift: 'Noturno',
    post: 'Segurança Bloco A',
    reason: 'Emergência familiar',
    status: 'completed',
    requestedBy: 'Supervisor Carlos',
    requestedAt: '2026-01-14T22:00:00',
    approvedBy: 'Gerente Pedro'
  },
  {
    id: '4',
    originalEmployee: 'Fernanda Dias',
    substituteEmployee: '-',
    date: '2026-01-18',
    shift: 'Matutino',
    post: 'Limpeza Setor B',
    reason: 'Férias',
    status: 'pending',
    requestedBy: 'Supervisor Maria',
    requestedAt: '2026-01-16T09:00:00'
  }
];

const mockAvailableSubstitutes: AvailableSubstitute[] = [
  {
    id: '1',
    name: 'Carlos Santos',
    department: 'Segurança',
    currentShift: 'Folga',
    skills: ['Portaria', 'Vigilância', 'CFTV'],
    available: true,
    rating: 4.8
  },
  {
    id: '2',
    name: 'Ana Lima',
    department: 'Administrativo',
    currentShift: 'Folga',
    skills: ['Recepção', 'Atendimento', 'Controle de Acesso'],
    available: true,
    rating: 4.5
  },
  {
    id: '3',
    name: 'Roberto Alves',
    department: 'Segurança',
    currentShift: 'Vespertino',
    skills: ['Vigilância', 'Ronda', 'Segurança Patrimonial'],
    available: false,
    rating: 4.2
  },
  {
    id: '4',
    name: 'Luciana Ferreira',
    department: 'Limpeza',
    currentShift: 'Folga',
    skills: ['Limpeza Geral', 'Conservação'],
    available: true,
    rating: 4.6
  }
];

// Chart data
const substitutionsByReason = [
  { name: 'Médico', value: 35, color: '#6366f1' },
  { name: 'Pessoal', value: 25, color: '#8b5cf6' },
  { name: 'Férias', value: 20, color: '#10b981' },
  { name: 'Emergência', value: 15, color: '#f59e0b' },
  { name: 'Outros', value: 5, color: '#ef4444' }
];

const weeklySubstitutions = [
  { day: 'Seg', pending: 3, approved: 8, completed: 5 },
  { day: 'Ter', pending: 2, approved: 6, completed: 7 },
  { day: 'Qua', pending: 4, approved: 5, completed: 6 },
  { day: 'Qui', pending: 5, approved: 7, completed: 4 },
  { day: 'Sex', pending: 3, approved: 9, completed: 8 },
  { day: 'Sáb', pending: 1, approved: 4, completed: 3 },
  { day: 'Dom', pending: 2, approved: 3, completed: 2 }
];

export function SubstitutionsPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showNewSubstitutionModal, setShowNewSubstitutionModal] = useState(false);
  const [selectedSubstitution, setSelectedSubstitution] = useState<Substitution | null>(null);

  // Filter states
  const [filterDepartment, setFilterDepartment] = useState('');

  // Modal form states
  const [newTitular, setNewTitular] = useState('');
  const [newSubstitute, setNewSubstitute] = useState('');
  const [newShift, setNewShift] = useState('');
  const [newReason, setNewReason] = useState('');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <UserCog className="h-4 w-4" /> },
    { value: 'substitutions', label: 'Substituições', icon: <ArrowRightLeft className="h-4 w-4" /> },
    { value: 'available', label: 'Disponíveis', icon: <Users className="h-4 w-4" /> }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending': return <Badge variant="warning">Pendente</Badge>;
      case 'approved': return <Badge variant="success">Aprovado</Badge>;
      case 'rejected': return <Badge variant="danger">Rejeitado</Badge>;
      case 'completed': return <Badge variant="info">Concluído</Badge>;
      default: return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const substitutionColumns: Column<Substitution>[] = [
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-text-muted" />
          <span className="text-text-primary">
            {new Date(row.date).toLocaleDateString('pt-BR')}
          </span>
        </div>
      )
    },
    {
      key: 'originalEmployee',
      header: 'Titular',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.originalEmployee}</p>
          <p className="text-sm text-text-secondary">{row.post}</p>
        </div>
      )
    },
    {
      key: 'substituteEmployee',
      header: 'Substituto',
      render: (row) => (
        row.substituteEmployee !== '-' ? (
          <span className="text-text-primary">{row.substituteEmployee}</span>
        ) : (
          <span className="text-warning italic">Não definido</span>
        )
      )
    },
    {
      key: 'shift',
      header: 'Turno',
      render: (row) => (
        <span className="text-text-secondary">{row.shift}</span>
      )
    },
    {
      key: 'reason',
      header: 'Motivo',
      render: (row) => (
        <span className="text-text-secondary">{row.reason}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedSubstitution(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'pending' && (
            <>
              <Button variant="ghost" size="sm" className="text-success">
                <Check className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="text-danger">
                <X className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      )
    }
  ];

  const availableColumns: Column<AvailableSubstitute>[] = [
    {
      key: 'name',
      header: 'Colaborador',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.department}</p>
          </div>
        </div>
      )
    },
    {
      key: 'currentShift',
      header: 'Turno Atual',
      render: (row) => (
        <span className="text-text-secondary">{row.currentShift}</span>
      )
    },
    {
      key: 'skills',
      header: 'Habilidades',
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          {row.skills.slice(0, 2).map((skill) => (
            <Badge key={skill} variant="outline" size="sm">{skill}</Badge>
          ))}
          {row.skills.length > 2 && (
            <Badge variant="outline" size="sm">+{row.skills.length - 2}</Badge>
          )}
        </div>
      )
    },
    {
      key: 'rating',
      header: 'Avaliação',
      render: (row) => (
        <div className="flex items-center gap-1">
          <span className="text-warning">★</span>
          <span className="text-text-primary">{row.rating.toFixed(1)}</span>
        </div>
      )
    },
    {
      key: 'available',
      header: 'Disponível',
      render: (row) => (
        row.available ? (
          <Badge variant="success">Sim</Badge>
        ) : (
          <Badge variant="neutral">Não</Badge>
        )
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <Button
          variant="outline"
          size="sm"
          disabled={!row.available}
        >
          <UserCog className="h-4 w-4 mr-1" />
          Alocar
        </Button>
      )
    }
  ];

  const filteredSubstitutions = mockSubstitutions.filter(sub => {
    const matchesSearch = sub.originalEmployee.toLowerCase().includes(searchTerm.toLowerCase()) ||
      sub.substituteEmployee.toLowerCase().includes(searchTerm.toLowerCase()) ||
      sub.post.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || sub.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const pendingCount = mockSubstitutions.filter(s => s.status === 'pending').length;
  const approvedCount = mockSubstitutions.filter(s => s.status === 'approved').length;
  const availableCount = mockAvailableSubstitutes.filter(s => s.available).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Substituições
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de substituições de funcionários
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewSubstitutionModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Substituição
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Substituições Hoje"
            value={approvedCount.toString()}
            icon={<UserCog className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Pendentes de Aprovação"
            value={pendingCount.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Aprovadas Este Mês"
            value="89"
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Substitutos Disponíveis"
            value={availableCount.toString()}
            icon={<Users className="h-5 w-5" />}
            iconColor="info"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* By Reason */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Substituições por Motivo
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={substitutionsByReason}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {substitutionsByReason.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Weekly Trend */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Tendência Semanal
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklySubstitutions}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Bar dataKey="pending" name="Pendentes" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="approved" name="Aprovadas" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="completed" name="Concluídas" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Pending Approvals */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Aguardando Aprovação
                </h3>
                <Badge variant="warning">{pendingCount}</Badge>
              </div>
              <div className="space-y-4">
                {mockSubstitutions.filter(s => s.status === 'pending').map((sub) => (
                  <div key={sub.id} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-warning/10 flex items-center justify-center">
                        <ArrowRightLeft className="h-5 w-5 text-warning" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{sub.originalEmployee}</p>
                        <p className="text-sm text-text-secondary">
                          {sub.post} • {new Date(sub.date).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" className="text-success">
                        <Check className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="text-danger">
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Available Substitutes */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Substitutos Disponíveis
                </h3>
                <Badge variant="success">{availableCount}</Badge>
              </div>
              <div className="space-y-4">
                {mockAvailableSubstitutes.filter(s => s.available).slice(0, 4).map((sub) => (
                  <div key={sub.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-success/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-success" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{sub.name}</p>
                        <p className="text-sm text-text-secondary">{sub.department}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-warning">★</span>
                      <span className="text-text-secondary">{sub.rating}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Substitutions Tab */}
        {activeTab === 'substitutions' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar substituição..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={[
                  { value: 'all', label: 'Todos os status' },
                  { value: 'pending', label: 'Pendentes' },
                  { value: 'approved', label: 'Aprovadas' },
                  { value: 'rejected', label: 'Rejeitadas' },
                  { value: 'completed', label: 'Concluídas' }
                ]}
                className="w-40"
              />
              <Input type="date" className="w-40" />
            </div>
            <DataTable
              columns={substitutionColumns}
              data={filteredSubstitutions}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Available Tab */}
        {activeTab === 'available' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar colaborador..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterDepartment}
                onChange={(value) => setFilterDepartment(value)}
                options={[
                  { value: '', label: 'Todos os departamentos' },
                  { value: 'Segurança', label: 'Segurança' },
                  { value: 'Administrativo', label: 'Administrativo' },
                  { value: 'Limpeza', label: 'Limpeza' }
                ]}
                className="w-48"
              />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={availableColumns}
              data={mockAvailableSubstitutes}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Substitution Detail Modal */}
        {selectedSubstitution && (
          <Modal
            isOpen={!!selectedSubstitution}
            onClose={() => setSelectedSubstitution(null)}
            title="Detalhes da Substituição"
            size="md"
          >
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-xl bg-primary/10 flex items-center justify-center">
                  <ArrowRightLeft className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-text-primary">{selectedSubstitution.originalEmployee}</span>
                    <ArrowRightLeft className="h-4 w-4 text-text-muted" />
                    <span className="font-medium text-text-primary">{selectedSubstitution.substituteEmployee}</span>
                  </div>
                  <p className="text-text-secondary">{selectedSubstitution.post}</p>
                  <div className="mt-1">{getStatusBadge(selectedSubstitution.status)}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Data</p>
                  <p className="font-medium text-text-primary">
                    {new Date(selectedSubstitution.date).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Turno</p>
                  <p className="font-medium text-text-primary">{selectedSubstitution.shift}</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-secondary mb-1">Motivo</p>
                <p className="text-text-primary">{selectedSubstitution.reason}</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">Solicitado por:</span>
                  <span className="text-text-primary">{selectedSubstitution.requestedBy}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">Data da solicitação:</span>
                  <span className="text-text-primary">
                    {new Date(selectedSubstitution.requestedAt).toLocaleString('pt-BR')}
                  </span>
                </div>
                {selectedSubstitution.approvedBy && (
                  <div className="flex items-center justify-between">
                    <span className="text-text-secondary">Aprovado por:</span>
                    <span className="text-text-primary">{selectedSubstitution.approvedBy}</span>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedSubstitution(null)}>
                  Fechar
                </Button>
                {selectedSubstitution.status === 'pending' && (
                  <>
                    <Button variant="outline" className="text-danger border-danger">
                      <X className="h-4 w-4 mr-2" />
                      Rejeitar
                    </Button>
                    <Button>
                      <Check className="h-4 w-4 mr-2" />
                      Aprovar
                    </Button>
                  </>
                )}
              </div>
            </div>
          </Modal>
        )}

        {/* New Substitution Modal */}
        <Modal
          isOpen={showNewSubstitutionModal}
          onClose={() => setShowNewSubstitutionModal(false)}
          title="Nova Substituição"
          size="md"
        >
          <div className="space-y-4">
            <Select
              value={newTitular}
              onChange={(value) => setNewTitular(value)}
              options={[
                { value: '', label: 'Selecione o funcionário titular' },
                { value: '1', label: 'João Silva' },
                { value: '2', label: 'Maria Costa' },
                { value: '3', label: 'Pedro Souza' }
              ]}
              className="w-full"
            />
            <Select
              value={newSubstitute}
              onChange={(value) => setNewSubstitute(value)}
              options={[
                { value: '', label: 'Selecione o substituto' },
                ...mockAvailableSubstitutes.filter(s => s.available).map(s => ({ value: s.id, label: s.name }))
              ]}
              className="w-full"
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data" type="date" />
              <Select
                value={newShift}
                onChange={(value) => setNewShift(value)}
                options={[
                  { value: '', label: 'Selecione o turno' },
                  { value: 'morning', label: 'Matutino' },
                  { value: 'afternoon', label: 'Vespertino' },
                  { value: 'night', label: 'Noturno' }
                ]}
                className="w-full"
              />
            </div>
            <Select
              value={newReason}
              onChange={(value) => setNewReason(value)}
              options={[
                { value: '', label: 'Selecione o motivo' },
                { value: 'medical', label: 'Consulta médica' },
                { value: 'personal', label: 'Licença pessoal' },
                { value: 'vacation', label: 'Férias' },
                { value: 'emergency', label: 'Emergência' },
                { value: 'other', label: 'Outros' }
              ]}
              className="w-full"
            />
            <Input label="Observações" placeholder="Informações adicionais (opcional)" />
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewSubstitutionModal(false)}>
                Cancelar
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Criar Substituição
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
