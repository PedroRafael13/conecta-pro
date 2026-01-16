'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  FileText,
  Calendar,
  DollarSign,
  Clock,
  Bell,
  Download,
  Upload,
  Eye,
  Edit2,
  CheckCircle,
  AlertTriangle,
  ChevronRight,
  Briefcase,
  Heart,
  GraduationCap,
  Building,
  MapPin,
  Phone,
  Mail,
  Award,
  TrendingUp
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Badge } from '../../design-system/components/Badge';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { MainLayout } from '../../layouts/MainLayout';

// Mock Data - Employee Info
const employeeData = {
  id: 'EMP-001',
  name: 'João Silva Santos',
  email: 'joao.santos@empresa.com.br',
  phone: '(11) 99999-1234',
  cpf: '123.456.789-00',
  position: 'Analista de Sistemas Sênior',
  department: 'Tecnologia da Informação',
  admissionDate: '2021-03-15',
  manager: 'Maria Fernanda Costa',
  workLocation: 'Matriz - São Paulo',
  contractType: 'CLT',
  workSchedule: '09:00 - 18:00',
  salary: 12500,
  avatarUrl: null
};

const vacationBalance = {
  available: 15,
  scheduled: 10,
  used: 5,
  periodStart: '2024-03-15',
  periodEnd: '2025-03-14'
};

const recentPayslips = [
  { month: 'Janeiro/2024', grossSalary: 12500, netSalary: 9850, date: '2024-01-31' },
  { month: 'Dezembro/2023', grossSalary: 25000, netSalary: 19700, date: '2023-12-20', bonus: true },
  { month: 'Novembro/2023', grossSalary: 12500, netSalary: 9850, date: '2023-11-30' }
];

const pendingDocuments = [
  { id: '1', name: 'Atualização cadastral anual', dueDate: '2024-03-01', type: 'update' },
  { id: '2', name: 'Declaração de dependentes IR', dueDate: '2024-02-28', type: 'document' }
];

const announcements = [
  { id: '1', title: 'Novo plano de saúde', date: '2024-02-15', priority: 'high', read: false },
  { id: '2', title: 'Atualização do código de conduta', date: '2024-02-10', priority: 'medium', read: true },
  { id: '3', title: 'Calendário de feriados 2024', date: '2024-01-20', priority: 'low', read: true }
];

const benefits = [
  { name: 'Plano de Saúde', provider: 'Unimed', status: 'active', icon: Heart },
  { name: 'Vale Refeição', provider: 'Sodexo', value: 35, status: 'active', icon: DollarSign },
  { name: 'Seguro de Vida', provider: 'Porto Seguro', status: 'active', icon: Award },
  { name: 'Auxílio Educação', provider: 'Empresa', value: 500, status: 'active', icon: GraduationCap }
];

const timeTracking = {
  today: { entry: '08:55', lunch: '12:00', lunchReturn: '13:00', exit: null },
  hoursWorked: '6h 15min',
  balance: '+2h 30min'
};

export function EmployeePortalPage() {
  const yearsEmployed = Math.floor(
    (new Date().getTime() - new Date(employeeData.admissionDate).getTime()) / (1000 * 60 * 60 * 24 * 365)
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-white text-xl font-bold">
              {employeeData.name.split(' ').map(n => n[0]).slice(0, 2).join('')}
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold text-text-primary">
                Olá, {employeeData.name.split(' ')[0]}!
              </h1>
              <p className="text-text-secondary">
                {employeeData.position} | {employeeData.department}
              </p>
              <p className="text-sm text-text-secondary mt-1">
                {yearsEmployed} ano{yearsEmployed !== 1 ? 's' : ''} de empresa
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Edit2 className="h-4 w-4 mr-2" />
              Atualizar Dados
            </Button>
            <Button variant="ghost" className="relative">
              <Bell className="h-5 w-5" />
              {announcements.filter(a => !a.read).length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-accent-danger rounded-full text-xs text-white flex items-center justify-center">
                  {announcements.filter(a => !a.read).length}
                </span>
              )}
            </Button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { icon: FileText, label: 'Meus Contracheques', href: '/hr-portal/payslips', color: 'primary' },
            { icon: Calendar, label: 'Solicitar Férias', href: '/hr-portal/vacation', color: 'success' },
            { icon: Clock, label: 'Registro de Ponto', href: '/hr-portal/timesheet', color: 'warning' },
            { icon: FileText, label: 'Meus Documentos', href: '/hr-portal/documents', color: 'info' }
          ].map((action, index) => (
            <motion.a
              key={action.label}
              href={action.href}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 bg-bg-secondary rounded-xl border border-border-subtle hover:border-accent-primary/50 transition-all group"
            >
              <div className={`w-12 h-12 rounded-xl bg-accent-${action.color}/20 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                <action.icon className={`h-6 w-6 text-accent-${action.color}`} />
              </div>
              <p className="font-medium text-text-primary">{action.label}</p>
            </motion.a>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Pending Actions */}
            {pendingDocuments.length > 0 && (
              <Card className="border-accent-warning/30 bg-accent-warning/5">
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-accent-warning" />
                    <h3 className="text-lg font-semibold text-text-primary">
                      Pendências
                    </h3>
                  </div>
                </CardHeader>
                <CardBody className="space-y-3">
                  {pendingDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-accent-warning/20">
                          <FileText className="h-4 w-4 text-accent-warning" />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{doc.name}</p>
                          <p className="text-xs text-text-secondary">
                            Prazo: {new Date(doc.dueDate).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        Resolver
                      </Button>
                    </div>
                  ))}
                </CardBody>
              </Card>
            )}

            {/* Recent Payslips */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Últimos Contracheques
                  </h3>
                  <Button variant="ghost" size="sm">
                    Ver todos
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              </CardHeader>
              <CardBody className="space-y-3">
                {recentPayslips.map((payslip, index) => (
                  <motion.div
                    key={payslip.month}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="p-2 rounded-lg bg-accent-primary/20">
                        <DollarSign className="h-5 w-5 text-accent-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{payslip.month}</p>
                        {payslip.bonus && (
                          <Badge variant="success" size="sm">13º Salário</Badge>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-text-primary">
                        {payslip.netSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <p className="text-xs text-text-secondary">
                        Bruto: {payslip.grossSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  </motion.div>
                ))}
              </CardBody>
            </Card>

            {/* Time Tracking */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Registro de Ponto - Hoje
                  </h3>
                  <Button variant="primary" size="sm">
                    <Clock className="h-4 w-4 mr-2" />
                    Registrar Saída
                  </Button>
                </div>
              </CardHeader>
              <CardBody>
                <div className="grid grid-cols-4 gap-4 mb-4">
                  {[
                    { label: 'Entrada', time: timeTracking.today.entry, icon: '🌅' },
                    { label: 'Saída Almoço', time: timeTracking.today.lunch, icon: '🍽️' },
                    { label: 'Retorno', time: timeTracking.today.lunchReturn, icon: '🔙' },
                    { label: 'Saída', time: timeTracking.today.exit || '--:--', icon: '🌙' }
                  ].map((entry) => (
                    <div key={entry.label} className="text-center p-3 bg-bg-tertiary rounded-lg">
                      <p className="text-2xl mb-1">{entry.icon}</p>
                      <p className="text-xs text-text-secondary">{entry.label}</p>
                      <p className="font-mono font-semibold text-text-primary">{entry.time}</p>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                  <div>
                    <p className="text-sm text-text-secondary">Horas trabalhadas hoje</p>
                    <p className="text-lg font-semibold text-text-primary">{timeTracking.hoursWorked}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-text-secondary">Banco de horas</p>
                    <p className="text-lg font-semibold text-accent-success">{timeTracking.balance}</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Vacation Balance */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">
                  Saldo de Férias
                </h3>
              </CardHeader>
              <CardBody>
                <div className="text-center mb-4">
                  <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-accent-success/20 to-accent-success/5 mb-3">
                    <span className="text-3xl font-bold text-accent-success">{vacationBalance.available}</span>
                  </div>
                  <p className="text-text-secondary">dias disponíveis</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Agendados</span>
                    <span className="text-text-primary">{vacationBalance.scheduled} dias</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Utilizados</span>
                    <span className="text-text-primary">{vacationBalance.used} dias</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Período aquisitivo</span>
                    <span className="text-text-primary">
                      {new Date(vacationBalance.periodStart).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })} - {new Date(vacationBalance.periodEnd).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                    </span>
                  </div>
                </div>
                <Button variant="primary" className="w-full mt-4">
                  <Calendar className="h-4 w-4 mr-2" />
                  Solicitar Férias
                </Button>
              </CardBody>
            </Card>

            {/* Benefits */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">
                  Meus Benefícios
                </h3>
              </CardHeader>
              <CardBody className="space-y-3">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit.name}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-accent-primary/20">
                        <benefit.icon className="h-4 w-4 text-accent-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary text-sm">{benefit.name}</p>
                        <p className="text-xs text-text-secondary">{benefit.provider}</p>
                      </div>
                    </div>
                    {benefit.value && (
                      <span className="text-sm font-medium text-text-primary">
                        R$ {benefit.value}/dia
                      </span>
                    )}
                    <Badge variant="success" size="sm">Ativo</Badge>
                  </motion.div>
                ))}
              </CardBody>
            </Card>

            {/* Announcements */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Comunicados
                  </h3>
                  <Button variant="ghost" size="sm">
                    Ver todos
                  </Button>
                </div>
              </CardHeader>
              <CardBody className="space-y-3">
                {announcements.slice(0, 3).map((announcement, index) => (
                  <motion.div
                    key={announcement.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      announcement.read ? 'bg-bg-tertiary' : 'bg-accent-primary/10 border border-accent-primary/30'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {!announcement.read && (
                        <div className="w-2 h-2 rounded-full bg-accent-primary mt-2" />
                      )}
                      <div className="flex-1">
                        <p className={`text-sm ${announcement.read ? 'text-text-primary' : 'font-medium text-text-primary'}`}>
                          {announcement.title}
                        </p>
                        <p className="text-xs text-text-secondary mt-1">
                          {new Date(announcement.date).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      {announcement.priority === 'high' && (
                        <Badge variant="danger" size="sm">Importante</Badge>
                      )}
                    </div>
                  </motion.div>
                ))}
              </CardBody>
            </Card>

            {/* Quick Info */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">
                  Informações Rápidas
                </h3>
              </CardHeader>
              <CardBody className="space-y-3">
                <div className="flex items-center gap-3 p-2">
                  <Building className="h-4 w-4 text-text-secondary" />
                  <span className="text-sm text-text-primary">{employeeData.workLocation}</span>
                </div>
                <div className="flex items-center gap-3 p-2">
                  <Clock className="h-4 w-4 text-text-secondary" />
                  <span className="text-sm text-text-primary">{employeeData.workSchedule}</span>
                </div>
                <div className="flex items-center gap-3 p-2">
                  <User className="h-4 w-4 text-text-secondary" />
                  <span className="text-sm text-text-primary">Gestor: {employeeData.manager}</span>
                </div>
                <div className="flex items-center gap-3 p-2">
                  <Mail className="h-4 w-4 text-text-secondary" />
                  <span className="text-sm text-text-primary">{employeeData.email}</span>
                </div>
              </CardBody>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

export default EmployeePortalPage;
