'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Plus,
  Users,
  User,
  Building,
  ChevronDown,
  ChevronRight,
  Edit2,
  Eye,
  Download,
  Settings,
  MoreHorizontal,
  Briefcase,
  Mail,
  Phone,
  MapPin,
  Calendar,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Grid,
  List,
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
  Modal,
  Select,
} from '@/design-system/components';

// Types
interface OrgNode {
  id: string;
  name: string;
  title: string;
  department: string;
  email: string;
  phone: string;
  location: string;
  hireDate: string;
  directReports: number;
  children?: OrgNode[];
}

// Mock Data
const orgData: OrgNode = {
  id: '1',
  name: 'Carlos Eduardo Lima',
  title: 'CEO',
  department: 'Diretoria',
  email: 'carlos.lima@empresa.com',
  phone: '(11) 99999-0001',
  location: 'São Paulo',
  hireDate: '2015-01-15',
  directReports: 4,
  children: [
    {
      id: '2',
      name: 'Ana Paula Costa',
      title: 'Diretora Comercial',
      department: 'Comercial',
      email: 'ana.costa@empresa.com',
      phone: '(11) 99999-0002',
      location: 'São Paulo',
      hireDate: '2016-03-20',
      directReports: 3,
      children: [
        { id: '2.1', name: 'Roberto Alves', title: 'Gerente de Vendas', department: 'Comercial', email: 'roberto@empresa.com', phone: '(11) 99999-0010', location: 'São Paulo', hireDate: '2018-05-10', directReports: 8 },
        { id: '2.2', name: 'Fernanda Reis', title: 'Gerente de Marketing', department: 'Marketing', email: 'fernanda@empresa.com', phone: '(11) 99999-0011', location: 'São Paulo', hireDate: '2019-02-15', directReports: 5 },
        { id: '2.3', name: 'Lucas Silva', title: 'Gerente de Parcerias', department: 'Comercial', email: 'lucas@empresa.com', phone: '(11) 99999-0012', location: 'Rio de Janeiro', hireDate: '2020-08-01', directReports: 4 },
      ],
    },
    {
      id: '3',
      name: 'Maria Oliveira',
      title: 'Diretora de RH',
      department: 'Recursos Humanos',
      email: 'maria.oliveira@empresa.com',
      phone: '(11) 99999-0003',
      location: 'São Paulo',
      hireDate: '2017-06-01',
      directReports: 2,
      children: [
        { id: '3.1', name: 'Patricia Santos', title: 'Gerente de DP', department: 'RH', email: 'patricia@empresa.com', phone: '(11) 99999-0020', location: 'São Paulo', hireDate: '2019-04-15', directReports: 4 },
        { id: '3.2', name: 'Marcos Ferreira', title: 'Gerente de T&D', department: 'RH', email: 'marcos@empresa.com', phone: '(11) 99999-0021', location: 'São Paulo', hireDate: '2020-01-10', directReports: 3 },
      ],
    },
    {
      id: '4',
      name: 'Roberto Silva',
      title: 'Diretor de TI',
      department: 'Tecnologia',
      email: 'roberto.silva@empresa.com',
      phone: '(11) 99999-0004',
      location: 'São Paulo',
      hireDate: '2016-09-15',
      directReports: 3,
      children: [
        { id: '4.1', name: 'Julia Tech', title: 'Gerente de Desenvolvimento', department: 'TI', email: 'julia@empresa.com', phone: '(11) 99999-0030', location: 'São Paulo', hireDate: '2018-11-01', directReports: 12 },
        { id: '4.2', name: 'André Infra', title: 'Gerente de Infraestrutura', department: 'TI', email: 'andre@empresa.com', phone: '(11) 99999-0031', location: 'São Paulo', hireDate: '2019-07-20', directReports: 6 },
        { id: '4.3', name: 'Carla Dados', title: 'Gerente de Dados', department: 'TI', email: 'carla@empresa.com', phone: '(11) 99999-0032', location: 'São Paulo', hireDate: '2021-03-15', directReports: 4 },
      ],
    },
    {
      id: '5',
      name: 'Pedro Santos',
      title: 'Diretor Financeiro',
      department: 'Financeiro',
      email: 'pedro.santos@empresa.com',
      phone: '(11) 99999-0005',
      location: 'São Paulo',
      hireDate: '2017-02-01',
      directReports: 2,
      children: [
        { id: '5.1', name: 'Regina Contabil', title: 'Gerente Contábil', department: 'Financeiro', email: 'regina@empresa.com', phone: '(11) 99999-0040', location: 'São Paulo', hireDate: '2018-08-10', directReports: 5 },
        { id: '5.2', name: 'Bruno Fiscal', title: 'Gerente Fiscal', department: 'Financeiro', email: 'bruno@empresa.com', phone: '(11) 99999-0041', location: 'São Paulo', hireDate: '2019-12-01', directReports: 4 },
      ],
    },
  ],
};

const departments = [
  { name: 'Diretoria', count: 5, color: '#8B5CF6' },
  { name: 'Comercial', count: 25, color: '#3B82F6' },
  { name: 'TI', count: 35, color: '#10B981' },
  { name: 'RH', count: 12, color: '#F59E0B' },
  { name: 'Financeiro', count: 15, color: '#EF4444' },
  { name: 'Operacional', count: 45, color: '#6B7280' },
];

// Org Card Component
function OrgCard({ node, onSelect, expanded, onToggle }: {
  node: OrgNode;
  onSelect: (node: OrgNode) => void;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex flex-col items-center">
      <div
        className="relative p-4 rounded-xl border-2 border-border bg-bg-primary hover:border-primary/50 transition-colors cursor-pointer shadow-sm w-64"
        onClick={() => onSelect(node)}
      >
        <div className="flex items-center gap-3">
          <Avatar name={node.name} size="lg" />
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-text-primary truncate">{node.name}</p>
            <p className="text-sm text-primary truncate">{node.title}</p>
            <p className="text-xs text-text-muted truncate">{node.department}</p>
          </div>
        </div>
        {node.directReports > 0 && (
          <div className="absolute -bottom-3 left-1/2 -translate-x-1/2">
            <button
              onClick={(e) => { e.stopPropagation(); onToggle(); }}
              className="flex items-center gap-1 px-2 py-1 rounded-full bg-primary text-white text-xs font-medium shadow-md hover:bg-primary/90 transition-colors"
            >
              {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              {node.directReports}
            </button>
          </div>
        )}
      </div>

      {/* Children */}
      {expanded && node.children && node.children.length > 0 && (
        <>
          <div className="w-px h-8 bg-border" />
          <div className="relative flex gap-8">
            {node.children.length > 1 && (
              <div className="absolute top-0 left-1/2 -translate-x-1/2 h-px bg-border" style={{ width: `calc(100% - 16rem)` }} />
            )}
            {node.children.map((child, index) => (
              <div key={child.id} className="flex flex-col items-center">
                <div className="w-px h-4 bg-border" />
                <OrgCard
                  node={child}
                  onSelect={onSelect}
                  expanded={false}
                  onToggle={() => {}}
                />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function OrgChartPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'chart' | 'list'>('chart');
  const [selectedNode, setSelectedNode] = useState<OrgNode | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['1']));
  const [zoom, setZoom] = useState(100);

  const toggleNode = (nodeId: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  // Stats
  const totalEmployees = 137;
  const totalDepartments = departments.length;
  const avgTeamSize = (totalEmployees / totalDepartments).toFixed(1);
  const levels = 4;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Organograma
            </h1>
            <p className="text-text-secondary mt-1">
              Visualize a estrutura organizacional da empresa
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 bg-bg-secondary rounded-lg p-1">
              <Button variant={viewMode === 'chart' ? 'primary' : 'ghost'} size="icon-sm" onClick={() => setViewMode('chart')}>
                <Grid className="w-4 h-4" />
              </Button>
              <Button variant={viewMode === 'list' ? 'primary' : 'ghost'} size="icon-sm" onClick={() => setViewMode('list')}>
                <List className="w-4 h-4" />
              </Button>
            </div>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
              Adicionar Cargo
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Colaboradores" value={totalEmployees} icon={<Users className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Departamentos" value={totalDepartments} icon={<Building className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Média por Equipe" value={avgTeamSize} icon={<User className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Níveis Hierárquicos" value={levels} icon={<Briefcase className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Department Overview */}
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Departamentos</h3>
          </CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-3">
              {departments.map((dept) => (
                <div
                  key={dept.name}
                  className="flex items-center gap-3 px-4 py-2 rounded-lg border border-border hover:border-primary/50 cursor-pointer transition-colors"
                >
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: dept.color }} />
                  <span className="font-medium">{dept.name}</span>
                  <Badge variant="neutral" size="sm">{dept.count}</Badge>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Search & Zoom */}
        <div className="flex items-center justify-between">
          <Input
            placeholder="Buscar colaborador..."
            leftIcon={<Search className="w-4 h-4" />}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-64"
          />
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon-sm" onClick={() => setZoom(Math.max(50, zoom - 10))}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            <span className="text-sm text-text-muted w-12 text-center">{zoom}%</span>
            <Button variant="ghost" size="icon-sm" onClick={() => setZoom(Math.min(150, zoom + 10))}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" onClick={() => setZoom(100)}>
              <Maximize2 className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Org Chart */}
        {viewMode === 'chart' ? (
          <Card>
            <CardBody className="overflow-auto">
              <div
                className="flex justify-center py-8 min-w-max"
                style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}
              >
                <OrgCard
                  node={orgData}
                  onSelect={setSelectedNode}
                  expanded={expandedNodes.has(orgData.id)}
                  onToggle={() => toggleNode(orgData.id)}
                />
              </div>
            </CardBody>
          </Card>
        ) : (
          <Card>
            <CardBody className="p-0">
              <div className="divide-y divide-border">
                {[orgData, ...(orgData.children || [])].map((node) => (
                  <div key={node.id} className="flex items-center justify-between p-4 hover:bg-bg-secondary/50 cursor-pointer" onClick={() => setSelectedNode(node)}>
                    <div className="flex items-center gap-3">
                      <Avatar name={node.name} size="sm" />
                      <div>
                        <p className="font-medium text-text-primary">{node.name}</p>
                        <p className="text-sm text-text-muted">{node.title}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge variant="neutral">{node.department}</Badge>
                      <span className="text-sm text-text-muted">{node.directReports} subordinados</span>
                      <Button variant="ghost" size="icon-sm"><Eye className="w-4 h-4" /></Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {/* Employee Detail Modal */}
        <Modal isOpen={!!selectedNode} onClose={() => setSelectedNode(null)} title="Detalhes do Colaborador" size="md" footer={<><Button variant="secondary" onClick={() => setSelectedNode(null)}>Fechar</Button><Button variant="primary" leftIcon={<Edit2 className="w-4 h-4" />}>Editar</Button></>}>
          {selectedNode && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <Avatar name={selectedNode.name} size="xl" />
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedNode.name}</h3>
                  <p className="text-primary">{selectedNode.title}</p>
                  <Badge variant="neutral" className="mt-2">{selectedNode.department}</Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                  <Mail className="w-5 h-5 text-text-muted" />
                  <div>
                    <p className="text-xs text-text-muted">E-mail</p>
                    <p className="text-sm font-medium">{selectedNode.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                  <Phone className="w-5 h-5 text-text-muted" />
                  <div>
                    <p className="text-xs text-text-muted">Telefone</p>
                    <p className="text-sm font-medium">{selectedNode.phone}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                  <MapPin className="w-5 h-5 text-text-muted" />
                  <div>
                    <p className="text-xs text-text-muted">Localização</p>
                    <p className="text-sm font-medium">{selectedNode.location}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                  <Calendar className="w-5 h-5 text-text-muted" />
                  <div>
                    <p className="text-xs text-text-muted">Admissão</p>
                    <p className="text-sm font-medium">{new Date(selectedNode.hireDate).toLocaleDateString('pt-BR')}</p>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-lg border border-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-primary" />
                    <span className="font-medium">Subordinados Diretos</span>
                  </div>
                  <Badge variant="primary">{selectedNode.directReports}</Badge>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
