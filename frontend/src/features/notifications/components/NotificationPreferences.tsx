/**
 * NotificationPreferences - Modal de preferências de notificações
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

'use client';

import { X, Save } from 'lucide-react';
import { useState, useEffect } from 'react';
;

interface NotificationPreferencesProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Preferences {
  push_enabled: boolean;
  push_sound_enabled: boolean;
  push_vibration_enabled: boolean;
  email_enabled: boolean;
  notifications_enabled: boolean;
}

export function NotificationPreferences({ isOpen, onClose }: NotificationPreferencesProps) {
  const [preferences, setPreferences] = useState<Preferences>({
    push_enabled: true,
    push_sound_enabled: true,
    push_vibration_enabled: true,
    email_enabled: true,
    notifications_enabled: true,
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchPreferences();
    }
  }, [isOpen]);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/notifications/preferences/me', {
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setPreferences({
          push_enabled: data.push_enabled ?? true,
          push_sound_enabled: data.push_sound_enabled ?? true,
          push_vibration_enabled: data.push_vibration_enabled ?? true,
          email_enabled: data.email_enabled ?? true,
          notifications_enabled: data.notifications_enabled ?? true,
        });
      }
    } catch (err) {
      console.error('Erro ao buscar preferências:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch('/api/v1/notifications/preferences/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(preferences),
      });

      if (response.ok) {
        onClose();
      }
    } catch (err) {
      console.error('Erro ao salvar preferências:', err);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Preferências de Notificações
          </h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 space-y-4">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Carregando...</div>
          ) : (
            <>
              {/* Notificações Gerais */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Notificações Ativadas
                </label>
                <input
                  type="checkbox"
                  checked={preferences.notifications_enabled}
                  onChange={(e) =>
                    setPreferences({ ...preferences, notifications_enabled: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
              </div>

              {/* Push Notifications */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Notificações Push
                </label>
                <input
                  type="checkbox"
                  checked={preferences.push_enabled}
                  onChange={(e) =>
                    setPreferences({ ...preferences, push_enabled: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  disabled={!preferences.notifications_enabled}
                />
              </div>

              {/* Push Sound */}
              <div className="flex items-center justify-between ml-4">
                <label className="text-sm text-gray-600 dark:text-gray-400">
                  Som nas notificações
                </label>
                <input
                  type="checkbox"
                  checked={preferences.push_sound_enabled}
                  onChange={(e) =>
                    setPreferences({ ...preferences, push_sound_enabled: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  disabled={!preferences.push_enabled}
                />
              </div>

              {/* Push Vibration */}
              <div className="flex items-center justify-between ml-4">
                <label className="text-sm text-gray-600 dark:text-gray-400">
                  Vibração
                </label>
                <input
                  type="checkbox"
                  checked={preferences.push_vibration_enabled}
                  onChange={(e) =>
                    setPreferences({ ...preferences, push_vibration_enabled: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  disabled={!preferences.push_enabled}
                />
              </div>

              {/* Email */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Notificações por Email
                </label>
                <input
                  type="checkbox"
                  checked={preferences.email_enabled}
                  onChange={(e) =>
                    setPreferences({ ...preferences, email_enabled: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  disabled={!preferences.notifications_enabled}
                />
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={saving || loading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </div>
    </div>
  );
}
