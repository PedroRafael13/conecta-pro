/**
 * React Query Hooks - HR Payroll Integration
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { payrollIntegrationService } from '@/services/hr';
import { customInstance } from '@/lib/api-client';

export const payrollKeys = {
  all: ['hr', 'payroll'] as const,
  periods: () => [...payrollKeys.all, 'periods'] as const,
  period: (id: string) => [...payrollKeys.periods(), id] as const,
  events: () => [...payrollKeys.all, 'events'] as const,
  event: (id: string) => [...payrollKeys.events(), id] as const,
  exports: () => [...payrollKeys.all, 'exports'] as const,
  esocial: () => [...payrollKeys.all, 'esocial'] as const,
};

// Periods
export const usePayrollPeriods = (params?: any) => {
  return useQuery({
    queryKey: [...payrollKeys.periods(), params],
    queryFn: () => customInstance(payrollIntegrationService.periods.list(params)),
  });
};

export const usePayrollPeriod = (id: string) => {
  return useQuery({
    queryKey: payrollKeys.period(id),
    queryFn: () => customInstance(payrollIntegrationService.periods.getById(id)),
    enabled: !!id,
  });
};

export const useCreatePayrollPeriod = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(payrollIntegrationService.periods.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payrollKeys.periods() });
    },
  });
};

export const useCalculatePayroll = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => customInstance(payrollIntegrationService.periods.calculate(id)),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: payrollKeys.period(id) });
    },
  });
};

// Events
export const usePayrollEvents = (params?: any) => {
  return useQuery({
    queryKey: [...payrollKeys.events(), params],
    queryFn: () => customInstance(payrollIntegrationService.events.list(params)),
  });
};

export const useCreatePayrollEvent = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(payrollIntegrationService.events.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payrollKeys.events() });
    },
  });
};

// Exports
export const usePayrollExports = (params?: any) => {
  return useQuery({
    queryKey: [...payrollKeys.exports(), params],
    queryFn: () => customInstance(payrollIntegrationService.exports.list(params)),
  });
};

export const useCreatePayrollExport = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(payrollIntegrationService.exports.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payrollKeys.exports() });
    },
  });
};

// eSocial
export const useSendESocial = () => {
  return useMutation({
    mutationFn: ({ eventType, data }: { eventType: string; data: any }) =>
      customInstance(payrollIntegrationService.esocial.send(eventType, data)),
  });
};
