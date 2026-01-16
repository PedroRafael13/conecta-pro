'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  Wrench,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  TrendingUp,
  TrendingDown,
  BarChart3,
  MapPin,
  QrCode,
  Building,
  Settings,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  ChevronRight,
  Plus
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Badge } from '../../design-system/components/Badge';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { MainLayout } from '../../layouts/MainLayout';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';

// Mock Data
const maintenanceTrendData = [
  { month: 'Set', preventiva: 45, corretiva: 12 },
  { month: 'Out', preventiva: 52, corretiva: 8 },
  { month: 'Nov', preventiva: 48, corretiva: 15 },
  { month: 'Dez', preventiva: 55, corretiva: 6 },
  { month: 'Jan', preventiva: 60, corretiva: 10 },
  { month: 'Fev', preventiva: 58, corretiva: 7 }
];

const equipmentByCategory = [
  { name: 'TI & Informática', value: 245, color: '#6366f1' },
  { name: 'Veículos', value: 42, color: '#10b981' },
  { name: 'Móveis', value: 180, color: '#f59e0b' },
  { name: 'Máquinas', value: 65, color: '#ef4444' },
  { name: 'Ferramentas', value: 120, color: '#8b5cf6' },
  { name: 'Outros', value: 85, color: '#3b82f6' }
];

const equipmentByStatus = [
  { status: 'Ativo', count: 580, percentage: 78.4 },
  { status: 'Em Manutenção', count: 35, percentage: 4.7 },
  { status: 'Comodato', count: 82, percentage: 11.1 },
  { status: 'Baixado', count: 40, percentage: 5.4 }
];

const locationDistribution = [
  { location: 'Matriz', count: 320 },
  { location: 'Filial SP', count: 180 },
  { location: 'Filial RJ', count: 120 },
  { location: 'CD Logístico', count: 85 },
  { location: 'Em Campo', count: 32 }
];

const recentMaintenances = [
  { id: '1', equipment: 'Servidor Dell PowerEdge R740', type: 'preventiva', status: 'completed', date: '2024-02-15', cost: 1200 },
  { id: '2', equipment: 'Veículo Ford Transit ABC-1234', type: 'corretiva', status: 'in_progress', date: '2024-02-16', cost: 3500 },
  { id: '3', equipment: 'Impressora HP LaserJet Pro', type: 'preventiva', status: 'scheduled', date: '2024-02-20', cost: 450 },
  { id: '4', equipment: 'Ar Condicionado Split 12000 BTU', type: 'corretiva', status: 'completed', date: '2024-02-14', cost: 890 },
  { id: '5', equipment: 'Notebook Dell Latitude 5520', type: 'preventiva', status: 'scheduled', date: '2024-02-22', cost: 200 }
];

const pendingComodatos = [
  { id: '1', equipment: 'Notebook Dell XPS 15', client: 'Tech Solutions Ltda', dueDate: '2024-03-01', daysRemaining: 13 },
  { id: '2', equipment: 'Projetor Epson EB-X41', client: 'Evento Corp', dueDate: '2024-02-28', daysRemaining: 12 },
  { id: '3', equipment: 'Kit Ferramentas Completo', client: 'Manutenção Express', dueDate: '2024-02-25', daysRemaining: 9 }
];

const depreciationAlerts = [
  { id: '1', equipment: 'Servidor HP ProLiant', purchaseDate: '2019-03-15', depreciation: 95, action: 'Avaliar baixa' },
  { id: '2', equipment: 'Impressora Xerox WorkCentre', purchaseDate: '2020-06-10', depreciation: 82, action: 'Planejar substituição' },
  { id: '3', equipment: 'Switch Cisco Catalyst 2960', purchaseDate: '2019-08-20', depreciation: 90, action: 'Avaliar upgrade' }
];

export function EquipmentDashboardPage() {
  const getMaintenanceStatusInfo = (status: string) => {
    const statuses: Record<string, { label: string; color: 'success' | 'warning' | 'info' | 'danger' }> = {
      completed: { label: 'Concluída', color: 'success' },
      in_progress: { label: 'Em Andamento', color: 'info' },
      scheduled: { label: 'Agendada', color: 'warning' }
    };
    return statuses[status] || { label: status, color: 'info' as const };
  };

  const getMaintenanceTypeLabel = (type: string) => {
    return type === 'preventiva' ? 'Preventiva' : 'Corretiva';
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Patrimônio
            </h1>
            <p className="text-text-secondary mt-1">
              Equipamentos, manutenções e controle de ativos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <QrCode className="h-4 w-4 mr-2" />
              Escanear QR
            </Button>
            <Button variant="primary">
              <Plus className="h-4 w-4 mr-2" />
              Novo Equipamento
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <StatCard
            title="Total de Equipamentos"
            value="737"
            change={12}
            changeLabel="novos este mês"
            icon={<Package className="h-5 w-5" />}
          />
          <StatCard
            title="Valor do Patrimônio"
            value="R$ 2.4M"
            change={5.2}
            changeLabel="valorização"
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Em Manutenção"
            value="35"
            changeLabel="4.7% do total"
            icon={<Wrench className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Em Comodato"
            value="82"
            changeLabel="11.1% do total"
            icon={<Building className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Alertas"
            value="8"
            changeLabel="depreciação/vencimento"
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
          />
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Maintenance Trend */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-text-primary">
                  Manutenções por Mês
                </h3>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-accent-primary" />
                    <span className="text-text-secondary">Preventiva</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-accent-danger" />
                    <span className="text-text-secondary">Corretiva</span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={maintenanceTrendData}>
                    <defs>
                      <linearGradient id="colorPreventiva" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorCorretiva" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="preventiva"
                      name="Preventiva"
                      stroke="#6366f1"
                      fillOpacity={1}
                      fill="url(#colorPreventiva)"
                    />
                    <Area
                      type="monotone"
                      dataKey="corretiva"
                      name="Corretiva"
                      stroke="#ef4444"
                      fillOpacity={1}
                      fill="url(#colorCorretiva)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Category Distribution */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Por Categoria
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={equipmentByCategory}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {equipmentByCategory.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {equipmentByCategory.map((cat) => (
                  <div key={cat.name} className="flex items-center gap-2 text-xs">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cat.color }} />
                    <span className="text-text-secondary truncate">{cat.name}</span>
                    <span className="text-text-primary font-medium">{cat.value}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Status and Location Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Status Distribution */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Status dos Equipamentos
              </h3>
            </CardHeader>
            <CardBody className="space-y-4">
              {equipmentByStatus.map((item, index) => (
                <motion.div
                  key={item.status}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-4"
                >
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-text-primary font-medium">{item.status}</span>
                      <span className="text-text-secondary text-sm">{item.count} ({item.percentage}%)</span>
                    </div>
                    <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.percentage}%` }}
                        transition={{ duration: 0.8, delay: index * 0.1 }}
                        className={`h-full rounded-full ${
                          item.status === 'Ativo' ? 'bg-accent-success' :
                          item.status === 'Em Manutenção' ? 'bg-accent-warning' :
                          item.status === 'Comodato' ? 'bg-accent-info' :
                          'bg-accent-secondary'
                        }`}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </CardBody>
          </Card>

          {/* Location Distribution */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Distribuição por Local
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={locationDistribution} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#64748b" />
                    <YAxis dataKey="location" type="category" stroke="#64748b" width={90} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="count" name="Equipamentos" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Bottom Row - Lists */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Maintenances */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-text-primary">
                  Manutenções Recentes
                </h3>
                <Button variant="ghost" size="sm">
                  Ver todas
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </CardHeader>
            <CardBody className="space-y-3">
              {recentMaintenances.map((maintenance, index) => (
                <motion.div
                  key={maintenance.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-3 bg-bg-tertiary rounded-lg"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-text-primary text-sm truncate">
                        {maintenance.equipment}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge
                          variant={maintenance.type === 'preventiva' ? 'primary' : 'danger'}
                          size="sm"
                        >
                          {getMaintenanceTypeLabel(maintenance.type)}
                        </Badge>
                        <Badge
                          variant={getMaintenanceStatusInfo(maintenance.status).color}
                          size="sm"
                        >
                          {getMaintenanceStatusInfo(maintenance.status).label}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-text-primary">
                        {maintenance.cost.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <p className="text-xs text-text-secondary">
                        {new Date(maintenance.date).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </CardBody>
          </Card>

          {/* Pending Comodatos */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-text-primary">
                  Comodatos a Vencer
                </h3>
                <Button variant="ghost" size="sm">
                  Ver todos
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </CardHeader>
            <CardBody className="space-y-3">
              {pendingComodatos.map((comodato, index) => (
                <motion.div
                  key={comodato.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-3 bg-bg-tertiary rounded-lg"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-text-primary text-sm truncate">
                        {comodato.equipment}
                      </p>
                      <p className="text-xs text-text-secondary mt-1">
                        {comodato.client}
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge
                        variant={comodato.daysRemaining <= 7 ? 'danger' : 'warning'}
                        size="sm"
                      >
                        {comodato.daysRemaining} dias
                      </Badge>
                      <p className="text-xs text-text-secondary mt-1">
                        {new Date(comodato.dueDate).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </CardBody>
          </Card>

          {/* Depreciation Alerts */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-accent-warning" />
                  <h3 className="text-lg font-semibold text-text-primary">
                    Alertas de Depreciação
                  </h3>
                </div>
              </div>
            </CardHeader>
            <CardBody className="space-y-3">
              {depreciationAlerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-3 bg-bg-tertiary rounded-lg border border-accent-warning/30"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-text-primary text-sm truncate">
                        {alert.equipment}
                      </p>
                      <p className="text-xs text-text-secondary mt-1">
                        Aquisição: {new Date(alert.purchaseDate).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1">
                        <TrendingDown className="h-4 w-4 text-accent-danger" />
                        <span className="text-accent-danger font-medium text-sm">
                          {alert.depreciation}%
                        </span>
                      </div>
                      <p className="text-xs text-accent-warning mt-1">
                        {alert.action}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </CardBody>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Ações Rápidas
            </h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {[
                { icon: Package, label: 'Cadastrar Equipamento', color: 'primary' },
                { icon: Wrench, label: 'Abrir Manutenção', color: 'warning' },
                { icon: Building, label: 'Novo Comodato', color: 'info' },
                { icon: QrCode, label: 'Gerar Etiquetas', color: 'success' },
                { icon: MapPin, label: 'Transferência', color: 'info' },
                { icon: BarChart3, label: 'Relatório Patrimonial', color: 'primary' }
              ].map((action, index) => (
                <motion.button
                  key={action.label}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors text-center group"
                >
                  <div className={`mx-auto w-12 h-12 rounded-xl bg-accent-${action.color}/20 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform`}>
                    <action.icon className={`h-6 w-6 text-accent-${action.color}`} />
                  </div>
                  <p className="text-sm text-text-primary font-medium">{action.label}</p>
                </motion.button>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </MainLayout>
  );
}

export default EquipmentDashboardPage;
