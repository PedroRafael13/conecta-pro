import React, { useState } from 'react';
import { 
  MapPin, 
  Calendar, 
  Users, 
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  RotateCcw,
  Plus
} from 'lucide-react';

interface Site {
  id: string;
  name: string;
  address: string;
  status: 'active' | 'inactive';
  coordinates: [number, number];
  shifts: Shift[];
  assignedStaff: number;
  requiredStaff: number;
}

interface Shift {
  id: string;
  siteId: string;
  startTime: string;
  endTime: string;
  date: string;
  assignedEmployee?: Employee;
  status: 'scheduled' | 'in-progress' | 'completed' | 'no-show';
}

interface Employee {
  id: string;
  name: string;
  position: string;
  avatar?: string;
  skills: string[];
  isAvailable: boolean;
}

export const OperationsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'sites' | 'schedules' | 'substitutions'>('sites');

  // Mock data
  const [sites] = useState<Site[]>([
    {
      id: '1',
      name: 'Shopping Center Norte',
      address: 'Av. Paulista, 1000 - São Paulo/SP',
      status: 'active',
      coordinates: [-23.5505, -46.6333],
      shifts: [],
      assignedStaff: 12,
      requiredStaff: 15
    },
    {
      id: '2',
      name: 'Condomínio Residencial Aurora',
      address: 'Rua das Flores, 500 - São Paulo/SP',
      status: 'active',
      coordinates: [-23.5505, -46.6333],
      shifts: [],
      assignedStaff: 8,
      requiredStaff: 8
    }
  ]);

  const [todaySchedules] = useState([
    {
      id: '1',
      site: 'Shopping Center Norte',
      employee: 'João Silva',
      shift: '08:00 - 16:00',
      status: 'in-progress',
      position: 'Porteiro'
    },
    {
      id: '2',
      site: 'Condomínio Aurora',
      employee: 'Maria Santos',
      shift: '16:00 - 00:00',
      status: 'scheduled',
      position: 'Recepcionista'
    }
  ]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'in-progress':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'no-show':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Calendar className="w-4 h-4 text-blue-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in-progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'no-show':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <MapPin className="w-8 h-8 mr-3 text-blue-600" />
                Gestão de Operações
              </h1>
              <p className="text-gray-600 mt-1">
                Postos, escalas e substituições em tempo real
              </p>
            </div>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Nova Escala</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Postos Ativos</p>
                <p className="text-3xl font-bold text-gray-900">{sites.filter(s => s.status === 'active').length}</p>
              </div>
              <MapPin className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Escalas Hoje</p>
                <p className="text-3xl font-bold text-gray-900">{todaySchedules.length}</p>
              </div>
              <Calendar className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Substituições</p>
                <p className="text-3xl font-bold text-gray-900">3</p>
                <p className="text-xs text-orange-600">Pendentes</p>
              </div>
              <RotateCcw className="w-8 h-8 text-orange-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Eficiência</p>
                <p className="text-3xl font-bold text-gray-900">94%</p>
              </div>
              <Users className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'sites', label: 'Postos', count: sites.length },
                { id: 'schedules', label: 'Escalas', count: todaySchedules.length },
                { id: 'substitutions', label: 'Substituições', count: 3 },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.label} ({tab.count})
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          
          {/* Sites Tab */}
          {activeTab === 'sites' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Postos de Trabalho</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {sites.map((site) => (
                  <div key={site.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-medium text-gray-900">{site.name}</h3>
                        <p className="text-sm text-gray-600">{site.address}</p>
                      </div>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        site.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {site.status}
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Staff Alocado:</span>
                        <span className="font-medium">{site.assignedStaff}/{site.requiredStaff}</span>
                      </div>
                      
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            site.assignedStaff >= site.requiredStaff ? 'bg-green-500' : 'bg-yellow-500'
                          }`}
                          style={{ width: `${(site.assignedStaff / site.requiredStaff) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Schedules Tab */}
          {activeTab === 'schedules' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Escalas de Hoje</h2>
              <div className="space-y-4">
                {todaySchedules.map((schedule) => (
                  <div key={schedule.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(schedule.status)}
                      <div>
                        <h3 className="font-medium text-gray-900">{schedule.employee}</h3>
                        <p className="text-sm text-gray-600">{schedule.position} • {schedule.site}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">{schedule.shift}</p>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(schedule.status)}`}>
                          {schedule.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Substitutions Tab */}
          {activeTab === 'substitutions' && (
            <div className="text-center py-16">
              <AlertTriangle className="w-16 h-16 text-orange-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Módulo de Substituições
              </h3>
              <p className="text-gray-500">
                Gerenciamento de substituições e banco de horas em desenvolvimento...
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
