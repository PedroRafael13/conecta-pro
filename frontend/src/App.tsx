'use client';

import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider, PageLoader } from '@/design-system/components';
import { ThemeProvider } from '@/shared/contexts/ThemeContext';
import { AuthProvider } from '@/core/auth/AuthProvider';
import { OfflineBanner, InstallPrompt, UpdatePrompt, CapacitorInit } from '@/core/components/pwa';

// Lazy load pages - Auth
const LoginPage = lazy(() => import('@/features/auth/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/features/auth/RegisterPage').then(m => ({ default: m.RegisterPage })));
const ForgotPasswordPage = lazy(() => import('@/features/auth/ForgotPasswordPage').then(m => ({ default: m.ForgotPasswordPage })));
const AuthCallbackPage = lazy(() => import('@/features/auth/AuthCallbackPage').then(m => ({ default: m.AuthCallbackPage })));
const PendingApprovalPage = lazy(() => import('@/features/auth/PendingApprovalPage').then(m => ({ default: m.PendingApprovalPage })));

// Lazy load pages - Home Hub
const HomeHubPage = lazy(() => import('@/features/home/HomeHubPage').then(m => ({ default: m.HomeHubPage })));

// Lazy load pages - Profile & Help
const ProfilePage = lazy(() => import('@/pages/ProfilePage').then(m => ({ default: m.ProfilePage })));
const HelpPage = lazy(() => import('@/pages/HelpPage').then(m => ({ default: m.HelpPage })));

// Lazy load pages - Dashboard
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage').then(m => ({ default: m.DashboardPage })));
const AnalyticsPage = lazy(() => import('@/features/dashboard/AnalyticsPage').then(m => ({ default: m.AnalyticsPage })));

// Lazy load pages - CRM
const LeadsPage = lazy(() => import('@/features/crm/LeadsPage').then(m => ({ default: m.LeadsPage })));
const OpportunitiesPage = lazy(() => import('@/features/crm/OpportunitiesPage').then(m => ({ default: m.OpportunitiesPage })));
const ProposalsPage = lazy(() => import('@/features/crm/ProposalsPage').then(m => ({ default: m.ProposalsPage })));
const ContractsPage = lazy(() => import('@/features/crm/ContractsPage').then(m => ({ default: m.ContractsPage })));
const CommissionsPage = lazy(() => import('@/features/crm/CommissionsPage').then(m => ({ default: m.CommissionsPage })));

// Lazy load pages - Financial
const FinancialDashboardPage = lazy(() => import('@/features/financial/FinancialDashboardPage').then(m => ({ default: m.FinancialDashboardPage })));
const PayablesPage = lazy(() => import('@/features/financial/PayablesPage').then(m => ({ default: m.PayablesPage })));
const ReceivablesPage = lazy(() => import('@/features/financial/ReceivablesPage').then(m => ({ default: m.ReceivablesPage })));
const BankingPage = lazy(() => import('@/features/financial/BankingPage').then(m => ({ default: m.BankingPage })));
const CashflowPage = lazy(() => import('@/features/financial/CashflowPage').then(m => ({ default: m.CashflowPage })));
const InventoryPage = lazy(() => import('@/features/financial/InventoryPage').then(m => ({ default: m.InventoryPage })));
const ProcurementPage = lazy(() => import('@/features/financial/ProcurementPage').then(m => ({ default: m.ProcurementPage })));
const FiscalPage = lazy(() => import('@/features/financial/FiscalPage').then(m => ({ default: m.FiscalPage })));
const AccountingPage = lazy(() => import('@/features/financial/AccountingPage').then(m => ({ default: m.AccountingPage })));
const SuppliersPage = lazy(() => import('@/features/financial/SuppliersPage').then(m => ({ default: m.SuppliersPage })));
const BillingRulesPage = lazy(() => import('@/features/financial/BillingRulesPage').then(m => ({ default: m.BillingRulesPage })));
const BankReconciliationPage = lazy(() => import('@/features/financial/BankReconciliationPage').then(m => ({ default: m.BankReconciliationPage })));

// Lazy load pages - HR
const HRDashboardPage = lazy(() => import('@/features/hr/HRDashboardPage').then(m => ({ default: m.HRDashboardPage })));
const TimeTrackingPage = lazy(() => import('@/features/hr/TimeTrackingPage').then(m => ({ default: m.TimeTrackingPage })));
const EmployeesPage = lazy(() => import('@/features/hr/EmployeesPage').then(m => ({ default: m.EmployeesPage })));
const PayrollPage = lazy(() => import('@/features/hr/PayrollPage').then(m => ({ default: m.PayrollPage })));
const RecruitmentPage = lazy(() => import('@/features/hr/RecruitmentPage').then(m => ({ default: m.RecruitmentPage })));
const MobileTimeClockPage = lazy(() => import('@/features/hr/MobileTimeClockPage').then(m => ({ default: m.MobileTimeClockPage })));
const REPIntegrationPage = lazy(() => import('@/features/hr/REPIntegrationPage').then(m => ({ default: m.REPIntegrationPage })));

// Lazy load pages - Operations
const PostsPage = lazy(() => import('@/features/operations/PostsPage').then(m => ({ default: m.PostsPage })));
const ScalesPage = lazy(() => import('@/features/operations/ScalesPage').then(m => ({ default: m.ScalesPage })));
const AllocationsPage = lazy(() => import('@/features/operations/AllocationsPage').then(m => ({ default: m.AllocationsPage })));
const ShiftsPage = lazy(() => import('@/features/operations/ShiftsPage').then(m => ({ default: m.ShiftsPage })));
const SubstitutionsPage = lazy(() => import('@/features/operations/SubstitutionsPage').then(m => ({ default: m.SubstitutionsPage })));
const TimeBankPage = lazy(() => import('@/features/operations/TimeBankPage').then(m => ({ default: m.TimeBankPage })));
const DailyWorkersPage = lazy(() => import('@/features/operations/DailyWorkersPage').then(m => ({ default: m.DailyWorkersPage })));

// Lazy load pages - Integrations
const IntegrationsHubPage = lazy(() => import('@/features/integrations/IntegrationsHubPage').then(m => ({ default: m.IntegrationsHubPage })));
const OpenBankingPage = lazy(() => import('@/features/integrations/OpenBankingPage').then(m => ({ default: m.OpenBankingPage })));
const EmailIntegrationPage = lazy(() => import('@/features/integrations/EmailIntegrationPage').then(m => ({ default: m.EmailIntegrationPage })));
const WhatsAppIntegrationPage = lazy(() => import('@/features/integrations/WhatsAppIntegrationPage').then(m => ({ default: m.WhatsAppIntegrationPage })));

// Lazy load pages - AI
const AIHubPage = lazy(() => import('@/features/ai/AIHubPage').then(m => ({ default: m.AIHubPage })));
const AIAnalyticsPage = lazy(() => import('@/features/ai/AIAnalyticsPage').then(m => ({ default: m.AIAnalyticsPage })));
const AIPredictionsPage = lazy(() => import('@/features/ai/AIPredictionsPage').then(m => ({ default: m.AIPredictionsPage })));
const AIDocumentAnalysisPage = lazy(() => import('@/features/ai/AIDocumentAnalysisPage').then(m => ({ default: m.AIDocumentAnalysisPage })));
const AISentimentPage = lazy(() => import('@/features/ai/AISentimentPage').then(m => ({ default: m.AISentimentPage })));
const AIFraudDetectionPage = lazy(() => import('@/features/ai/AIFraudDetectionPage').then(m => ({ default: m.AIFraudDetectionPage })));

// Lazy load pages - GED
const GEDPage = lazy(() => import('@/features/ged/GEDPage').then(m => ({ default: m.GEDPage })));
const GEDSearchPage = lazy(() => import('@/pages/GEDSearchPage').then(m => ({ default: m.GEDSearchPage })));

// Lazy load pages - Compliance
const CompliancePage = lazy(() => import('@/features/compliance/CompliancePage').then(m => ({ default: m.CompliancePage })));
const GovernmentPage = lazy(() => import('@/features/compliance/GovernmentPage').then(m => ({ default: m.GovernmentPage })));
const LGPDPage = lazy(() => import('@/features/compliance/LGPDPage').then(m => ({ default: m.LGPDPage })));
const ESocialPage = lazy(() => import('@/features/compliance/ESocialPage').then(m => ({ default: m.ESocialPage })));
const SEFAZPage = lazy(() => import('@/features/compliance/SEFAZPage').then(m => ({ default: m.SEFAZPage })));
const ReceitaFederalPage = lazy(() => import('@/features/compliance/ReceitaFederalPage').then(m => ({ default: m.ReceitaFederalPage })));

// Lazy load pages - Extras
const DocumentKitsPage = lazy(() => import('@/features/extras/DocumentKitsPage').then(m => ({ default: m.DocumentKitsPage })));
const MonitoringPage = lazy(() => import('@/features/extras/MonitoringPage').then(m => ({ default: m.MonitoringPage })));
const RealtimeMonitoringPage = lazy(() => import('@/features/extras/RealtimeMonitoringPage').then(m => ({ default: m.RealtimeMonitoringPage })));
const SchedulerPage = lazy(() => import('@/features/extras/SchedulerPage').then(m => ({ default: m.SchedulerPage })));
const FieldInventoryPage = lazy(() => import('@/features/extras/FieldInventoryPage').then(m => ({ default: m.FieldInventoryPage })));

// Lazy load pages - Campo (Field Service)
const CampoDashboardPage = lazy(() => import('@/features/campo/CampoDashboardPage').then(m => ({ default: m.CampoDashboardPage })));
const ServiceOrdersPage = lazy(() => import('@/features/campo/ServiceOrdersPage').then(m => ({ default: m.ServiceOrdersPage })));
const VisitsPage = lazy(() => import('@/features/campo/VisitsPage').then(m => ({ default: m.VisitsPage })));
const ChecklistPage = lazy(() => import('@/features/campo/ChecklistPage').then(m => ({ default: m.ChecklistPage })));
const OccurrencesPage = lazy(() => import('@/features/campo/OccurrencesPage').then(m => ({ default: m.OccurrencesPage })));
const AccessLogPage = lazy(() => import('@/features/campo/AccessLogPage').then(m => ({ default: m.AccessLogPage })));
const EquipmentStatusPage = lazy(() => import('@/features/campo/EquipmentStatusPage').then(m => ({ default: m.EquipmentStatusPage })));
const RoutesPage = lazy(() => import('@/features/campo/RoutesPage').then(m => ({ default: m.RoutesPage })));

// Lazy load pages - Bidding (Licitações)
const BiddingDashboardPage = lazy(() => import('@/features/bidding/BiddingDashboardPage').then(m => ({ default: m.BiddingDashboardPage })));
const BiddingsPage = lazy(() => import('@/features/bidding/BiddingsPage').then(m => ({ default: m.BiddingsPage })));
const BidProposalsPage = lazy(() => import('@/features/bidding/BidProposalsPage').then(m => ({ default: m.BidProposalsPage })));
const BidDocumentsPage = lazy(() => import('@/features/bidding/BidDocumentsPage').then(m => ({ default: m.BidDocumentsPage })));

// Lazy load pages - Clients
const ClientsPage = lazy(() => import('@/features/clients/ClientsPage').then(m => ({ default: m.ClientsPage })));
const ClientDetailPage = lazy(() => import('@/features/clients/ClientDetailPage').then(m => ({ default: m.ClientDetailPage })));

// Lazy load pages - Admin
const UsersManagementPage = lazy(() => import('@/features/admin/UsersManagementPage').then(m => ({ default: m.UsersManagementPage })));

// Lazy load pages - Notifications, Settings, Reports
const NotificationsPage = lazy(() => import('@/features/notifications/NotificationsPage').then(m => ({ default: m.NotificationsPage })));
const SettingsPage = lazy(() => import('@/features/settings/SettingsPage').then(m => ({ default: m.SettingsPage })));
const ReportsPage = lazy(() => import('@/features/reports/ReportsPage').then(m => ({ default: m.ReportsPage })));

// Lazy load pages - Services
const ServicesPage = lazy(() => import('@/features/services/ServicesPage').then(m => ({ default: m.ServicesPage })));

// Lazy load pages - Health & Safety (Saúde Ocupacional)
const HealthSafetyDashboardPage = lazy(() => import('@/features/health-safety/HealthSafetyDashboardPage').then(m => ({ default: m.HealthSafetyDashboardPage })));
const PCMSOPage = lazy(() => import('@/features/health-safety/PCMSOPage').then(m => ({ default: m.PCMSOPage })));
const PPRAPage = lazy(() => import('@/features/health-safety/PPRAPage').then(m => ({ default: m.PPRAPage })));
const EPIPage = lazy(() => import('@/features/health-safety/EPIPage').then(m => ({ default: m.EPIPage })));

// Lazy load pages - Equipment Management (Patrimônio)
const EquipmentDashboardPage = lazy(() => import('@/features/equipment/EquipmentDashboardPage').then(m => ({ default: m.EquipmentDashboardPage })));
const EquipmentListPage = lazy(() => import('@/features/equipment/EquipmentListPage').then(m => ({ default: m.EquipmentListPage })));
const MaintenancePage = lazy(() => import('@/features/equipment/MaintenancePage').then(m => ({ default: m.MaintenancePage })));
const ComodatoPage = lazy(() => import('@/features/equipment/ComodatoPage').then(m => ({ default: m.ComodatoPage })));

// Lazy load pages - HR Portal (Portal do Colaborador)
const EmployeePortalPage = lazy(() => import('@/features/hr-portal/EmployeePortalPage').then(m => ({ default: m.EmployeePortalPage })));
const PortalPayslipsPage = lazy(() => import('@/features/hr-portal/PayslipsPage').then(m => ({ default: m.PayslipsPage })));
const VacationPage = lazy(() => import('@/features/hr-portal/VacationPage').then(m => ({ default: m.VacationPage })));
const EmployeeDocumentsPage = lazy(() => import('@/features/hr-portal/DocumentsPage').then(m => ({ default: m.DocumentsPage })));

// Lazy load pages - Automation (Workflows Engine)
const AutomationDashboardPage = lazy(() => import('@/features/automation/AutomationDashboardPage').then(m => ({ default: m.AutomationDashboardPage })));
const WorkflowBuilderPage = lazy(() => import('@/features/automation/WorkflowBuilderPage').then(m => ({ default: m.WorkflowBuilderPage })));

// Lazy load pages - Document Intelligence (OCR)
const DocIntelligencePage = lazy(() => import('@/features/doc-intelligence/DocIntelligencePage').then(m => ({ default: m.DocIntelligencePage })));

// Placeholder pages (remaining pages to be implemented)
const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="min-h-screen bg-bg-primary flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-2xl font-display font-bold text-text-primary mb-2">{title}</h1>
      <p className="text-text-secondary">Página em desenvolvimento</p>
    </div>
  </div>
);

// Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <ToastProvider position="top-right">
          <AuthProvider>
            <CapacitorInit />
            <OfflineBanner />
            <UpdatePrompt />
            <InstallPrompt />
            <BrowserRouter>
              <Suspense fallback={<PageLoader />}>
                <Routes>
              {/* Auth Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/auth/callback" element={<AuthCallbackPage />} />
              <Route path="/pending-approval" element={<PendingApprovalPage />} />

              {/* Home Hub */}
              <Route path="/home" element={<HomeHubPage />} />
              <Route path="/" element={<Navigate to="/home" replace />} />

              {/* Dashboard */}
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/realtime" element={<RealtimeMonitoringPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />

              {/* CRM */}
              <Route path="/crm" element={<Navigate to="/crm/leads" replace />} />
              <Route path="/crm/leads" element={<LeadsPage />} />
              <Route path="/crm/opportunities" element={<OpportunitiesPage />} />
              <Route path="/crm/proposals" element={<ProposalsPage />} />
              <Route path="/crm/contracts" element={<ContractsPage />} />
              <Route path="/crm/commissions" element={<CommissionsPage />} />

              {/* Financial */}
              <Route path="/financial" element={<FinancialDashboardPage />} />
              <Route path="/financial/payables" element={<PayablesPage />} />
              <Route path="/financial/receivables" element={<ReceivablesPage />} />
              <Route path="/financial/banking" element={<BankingPage />} />
              <Route path="/financial/cashflow" element={<CashflowPage />} />
              <Route path="/financial/inventory" element={<InventoryPage />} />
              <Route path="/financial/procurement" element={<ProcurementPage />} />
              <Route path="/financial/fiscal" element={<FiscalPage />} />
              <Route path="/financial/accounting" element={<AccountingPage />} />
              <Route path="/financial/suppliers" element={<SuppliersPage />} />
              <Route path="/financial/billing-rules" element={<BillingRulesPage />} />
              <Route path="/financial/reconciliation" element={<BankReconciliationPage />} />

              {/* HR */}
              <Route path="/hr" element={<HRDashboardPage />} />
              <Route path="/hr/employees" element={<EmployeesPage />} />
              <Route path="/hr/payroll" element={<PayrollPage />} />
              <Route path="/hr/time-tracking" element={<TimeTrackingPage />} />
              <Route path="/hr/recruitment" element={<RecruitmentPage />} />
              <Route path="/hr/mobile-clock" element={<MobileTimeClockPage />} />
              <Route path="/hr/rep" element={<REPIntegrationPage />} />

              {/* Operations */}
              <Route path="/operations" element={<Navigate to="/operations/posts" replace />} />
              <Route path="/operations/posts" element={<PostsPage />} />
              <Route path="/operations/scales" element={<ScalesPage />} />
              <Route path="/operations/allocations" element={<AllocationsPage />} />
              <Route path="/operations/shifts" element={<ShiftsPage />} />
              <Route path="/operations/substitutions" element={<SubstitutionsPage />} />
              <Route path="/operations/time-bank" element={<TimeBankPage />} />
              <Route path="/operations/daily-workers" element={<DailyWorkersPage />} />

              {/* Field Service (Campo) */}
              <Route path="/field-service" element={<CampoDashboardPage />} />
              <Route path="/field-service/orders" element={<ServiceOrdersPage />} />
              <Route path="/field-service/visits" element={<VisitsPage />} />
              <Route path="/field-service/checklists" element={<ChecklistPage />} />
              <Route path="/field-service/occurrences" element={<OccurrencesPage />} />
              <Route path="/field-service/access-log" element={<AccessLogPage />} />
              <Route path="/field-service/equipment" element={<EquipmentStatusPage />} />
              <Route path="/field-service/routes" element={<RoutesPage />} />

              {/* Integrations */}
              <Route path="/integrations" element={<IntegrationsHubPage />} />
              <Route path="/integrations/banking" element={<OpenBankingPage />} />
              <Route path="/integrations/email" element={<EmailIntegrationPage />} />
              <Route path="/integrations/whatsapp" element={<WhatsAppIntegrationPage />} />

              {/* AI */}
              <Route path="/ai" element={<AIHubPage />} />
              <Route path="/ai/bartolo" element={<AIHubPage />} />
              <Route path="/ai/analytics" element={<AIAnalyticsPage />} />
              <Route path="/ai/predictions" element={<AIPredictionsPage />} />
              <Route path="/ai/documents" element={<AIDocumentAnalysisPage />} />
              <Route path="/ai/sentiment" element={<AISentimentPage />} />
              <Route path="/ai/fraud" element={<AIFraudDetectionPage />} />

              {/* GED */}
              <Route path="/ged" element={<GEDPage />} />
              <Route path="/ged/folders" element={<GEDPage />} />
              <Route path="/ged/search" element={<GEDSearchPage />} />

              {/* Compliance */}
              <Route path="/compliance" element={<CompliancePage />} />
              <Route path="/compliance/audit" element={<CompliancePage />} />
              <Route path="/compliance/lgpd" element={<LGPDPage />} />
              <Route path="/compliance/government" element={<GovernmentPage />} />
              <Route path="/compliance/esocial" element={<ESocialPage />} />
              <Route path="/compliance/sefaz" element={<SEFAZPage />} />
              <Route path="/compliance/receita" element={<ReceitaFederalPage />} />

              {/* Extras */}
              <Route path="/extras/document-kits" element={<DocumentKitsPage />} />
              <Route path="/extras/monitoring" element={<MonitoringPage />} />
              <Route path="/extras/scheduler" element={<SchedulerPage />} />
              <Route path="/field-service/inventory" element={<FieldInventoryPage />} />

              {/* Bidding (Licitações) */}
              <Route path="/bidding" element={<BiddingDashboardPage />} />
              <Route path="/bidding/list" element={<BiddingsPage />} />
              <Route path="/bidding/proposals" element={<BidProposalsPage />} />
              <Route path="/bidding/documents" element={<BidDocumentsPage />} />

              {/* Clients */}
              <Route path="/clients" element={<ClientsPage />} />
              <Route path="/clients/:id" element={<ClientDetailPage />} />

              {/* Settings & Admin */}
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/settings/users" element={<UsersManagementPage />} />
              <Route path="/admin/users" element={<UsersManagementPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/help" element={<HelpPage />} />

              {/* Services */}
              <Route path="/services" element={<ServicesPage />} />

              {/* Health & Safety (Saúde Ocupacional) */}
              <Route path="/health-safety" element={<HealthSafetyDashboardPage />} />
              <Route path="/health-safety/pcmso" element={<PCMSOPage />} />
              <Route path="/health-safety/ppra" element={<PPRAPage />} />
              <Route path="/health-safety/epi" element={<EPIPage />} />

              {/* Equipment Management (Patrimônio) */}
              <Route path="/equipment" element={<EquipmentDashboardPage />} />
              <Route path="/equipment/list" element={<EquipmentListPage />} />
              <Route path="/equipment/maintenance" element={<MaintenancePage />} />
              <Route path="/equipment/comodato" element={<ComodatoPage />} />

              {/* HR Portal (Portal do Colaborador) */}
              <Route path="/hr-portal" element={<EmployeePortalPage />} />
              <Route path="/hr-portal/payslips" element={<PortalPayslipsPage />} />
              <Route path="/hr-portal/vacation" element={<VacationPage />} />
              <Route path="/hr-portal/documents" element={<EmployeeDocumentsPage />} />

              {/* Automation (Workflows Engine) */}
              <Route path="/automation" element={<AutomationDashboardPage />} />
              <Route path="/automation/builder" element={<WorkflowBuilderPage />} />
              <Route path="/automation/builder/:id" element={<WorkflowBuilderPage />} />

              {/* Document Intelligence (OCR) */}
              <Route path="/doc-intelligence" element={<DocIntelligencePage />} />

              {/* Catch all */}
              <Route path="*" element={<Navigate to="/home" replace />} />
                </Routes>
              </Suspense>
            </BrowserRouter>
          </AuthProvider>
        </ToastProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
