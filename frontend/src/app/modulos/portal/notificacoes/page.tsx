'use client'

import { useState, useEffect } from 'react'
import { Bell, Check, Info } from 'lucide-react'

const API_BASE = '/api/v1/people-management/portal'

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

export default function NotificacoesPortalPage() {
  const [notifications, setNotifications] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/my-notifications`, { headers: getAuthHeaders() })
        if (res.ok) { const data = await res.json(); setNotifications(data.items || data || []) }
      } catch { setNotifications([]) } finally { setLoading(false) }
    }
    load()
  }, [])

  async function markAsRead(id: string) {
    try {
      await fetch(`${API_BASE}/my-notifications/${id}/read`, { method: 'PATCH', headers: getAuthHeaders() })
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
    } catch { /* ignore */ }
  }

  if (loading) {
    return <div className="bg-white rounded-xl p-6 shadow-sm animate-pulse"><div className="h-40 bg-gray-100 rounded" /></div>
  }

  const unread = notifications.filter(n => !n.is_read)
  const read = notifications.filter(n => n.is_read)

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Bell className="w-5 h-5 text-orange-600" />
        Notificações ({unread.length} não lidas)
      </h2>

      {notifications.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhuma notificação</p>
      ) : (
        <div className="space-y-3">
          {unread.map((n: any) => (
            <div key={n.id} className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <Info className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-medium text-sm">{n.title}</p>
                <p className="text-xs text-gray-600 mt-1">{n.message}</p>
                <p className="text-xs text-gray-400 mt-2">{n.created_at}</p>
              </div>
              <button type="button" onClick={() => markAsRead(n.id)} className="text-blue-600 hover:text-blue-800">
                <Check className="w-4 h-4" />
              </button>
            </div>
          ))}
          {read.map((n: any) => (
            <div key={n.id} className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg opacity-75">
              <Info className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-600">{n.title}</p>
                <p className="text-xs text-gray-500 mt-1">{n.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
