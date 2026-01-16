import React, { useState } from 'react';
import {
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Edit2,
  Camera,
  Key,
  Shield,
  Bell,
} from 'lucide-react';

export function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);

  const user = {
    name: 'Jordan Silva',
    email: 'jordan@conectapro.com.br',
    phone: '(11) 99999-9999',
    department: 'Tecnologia',
    position: 'Desenvolvedor Senior',
    location: 'Sao Paulo, SP',
    joinDate: '2023-03-15',
    avatar: null,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <User className="h-7 w-7 text-conecta-escuro" />
          Meu Perfil
        </h1>
        <p className="text-gray-600 mt-1">
          Gerencie suas informacoes pessoais e preferencias
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
            <div className="relative inline-block">
              <div className="w-32 h-32 bg-conecta-escuro rounded-full flex items-center justify-center mx-auto">
                <span className="text-4xl font-bold text-white">
                  {user.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <button className="absolute bottom-0 right-0 p-2 bg-white border border-gray-200 rounded-full shadow-sm hover:bg-gray-50">
                <Camera className="h-4 w-4 text-gray-600" />
              </button>
            </div>
            <h2 className="text-xl font-bold text-gray-900 mt-4">{user.name}</h2>
            <p className="text-gray-600">{user.position}</p>
            <p className="text-sm text-gray-500 mt-1">{user.department}</p>

            <div className="mt-6 pt-6 border-t border-gray-200 space-y-3">
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <Mail className="h-4 w-4" />
                <span>{user.email}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <Phone className="h-4 w-4" />
                <span>{user.phone}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <MapPin className="h-4 w-4" />
                <span>{user.location}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <Calendar className="h-4 w-4" />
                <span>Desde {new Date(user.joinDate).toLocaleDateString('pt-BR')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal Info */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Informacoes Pessoais</h2>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-conecta-escuro hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Edit2 className="h-4 w-4" />
                {isEditing ? 'Cancelar' : 'Editar'}
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome Completo
                </label>
                <input
                  type="text"
                  value={user.name}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro disabled:bg-gray-50 disabled:text-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={user.email}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro disabled:bg-gray-50 disabled:text-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefone
                </label>
                <input
                  type="tel"
                  value={user.phone}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro disabled:bg-gray-50 disabled:text-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Localizacao
                </label>
                <input
                  type="text"
                  value={user.location}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro disabled:bg-gray-50 disabled:text-gray-500"
                />
              </div>
            </div>
            {isEditing && (
              <div className="mt-4 flex justify-end">
                <button className="px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
                  Salvar Alteracoes
                </button>
              </div>
            )}
          </div>

          {/* Security */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Seguranca</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Key className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="font-medium text-gray-900">Senha</p>
                    <p className="text-sm text-gray-600">Ultima alteracao ha 30 dias</p>
                  </div>
                </div>
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                  Alterar
                </button>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Shield className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="font-medium text-gray-900">Autenticacao em Duas Etapas</p>
                    <p className="text-sm text-gray-600">Nao configurado</p>
                  </div>
                </div>
                <button className="px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
                  Configurar
                </button>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Preferencias de Notificacao
            </h2>
            <div className="space-y-3">
              {[
                { id: 'email', label: 'Notificacoes por email' },
                { id: 'push', label: 'Notificacoes push' },
                { id: 'updates', label: 'Atualizacoes do sistema' },
                { id: 'reports', label: 'Relatorios semanais' },
              ].map((item) => (
                <div key={item.id} className="flex items-center justify-between py-2">
                  <span className="text-gray-700">{item.label}</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-conecta-escuro/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-conecta-escuro"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
