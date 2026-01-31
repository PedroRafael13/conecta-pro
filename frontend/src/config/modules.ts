import { Module, ModuleCategory } from '@/types/modules';

// Definição de todos os módulos do sistema baseado nos endpoints reais
export const modules: Module[] = [
  // === OPERACIONAL ===
  {
    id: 'crm',
    title: 'CRM',
    description: 'Gestão de leads, oportunidades e clientes',
    icon: 'Users',
    href: '/modulos/crm',
    color: 'cyan',
    permissions: ['crm:read'],
    enabled: true,
    subModules: [
      { id: 'leads', title: 'Leads', href: '/modulos/crm/leads', icon: 'UserPlus', permissions: ['crm:leads'] },
      { id: 'oportunidades', title: 'Oportunidades', href: '/modulos/crm/oportunidades', icon: 'Target', permissions: ['crm:oportunidades'] },
      { id: 'clientes', title: 'Clientes', href: '/modulos/crm/clientes', icon: 'Building2', permissions: ['crm:clientes'] },
      { id: 'contatos', title: 'Contatos', href: '/modulos/crm/contatos', icon: 'Contact', permissions: ['crm:contatos'] },
      { id: 'propostas', title: 'Propostas', href: '/modulos/crm/propostas', icon: 'FileText', permissions: ['crm:propostas'] },
    ],
  },
  {
    id: 'services',
    title: 'Serviços',
    description: 'Contratos, ordens de serviço e agendamentos',
    icon: 'Briefcase',
    href: '/modulos/servicos',
    color: 'blue',
    permissions: ['services:read'],
    enabled: true,
    subModules: [
      { id: 'contratos', title: 'Contratos', href: '/modulos/servicos/contratos', icon: 'FileSignature', permissions: ['services:contratos'] },
      { id: 'ordens', title: 'Ordens de Serviço', href: '/modulos/servicos/ordens', icon: 'ClipboardList', permissions: ['services:ordens'] },
      { id: 'agendamentos', title: 'Agendamentos', href: '/modulos/servicos/agendamentos', icon: 'Calendar', permissions: ['services:agendamentos'] },
    ],
  },
  {
    id: 'operacional',
    title: 'Operacional',
    description: 'Escalas, postos e gestão de agentes',
    icon: 'Shield',
    href: '/modulos/operacional',
    color: 'green',
    permissions: ['operacional:read'],
    enabled: true,
    subModules: [
      { id: 'postos', title: 'Postos', href: '/modulos/operacional/postos', icon: 'MapPin', permissions: ['operacional:postos'] },
      { id: 'colaboradores', title: 'Colaboradores', href: '/modulos/operacional/colaboradores', icon: 'UserCheck', permissions: ['operacional:colaboradores'] },
      { id: 'escalas', title: 'Escalas', href: '/modulos/operacional/escalas', icon: 'CalendarDays', permissions: ['operacional:escalas'] },
      { id: 'alocacoes', title: 'Alocações', href: '/modulos/operacional/alocacoes', icon: 'Users', permissions: ['operacional:alocacoes'] },
      { id: 'turnos', title: 'Turnos', href: '/modulos/operacional/turnos', icon: 'Clock', permissions: ['operacional:turnos'] },
      { id: 'ocorrencias', title: 'Ocorrências', href: '/modulos/operacional/ocorrencias', icon: 'AlertTriangle', permissions: ['operacional:ocorrencias'] },
      { id: 'rondas', title: 'Rondas', href: '/modulos/operacional/rondas', icon: 'Route', permissions: ['operacional:rondas'] },
      { id: 'comunicados', title: 'Comunicados', href: '/modulos/operacional/comunicados', icon: 'Bell', permissions: ['operacional:comunicados'] },
      { id: 'notificacoes', title: 'Notificações', href: '/modulos/operacional/notificacoes', icon: 'Bell', permissions: ['operacional:notificacoes'] },
      { id: 'reembolsos', title: 'Reembolsos', href: '/modulos/operacional/reembolsos', icon: 'Receipt', permissions: ['operacional:reembolsos'] },
      { id: 'disciplinar', title: 'Processos Disciplinares', href: '/modulos/operacional/disciplinar', icon: 'FileText', permissions: ['operacional:disciplinar'] },
    ],
  },
  {
    id: 'campo',
    title: 'Campo',
    description: 'App mobile, check-in e monitoramento',
    icon: 'Smartphone',
    href: '/modulos/campo',
    color: 'purple',
    permissions: ['campo:read'],
    enabled: true,
    subModules: [
      { id: 'checkin', title: 'Check-in/out', href: '/modulos/campo/checkin', icon: 'LogIn', permissions: ['campo:checkin'] },
      { id: 'monitoramento', title: 'Monitoramento', href: '/modulos/campo/monitoramento', icon: 'Monitor', permissions: ['campo:monitoramento'] },
      { id: 'comunicados', title: 'Comunicados', href: '/modulos/campo/comunicados', icon: 'Bell', permissions: ['campo:comunicados'] },
    ],
  },

  // === FINANCEIRO ===
  {
    id: 'financial',
    title: 'Financeiro',
    description: 'Contas, fluxo de caixa e faturamento',
    icon: 'DollarSign',
    href: '/modulos/financeiro',
    color: 'green',
    permissions: ['financial:read'],
    enabled: true,
    subModules: [
      { id: 'contas-pagar', title: 'Contas a Pagar', href: '/modulos/financeiro/contas-pagar', icon: 'TrendingDown', permissions: ['financial:contas-pagar'] },
      { id: 'contas-receber', title: 'Contas a Receber', href: '/modulos/financeiro/contas-receber', icon: 'TrendingUp', permissions: ['financial:contas-receber'] },
      { id: 'fluxo-caixa', title: 'Fluxo de Caixa', href: '/modulos/financeiro/fluxo-caixa', icon: 'Activity', permissions: ['financial:fluxo'] },
      { id: 'faturamento', title: 'Faturamento', href: '/modulos/financeiro/faturamento', icon: 'Receipt', permissions: ['financial:faturamento'] },
      { id: 'conciliacao', title: 'Conciliação', href: '/modulos/financeiro/conciliacao', icon: 'CheckCircle2', permissions: ['financial:conciliacao'] },
    ],
  },
  {
    id: 'government',
    title: 'Fiscal',
    description: 'NFS-e, eSocial, SPED e obrigações',
    icon: 'Landmark',
    href: '/modulos/fiscal',
    color: 'orange',
    permissions: ['government:read'],
    enabled: true,
    subModules: [
      { id: 'nfse', title: 'NFS-e', href: '/modulos/fiscal/nfse', icon: 'FileText', permissions: ['government:nfse'] },
      { id: 'esocial', title: 'eSocial', href: '/modulos/fiscal/esocial', icon: 'Users', permissions: ['government:esocial'] },
      { id: 'sped', title: 'SPED', href: '/modulos/fiscal/sped', icon: 'Database', permissions: ['government:sped'] },
      { id: 'dctfweb', title: 'DCTFWeb', href: '/modulos/fiscal/dctfweb', icon: 'FileSpreadsheet', permissions: ['government:dctfweb'] },
      { id: 'reinf', title: 'EFD-Reinf', href: '/modulos/fiscal/reinf', icon: 'FileCode', permissions: ['government:reinf'] },
      { id: 'certidoes', title: 'Certidões', href: '/modulos/fiscal/certidoes', icon: 'Award', permissions: ['government:certidoes'] },
    ],
  },

  // === ADMINISTRATIVO ===
  {
    id: 'ged',
    title: 'Documentos',
    description: 'Gestão eletrônica de documentos',
    icon: 'FolderOpen',
    href: '/modulos/documentos',
    color: 'yellow',
    permissions: ['ged:read'],
    enabled: true,
    subModules: [
      { id: 'arquivos', title: 'Arquivos', href: '/modulos/documentos/arquivos', icon: 'File', permissions: ['ged:arquivos'] },
      { id: 'pastas', title: 'Pastas', href: '/modulos/documentos/pastas', icon: 'Folder', permissions: ['ged:pastas'] },
      { id: 'kits', title: 'Kits de Documentos', href: '/modulos/documentos/kits', icon: 'Package', permissions: ['ged:kits'] },
    ],
  },
  {
    id: 'equipment',
    title: 'Equipamentos',
    description: 'Patrimônio, comodatos e manutenções',
    icon: 'Wrench',
    href: '/modulos/equipamentos',
    color: 'pink',
    permissions: ['equipment:read'],
    enabled: true,
    subModules: [
      { id: 'patrimonio', title: 'Patrimônio', href: '/modulos/equipamentos/patrimonio', icon: 'Package', permissions: ['equipment:patrimonio'] },
      { id: 'comodatos', title: 'Comodatos', href: '/modulos/equipamentos/comodatos', icon: 'Repeat', permissions: ['equipment:comodatos'] },
      { id: 'manutencoes', title: 'Manutenções', href: '/modulos/equipamentos/manutencoes', icon: 'Settings', permissions: ['equipment:manutencoes'] },
    ],
  },
  {
    id: 'integrations',
    title: 'Integrações',
    description: 'Intelbras, Control iD, Hikvision',
    icon: 'Plug',
    href: '/modulos/integracoes',
    color: 'cyan',
    permissions: ['integrations:read'],
    enabled: true,
    subModules: [
      { id: 'intelbras', title: 'Intelbras', href: '/modulos/integracoes/intelbras', icon: 'Camera', permissions: ['integrations:intelbras'] },
      { id: 'controlid', title: 'Control iD', href: '/modulos/integracoes/controlid', icon: 'Fingerprint', permissions: ['integrations:controlid'] },
      { id: 'hikvision', title: 'Hikvision', href: '/modulos/integracoes/hikvision', icon: 'Video', permissions: ['integrations:hikvision'] },
      { id: 'webhooks', title: 'Webhooks', href: '/modulos/integracoes/webhooks', icon: 'Webhook', permissions: ['integrations:webhooks'] },
    ],
  },

  // === RELATÓRIOS ===
  {
    id: 'reports',
    title: 'Relatórios',
    description: 'Dashboards e análises gerenciais',
    icon: 'BarChart3',
    href: '/modulos/relatorios',
    color: 'blue',
    permissions: ['reports:read'],
    enabled: true,
    subModules: [
      { id: 'dashboards', title: 'Dashboards', href: '/modulos/relatorios/dashboards', icon: 'LayoutDashboard', permissions: ['reports:dashboards'] },
      { id: 'operacional', title: 'Operacional', href: '/modulos/relatorios/operacional', icon: 'ClipboardCheck', permissions: ['reports:operacional'] },
      { id: 'financeiro', title: 'Financeiro', href: '/modulos/relatorios/financeiro', icon: 'PieChart', permissions: ['reports:financeiro'] },
      { id: 'comercial', title: 'Comercial', href: '/modulos/relatorios/comercial', icon: 'TrendingUp', permissions: ['reports:comercial'] },
    ],
  },

  // === CONFIGURAÇÕES ===
  {
    id: 'config',
    title: 'Configurações',
    description: 'Usuários, permissões e sistema',
    icon: 'Settings',
    href: '/modulos/configuracoes',
    color: 'red',
    permissions: ['config:read'],
    enabled: true,
    subModules: [
      { id: 'usuarios', title: 'Usuários', href: '/modulos/configuracoes/usuarios', icon: 'Users', permissions: ['config:usuarios'] },
      { id: 'permissoes', title: 'Permissões', href: '/modulos/configuracoes/permissoes', icon: 'Lock', permissions: ['config:permissoes'] },
      { id: 'empresa', title: 'Empresa', href: '/modulos/configuracoes/empresa', icon: 'Building', permissions: ['config:empresa'] },
      { id: 'auditoria', title: 'Auditoria', href: '/modulos/configuracoes/auditoria', icon: 'Eye', permissions: ['config:auditoria'] },
    ],
  },
];

// Agrupar módulos por categoria
export const moduleCategories: ModuleCategory[] = [
  {
    id: 'operacional',
    title: 'Operacional',
    modules: modules.filter(m => ['crm', 'services', 'operacional', 'campo'].includes(m.id)),
  },
  {
    id: 'financeiro',
    title: 'Financeiro & Fiscal',
    modules: modules.filter(m => ['financial', 'government'].includes(m.id)),
  },
  {
    id: 'administrativo',
    title: 'Administrativo',
    modules: modules.filter(m => ['ged', 'equipment', 'integrations'].includes(m.id)),
  },
  {
    id: 'gestao',
    title: 'Gestão',
    modules: modules.filter(m => ['reports', 'config'].includes(m.id)),
  },
];

// Buscar módulo por ID
export function getModuleById(id: string): Module | undefined {
  return modules.find(m => m.id === id);
}

// Buscar módulo por path
export function getModuleByPath(path: string): Module | undefined {
  return modules.find(m => path.startsWith(m.href));
}
