// @ts-nocheck
/**
 * EXEMPLOS DE USO - Módulo HR API
 *
 * Demonstra como usar os hooks gerados do módulo HR
 */

'use client';

import { 
  // Analytics
  useListDashboardsApiV1HrAnalyticsDashboardsDashboardsGet,
  useGetKpiApiV1HrAnalyticsKpisKpisKpiCodeGet,
  useExportReportApiV1HrAnalyticsReportsReportsReportIdExportGet,
  
  // Portal
  useListPayslipsApiV1HrPortalPortalPayslipsGet,
  useListVacationRequestsApiV1HrPortalPortalVacationRequestsGet,
  useMarkAsReadApiV1HrPortalPortalNotificationsNotificationIdReadPost,
  
  // Time Tracking
  useListTimeSheetsApiV1HrTimeTrackingTimeTrackingTimesheetsGet,
  useCreateOvertimeApiV1HrTimeTrackingTimeTrackingOvertimePost,
  useListJustificationsApiV1HrTimeTrackingTimeTrackingJustificationsGet,
  
  // Mobile
  useCheckInApiV1HrMobileCheckinCheckInPost,
  useListGeofencesApiV1HrMobileGeofenceGeofencesGet,
  
  // Payroll
  useExportPayrollDataApiV1HrPayrollExportExportPost,
  useListPayrollPeriodsApiV1HrPayrollPeriodsPeriodsGet,
  
  // REP
  useSyncDevicesApiV1HrRepSyncDevicesSyncPost,
  useExportAfdApiV1HrRepAfdExportPost,
  
  // Types
  type DashboardConfigResponse,
  type TimeSheetResponse,
  type PayslipResponse,
  type CheckInRequest,
  type OvertimeCreate,
  type JustificationResponse,
} from '@/api/hr';

/**
 * Exemplo: Dashboard Analytics
 */
export function HRAnalyticsDashboard() {
  const { data: dashboards, isLoading } = useListDashboardsApiV1HrAnalyticsDashboardsDashboardsGet({
    skip: 0,
    limit: 10,
    dashboard_type: 'general'
  });

  if (isLoading) return <div>Carregando dashboards...</div>;

  return (
    <div>
      <h2>Dashboards HR</h2>
      {dashboards?.items.map((dashboard: DashboardConfigResponse) => (
        <div key={dashboard.id}>
          <h3>{dashboard.name}</h3>
          <p>{dashboard.description}</p>
          <span>Widgets: {dashboard.widget_count}</span>
        </div>
      ))}
    </div>
  );
}
