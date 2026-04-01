'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Bell, ArrowLeft, ShieldCheck, LogOut, Loader2, AlertCircle, CheckCheck, Circle } from 'lucide-react';

const API_BASE = '/api/v1/people-management/portal';

function getPortalHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Notification {
  id: number | null;
  title: string | null;
  message: string | null;
  is_read: boolean;
  notification_type: string | null;
  created_at: string | null;
}

const typeColors: Record<string, string> = {
  info: 'bg-blue-100 text-blue-700',
  warning: 'bg-yellow-100 text-yellow-700',
  success: 'bg-green-100 text-green-700',
  error: 'bg-red-100 text-red-600',
  payslip: 'bg-purple-100 text-purple-700',
  vacation: 'bg-green-100 text-green-700',
  document: 'bg-orange-100 text-orange-700',
};

const fmtDate = (d: string | null) => {
  if (!d) return '';
  const date = new Date(d);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `há ${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `há ${hours}h`;
  return date.toLocaleDateString('pt-BR');
};

export default function NotificacoesPage() {
  const router = useRouter();
  const [employeeName, setEmployeeName] = useState('');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [markingAll, setMarkingAll] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('portal_token');
    if (!token) { router.push('/portal-funcionario/login'); return; }
    setEmployeeName(localStorage.getItem('portal_employee_name') || 'Funcionário');
    loadNotifications();
  }, [router]);

  async function loadNotifications() {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/my-notifications`, { headers: getPortalHeaders() });
      if (res.ok) {
        const data = await res.json();
        setNotifications(Array.isArray(data) ? data : (data.items || data.notifications || []));
      } else {
        setNotifications([]);
      }
    } catch {
      setError('Erro ao carregar notificações.');
    } finally {
      setLoading(false);
    }
  }

  async function markAsRead(n: Notification) {
    if (n.is_read || !n.id) return;
    try {
      const res = await fetch(`${API_BASE}/my-notifications/${n.id}/read`, {
        method: 'PATCH',
        headers: getPortalHeaders(),
      });
      if (res.ok) {
        setNotifications(prev => prev.map(item => item.id === n.id ? { ...item, is_read: true } : item));
      }
    } catch { /* ignore */ }
  }

  async function markAllRead() {
    setMarkingAll(true);
    const unread = notifications.filter(n => !n.is_read && n.id);
    await Promise.all(unread.map(n =>
      fetch(`${API_BASE}/my-notifications/${n.id}/read`, { method: 'PATCH', headers: getPortalHeaders() })
    ));
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    setMarkingAll(false);
  }

  const handleLogout = () => {
    localStorage.removeItem('portal_token');
    localStorage.removeItem('portal_refresh_token');
    localStorage.removeItem('portal_employee_name');
    router.push('/portal-funcionario/login');
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-[#0A2540] text-white">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-6 h-6 text-blue-300" />
            <div>
              <h1 className="text-base font-bold leading-none">CONECTA PRO</h1>
              <p className="text-xs text-blue-300">Portal do Funcionário</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-blue-200 hidden sm:block">{employeeName}</span>
            <button onClick={handleLogout} className="text-blue-300 hover:text-white" title="Sair">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Link href="/portal-funcionario/dashboard" className="text-gray-500 hover:text-gray-700">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Bell className="w-5 h-5 text-pink-600" /> Notificações
              {unreadCount > 0 && (
                <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{unreadCount}</span>
              )}
            </h2>
          </div>
          {unreadCount > 0 && (
            <button
              onClick={markAllRead}
              disabled={markingAll}
              className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800 font-medium transition"
            >
              {markingAll ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCheck className="w-4 h-4" />}
              Marcar todas como lidas
            </button>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 flex items-center gap-2 text-red-700 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
            <Bell className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Nenhuma notificação.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map((n, i) => (
              <div
                key={n.id || i}
                onClick={() => markAsRead(n)}
                className={`bg-white rounded-xl shadow-sm p-4 cursor-pointer transition hover:shadow-md ${!n.is_read ? 'border-l-4 border-blue-500' : ''}`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex-shrink-0">
                    {n.is_read
                      ? <Circle className="w-4 h-4 text-gray-300" />
                      : <Circle className="w-4 h-4 text-blue-500 fill-blue-500" />
                    }
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`font-medium text-sm ${n.is_read ? 'text-gray-600' : 'text-gray-900'}`}>
                        {n.title || 'Notificação'}
                      </p>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {n.notification_type && (
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${typeColors[n.notification_type] || 'bg-gray-100 text-gray-600'}`}>
                            {n.notification_type}
                          </span>
                        )}
                        <span className="text-xs text-gray-400">{fmtDate(n.created_at)}</span>
                      </div>
                    </div>
                    {n.message && (
                      <p className={`text-sm mt-0.5 ${n.is_read ? 'text-gray-400' : 'text-gray-600'}`}>{n.message}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
