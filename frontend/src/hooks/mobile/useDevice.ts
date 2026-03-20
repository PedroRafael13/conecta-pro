/**
 * React Query Hooks - Device Management
 *
 * Hooks para registro e gestão de dispositivos móveis
 * para push notifications.
 *
 * @module hooks/mobile/useDevice
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  registerDevice,
  unregisterDevice,
  getDeviceId,
  detectPlatform,
  getDeviceInfo,
} from '@/services/mobile/deviceService';
import type { DeviceTokenCreate } from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

/**
 * Hook para registrar dispositivo.
 *
 * @example
 * ```tsx
 * const { mutate: register, isPending } = useRegisterDevice();
 *
 * const handleRegister = async (pushToken: string) => {
 *   register({
 *     token: pushToken,
 *     platform: 'android',
 *     device_id: await getDeviceId(),
 *     ...getDeviceInfo(),
 *   });
 * };
 * ```
 */
export function useRegisterDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: registerDevice,
    onSuccess: () => {
      // Invalidar lista de dispositivos se existir
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
  });
}

/**
 * Hook para remover registro de dispositivo.
 *
 * @example
 * ```tsx
 * const { mutate: unregister } = useUnregisterDevice();
 *
 * const handleLogout = () => {
 *   unregister(currentDeviceId);
 * };
 * ```
 */
export function useUnregisterDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: unregisterDevice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
  });
}

/**
 * Hook helper para obter informações do dispositivo.
 *
 * @example
 * ```tsx
 * const deviceInfo = useDeviceInfo();
 *
 * console.log(deviceInfo.platform); // 'android' | 'ios' | 'web'
 * console.log(deviceInfo.id);
 * ```
 */
export function useDeviceInfo() {
  return {
    id: getDeviceId(),
    platform: detectPlatform(),
    ...getDeviceInfo(),
  };
}

/**
 * Hook para registro automático de push notifications.
 *
 * Registra dispositivo automaticamente ao obter token do FCM/APNs.
 *
 * @param pushToken - Token FCM/APNs (opcional, aguarda se não fornecido)
 *
 * @example
 * ```tsx
 * const { register, isRegistered } = useAutoRegisterDevice(fcmToken);
 *
 * useEffect(() => {
 *   if (fcmToken && !isRegistered) {
 *     register();
 *   }
 * }, [fcmToken, isRegistered]);
 * ```
 */
export function useAutoRegisterDevice(pushToken?: string) {
  const { mutate: register, isPending, isSuccess } = useRegisterDevice();
  const deviceInfo = useDeviceInfo();

  const handleRegister = () => {
    if (!pushToken) {
      return;
    }

    const deviceData: DeviceTokenCreate = {
      token: pushToken,
      platform: deviceInfo.platform,
      device_id: deviceInfo.id,
      device_name: deviceInfo.device_name,
      device_model: deviceInfo.device_model,
      os_version: deviceInfo.os_version,
      app_version: deviceInfo.app_version,
      locale: navigator.language || 'pt-BR',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    };

    register(deviceData);
  };

  return {
    register: handleRegister,
    isRegistering: isPending,
    isRegistered: isSuccess,
    deviceInfo,
  };
}
