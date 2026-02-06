/**
 * React Query Hooks - HR Employee Portal
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { employeePortalService } from '@/services/hr';
import { customInstance } from '@/lib/api-client';

// Query Keys
export const portalKeys = {
  all: ['hr', 'portal'] as const,
  payslips: () => [...portalKeys.all, 'payslips'] as const,
  payslip: (id: string) => [...portalKeys.payslips(), id] as const,
  vacations: () => [...portalKeys.all, 'vacations'] as const,
  vacation: (id: string) => [...portalKeys.vacations(), id] as const,
  documents: () => [...portalKeys.all, 'documents'] as const,
  document: (id: string) => [...portalKeys.documents(), id] as const,
  notifications: () => [...portalKeys.all, 'notifications'] as const,
  preferences: (employeeId: string) => [...portalKeys.all, 'preferences', employeeId] as const,
};

// Payslips
export const usePayslips = (filters?: any) => {
  return useQuery({
    queryKey: [...portalKeys.payslips(), filters],
    queryFn: () => customInstance(employeePortalService.payslips.list(filters)),
  });
};

export const usePayslip = (id: string) => {
  return useQuery({
    queryKey: portalKeys.payslip(id),
    queryFn: () => customInstance(employeePortalService.payslips.getById(id)),
    enabled: !!id,
  });
};

// Vacations
export const useVacations = (filters?: any) => {
  return useQuery({
    queryKey: [...portalKeys.vacations(), filters],
    queryFn: () => customInstance(employeePortalService.vacations.list(filters)),
  });
};

export const useCreateVacation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(employeePortalService.vacations.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: portalKeys.vacations() });
    },
  });
};

export const useApproveVacation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      customInstance(employeePortalService.vacations.approve(id, comment)),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: portalKeys.vacation(id) });
      queryClient.invalidateQueries({ queryKey: portalKeys.vacations() });
    },
  });
};

// Documents
export const useDocuments = (filters?: any) => {
  return useQuery({
    queryKey: [...portalKeys.documents(), filters],
    queryFn: () => customInstance(employeePortalService.documents.list(filters)),
  });
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ data, file }: { data: any; file: File }) =>
      customInstance(employeePortalService.documents.upload(data, file)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: portalKeys.documents() });
    },
  });
};

// Notifications
export const useNotifications = (filters?: any) => {
  return useQuery({
    queryKey: [...portalKeys.notifications(), filters],
    queryFn: () => customInstance(employeePortalService.notifications.list(filters)),
  });
};

export const useMarkNotificationAsRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => customInstance(employeePortalService.notifications.markAsRead(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: portalKeys.notifications() });
    },
  });
};

// Preferences
export const usePreferences = (employeeId: string) => {
  return useQuery({
    queryKey: portalKeys.preferences(employeeId),
    queryFn: () => customInstance(employeePortalService.preferences.get(employeeId)),
    enabled: !!employeeId,
  });
};

export const useUpdatePreferences = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ employeeId, data }: { employeeId: string; data: any }) =>
      customInstance(employeePortalService.preferences.update(employeeId, data)),
    onSuccess: (_, { employeeId }) => {
      queryClient.invalidateQueries({ queryKey: portalKeys.preferences(employeeId) });
    },
  });
};
