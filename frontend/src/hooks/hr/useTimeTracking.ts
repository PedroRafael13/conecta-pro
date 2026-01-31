/**
 * React Query Hooks - HR Time Tracking
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { timeTrackingService } from '@/services/hr';
import { customInstance } from '@/lib/api-client';

export const timeTrackingKeys = {
  all: ['hr', 'time-tracking'] as const,
  entries: () => [...timeTrackingKeys.all, 'entries'] as const,
  entry: (id: string) => [...timeTrackingKeys.entries(), id] as const,
  timesheets: () => [...timeTrackingKeys.all, 'timesheets'] as const,
  timesheet: (id: string) => [...timeTrackingKeys.timesheets(), id] as const,
  overtime: () => [...timeTrackingKeys.all, 'overtime'] as const,
  justifications: () => [...timeTrackingKeys.all, 'justifications'] as const,
  dashboard: () => [...timeTrackingKeys.all, 'dashboard'] as const,
};

// Time Entries
export const useTimeEntries = (params?: any) => {
  return useQuery({
    queryKey: [...timeTrackingKeys.entries(), params],
    queryFn: () => customInstance(timeTrackingService.entries.list(params)),
  });
};

export const useTimeEntry = (id: string) => {
  return useQuery({
    queryKey: timeTrackingKeys.entry(id),
    queryFn: () => customInstance(timeTrackingService.entries.getById(id)),
    enabled: !!id,
  });
};

export const useCreateTimeEntry = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(timeTrackingService.entries.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timeTrackingKeys.entries() });
    },
  });
};

// Timesheets
export const useTimesheets = (params?: any) => {
  return useQuery({
    queryKey: [...timeTrackingKeys.timesheets(), params],
    queryFn: () => customInstance(timeTrackingService.timesheets.list(params)),
  });
};

export const useGenerateTimesheet = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: any) =>
      customInstance(timeTrackingService.timesheets.generate(params.employeeId, params.startDate, params.endDate)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timeTrackingKeys.timesheets() });
    },
  });
};

export const useApproveTimesheet = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      customInstance(timeTrackingService.timesheets.approve(id, comment)),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: timeTrackingKeys.timesheet(id) });
      queryClient.invalidateQueries({ queryKey: timeTrackingKeys.timesheets() });
    },
  });
};

// Overtime
export const useOvertime = (params?: any) => {
  return useQuery({
    queryKey: [...timeTrackingKeys.overtime(), params],
    queryFn: () => customInstance(timeTrackingService.overtime.list(params)),
  });
};

export const useRequestOvertime = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(timeTrackingService.overtime.request(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timeTrackingKeys.overtime() });
    },
  });
};

export const useCalculateOvertime = () => {
  return useMutation({
    mutationFn: (params: any) =>
      customInstance(timeTrackingService.overtime.calculate(params.employeeId, params.startDate, params.endDate)),
  });
};

// Justifications
export const useJustifications = (params?: any) => {
  return useQuery({
    queryKey: [...timeTrackingKeys.justifications(), params],
    queryFn: () => customInstance(timeTrackingService.justifications.list(params)),
  });
};

export const useCreateJustification = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(timeTrackingService.justifications.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timeTrackingKeys.justifications() });
    },
  });
};

export const useApproveJustification = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => customInstance(timeTrackingService.justifications.approve(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timeTrackingKeys.justifications() });
    },
  });
};

// Dashboard
export const useTimeTrackingDashboard = (employeeId: string) => {
  return useQuery({
    queryKey: [...timeTrackingKeys.dashboard(), employeeId],
    queryFn: () => customInstance(timeTrackingService.dashboard.getSummary(employeeId)),
    enabled: !!employeeId,
  });
};
