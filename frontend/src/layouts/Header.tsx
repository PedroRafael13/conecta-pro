'use client';

import { useState, Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Bell,
  Settings,
  LogOut,
  User,
  ChevronDown,
  Moon,
  Sun,
  Command,
  HelpCircle,
} from 'lucide-react';
import { cn } from '@/shared/utils/cn';
import { Avatar, Badge, Button } from '@/design-system/components';

interface HeaderProps {
  sidebarCollapsed: boolean;
}

// Mock notifications
const notifications = [
  {
    id: '1',
    type: 'info',
    title: 'Novo lead cadastrado',
    description: 'Empresa ABC Ltda foi adicionada ao pipeline',
    time: '5 min',
    read: false,
  },
  {
    id: '2',
    type: 'warning',
    title: 'Contrato próximo do vencimento',
    description: 'Contrato #1234 vence em 7 dias',
    time: '1h',
    read: false,
  },
  {
    id: '3',
    type: 'success',
    title: 'Pagamento recebido',
    description: 'R$ 15.000,00 de Cliente XYZ',
    time: '2h',
    read: true,
  },
];

export function Header({ sidebarCollapsed }: HeaderProps) {
  const navigate = useNavigate();
  const [searchOpen, setSearchOpen] = useState(false);
  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <header
      className={cn(
        'fixed top-0 right-0 h-16 bg-bg-secondary/80 backdrop-blur-xl',
        'border-b border-border-subtle flex items-center justify-between px-6 z-20',
        'transition-all duration-300',
        sidebarCollapsed ? 'left-20' : 'left-64'
      )}
    >
      {/* Left: Search */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSearchOpen(true)}
          className={cn(
            'flex items-center gap-3 px-4 py-2 rounded-lg',
            'bg-bg-tertiary border border-border-subtle',
            'text-text-muted hover:text-text-secondary hover:border-border-default',
            'transition-all duration-200 w-72'
          )}
        >
          <Search className="w-4 h-4" />
          <span className="text-sm">Buscar...</span>
          <kbd className="ml-auto flex items-center gap-1 px-2 py-0.5 rounded bg-bg-elevated text-2xs text-text-muted">
            <Command className="w-3 h-3" />K
          </kbd>
        </button>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Theme Toggle */}
        <Button variant="ghost" size="icon-sm">
          <Moon className="w-5 h-5" />
        </Button>

        {/* Help */}
        <Button variant="ghost" size="icon-sm">
          <HelpCircle className="w-5 h-5" />
        </Button>

        {/* Notifications */}
        <Menu as="div" className="relative">
          <Menu.Button className="relative p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-tertiary transition-colors">
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full" />
            )}
          </Menu.Button>
          <Transition
            as={Fragment}
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <Menu.Items className="absolute right-0 mt-2 w-80 bg-bg-secondary rounded-xl border border-border-subtle shadow-dropdown overflow-hidden focus:outline-none">
              <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
                <h3 className="font-semibold text-text-primary">Notificações</h3>
                {unreadCount > 0 && (
                  <Badge variant="primary" size="sm">
                    {unreadCount} novas
                  </Badge>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto divide-y divide-border-subtle">
                {notifications.map((notification) => (
                  <Menu.Item key={notification.id}>
                    {({ active }) => (
                      <button
                        className={cn(
                          'w-full px-4 py-3 text-left transition-colors',
                          active && 'bg-bg-tertiary',
                          !notification.read && 'bg-accent-primary/5'
                        )}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={cn(
                              'w-2 h-2 mt-2 rounded-full flex-shrink-0',
                              notification.type === 'info' && 'bg-info',
                              notification.type === 'warning' && 'bg-warning',
                              notification.type === 'success' && 'bg-success'
                            )}
                          />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-text-primary">
                              {notification.title}
                            </p>
                            <p className="text-xs text-text-secondary mt-0.5 truncate">
                              {notification.description}
                            </p>
                          </div>
                          <span className="text-2xs text-text-muted">
                            {notification.time}
                          </span>
                        </div>
                      </button>
                    )}
                  </Menu.Item>
                ))}
              </div>
              <div className="px-4 py-3 border-t border-border-subtle">
                <button className="w-full text-sm text-accent-primary hover:text-accent-primary-hover font-medium">
                  Ver todas as notificações
                </button>
              </div>
            </Menu.Items>
          </Transition>
        </Menu>

        {/* Divider */}
        <div className="w-px h-6 bg-border-subtle mx-2" />

        {/* User Menu */}
        <Menu as="div" className="relative">
          <Menu.Button className="flex items-center gap-3 p-1.5 rounded-lg hover:bg-bg-tertiary transition-colors">
            <Avatar name="Jordan Admin" size="sm" status="online" />
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium text-text-primary">Jordan</p>
              <p className="text-xs text-text-muted">Administrador</p>
            </div>
            <ChevronDown className="w-4 h-4 text-text-muted hidden md:block" />
          </Menu.Button>
          <Transition
            as={Fragment}
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <Menu.Items className="absolute right-0 mt-2 w-56 bg-bg-secondary rounded-xl border border-border-subtle shadow-dropdown py-1 focus:outline-none">
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={() => navigate('/profile')}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-2.5 text-sm',
                      'text-text-secondary transition-colors',
                      active && 'bg-bg-tertiary text-text-primary'
                    )}
                  >
                    <User className="w-4 h-4" />
                    Meu Perfil
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={() => navigate('/settings')}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-2.5 text-sm',
                      'text-text-secondary transition-colors',
                      active && 'bg-bg-tertiary text-text-primary'
                    )}
                  >
                    <Settings className="w-4 h-4" />
                    Configurações
                  </button>
                )}
              </Menu.Item>
              <div className="my-1 border-t border-border-subtle" />
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={() => navigate('/login')}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-2.5 text-sm',
                      'text-danger transition-colors',
                      active && 'bg-danger/10'
                    )}
                  >
                    <LogOut className="w-4 h-4" />
                    Sair
                  </button>
                )}
              </Menu.Item>
            </Menu.Items>
          </Transition>
        </Menu>
      </div>
    </header>
  );
}
