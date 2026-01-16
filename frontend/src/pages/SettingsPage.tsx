import React, { useState } from 'react';
import {
  Settings,
  Building,
  Bell,
  Shield,
  Palette,
  Database,
  Key,
  Mail,
  Smartphone,
  Monitor,
} from 'lucide-react';

type SettingsTab = 'general' | 'company' | 'notifications' | 'security' | 'integrations' | 'appearance';

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('general');

  const tabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
    { id: 'general', label: 'Geral', icon: <Settings className="h-4 w-4" /> },
    { id: 'company', label: 'Empresa', icon: <Building className="h-4 w-4" /> },
    { id: 'notifications', label: 'Notificacoes', icon: <Bell className="h-4 w-4" /> },
    { id: 'security', label: 'Seguranca', icon: <Shield className="h-4 w-4" /> },
    { id: 'integrations', label: 'Integracoes', icon: <Database className="h-4 w-4" /> },
    { id: 'appearance', label: 'Aparencia', icon: <Palette className="h-4 w-4" /> },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Settings className="h-7 w-7 text-conecta-escuro" />
          Configuracoes
        </h1>
        <p className="text-gray-600 mt-1">
          Gerencie as configuracoes do sistema
        </p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-64 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-conecta-escuro text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {tab.icon}
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'general' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuracoes Gerais</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Idioma
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro">
                      <option value="pt-BR">Portugues (Brasil)</option>
                      <option value="en-US">English (US)</option>
                      <option value="es">Espanol</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fuso Horario
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro">
                      <option value="America/Sao_Paulo">America/Sao_Paulo (GMT-3)</option>
                      <option value="America/Manaus">America/Manaus (GMT-4)</option>
                      <option value="America/Recife">America/Recife (GMT-3)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Formato de Data
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro">
                      <option value="dd/MM/yyyy">DD/MM/AAAA</option>
                      <option value="MM/dd/yyyy">MM/DD/AAAA</option>
                      <option value="yyyy-MM-dd">AAAA-MM-DD</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'company' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Dados da Empresa</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Razao Social
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro"
                      placeholder="Nome da empresa"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      CNPJ
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro"
                      placeholder="00.000.000/0000-00"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email Corporativo
                    </label>
                    <input
                      type="email"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro"
                      placeholder="contato@empresa.com.br"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Preferencias de Notificacao</h2>
                <div className="space-y-4">
                  {[
                    { id: 'email', label: 'Notificacoes por Email', icon: <Mail className="h-5 w-5" /> },
                    { id: 'push', label: 'Notificacoes Push', icon: <Smartphone className="h-5 w-5" /> },
                    { id: 'desktop', label: 'Notificacoes Desktop', icon: <Monitor className="h-5 w-5" /> },
                  ].map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="text-gray-500">{item.icon}</div>
                        <span className="font-medium text-gray-900">{item.label}</span>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-conecta-escuro/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-conecta-escuro"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Seguranca</h2>
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3 mb-2">
                      <Key className="h-5 w-5 text-gray-500" />
                      <span className="font-medium text-gray-900">Autenticacao em Duas Etapas</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Adicione uma camada extra de seguranca a sua conta
                    </p>
                    <button className="px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
                      Configurar 2FA
                    </button>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3 mb-2">
                      <Shield className="h-5 w-5 text-gray-500" />
                      <span className="font-medium text-gray-900">Sessoes Ativas</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Gerencie dispositivos conectados a sua conta
                    </p>
                    <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                      Ver Sessoes
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Integracoes</h2>
                <div className="space-y-4">
                  {[
                    { name: 'ERP', status: 'connected', description: 'Integracao com sistema ERP' },
                    { name: 'WhatsApp Business', status: 'connected', description: 'Envio de notificacoes' },
                    { name: 'Google Calendar', status: 'disconnected', description: 'Sincronizacao de agenda' },
                    { name: 'Slack', status: 'disconnected', description: 'Notificacoes de equipe' },
                  ].map((integration) => (
                    <div key={integration.name} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <span className="font-medium text-gray-900">{integration.name}</span>
                        <p className="text-sm text-gray-600">{integration.description}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        integration.status === 'connected'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {integration.status === 'connected' ? 'Conectado' : 'Desconectado'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Aparencia</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Tema
                    </label>
                    <div className="flex gap-4">
                      {[
                        { id: 'light', label: 'Claro' },
                        { id: 'dark', label: 'Escuro' },
                        { id: 'system', label: 'Sistema' },
                      ].map((theme) => (
                        <button
                          key={theme.id}
                          className="flex-1 p-4 border-2 border-gray-200 rounded-lg hover:border-conecta-escuro transition-colors"
                        >
                          <span className="font-medium text-gray-900">{theme.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Densidade
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro">
                      <option value="comfortable">Confortavel</option>
                      <option value="compact">Compacto</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="mt-6 flex justify-end">
            <button className="px-6 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
              Salvar Alteracoes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
