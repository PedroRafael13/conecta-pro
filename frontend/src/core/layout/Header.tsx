import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu,
  Bell,
  ChevronDown,
  User,
  Settings,
  HelpCircle,
  LogOut,
  PanelLeftClose,
  PanelLeft,
} from 'lucide-react';
import { useAuth } from '@core/auth';
import { useUIStore } from '@stores/uiStore';
import { Breadcrumbs } from '@core/navigation/Breadcrumbs';

export function Header() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const {
    sidebarCollapsed,
    toggleSidebar,
    toggleSidebarCollapse,
  } = useUIStore();

  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setShowUserMenu(false);
      }
      if (
        notificationRef.current &&
        !notificationRef.current.contains(event.target as Node)
      ) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const initials = user?.name
    ? user.name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'U';

  return (
    <header className="sticky top-0 z-30 h-16 bg-conecta-escuro border-b border-conecta-medio flex items-center justify-between px-4 lg:px-6">
      {/* Left side */}
      <div className="flex items-center gap-4">
        {/* Mobile menu toggle */}
        <button
          onClick={toggleSidebar}
          className="lg:hidden p-2 text-gray-300 hover:text-white hover:bg-conecta-medio rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Desktop collapse toggle */}
        <button
          onClick={toggleSidebarCollapse}
          className="hidden lg:flex p-2 text-gray-300 hover:text-white hover:bg-conecta-medio rounded-lg transition-colors"
        >
          {sidebarCollapsed ? (
            <PanelLeft className="w-5 h-5" />
          ) : (
            <PanelLeftClose className="w-5 h-5" />
          )}
        </button>

        {/* Breadcrumbs */}
        <div className="hidden md:block">
          <Breadcrumbs />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Notifications */}
        <div className="relative" ref={notificationRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-gray-300 hover:text-white hover:bg-conecta-medio rounded-lg transition-colors"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-conecta-laranja rounded-full" />
          </button>

          <AnimatePresence>
            {showNotifications && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-dropdown overflow-hidden"
              >
                <div className="p-4 border-b">
                  <h3 className="font-semibold text-gray-900">Notificacoes</h3>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  <div className="p-4 text-center text-sm text-gray-500">
                    Nenhuma notificacao nova
                  </div>
                </div>
                <div className="p-3 border-t bg-gray-50">
                  <button className="w-full text-sm text-conecta-escuro hover:text-conecta-medio font-medium">
                    Ver todas
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* User Menu */}
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 p-1.5 hover:bg-conecta-medio rounded-lg transition-colors"
          >
            <div className="w-8 h-8 bg-conecta-laranja rounded-full flex items-center justify-center">
              <span className="text-sm font-semibold text-white">{initials}</span>
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-sm font-medium text-white truncate max-w-[120px]">
                {user?.name || 'Usuario'}
              </p>
              <p className="text-xs text-gray-400 truncate max-w-[120px]">
                {user?.role || 'Membro'}
              </p>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </button>

          <AnimatePresence>
            {showUserMenu && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-dropdown overflow-hidden"
              >
                {/* User info */}
                <div className="p-4 border-b bg-gray-50">
                  <p className="font-medium text-gray-900">{user?.name}</p>
                  <p className="text-sm text-gray-500">{user?.email}</p>
                </div>

                {/* Menu items */}
                <div className="py-2">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      navigate('/profile');
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <User className="w-4 h-4" />
                    Meu Perfil
                  </button>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      navigate('/settings');
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Settings className="w-4 h-4" />
                    Configuracoes
                  </button>
                  <button
                    onClick={() => setShowUserMenu(false)}
                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <HelpCircle className="w-4 h-4" />
                    Ajuda
                  </button>
                </div>

                {/* Logout */}
                <div className="py-2 border-t">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4" />
                    Sair
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}

export default Header;
