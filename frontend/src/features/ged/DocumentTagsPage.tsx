'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Tag,
  Tags,
  Plus,
  Edit2,
  Trash2,
  FileText,
  MoreHorizontal,
  Palette,
  Hash,
  Filter,
  Download,
  Upload,
  Settings,
  FolderOpen,
  TrendingUp,
  BarChart2,
  PieChart,
  CheckCircle2,
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
  Textarea,
} from '@/design-system/components';
import {
  PieChart as RechartsPie,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

// Types
interface DocumentTag {
  id: string;
  name: string;
  slug: string;
  color: string;
  description: string;
  documentCount: number;
  category: string;
  createdAt: string;
  createdBy: string;
  isSystem: boolean;
}

interface TagCategory {
  id: string;
  name: string;
  tagCount: number;
  color: string;
}

// Mock Data
const tags: DocumentTag[] = [
  {
    id: '1',
    name: 'Contrato',
    slug: 'contrato',
    color: '#3B82F6',
    description: 'Documentos contratuais e acordos',
    documentCount: 145,
    category: 'Tipo de Documento',
    createdAt: '2024-01-15',
    createdBy: 'Sistema',
    isSystem: true,
  },
  {
    id: '2',
    name: 'Urgente',
    slug: 'urgente',
    color: '#EF4444',
    description: 'Documentos com prioridade alta',
    documentCount: 23,
    category: 'Prioridade',
    createdAt: '2024-01-15',
    createdBy: 'Sistema',
    isSystem: true,
  },
  {
    id: '3',
    name: 'Aprovado',
    slug: 'aprovado',
    color: '#22C55E',
    description: 'Documentos já aprovados',
    documentCount: 312,
    category: 'Status',
    createdAt: '2024-01-15',
    createdBy: 'Sistema',
    isSystem: true,
  },
  {
    id: '4',
    name: 'Pendente',
    slug: 'pendente',
    color: '#F59E0B',
    description: 'Aguardando revisão ou aprovação',
    documentCount: 67,
    category: 'Status',
    createdAt: '2024-01-15',
    createdBy: 'Sistema',
    isSystem: true,
  },
  {
    id: '5',
    name: 'Confidencial',
    slug: 'confidencial',
    color: '#8B5CF6',
    description: 'Documentos sensíveis',
    documentCount: 89,
    category: 'Classificação',
    createdAt: '2024-02-01',
    createdBy: 'Ana Costa',
    isSystem: false,
  },
  {
    id: '6',
    name: 'Financeiro',
    slug: 'financeiro',
    color: '#10B981',
    description: 'Documentos financeiros',
    documentCount: 234,
    category: 'Departamento',
    createdAt: '2024-01-20',
    createdBy: 'Carlos Lima',
    isSystem: false,
  },
  {
    id: '7',
    name: 'RH',
    slug: 'rh',
    color: '#EC4899',
    description: 'Documentos de recursos humanos',
    documentCount: 178,
    category: 'Departamento',
    createdAt: '2024-01-20',
    createdBy: 'Maria Oliveira',
    isSystem: false,
  },
  {
    id: '8',
    name: '2026',
    slug: '2026',
    color: '#06B6D4',
    description: 'Documentos do ano 2026',
    documentCount: 156,
    category: 'Período',
    createdAt: '2026-01-02',
    createdBy: 'Sistema',
    isSystem: true,
  },
  {
    id: '9',
    name: 'Arquivado',
    slug: 'arquivado',
    color: '#6B7280',
    description: 'Documentos arquivados',
    documentCount: 445,
    category: 'Status',
    createdAt: '2024-01-15',
    createdBy: 'Sistema',
    isSystem: true,
  },
  {
    id: '10',
    name: 'Cliente VIP',
    slug: 'cliente-vip',
    color: '#F59E0B',
    description: 'Documentos de clientes prioritários',
    documentCount: 56,
    category: 'Classificação',
    createdAt: '2025-06-15',
    createdBy: 'Roberto Silva',
    isSystem: false,
  },
];

const categories: TagCategory[] = [
  { id: '1', name: 'Tipo de Documento', tagCount: 12, color: '#3B82F6' },
  { id: '2', name: 'Status', tagCount: 8, color: '#22C55E' },
  { id: '3', name: 'Prioridade', tagCount: 4, color: '#EF4444' },
  { id: '4', name: 'Departamento', tagCount: 10, color: '#8B5CF6' },
  { id: '5', name: 'Classificação', tagCount: 6, color: '#F59E0B' },
  { id: '6', name: 'Período', tagCount: 5, color: '#06B6D4' },
];

const tabs = [
  { id: 'all', label: 'Todas as Tags' },
  { id: 'system', label: 'Sistema' },
  { id: 'custom', label: 'Personalizadas' },
  { id: 'categories', label: 'Categorias' },
];

// Chart Data
const tagUsageData = [
  { name: 'Contrato', value: 145 },
  { name: 'Aprovado', value: 312 },
  { name: 'Financeiro', value: 234 },
  { name: 'RH', value: 178 },
  { name: 'Outros', value: 450 },
];

const tagTrendData = [
  { month: 'Set', tags: 120 },
  { month: 'Out', tags: 145 },
  { month: 'Nov', tags: 180 },
  { month: 'Dez', tags: 220 },
  { month: 'Jan', tags: 195 },
];

const COLORS = ['#3B82F6', '#22C55E', '#10B981', '#EC4899', '#6B7280'];

const columns: Column<DocumentTag>[] = [
  {
    key: 'name',
    header: 'Tag',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: row.color }}
        />
        <div>
          <div className="flex items-center gap-2">
            <p className="font-medium text-text-primary">{row.name}</p>
            {row.isSystem && (
              <Badge variant="secondary" size="sm">Sistema</Badge>
            )}
          </div>
          <p className="text-xs text-text-muted">#{row.slug}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'description',
    header: 'Descrição',
    render: (row) => (
      <span className="text-sm text-text-secondary line-clamp-1">{row.description}</span>
    ),
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => <Badge variant="neutral">{row.category}</Badge>,
  },
  {
    key: 'documentCount',
    header: 'Documentos',
    render: (row) => (
      <div className="flex items-center gap-2">
        <FileText className="w-4 h-4 text-text-muted" />
        <span className="font-medium">{row.documentCount}</span>
      </div>
    ),
  },
  {
    key: 'createdBy',
    header: 'Criado por',
    render: (row) => (
      <span className="text-sm text-text-secondary">{row.createdBy}</span>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Documentos">
          <FolderOpen className="w-4 h-4" />
        </Button>
        {!row.isSystem && (
          <>
            <Button variant="ghost" size="icon-sm" title="Editar">
              <Edit2 className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Excluir">
              <Trash2 className="w-4 h-4" />
            </Button>
          </>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const colorOptions = [
  { value: '#3B82F6', label: 'Azul' },
  { value: '#EF4444', label: 'Vermelho' },
  { value: '#22C55E', label: 'Verde' },
  { value: '#F59E0B', label: 'Amarelo' },
  { value: '#8B5CF6', label: 'Roxo' },
  { value: '#EC4899', label: 'Rosa' },
  { value: '#06B6D4', label: 'Ciano' },
  { value: '#10B981', label: 'Esmeralda' },
  { value: '#6B7280', label: 'Cinza' },
];

export function DocumentTagsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [selectedColor, setSelectedColor] = useState('#3B82F6');
  const [newTagCategory, setNewTagCategory] = useState('');

  const filteredTags = tags.filter((tag) => {
    const matchesSearch = tag.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tag.description.toLowerCase().includes(searchTerm.toLowerCase());

    if (activeTab === 'system') return matchesSearch && tag.isSystem;
    if (activeTab === 'custom') return matchesSearch && !tag.isSystem;
    return matchesSearch;
  });

  // Stats
  const totalTags = tags.length;
  const systemTags = tags.filter(t => t.isSystem).length;
  const customTags = tags.filter(t => !t.isSystem).length;
  const totalDocuments = tags.reduce((acc, t) => acc + t.documentCount, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gerenciamento de Tags
            </h1>
            <p className="text-text-secondary mt-1">
              Organize documentos com etiquetas e categorias
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Nova Tag
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total de Tags"
              value={totalTags}
              icon={<Tags className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Tags do Sistema"
              value={systemTags}
              icon={<Settings className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Tags Personalizadas"
              value={customTags}
              icon={<Tag className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Documentos Etiquetados"
              value={totalDocuments.toLocaleString('pt-BR')}
              icon={<FileText className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <PieChart className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Distribuição por Tag</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPie>
                    <Pie
                      data={tagUsageData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {tagUsageData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPie>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Uso de Tags (Últimos Meses)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={tagTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-bg-secondary)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar dataKey="tags" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Categories Overview */}
        {activeTab === 'categories' ? (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Categorias de Tags</h3>
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={() => setIsCategoryModalOpen(true)}
                >
                  Nova Categoria
                </Button>
              </div>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-3 gap-4">
                {categories.map((category) => (
                  <div
                    key={category.id}
                    className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: category.color }}
                        />
                        <h4 className="font-medium text-text-primary">{category.name}</h4>
                      </div>
                      <Button variant="ghost" size="icon-sm">
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-text-muted">
                      <Tag className="w-4 h-4" />
                      <span>{category.tagCount} tags</span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {tags
                        .filter(t => t.category === category.name)
                        .slice(0, 3)
                        .map((tag) => (
                          <Badge
                            key={tag.id}
                            size="sm"
                            style={{ backgroundColor: `${tag.color}20`, color: tag.color }}
                          >
                            {tag.name}
                          </Badge>
                        ))}
                      {tags.filter(t => t.category === category.name).length > 3 && (
                        <Badge variant="neutral" size="sm">
                          +{tags.filter(t => t.category === category.name).length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        ) : (
          <>
            {/* Popular Tags */}
            <Card>
              <CardHeader>
                <h3 className="font-semibold">Tags Mais Usadas</h3>
              </CardHeader>
              <CardBody>
                <div className="flex flex-wrap gap-2">
                  {tags
                    .sort((a, b) => b.documentCount - a.documentCount)
                    .slice(0, 10)
                    .map((tag) => (
                      <button
                        key={tag.id}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors"
                      >
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: tag.color }}
                        />
                        <span className="font-medium text-text-primary">{tag.name}</span>
                        <span className="text-sm text-text-muted">{tag.documentCount}</span>
                      </button>
                    ))}
                </div>
              </CardBody>
            </Card>

            {/* Tabs & Search */}
            <div className="flex items-center justify-between">
              <SimpleTabBar
                tabs={tabs}
                activeTab={activeTab}
                onTabChange={setActiveTab}
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar tags..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
              </div>
            </div>

            {/* Tags Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card>
                <CardBody className="p-0">
                  <DataTable
                    columns={columns}
                    data={filteredTags}
                    keyExtractor={(row) => row.id}
                  />
                </CardBody>
              </Card>
            </motion.div>
          </>
        )}

        {/* Create Tag Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Nova Tag"
          description="Crie uma nova tag para organizar documentos"
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsCreateModalOpen(false)}>
                Criar Tag
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Nome da Tag"
              placeholder="Ex: Importante"
              required
            />

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Cor</label>
              <div className="flex flex-wrap gap-2">
                {colorOptions.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => setSelectedColor(color.value)}
                    className={`w-8 h-8 rounded-full transition-transform ${
                      selectedColor === color.value ? 'ring-2 ring-offset-2 ring-primary scale-110' : ''
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.label}
                  />
                ))}
              </div>
            </div>

            <Select
              label="Categoria"
              options={categories.map(c => ({ value: c.id, label: c.name }))}
              value={newTagCategory}
              onChange={(value) => setNewTagCategory(value)}
              placeholder="Selecione uma categoria"
            />

            <Textarea
              label="Descrição"
              placeholder="Descreva o propósito desta tag"
              rows={3}
            />

            <div className="p-3 rounded-lg bg-bg-secondary">
              <div className="flex items-center gap-3">
                <Tag className="w-5 h-5 text-text-muted" />
                <div>
                  <p className="text-sm text-text-muted">Preview</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge style={{ backgroundColor: `${selectedColor}20`, color: selectedColor }}>
                      Nova Tag
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Modal>

        {/* Create Category Modal */}
        <Modal
          isOpen={isCategoryModalOpen}
          onClose={() => setIsCategoryModalOpen(false)}
          title="Nova Categoria"
          description="Crie uma categoria para agrupar tags"
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCategoryModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsCategoryModalOpen(false)}>
                Criar Categoria
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Nome da Categoria"
              placeholder="Ex: Tipo de Documento"
              required
            />

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Cor</label>
              <div className="flex flex-wrap gap-2">
                {colorOptions.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => setSelectedColor(color.value)}
                    className={`w-8 h-8 rounded-full transition-transform ${
                      selectedColor === color.value ? 'ring-2 ring-offset-2 ring-primary scale-110' : ''
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.label}
                  />
                ))}
              </div>
            </div>

            <Textarea
              label="Descrição"
              placeholder="Descreva o propósito desta categoria"
              rows={3}
            />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
