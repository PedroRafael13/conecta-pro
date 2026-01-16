import React, { useState } from 'react';
import { 
  Thermometer, 
  Droplets, 
  Zap, 
  Wifi,
  QrCode,
  Wrench,
  AlertTriangle,
  
  TrendingUp,
  Calendar
} from 'lucide-react';

interface IoTSensor {
  id: string;
  name: string;
  type: 'temperature' | 'humidity' | 'energy' | 'occupancy';
  location: string;
  value: number;
  unit: string;
  status: 'online' | 'offline' | 'warning';
  lastUpdate: string;
  threshold: {
    min: number;
    max: number;
  };
}

interface Equipment {
  id: string;
  name: string;
  category: string;
  rfidTag: string;
  qrCode: string;
  status: 'operational' | 'maintenance' | 'out-of-order';
  location: string;
  lastMaintenance: string;
  nextMaintenance: string;
  warrantyEnd: string;
}

interface MaintenanceTask {
  id: string;
  equipmentId: string;
  equipment: Equipment;
  type: 'preventive' | 'corrective' | 'predictive';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'scheduled' | 'in-progress' | 'completed' | 'overdue';
  scheduledDate: string;
  description: string;
  assignedTo?: string;
}

export const FacilitiesDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'iot' | 'equipment' | 'maintenance'>('iot');

  // Mock IoT sensors data
  const [sensors] = useState<IoTSensor[]>([
    {
      id: 'TEMP-001',
      name: 'Sala de Servidores - Temperatura',
      type: 'temperature',
      location: 'Prédio A - 2º Andar',
      value: 18.5,
      unit: '°C',
      status: 'online',
      lastUpdate: '2024-01-12T14:30:00Z',
      threshold: { min: 18, max: 24 }
    },
    {
      id: 'HUM-001',
      name: 'Sala de Servidores - Umidade',
      type: 'humidity',
      location: 'Prédio A - 2º Andar',
      value: 65,
      unit: '%',
      status: 'warning',
      lastUpdate: '2024-01-12T14:30:00Z',
      threshold: { min: 40, max: 60 }
    },
    {
      id: 'POW-001',
      name: 'Consumo Elétrico - Total',
      type: 'energy',
      location: 'Medidor Principal',
      value: 125.6,
      unit: 'kW',
      status: 'online',
      lastUpdate: '2024-01-12T14:30:00Z',
      threshold: { min: 0, max: 200 }
    }
  ]);

  // Mock equipment data
  const [equipment] = useState<Equipment[]>([
    {
      id: 'AC-001',
      name: 'Ar Condicionado Central',
      category: 'HVAC',
      rfidTag: 'RFID-AC-001',
      qrCode: 'QR-AC-001',
      status: 'operational',
      location: 'Prédio A - Térreo',
      lastMaintenance: '2024-01-01',
      nextMaintenance: '2024-04-01',
      warrantyEnd: '2025-12-31'
    },
    {
      id: 'GEN-001',
      name: 'Gerador Diesel',
      category: 'Energia',
      rfidTag: 'RFID-GEN-001',
      qrCode: 'QR-GEN-001',
      status: 'maintenance',
      location: 'Subsolo',
      lastMaintenance: '2024-01-10',
      nextMaintenance: '2024-01-15',
      warrantyEnd: '2026-06-30'
    }
  ]);

  // Mock maintenance tasks
  const [maintenanceTasks] = useState<MaintenanceTask[]>([
    {
      id: 'MAINT-001',
      equipmentId: 'AC-001',
      equipment: equipment[0],
      type: 'preventive',
      priority: 'medium',
      status: 'scheduled',
      scheduledDate: '2024-04-01',
      description: 'Limpeza de filtros e verificação do sistema',
      assignedTo: 'João Técnico'
    },
    {
      id: 'MAINT-002',
      equipmentId: 'GEN-001',
      equipment: equipment[1],
      type: 'corrective',
      priority: 'urgent',
      status: 'in-progress',
      scheduledDate: '2024-01-12',
      description: 'Reparo no sistema de combustível',
      assignedTo: 'Maria Técnica'
    }
  ]);

  const getSensorStatusColor = (status: IoTSensor['status']) => {
    switch (status) {
      case 'online':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'offline':
        return 'text-red-500';
    }
  };

  const getSensorIcon = (type: IoTSensor['type']) => {
    switch (type) {
      case 'temperature':
        return <Thermometer className="w-6 h-6" />;
      case 'humidity':
        return <Droplets className="w-6 h-6" />;
      case 'energy':
        return <Zap className="w-6 h-6" />;
      case 'occupancy':
        return <Wifi className="w-6 h-6" />;
    }
  };

  const getEquipmentStatusColor = (status: Equipment['status']) => {
    switch (status) {
      case 'operational':
        return 'bg-green-100 text-green-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'out-of-order':
        return 'bg-red-100 text-red-800';
    }
  };

  const getMaintenanceStatusColor = (status: MaintenanceTask['status']) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'in-progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
    }
  };

  const isValueInRange = (value: number, threshold: { min: number; max: number }) => {
    return value >= threshold.min && value <= threshold.max;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <Thermometer className="w-8 h-8 mr-3 text-blue-600" />
                Facilities IoT + Equipment
              </h1>
              <p className="text-gray-600 mt-1">
                Monitoramento IoT, RFID tracking e manutenção preditiva
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sensores Online</p>
                <p className="text-3xl font-bold text-gray-900">
                  {sensors.filter(s => s.status === 'online').length}/{sensors.length}
                </p>
              </div>
              <Wifi className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Equipamentos</p>
                <p className="text-3xl font-bold text-gray-900">{equipment.length}</p>
                <p className="text-xs text-green-600">
                  {equipment.filter(e => e.status === 'operational').length} operacionais
                </p>
              </div>
              <QrCode className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Manutenções</p>
                <p className="text-3xl font-bold text-gray-900">{maintenanceTasks.length}</p>
                <p className="text-xs text-yellow-600">
                  {maintenanceTasks.filter(m => m.status === 'in-progress').length} em andamento
                </p>
              </div>
              <Wrench className="w-8 h-8 text-orange-600" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Eficiência</p>
                <p className="text-3xl font-bold text-gray-900">97.2%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'iot', label: 'Sensores IoT', count: sensors.length },
                { id: 'equipment', label: 'Equipamentos', count: equipment.length },
                { id: 'maintenance', label: 'Manutenção', count: maintenanceTasks.length },
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
          
          {/* IoT Sensors */}
          {activeTab === 'iot' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Sensores IoT em Tempo Real</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {sensors.map((sensor) => (
                  <div key={sensor.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`flex items-center space-x-2 ${getSensorStatusColor(sensor.status)}`}>
                        {getSensorIcon(sensor.type)}
                        <span className="font-medium">{sensor.name}</span>
                      </div>
                      <span className={`w-3 h-3 rounded-full ${
                        sensor.status === 'online' ? 'bg-green-500' :
                        sensor.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                      }`} />
                    </div>
                    
                    <div className="text-center mb-4">
                      <div className={`text-4xl font-bold ${
                        isValueInRange(sensor.value, sensor.threshold) ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {sensor.value}
                      </div>
                      <div className="text-lg text-gray-600">{sensor.unit}</div>
                    </div>
                    
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>Localização:</span>
                        <span>{sensor.location}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Range:</span>
                        <span>{sensor.threshold.min} - {sensor.threshold.max} {sensor.unit}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Atualizado:</span>
                        <span>{new Date(sensor.lastUpdate).toLocaleTimeString('pt-BR')}</span>
                      </div>
                    </div>
                    
                    {!isValueInRange(sensor.value, sensor.threshold) && (
                      <div className="mt-3 flex items-center text-sm text-red-600">
                        <AlertTriangle className="w-4 h-4 mr-1" />
                        <span>Valor fora do range!</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Equipment */}
          {activeTab === 'equipment' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Equipamentos RFID</h2>
              <div className="space-y-4">
                {equipment.map((item) => (
                  <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">{item.name}</h3>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getEquipmentStatusColor(item.status)}`}>
                            {item.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">{item.category} • {item.location}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">RFID:</p>
                        <p className="font-medium">{item.rfidTag}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">QR Code:</p>
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{item.qrCode}</span>
                          <QrCode className="w-4 h-4 text-gray-400" />
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-500">Última Manutenção:</p>
                        <p className="font-medium">{new Date(item.lastMaintenance).toLocaleDateString('pt-BR')}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Próxima Manutenção:</p>
                        <p className="font-medium">{new Date(item.nextMaintenance).toLocaleDateString('pt-BR')}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Maintenance */}
          {activeTab === 'maintenance' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Manutenção Preditiva</h2>
              <div className="space-y-4">
                {maintenanceTasks.map((task) => (
                  <div key={task.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">{task.id}</h3>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getMaintenanceStatusColor(task.status)}`}>
                            {task.status}
                          </span>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            task.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                            task.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                            task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {task.priority}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-1">
                          {task.equipment.name} • {task.equipment.location}
                        </p>
                        <p className="text-sm text-gray-700">{task.description}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center">
                          <Calendar className="w-4 h-4 mr-1" />
                          <span>Agendado: {new Date(task.scheduledDate).toLocaleDateString('pt-BR')}</span>
                        </div>
                        <div className="flex items-center">
                          <Wrench className="w-4 h-4 mr-1" />
                          <span>Tipo: {task.type}</span>
                        </div>
                      </div>
                      
                      {task.assignedTo && (
                        <div className="text-right">
                          <p className="font-medium text-gray-900">{task.assignedTo}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
