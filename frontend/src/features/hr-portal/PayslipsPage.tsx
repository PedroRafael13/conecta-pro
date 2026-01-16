'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  Download,
  Eye,
  Calendar,
  FileText,
  TrendingUp,
  TrendingDown,
  Minus,
  Plus,
  Filter,
  Search,
  ChevronDown,
  Printer
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { MainLayout } from '../../layouts/MainLayout';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

// Types
interface Payslip {
  id: string;
  month: string;
  year: number;
  reference: string;
  grossSalary: number;
  netSalary: number;
  deductions: number;
  additions: number;
  type: 'regular' | 'bonus' | 'vacation' | 'termination';
  paymentDate: string;
  status: 'paid' | 'pending';
  details: {
    earnings: { description: string; reference: number; value: number }[];
    deductions: { description: string; reference: number; value: number }[];
  };
}

// Mock Data
const mockPayslips: Payslip[] = [
  {
    id: '1',
    month: 'Janeiro',
    year: 2024,
    reference: '01/2024',
    grossSalary: 12500,
    netSalary: 9850.45,
    deductions: 2649.55,
    additions: 0,
    type: 'regular',
    paymentDate: '2024-01-31',
    status: 'paid',
    details: {
      earnings: [
        { description: 'Salário Base', reference: 220, value: 12500 },
        { description: 'DSR s/ Variáveis', reference: 0, value: 0 }
      ],
      deductions: [
        { description: 'INSS', reference: 0, value: 876.97 },
        { description: 'IRRF', reference: 0, value: 1522.58 },
        { description: 'Vale Transporte', reference: 6, value: 250.00 }
      ]
    }
  },
  {
    id: '2',
    month: 'Dezembro',
    year: 2023,
    reference: '12/2023',
    grossSalary: 25000,
    netSalary: 19700.90,
    deductions: 5299.10,
    additions: 12500,
    type: 'bonus',
    paymentDate: '2023-12-20',
    status: 'paid',
    details: {
      earnings: [
        { description: 'Salário Base', reference: 220, value: 12500 },
        { description: '13º Salário', reference: 0, value: 12500 }
      ],
      deductions: [
        { description: 'INSS', reference: 0, value: 1753.94 },
        { description: 'IRRF', reference: 0, value: 3295.16 },
        { description: 'Vale Transporte', reference: 6, value: 250.00 }
      ]
    }
  },
  {
    id: '3',
    month: 'Novembro',
    year: 2023,
    reference: '11/2023',
    grossSalary: 12500,
    netSalary: 9850.45,
    deductions: 2649.55,
    additions: 0,
    type: 'regular',
    paymentDate: '2023-11-30',
    status: 'paid',
    details: {
      earnings: [
        { description: 'Salário Base', reference: 220, value: 12500 }
      ],
      deductions: [
        { description: 'INSS', reference: 0, value: 876.97 },
        { description: 'IRRF', reference: 0, value: 1522.58 },
        { description: 'Vale Transporte', reference: 6, value: 250.00 }
      ]
    }
  },
  {
    id: '4',
    month: 'Outubro',
    year: 2023,
    reference: '10/2023',
    grossSalary: 12500,
    netSalary: 9850.45,
    deductions: 2649.55,
    additions: 0,
    type: 'regular',
    paymentDate: '2023-10-31',
    status: 'paid',
    details: {
      earnings: [
        { description: 'Salário Base', reference: 220, value: 12500 }
      ],
      deductions: [
        { description: 'INSS', reference: 0, value: 876.97 },
        { description: 'IRRF', reference: 0, value: 1522.58 },
        { description: 'Vale Transporte', reference: 6, value: 250.00 }
      ]
    }
  }
];

const salaryTrendData = [
  { month: 'Ago', bruto: 12500, liquido: 9850 },
  { month: 'Set', bruto: 12500, liquido: 9850 },
  { month: 'Out', bruto: 12500, liquido: 9850 },
  { month: 'Nov', bruto: 12500, liquido: 9850 },
  { month: 'Dez', bruto: 25000, liquido: 19700 },
  { month: 'Jan', bruto: 12500, liquido: 9850 }
];

export function PayslipsPage() {
  const [selectedYear, setSelectedYear] = useState(2024);
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const getTypeInfo = (type: Payslip['type']) => {
    const types = {
      regular: { label: 'Regular', color: 'primary' as const },
      bonus: { label: '13º Salário', color: 'success' as const },
      vacation: { label: 'Férias', color: 'info' as const },
      termination: { label: 'Rescisão', color: 'warning' as const }
    };
    return types[type];
  };

  const handleViewDetails = (payslip: Payslip) => {
    setSelectedPayslip(payslip);
    setShowDetailModal(true);
  };

  const filteredPayslips = mockPayslips.filter(p => p.year === selectedYear || selectedYear === 0);

  const totalBruto = filteredPayslips.reduce((sum, p) => sum + p.grossSalary, 0);
  const totalLiquido = filteredPayslips.reduce((sum, p) => sum + p.netSalary, 0);
  const totalDeducoes = filteredPayslips.reduce((sum, p) => sum + p.deductions, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Meus Contracheques
            </h1>
            <p className="text-text-secondary mt-1">
              Histórico de pagamentos e holerites
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary"
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
            >
              <option value={0}>Todos os anos</option>
              <option value={2024}>2024</option>
              <option value={2023}>2023</option>
              <option value={2022}>2022</option>
            </select>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Baixar Todos
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <StatCard
            title="Total Bruto (Ano)"
            value={totalBruto.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Total Líquido (Ano)"
            value={totalLiquido.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Total Deduções"
            value={totalDeducoes.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<TrendingDown className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Holerites"
            value={filteredPayslips.length.toString()}
            changeLabel="no período"
            icon={<FileText className="h-5 w-5" />}
          />
        </StatGrid>

        {/* Chart */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Evolução Salarial
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={salaryTrendData}>
                  <defs>
                    <linearGradient id="colorBruto" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorLiquido" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
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
                    formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  />
                  <Area
                    type="monotone"
                    dataKey="bruto"
                    name="Bruto"
                    stroke="#6366f1"
                    fillOpacity={1}
                    fill="url(#colorBruto)"
                  />
                  <Area
                    type="monotone"
                    dataKey="liquido"
                    name="Líquido"
                    stroke="#10b981"
                    fillOpacity={1}
                    fill="url(#colorLiquido)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Payslips List */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Histórico de Contracheques
            </h3>
          </CardHeader>
          <CardBody className="space-y-3">
            {filteredPayslips.map((payslip, index) => (
              <motion.div
                key={payslip.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-bg-tertiary rounded-xl hover:bg-bg-hover transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-accent-primary/20">
                      <DollarSign className="h-6 w-6 text-accent-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-text-primary">
                          {payslip.month}/{payslip.year}
                        </h4>
                        <Badge variant={getTypeInfo(payslip.type).color} size="sm">
                          {getTypeInfo(payslip.type).label}
                        </Badge>
                      </div>
                      <p className="text-sm text-text-secondary">
                        Pago em {new Date(payslip.paymentDate).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-8">
                    <div className="text-right">
                      <p className="text-sm text-text-secondary">Bruto</p>
                      <p className="font-semibold text-text-primary">
                        {payslip.grossSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-text-secondary">Deduções</p>
                      <p className="font-semibold text-accent-danger">
                        - {payslip.deductions.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-text-secondary">Líquido</p>
                      <p className="font-bold text-accent-success text-lg">
                        {payslip.netSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" onClick={() => handleViewDetails(payslip)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Printer className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </CardBody>
        </Card>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={`Contracheque ${selectedPayslip?.reference}`}
          size="lg"
        >
          {selectedPayslip && (
            <div className="space-y-6">
              {/* Header Info */}
              <div className="grid grid-cols-3 gap-4 p-4 bg-bg-tertiary rounded-lg">
                <div>
                  <p className="text-sm text-text-secondary">Referência</p>
                  <p className="font-semibold text-text-primary">{selectedPayslip.reference}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Data de Pagamento</p>
                  <p className="font-semibold text-text-primary">
                    {new Date(selectedPayslip.paymentDate).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Tipo</p>
                  <Badge variant={getTypeInfo(selectedPayslip.type).color}>
                    {getTypeInfo(selectedPayslip.type).label}
                  </Badge>
                </div>
              </div>

              {/* Proventos */}
              <div>
                <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                  <Plus className="h-4 w-4 text-accent-success" />
                  Proventos
                </h4>
                <div className="bg-bg-tertiary rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border-subtle">
                        <th className="text-left p-3 text-sm text-text-secondary">Descrição</th>
                        <th className="text-right p-3 text-sm text-text-secondary">Referência</th>
                        <th className="text-right p-3 text-sm text-text-secondary">Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedPayslip.details.earnings.map((item, index) => (
                        <tr key={index} className="border-b border-border-subtle last:border-0">
                          <td className="p-3 text-text-primary">{item.description}</td>
                          <td className="p-3 text-text-secondary text-right">{item.reference || '-'}</td>
                          <td className="p-3 text-accent-success text-right font-medium">
                            {item.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="bg-accent-success/10">
                        <td colSpan={2} className="p-3 font-semibold text-text-primary">Total Proventos</td>
                        <td className="p-3 font-bold text-accent-success text-right">
                          {selectedPayslip.grossSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              {/* Descontos */}
              <div>
                <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                  <Minus className="h-4 w-4 text-accent-danger" />
                  Descontos
                </h4>
                <div className="bg-bg-tertiary rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border-subtle">
                        <th className="text-left p-3 text-sm text-text-secondary">Descrição</th>
                        <th className="text-right p-3 text-sm text-text-secondary">Referência</th>
                        <th className="text-right p-3 text-sm text-text-secondary">Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedPayslip.details.deductions.map((item, index) => (
                        <tr key={index} className="border-b border-border-subtle last:border-0">
                          <td className="p-3 text-text-primary">{item.description}</td>
                          <td className="p-3 text-text-secondary text-right">{item.reference || '-'}</td>
                          <td className="p-3 text-accent-danger text-right font-medium">
                            - {item.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="bg-accent-danger/10">
                        <td colSpan={2} className="p-3 font-semibold text-text-primary">Total Descontos</td>
                        <td className="p-3 font-bold text-accent-danger text-right">
                          - {selectedPayslip.deductions.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              {/* Totals */}
              <div className="p-4 bg-gradient-to-r from-accent-primary/20 to-accent-success/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-lg font-semibold text-text-primary">Valor Líquido</span>
                  <span className="text-2xl font-bold text-accent-success">
                    {selectedPayslip.netSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3">
                <Button variant="outline">
                  <Printer className="h-4 w-4 mr-2" />
                  Imprimir
                </Button>
                <Button variant="primary">
                  <Download className="h-4 w-4 mr-2" />
                  Baixar PDF
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}

export default PayslipsPage;
