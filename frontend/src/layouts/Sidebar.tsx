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
  LogOut,
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

const navigation: NavItem[] = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    children: [
      { label: 'Executivo', path: '/', icon: BarChart3 },
      { label: 'Analytics', path: '/analytics', icon: TrendingUp },
      { label: 'Tempo Real', path: '/realtime', icon: Zap },
      { label: 'Relatórios', path: '/reports', icon: FileSpreadsheet },
    ],
  },
  {
    label: 'CRM',
    icon: Users,
    children: [
      { label: 'Overview', path: '/crm' },
      { label: 'Leads', path: '/crm/leads' },
      { label: 'Oportunidades', path: '/crm/opportunities' },
      { label: 'Propostas', path: '/crm/proposals' },
      { label: 'Contratos', path: '/crm/contracts' },
    ],
  },
  {
    label: 'Financeiro',
    icon: DollarSign,
    children: [
      { label: 'Dashboard', path: '/financial', icon: Wallet },
      { label: 'Contas a Pagar', path: '/financial/payables', icon: Receipt },
      { label: 'Contas a Receber', path: '/financial/receivables', icon: Banknote },
      { label: 'Bancos', path: '/financial/banking', icon: Building2 },
      { label: 'Fluxo de Caixa', path: '/financial/cashflow', icon: TrendingUp },
      { label: 'Estoque', path: '/financial/inventory', icon: Package },
      { label: 'Compras', path: '/financial/procurement', icon: ShoppingCart },
      { label: 'Fiscal', path: '/financial/fiscal', icon: FileSpreadsheet },
    ],
  },
  {
    label: 'RH',
    icon: UserCircle,
    children: [
      { label: 'Dashboard', path: '/hr' },
      { label: 'Funcionários', path: '/hr/employees' },
      { label: 'Folha', path: '/hr/payroll' },
      { label: 'Ponto', path: '/hr/time-tracking', icon: Clock },
      { label: 'Recrutamento', path: '/hr/recruitment' },
    ],
  },
  {
    label: 'Operações',
    icon: Briefcase,
    children: [
      { label: 'Dashboard', path: '/operations' },
      { label: 'Postos', path: '/operations/posts', icon: MapPin },
      { label: 'Escalas', path: '/operations/scales', icon: Calendar },
      { label: 'Alocações', path: '/operations/allocations' },
    ],
  },
  {
    label: 'Campo',
    icon: Route,
    children: [
      { label: 'Dashboard', path: '/field-service' },
      { label: 'Ordens de Serviço', path: '/field-service/orders', icon: ClipboardList },
      { label: 'Visitas', path: '/field-service/visits' },
      { label: 'Roteirização', path: '/field-service/routes' },
    ],
  },
  {
    label: 'Integrações',
    icon: Zap,
    children: [
      { label: 'Hub', path: '/integrations' },
      { label: 'Banking', path: '/integrations/banking' },
      { label: 'Email', path: '/integrations/email' },
      { label: 'WhatsApp', path: '/integrations/whatsapp' },
    ],
  },
  {
    label: 'IA',
    icon: Bot,
    children: [
      { label: 'Intelligence Hub', path: '/ai' },
      { label: 'Bartolo', path: '/ai/bartolo' },
      { label: 'Análises', path: '/ai/analytics' },
    ],
  },
  {
    label: 'Documentos',
    icon: FolderOpen,
    path: '/ged',
  },
  {
    label: 'Compliance',
    icon: Shield,
    children: [
      { label: 'Dashboard', path: '/compliance' },
      { label: 'Auditoria', path: '/compliance/audit' },
      { label: 'LGPD', path: '/compliance/lgpd' },
      { label: 'Governo', path: '/compliance/government' },
    ],
  },
];

const bottomNav: NavItem[] = [
  { label: 'Configurações', icon: Settings, path: '/settings' },
  { label: 'Ajuda', icon: HelpCircle, path: '/help' },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
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

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-bg-secondary border-r border-border-subtle',
        'flex flex-col z-30 transition-all duration-300',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-border-subtle">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden"
              >
                <span className="font-display font-bold text-text-primary whitespace-nowrap">
                  Conecta PRO
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-bg-tertiary transition-colors"
        >
          <ChevronLeft
            className={cn(
              'w-5 h-5 transition-transform duration-300',
              collapsed && 'rotate-180'
            )}
          />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 scrollbar-hide">
        <ul className="space-y-1">
          {navigation.map((item) => (
            <li key={item.label}>
              {item.children ? (
                <div>
                  <button
                    onClick={() => !collapsed && toggleExpanded(item.label)}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                      'transition-all duration-200',
                      isParentActive(item.children)
                        ? 'bg-accent-primary/10 text-accent-primary'
                        : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                    )}
                  >
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    {!collapsed && (
                      <>
                        <span className="flex-1 text-left">{item.label}</span>
                        <ChevronDown
                          className={cn(
                            'w-4 h-4 transition-transform',
                            expandedItems.includes(item.label) && 'rotate-180'
                          )}
                        />
                      </>
                    )}
                  </button>
                  <AnimatePresence>
                    {!collapsed && expandedItems.includes(item.label) && (
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
                              {child.icon && <child.icon className="w-4 h-4" />}
                              <span>{child.label}</span>
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
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                      'transition-all duration-200',
                      isActive
                        ? 'bg-accent-primary/10 text-accent-primary'
                        : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                    )
                  }
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </NavLink>
              )}
            </li>
          ))}
        </ul>
      </nav>

      {/* Bottom Navigation */}
      <div className="border-t border-border-subtle p-3 space-y-1">
        {bottomNav.map((item) => (
          <NavLink
            key={item.label}
            to={item.path!}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                'transition-all duration-200',
                isActive
                  ? 'bg-accent-primary/10 text-accent-primary'
                  : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
              )
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </div>

      {/* User */}
      <div className="border-t border-border-subtle p-3">
        <div
          className={cn(
            'flex items-center gap-3 p-2 rounded-lg hover:bg-bg-tertiary transition-colors cursor-pointer',
            collapsed && 'justify-center'
          )}
        >
          <Avatar name="Jordan Admin" size="sm" status="online" />
          {!collapsed && (
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
