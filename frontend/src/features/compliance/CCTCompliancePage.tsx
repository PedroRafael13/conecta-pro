'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Scale,
  Search,
  Calculator,
  FileText,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  DollarSign,
  Users,
  Briefcase,
  TrendingUp,
  Download,
  RefreshCw,
  Info,
  Clock,
  Building2,
  FileSpreadsheet,
  BadgeCheck,
  AlertCircle,
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
} from '@/design-system/components';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

// Types
interface Cargo {
  id: string;
  codigo: string;
  nome: string;
  pisoSalarial: number;
  vigencia: string;
  reajuste: number;
  categoria: 'operacional' | 'administrativo' | 'supervisao' | 'gerencia';
  cargaHoraria: string;
  beneficiosObrigatorios: string[];
}

interface ValidacaoSalario {
  id: string;
  funcionario: string;
  cargo: string;
  salarioAtual: number;
  pisoSalarial: number;
  status: 'conforme' | 'abaixo_piso' | 'pendente';
  diferenca: number;
  dataVerificacao: string;
}

interface CustoFuncionario {
  id: string;
  cargo: string;
  salarioBase: number;
  encargos: number;
  beneficios: number;
  custoTotal: number;
  margemSugerida: number;
  valorFaturamento: number;
}

interface PropostaComercial {
  id: string;
  cliente: string;
  cargos: { cargo: string; quantidade: number; valorUnitario: number }[];
  valorTotal: number;
  margem: number;
  status: 'rascunho' | 'enviada' | 'aprovada' | 'rejeitada';
  dataCriacao: string;
}

// Mock Data
const cargos: Cargo[] = [
  {
    id: '1',
    codigo: 'VIG_PAT',
    nome: 'Vigilante Patrimonial',
    pisoSalarial: 2145.00,
    vigencia: 'SINDCOND 2026',
    reajuste: 7.1,
    categoria: 'operacional',
    cargaHoraria: '12x36',
    beneficiosObrigatorios: ['Vale Transporte', 'Vale Alimentacao', 'Uniforme'],
  },
  {
    id: '2',
    codigo: 'PORT_12',
    nome: 'Porteiro 12x36',
    pisoSalarial: 1980.00,
    vigencia: 'SINDCOND 2026',
    reajuste: 7.1,
    categoria: 'operacional',
    cargaHoraria: '12x36',
    beneficiosObrigatorios: ['Vale Transporte', 'Vale Alimentacao'],
  },
  {
    id: '3',
    codigo: 'PORT_44',
    nome: 'Porteiro 44h',
    pisoSalarial: 1850.00,
    vigencia: 'SINDCOND 2026',
    reajuste: 7.1,
    categoria: 'operacional',
    cargaHoraria: '44h_semanais',
    beneficiosObrigatorios: ['Vale Transporte', 'Vale Alimentacao'],
  },
  {
    id: '4',
    codigo: 'ZEL_12',
    nome: 'Zelador 12x36',
    pisoSalarial: 1920.00,
    vigencia: 'SINDCOND 2026',
    reajuste: 7.1,
    categoria: 'operacional',
    cargaHoraria: '12x36',
    beneficiosObrigatorios: ['Vale Transporte', 'Vale Alimentacao'],
  },
  {
    id: '5',
    codigo: 'LIMP_44',
    nome: 'Auxiliar de Limpeza 44h',
    pisoSalarial: 1520.00,
    vigencia: 'SINDCOND 2026',
    reajuste: 7.1,
    categoria: 'operacional',
    cargaHoraria: '44h_semanais',
    beneficiosObrigatorios: ['Vale Transporte', 'Vale Alimentacao'],
  },
  {
    id: '6',
    codigo: 'SUP_OP',
    nome: 'Supervisor Operacional',
    pisoSalarial: 3200.00,
    vigencia: 'SINDCOND 2026',
    reajuste: 7.1,
    categoria: 'supervisao',
    cargaHoraria: '44h_semanais',
    beneficiosObrigatorios: ['Vale Transporte', 'Vale Alimentacao', 'Plano de Saude'],
  },
];

const validacoes: ValidacaoSalario[] = [
  {
    id: '1',
    funcionario: 'Jose da Silva',
    cargo: 'Porteiro 12x36',
    salarioAtual: 1980.00,
    pisoSalarial: 1980.00,
    status: 'conforme',
    diferenca: 0,
    dataVerificacao: '2026-01-15',
  },
  {
    id: '2',
    funcionario: 'Maria Santos',
    cargo: 'Auxiliar de Limpeza 44h',
    salarioAtual: 1450.00,
    pisoSalarial: 1520.00,
    status: 'abaixo_piso',
    diferenca: -70.00,
    dataVerificacao: '2026-01-15',
  },
  {
    id: '3',
    funcionario: 'Carlos Oliveira',
    cargo: 'Vigilante Patrimonial',
    salarioAtual: 2200.00,
    pisoSalarial: 2145.00,
    status: 'conforme',
    diferenca: 55.00,
    dataVerificacao: '2026-01-15',
  },
  {
    id: '4',
    funcionario: 'Ana Pereira',
    cargo: 'Zelador 12x36',
    salarioAtual: 1920.00,
    pisoSalarial: 1920.00,
    status: 'conforme',
    diferenca: 0,
    dataVerificacao: '2026-01-15',
  },
];

const custos: CustoFuncionario[] = [
  {
    id: '1',
    cargo: 'Porteiro 12x36',
    salarioBase: 1980.00,
    encargos: 1584.00,
    beneficios: 650.00,
    custoTotal: 4214.00,
    margemSugerida: 15,
    valorFaturamento: 4846.10,
  },
  {
    id: '2',
    cargo: 'Vigilante Patrimonial',
    salarioBase: 2145.00,
    encargos: 1716.00,
    beneficios: 780.00,
    custoTotal: 4641.00,
    margemSugerida: 15,
    valorFaturamento: 5337.15,
  },
  {
    id: '3',
    cargo: 'Auxiliar de Limpeza 44h',
    salarioBase: 1520.00,
    encargos: 1216.00,
    beneficios: 520.00,
    custoTotal: 3256.00,
    margemSugerida: 15,
    valorFaturamento: 3744.40,
  },
];

const propostas: PropostaComercial[] = [
  {
    id: '1',
    cliente: 'Condominio Parque das Flores',
    cargos: [
      { cargo: 'Porteiro 12x36', quantidade: 4, valorUnitario: 4846.10 },
      { cargo: 'Zelador 12x36', quantidade: 2, valorUnitario: 4520.00 },
    ],
    valorTotal: 28424.40,
    margem: 15,
    status: 'aprovada',
    dataCriacao: '2026-01-10',
  },
  {
    id: '2',
    cliente: 'Edificio Central Business',
    cargos: [
      { cargo: 'Vigilante Patrimonial', quantidade: 6, valorUnitario: 5337.15 },
      { cargo: 'Porteiro 12x36', quantidade: 4, valorUnitario: 4846.10 },
    ],
    valorTotal: 51407.30,
    margem: 18,
    status: 'enviada',
    dataCriacao: '2026-01-12',
  },
];

// Chart data
const evolucaoPisos = [
  { ano: '2022', vigilante: 1820, porteiro: 1680, zelador: 1620 },
  { ano: '2023', vigilante: 1920, porteiro: 1780, zelador: 1720 },
  { ano: '2024', vigilante: 1980, porteiro: 1840, zelador: 1780 },
  { ano: '2025', vigilante: 2005, porteiro: 1850, zelador: 1795 },
  { ano: '2026', vigilante: 2145, porteiro: 1980, zelador: 1920 },
];

const distribuicaoCargos = [
  { name: 'Porteiro', value: 45, color: '#2563eb' },
  { name: 'Vigilante', value: 25, color: '#16a34a' },
  { name: 'Zelador', value: 15, color: '#ca8a04' },
  { name: 'Limpeza', value: 10, color: '#dc2626' },
  { name: 'Supervisao', value: 5, color: '#7c3aed' },
];

const statusConfig = {
  conforme: { label: 'Conforme', variant: 'success' as const, icon: CheckCircle2 },
  abaixo_piso: { label: 'Abaixo do Piso', variant: 'danger' as const, icon: XCircle },
  pendente: { label: 'Pendente', variant: 'warning' as const, icon: AlertTriangle },
  rascunho: { label: 'Rascunho', variant: 'neutral' as const, icon: FileText },
  enviada: { label: 'Enviada', variant: 'info' as const, icon: Clock },
  aprovada: { label: 'Aprovada', variant: 'success' as const, icon: CheckCircle2 },
  rejeitada: { label: 'Rejeitada', variant: 'danger' as const, icon: XCircle },
};

const categoriaConfig = {
  operacional: { label: 'Operacional', variant: 'info' as const },
  administrativo: { label: 'Administrativo', variant: 'neutral' as const },
  supervisao: { label: 'Supervisao', variant: 'warning' as const },
  gerencia: { label: 'Gerencia', variant: 'success' as const },
};

export function CCTCompliancePage() {
  const [activeTab, setActiveTab] = useState('cargos');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCalculadoraModal, setShowCalculadoraModal] = useState(false);
  const [selectedCargo, setSelectedCargo] = useState<Cargo | null>(null);

  // Calculadora state
  const [calcCargo, setCalcCargo] = useState('');
  const [calcSalario, setCalcSalario] = useState('');
  const [calcJornada, setCalcJornada] = useState('12x36');
  const [calcMargem, setCalcMargem] = useState('15');

  const tabs = [
    { value: 'cargos', label: 'Tabela de Cargos', icon: <Briefcase className="w-4 h-4" /> },
    { value: 'validacao', label: 'Validacao Salarial', icon: <Scale className="w-4 h-4" /> },
    { value: 'custos', label: 'Calculadora de Custos', icon: <Calculator className="w-4 h-4" /> },
    { value: 'propostas', label: 'Propostas Comerciais', icon: <FileSpreadsheet className="w-4 h-4" /> },
  ];

  const cargoColumns: Column<Cargo>[] = [
    {
      key: 'codigo',
      header: 'Codigo',
      render: (row) => (
        <span className="font-mono text-sm bg-bg-tertiary px-2 py-1 rounded">
          {row.codigo}
        </span>
      ),
    },
    { key: 'nome', header: 'Cargo' },
    {
      key: 'pisoSalarial',
      header: 'Piso Salarial',
      render: (row) => (
        <span className="font-semibold text-success">
          R$ {row.pisoSalarial.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'reajuste',
      header: 'Reajuste',
      render: (row) => (
        <Badge variant="info" size="sm">
          +{row.reajuste}%
        </Badge>
      ),
    },
    {
      key: 'categoria',
      header: 'Categoria',
      render: (row) => (
        <Badge variant={categoriaConfig[row.categoria].variant} size="sm">
          {categoriaConfig[row.categoria].label}
        </Badge>
      ),
    },
    { key: 'cargaHoraria', header: 'Carga Horaria' },
    {
      key: 'vigencia',
      header: 'Vigencia',
      render: (row) => (
        <Badge variant="success" size="sm">
          {row.vigencia}
        </Badge>
      ),
    },
  ];

  const validacaoColumns: Column<ValidacaoSalario>[] = [
    { key: 'funcionario', header: 'Funcionario' },
    { key: 'cargo', header: 'Cargo' },
    {
      key: 'salarioAtual',
      header: 'Salario Atual',
      render: (row) => `R$ ${row.salarioAtual.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'pisoSalarial',
      header: 'Piso CCT',
      render: (row) => `R$ ${row.pisoSalarial.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'diferenca',
      header: 'Diferenca',
      render: (row) => (
        <span className={row.diferenca >= 0 ? 'text-success' : 'text-danger font-semibold'}>
          {row.diferenca >= 0 ? '+' : ''}R$ {row.diferenca.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = statusConfig[row.status];
        const Icon = config.icon;
        return (
          <Badge variant={config.variant} size="sm">
            <Icon className="w-3 h-3 mr-1" />
            {config.label}
          </Badge>
        );
      },
    },
  ];

  const custoColumns: Column<CustoFuncionario>[] = [
    { key: 'cargo', header: 'Cargo' },
    {
      key: 'salarioBase',
      header: 'Salario Base',
      render: (row) => `R$ ${row.salarioBase.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'encargos',
      header: 'Encargos (80%)',
      render: (row) => `R$ ${row.encargos.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'beneficios',
      header: 'Beneficios',
      render: (row) => `R$ ${row.beneficios.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
    {
      key: 'custoTotal',
      header: 'Custo Total',
      render: (row) => (
        <span className="font-semibold">
          R$ {row.custoTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'valorFaturamento',
      header: 'Valor Faturamento',
      render: (row) => (
        <span className="font-semibold text-success">
          R$ {row.valorFaturamento.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
  ];

  const propostaColumns: Column<PropostaComercial>[] = [
    { key: 'cliente', header: 'Cliente' },
    {
      key: 'cargos',
      header: 'Composicao',
      render: (row) => (
        <span className="text-sm text-text-secondary">
          {row.cargos.map(c => `${c.quantidade}x ${c.cargo}`).join(', ')}
        </span>
      ),
    },
    {
      key: 'valorTotal',
      header: 'Valor Total',
      render: (row) => (
        <span className="font-semibold">
          R$ {row.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'margem',
      header: 'Margem',
      render: (row) => <Badge variant="info" size="sm">{row.margem}%</Badge>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = statusConfig[row.status];
        const Icon = config.icon;
        return (
          <Badge variant={config.variant} size="sm">
            <Icon className="w-3 h-3 mr-1" />
            {config.label}
          </Badge>
        );
      },
    },
    {
      key: 'dataCriacao',
      header: 'Data',
      render: (row) => new Date(row.dataCriacao).toLocaleDateString('pt-BR'),
    },
  ];

  const conformes = validacoes.filter(v => v.status === 'conforme').length;
  const abaixoPiso = validacoes.filter(v => v.status === 'abaixo_piso').length;
  const totalValidacoes = validacoes.length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
              <Scale className="w-7 h-7 text-primary" />
              CCT Compliance - SINDCOND 2026
            </h1>
            <p className="text-text-secondary mt-1">
              Gestao de pisos salariais e compliance trabalhista
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              leftIcon={<Download className="w-4 h-4" />}
            >
              Exportar Tabela
            </Button>
            <Button
              variant="outline"
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              Atualizar CCT
            </Button>
            <Button
              variant="primary"
              leftIcon={<Calculator className="w-4 h-4" />}
              onClick={() => setShowCalculadoraModal(true)}
            >
              Calcular Custo
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <StatCard
            title="Piso Medio"
            value="R$ 1.920"
            icon={<DollarSign className="w-5 h-5" />}
            change={7.1}
            changeLabel="reajuste 2026"
            iconColor="primary"
          />
          <StatCard
            title="Funcionarios Validados"
            value={`${conformes}/${totalValidacoes}`}
            icon={<BadgeCheck className="w-5 h-5" />}
            change={Math.round((conformes/totalValidacoes)*100)}
            changeLabel="conformes"
            iconColor="success"
          />
          <StatCard
            title="Alertas de Piso"
            value={abaixoPiso.toString()}
            icon={<AlertCircle className="w-5 h-5" />}
            change={-abaixoPiso}
            changeLabel="abaixo do piso"
            iconColor="danger"
          />
          <StatCard
            title="Propostas Ativas"
            value={propostas.filter(p => p.status === 'enviada').length.toString()}
            icon={<FileSpreadsheet className="w-5 h-5" />}
            change={12}
            changeLabel="este mes"
            iconColor="info"
          />
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="Evolucao dos Pisos Salariais"
              subtitle="Historico de reajustes CCT"
            />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={evolucaoPisos}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="ano" stroke="#6b7280" fontSize={12} />
                    <YAxis stroke="#6b7280" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => [`R$ ${value.toLocaleString('pt-BR')}`, '']}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="vigilante"
                      name="Vigilante"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={{ fill: '#2563eb' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="porteiro"
                      name="Porteiro"
                      stroke="#16a34a"
                      strokeWidth={2}
                      dot={{ fill: '#16a34a' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="zelador"
                      name="Zelador"
                      stroke="#ca8a04"
                      strokeWidth={2}
                      dot={{ fill: '#ca8a04' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Distribuicao por Cargo"
              subtitle="Percentual de funcionarios"
            />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={distribuicaoCargos}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {distribuicaoCargos.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`${value}%`, 'Participacao']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <Card>
          <CardHeader
            title=""
            action={
              <div className="flex items-center gap-4 w-full">
                <SimpleTabBar
                  tabs={tabs}
                  value={activeTab}
                  onChange={setActiveTab}
                />
                <div className="flex-1" />
                <div className="relative w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                  <Input
                    placeholder="Buscar..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
            }
          />
          <CardBody className="p-0">
            {activeTab === 'cargos' && (
              <DataTable
                columns={cargoColumns}
                data={cargos.filter(c =>
                  c.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  c.codigo.toLowerCase().includes(searchTerm.toLowerCase())
                )}
                onRowClick={(row) => setSelectedCargo(row)}
              />
            )}

            {activeTab === 'validacao' && (
              <div>
                <div className="p-4 bg-warning/10 border-b border-warning/20">
                  <div className="flex items-center gap-2 text-warning">
                    <AlertTriangle className="w-5 h-5" />
                    <span className="font-medium">
                      {abaixoPiso} funcionario(s) com salario abaixo do piso CCT
                    </span>
                  </div>
                </div>
                <DataTable
                  columns={validacaoColumns}
                  data={validacoes.filter(v =>
                    v.funcionario.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    v.cargo.toLowerCase().includes(searchTerm.toLowerCase())
                  )}
                />
              </div>
            )}

            {activeTab === 'custos' && (
              <DataTable
                columns={custoColumns}
                data={custos.filter(c =>
                  c.cargo.toLowerCase().includes(searchTerm.toLowerCase())
                )}
              />
            )}

            {activeTab === 'propostas' && (
              <DataTable
                columns={propostaColumns}
                data={propostas.filter(p =>
                  p.cliente.toLowerCase().includes(searchTerm.toLowerCase())
                )}
              />
            )}
          </CardBody>
        </Card>

        {/* Info Card */}
        <Card>
          <CardBody>
            <div className="flex items-start gap-4">
              <div className="p-3 bg-info/10 rounded-lg">
                <Info className="w-6 h-6 text-info" />
              </div>
              <div>
                <h3 className="font-semibold text-text-primary mb-1">
                  Convencao Coletiva de Trabalho - SINDCOND 2026
                </h3>
                <p className="text-text-secondary text-sm">
                  Os valores apresentados sao baseados na CCT SINDCOND 2026 com vigencia de 01/01/2026 a 31/12/2026.
                  O reajuste de 7.1% foi aplicado sobre os pisos de 2025. Esta ferramenta auxilia na validacao
                  de compliance salarial e calculo de custos para propostas comerciais.
                </p>
                <div className="flex items-center gap-4 mt-3">
                  <Badge variant="success">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Vigente
                  </Badge>
                  <span className="text-sm text-text-muted">
                    Ultima atualizacao: 01/01/2026
                  </span>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Calculadora Modal */}
        <Modal
          isOpen={showCalculadoraModal}
          onClose={() => setShowCalculadoraModal(false)}
          title="Calculadora de Custo de Funcionario"
          size="md"
        >
          <div className="space-y-4">
            <Select
              label="Cargo"
              value={calcCargo}
              onChange={(value) => setCalcCargo(value)}
              options={[
                { value: '', label: 'Selecione um cargo' },
                ...cargos.map(c => ({ value: c.codigo, label: c.nome }))
              ]}
            />

            <Input
              label="Salario Base (opcional)"
              type="number"
              placeholder="Usar piso se vazio"
              value={calcSalario}
              onChange={(e) => setCalcSalario(e.target.value)}
            />

            <Select
              label="Jornada"
              value={calcJornada}
              onChange={(value) => setCalcJornada(value)}
              options={[
                { value: '12x36', label: '12x36' },
                { value: '44h_semanais', label: '44h Semanais' },
                { value: '36h_semanais', label: '36h Semanais' },
              ]}
            />

            <Input
              label="Margem de Lucro (%)"
              type="number"
              value={calcMargem}
              onChange={(e) => setCalcMargem(e.target.value)}
            />

            {calcCargo && (
              <div className="p-4 bg-bg-secondary rounded-lg space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Salario Base:</span>
                  <span className="font-medium">
                    R$ {(parseFloat(calcSalario) || cargos.find(c => c.codigo === calcCargo)?.pisoSalarial || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Encargos (80%):</span>
                  <span className="font-medium">
                    R$ {((parseFloat(calcSalario) || cargos.find(c => c.codigo === calcCargo)?.pisoSalarial || 0) * 0.8).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Beneficios (estimado):</span>
                  <span className="font-medium">R$ 650,00</span>
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Custo Total:</span>
                    <span className="font-bold text-lg">
                      R$ {(((parseFloat(calcSalario) || cargos.find(c => c.codigo === calcCargo)?.pisoSalarial || 0) * 1.8) + 650).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex justify-between mt-1">
                    <span className="font-medium text-success">Valor Faturamento:</span>
                    <span className="font-bold text-lg text-success">
                      R$ {((((parseFloat(calcSalario) || cargos.find(c => c.codigo === calcCargo)?.pisoSalarial || 0) * 1.8) + 650) * (1 + parseFloat(calcMargem || '15') / 100)).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowCalculadoraModal(false)}>
                Fechar
              </Button>
              <Button variant="primary" leftIcon={<FileSpreadsheet className="w-4 h-4" />}>
                Gerar Proposta
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}

export default CCTCompliancePage;
