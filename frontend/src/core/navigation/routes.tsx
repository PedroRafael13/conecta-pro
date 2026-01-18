import { createBrowserRouter, Navigate } from 'react-router-dom';
import { MainLayout } from '@core/layout';
import { LoginPage, ProtectedRoute } from '@core/auth';

// Lazy load pages
import { lazy, Suspense } from 'react';

// Dashboard & Analytics
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const AnalyticsPage = lazy(() => import('@/pages/AnalyticsPage'));
const RealtimePage = lazy(() => import('@/pages/RealtimePage'));
const ReportsPage = lazy(() => import('@/pages/ReportsPage'));

// Compliance
const AuditPage = lazy(() => import('@/pages/AuditPage'));
const LGPDPage = lazy(() => import('@/pages/LGPDPage'));
const GovernmentPage = lazy(() => import('@/pages/GovernmentPage'));
const BiddingPage = lazy(() => import('@/pages/BiddingPage'));
const CCTCompliancePage = lazy(() => import('@/pages/CCTCompliancePage'));

// Government Integrations
const CTePage = lazy(() => import('@/features/compliance/CTePage'));
const MDFePage = lazy(() => import('@/features/compliance/MDFePage'));
const SPEDFiscalPage = lazy(() => import('@/features/compliance/SPEDFiscalPage'));
const SPEDContabilPage = lazy(() => import('@/features/compliance/SPEDContabilPage'));
const NFCePage = lazy(() => import('@/features/compliance/NFCePage'));
const NFSeNacionalPage = lazy(() => import('@/features/compliance/NFSeNacionalPage'));
const FGTSDigitalPage = lazy(() => import('@/features/compliance/FGTSDigitalPage'));
const SimplesNacionalPage = lazy(() => import('@/features/compliance/SimplesNacionalPage'));

// GED
const GEDPage = lazy(() => import('@/pages/GEDPage'));
const GEDClassificationPage = lazy(() => import('@/pages/GEDClassificationPage'));
const GEDSearchPage = lazy(() => import('@/pages/GEDSearchPage'));

// CRM
const CRMPage = lazy(() => import('@/pages/CRMPage'));
const CRMPipelinePage = lazy(() => import('@/pages/CRMPipelinePage'));
const CRMDashboardPage = lazy(() => import('@/pages/CRMDashboardPage'));
const ProposalsPage = lazy(() => import('@/pages/ProposalsPage'));
const MarketplacePage = lazy(() => import('@/pages/MarketplacePage'));

// Operations
const OperationsPage = lazy(() => import('@/pages/OperationsPage'));
const FieldServicePage = lazy(() => import('@/pages/FieldServicePage'));
const SchedulingPage = lazy(() => import('@/pages/SchedulingPage'));
const FacilitiesPage = lazy(() => import('@/pages/FacilitiesPage'));
const EquipmentPage = lazy(() => import('@/pages/EquipmentPage'));
const InstallationPage = lazy(() => import('@/pages/InstallationPage'));

// Finance
const FinancePage = lazy(() => import('@/pages/FinancePage'));

// HR
const HRPage = lazy(() => import('@/pages/HRPage'));

// Settings & Profile
const SettingsPage = lazy(() => import('@/pages/SettingsPage'));
const ProfilePage = lazy(() => import('@/pages/ProfilePage'));
const TenantsPage = lazy(() => import('@/pages/TenantsPage'));
const FeatureFlagsPage = lazy(() => import('@/pages/FeatureFlagsPage'));
const ConfigTemplatesPage = lazy(() => import('@/pages/ConfigTemplatesPage'));

// Clients
const UnitsResidentsPage = lazy(() => import('@/pages/UnitsResidentsPage'));

// Notifications
const IntelligentNotificationsPage = lazy(() => import('@/pages/IntelligentNotificationsPage'));

// Integrations
const IntegrationsHubPage = lazy(() => import('@/features/integrations').then(m => ({ default: m.IntegrationsHubPage })));
const SolidesIntegrationPage = lazy(() => import('@/features/integrations').then(m => ({ default: m.SolidesIntegrationPage })));

// Error
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));

// Loading component for lazy loaded pages
// eslint-disable-next-line react-refresh/only-export-components
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-conecta-escuro" />
    </div>
  );
}

// Wrapper for lazy loaded components
// eslint-disable-next-line react-refresh/only-export-components
function LazyPage({ component: Component }: { component: React.ComponentType }) {
  return (
    <Suspense fallback={<PageLoader />}>
      <Component />
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <MainLayout />,
        children: [
          {
            path: '/',
            element: <Navigate to="/dashboard" replace />,
          },
          // Dashboard & Analytics
          {
            path: '/dashboard',
            element: <LazyPage component={DashboardPage} />,
          },
          {
            path: '/reports',
            element: <LazyPage component={ReportsPage} />,
          },
          {
            path: '/analytics',
            element: <LazyPage component={AnalyticsPage} />,
          },
          {
            path: '/realtime',
            element: <LazyPage component={RealtimePage} />,
          },
          // Compliance
          {
            path: '/audit',
            element: <LazyPage component={AuditPage} />,
          },
          {
            path: '/lgpd',
            element: <LazyPage component={LGPDPage} />,
          },
          {
            path: '/government',
            element: <LazyPage component={GovernmentPage} />,
          },
          {
            path: '/bidding',
            element: <LazyPage component={BiddingPage} />,
          },
          {
            path: '/compliance/cct',
            element: <LazyPage component={CCTCompliancePage} />,
          },
          // Government Integrations - Fiscal
          {
            path: '/fiscal/cte',
            element: <LazyPage component={CTePage} />,
          },
          {
            path: '/fiscal/mdfe',
            element: <LazyPage component={MDFePage} />,
          },
          {
            path: '/fiscal/nfce',
            element: <LazyPage component={NFCePage} />,
          },
          {
            path: '/fiscal/nfse',
            element: <LazyPage component={NFSeNacionalPage} />,
          },
          // SPED
          {
            path: '/sped/fiscal',
            element: <LazyPage component={SPEDFiscalPage} />,
          },
          {
            path: '/sped/contabil',
            element: <LazyPage component={SPEDContabilPage} />,
          },
          // Trabalhista
          {
            path: '/trabalhista/fgts',
            element: <LazyPage component={FGTSDigitalPage} />,
          },
          // Simples Nacional
          {
            path: '/fiscal/simples',
            element: <LazyPage component={SimplesNacionalPage} />,
          },
          // GED
          {
            path: '/ged',
            element: <LazyPage component={GEDPage} />,
          },
          {
            path: '/ged/classification',
            element: <LazyPage component={GEDClassificationPage} />,
          },
          {
            path: '/ged/search',
            element: <LazyPage component={GEDSearchPage} />,
          },
          // CRM
          {
            path: '/crm',
            element: <LazyPage component={CRMPage} />,
          },
          {
            path: '/crm/pipeline',
            element: <LazyPage component={CRMPipelinePage} />,
          },
          {
            path: '/crm/dashboard',
            element: <LazyPage component={CRMDashboardPage} />,
          },
          {
            path: '/proposals',
            element: <LazyPage component={ProposalsPage} />,
          },
          {
            path: '/marketplace',
            element: <LazyPage component={MarketplacePage} />,
          },
          // Operations
          {
            path: '/operations',
            element: <LazyPage component={OperationsPage} />,
          },
          {
            path: '/field-service',
            element: <LazyPage component={FieldServicePage} />,
          },
          {
            path: '/scheduling',
            element: <LazyPage component={SchedulingPage} />,
          },
          {
            path: '/facilities',
            element: <LazyPage component={FacilitiesPage} />,
          },
          {
            path: '/equipment',
            element: <LazyPage component={EquipmentPage} />,
          },
          {
            path: '/equipment/installations',
            element: <LazyPage component={InstallationPage} />,
          },
          // Finance
          {
            path: '/finance/cfo',
            element: <LazyPage component={FinancePage} />,
          },
          {
            path: '/finance/cashflow',
            element: <LazyPage component={FinancePage} />,
          },
          {
            path: '/finance/forecasts',
            element: <LazyPage component={FinancePage} />,
          },
          // HR
          {
            path: '/hr',
            element: <LazyPage component={HRPage} />,
          },
          {
            path: '/hr/recruitment',
            element: <LazyPage component={HRPage} />,
          },
          {
            path: '/hr/health',
            element: <LazyPage component={HRPage} />,
          },
          // Settings & Profile
          {
            path: '/settings',
            element: <LazyPage component={SettingsPage} />,
          },
          {
            path: '/settings/tenants',
            element: <LazyPage component={TenantsPage} />,
          },
          {
            path: '/settings/feature-flags',
            element: <LazyPage component={FeatureFlagsPage} />,
          },
          {
            path: '/settings/config-templates',
            element: <LazyPage component={ConfigTemplatesPage} />,
          },
          {
            path: '/profile',
            element: <LazyPage component={ProfilePage} />,
          },
          // Clients
          {
            path: '/clients/units-residents',
            element: <LazyPage component={UnitsResidentsPage} />,
          },
          // Notifications
          {
            path: '/notifications/intelligent',
            element: <LazyPage component={IntelligentNotificationsPage} />,
          },
          // Integrations
          {
            path: '/integrations',
            element: <LazyPage component={IntegrationsHubPage} />,
          },
          {
            path: '/integrations/solides',
            element: <LazyPage component={SolidesIntegrationPage} />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <LazyPage component={NotFoundPage} />,
  },
]);

export default router;
