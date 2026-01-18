'use client';

import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  FileText,
  DollarSign,
  UserCircle,
  Calendar,
  MapPin,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronDown,
  BarChart3,
  Building2,
  Wallet,
  Receipt,
  Banknote,
  TrendingUp,
  Package,
  ShoppingCart,
  FileSpreadsheet,
  Clock,
  ClipboardList,
  Route,
  Zap,
  Bot,
  FolderOpen,
  Shield,
  Bell,
  X,
  Gavel,
  HeartPulse,
  Wrench,
  Mail,
  MessageSquare,
  Store,
  FileCheck,
  Scale,
  Key,
  Database,
  Truck,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/shared/utils/cn';
import { Avatar } from '@/design-system/components';

interface NavItem {
  label: string;
  icon: LucideIcon;
  path?: string;
  children?: { label: string; path: string; icon?: LucideIcon }[];
  badge?: string | number;
}

// Navegação completa com TODOS os módulos habilitados
const navigation: NavItem[] = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    children: [
      { label: 'Executivo', path: '/dashboard', icon: BarChart3 },
      { label: 'Analytics', path: '/analytics', icon: TrendingUp },
      { label: 'Tempo Real', path: '/realtime', icon: Zap },
      { label: 'Relatórios', path: '/reports', icon: FileSpreadsheet },
    ],
  },
  {
    label: 'CRM',
    icon: Users,
    children: [
      { label: 'Dashboard', path: '/crm/dashboard', icon: BarChart3 },
      { label: 'Pipeline', path: '/crm/pipeline', icon: TrendingUp },
      { label: 'Leads', path: '/crm/leads', icon: Users },
      { label: 'Oportunidades', path: '/crm/opportunities', icon: Briefcase },
      { label: 'Propostas', path: '/crm/proposals', icon: FileText },
      { label: 'Contratos', path: '/crm/contracts', icon: FileCheck },
    ],
  },
  {
    label: 'Clientes',
    icon: Building2,
    children: [
      { label: 'Unidades/Moradores', path: '/clients/units-residents', icon: Building2 },
      { label: 'Marketplace', path: '/marketplace', icon: Store },
    ],
  },
  {
    label: 'Financeiro',
    icon: DollarSign,
    children: [
      { label: 'Dashboard CFO', path: '/finance/cfo', icon: Wallet },
      { label: 'Fluxo de Caixa', path: '/finance/cashflow', icon: TrendingUp },
      { label: 'Previsões', path: '/finance/forecasts', icon: BarChart3 },
      { label: 'Contas a Pagar', path: '/financial/payables', icon: Receipt },
      { label: 'Contas a Receber', path: '/financial/receivables', icon: Banknote },
      { label: 'Bancos', path: '/financial/banking', icon: Building2 },
      { label: 'Conciliação', path: '/financial/reconciliation', icon: FileCheck },
      { label: 'Contabilidade', path: '/financial/accounting', icon: FileSpreadsheet },
      { label: 'Fiscal', path: '/financial/fiscal', icon: FileText },
      { label: 'Estoque', path: '/financial/inventory', icon: Package },
      { label: 'Compras', path: '/financial/procurement', icon: ShoppingCart },
      { label: 'Fornecedores', path: '/financial/suppliers', icon: Truck },
      { label: 'Regras Faturamento', path: '/financial/billing-rules', icon: Receipt },
    ],
  },
  {
    label: 'Fiscal',
    icon: Receipt,
    children: [
      { label: 'NFC-e', path: '/fiscal/nfce', icon: Receipt },
      { label: 'NFS-e', path: '/fiscal/nfse', icon: FileText },
      { label: 'CT-e', path: '/fiscal/cte', icon: Truck },
      { label: 'MDF-e', path: '/fiscal/mdfe', icon: Route },
      { label: 'Simples Nacional', path: '/fiscal/simples', icon: DollarSign },
      { label: 'SPED Fiscal', path: '/sped/fiscal', icon: FileSpreadsheet },
      { label: 'SPED Contábil', path: '/sped/contabil', icon: FileSpreadsheet },
    ],
  },
  {
    label: 'RH',
    icon: UserCircle,
    children: [
      { label: 'Dashboard', path: '/hr', icon: BarChart3 },
      { label: 'Funcionários', path: '/hr/employees', icon: Users },
      { label: 'Folha', path: '/hr/payroll', icon: DollarSign },
      { label: 'FGTS Digital', path: '/trabalhista/fgts', icon: Wallet },
      { label: 'Ponto', path: '/hr/time-tracking', icon: Clock },
      { label: 'Recrutamento', path: '/hr/recruitment', icon: UserCircle },
      { label: 'REP', path: '/hr/rep-integration', icon: Zap },
      { label: 'Ponto Mobile', path: '/hr/mobile-time-clock', icon: Clock },
      { label: 'Saúde Ocupacional', path: '/hr/health', icon: HeartPulse },
    ],
  },
  {
    label: 'Operações',
    icon: Briefcase,
    children: [
      { label: 'Dashboard', path: '/operations', icon: BarChart3 },
      { label: 'Postos', path: '/operations/posts', icon: MapPin },
      { label: 'Escalas', path: '/operations/scales', icon: Calendar },
      { label: 'Turnos', path: '/operations/shifts', icon: Clock },
      { label: 'Alocações', path: '/operations/allocations', icon: Users },
      { label: 'Substituições', path: '/operations/substitutions', icon: UserCircle },
      { label: 'Banco de Horas', path: '/operations/time-bank', icon: Clock },
      { label: 'Diaristas', path: '/operations/daily-workers', icon: Users },
    ],
  },
  {
    label: 'Campo',
    icon: Route,
    children: [
      { label: 'Dashboard', path: '/field-service', icon: BarChart3 },
      { label: 'Ordens de Serviço', path: '/field-service/orders', icon: ClipboardList },
      { label: 'Visitas', path: '/field-service/visits', icon: MapPin },
      { label: 'Ocorrências', path: '/field-service/occurrences', icon: Bell },
      { label: 'Checklist', path: '/field-service/checklist', icon: FileCheck },
      { label: 'Roteirização', path: '/field-service/routes', icon: Route },
      { label: 'Inventário Campo', path: '/field-service/inventory', icon: Package },
    ],
  },
  {
    label: 'Equipamentos',
    icon: Wrench,
    children: [
      { label: 'Dashboard', path: '/equipment', icon: BarChart3 },
      { label: 'Lista', path: '/equipment/list', icon: Package },
      { label: 'Manutenção', path: '/equipment/maintenance', icon: Wrench },
      { label: 'Comodato', path: '/equipment/comodato', icon: FileCheck },
      { label: 'Instalações', path: '/equipment/installations', icon: Zap },
      { label: 'Monitoramento', path: '/equipment/monitoring', icon: BarChart3 },
    ],
  },
  {
    label: 'Documentos',
    icon: FolderOpen,
    children: [
      { label: 'GED', path: '/ged', icon: FolderOpen },
      { label: 'Classificação IA', path: '/ged/classification', icon: Bot },
      { label: 'Busca', path: '/ged/search', icon: FileText },
      { label: 'Kits de Documentos', path: '/ged/document-kits', icon: Package },
      { label: 'Doc Intelligence', path: '/ged/doc-intelligence', icon: Bot },
    ],
  },
  {
    label: 'Integrações',
    icon: Zap,
    children: [
      { label: 'Hub', path: '/integrations', icon: Zap },
      { label: 'Sólides (RH)', path: '/integrations/solides', icon: Users },
      { label: 'Open Banking', path: '/integrations/open-banking', icon: Building2 },
      { label: 'Email', path: '/integrations/email', icon: Mail },
      { label: 'WhatsApp', path: '/integrations/whatsapp', icon: MessageSquare },
    ],
  },
  {
    label: 'IA',
    icon: Bot,
    children: [
      { label: 'Intelligence Hub', path: '/ai', icon: Bot },
      { label: 'Bartolo', path: '/ai/bartolo', icon: Bot },
      { label: 'Análises', path: '/ai/analytics', icon: BarChart3 },
      { label: 'Detecção Fraude', path: '/ai/fraud-detection', icon: Shield },
    ],
  },
  {
    label: 'Compliance',
    icon: Shield,
    children: [
      { label: 'Dashboard', path: '/compliance', icon: BarChart3 },
      { label: 'Auditoria', path: '/audit', icon: FileCheck },
      { label: 'Logs Auditoria', path: '/compliance/audit-logs', icon: FileText },
      { label: 'LGPD', path: '/lgpd', icon: Shield },
      { label: 'Consentimentos', path: '/compliance/consent', icon: FileCheck },
      { label: 'Criptografia', path: '/compliance/encryption', icon: Key },
      { label: 'Mascaramento', path: '/compliance/data-masking', icon: Database },
      { label: 'Exclusão Dados', path: '/compliance/data-erasure', icon: FileText },
      { label: 'PIA', path: '/compliance/pia', icon: FileCheck },
      { label: 'Governo', path: '/government', icon: Building2 },
      { label: 'eSocial', path: '/compliance/esocial', icon: FileSpreadsheet },
      { label: 'SEFAZ', path: '/compliance/sefaz', icon: Receipt },
      { label: 'Receita Federal', path: '/compliance/receita-federal', icon: Building2 },
      { label: 'CCT/Convenções', path: '/compliance/cct', icon: Scale },
    ],
  },
  {
    label: 'Licitações',
    icon: Gavel,
    children: [
      { label: 'Dashboard', path: '/bidding', icon: BarChart3 },
      { label: 'Editais', path: '/bidding/notices', icon: FileText },
      { label: 'Propostas', path: '/bidding/proposals', icon: FileCheck },
    ],
  },
  {
    label: 'Notificações',
    icon: Bell,
    children: [
      { label: 'Central', path: '/notifications', icon: Bell },
      { label: 'Inteligentes', path: '/notifications/intelligent', icon: Bot },
    ],
  },
  {
    label: 'Extras',
    icon: Package,
    children: [
      { label: 'Agendador', path: '/extras/scheduler', icon: Calendar },
      { label: 'Kits Documentos', path: '/extras/document-kits', icon: FolderOpen },
    ],
  },
];

const bottomNav: NavItem[] = [
  {
    label: 'Configurações',
    icon: Settings,
    children: [
      { label: 'Geral', path: '/settings', icon: Settings },
      { label: 'Usuarios', path: '/settings/users', icon: Users },
      { label: 'Tenants', path: '/settings/tenants', icon: Building2 },
      { label: 'Feature Flags', path: '/settings/feature-flags', icon: Zap },
      { label: 'Templates Config', path: '/settings/config-templates', icon: FileText },
    ],
  },
  { label: 'Ajuda', icon: HelpCircle, path: '/help' },
];

interface SidebarProps {
  collapsed: boolean;
  mobileOpen: boolean;
  isMobile: boolean;
  isTablet: boolean;
  onToggle: () => void;
  onClose: () => void;
}

export function Sidebar({
  collapsed,
  mobileOpen,
  isMobile,
  isTablet,
  onToggle,
  onClose,
}: SidebarProps) {
  const location = useLocation();
  const [expandedItems, setExpandedItems] = useState<string[]>(['Dashboard']);

  const toggleExpanded = (label: string) => {
    setExpandedItems((prev) =>
      prev.includes(label)
        ? prev.filter((item) => item !== label)
        : [...prev, label]
    );
  };

  const isActive = (path: string) => location.pathname === path;
  const isParentActive = (children?: { path: string }[]) =>
    children?.some((child) => location.pathname.startsWith(child.path));

  // Determinar se deve mostrar como colapsada
  const showCollapsed = collapsed || isTablet;

  // Determinar visibilidade no mobile
  const isVisible = isMobile ? mobileOpen : true;

  if (!isVisible && isMobile) {
    return null;
  }

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-bg-secondary border-r border-border-subtle',
        'flex flex-col z-50 transition-all duration-300',
        // Mobile: drawer com largura fixa
        isMobile && 'w-72',
        // Tablet/Desktop: largura variável
        !isMobile && (showCollapsed ? 'w-20' : 'w-64'),
        // Animação de entrada no mobile
        isMobile && (mobileOpen ? 'translate-x-0' : '-translate-x-full')
      )}
    >
      {/* Logo */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-border-subtle">
        <div className="flex items-center gap-3 overflow-hidden">
          <img
            src="/logo.png"
            alt="Conecta PRO"
            className="h-10 w-auto flex-shrink-0"
          />
          <AnimatePresence>
            {(!showCollapsed || isMobile) && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden"
              >
                <div className="whitespace-nowrap">
                  <span className="font-display font-bold text-text-primary block leading-tight">
                    Conecta PRO
                  </span>
                  <span className="text-2xs text-text-muted">
                    By <span className="text-accent-primary">Conecta Mais</span>
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Botão fechar no mobile ou toggle no desktop */}
        {isMobile ? (
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-bg-tertiary transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        ) : (
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-bg-tertiary transition-colors"
          >
            <ChevronLeft
              className={cn(
                'w-5 h-5 transition-transform duration-300',
                showCollapsed && 'rotate-180'
              )}
            />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 scrollbar-hide">
        <ul className="space-y-1">
          {navigation.map((item) => (
            <li key={item.label}>
              {item.children ? (
                <div>
                  <button
                    onClick={() => (!showCollapsed || isMobile) && toggleExpanded(item.label)}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                      'transition-all duration-200',
                      isParentActive(item.children)
                        ? 'bg-accent-primary/10 text-accent-primary'
                        : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                    )}
                    title={showCollapsed && !isMobile ? item.label : undefined}
                  >
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    {(!showCollapsed || isMobile) && (
                      <>
                        <span className="flex-1 text-left truncate">{item.label}</span>
                        <ChevronDown
                          className={cn(
                            'w-4 h-4 transition-transform flex-shrink-0',
                            expandedItems.includes(item.label) && 'rotate-180'
                          )}
                        />
                      </>
                    )}
                  </button>
                  <AnimatePresence>
                    {(!showCollapsed || isMobile) && expandedItems.includes(item.label) && (
                      <motion.ul
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden ml-4 mt-1 space-y-1"
                      >
                        {item.children.map((child) => (
                          <li key={child.path}>
                            <NavLink
                              to={child.path}
                              onClick={isMobile ? onClose : undefined}
                              className={({ isActive }) =>
                                cn(
                                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm',
                                  'transition-all duration-200',
                                  isActive
                                    ? 'bg-accent-primary/10 text-accent-primary font-medium'
                                    : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                                )
                              }
                            >
                              {child.icon && <child.icon className="w-4 h-4 flex-shrink-0" />}
                              <span className="truncate">{child.label}</span>
                            </NavLink>
                          </li>
                        ))}
                      </motion.ul>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <NavLink
                  to={item.path!}
                  onClick={isMobile ? onClose : undefined}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                      'transition-all duration-200',
                      isActive
                        ? 'bg-accent-primary/10 text-accent-primary'
                        : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                    )
                  }
                  title={showCollapsed && !isMobile ? item.label : undefined}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  {(!showCollapsed || isMobile) && <span className="truncate">{item.label}</span>}
                </NavLink>
              )}
            </li>
          ))}
        </ul>
      </nav>

      {/* Bottom Navigation */}
      <div className="border-t border-border-subtle p-3 space-y-1">
        {bottomNav.map((item) => (
          item.children ? (
            <div key={item.label}>
              <button
                onClick={() => (!showCollapsed || isMobile) && toggleExpanded(item.label)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                  'transition-all duration-200',
                  isParentActive(item.children)
                    ? 'bg-accent-primary/10 text-accent-primary'
                    : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                )}
                title={showCollapsed && !isMobile ? item.label : undefined}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {(!showCollapsed || isMobile) && (
                  <>
                    <span className="flex-1 text-left truncate">{item.label}</span>
                    <ChevronDown
                      className={cn(
                        'w-4 h-4 transition-transform flex-shrink-0',
                        expandedItems.includes(item.label) && 'rotate-180'
                      )}
                    />
                  </>
                )}
              </button>
              <AnimatePresence>
                {(!showCollapsed || isMobile) && expandedItems.includes(item.label) && (
                  <motion.ul
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden ml-4 mt-1 space-y-1"
                  >
                    {item.children.map((child) => (
                      <li key={child.path}>
                        <NavLink
                          to={child.path}
                          onClick={isMobile ? onClose : undefined}
                          className={({ isActive }) =>
                            cn(
                              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm',
                              'transition-all duration-200',
                              isActive
                                ? 'bg-accent-primary/10 text-accent-primary font-medium'
                                : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                            )
                          }
                        >
                          {child.icon && <child.icon className="w-4 h-4 flex-shrink-0" />}
                          <span className="truncate">{child.label}</span>
                        </NavLink>
                      </li>
                    ))}
                  </motion.ul>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <NavLink
              key={item.label}
              to={item.path!}
              onClick={isMobile ? onClose : undefined}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                  'transition-all duration-200',
                  isActive
                    ? 'bg-accent-primary/10 text-accent-primary'
                    : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                )
              }
              title={showCollapsed && !isMobile ? item.label : undefined}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {(!showCollapsed || isMobile) && <span className="truncate">{item.label}</span>}
            </NavLink>
          )
        ))}
      </div>

      {/* User */}
      <div className="border-t border-border-subtle p-3">
        <div
          className={cn(
            'flex items-center gap-3 p-2 rounded-lg hover:bg-bg-tertiary transition-colors cursor-pointer',
            (showCollapsed && !isMobile) && 'justify-center'
          )}
        >
          <Avatar name="Jordan Admin" size="sm" status="online" />
          {(!showCollapsed || isMobile) && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary truncate">
                Jordan Admin
              </p>
              <p className="text-xs text-text-muted truncate">
                admin@conectapro.com.br
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
