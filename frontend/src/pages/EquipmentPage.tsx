import React, { useState } from 'react';
import {
  Package,
  Plus,
  Search,
  Grid3X3,
  List,
  QrCode,
  Radio,
  Wrench,
  AlertTriangle,
} from 'lucide-react';
import { EquipmentCard, QRScanner, useEquipment } from '@/modules/facilities/equipment';

type ViewMode = 'grid' | 'list';
type FilterStatus = 'all' | 'active' | 'maintenance' | 'inactive';

export function EquipmentPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showQRScanner, setShowQRScanner] = useState(false);

  const { equipments: equipment, isLoading: loading, stats } = useEquipment();

  const statsData = {
    total: stats?.total ?? 456,
    active: stats?.operacionais ?? 389,
    maintenance: stats?.em_manutencao ?? 42,
    inactive: stats?.inativos ?? 25,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Package className="h-7 w-7 text-conecta-escuro" />
            Gestao de Equipamentos
          </h1>
          <p className="text-gray-600 mt-1">
            Controle de patrimonio com QR Code e RFID
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowQRScanner(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <QrCode className="h-4 w-4" />
            Escanear QR
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
            <Plus className="h-4 w-4" />
            Novo Equipamento
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-xl font-bold text-gray-900">{statsData.total}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Radio className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Ativos</p>
              <p className="text-xl font-bold text-gray-900">{statsData.active}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Wrench className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Em Manutencao</p>
              <p className="text-xl font-bold text-gray-900">{statsData.maintenance}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Inativos</p>
              <p className="text-xl font-bold text-gray-900">{statsData.inactive}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex-1 min-w-64 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar equipamento por nome, codigo ou RFID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro"
          />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'all'
                ? 'bg-conecta-escuro text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Todos
          </button>
          <button
            onClick={() => setFilterStatus('active')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'active'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Ativos
          </button>
          <button
            onClick={() => setFilterStatus('maintenance')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'maintenance'
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Manutencao
          </button>
          <button
            onClick={() => setFilterStatus('inactive')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'inactive'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Inativos
          </button>
        </div>
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1.5 rounded-md transition-colors ${
              viewMode === 'grid'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Grid3X3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-1.5 rounded-md transition-colors ${
              viewMode === 'list'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Equipment Grid */}
      <div className={`grid gap-4 ${
        viewMode === 'grid'
          ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
          : 'grid-cols-1'
      }`}>
        {loading ? (
          <div className="col-span-full flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-conecta-escuro" />
          </div>
        ) : equipment && equipment.length > 0 ? (
          equipment.map((item) => (
            <EquipmentCard
              key={item.id}
              equipment={item}
              onView={() => console.log('View equipment:', item.id)}
            />
          ))
        ) : (
          <div className="col-span-full text-center py-12 bg-white rounded-lg border border-gray-200">
            <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum equipamento encontrado
            </h3>
            <p className="text-gray-600 mb-4">
              Comece cadastrando seu primeiro equipamento
            </p>
            <button className="inline-flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
              <Plus className="h-4 w-4" />
              Novo Equipamento
            </button>
          </div>
        )}
      </div>

      {/* QR Scanner Modal */}
      {showQRScanner && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Escanear QR Code</h2>
              <button
                onClick={() => setShowQRScanner(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                &times;
              </button>
            </div>
            <QRScanner
              onScan={(code) => {
                console.log('Scanned:', code);
                setShowQRScanner(false);
              }}
              onClose={() => setShowQRScanner(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default EquipmentPage;
