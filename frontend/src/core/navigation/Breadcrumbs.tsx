import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  reports: 'Relatorios',
  analytics: 'Analytics',
  audit: 'Auditoria',
  lgpd: 'LGPD',
  government: 'Integracoes Gov',
  bidding: 'Licitacoes',
  ged: 'GED',
  classification: 'Classificacao',
  search: 'Busca',
  crm: 'CRM',
  pipeline: 'Pipeline',
  proposals: 'Propostas',
  marketplace: 'Marketplace',
  operations: 'Operacoes',
  'field-service': 'Servico de Campo',
  scheduling: 'Agendamento',
  facilities: 'Facilities',
  equipment: 'Equipamentos',
  finance: 'Financeiro',
  cfo: 'CFO Virtual',
  cashflow: 'Fluxo de Caixa',
  forecasts: 'Previsoes',
  hr: 'RH',
  recruitment: 'Recrutamento',
  health: 'Saude',
  settings: 'Configuracoes',
  profile: 'Perfil',
};

export function Breadcrumbs() {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  if (pathnames.length === 0) {
    return null;
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center text-sm">
      <Link
        to="/dashboard"
        className="text-gray-400 hover:text-white transition-colors"
      >
        <Home className="w-4 h-4" />
      </Link>

      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;
        const label = routeLabels[value] || value;

        return (
          <div key={to} className="flex items-center">
            <ChevronRight className="w-4 h-4 mx-2 text-gray-500" />
            {isLast ? (
              <span className="text-white font-medium">{label}</span>
            ) : (
              <Link
                to={to}
                className="text-gray-400 hover:text-white transition-colors"
              >
                {label}
              </Link>
            )}
          </div>
        );
      })}
    </nav>
  );
}

export default Breadcrumbs;
