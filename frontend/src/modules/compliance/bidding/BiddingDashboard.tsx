import {
  Star,
  TrendingUp,
  Award,
} from 'lucide-react';
import { StatCard } from '@modules/dashboards/widgets';

export const BiddingDashboard = () => {
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Licitações PNCP
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Oportunidades"
            value="156"
            icon={Award}
            variant="primary"
            trend={{ value: 12, direction: 'up' }}
          />

          <StatCard
            title="Score Medio IA"
            value="78%"
            icon={Star}
            variant="warning"
            trend={{ value: 5, direction: 'up' }}
          />

          <StatCard
            title="Propostas Enviadas"
            value="23"
            icon={TrendingUp}
            variant="success"
            trend={{ value: 8, direction: 'up' }}
          />

          <StatCard
            title="Taxa Sucesso"
            value="24%"
            icon={Award}
            variant="primary"
            trend={{ value: 3, direction: 'up' }}
          />
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Módulo em Desenvolvimento</h2>
          <p className="text-gray-600">
            Integração completa com PNCP em implementação...
          </p>
        </div>
      </div>
    </div>
  );
};
