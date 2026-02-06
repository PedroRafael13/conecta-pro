'use client';

import { Bell, X, CheckCircle, CheckCheck, Trash2, Clock, AlertTriangle, ChevronRight, Settings, Eye } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
;
import { Button } from '@/components/ui/button';
import { useNotifications, useUnreadCount, useUserAlerts } from '@/hooks/useNotifications';

// Cores dos tipos de notificacao
const NOTIFICATION_TYPE_COLORS: Record<NotificationType, string> = {
  sistema: 'bg-blue-500',
  operacional: 'bg-green-500',
  alerta: 'bg-red-500',
  comunicado: 'bg-purple-500',
  tarefa: 'bg-orange-500',
  lembrete: 'bg-yellow-500',
};

interface NotificationCenterProps {
  className?: string;
}

export function NotificationCenter({ className = '' }: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Notificacoes
  const {
    notifications,
    isLoading,
    refresh,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  } = useNotifications({ initialPageSize: 10, pollInterval: 30000 });

  // Contagem de nao lidas
  const { total: unreadTotal, refresh: refreshCount } = useUnreadCount(30000);

  // Alertas ativos
  const { alerts, acknowledge: acknowledgeAlert } = useUserAlerts(30000);

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      refresh();
      refreshCount();
    }
  };

  const handleMarkAsRead = async (notification: Notification, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!notification.is_read) {
      await markAsRead(notification.id);
      refreshCount();
    }
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
    refreshCount();
    refresh();
  };

  const handleDelete = async (notification: Notification, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteNotification(notification.id);
    refreshCount();
  };

  const handleAcknowledgeAlert = async (alert: Alert, e: React.MouseEvent) => {
    e.stopPropagation();
    await acknowledgeAlert(alert.id);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Agora';
    if (minutes < 60) return `${minutes}min`;
    if (hours < 24) return `${hours}h`;
    if (days < 7) return `${days}d`;

    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  };

  const totalBadge = unreadTotal + alerts.length;

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      {/* Bell Button */}
      <button
        onClick={handleToggle}
        className="relative p-2 rounded-lg hover:bg-[hsl(var(--muted))] transition-colors"
        aria-label="Notificacoes"
      >
        <Bell className="w-5 h-5 text-[hsl(var(--muted-foreground))]" />
        {totalBadge > 0 && (
          <span className="absolute -top-0.5 -right-0.5 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-medium">
            {totalBadge > 99 ? '99+' : totalBadge}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-96 max-h-[80vh] overflow-hidden bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl shadow-xl z-50">
          {/* Header */}
          <div className="sticky top-0 z-10 flex items-center justify-between px-4 py-3 border-b border-[hsl(var(--border))] bg-[hsl(var(--card))]">
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-[hsl(var(--primary))]" />
              <h3 className="font-semibold text-[hsl(var(--foreground))]">Notificacoes</h3>
              {unreadTotal > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-red-500/10 text-red-500 text-xs font-medium">
                  {unreadTotal} novas
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              {unreadTotal > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMarkAllAsRead}
                  title="Marcar todas como lidas"
                >
                  <CheckCheck className="w-4 h-4" />
                </Button>
              )}
              <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)}>
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Content */}
          <div className="max-h-[60vh] overflow-y-auto">
            {/* Alertas */}
            {alerts.length > 0 && (
              <div className="px-3 py-2 border-b border-[hsl(var(--border))]">
                <p className="text-xs font-medium text-[hsl(var(--muted-foreground))] mb-2 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  Alertas Ativos
                </p>
                <div className="space-y-2">
                  {alerts.slice(0, 3).map((alert) => (
                    <div
                      key={alert.id}
                      className="bg-red-500/10 border border-red-500/20 rounded-lg p-2"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-red-500 truncate">{alert.title}</p>
                          <p className="text-xs text-red-400 line-clamp-1">{alert.message}</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => handleAcknowledgeAlert(alert, e)}
                          className="shrink-0 text-red-500 hover:text-red-600 h-7 px-2"
                        >
                          <CheckCircle className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Loading */}
            {isLoading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[hsl(var(--primary))]" />
              </div>
            )}

            {/* Notificacoes */}
            {!isLoading && notifications.length > 0 && (
              <div className="divide-y divide-[hsl(var(--border))]">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`px-4 py-3 hover:bg-[hsl(var(--muted))]/50 transition-colors cursor-pointer ${
                      !notification.is_read ? 'bg-[hsl(var(--primary))]/5' : ''
                    }`}
                    onClick={(e) => {
                      handleMarkAsRead(notification, e);
                      if (notification.action_url) {
                        setIsOpen(false);
                      }
                    }}
                  >
                    <div className="flex items-start gap-3">
                      {/* Indicator */}
                      <div
                        className={`w-2 h-2 rounded-full mt-2 shrink-0 ${
                          notification.is_read
                            ? 'bg-transparent'
                            : NOTIFICATION_TYPE_COLORS[notification.type]
                        }`}
                      />

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <p
                            className={`text-sm truncate ${
                              notification.is_read
                                ? 'text-[hsl(var(--muted-foreground))]'
                                : 'text-[hsl(var(--foreground))] font-medium'
                            }`}
                          >
                            {notification.title}
                          </p>
                          <span className="text-xs text-[hsl(var(--muted-foreground))] shrink-0">
                            {formatDate(notification.created_at)}
                          </span>
                        </div>
                        <p className="text-xs text-[hsl(var(--muted-foreground))] line-clamp-2 mt-0.5">
                          {notification.body}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-1.5 py-0.5 rounded bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]">
                            {NOTIFICATION_TYPE_LABELS[notification.type]}
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-1 shrink-0">
                        {notification.action_url && (
                          <Link href={notification.action_url}>
                            <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                              <Eye className="w-3 h-3" />
                            </Button>
                          </Link>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => handleDelete(notification, e)}
                          className="h-7 w-7 p-0 text-red-500 hover:text-red-600"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Empty */}
            {!isLoading && notifications.length === 0 && alerts.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12 px-4">
                <Bell className="w-12 h-12 text-[hsl(var(--muted-foreground))] mb-3" />
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  Nenhuma notificacao
                </p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 z-10 flex items-center justify-between px-4 py-3 border-t border-[hsl(var(--border))] bg-[hsl(var(--card))]">
            <Link
              href="/modulos/operacional/notificacoes"
              onClick={() => setIsOpen(false)}
              className="text-sm text-[hsl(var(--primary))] hover:underline flex items-center gap-1"
            >
              Ver todas
              <ChevronRight className="w-4 h-4" />
            </Link>
            <Link
              href="/modulos/configuracoes"
              onClick={() => setIsOpen(false)}
              className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] flex items-center gap-1"
            >
              <Settings className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationCenter;
