'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Zap,
  Play,
  Save,
  ArrowLeft,
  Plus,
  Trash2,
  Settings,
  GitBranch,
  Mail,
  MessageSquare,
  Bell,
  Database,
  Clock,
  Calendar,
  Filter,
  CheckCircle,
  ArrowRight,
  ChevronDown,
  Copy,
  Workflow,
  AlertTriangle,
  FileText,
  Users,
  DollarSign,
  Send,
  Webhook
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { MainLayout } from '../../layouts/MainLayout';

// Types
interface WorkflowStep {
  id: string;
  type: 'trigger' | 'condition' | 'action' | 'delay';
  name: string;
  icon: React.ElementType;
  config: Record<string, unknown>;
  connections: string[];
}

interface TriggerOption {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  category: string;
}

interface ActionOption {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  category: string;
}

// Available Triggers
const triggers: TriggerOption[] = [
  { id: 'lead_created', name: 'Lead Criado', description: 'Quando um novo lead é cadastrado', icon: Users, category: 'CRM' },
  { id: 'lead_qualified', name: 'Lead Qualificado', description: 'Quando um lead é qualificado', icon: CheckCircle, category: 'CRM' },
  { id: 'contract_signed', name: 'Contrato Assinado', description: 'Quando um contrato é assinado', icon: FileText, category: 'CRM' },
  { id: 'invoice_created', name: 'Fatura Criada', description: 'Quando uma fatura é gerada', icon: DollarSign, category: 'Financeiro' },
  { id: 'payment_received', name: 'Pagamento Recebido', description: 'Quando um pagamento é confirmado', icon: DollarSign, category: 'Financeiro' },
  { id: 'payment_overdue', name: 'Pagamento Atrasado', description: 'Quando uma fatura vence', icon: AlertTriangle, category: 'Financeiro' },
  { id: 'employee_hired', name: 'Funcionário Contratado', description: 'Quando novo funcionário é admitido', icon: Users, category: 'RH' },
  { id: 'employee_birthday', name: 'Aniversário', description: 'No aniversário do funcionário', icon: Calendar, category: 'RH' },
  { id: 'schedule', name: 'Agendamento', description: 'Executa em horário específico', icon: Clock, category: 'Sistema' },
  { id: 'webhook', name: 'Webhook', description: 'Quando webhook é chamado', icon: Webhook, category: 'Sistema' }
];

// Available Actions
const actions: ActionOption[] = [
  { id: 'send_email', name: 'Enviar Email', description: 'Envia email personalizado', icon: Mail, category: 'Comunicação' },
  { id: 'send_whatsapp', name: 'Enviar WhatsApp', description: 'Envia mensagem via WhatsApp', icon: MessageSquare, category: 'Comunicação' },
  { id: 'send_notification', name: 'Notificação', description: 'Envia notificação no sistema', icon: Bell, category: 'Comunicação' },
  { id: 'create_task', name: 'Criar Tarefa', description: 'Cria uma nova tarefa', icon: CheckCircle, category: 'Tarefas' },
  { id: 'update_record', name: 'Atualizar Registro', description: 'Atualiza dados no sistema', icon: Database, category: 'Dados' },
  { id: 'create_record', name: 'Criar Registro', description: 'Cria novo registro', icon: Plus, category: 'Dados' },
  { id: 'call_webhook', name: 'Chamar Webhook', description: 'Faz chamada HTTP externa', icon: Webhook, category: 'Integração' },
  { id: 'delay', name: 'Aguardar', description: 'Aguarda tempo específico', icon: Clock, category: 'Controle' },
  { id: 'condition', name: 'Condição', description: 'Executa condicionalmente', icon: GitBranch, category: 'Controle' }
];

// Mock workflow for editing
const initialSteps: WorkflowStep[] = [
  {
    id: '1',
    type: 'trigger',
    name: 'Lead Qualificado',
    icon: CheckCircle,
    config: { event: 'lead.qualified' },
    connections: ['2']
  },
  {
    id: '2',
    type: 'condition',
    name: 'Verificar Valor',
    icon: GitBranch,
    config: { field: 'value', operator: 'greater_than', value: 10000 },
    connections: ['3', '4']
  },
  {
    id: '3',
    type: 'action',
    name: 'Notificar Gerente',
    icon: Bell,
    config: { recipient: 'manager', message: 'Lead de alto valor qualificado!' },
    connections: []
  },
  {
    id: '4',
    type: 'action',
    name: 'Enviar Email',
    icon: Mail,
    config: { template: 'lead_qualified', to: '{{lead.email}}' },
    connections: []
  }
];

export function WorkflowBuilderPage() {
  const [workflowName, setWorkflowName] = useState('Notificação de Lead Qualificado');
  const [workflowDescription, setWorkflowDescription] = useState('Envia notificação ao vendedor quando lead é qualificado');
  const [steps, setSteps] = useState<WorkflowStep[]>(initialSteps);
  const [selectedStep, setSelectedStep] = useState<WorkflowStep | null>(null);
  const [showTriggerModal, setShowTriggerModal] = useState(false);
  const [showActionModal, setShowActionModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);

  const getStepTypeColor = (type: WorkflowStep['type']) => {
    const colors = {
      trigger: 'primary',
      condition: 'warning',
      action: 'success',
      delay: 'info'
    };
    return colors[type] as 'primary' | 'warning' | 'success' | 'info';
  };

  const handleAddStep = (type: 'trigger' | 'action') => {
    if (type === 'trigger') {
      setShowTriggerModal(true);
    } else {
      setShowActionModal(true);
    }
  };

  const handleSelectTrigger = (trigger: TriggerOption) => {
    const newStep: WorkflowStep = {
      id: Date.now().toString(),
      type: 'trigger',
      name: trigger.name,
      icon: trigger.icon,
      config: { eventId: trigger.id },
      connections: []
    };
    setSteps([newStep, ...steps.filter(s => s.type !== 'trigger')]);
    setShowTriggerModal(false);
  };

  const handleSelectAction = (action: ActionOption) => {
    const newStep: WorkflowStep = {
      id: Date.now().toString(),
      type: action.id === 'condition' ? 'condition' : action.id === 'delay' ? 'delay' : 'action',
      name: action.name,
      icon: action.icon,
      config: { actionId: action.id },
      connections: []
    };
    setSteps([...steps, newStep]);
    setShowActionModal(false);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar
            </Button>
            <div>
              <Input
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                className="text-xl font-bold bg-transparent border-0 p-0 h-auto focus:ring-0"
              />
              <Input
                value={workflowDescription}
                onChange={(e) => setWorkflowDescription(e.target.value)}
                className="text-sm text-text-secondary bg-transparent border-0 p-0 h-auto focus:ring-0 mt-1"
                placeholder="Adicione uma descrição..."
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Play className="h-4 w-4 mr-2" />
              Testar
            </Button>
            <Button variant="primary">
              <Save className="h-4 w-4 mr-2" />
              Salvar
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Workflow Canvas */}
          <div className="lg:col-span-3">
            <Card className="min-h-[600px]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Fluxo de Trabalho
                  </h3>
                  <div className="flex items-center gap-2">
                    <Badge variant="success">Ativo</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="relative space-y-4">
                  {/* Trigger */}
                  {steps.filter(s => s.type === 'trigger').length === 0 ? (
                    <motion.button
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      onClick={() => handleAddStep('trigger')}
                      className="w-full p-6 border-2 border-dashed border-border-default rounded-xl text-center hover:border-accent-primary/50 transition-colors"
                    >
                      <Zap className="h-8 w-8 text-text-secondary mx-auto mb-2" />
                      <p className="text-text-primary font-medium">Adicionar Gatilho</p>
                      <p className="text-sm text-text-secondary">O que inicia esta automação?</p>
                    </motion.button>
                  ) : null}

                  {/* Steps */}
                  {steps.map((step, index) => {
                    const StepIcon = step.icon;
                    const color = getStepTypeColor(step.type);
                    return (
                      <motion.div
                        key={step.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="relative"
                      >
                        {/* Connection Line */}
                        {index > 0 && (
                          <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-0.5 h-4 bg-border-default" />
                        )}

                        <div
                          onClick={() => { setSelectedStep(step); setShowConfigModal(true); }}
                          className={`
                            p-4 rounded-xl border-2 cursor-pointer transition-all
                            ${selectedStep?.id === step.id
                              ? `border-accent-${color} bg-accent-${color}/10`
                              : 'border-border-default hover:border-accent-primary/50'
                            }
                          `}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className={`p-2 rounded-lg bg-accent-${color}/20`}>
                                <StepIcon className={`h-5 w-5 text-accent-${color}`} />
                              </div>
                              <div>
                                <div className="flex items-center gap-2">
                                  <p className="font-medium text-text-primary">{step.name}</p>
                                  <Badge variant={color} size="sm">
                                    {step.type === 'trigger' ? 'Gatilho' :
                                     step.type === 'condition' ? 'Condição' :
                                     step.type === 'delay' ? 'Aguardar' : 'Ação'}
                                  </Badge>
                                </div>
                                <p className="text-xs text-text-secondary mt-1">
                                  {step.type === 'trigger' && 'Quando o evento ocorrer...'}
                                  {step.type === 'condition' && 'Se a condição for verdadeira...'}
                                  {step.type === 'action' && 'Executar ação...'}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button variant="ghost" size="sm">
                                <Settings className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="sm">
                                <Trash2 className="h-4 w-4 text-accent-danger" />
                              </Button>
                            </div>
                          </div>

                          {/* Condition Branches */}
                          {step.type === 'condition' && (
                            <div className="mt-4 grid grid-cols-2 gap-4">
                              <div className="p-3 bg-accent-success/10 border border-accent-success/30 rounded-lg">
                                <p className="text-xs text-accent-success font-medium mb-1">Se VERDADEIRO</p>
                                <p className="text-xs text-text-secondary">→ Próximas ações...</p>
                              </div>
                              <div className="p-3 bg-accent-danger/10 border border-accent-danger/30 rounded-lg">
                                <p className="text-xs text-accent-danger font-medium mb-1">Se FALSO</p>
                                <p className="text-xs text-text-secondary">→ Próximas ações...</p>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Add Step Button */}
                        {index === steps.length - 1 && (
                          <motion.button
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            onClick={() => handleAddStep('action')}
                            className="mt-4 w-full p-4 border-2 border-dashed border-border-default rounded-xl text-center hover:border-accent-primary/50 transition-colors flex items-center justify-center gap-2"
                          >
                            <Plus className="h-5 w-5 text-text-secondary" />
                            <span className="text-text-secondary">Adicionar Etapa</span>
                          </motion.button>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Sidebar - Templates & Help */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">
                  Ações Rápidas
                </h3>
              </CardHeader>
              <CardBody className="space-y-2">
                {[
                  { icon: Mail, label: 'Email', color: 'primary' },
                  { icon: MessageSquare, label: 'WhatsApp', color: 'success' },
                  { icon: Bell, label: 'Notificação', color: 'warning' },
                  { icon: Clock, label: 'Aguardar', color: 'info' },
                  { icon: GitBranch, label: 'Condição', color: 'secondary' }
                ].map((action) => (
                  <button
                    key={action.label}
                    className="w-full p-3 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors flex items-center gap-3"
                  >
                    <div className={`p-2 rounded-lg bg-accent-${action.color}/20`}>
                      <action.icon className={`h-4 w-4 text-accent-${action.color}`} />
                    </div>
                    <span className="text-text-primary">{action.label}</span>
                  </button>
                ))}
              </CardBody>
            </Card>

            {/* Templates */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">
                  Templates
                </h3>
              </CardHeader>
              <CardBody className="space-y-2">
                {[
                  'Boas-vindas ao Cliente',
                  'Follow-up de Lead',
                  'Cobrança Automática',
                  'Aniversário Funcionário'
                ].map((template) => (
                  <button
                    key={template}
                    className="w-full p-3 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors text-left"
                  >
                    <p className="text-text-primary text-sm">{template}</p>
                  </button>
                ))}
              </CardBody>
            </Card>

            {/* Variables */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">
                  Variáveis Disponíveis
                </h3>
              </CardHeader>
              <CardBody>
                <div className="space-y-2 text-sm">
                  <code className="block p-2 bg-bg-tertiary rounded text-accent-primary">{'{{lead.name}}'}</code>
                  <code className="block p-2 bg-bg-tertiary rounded text-accent-primary">{'{{lead.email}}'}</code>
                  <code className="block p-2 bg-bg-tertiary rounded text-accent-primary">{'{{lead.value}}'}</code>
                  <code className="block p-2 bg-bg-tertiary rounded text-accent-primary">{'{{user.name}}'}</code>
                </div>
              </CardBody>
            </Card>
          </div>
        </div>

        {/* Trigger Selection Modal */}
        <Modal
          isOpen={showTriggerModal}
          onClose={() => setShowTriggerModal(false)}
          title="Selecionar Gatilho"
          size="lg"
        >
          <div className="space-y-4">
            <p className="text-text-secondary">
              Escolha o evento que irá iniciar esta automação
            </p>
            <div className="grid grid-cols-2 gap-3">
              {triggers.map((trigger) => (
                <button
                  key={trigger.id}
                  onClick={() => handleSelectTrigger(trigger)}
                  className="p-4 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors text-left"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-accent-primary/20">
                      <trigger.icon className="h-5 w-5 text-accent-primary" />
                    </div>
                    <Badge variant="secondary" size="sm">{trigger.category}</Badge>
                  </div>
                  <p className="font-medium text-text-primary">{trigger.name}</p>
                  <p className="text-xs text-text-secondary mt-1">{trigger.description}</p>
                </button>
              ))}
            </div>
          </div>
        </Modal>

        {/* Action Selection Modal */}
        <Modal
          isOpen={showActionModal}
          onClose={() => setShowActionModal(false)}
          title="Adicionar Ação"
          size="lg"
        >
          <div className="space-y-4">
            <p className="text-text-secondary">
              Escolha a ação a ser executada
            </p>
            <div className="grid grid-cols-2 gap-3">
              {actions.map((action) => (
                <button
                  key={action.id}
                  onClick={() => handleSelectAction(action)}
                  className="p-4 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors text-left"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-accent-success/20">
                      <action.icon className="h-5 w-5 text-accent-success" />
                    </div>
                    <Badge variant="secondary" size="sm">{action.category}</Badge>
                  </div>
                  <p className="font-medium text-text-primary">{action.name}</p>
                  <p className="text-xs text-text-secondary mt-1">{action.description}</p>
                </button>
              ))}
            </div>
          </div>
        </Modal>

        {/* Step Configuration Modal */}
        <Modal
          isOpen={showConfigModal}
          onClose={() => setShowConfigModal(false)}
          title={`Configurar: ${selectedStep?.name}`}
          size="md"
        >
          {selectedStep && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Nome da Etapa
                </label>
                <Input defaultValue={selectedStep.name} />
              </div>

              {selectedStep.type === 'action' && selectedStep.icon === Mail && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Destinatário
                    </label>
                    <Input placeholder="{{lead.email}}" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Assunto
                    </label>
                    <Input placeholder="Assunto do email" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Conteúdo
                    </label>
                    <textarea
                      className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                      rows={4}
                      placeholder="Conteúdo do email..."
                    />
                  </div>
                </>
              )}

              {selectedStep.type === 'condition' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Campo
                    </label>
                    <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                      <option value="value">Valor do Lead</option>
                      <option value="source">Origem</option>
                      <option value="status">Status</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Operador
                    </label>
                    <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                      <option value="equals">Igual a</option>
                      <option value="not_equals">Diferente de</option>
                      <option value="greater_than">Maior que</option>
                      <option value="less_than">Menor que</option>
                      <option value="contains">Contém</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Valor
                    </label>
                    <Input placeholder="Valor para comparação" />
                  </div>
                </>
              )}

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="ghost" onClick={() => setShowConfigModal(false)}>
                  Cancelar
                </Button>
                <Button variant="primary">
                  Salvar Configuração
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}

export default WorkflowBuilderPage;
