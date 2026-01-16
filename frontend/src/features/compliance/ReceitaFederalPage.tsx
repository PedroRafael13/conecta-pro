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
  Modal
} from '@/design-system/components';
import {
  Building2,
  FileText,
  Send,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Download,
  Upload,
  RefreshCw,
  Calendar,
  DollarSign,
  FileCheck,
  BarChart2,
  Users,
  Shield,
  Eye,
  Info
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend
} from 'recharts';

interface Obrigacao {
  id: string;
  nome: string;
  codigo: string;
  competencia: string;
  vencimento: string;
  valor: number;
  status: 'pendente' | 'transmitida' | 'processada' | 'erro' | 'atrasada';
  tipo: 'mensal' | 'trimestral' | 'anual';
  categoria: 'tributo' | 'declaracao' | 'contribuicao';
}

interface ConsultaCNPJ {
  cnpj: string;
  razaoSocial: string;
  situacao: string;
  dataAbertura: string;
  naturezaJuridica: string;
  capitalSocial: number;
  atividadePrincipal: string;
  endereco: string;
}

const mockObrigacoes: Obrigacao[] = [
  {
    id: '1',
    nome: 'DCTF Mensal',
    codigo: 'DCTF',
    competencia: 'Janeiro/2024',
    vencimento: '2024-02-15',
    valor: 0,
    status: 'pendente',
    tipo: 'mensal',
    categoria: 'declaracao'
  },
  {
    id: '2',
    nome: 'EFD-Contribuições',
    codigo: 'EFD',
    competencia: 'Janeiro/2024',
    vencimento: '2024-02-14',
    valor: 0,
    status: 'transmitida',
    tipo: 'mensal',
    categoria: 'declaracao'
  },
  {
    id: '3',
    nome: 'IRPJ/CSLL',
    codigo: 'IRPJ',
    competencia: '4º Trim/2023',
    vencimento: '2024-01-31',
    valor: 45680.00,
    status: 'processada',
    tipo: 'trimestral',
    categoria: 'tributo'
  },
  {
    id: '4',
    nome: 'PIS/COFINS',
    codigo: 'PIS-COFINS',
    competencia: 'Janeiro/2024',
    vencimento: '2024-02-25',
    valor: 32450.00,
    status: 'pendente',
    tipo: 'mensal',
    categoria: 'contribuicao'
  },
  {
    id: '5',
    nome: 'DIRF',
    codigo: 'DIRF',
    competencia: 'Ano 2023',
    vencimento: '2024-02-28',
    valor: 0,
    status: 'pendente',
    tipo: 'anual',
    categoria: 'declaracao'
  },
  {
    id: '6',
    nome: 'ECF',
    codigo: 'ECF',
    competencia: 'Ano 2023',
    vencimento: '2024-07-31',
    valor: 0,
    status: 'pendente',
    tipo: 'anual',
    categoria: 'declaracao'
  }
];

const mockChartData = [
  { mes: 'Jul', tributos: 125000, declaracoes: 6 },
  { mes: 'Ago', tributos: 132000, declaracoes: 5 },
  { mes: 'Set', tributos: 128000, declaracoes: 6 },
  { mes: 'Out', tributos: 145000, declaracoes: 5 },
  { mes: 'Nov', tributos: 138000, declaracoes: 6 },
  { mes: 'Dez', tributos: 156000, declaracoes: 8 }
];

const mockCNPJResult: ConsultaCNPJ = {
  cnpj: '12.345.678/0001-90',
  razaoSocial: 'CONECTA PRO SERVIÇOS ESPECIALIZADOS LTDA',
  situacao: 'ATIVA',
  dataAbertura: '15/03/2018',
  naturezaJuridica: '206-2 - Sociedade Empresária Limitada',
  capitalSocial: 500000,
  atividadePrincipal: '80.11-1-01 - Atividades de vigilância e segurança privada',
  endereco: 'Av. Paulista, 1000 - Bela Vista - São Paulo/SP - 01310-100'
};

const tabs = [
  { value: 'obrigacoes', label: 'Obrigações', icon: <Calendar className="h-4 w-4" /> },
  { value: 'consultas', label: 'Consultas', icon: <FileCheck className="h-4 w-4" /> },
  { value: 'certidoes', label: 'Certidões', icon: <Shield className="h-4 w-4" /> },
  { value: 'relatorios', label: 'Relatórios', icon: <BarChart2 className="h-4 w-4" /> }
];

export function ReceitaFederalPage() {
  const [activeTab, setActiveTab] = useState('obrigacoes');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedObrigacao, setSelectedObrigacao] = useState<Obrigacao | null>(null);
  const [searchCNPJ, setSearchCNPJ] = useState('');
  const [cnpjResult, setCnpjResult] = useState<ConsultaCNPJ | null>(null);

  const handleSearchCNPJ = () => {
    // Simular consulta
    setCnpjResult(mockCNPJResult);
  };

  const columns: Column<Obrigacao>[] = [
    {
      key: 'nome',
      header: 'Obrigação',
      render: (ob) => (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            ob.categoria === 'tributo' ? 'bg-red-500/10' :
            ob.categoria === 'declaracao' ? 'bg-blue-500/10' :
            'bg-purple-500/10'
          }`}>
            {ob.categoria === 'tributo' && <DollarSign className="h-5 w-5 text-red-400" />}
            {ob.categoria === 'declaracao' && <FileText className="h-5 w-5 text-blue-400" />}
            {ob.categoria === 'contribuicao' && <Building2 className="h-5 w-5 text-purple-400" />}
          </div>
          <div>
            <span className="font-medium text-text-primary">{ob.nome}</span>
            <p className="text-sm text-text-secondary">{ob.codigo}</p>
          </div>
        </div>
      )
    },
    {
      key: 'competencia',
      header: 'Competência',
      render: (ob) => (
        <span className="text-text-primary">{ob.competencia}</span>
      )
    },
    {
      key: 'vencimento',
      header: 'Vencimento',
      render: (ob) => {
        const venc = new Date(ob.vencimento);
        const hoje = new Date();
        const isAtrasado = venc < hoje && ob.status === 'pendente';
        return (
          <span className={isAtrasado ? 'text-red-400' : 'text-text-secondary'}>
            {venc.toLocaleDateString('pt-BR')}
          </span>
        );
      }
    },
    {
      key: 'valor',
      header: 'Valor',
      render: (ob) => (
        <span className="font-medium text-text-primary">
          {ob.valor > 0
            ? ob.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
            : '-'}
        </span>
      )
    },
    {
      key: 'tipo',
      header: 'Periodicidade',
      render: (ob) => (
        <Badge variant="info">
          {ob.tipo === 'mensal' ? 'Mensal' :
           ob.tipo === 'trimestral' ? 'Trimestral' : 'Anual'}
        </Badge>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (ob) => (
        <Badge variant={
          ob.status === 'processada' ? 'success' :
          ob.status === 'transmitida' ? 'primary' :
          ob.status === 'pendente' ? 'warning' :
          ob.status === 'atrasada' ? 'danger' : 'danger'
        }>
          <span className="flex items-center gap-1">
            {ob.status === 'processada' && <CheckCircle className="h-3 w-3" />}
            {ob.status === 'transmitida' && <Send className="h-3 w-3" />}
            {ob.status === 'pendente' && <Clock className="h-3 w-3" />}
            {ob.status === 'erro' && <XCircle className="h-3 w-3" />}
            {ob.status === 'atrasada' && <AlertTriangle className="h-3 w-3" />}
            {ob.status === 'processada' ? 'Processada' :
             ob.status === 'transmitida' ? 'Transmitida' :
             ob.status === 'pendente' ? 'Pendente' :
             ob.status === 'atrasada' ? 'Atrasada' : 'Erro'}
          </span>
        </Badge>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (ob) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedObrigacao(ob);
              setShowDetailModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {ob.status === 'pendente' && (
            <Button variant="ghost" size="sm">
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Receita Federal</h1>
            <p className="text-text-secondary mt-1">Obrigações acessórias e consultas junto à RFB</p>
          </div>
          <div className="flex items-center gap-3">
            {
            <div className="flex items-center gap-3">
              <Button variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Sincronizar
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Button>
                <Send className="h-4 w-4 mr-2" />
                Transmitir Pendentes
              </Button>
            </div>
          }
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Obrigações Pendentes"
            value="4"
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
            change={-2}
            changeLabel="vs mês anterior"
          />
          <StatCard
            title="Tributos a Pagar"
            value="R$ 78K"
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="danger"
            change={12}
            changeLabel="próximos 30 dias"
          />
          <StatCard
            title="Certidões Válidas"
            value="3/3"
            icon={<Shield className="h-5 w-5" />}
            iconColor="success"
            change={0}
            changeLabel="todas válidas"
          />
          <StatCard
            title="Taxa de Conformidade"
            value="98.5%"
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
            change={1.2}
            changeLabel="vs ano anterior"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Content */}
        {activeTab === 'obrigacoes' && (
          <div className="space-y-6">
            {/* Calendar Alert */}
            <Card className="p-4 bg-amber-500/10 border-amber-500/20">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-400" />
                <div>
                  <span className="font-medium text-amber-400">Próximos Vencimentos</span>
                  <p className="text-sm text-text-secondary">
                    2 obrigações vencem nos próximos 7 dias: EFD-Contribuições (14/02) e DCTF (15/02)
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <DataTable<Obrigacao>
                data={mockObrigacoes}
                columns={columns}
                keyExtractor={(row) => row.id}
              />
            </Card>
          </div>
        )}

        {activeTab === 'consultas' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Consulta CNPJ
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    CNPJ para Consulta
                  </label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="00.000.000/0000-00"
                      value={searchCNPJ}
                      onChange={(e) => setSearchCNPJ(e.target.value)}
                      className="flex-1"
                    />
                    <Button onClick={handleSearchCNPJ}>
                      Consultar
                    </Button>
                  </div>
                </div>

                {cnpjResult && (
                  <div className="mt-4 p-4 bg-bg-tertiary rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-text-primary">{cnpjResult.razaoSocial}</h4>
                      <Badge variant="success">{cnpjResult.situacao}</Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-text-secondary">CNPJ</span>
                        <p className="text-text-primary">{cnpjResult.cnpj}</p>
                      </div>
                      <div>
                        <span className="text-text-secondary">Data de Abertura</span>
                        <p className="text-text-primary">{cnpjResult.dataAbertura}</p>
                      </div>
                      <div>
                        <span className="text-text-secondary">Natureza Jurídica</span>
                        <p className="text-text-primary">{cnpjResult.naturezaJuridica}</p>
                      </div>
                      <div>
                        <span className="text-text-secondary">Capital Social</span>
                        <p className="text-text-primary">
                          {cnpjResult.capitalSocial.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </p>
                      </div>
                    </div>
                    <div>
                      <span className="text-text-secondary text-sm">Atividade Principal</span>
                      <p className="text-text-primary">{cnpjResult.atividadePrincipal}</p>
                    </div>
                    <div>
                      <span className="text-text-secondary text-sm">Endereço</span>
                      <p className="text-text-primary">{cnpjResult.endereco}</p>
                    </div>
                  </div>
                )}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Outras Consultas
              </h3>
              <div className="space-y-3">
                {[
                  { name: 'Situação Fiscal', desc: 'Consulta débitos e pendências', icon: FileCheck },
                  { name: 'CPF/CNPJ', desc: 'Validar documentos de terceiros', icon: Users },
                  { name: 'Simples Nacional', desc: 'Verificar enquadramento', icon: Building2 },
                  { name: 'Parcelamentos', desc: 'Status de parcelamentos ativos', icon: Calendar },
                  { name: 'e-CAC', desc: 'Acesso ao portal da Receita', icon: Shield }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <item.icon className="h-5 w-5 text-accent-primary" />
                      <div>
                        <span className="text-text-primary">{item.name}</span>
                        <p className="text-sm text-text-secondary">{item.desc}</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Acessar
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'certidoes' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                nome: 'CND Federal',
                orgao: 'Receita Federal',
                validade: '15/04/2024',
                status: 'valid',
                emissao: '15/10/2023'
              },
              {
                nome: 'CRF FGTS',
                orgao: 'Caixa Econômica',
                validade: '28/02/2024',
                status: 'valid',
                emissao: '28/11/2023'
              },
              {
                nome: 'CNDT',
                orgao: 'Justiça do Trabalho',
                validade: '20/03/2024',
                status: 'valid',
                emissao: '20/09/2023'
              }
            ].map((cert, idx) => (
              <Card key={idx} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-green-500/10 rounded-lg">
                    <Shield className="h-6 w-6 text-green-400" />
                  </div>
                  <Badge variant="success">Válida</Badge>
                </div>
                <h3 className="font-semibold text-text-primary">{cert.nome}</h3>
                <p className="text-sm text-text-secondary">{cert.orgao}</p>
                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Emissão</span>
                    <span className="text-text-primary">{cert.emissao}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Validade</span>
                    <span className="text-green-400">{cert.validade}</span>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-border-subtle flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-4 w-4 mr-1" />
                    Ver
                  </Button>
                  <Button size="sm" className="flex-1">
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Renovar
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'relatorios' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="lg:col-span-2 p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Tributos Pagos x Declarações
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={mockChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis dataKey="mes" stroke="#64748b" />
                  <YAxis
                    yAxisId="left"
                    stroke="#64748b"
                    tickFormatter={(v) => `R$ ${(v/1000)}K`}
                  />
                  <YAxis yAxisId="right" orientation="right" stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                    formatter={(value: number, name: string) => [
                      name === 'tributos'
                        ? value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                        : value,
                      name === 'tributos' ? 'Tributos' : 'Declarações'
                    ]}
                  />
                  <Legend />
                  <Bar yAxisId="left" dataKey="tributos" fill="#6366f1" name="Tributos" />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="declaracoes"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Declarações"
                  />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Resumo do Período
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex justify-between mb-2">
                    <span className="text-text-secondary">Total Tributos (12m)</span>
                    <span className="text-text-primary font-semibold">R$ 824.000,00</span>
                  </div>
                  <div className="flex justify-between mb-2">
                    <span className="text-text-secondary">Declarações Enviadas</span>
                    <span className="text-text-primary font-semibold">72</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Conformidade</span>
                    <span className="text-green-400 font-semibold">98.5%</span>
                  </div>
                </div>
                <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <span className="text-green-400 font-medium">Empresa Regular</span>
                  </div>
                  <p className="text-sm text-text-secondary mt-2">
                    Todas as obrigações principais estão em dia com a Receita Federal.
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Documentos para Download
              </h3>
              <div className="space-y-3">
                {[
                  { name: 'Relatório Anual 2023', type: 'PDF' },
                  { name: 'Resumo Tributos Q4/2023', type: 'XLSX' },
                  { name: 'Declarações Enviadas', type: 'PDF' },
                  { name: 'Histórico de Pagamentos', type: 'XLSX' }
                ].map((doc, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-accent-primary" />
                      <div>
                        <span className="text-text-primary">{doc.name}</span>
                        <p className="text-sm text-text-secondary">{doc.type}</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes da Obrigação"
        >
          {selectedObrigacao && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-bg-tertiary rounded-lg">
                <div className={`p-3 rounded-lg ${
                  selectedObrigacao.categoria === 'tributo' ? 'bg-red-500/10' :
                  selectedObrigacao.categoria === 'declaracao' ? 'bg-blue-500/10' :
                  'bg-purple-500/10'
                }`}>
                  {selectedObrigacao.categoria === 'tributo' && <DollarSign className="h-6 w-6 text-red-400" />}
                  {selectedObrigacao.categoria === 'declaracao' && <FileText className="h-6 w-6 text-blue-400" />}
                  {selectedObrigacao.categoria === 'contribuicao' && <Building2 className="h-6 w-6 text-purple-400" />}
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary">{selectedObrigacao.nome}</h4>
                  <p className="text-sm text-text-secondary">{selectedObrigacao.codigo}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-secondary text-sm">Competência</span>
                  <p className="font-medium text-text-primary">{selectedObrigacao.competencia}</p>
                </div>
                <div className="p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-secondary text-sm">Vencimento</span>
                  <p className="font-medium text-text-primary">
                    {new Date(selectedObrigacao.vencimento).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>

              {selectedObrigacao.valor > 0 && (
                <div className="p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-secondary text-sm">Valor</span>
                  <p className="text-2xl font-bold text-text-primary">
                    {selectedObrigacao.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                </div>
              )}

              <div className="p-3 bg-bg-tertiary rounded-lg">
                <span className="text-text-secondary text-sm">Status</span>
                <div className="mt-2">
                  <Badge variant={
                    selectedObrigacao.status === 'processada' ? 'success' :
                    selectedObrigacao.status === 'transmitida' ? 'primary' :
                    selectedObrigacao.status === 'pendente' ? 'warning' : 'danger'
                  }>
                    {selectedObrigacao.status.charAt(0).toUpperCase() + selectedObrigacao.status.slice(1)}
                  </Badge>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fechar
                </Button>
                {selectedObrigacao.status === 'pendente' && (
                  <Button>
                    <Send className="h-4 w-4 mr-2" />
                    Transmitir
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
