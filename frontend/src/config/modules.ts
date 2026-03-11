import { Module, ModuleCategory } from '@/types/modules';

// Definicao de todos os modulos do sistema — 9 modulos organizados
// Reorganizacao visual (frontend only) — backend continua com 35 modulos
export const modules: Module[] = [
  // ═══════════════════════════════════════════════════════════════════
  // 1. COMERCIAL (antigos: CRM + Servicos)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'comercial',
    title: 'Comercial',
    description: 'Leads, clientes, propostas, contratos e servicos',
    icon: 'Handshake',
    href: '/modulos/crm',
    color: 'cyan',
    permissions: ['crm:read'],
    enabled: true,
    subModules: [
      // --- CRM ---
      { id: 'leads', title: 'Leads', href: '/modulos/crm/leads', icon: 'UserPlus', permissions: ['crm:leads'] },
      { id: 'oportunidades', title: 'Oportunidades', href: '/modulos/crm/oportunidades', icon: 'Target', permissions: ['crm:oportunidades'] },
      { id: 'clientes', title: 'Clientes', href: '/modulos/crm/clientes', icon: 'Building2', permissions: ['crm:clientes'] },
      { id: 'contatos', title: 'Contatos', href: '/modulos/crm/contatos', icon: 'Contact', permissions: ['crm:contatos'] },
      { id: 'propostas', title: 'Propostas', href: '/modulos/crm/propostas', icon: 'FileText', permissions: ['crm:propostas'] },
      // --- Servicos ---
      { id: 'contratos', title: 'Contratos', href: '/modulos/servicos/contratos', icon: 'FileSignature', permissions: ['services:contratos'] },
      { id: 'ordens', title: 'Ordens de Servico', href: '/modulos/servicos/ordens', icon: 'ClipboardList', permissions: ['services:ordens'] },
      { id: 'agendamentos', title: 'Agendamentos', href: '/modulos/servicos/agendamentos', icon: 'Calendar', permissions: ['services:agendamentos'] },
      // --- Licitacoes ---
      { id: 'editais', title: 'Editais', href: '/modulos/licitacoes/editais', icon: 'FileSearch', permissions: ['bidding:tenders:read'] },
      { id: 'propostas-licitacao', title: 'Propostas Licitacao', href: '/modulos/licitacoes/propostas', icon: 'FileCheck', permissions: ['bidding:proposals:read'] },
      { id: 'contratos-licitacao', title: 'Contratos Publicos', href: '/modulos/licitacoes/contratos', icon: 'FileSignature', permissions: ['bidding:contracts:read'] },
      { id: 'certidoes-licitacao', title: 'Certidoes', href: '/modulos/licitacoes/certidoes', icon: 'Award', permissions: ['bidding:certificates:read'] },
      { id: 'documentos-licitacao', title: 'Documentos', href: '/modulos/licitacoes/documentos', icon: 'FolderOpen', permissions: ['bidding:documents:read'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 2. OPERACOES (antigos: Operacional + Campo)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'operacoes',
    title: 'Operacoes',
    description: 'Postos, escalas, campo e inteligencia operacional',
    icon: 'Shield',
    href: '/modulos/operacional',
    color: 'green',
    permissions: ['operacional:read'],
    enabled: true,
    subModules: [
      // --- Postos e Escalas ---
      { id: 'postos', title: 'Postos', href: '/modulos/operacional/postos', icon: 'MapPin', permissions: ['operacional:postos'] },
      { id: 'colaboradores', title: 'Colaboradores', href: '/modulos/operacional/colaboradores', icon: 'UserCheck', permissions: ['operacional:colaboradores'] },
      { id: 'escalas', title: 'Escalas', href: '/modulos/operacional/escalas', icon: 'CalendarDays', permissions: ['operacional:escalas'] },
      { id: 'escalas-visual', title: 'Editor Visual', href: '/modulos/operacional/escalas/visual', icon: 'CalendarDays', permissions: ['operacional:escalas'] },
      { id: 'alocacoes', title: 'Alocacoes', href: '/modulos/operacional/alocacoes', icon: 'Users', permissions: ['operacional:alocacoes'] },
      { id: 'turnos', title: 'Turnos', href: '/modulos/operacional/turnos', icon: 'Clock', permissions: ['operacional:turnos'] },
      { id: 'substituicoes', title: 'Substituicoes', href: '/modulos/operacional/substituicoes', icon: 'RefreshCw', permissions: ['operacional:read'] },
      { id: 'diaristas', title: 'Diaristas', href: '/modulos/operacional/diaristas', icon: 'UserCheck', permissions: ['operacional:read'] },
      { id: 'banco-horas', title: 'Banco de Horas', href: '/modulos/operacional/banco-horas', icon: 'Clock', permissions: ['operacional:read'] },
      // --- Ocorrencias e Disciplinar ---
      { id: 'ocorrencias', title: 'Ocorrencias', href: '/modulos/operacional/ocorrencias', icon: 'AlertTriangle', permissions: ['operacional:ocorrencias'] },
      { id: 'disciplinar', title: 'Processos Disciplinares', href: '/modulos/operacional/disciplinar', icon: 'FileText', permissions: ['operacional:disciplinar'] },
      { id: 'medidas-administrativas', title: 'Medidas Administrativas', href: '/modulos/operacional/medidas-administrativas', icon: 'AlertTriangle', permissions: ['operacional:disciplinar'] },
      // --- Campo e Rondas ---
      { id: 'rondas', title: 'Rondas', href: '/modulos/operacional/rondas', icon: 'Route', permissions: ['operacional:rondas'] },
      { id: 'checkin', title: 'Check-in/out', href: '/modulos/campo/checkin', icon: 'LogIn', permissions: ['campo:checkin'] },
      { id: 'monitoramento', title: 'Monitoramento Campo', href: '/modulos/campo/monitoramento', icon: 'Monitor', permissions: ['campo:monitoramento'] },
      { id: 'comunicados-campo', title: 'Comunicados Campo', href: '/modulos/campo/comunicados', icon: 'Megaphone', permissions: ['campo:comunicados'] },
      // --- Tempo Real ---
      { id: 'cobertura', title: 'Cobertura ao Vivo', href: '/modulos/operacional/cobertura', icon: 'Activity', permissions: ['operacional:postos'] },
      { id: 'mapa', title: 'Mapa ao Vivo', href: '/modulos/operacional/mapa', icon: 'MapPin', permissions: ['operacional:postos'] },
      { id: 'kpi', title: 'KPI & Tendencias', href: '/modulos/operacional/kpi', icon: 'TrendingUp', permissions: ['operacional:read'] },
      // --- Comunicacao ---
      { id: 'comunicados', title: 'Comunicados', href: '/modulos/operacional/comunicados', icon: 'Bell', permissions: ['operacional:comunicados'] },
      { id: 'notificacoes', title: 'Notificacoes', href: '/modulos/operacional/notificacoes', icon: 'Bell', permissions: ['operacional:notificacoes'] },
      // --- IA Operacional ---
      { id: 'ai-command-center', title: 'Central IA', href: '/modulos/operacional/ai-command-center', icon: 'Zap', permissions: ['operacional:read'] },
      { id: 'agentes-ia', title: 'Agentes IA', href: '/modulos/operacional/agentes', icon: 'Bot', permissions: ['operacional:read'] },
      // --- Ferias e Reembolsos ---
      { id: 'ferias', title: 'Ferias e Afastamentos', href: '/modulos/operacional/ferias', icon: 'Plane', permissions: ['operacional:read'] },
      { id: 'reembolsos-op', title: 'Reembolsos', href: '/modulos/operacional/reembolsos', icon: 'Receipt', permissions: ['operacional:reembolsos'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 3. PESSOAS (antigos: Recrutamento + Saude Ocupacional)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'pessoas',
    title: 'Pessoas',
    description: 'Recrutamento, saude ocupacional e reembolsos',
    icon: 'Users',
    href: '/modulos/recrutamento',
    color: 'purple',
    permissions: ['operacional:read'],
    enabled: true,
    subModules: [
      // --- Recrutamento ---
      { id: 'vagas', title: 'Vagas', href: '/modulos/recrutamento/vagas', icon: 'Briefcase', permissions: ['operacional:read'] },
      { id: 'candidatos', title: 'Candidatos', href: '/modulos/recrutamento/candidatos', icon: 'Users', permissions: ['operacional:read'] },
      { id: 'candidaturas', title: 'Candidaturas', href: '/modulos/recrutamento/candidaturas', icon: 'FileText', permissions: ['operacional:read'] },
      { id: 'entrevistas', title: 'Entrevistas', href: '/modulos/recrutamento/entrevistas', icon: 'Calendar', permissions: ['operacional:read'] },
      // --- Saude Ocupacional ---
      { id: 'epi', title: 'EPI', href: '/modulos/saude-ocupacional/epi', icon: 'HardHat', permissions: ['operacional:read'] },
      { id: 'exames', title: 'Exames Medicos', href: '/modulos/saude-ocupacional/exames', icon: 'Stethoscope', permissions: ['operacional:read'] },
      { id: 'riscos', title: 'Gestao de Riscos', href: '/modulos/saude-ocupacional/riscos', icon: 'AlertTriangle', permissions: ['operacional:read'] },
      // --- Reembolso ---
      { id: 'reembolso-aprovacoes', title: 'Reembolsos', href: '/modulos/reembolso/aprovacoes', icon: 'Receipt', permissions: ['operacional:read'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 4. FINANCEIRO (antigo: Financial + Suprimentos + boletos)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'financeiro',
    title: 'Financeiro',
    description: 'Contas, fluxo de caixa, compras e estoque',
    icon: 'DollarSign',
    href: '/modulos/financeiro',
    color: 'green',
    permissions: ['financial:read'],
    enabled: true,
    subModules: [
      { id: 'contas-pagar', title: 'Contas a Pagar', href: '/modulos/financeiro/contas-pagar', icon: 'TrendingDown', permissions: ['financial:contas-pagar'] },
      { id: 'contas-receber', title: 'Contas a Receber', href: '/modulos/financeiro/contas-receber', icon: 'TrendingUp', permissions: ['financial:contas-receber'] },
      { id: 'fluxo-caixa', title: 'Fluxo de Caixa', href: '/modulos/financeiro/fluxo-caixa', icon: 'Activity', permissions: ['financial:fluxo'] },
      { id: 'conciliacao', title: 'Conciliacao Bancaria', href: '/modulos/financeiro/conciliacao', icon: 'CheckCircle2', permissions: ['financial:conciliacao'] },
      { id: 'boletos', title: 'Boletos', href: '/modulos/financeiro/boletos', icon: 'CreditCard', permissions: ['financial:faturamento'] },
      { id: 'cobrancas', title: 'Cobrancas', href: '/modulos/financeiro/cobrancas', icon: 'DollarSign', permissions: ['financial:faturamento'] },
      { id: 'fornecedores', title: 'Fornecedores', href: '/modulos/financeiro/fornecedores', icon: 'Truck', permissions: ['financial:fornecedores'] },
      // --- Suprimentos ---
      { id: 'compras', title: 'Compras', href: '/modulos/financeiro/compras', icon: 'ShoppingCart', permissions: ['financial:compras'] },
      { id: 'estoque', title: 'Estoque', href: '/modulos/financeiro/estoque', icon: 'Package', permissions: ['financial:estoque'] },
      // --- Custos e Precificacao ---
      { id: 'custos', title: 'Custos', href: '/modulos/financeiro/custos', icon: 'PieChart', permissions: ['financial:custeio'] },
      { id: 'custeio', title: 'Custeio ABC', href: '/modulos/financeiro/custeio', icon: 'Calculator', permissions: ['financial:custeio'] },
      { id: 'precificacao', title: 'Precificacao', href: '/modulos/financeiro/precificacao', icon: 'Tag', permissions: ['financial:read'] },
      { id: 'orcamentos', title: 'Orcamentos', href: '/modulos/financeiro/orcamentos', icon: 'Target', permissions: ['financial:read'] },
      // --- Contabilidade e Relatorios ---
      { id: 'contabilidade', title: 'Contabilidade', href: '/modulos/financeiro/contabilidade', icon: 'Calculator', permissions: ['financial:contabilidade'] },
      { id: 'faturamento', title: 'Faturamento', href: '/modulos/financeiro/faturamento', icon: 'Receipt', permissions: ['financial:faturamento'] },
      { id: 'relatorios-fin', title: 'Relatorios', href: '/modulos/financeiro/relatorios', icon: 'BarChart2', permissions: ['financial:read'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 5. FISCAL & CONTABIL (antigos: Fiscal + Empresas)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'fiscal',
    title: 'Fiscal & Contabil',
    description: 'NFS-e, impostos, SPED, multi-empresa e demonstrativos',
    icon: 'Landmark',
    href: '/modulos/fiscal',
    color: 'orange',
    permissions: ['government:read'],
    enabled: true,
    subModules: [
      // --- Notas Fiscais ---
      { id: 'nfe', title: 'NF-e', href: '/modulos/financeiro/fiscal', icon: 'Receipt', permissions: ['government:nfse'] },
      { id: 'nfse', title: 'NFS-e', href: '/modulos/fiscal/nfse', icon: 'FileText', permissions: ['government:nfse'] },
      { id: 'nfse-multi', title: 'NFS-e Multi-Empresa', href: '/modulos/fiscal/nfse-multi', icon: 'FileText', permissions: ['government:nfse'] },
      // --- Obrigacoes ---
      { id: 'esocial', title: 'eSocial', href: '/modulos/fiscal/esocial', icon: 'Users', permissions: ['government:esocial'] },
      { id: 'sped', title: 'SPED', href: '/modulos/fiscal/sped', icon: 'Database', permissions: ['government:sped'] },
      { id: 'dctfweb', title: 'DCTFWeb', href: '/modulos/fiscal/dctfweb', icon: 'FileSpreadsheet', permissions: ['government:dctfweb'] },
      { id: 'reinf', title: 'EFD-Reinf', href: '/modulos/fiscal/reinf', icon: 'FileCode', permissions: ['government:reinf'] },
      { id: 'certidoes', title: 'Certidoes', href: '/modulos/fiscal/certidoes', icon: 'Award', permissions: ['government:certidoes'] },
      // --- Multi-Empresa ---
      { id: 'empresas-gestao', title: 'Gestao Empresas', href: '/modulos/empresas', icon: 'Building2', permissions: ['empresas:read'] },
      { id: 'liminares', title: 'Liminares', href: '/modulos/empresas/liminares', icon: 'Scale', permissions: ['empresas:read'] },
      { id: 'rentabilidade', title: 'Rentabilidade', href: '/modulos/empresas/rentabilidade', icon: 'TrendingUp', permissions: ['empresas:read'] },
      { id: 'dashboard-empresas', title: 'Dashboard Multi-CNPJ', href: '/modulos/empresas/dashboard', icon: 'LayoutDashboard', permissions: ['empresas:read'] },
      { id: 'demonstrativos', title: 'Demonstrativos', href: '/modulos/empresas/demonstrativos', icon: 'BarChart2', permissions: ['empresas:read'] },
      { id: 'obrigacoes-empresa', title: 'Obrigacoes', href: '/modulos/empresas/obrigacoes', icon: 'CalendarDays', permissions: ['empresas:read'] },
      { id: 'migrador', title: 'Migrador Contratos', href: '/modulos/empresas/migrador', icon: 'ArrowRightLeft', permissions: ['empresas:read'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 6. INTELIGENCIA (antigos: Relatorios + Analytics + Assistente)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'inteligencia',
    title: 'Inteligencia',
    description: 'Dashboards, KPIs, relatorios e analytics',
    icon: 'BarChart3',
    href: '/modulos/relatorios',
    color: 'blue',
    permissions: ['reports:read'],
    enabled: true,
    subModules: [
      { id: 'dashboards', title: 'Dashboards', href: '/modulos/relatorios/dashboards', icon: 'LayoutDashboard', permissions: ['reports:dashboards'] },
      { id: 'rel-operacional', title: 'Operacional', href: '/modulos/relatorios/operacional', icon: 'ClipboardCheck', permissions: ['reports:operacional'] },
      { id: 'rel-financeiro', title: 'Financeiro', href: '/modulos/relatorios/financeiro', icon: 'PieChart', permissions: ['reports:financeiro'] },
      { id: 'rel-comercial', title: 'Comercial', href: '/modulos/relatorios/comercial', icon: 'TrendingUp', permissions: ['reports:comercial'] },
      { id: 'analytics', title: 'Analytics', href: '/modulos/analytics', icon: 'Activity', permissions: ['reports:read'] },
      { id: 'rel-operacional-detalhado', title: 'Relatorios Operacionais', href: '/modulos/operacional/relatorios', icon: 'FileText', permissions: ['operacional:read'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 7. DOCUMENTOS & EQUIPAMENTOS (antigos: GED + Equipamentos)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'patrimonio',
    title: 'Documentos & Patrimonio',
    description: 'GED, equipamentos, comodatos e manutencoes',
    icon: 'FolderOpen',
    href: '/modulos/documentos',
    color: 'yellow',
    permissions: ['ged:read'],
    enabled: true,
    subModules: [
      // --- GED ---
      { id: 'arquivos', title: 'Arquivos', href: '/modulos/documentos/arquivos', icon: 'File', permissions: ['ged:arquivos'] },
      { id: 'pastas', title: 'Pastas', href: '/modulos/documentos/pastas', icon: 'Folder', permissions: ['ged:pastas'] },
      { id: 'kits', title: 'Kits de Documentos', href: '/modulos/documentos/kits', icon: 'Package', permissions: ['ged:kits'] },
      // --- Equipamentos ---
      { id: 'patrimonio-equip', title: 'Patrimonio', href: '/modulos/equipamentos/patrimonio', icon: 'Package', permissions: ['equipment:patrimonio'] },
      { id: 'comodatos', title: 'Comodatos', href: '/modulos/equipamentos/comodatos', icon: 'Repeat', permissions: ['equipment:comodatos'] },
      { id: 'manutencoes', title: 'Manutencoes', href: '/modulos/equipamentos/manutencoes', icon: 'Wrench', permissions: ['equipment:manutencoes'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 8. ADMINISTRATIVO (antigos: Integracoes + Seguranca + Agendador + Automacoes)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'administrativo',
    title: 'Administrativo',
    description: 'Integracoes, seguranca, LGPD, automacoes e agendador',
    icon: 'Settings',
    href: '/modulos/integracoes',
    color: 'red',
    permissions: ['integrations:read'],
    enabled: true,
    subModules: [
      // --- Integracoes ---
      { id: 'conectores', title: 'Conectores', href: '/modulos/integracoes/conectores', icon: 'Plug', permissions: ['integrations:conectores'] },
      { id: 'api-keys', title: 'API Keys', href: '/modulos/integracoes/api-keys', icon: 'Key', permissions: ['integrations:api-keys'] },
      { id: 'webhooks', title: 'Webhooks', href: '/modulos/integracoes/webhooks', icon: 'Webhook', permissions: ['integrations:webhooks'] },
      { id: 'logs-integracao', title: 'Logs', href: '/modulos/integracoes/logs', icon: 'FileText', permissions: ['integrations:logs'] },
      { id: 'sync', title: 'Sincronizacao', href: '/modulos/integracoes/sync', icon: 'RefreshCw', permissions: ['integrations:sync'] },
      { id: 'solides', title: 'Solides', href: '/modulos/integracoes/solides', icon: 'Zap', permissions: ['integrations:solides'] },
      // --- Seguranca & LGPD ---
      { id: 'auditoria', title: 'Auditoria', href: '/modulos/seguranca/auditoria', icon: 'Eye', permissions: ['security:auditoria'] },
      { id: 'consentimento', title: 'Consentimento', href: '/modulos/seguranca/consentimento', icon: 'CheckCircle2', permissions: ['security:consentimento'] },
      { id: 'pia-dpia', title: 'PIA/DPIA', href: '/modulos/seguranca/pia-dpia', icon: 'FileText', permissions: ['security:pia'] },
      { id: 'esquecimento', title: 'Esquecimento', href: '/modulos/seguranca/esquecimento', icon: 'Trash2', permissions: ['security:esquecimento'] },
      { id: 'mascaramento', title: 'Mascaramento', href: '/modulos/seguranca/mascaramento', icon: 'Eye', permissions: ['security:mascaramento'] },
      { id: 'criptografia', title: 'Criptografia', href: '/modulos/seguranca/criptografia', icon: 'Lock', permissions: ['security:criptografia'] },
      // --- Agendador ---
      { id: 'tarefas-agendador', title: 'Tarefas Agendadas', href: '/modulos/agendador/tarefas', icon: 'Clock', permissions: ['config:read'] },
      { id: 'execucoes-agendador', title: 'Execucoes', href: '/modulos/agendador/execucoes', icon: 'Play', permissions: ['config:read'] },
      // --- Automacoes ---
      { id: 'workflows', title: 'Workflows', href: '/modulos/automacoes/workflows', icon: 'GitBranch', permissions: ['config:read'] },
      { id: 'execucoes-workflow', title: 'Execucoes Workflow', href: '/modulos/automacoes/execucoes', icon: 'Play', permissions: ['config:read'] },
    ],
  },

  // ═══════════════════════════════════════════════════════════════════
  // 9. CONFIGURACOES (mantido)
  // ═══════════════════════════════════════════════════════════════════
  {
    id: 'config',
    title: 'Configuracoes',
    description: 'Usuarios, permissoes e sistema',
    icon: 'Settings',
    href: '/modulos/configuracoes',
    color: 'red',
    permissions: ['config:read'],
    enabled: true,
    subModules: [
      { id: 'dashboard-config', title: 'Dashboard', href: '/modulos/configuracoes', icon: 'LayoutDashboard', permissions: ['config:read'] },
      { id: 'tenants', title: 'Tenants', href: '/modulos/configuracoes/tenants', icon: 'Building2', permissions: ['config:tenants'] },
      { id: 'feature-flags', title: 'Feature Flags', href: '/modulos/configuracoes/feature-flags', icon: 'ToggleRight', permissions: ['config:flags'] },
      { id: 'sistema', title: 'Sistema', href: '/modulos/configuracoes/configuracoes-sistema', icon: 'Settings', permissions: ['config:system'] },
      { id: 'templates', title: 'Templates', href: '/modulos/configuracoes/templates-notificacao', icon: 'Mail', permissions: ['config:templates'] },
    ],
  },
];

// Agrupar modulos por categoria — 4 categorias
export const moduleCategories: ModuleCategory[] = [
  {
    id: 'negocios',
    title: 'Negocios & Operacoes',
    modules: modules.filter(m => ['comercial', 'operacoes', 'pessoas'].includes(m.id)),
  },
  {
    id: 'financeiro',
    title: 'Financeiro & Fiscal',
    modules: modules.filter(m => ['financeiro', 'fiscal'].includes(m.id)),
  },
  {
    id: 'inteligencia',
    title: 'Inteligencia & Documentos',
    modules: modules.filter(m => ['inteligencia', 'patrimonio'].includes(m.id)),
  },
  {
    id: 'administracao',
    title: 'Administracao',
    modules: modules.filter(m => ['administrativo', 'config'].includes(m.id)),
  },
];

// Buscar modulo por ID
export function getModuleById(id: string): Module | undefined {
  return modules.find(m => m.id === id);
}

// Buscar modulo por path — match mais especifico primeiro
export function getModuleByPath(path: string): Module | undefined {
  // 1. Tentar match direto pelo href do modulo
  let best: Module | undefined;
  let bestLen = 0;

  for (const m of modules) {
    if (path.startsWith(m.href) && m.href.length > bestLen) {
      best = m;
      bestLen = m.href.length;
    }
  }

  if (best) return best;

  // 2. Fallback: buscar pelo href dos submodules
  for (const m of modules) {
    for (const sub of m.subModules) {
      if (path.startsWith(sub.href)) {
        return m;
      }
    }
  }

  return undefined;
}
