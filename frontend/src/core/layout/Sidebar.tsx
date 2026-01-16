import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Shield,
  FileText,
  Users,
  Wrench,
  DollarSign,
  UserCircle,
  Settings,
  ChevronDown,
  ChevronRight,
  BarChart3,
  FileSearch,
  ShieldCheck,
  Building,
  Gavel,
  FolderOpen,
  PieChart,
  Target,
  FileSignature,
  Store,
  Truck,
  Calendar,
  Cpu,
  Package,
  Wallet,
  TrendingUp,
  Brain,
  Heart,
  X,
} from 'lucide-react';
import { useState } from 'react';
import { useUIStore } from '@stores/uiStore';

interface MenuItem {
  label: string;
  icon: React.ElementType;
  path?: string;
  children?: { label: string; path: string; icon?: React.ElementType }[];
}

const menuItems: MenuItem[] = [
  {
    label: 'Analytics',
    icon: LayoutDashboard,
    children: [
      { label: 'Dashboard Executivo', path: '/dashboard', icon: BarChart3 },
      { label: 'Relatorios Avancados', path: '/reports', icon: FileSearch },
      { label: 'Analytics Real-time', path: '/analytics', icon: PieChart },
    ],
  },
  {
    label: 'Compliance',
    icon: Shield,
    children: [
      { label: 'Auditoria Continua', path: '/audit', icon: ShieldCheck },
      { label: 'LGPD', path: '/lgpd', icon: Shield },
      { label: 'Integracoes Gov', path: '/government', icon: Building },
      { label: 'Licitacoes (PNCP)', path: '/bidding', icon: Gavel },
    ],
  },
  {
    label: 'Gestao Documental',
    icon: FileText,
    children: [
      { label: 'GED (OCR + IA)', path: '/ged', icon: FolderOpen },
      { label: 'Classificacao Auto', path: '/ged/classification', icon: FileSearch },
      { label: 'Busca Inteligente', path: '/ged/search', icon: FileSearch },
    ],
  },
  {
    label: 'CRM & Vendas',
    icon: Users,
    children: [
      { label: 'CRM 360', path: '/crm', icon: Target },
      { label: 'Pipeline Vendas', path: '/crm/pipeline', icon: TrendingUp },
      { label: 'Propostas', path: '/proposals', icon: FileSignature },
      { label: 'Marketplace B2B', path: '/marketplace', icon: Store },
    ],
  },
  {
    label: 'Operacoes',
    icon: Wrench,
    children: [
      { label: 'Gestao Operacoes', path: '/operations', icon: Package },
      { label: 'Servico de Campo', path: '/field-service', icon: Truck },
      { label: 'Agendamento IA', path: '/scheduling', icon: Calendar },
      { label: 'Facilities IoT', path: '/facilities', icon: Cpu },
      { label: 'Equipamentos RFID', path: '/equipment', icon: Package },
    ],
  },
  {
    label: 'Financeiro',
    icon: DollarSign,
    children: [
      { label: 'CFO Virtual', path: '/finance/cfo', icon: Brain },
      { label: 'Fluxo de Caixa', path: '/finance/cashflow', icon: Wallet },
      { label: 'Previsoes IA', path: '/finance/forecasts', icon: TrendingUp },
    ],
  },
  {
    label: 'RH',
    icon: UserCircle,
    children: [
      { label: 'RH Preditivo', path: '/hr', icon: Brain },
      { label: 'Recrutamento IA', path: '/hr/recruitment', icon: Users },
      { label: 'Saude Ocupacional', path: '/hr/health', icon: Heart },
    ],
  },
  {
    label: 'Configuracoes',
    icon: Settings,
    path: '/settings',
  },
];

interface SidebarItemProps {
  item: MenuItem;
  collapsed: boolean;
}

function SidebarItem({ item, collapsed }: SidebarItemProps) {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const hasChildren = item.children && item.children.length > 0;

  const isActive = hasChildren && item.children
    ? item.children.some((child) => location.pathname.startsWith(child.path))
    : location.pathname === item.path;

  const Icon = item.icon;

  if (!hasChildren && item.path) {
    return (
      <NavLink
        to={item.path}
        className={({ isActive }) =>
          `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
            isActive
              ? 'bg-conecta-claro text-white border-l-4 border-conecta-laranja'
              : 'text-gray-300 hover:bg-conecta-claro/50 hover:text-white'
          }`
        }
      >
        <Icon className="w-5 h-5 flex-shrink-0" />
        {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
      </NavLink>
    );
  }

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg transition-all duration-200 ${
          isActive
            ? 'bg-conecta-claro text-white'
            : 'text-gray-300 hover:bg-conecta-claro/50 hover:text-white'
        }`}
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5 flex-shrink-0" />
          {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
        </div>
        {!collapsed && hasChildren && (
          <motion.div
            animate={{ rotate: isOpen ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-4 h-4" />
          </motion.div>
        )}
      </button>

      <AnimatePresence>
        {isOpen && !collapsed && hasChildren && item.children && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="ml-4 mt-1 space-y-1 overflow-hidden"
          >
            {item.children.map((child) => (
              <NavLink
                key={child.path}
                to={child.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-conecta-laranja/20 text-conecta-laranja font-medium'
                      : 'text-gray-400 hover:bg-conecta-claro/30 hover:text-white'
                  }`
                }
              >
                {child.icon && <child.icon className="w-4 h-4" />}
                {!child.icon && <ChevronRight className="w-4 h-4" />}
                <span>{child.label}</span>
              </NavLink>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Sidebar() {
  const { sidebarOpen, sidebarCollapsed, setSidebarOpen } = useUIStore();

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          width: sidebarCollapsed ? 80 : 280,
          x: sidebarOpen ? 0 : -280,
        }}
        transition={{ duration: 0.2 }}
        className={`fixed lg:relative inset-y-0 left-0 z-50 flex flex-col bg-conecta-medio ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-conecta-claro/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-md">
              <svg className="w-6 h-6" viewBox="0 0 32 32">
                <path
                  d="M6 16L12 22L26 8"
                  stroke="#FF6B35"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              </svg>
            </div>
            {!sidebarCollapsed && (
              <div>
                <h1 className="text-lg font-bold text-white">
                  CONECTA <span className="text-conecta-laranja">PRO</span>
                </h1>
                <p className="text-[10px] text-gray-400">By Conecta Mais</p>
              </div>
            )}
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto scrollbar-thin py-4 px-3 space-y-1">
          {menuItems.map((item) => (
            <SidebarItem
              key={item.label}
              item={item}
              collapsed={sidebarCollapsed}
            />
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-conecta-claro/30">
          {!sidebarCollapsed && (
            <p className="text-xs text-gray-500 text-center">
              v1.0.0
            </p>
          )}
        </div>
      </motion.aside>
    </>
  );
}

export default Sidebar;
