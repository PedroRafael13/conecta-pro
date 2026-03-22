'use client';

import { useState, useEffect } from 'react';
import {
  Loader2,
  HardDrive,
  Mail,
  FileText,
  Clock,
  Save,
  CheckCircle,
  XCircle,
  Pencil,
  ToggleLeft,
  ToggleRight,
  Link,
  Unlink,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/ged';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface DriveConfig {
  connected: boolean;
  folder_id: string;
  email: string;
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
}

interface DocumentType {
  id: string;
  name: string;
  code: string;
  enabled: boolean;
}

interface ScheduleConfig {
  enabled: boolean;
  cron_expression: string;
  description: string;
  last_run: string | null;
}

export default function ConfiguracoesPage() {
  const [loading, setLoading] = useState(true);
  const [savingSection, setSavingSection] = useState<string | null>(null);

  const [driveConfig, setDriveConfig] = useState<DriveConfig>({
    connected: false,
    folder_id: '',
    email: '',
  });

  const [emailTemplates, setEmailTemplates] = useState<EmailTemplate[]>([]);

  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);

  const [schedule, setSchedule] = useState<ScheduleConfig>({
    enabled: false,
    cron_expression: '0 6 1 * *',
    description: 'Todo dia 1 as 06:00',
    last_run: null,
  });

  useEffect(() => {
    fetchConfig();
  }, []);

  async function fetchConfig() {
    setLoading(true);
    try {
      const [driveRes, templatesRes, typesRes, scheduleRes] = await Promise.all([
        fetch(`${API_BASE}/config/drive`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/config/email-templates`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/config/document-types`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/config/schedule`, { headers: getAuthHeaders() }),
      ]);

      if (driveRes.ok) setDriveConfig(await driveRes.json());
      if (templatesRes.ok) {
        const data = await templatesRes.json();
        setEmailTemplates(Array.isArray(data) ? data : data.items || []);
      }
      if (typesRes.ok) {
        const data = await typesRes.json();
        setDocumentTypes(Array.isArray(data) ? data : data.items || []);
      }
      if (scheduleRes.ok) setSchedule(await scheduleRes.json());
    } catch {
      // silenced
    } finally {
      setLoading(false);
    }
  }

  async function saveDriveConfig() {
    setSavingSection('drive');
    try {
      await fetch(`${API_BASE}/config/drive`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(driveConfig),
      });
    } catch {
      // silenced
    } finally {
      setSavingSection(null);
    }
  }

  async function handleDriveConnect() {
    try {
      const res = await fetch(`${API_BASE}/config/drive/connect`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.auth_url) {
          window.open(data.auth_url, '_blank');
        }
        fetchConfig();
      }
    } catch {
      // silenced
    }
  }

  async function handleDriveDisconnect() {
    if (!confirm('Deseja desconectar o Google Drive?')) return;
    try {
      await fetch(`${API_BASE}/config/drive/disconnect`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      setDriveConfig({ connected: false, folder_id: '', email: '' });
    } catch {
      // silenced
    }
  }

  async function toggleDocumentType(docType: DocumentType) {
    const updated = { ...docType, enabled: !docType.enabled };
    try {
      await fetch(`${API_BASE}/config/document-types/${docType.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updated),
      });
      setDocumentTypes((prev) =>
        prev.map((dt) => (dt.id === docType.id ? updated : dt))
      );
    } catch {
      // silenced
    }
  }

  async function saveSchedule() {
    setSavingSection('schedule');
    try {
      await fetch(`${API_BASE}/config/schedule`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(schedule),
      });
    } catch {
      // silenced
    } finally {
      setSavingSection(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">Carregando configuracoes...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuracoes GED</h1>
        <p className="text-gray-500 mt-1">Gerencie integracoes, templates e preferencias</p>
      </div>

      {/* Google Drive */}
      <Card className="border border-gray-200">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <HardDrive className="h-5 w-5 text-green-600" />
            </div>
            <div className="flex-1">
              <CardTitle className="text-base font-semibold">Google Drive</CardTitle>
              <p className="text-sm text-gray-500">Integracao para envio automatico de kits</p>
            </div>
            {driveConfig.connected ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                <CheckCircle className="h-3 w-3" />
                Conectado
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
                <XCircle className="h-3 w-3" />
                Desconectado
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ID da Pasta</label>
            <input
              type="text"
              value={driveConfig.folder_id}
              onChange={(e) => setDriveConfig({ ...driveConfig, folder_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder="ID da pasta no Google Drive"
            />
          </div>
          {driveConfig.connected && driveConfig.email && (
            <p className="text-xs text-gray-500">Conectado como: {driveConfig.email}</p>
          )}
          <div className="flex gap-2">
            {driveConfig.connected ? (
              <button
                onClick={handleDriveDisconnect}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
              >
                <Unlink className="h-4 w-4" />
                Desconectar
              </button>
            ) : (
              <button
                onClick={handleDriveConnect}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
              >
                <Link className="h-4 w-4" />
                Conectar Google Drive
              </button>
            )}
            <button
              onClick={saveDriveConfig}
              disabled={savingSection === 'drive'}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {savingSection === 'drive' ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Salvar
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Email Templates */}
      <Card className="border border-gray-200">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Mail className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-base font-semibold">Templates de Email</CardTitle>
              <p className="text-sm text-gray-500">Modelos de email para envio de kits</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {emailTemplates.length === 0 ? (
            <p className="text-sm text-gray-400 py-4 text-center">Nenhum template cadastrado</p>
          ) : (
            <div className="space-y-2">
              {emailTemplates.map((template) => (
                <div
                  key={template.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{template.name}</p>
                    <p className="text-xs text-gray-500">Assunto: {template.subject}</p>
                  </div>
                  <button
                    className="p-1.5 rounded hover:bg-gray-200 transition-colors"
                    title="Editar template"
                  >
                    <Pencil className="h-4 w-4 text-gray-500" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Document Types */}
      <Card className="border border-gray-200">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-50 rounded-lg">
              <FileText className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <CardTitle className="text-base font-semibold">Tipos de Documento</CardTitle>
              <p className="text-sm text-gray-500">Ative ou desative tipos de documentos nos kits</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {documentTypes.length === 0 ? (
            <p className="text-sm text-gray-400 py-4 text-center">Nenhum tipo de documento cadastrado</p>
          ) : (
            <div className="space-y-2">
              {documentTypes.map((docType) => (
                <div
                  key={docType.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{docType.name}</p>
                    <p className="text-xs text-gray-500 font-mono">{docType.code}</p>
                  </div>
                  <button
                    onClick={() => toggleDocumentType(docType)}
                    className="focus:outline-none"
                    title={docType.enabled ? 'Desativar' : 'Ativar'}
                  >
                    {docType.enabled ? (
                      <ToggleRight className="h-7 w-7 text-blue-600" />
                    ) : (
                      <ToggleLeft className="h-7 w-7 text-gray-400" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Schedule */}
      <Card className="border border-gray-200">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Clock className="h-5 w-5 text-purple-600" />
            </div>
            <div className="flex-1">
              <CardTitle className="text-base font-semibold">Coleta Automatica</CardTitle>
              <p className="text-sm text-gray-500">Agendamento de montagem automatica de kits</p>
            </div>
            <button
              onClick={() => setSchedule({ ...schedule, enabled: !schedule.enabled })}
              className="focus:outline-none"
            >
              {schedule.enabled ? (
                <ToggleRight className="h-7 w-7 text-blue-600" />
              ) : (
                <ToggleLeft className="h-7 w-7 text-gray-400" />
              )}
            </button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Expressao Cron</label>
            <input
              type="text"
              value={schedule.cron_expression}
              onChange={(e) => setSchedule({ ...schedule, cron_expression: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder="0 6 1 * *"
            />
            <p className="text-xs text-gray-500 mt-1">{schedule.description}</p>
          </div>
          {schedule.last_run && (
            <p className="text-xs text-gray-500">
              Ultima execucao: {new Date(schedule.last_run).toLocaleString('pt-BR')}
            </p>
          )}
          <button
            onClick={saveSchedule}
            disabled={savingSection === 'schedule'}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {savingSection === 'schedule' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Salvar Agendamento
          </button>
        </CardContent>
      </Card>
    </div>
  );
}
