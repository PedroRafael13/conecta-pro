'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  Building2,
  Users,
  Shield,
  Bell,
  Palette,
  Globe,
  Database,
  Key,
  Mail,
  Smartphone,
  CreditCard,
  FileText,
  Clock,
  ChevronRight,
  Save,
  RefreshCw,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  SimpleTabBar,
  Select,
} from '@/design-system/components';

// Types
interface SettingSection {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  badge?: string;
}

const settingSections: SettingSection[] = [
  { id: 'company', title: 'Dados da Empresa', description: 'Informações cadastrais e documentos', icon: Building2 },
  { id: 'users', title: 'Usuários e Permissões', description: 'Gerenciar acessos e papéis', icon: Users, badge: '12 usuários' },
  { id: 'security', title: 'Segurança', description: 'Políticas de senha e autenticação', icon: Shield },
  { id: 'notifications', title: 'Notificações', description: 'Configurar alertas e e-mails', icon: Bell },
  { id: 'integrations', title: 'Integrações', description: 'APIs e conexões externas', icon: Globe },
  { id: 'billing', title: 'Faturamento', description: 'Plano e forma de pagamento', icon: CreditCard },
];

export function SettingsPage() {
  const [selectedSection, setSelectedSection] = useState('company');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 1500);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Configurações
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie as configurações do sistema
            </p>
          </div>
          <Button
            variant="primary"
            leftIcon={isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? 'Salvando...' : 'Salvar Alterações'}
          </Button>
        </div>

        <div className="grid grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="col-span-1"
          >
            <Card>
              <CardBody className="p-2">
                <nav className="space-y-1">
                  {settingSections.map((section) => {
                    const Icon = section.icon;
                    const isActive = selectedSection === section.id;
                    return (
                      <button
                        key={section.id}
                        onClick={() => setSelectedSection(section.id)}
                        className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors text-left ${
                          isActive
                            ? 'bg-accent-primary/10 text-accent-primary'
                            : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm">{section.title}</p>
                          {section.badge && (
                            <p className="text-xs text-text-muted">{section.badge}</p>
                          )}
                        </div>
                        <ChevronRight className={`w-4 h-4 transition-transform ${isActive ? 'rotate-90' : ''}`} />
                      </button>
                    );
                  })}
                </nav>
              </CardBody>
            </Card>
          </motion.div>

          {/* Content Area */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-3"
          >
            {selectedSection === 'company' && (
              <Card>
                <CardHeader
                  title="Dados da Empresa"
                  subtitle="Informações cadastrais da sua empresa"
                />
                <CardBody className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <Input label="Razão Social" defaultValue="Conecta Plus Segurança Ltda" />
                    <Input label="Nome Fantasia" defaultValue="Conecta Plus" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Input label="CNPJ" defaultValue="12.345.678/0001-90" />
                    <Input label="Inscrição Estadual" defaultValue="123.456.789.000" />
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <Input label="CEP" defaultValue="01310-100" className="col-span-1" />
                    <Input label="Logradouro" defaultValue="Av. Paulista" className="col-span-2" />
                  </div>
                  <div className="grid grid-cols-4 gap-4">
                    <Input label="Número" defaultValue="1000" />
                    <Input label="Complemento" defaultValue="12º andar" />
                    <Input label="Cidade" defaultValue="São Paulo" />
                    <Input label="Estado" defaultValue="SP" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Input label="Telefone" defaultValue="(11) 3456-7890" />
                    <Input label="E-mail" defaultValue="contato@conectaplus.com.br" />
                  </div>
                </CardBody>
              </Card>
            )}

            {selectedSection === 'users' && (
              <Card>
                <CardHeader
                  title="Usuários e Permissões"
                  subtitle="Gerenciar acessos ao sistema"
                  action={<Button variant="primary" size="sm">Novo Usuário</Button>}
                />
                <CardBody>
                  <div className="space-y-4">
                    {[
                      { name: 'Admin Sistema', email: 'admin@conectaplus.com.br', role: 'Administrador', status: 'active' },
                      { name: 'Ana Paula Costa', email: 'ana.paula@conectaplus.com.br', role: 'Gerente Operacional', status: 'active' },
                      { name: 'Carlos Eduardo', email: 'carlos@conectaplus.com.br', role: 'Supervisor Campo', status: 'active' },
                      { name: 'Roberto Silva', email: 'roberto@conectaplus.com.br', role: 'Técnico', status: 'active' },
                      { name: 'Maria Santos', email: 'maria@conectaplus.com.br', role: 'Financeiro', status: 'inactive' },
                    ].map((user, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-accent-primary/20 flex items-center justify-center">
                            <span className="text-sm font-medium text-accent-primary">
                              {user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-text-primary">{user.name}</p>
                            <p className="text-xs text-text-muted">{user.email}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge variant="info">{user.role}</Badge>
                          <Badge variant={user.status === 'active' ? 'success' : 'danger'}>
                            {user.status === 'active' ? 'Ativo' : 'Inativo'}
                          </Badge>
                          <Button variant="ghost" size="sm">Editar</Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            )}

            {selectedSection === 'security' && (
              <Card>
                <CardHeader
                  title="Segurança"
                  subtitle="Políticas de segurança do sistema"
                />
                <CardBody className="space-y-6">
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <p className="font-medium text-text-primary">Autenticação de Dois Fatores</p>
                        <p className="text-xs text-text-muted">Adicione uma camada extra de segurança</p>
                      </div>
                      <Badge variant="success">Ativo</Badge>
                    </div>
                    <Button variant="secondary" size="sm">Configurar</Button>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Input label="Tamanho mínimo de senha" type="number" defaultValue="8" />
                    <Input label="Expiração de senha (dias)" type="number" defaultValue="90" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Input label="Tentativas máximas de login" type="number" defaultValue="5" />
                    <Input label="Tempo de bloqueio (minutos)" type="number" defaultValue="30" />
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-text-primary">Registro de Atividades (Audit Log)</p>
                        <p className="text-xs text-text-muted">Rastrear todas as ações dos usuários</p>
                      </div>
                      <Badge variant="success">Ativo</Badge>
                    </div>
                  </div>
                </CardBody>
              </Card>
            )}

            {selectedSection === 'notifications' && (
              <Card>
                <CardHeader
                  title="Notificações"
                  subtitle="Configure como deseja receber alertas"
                />
                <CardBody className="space-y-6">
                  <div className="space-y-4">
                    {[
                      { title: 'Alertas de Segurança', desc: 'Ocorrências críticas e invasões', email: true, push: true, sms: true },
                      { title: 'Financeiro', desc: 'Vencimentos e pagamentos', email: true, push: true, sms: false },
                      { title: 'Operacional', desc: 'Escalas e ordens de serviço', email: true, push: false, sms: false },
                      { title: 'Sistema', desc: 'Manutenções e atualizações', email: true, push: false, sms: false },
                    ].map((item, idx) => (
                      <div key={idx} className="p-4 bg-bg-tertiary rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-text-primary">{item.title}</p>
                            <p className="text-xs text-text-muted">{item.desc}</p>
                          </div>
                          <div className="flex items-center gap-4">
                            <label className="flex items-center gap-2">
                              <input type="checkbox" defaultChecked={item.email} className="rounded" />
                              <Mail className="w-4 h-4 text-text-muted" />
                            </label>
                            <label className="flex items-center gap-2">
                              <input type="checkbox" defaultChecked={item.push} className="rounded" />
                              <Bell className="w-4 h-4 text-text-muted" />
                            </label>
                            <label className="flex items-center gap-2">
                              <input type="checkbox" defaultChecked={item.sms} className="rounded" />
                              <Smartphone className="w-4 h-4 text-text-muted" />
                            </label>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            )}

            {selectedSection === 'integrations' && (
              <Card>
                <CardHeader
                  title="Integrações"
                  subtitle="Conexões com sistemas externos"
                />
                <CardBody className="space-y-4">
                  {[
                    { name: 'WhatsApp Business', status: 'connected', icon: Smartphone },
                    { name: 'Open Banking', status: 'connected', icon: CreditCard },
                    { name: 'eSocial', status: 'pending', icon: FileText },
                    { name: 'SEFAZ (NF-e)', status: 'disconnected', icon: Globe },
                  ].map((integration, idx) => {
                    const Icon = integration.icon;
                    return (
                      <div key={idx} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-bg-primary rounded-lg">
                            <Icon className="w-5 h-5 text-text-muted" />
                          </div>
                          <div>
                            <p className="font-medium text-text-primary">{integration.name}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge variant={
                            integration.status === 'connected' ? 'success' :
                            integration.status === 'pending' ? 'warning' : 'danger'
                          }>
                            {integration.status === 'connected' ? 'Conectado' :
                             integration.status === 'pending' ? 'Pendente' : 'Desconectado'}
                          </Badge>
                          <Button variant="secondary" size="sm">
                            {integration.status === 'connected' ? 'Configurar' : 'Conectar'}
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </CardBody>
              </Card>
            )}

            {selectedSection === 'billing' && (
              <Card>
                <CardHeader
                  title="Faturamento"
                  subtitle="Informações do seu plano e pagamento"
                />
                <CardBody className="space-y-6">
                  <div className="p-6 bg-gradient-to-r from-accent-primary/20 to-accent-secondary/20 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <Badge variant="primary">Plano Enterprise</Badge>
                        <p className="text-2xl font-bold text-text-primary mt-2">R$ 2.499/mês</p>
                        <p className="text-xs text-text-muted">Próxima cobrança: 01/02/2026</p>
                      </div>
                      <Button variant="secondary">Alterar Plano</Button>
                    </div>
                    <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border-subtle">
                      <div>
                        <p className="text-sm text-text-muted">Usuários</p>
                        <p className="font-medium text-text-primary">12 / Ilimitado</p>
                      </div>
                      <div>
                        <p className="text-sm text-text-muted">Armazenamento</p>
                        <p className="font-medium text-text-primary">45GB / 100GB</p>
                      </div>
                      <div>
                        <p className="text-sm text-text-muted">API Calls</p>
                        <p className="font-medium text-text-primary">125k / Ilimitado</p>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-text-primary mb-3">Método de Pagamento</h4>
                    <div className="flex items-center gap-3 p-4 bg-bg-tertiary rounded-lg">
                      <CreditCard className="w-5 h-5 text-text-muted" />
                      <div>
                        <p className="font-medium text-text-primary">•••• •••• •••• 4242</p>
                        <p className="text-xs text-text-muted">Válido até 12/2028</p>
                      </div>
                      <Button variant="ghost" size="sm" className="ml-auto">Alterar</Button>
                    </div>
                  </div>
                </CardBody>
              </Card>
            )}
          </motion.div>
        </div>
      </div>
    </MainLayout>
  );
}
