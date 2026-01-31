/**
 * React Query Hooks - HR Mobile Time Clock
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mobileTimeClockService } from '@/services/hr';
import { customInstance } from '@/lib/api-client';

export const mobileKeys = {
  all: ['hr', 'mobile'] as const,
  devices: () => [...mobileKeys.all, 'devices'] as const,
  device: (id: string) => [...mobileKeys.devices(), id] as const,
  checkins: () => [...mobileKeys.all, 'checkins'] as const,
  checkin: (id: string) => [...mobileKeys.checkins(), id] as const,
  geofences: () => [...mobileKeys.all, 'geofences'] as const,
  geofence: (id: string) => [...mobileKeys.geofences(), id] as const,
  offline: () => [...mobileKeys.all, 'offline'] as const,
};

// Devices
export const useMobileDevices = (params?: any) => {
  return useQuery({
    queryKey: [...mobileKeys.devices(), params],
    queryFn: () => customInstance(mobileTimeClockService.devices.list(params)),
  });
};

export const useRegisterDevice = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(mobileTimeClockService.devices.register(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mobileKeys.devices() });
    },
  });
};

// Check-ins
export const useCheckins = (params?: any) => {
  return useQuery({
    queryKey: [...mobileKeys.checkins(), params],
    queryFn: () => customInstance(mobileTimeClockService.checkins.list(params)),
  });
};

export const useCreateCheckin = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(mobileTimeClockService.checkins.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mobileKeys.checkins() });
    },
  });
};

// Geofences
export const useGeofences = (params?: any) => {
  return useQuery({
    queryKey: [...mobileKeys.geofences(), params],
    queryFn: () => customInstance(mobileTimeClockService.geofences.list(params)),
  });
};

export const useCreateGeofence = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(mobileTimeClockService.geofences.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mobileKeys.geofences() });
    },
  });
};

// Offline Sync
export const useOfflineSync = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any[]) => customInstance(mobileTimeClockService.offline.sync(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mobileKeys.checkins() });
    },
  });
};
