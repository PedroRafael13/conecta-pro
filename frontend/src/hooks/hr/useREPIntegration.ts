/**
 * React Query Hooks - HR REP Integration
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { repIntegrationService } from '@/services/hr';
import { customInstance } from '@/lib/api-client';

export const repKeys = {
  all: ['hr', 'rep'] as const,
  devices: () => [...repKeys.all, 'devices'] as const,
  device: (id: string) => [...repKeys.devices(), id] as const,
  sync: () => [...repKeys.all, 'sync'] as const,
  events: () => [...repKeys.all, 'events'] as const,
  afd: () => [...repKeys.all, 'afd'] as const,
  webhooks: () => [...repKeys.all, 'webhooks'] as const,
};

// Devices
export const useREPDevices = (params?: any) => {
  return useQuery({
    queryKey: [...repKeys.devices(), params],
    queryFn: () => customInstance(repIntegrationService.devices.list(params)),
  });
};

export const useRegisterREPDevice = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(repIntegrationService.devices.register(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: repKeys.devices() });
    },
  });
};

// Sync
export const useSyncREPDevice = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (deviceId: string) => customInstance(repIntegrationService.sync.manual(deviceId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: repKeys.sync() });
      queryClient.invalidateQueries({ queryKey: repKeys.events() });
    },
  });
};

export const useSyncStatus = (deviceId: string) => {
  return useQuery({
    queryKey: [...repKeys.sync(), deviceId],
    queryFn: () => customInstance(repIntegrationService.sync.status(deviceId)),
    enabled: !!deviceId,
  });
};

// Events
export const useREPEvents = (params?: any) => {
  return useQuery({
    queryKey: [...repKeys.events(), params],
    queryFn: () => customInstance(repIntegrationService.events.list(params)),
  });
};

export const useImportREPEvents = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: any) => customInstance(repIntegrationService.events.import(params.deviceId, params.startDate, params.endDate)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: repKeys.events() });
    },
  });
};

// AFD
export const useGenerateAFD = () => {
  return useMutation({
    mutationFn: (params: any) =>
      customInstance(repIntegrationService.afd.generate(params.deviceId, params.startDate, params.endDate)),
  });
};

// Webhooks
export const useREPWebhooks = (params?: any) => {
  return useQuery({
    queryKey: [...repKeys.webhooks(), params],
    queryFn: () => customInstance(repIntegrationService.webhooks.list(params)),
  });
};

export const useCreateREPWebhook = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(repIntegrationService.webhooks.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: repKeys.webhooks() });
    },
  });
};
